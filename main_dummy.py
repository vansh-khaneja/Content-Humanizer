"""
Dummy version of main.py for testing
- No heavy models loaded (Parrot, spaCy)
- Dummy responses for humanize and AI detection
- All PostgreSQL and API endpoints work normally
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import requests
import warnings
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from dotenv import load_dotenv
from database import get_db, UserUsage, init_db as init_database
import random

load_dotenv()
warnings.filterwarnings("ignore")

app = FastAPI(title="Text Humanizer API (Dummy Mode)")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    # Initialize database
    await init_database()
    print("Database initialized")
    print("⚠️  DUMMY MODE: Using mock responses (no models loaded)")
    print("Application ready!")

@app.get("/")
async def root():
    return {
        "message": "Text Humanizer API (Dummy Mode)",
        "status": "⚠️ Using mock responses - models not loaded",
        "endpoints": {
            "/detect-ai": "POST - Detect AI-generated content (dummy)",
            "/humanize": "POST - Humanize text with usage tracking (dummy)",
            "/update-limit": "POST - Update user usage limits (admin only)",
            "/user-usage/{user_id}": "GET - Get user usage statistics",
            "/health": "GET - Health check"
        }
    }

def get_or_create_user(db: AsyncSession, user_id: str):
    """Get or create a user with default usage limit"""
    result = db.execute(select(UserUsage).where(UserUsage.user_id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        default_limit = int(os.getenv("DEFAULT_USAGE_LIMIT", "400"))
        user = UserUsage(
            user_id=user_id,
            word_count=0,
            token_usage=0,
            usage_limit=default_limit
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return user

# Helper function to add punctuation and capitalization
def format_text(text: str) -> str:
    """Add punctuation and capitalization to text"""
    if not text.strip():
        return text
    
    # Add period if missing
    if not text.rstrip().endswith(('.', '!', '?')):
        text = text.rstrip() + '.'
    
    # Capitalize first letter
    text = text[0].upper() + text[1:] if text else text
    
    return text

@app.post("/humanize", response_model=HumanizeResponse)
async def humanize_text(request: HumanizeRequest, db: AsyncSession = Depends(get_db)):
    """
    Humanize text (DUMMY MODE - returns mock humanized text).
    Tracks usage per user.
    """
    try:
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
        
        # DUMMY: Just return formatted version of input text
        # Split into sentences (simple approach)
        sentences = [s.strip() for s in request.text.split('.') if s.strip()]
        
        # Humanize each sentence (dummy: just add punctuation/capitalization)
        humanized_sentences = [format_text(s) for s in sentences]
        humanized_text = '. '.join(humanized_sentences)
        
        # Update user usage
        user.word_count += word_count
        user.token_usage += token_count
        db.commit()
        db.refresh(user)
        
        # Calculate remaining usage
        remaining_usage = user.usage_limit - user.token_usage
        
        return HumanizeResponse(
            original_text=request.text,
            humanized_text=humanized_text,
            sentences=sentences,
            humanized_sentences=humanized_sentences,
            word_count=word_count,
            total_usage=user.token_usage,
            usage_limit=user.usage_limit,
            remaining_usage=remaining_usage
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error humanizing text: {str(e)}")

@app.post("/detect-ai", response_model=DetectAIResponse)
async def detect_ai(request: DetectAIRequest, db: AsyncSession = Depends(get_db)):
    """
    Detect AI-generated content (DUMMY MODE - returns mock detection).
    Tracks usage per user.
    """
    try:
        # Get or create user
        user = await get_or_create_user(db, request.user_id)
        
        # Calculate word count for usage tracking
        word_count = len(request.text.split())
        token_count = word_count
        
        # Check usage limits
        if user.token_usage >= user.usage_limit:
            raise HTTPException(
                status_code=403,
                detail=f"Usage limit exceeded. Current usage: {user.token_usage}/{user.usage_limit}"
            )
        
        if user.token_usage + token_count > user.usage_limit:
            raise HTTPException(
                status_code=403,
                detail=f"Request would exceed usage limit. Current usage: {user.token_usage}/{user.usage_limit}"
            )
        
        # DUMMY: Return mock AI detection results
        # Random score between 0-100
        ai_score = round(random.uniform(0, 100), 1)
        
        # Update user usage
        user.word_count += word_count
        user.token_usage += token_count
        db.commit()
        db.refresh(user)
        
        # Create dummy sentence details
        sentences = request.text.split('.')
        sentence_details = [
            SentenceDetail(
                length=len(s),
                score=round(random.uniform(0, 100), 2),
                text=s.strip()
            ) for s in sentences if s.strip()
        ]
        
        # Calculate remaining usage
        remaining_usage = user.usage_limit - user.token_usage
        
        usage_info = UsageInfo(
            word_count=word_count,
            total_usage=user.token_usage,
            usage_limit=user.usage_limit,
            remaining_usage=remaining_usage
        )
        
        return DetectAIResponse(
            status=200,
            length=len(request.text),
            score=ai_score,
            sentences=sentence_details,
            input=request.text,
            attack_detected=AttackDetected(
                zero_width_space=False,
                homoglyph_attack=False
            ),
            readability_score=round(random.uniform(50, 90), 2),
            credits_used=token_count,
            credits_remaining=remaining_usage,
            version="1.0",
            language="en",
            usage_info=usage_info
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting AI: {str(e)}")

@app.post("/update-limit")
async def update_usage_limit(request: UpdateLimitRequest, db: AsyncSession = Depends(get_db)):
    """Update user's usage limit by adding credits"""
    try:
        admin_token = os.getenv("ADMIN_TOKEN", "admin")
        
        if request.admin_token != admin_token:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid admin token")
        
        # Get user
        result = await db.execute(select(UserUsage).where(UserUsage.user_id == request.user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update limit (add credits)
        old_limit = user.usage_limit
        user.usage_limit += request.credits_to_add
        await db.commit()
        await db.refresh(user)
        
        return {
            "success": True,
            "old_limit": old_limit,
            "new_limit": user.usage_limit,
            "credits_added": request.credits_to_add,
            "current_usage": user.token_usage
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating limit: {str(e)}")

@app.get("/user-usage/{user_id}")
async def get_user_usage(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user usage statistics"""
    try:
        result = await db.execute(select(UserUsage).where(UserUsage.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user_id": user.user_id,
            "word_count": user.word_count,
            "token_usage": user.token_usage,
            "usage_limit": user.usage_limit,
            "remaining_usage": user.usage_limit - user.token_usage
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user usage: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "dummy"}

