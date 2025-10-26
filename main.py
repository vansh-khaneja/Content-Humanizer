from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
from parrot import Parrot
import spacy
import warnings
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from dotenv import load_dotenv
from database import get_db, UserUsage, init_db as init_database

load_dotenv()
warnings.filterwarnings("ignore")

app = FastAPI(title="Text Humanizer API")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models lazily
parrot = None
nlp = None

def get_parrot():
    global parrot
    if parrot is None:
        print("Loading Parrot model...")
        parrot = Parrot(model_tag="prithivida/parrot_paraphraser_on_T5", use_gpu=False)
    return parrot

def get_nlp():
    global nlp
    if nlp is None:
        print("Loading spaCy model...")
        nlp = spacy.load("en_core_web_sm")
    return nlp

# Request/Response models
class DetectAIRequest(BaseModel):
    text: str
    user_id: str

class HumanizeRequest(BaseModel):
    text: str
    user_id: str

class UpdateLimitRequest(BaseModel):
    user_id: str
    credits_to_add: int  # Number of credits to add to current limit
    admin_token: str


class SentenceDetail(BaseModel):
    length: int
    score: float
    text: str

class AttackDetected(BaseModel):
    zero_width_space: bool
    homoglyph_attack: bool

class UsageInfo(BaseModel):
    word_count: int
    total_usage: int
    usage_limit: int
    remaining_usage: int

class DetectAIResponse(BaseModel):
    status: int
    length: int
    score: float
    sentences: List[SentenceDetail]
    input: str
    attack_detected: AttackDetected
    readability_score: float
    credits_used: int
    credits_remaining: int
    version: str
    language: str
    usage_info: Optional[UsageInfo] = None

class HumanizeResponse(BaseModel):
    original_text: str
    humanized_text: str
    sentences: List[str]
    humanized_sentences: List[str]
    word_count: int
    total_usage: int
    usage_limit: int
    remaining_usage: int

# Startup event
@app.on_event("startup")
async def startup_event():
    await init_database()
    print("Database initialized")

@app.get("/")
async def root():
    return {
        "message": "Text Humanizer API",
        "endpoints": {
            "/detect-ai": "POST - Detect AI-generated content",
            "/humanize": "POST - Humanize text with usage tracking",
            "/update-limit": "POST - Update user usage limits (admin only)",
            "/user-usage/{user_id}": "GET - Get user usage statistics",
            "/health": "GET - Health check"
        }
    }

@app.post("/detect-ai", response_model=DetectAIResponse)
async def detect_ai(request: DetectAIRequest, db: AsyncSession = Depends(get_db)):
    """
    Detect AI-generated content in the provided text using Winston AI.
    Tracks usage per user.
    """
    try:
        # Get Winston AI token from environment
        winston_token = os.getenv("WINSTON_AI_TOKEN")
        if not winston_token:
            raise HTTPException(status_code=500, detail="WINSTON_AI_TOKEN not found in environment variables")
        
        # Get or create user
        user = await get_or_create_user(db, request.user_id)
        
        # Calculate word count for usage tracking
        word_count = len(request.text.split())
        token_count = word_count  # Using word count as token approximation
        
        # Check if user has exceeded usage limit
        if user.token_usage >= user.usage_limit:
            raise HTTPException(
                status_code=403,
                detail=f"Usage limit exceeded. Current usage: {user.token_usage}/{user.usage_limit}"
            )
        
        # Check if this request would exceed the limit
        if user.token_usage + token_count > user.usage_limit:
            raise HTTPException(
                status_code=403,
                detail=f"Request would exceed usage limit. Current usage: {user.token_usage}/{user.usage_limit}"
            )
        
        url = "https://api.gowinston.ai/v2/ai-content-detection"
        
        payload = {
            "text": request.text,
        }
        
        headers = {
            "Authorization": f"Bearer {winston_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Winston AI API error: {response.text}"
            )
        
        # Update user usage
        user.word_count += word_count
        user.token_usage += token_count
        await db.commit()
        await db.refresh(user)
        
        result = response.json()
        
        # Add usage info to response
        result['usage_info'] = {
            'word_count': word_count,
            'total_usage': user.token_usage,
            'usage_limit': user.usage_limit,
            'remaining_usage': user.usage_limit - user.token_usage
        }
        
        return result
        
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error calling Winston AI: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def get_or_create_user(db: AsyncSession, user_id: str):
    """Get user or create if doesn't exist"""
    result = await db.execute(select(UserUsage).where(UserUsage.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user with default limit
        default_limit = int(os.getenv("DEFAULT_USAGE_LIMIT", 400))
        user = UserUsage(user_id=user_id, usage_limit=default_limit)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

@app.post("/humanize", response_model=HumanizeResponse)
async def humanize_text(request: HumanizeRequest, db: AsyncSession = Depends(get_db)):
    """
    Humanize the provided text by paraphrasing it using Parrot.
    Processes the text sentence by sentence for better accuracy.
    Tracks usage per user and enforces usage limits.
    """
    try:
        # Get or create user
        user = await get_or_create_user(db, request.user_id)
        
        # Calculate word count and tokens for the input text
        word_count = len(request.text.split())
        token_count = word_count  # Using word count as token approximation
        
        # Check if user has exceeded usage limit
        if user.token_usage >= user.usage_limit:
            raise HTTPException(
                status_code=403,
                detail=f"Usage limit exceeded. Current usage: {user.token_usage}/{user.usage_limit}"
            )
        
        # Check if this request would exceed the limit
        if user.token_usage + token_count > user.usage_limit:
            raise HTTPException(
                status_code=403,
                detail=f"Request would exceed usage limit. Current usage: {user.token_usage}/{user.usage_limit}"
            )
        
        # Load models if not already loaded
        nlp_model = get_nlp()
        parrot_model = get_parrot()
        
        # Split text into sentences using spaCy
        doc = nlp_model(request.text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        
        humanized_sentences = []
        
        # Process each sentence separately
        for sentence in sentences:
            paraphrases = parrot_model.augment(input_phrase=sentence)
            
            if paraphrases:
                # Get the paraphrase with the highest score
                # paraphrases is a list of tuples: (text, score)
                best_paraphrase = max(paraphrases, key=lambda x: x[1])[0]  # Get text with max score
                
                # Clean up and format the paraphrased text
                # Remove extra whitespace
                best_paraphrase = " ".join(best_paraphrase.split())
                
                # Capitalize first letter
                best_paraphrase = best_paraphrase[0].upper() + best_paraphrase[1:] if best_paraphrase else best_paraphrase
                
                # Add period if sentence doesn't end with punctuation
                if best_paraphrase and not best_paraphrase.rstrip()[-1] in '.!?':
                    best_paraphrase += "."
                
                humanized_sentences.append(best_paraphrase)
            else:
                # If no paraphrase available, use original sentence
                humanized_sentences.append(sentence)
        
        # Combine all humanized sentences with proper spacing
        humanized_text = " ".join(humanized_sentences)
        
        # Update user usage
        user.word_count += word_count
        user.token_usage += token_count
        await db.commit()
        await db.refresh(user)
        
        return {
            "original_text": request.text,
            "humanized_text": humanized_text,
            "sentences": sentences,
            "humanized_sentences": humanized_sentences,
            "word_count": word_count,
            "total_usage": user.token_usage,
            "usage_limit": user.usage_limit,
            "remaining_usage": user.usage_limit - user.token_usage
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error humanizing text: {str(e)}")

@app.post("/update-limit")
async def update_usage_limit(request: UpdateLimitRequest, db: AsyncSession = Depends(get_db)):
    """
    Add credits to a user's usage limit.
    Example: If user has 400 limit and you add 50 credits, new limit will be 450.
    Requires admin token for authentication.
    """
    admin_token = os.getenv("ADMIN_TOKEN")
    
    if not admin_token or request.admin_token != admin_token:
        raise HTTPException(status_code=401, detail="Invalid admin token")
    
    try:
        result = await db.execute(select(UserUsage).where(UserUsage.user_id == request.user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")
        
        # Store old limit
        old_limit = user.usage_limit
        
        # Add credits to current limit
        user.usage_limit = user.usage_limit + request.credits_to_add
        await db.commit()
        await db.refresh(user)
        
        return {
            "user_id": user.user_id,
            "old_limit": old_limit,
            "credits_added": request.credits_to_add,
            "new_limit": user.usage_limit,
            "current_usage": user.token_usage,
            "message": f"Added {request.credits_to_add} credits. Usage limit updated from {old_limit} to {user.usage_limit}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating usage limit: {str(e)}")

@app.get("/user-usage/{user_id}")
async def get_user_usage(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get current usage information for a user"""
    try:
        result = await db.execute(select(UserUsage).where(UserUsage.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        return {
            "user_id": user.user_id,
            "word_count": user.word_count,
            "token_usage": user.token_usage,
            "usage_limit": user.usage_limit,
            "remaining_usage": user.usage_limit - user.token_usage,
            "usage_percentage": (user.token_usage / user.usage_limit * 100) if user.usage_limit > 0 else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user usage: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

