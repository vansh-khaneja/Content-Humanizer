# PostgreSQL Integration Summary

## What Was Implemented

### 1. Database Setup
- **File**: `database.py`
- **Model**: `UserUsage` table tracks:
  - `user_id`: Unique identifier per user
  - `word_count`: Total words processed
  - `token_usage`: Total tokens used (limit enforcement)
  - `usage_limit`: Max allowed usage (default: 400)
  - Timestamps for creation/updates

### 2. Updated Requirements
- Added `sqlalchemy==2.0.23`
- Added `asyncpg==0.29.0`
- Added `psycopg2-binary==2.9.9`

### 3. Updated Endpoints

#### `/humanize` - Now with Usage Tracking
**Changes:**
- Requires `user_id` in request
- Automatically creates user if doesn't exist
- Checks usage limit before processing
- Tracks word count and token usage
- Returns usage statistics in response
- Blocks requests if limit exceeded (403 error)

#### `/update-limit` - New Admin Endpoint
**Purpose**: Update user usage limits
**Authentication**: Requires `admin_token` from environment
**Usage**: 
```json
{
    "user_id": "some_user",
    "new_limit": 500,
    "admin_token": "your_admin_token"
}
```

#### `/user-usage/{user_id}` - New Endpoint
**Purpose**: Get user usage statistics
**Returns**: word_count, token_usage, usage_limit, remaining_usage, usage_percentage

### 4. Environment Variables
Create `.env` file with:
```
DATABASE_URL=postgresql://username:password@localhost:5432/humanizer_db
ADMIN_TOKEN=your_secure_admin_token_here
DEFAULT_USAGE_LIMIT=400
```

### 5. Usage Flow
1. User sends request with `user_id`
2. System checks if user exists (creates if not)
3. System checks current usage vs limit
4. If within limit, processes request
5. Updates usage statistics in database
6. Returns humanized text + usage stats

### 6. Error Handling
- **403 Forbidden**: Usage limit exceeded
- **500 Error**: Database or processing error
- **401 Unauthorized**: Invalid admin token

## Testing

Run the updated test script:
```bash
python test_api.py
```

The test now includes:
- Humanizing text with user_id
- Getting user usage stats
- Updating usage limits (with admin token)

## Database Initialization

The database tables are automatically created on server startup via the `startup_event` in `main.py`.

## Notes

- Token count is approximated using word count
- Default limit is 400 tokens per user
- Users are created automatically on first request
- Usage limits can be updated via admin endpoint
- All endpoints return appropriate error codes

