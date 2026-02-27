# 🚀 Render Deployment Guide - CompanyIntel

## ✅ Pre-Deployment Checklist

- [x] Code committed to Git
- [x] `.env` file is gitignored (verified)
- [x] `render.yaml` configuration complete
- [x] All dependencies listed in `requirements.txt`
- [x] Backend tested locally and working
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Render account created

---

## Step 1: Create GitHub Repository

### Option A: Using GitHub Website
1. Go to https://github.com/new
2. Repository name: `companyintel-ai`
3. Description: `Autonomous AI Company Intelligence Platform - Built for Autonomous Agents Hackathon 2026`
4. Visibility: **Public** (required for free Render deployment)
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

### Option B: Using GitHub CLI
```bash
gh repo create companyintel-ai --public --description "Autonomous AI Company Intelligence Platform"
```

---

## Step 2: Push Code to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/companyintel-ai.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

**Verify**: Go to your GitHub repository URL and confirm all files are there (except `.env`)

---

## Step 3: Create Render Account

1. Go to https://render.com
2. Click "Get Started" or "Sign Up"
3. Sign up with GitHub (recommended) or email
4. Verify your email if required

---

## Step 4: Deploy Using Render Blueprint

### 4.1 Connect GitHub Repository

1. In Render Dashboard, click **"New +"** (top right)
2. Select **"Blueprint"**
3. Click **"Connect GitHub"** if not already connected
4. Authorize Render to access your repositories
5. Select your repository: `companyintel-ai`
6. Click **"Connect"**

### 4.2 Render Detects Configuration

Render will automatically detect `backend/render.yaml` and show:
- ✅ Web Service: `companyintel-api`
- ✅ Redis Service: `companyintel-redis`

### 4.3 Review Services

You should see:

**Service 1: companyintel-api**
- Type: Web Service
- Environment: Python
- Region: Oregon
- Plan: Free
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Service 2: companyintel-redis**
- Type: Redis
- Region: Oregon
- Plan: Free

### 4.4 Click "Apply"

Render will create both services and start deploying.

---

## Step 5: Add Environment Variables

**IMPORTANT**: You must add these environment variables for the app to work!

### 5.1 Navigate to Web Service Settings

1. Click on **"companyintel-api"** service
2. Go to **"Environment"** tab in the left sidebar
3. Click **"Add Environment Variable"**

### 5.2 Add Each Variable

Add these one by one:

| Key | Value | Notes |
|-----|-------|-------|
| `YUTORI_API_KEY` | `your_yutori_api_key_here` | Get from Yutori dashboard |
| `TAVILY_API_KEY` | `your_tavily_api_key_here` | Get from Tavily dashboard |
| `OPENAI_API_KEY` | `your_openai_api_key_here` | Get from OpenAI dashboard |
| `ALPHA_VANTAGE_API_KEY` | `your_alpha_vantage_key_here` | Get from Alpha Vantage |
| `NEO4J_URI` | `your_neo4j_uri_here` | Format: bolt://host:port |
| `NEO4J_PASSWORD` | `your_neo4j_password_here` | Neo4j authentication |

**Note**: `REDIS_URL` is automatically set by Render from the Redis service connection.

### 5.3 Save Changes

After adding all variables, the service will automatically redeploy.

---

## Step 6: Monitor Deployment

### 6.1 Watch Build Logs

1. Go to **"Logs"** tab
2. Watch the build process:
   ```
   Installing dependencies...
   Collecting fastapi==0.109.0
   ...
   Successfully installed [packages]
   Build successful!
   Starting service...
   ```

### 6.2 Wait for "Live" Status

- Build time: ~2-3 minutes
- Status will change from "Building" → "Live"
- You'll see a green "Live" badge

### 6.3 Get Your URL

Once live, you'll see your service URL:
```
https://companyintel-api.onrender.com
```

---

## Step 7: Test Deployed Application

### 7.1 Test Health Endpoint

Open in browser or use curl:
```bash
curl https://companyintel-api.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "neo4j": "connected",
    "redis": "connected",
    "yutori": "available",
    "tavily": "available"
  },
  "version": "1.0.0"
}
```

### 7.2 Test API Documentation

Open in browser:
```
https://companyintel-api.onrender.com/docs
```

You should see the interactive Swagger UI with all endpoints.

### 7.3 Test Company Analysis

Using curl:
```bash
curl -X POST https://companyintel-api.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Stripe",
    "options": {
      "include_apis": true,
      "include_financials": true,
      "include_competitors": true,
      "include_team": true,
      "include_news": true,
      "include_graph": true
    }
  }'
```

Expected response:
```json
{
  "session_id": "uuid-here",
  "status": "processing",
  "estimated_time_seconds": 30,
  "websocket_url": "wss://companyintel-api.onrender.com/ws/progress/uuid-here"
}
```

### 7.4 Test Cached Data Retrieval

After analysis completes (wait 30 seconds), test:
```bash
curl https://companyintel-api.onrender.com/api/company/stripe
```

Should return full company data!

---

## Step 8: Update Frontend Configuration

Once backend is deployed, update frontend to use production URL:

### 8.1 Create Production Environment File

Create `frontend/.env.production`:
```env
VITE_API_URL=https://companyintel-api.onrender.com
```

### 8.2 Update API Client (Optional)

The frontend is already configured to use environment variables, so it will automatically use the production URL when built.

---

## Step 9: Deploy Frontend (Optional)

### Option A: Deploy to Render Static Site

1. In Render Dashboard, click **"New +"**
2. Select **"Static Site"**
3. Connect same GitHub repository
4. Configure:
   - **Name**: `companyintel-frontend`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
5. Add environment variable:
   - `VITE_API_URL`: `https://companyintel-api.onrender.com`
6. Click **"Create Static Site"**

### Option B: Deploy to Vercel (Faster)

```bash
cd frontend
npm install -g vercel
vercel --prod
```

### Option C: Use Test Page

For quick demos, just update `test-frontend.html`:
```javascript
const API_URL = 'https://companyintel-api.onrender.com/api';
```

Then host it anywhere (GitHub Pages, Netlify, etc.)

---

## 🎯 Verification Checklist

After deployment, verify:

- [ ] Backend URL is accessible
- [ ] `/api/health` returns healthy status
- [ ] Neo4j shows "connected"
- [ ] Redis shows "connected"
- [ ] `/docs` shows API documentation
- [ ] Can analyze a company (POST /api/analyze)
- [ ] Can retrieve cached data (GET /api/company/stripe)
- [ ] WebSocket connection works (check logs)
- [ ] All environment variables are set
- [ ] No errors in Render logs

---

## 🐛 Troubleshooting

### Issue: Build Fails

**Check**:
1. Logs tab for specific error
2. Python version (should be 3.11)
3. All dependencies in requirements.txt

**Fix**: Update render.yaml if needed

### Issue: Service Won't Start

**Check**:
1. Environment variables are all set
2. Port is using `$PORT` variable
3. Start command is correct

**Fix**: Check logs for specific error

### Issue: Neo4j/Redis Not Connected

**Check**:
1. Environment variables are correct
2. Neo4j URI format (bolt:// not neo4j+s://)
3. Redis URL from Render service

**Fix**: Update environment variables

### Issue: 502 Bad Gateway

**Cause**: Service is still starting or crashed

**Fix**: 
1. Wait 2-3 minutes for cold start
2. Check logs for errors
3. Verify environment variables

### Issue: WebSocket Not Working

**Check**:
1. URL uses `wss://` not `ws://`
2. CORS is configured correctly
3. Render allows WebSocket connections (it does)

**Fix**: Check frontend WebSocket URL format

---

## 📊 Render Free Tier Limits

Be aware of these limits:

- **Web Service**: 750 hours/month (enough for 24/7)
- **Redis**: 25MB storage
- **Bandwidth**: 100GB/month
- **Build Minutes**: 500 minutes/month
- **Cold Starts**: Service sleeps after 15 min inactivity

**For Hackathon**: These limits are more than sufficient!

---

## 🎉 Success!

Once everything is working, you'll have:

✅ **Backend API**: `https://companyintel-api.onrender.com`
✅ **API Docs**: `https://companyintel-api.onrender.com/docs`
✅ **Health Check**: `https://companyintel-api.onrender.com/api/health`
✅ **Redis**: Managed by Render
✅ **Neo4j**: Connected and working
✅ **Auto-deploy**: Push to GitHub = auto-deploy

---

## 📝 For Hackathon Submission

Use these URLs in your Devpost submission:

- **Live Demo**: `https://companyintel-api.onrender.com/docs`
- **GitHub**: `https://github.com/YOUR_USERNAME/companyintel-ai`
- **API Health**: `https://companyintel-api.onrender.com/api/health`

---

## 🚀 Next Steps

1. Test all endpoints thoroughly
2. Pre-cache demo companies (Stripe, OpenAI)
3. Create demo video showing the deployed app
4. Update README with deployed URLs
5. Submit to hackathon!

**You're ready to win! 🏆**
