# 🚀 Quick Deployment Commands

## Step-by-Step Commands to Deploy

### 1. Create GitHub Repository
```bash
# Go to https://github.com/new and create repository named: companyintel-ai
# Make it PUBLIC
# Don't initialize with README
```

### 2. Add Remote and Push
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/companyintel-ai.git

# Verify remote
git remote -v

# Push to GitHub
git push -u origin main
```

### 3. Deploy to Render
```
1. Go to https://render.com
2. Sign up/Login with GitHub
3. Click "New +" → "Blueprint"
4. Select your repository: companyintel-ai
5. Click "Connect"
6. Click "Apply"
```

### 4. Add Environment Variables in Render Dashboard

Go to your service → Environment tab → Add these:

```
YUTORI_API_KEY=your_yutori_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEO4J_URI=your_neo4j_uri_here
NEO4J_PASSWORD=your_neo4j_password_here
REDIS_URL=automatically_set_by_render
```

### 5. Test Deployed App

```bash
# Replace YOUR_APP_URL with your Render URL
curl https://YOUR_APP_URL.onrender.com/api/health

# Should return:
# {"status":"healthy","services":{"neo4j":"connected","redis":"connected",...}}
```

---

## Current Git Status

✅ **Committed**: 52 files, 8,400+ lines of code
✅ **Branch**: main
✅ **Ready to push**: Yes
✅ **.env ignored**: Yes (verified)

---

## What Happens When You Push

1. Code goes to GitHub
2. Render detects the push
3. Render reads `backend/render.yaml`
4. Render creates:
   - Web Service (FastAPI backend)
   - Redis instance
5. Render installs dependencies
6. Render starts your app
7. You get a public URL!

---

## After Deployment

Your app will be live at:
```
https://companyintel-api-XXXXX.onrender.com
```

Test endpoints:
- `/` - Welcome message
- `/api/health` - Health check
- `/docs` - API documentation
- `/api/analyze` - Analyze company
- `/api/company/{slug}` - Get cached data

---

## Need Help?

1. Check `RENDER_DEPLOYMENT_GUIDE.md` for detailed steps
2. Check Render logs if deployment fails
3. Verify all environment variables are set
4. Test locally first if issues occur

**You're ready to deploy! 🚀**
