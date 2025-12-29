# Vercel Deployment Guide for Weltanschauung (Noesis)

## Overview
This project consists of two parts:
1. **Frontend (Next.js)** - Deploy to Vercel
2. **Backend (FastAPI/Python)** - Deploy to Railway/Render/Fly.io

Vercel doesn't support Python backends natively, so the backend must be deployed separately.

---

## Step 1: Deploy Backend to Railway (Recommended)

### Option A: Railway (Easiest)

1. Go to [railway.app](https://railway.app) and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select the `backend` folder or use the Railway CLI:
   ```bash
   cd backend
   railway init
   railway up
   ```

4. Add environment variables in Railway dashboard:
   ```
   DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   GROQ_API_KEY=your_groq_api_key
   CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
   ```

5. Note your Railway backend URL (e.g., `https://noesis-backend.railway.app`)

### Option B: Render

1. Go to [render.com](https://render.com)
2. Create a new "Web Service"
3. Connect your GitHub repo
4. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables as above

### Option C: Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Create `backend/fly.toml`:
   ```toml
   app = "noesis-backend"
   
   [build]
     builder = "paketobuildpacks/builder:base"
   
   [env]
     PORT = "8080"
   
   [[services]]
     internal_port = 8080
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```
3. Deploy: `cd backend && fly deploy`
4. Set secrets: `fly secrets set DATABASE_URL=... GROQ_API_KEY=...`

---

## Step 2: Deploy Frontend to Vercel

### Method 1: Vercel CLI (Recommended)

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy from the frontend directory:
   ```bash
   cd frontend
   vercel
   ```

4. Follow the prompts:
   - Link to existing project or create new
   - Set root directory to `frontend` (or leave as-is if already in frontend dir)

5. Set environment variables in Vercel dashboard or via CLI:
   ```bash
   vercel env add NEXT_PUBLIC_API_URL production
   # Enter your backend URL: https://noesis-backend.railway.app/api
   ```

### Method 2: GitHub Integration

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Click "Add New Project"
4. Import your GitHub repository
5. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build`
   - **Output Directory**: Leave default

6. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api
   ```

7. Click "Deploy"

---

## Step 3: Configure CORS on Backend

After deploying both services, update your backend's `CORS_ORIGINS` environment variable:

```
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

If using Vercel preview deployments, you may want to allow the pattern:
```
CORS_ORIGINS=https://your-app.vercel.app,https://*.vercel.app
```

Or modify the backend CORS configuration to use regex patterns.

---

## Step 4: Database (Supabase)

Your Supabase database should already be configured. Ensure:

1. The `DATABASE_URL` in your backend environment uses the **Session Mode pooler** (port 5432):
   ```
   postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```

2. Your IP address (or `0.0.0.0/0` for development) is allowed in Supabase Network settings

3. Tables are created automatically on first backend startup

---

## Environment Variables Summary

### Frontend (Vercel)
| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://noesis-backend.railway.app/api` |

### Backend (Railway/Render/Fly.io)
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | Supabase PostgreSQL connection string | `postgresql+asyncpg://...` |
| `GROQ_API_KEY` | Groq API key for LLM | `gsk_...` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `https://app.vercel.app` |

---

## Troubleshooting

### CORS Errors
- Ensure `CORS_ORIGINS` includes your Vercel deployment URL
- Check for trailing slashes (don't include them)

### Database Connection Issues
- Verify the DATABASE_URL uses port 5432 (Session Mode)
- Check Supabase dashboard for connection limits
- Ensure pooler connection string is correct

### API Calls Failing
- Verify `NEXT_PUBLIC_API_URL` doesn't have trailing slash
- Check backend logs in Railway/Render dashboard
- Ensure backend health check endpoint works: `https://your-backend/health`

---

## Quick Verification

After deployment, test these endpoints:

1. **Backend Health**: `curl https://your-backend-url/health`
2. **Frontend**: Visit your Vercel URL
3. **API Integration**: Create a document in the app

---

## Local Development After Deployment

To run locally after deployment:

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

The frontend will automatically use `http://localhost:8000/api` for local development.
