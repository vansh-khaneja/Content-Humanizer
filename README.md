# Text Humanizer API

A FastAPI backend for text humanization with AI detection, paraphrasing capabilities, and user usage tracking via PostgreSQL.

## Features

- **AI Detection**: Detect AI-generated content using Winston AI API
- **Text Humanization**: Paraphrase text to make it more human-like using Parrot
- **Sentence-by-Sentence Processing**: Breaks text into sentences for accurate humanization
- **User Usage Tracking**: Track word and token usage per user with PostgreSQL
- **Usage Limits**: Enforce usage limits per user (default: 400 tokens)
- **Admin Controls**: Update user usage limits via admin endpoint

## Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Language Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Set Up PostgreSQL Database

Create a PostgreSQL database:

```sql
CREATE DATABASE humanizer_db;
```

### 6. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# PostgreSQL Database URL
DATABASE_URL=postgresql://username:password@localhost:5432/humanizer_db

# Winston AI Token
WINSTON_AI_TOKEN=your_winston_ai_token_here

# Admin Token (for updating usage limits)
ADMIN_TOKEN=your_secure_admin_token_here

# Default Usage Limit per User (in tokens)
DEFAULT_USAGE_LIMIT=400
```

Replace the placeholders with your actual database credentials, Winston AI token, and a secure admin token.

### 7. Run the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

**Note:** The database tables will be automatically created on first startup.

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### 1. Detect AI Content

**POST** `/detect-ai`

Detect if text is AI-generated. **Requires user authentication via user_id**.

**Request Body:**
```json
{
    "text": "Your text here",
    "user_id": "unique_user_identifier"
}
```

**Note:** The Winston AI token is loaded from environment variables (`WINSTON_AI_TOKEN`).

**Response:**
```json
{
    "status": 200,
    "length": 509,
    "score": 99.88,
    "sentences": [...],
    "readability_score": 40.41,
    "usage_info": {
        "word_count": 50,
        "total_usage": 150,
        "usage_limit": 400,
        "remaining_usage": 250
    },
    ...
}
```

**Error Responses:**
- `403`: Usage limit exceeded
- `500`: Error processing or Winston AI token not configured

### 2. Humanize Text

**POST** `/humanize`

Paraphrase text to make it more human-like. **Requires user authentication via user_id**.

**Request Body:**
```json
{
    "text": "Your text to humanize",
    "user_id": "unique_user_identifier"
}
```

**Response:**
```json
{
    "original_text": "Original text",
    "humanized_text": "Humanized version",
    "sentences": ["sentence1", "sentence2"],
    "humanized_sentences": ["humanized1", "humanized2"],
    "word_count": 50,
    "total_usage": 150,
    "usage_limit": 400,
    "remaining_usage": 250
}
```

**Error Responses:**
- `403`: Usage limit exceeded
- `500`: Error processing text

### 3. Get User Usage

**GET** `/user-usage/{user_id}`

Get current usage statistics for a specific user.

**Response:**
```json
{
    "user_id": "unique_user_identifier",
    "word_count": 100,
    "token_usage": 200,
    "usage_limit": 400,
    "remaining_usage": 200,
    "usage_percentage": 50.0
}
```

### 4. Add Credits to User (Admin Only)

**POST** `/update-limit`

Add credits to a user's usage limit. Requires admin authentication.

**Request Body:**
```json
{
    "user_id": "unique_user_identifier",
    "credits_to_add": 50,
    "admin_token": "your_admin_token"
}
```

**Example:** If user has limit of 400, adding 50 credits will make it 450.

**Response:**
```json
{
    "user_id": "unique_user_identifier",
    "old_limit": 400,
    "credits_added": 50,
    "new_limit": 450,
    "current_usage": 200,
    "message": "Added 50 credits. Usage limit updated from 400 to 450"
}
```

**Error Responses:**
- `401`: Invalid admin token
- `404`: User not found

### 5. Health Check

**GET** `/health`

Check if the API is running.

**Response:**
```json
{
    "status": "healthy"
}
```

## Usage Examples

### Python Example

```python
import requests

# Humanize text
response = requests.post(
    "http://localhost:8000/humanize",
    json={
        "text": "Your text here",
        "user_id": "my_unique_id"
    }
)

result = response.json()
print(f"Humanized: {result['humanized_text']}")
print(f"Usage: {result['total_usage']}/{result['usage_limit']}")
```

### Update Usage Limit

```python
import requests

response = requests.post(
    "http://localhost:8000/update-limit",
    json={
        "user_id": "my_unique_id",
        "credits_to_add": 100,  # Adds 100 to current limit
        "admin_token": "your_admin_token"
    }
)
```

## Database Schema

The `user_usage` table stores:

- `id`: Primary key
- `user_id`: Unique user identifier
- `word_count`: Total words processed
- `token_usage`: Total tokens used
- `usage_limit`: Maximum allowed usage (default: 400)
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

## Notes

- First startup will download the Parrot model (may take some time)
- The API uses `prithivida/parrot_paraphraser_on_T5` model
- Text is processed sentence-by-sentence for better results
- Usage limits are enforced per user based on token count
- New users are created automatically on first request
- Default usage limit can be changed via environment variable `DEFAULT_USAGE_LIMIT`
