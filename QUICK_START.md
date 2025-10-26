# Quick Start Guide

## Backend Setup

1. **Install dependencies:**
   ```bash
   cd C:\Users\VANSH KHANEJA\PROJECTS\personal\humanizer
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Your `.env` file is already set up with database and Winston AI token
   
3. **Start the backend:**
   ```bash
   uvicorn main:app --reload
   ```

## Frontend Setup

1. **Install dependencies:**
   ```bash
   cd humanizer-front
   npm install
   ```

2. **Set up Clerk:**
   - Sign up at [clerk.com](https://clerk.com)
   - Create a new application
   - Copy your API keys from Clerk dashboard
   - Update `humanizer-front/.env.local` with your actual Clerk keys:
     ```env
     NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_actual_key_here
     CLERK_SECRET_KEY=sk_test_your_actual_secret_here
     ```

3. **Start the frontend:**
   ```bash
   npm run dev
   ```

## How It Works

- **User Authentication**: Clerk handles login/signup automatically
- **User ID**: Automatically retrieved from Clerk session and sent to backend
- **Usage Tracking**: Each user's usage is tracked in PostgreSQL database
- **API Endpoints**: `/humanize` and `/detect-ai` both use user ID from Clerk

## Environment Variables Needed

### Backend (`.env` in project root):
- `DATABASE_URL` - Neon PostgreSQL URL
- `WINSTON_AI_TOKEN` - Winston AI API token
- `ADMIN_TOKEN` - Admin token for limit updates (set to "admin")
- `DEFAULT_USAGE_LIMIT` - Default usage limit per user (400)

### Frontend (`.env.local` in humanizer-front):
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk publishable key
- `CLERK_SECRET_KEY` - Clerk secret key

## API Endpoints

- `POST /humanize` - Humanize text (requires user_id from Clerk)
- `POST /detect-ai` - Detect AI content (requires user_id from Clerk)
- `POST /update-limit` - Add credits to user (admin only, admin_token: "admin")
- `GET /user-usage/{user_id}` - Get user usage stats

## Testing

1. Start backend: `uvicorn main:app --reload`
2. Start frontend: `npm run dev` (in humanizer-front)
3. Visit http://localhost:3000
4. Click "Login" and sign in with Clerk
5. Try humanizing or detecting AI in text!

