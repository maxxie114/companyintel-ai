# 🔧 Troubleshooting Guide

Common issues and solutions for CompanyIntel.

## Backend Issues

### Issue: "Command 'python' not found"
**Solution:**
```bash
# Try python3 instead
python3 --version

# Or install Python 3.11+
# Ubuntu/Debian:
sudo apt install python3.11

# Mac:
brew install python@3.11
```

### Issue: "Module not found" errors
**Solution:**
```bash
# Make sure you're in the virtual environment
cd backend
source venv/bin/activate  # Unix/Mac
# OR
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Address already in use" (Port 8000)
**Solution:**
```bash
# Find and kill the process using port 8000
# Unix/Mac:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change the port in start script
uvicorn app.main:app --reload --port 8001
```

### Issue: Redis connection failed
**Solution:**
```bash
# Install Redis locally
# Ubuntu/Debian:
sudo apt install redis-server
sudo systemctl start redis

# Mac:
brew install redis
brew services start redis

# Or use Docker:
docker run -d -p 6379:6379 redis

# Or disable Redis in code (uses in-memory fallback)
# The system will work without Redis, just slower
```

### Issue: Neo4j connection failed
**Solution:**
```bash
# Option 1: Create free Neo4j Aura instance
# Visit: https://neo4j.com/cloud/aura/

# Option 2: Run Neo4j locally with Docker
docker run -d \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Option 3: Skip Neo4j (graph features won't work)
# Leave NEO4J_URI empty in .env
# The system will work without Neo4j
```

### Issue: "No module named 'app'"
**Solution:**
```bash
# Make sure you're running from the backend directory
cd backend
uvicorn app.main:app --reload

# Check that app/__init__.py exists
ls app/__init__.py
```

## Frontend Issues

### Issue: "npm: command not found"
**Solution:**
```bash
# Install Node.js
# Visit: https://nodejs.org/

# Or use nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### Issue: "Cannot find module" errors
**Solution:**
```bash
# Delete node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: "Port 5173 already in use"
**Solution:**
```bash
# Kill the process
# Unix/Mac:
lsof -ti:5173 | xargs kill -9

# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or change port in vite.config.ts
server: {
  port: 5174,
  ...
}
```

### Issue: WebSocket connection fails
**Symptoms:**
- Progress indicator doesn't update
- "Connecting to server..." message persists

**Solution:**
```bash
# 1. Make sure backend is running
curl http://localhost:8000/api/health

# 2. Check WebSocket URL in browser console
# Should be: ws://localhost:8000/ws/progress/{session_id}

# 3. Check CORS settings in backend
# Make sure frontend URL is allowed

# 4. Try different browser (Chrome recommended)

# 5. Check firewall settings
# Make sure ports 8000 and 5173 are open
```

### Issue: "Failed to fetch" errors
**Solution:**
```bash
# 1. Verify backend is running
curl http://localhost:8000/api/health

# 2. Check API URL in frontend
# Should be: http://localhost:8000

# 3. Check CORS configuration in backend
# backend/app/main.py should have:
allow_origins=["*"]  # or ["http://localhost:5173"]

# 4. Clear browser cache and reload
```

## API Integration Issues

### Issue: Yutori API errors
**Solution:**
```bash
# 1. Check API key is set
echo $YUTORI_API_KEY

# 2. Verify API key is valid
# Visit: https://yutori.com/dashboard

# 3. Check API rate limits
# The system uses mock data as fallback

# 4. For demos, just use mock data
# Leave YUTORI_API_KEY empty in .env
```

### Issue: Neo4j authentication failed
**Solution:**
```bash
# 1. Check credentials in .env
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# 2. Test connection
# Visit Neo4j Aura console and verify instance is running

# 3. Check URI format
# Should start with neo4j+s:// for Aura
# Should start with neo4j:// for local

# 4. Verify firewall allows connection
```

## Data Issues

### Issue: No data showing in dashboard
**Solution:**
```bash
# 1. Check browser console for errors
# Press F12 and look at Console tab

# 2. Verify API response
curl http://localhost:8000/api/company/stripe

# 3. Check if analysis completed
# Look for "completed" message in progress

# 4. Try different company name
# "Stripe" and "OpenAI" have full mock data
```

### Issue: Progress stuck at certain stage
**Solution:**
```bash
# 1. Check backend logs
# Look for error messages in terminal

# 2. Verify Redis is working
redis-cli ping
# Should return: PONG

# 3. Check WebSocket connection
# Browser console should show WebSocket messages

# 4. Restart backend
# Kill and restart the uvicorn process
```

## Deployment Issues

### Issue: Render deployment fails
**Solution:**
```bash
# 1. Check render.yaml syntax
# Make sure indentation is correct

# 2. Verify Python version
# Should be 3.11.0 in render.yaml

# 3. Check environment variables
# All required vars should be set in Render dashboard

# 4. Check build logs
# Look for specific error messages in Render dashboard

# 5. Verify requirements.txt
# Make sure all dependencies are listed
```

### Issue: Deployed app not working
**Solution:**
```bash
# 1. Check service status in Render dashboard
# Should show "Live"

# 2. Verify environment variables
# All API keys should be set

# 3. Check logs
# Look for startup errors

# 4. Test health endpoint
curl https://your-app.onrender.com/api/health

# 5. Check CORS settings
# Update allow_origins for production domain
```

## Performance Issues

### Issue: Analysis takes too long
**Solution:**
```bash
# 1. Check if Redis is working
# Caching should speed up repeat requests

# 2. Verify parallel execution
# All 7 services should run in parallel

# 3. Check API response times
# Some APIs may be slow

# 4. Use mock data for demos
# Instant results without API calls
```

### Issue: High memory usage
**Solution:**
```bash
# 1. Limit concurrent analyses
# Don't run too many at once

# 2. Check for memory leaks
# Restart backend periodically

# 3. Reduce cache TTL
# Lower CACHE_TTL_SECONDS in .env

# 4. Use production ASGI server
# gunicorn instead of uvicorn --reload
```

## Development Issues

### Issue: Hot reload not working
**Solution:**
```bash
# Backend:
# Make sure using --reload flag
uvicorn app.main:app --reload

# Frontend:
# Vite should auto-reload
# Check vite.config.ts

# If still not working, restart both servers
```

### Issue: TypeScript errors in frontend
**Solution:**
```bash
# 1. Check tsconfig.json
# Make sure it's properly configured

# 2. Restart TypeScript server
# In VS Code: Cmd+Shift+P -> "Restart TS Server"

# 3. Check type definitions
# Make sure @types packages are installed

# 4. Clear TypeScript cache
rm -rf frontend/node_modules/.cache
```

## Testing Issues

### Issue: Can't test without API keys
**Solution:**
```bash
# Good news! The system works with mock data
# Just leave API keys empty in .env

# Mock data is available for:
# - Stripe (full data)
# - OpenAI (full data)
# - Any other company (generic data)

# Perfect for demos and testing!
```

### Issue: WebSocket test fails
**Solution:**
```bash
# 1. Use a WebSocket testing tool
# Chrome extension: "Simple WebSocket Client"

# 2. Test URL format
ws://localhost:8000/ws/progress/test-session-id

# 3. Check backend logs
# Should show "WebSocket connected"

# 4. Try different session ID
# Use a fresh UUID
```

## Quick Fixes

### Reset Everything
```bash
# Backend
cd backend
rm -rf venv
rm .env
./start.sh

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Check All Services
```bash
# Python
python3 --version  # Should be 3.11+

# Node
node --version  # Should be 18+

# Redis (optional)
redis-cli ping  # Should return PONG

# Backend
curl http://localhost:8000/api/health

# Frontend
curl http://localhost:5173
```

### Enable Debug Mode
```bash
# Backend - add to .env
LOG_LEVEL=DEBUG

# Frontend - check browser console
# Press F12 -> Console tab

# Backend logs
# Watch terminal where uvicorn is running
```

## Still Having Issues?

1. **Check the logs**
   - Backend: Terminal where uvicorn is running
   - Frontend: Browser console (F12)
   - Render: Dashboard logs

2. **Read the error message**
   - Most errors are self-explanatory
   - Google the error message
   - Check Stack Overflow

3. **Try the basics**
   - Restart both servers
   - Clear browser cache
   - Check all ports are available
   - Verify all dependencies installed

4. **Use mock data**
   - System works without any API keys
   - Perfect for testing and demos
   - Just leave .env keys empty

5. **Check documentation**
   - README.md for setup
   - PROJECT_SUMMARY.md for architecture
   - QUICKSTART.md for quick setup

## Emergency Demo Mode

If everything fails before your demo:

```bash
# 1. Use mock data (no API keys needed)
cd backend
# Leave .env empty or use .env.example
./start.sh

# 2. Use pre-tested companies
# Type "Stripe" or "OpenAI" in search
# These have full mock data

# 3. Have screenshots ready
# Take screenshots of working version
# Use as backup if live demo fails

# 4. Record video beforehand
# 3-minute demo video
# Show it if live demo has issues
```

---

**Remember:** The system is designed to work with mock data, so you can always demo without API keys!
