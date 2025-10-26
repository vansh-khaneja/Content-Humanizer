# How to Get Your Clerk Keys

## Step 1: Sign Up for Clerk
1. Go to https://clerk.com
2. Click "Sign Up" or "Get Started"
3. Create an account with your email

## Step 2: Create an Application
1. After logging in, click "Create Application"
2. Choose a name (e.g., "Text Humanizer")
3. Choose authentication methods (Email, Google, etc.)
4. Click "Create"

## Step 3: Get Your API Keys
1. In your application dashboard, go to **"API Keys"** section
2. You'll see two keys:
   - **Publishable Key** (starts with `pk_test_` or `pk_live_`)
   - **Secret Key** (starts with `sk_test_` or `sk_live_`)

## Step 4: Update `.env.local`

Edit `humanizer-front/.env.local` and replace the placeholder keys:

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_ACTUAL_KEY_HERE
CLERK_SECRET_KEY=sk_test_YOUR_ACTUAL_SECRET_HERE
```

Replace `YOUR_ACTUAL_KEY_HERE` and `YOUR_ACTUAL_SECRET_HERE` with the keys from Clerk dashboard.

## Step 5: Restart Your Dev Server

After updating the keys, restart your Next.js dev server:
- Stop the current server (Ctrl+C)
- Run `npm run dev` again

That's it! Now Clerk authentication will work.

---

## Alternative: Continue Without Clerk

If you don't want to set up Clerk right now, you can comment out the Clerk-related code and the app will work with guest users. Let me know if you need help with that.

