# 🚀 CompanyIntel - Quick Start Guide

Get CompanyIntel running in 5 minutes!

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- Git installed

## Step 1: Clone & Setup (1 minute)

```bash
# Clone the repository
git clone <your-repo-url>
cd companyintel-ai

# Or if you already have the files, just navigate to the directory
cd companyintel-ai
```

## Step 2: Start Backend (2 minutes)

### On Unix/Mac/Linux:
```bash
cd backend
chmod +x start.sh
./start.sh
```

### On Windows:
```bash
cd backend
start.bat
```

The script will:
- Create a virtual environment
- Install all dependencies
- Create .env from .env.example (if needed)
- Start the FastAPI server on http://localhost:8000

**Note:** The backend works with mock data even without API keys!

## Step 3: Start Frontend (2 minutes)

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will start on http://localhost:5173

## Step 4: Try It Out! (30 seconds)

1. Open http://localhost:5173 in your browser
2. Type "Stripe" or "OpenAI" in the search box
3. Click "Analyze Company"
4. Watch the 7-stage progress indicator
5. Explore the dashboard with 3 tabs of data!

## 🎉 That's It!

You now have a fully functional AI company intelligence platform running locally.

## 🔧 Optional: Add Real API Keys

To use real APIs instead of mock data:

1. Edit `backend/.env` file
2. Add your API keys:
   ```env
   YUTORI_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
   NEO4J_PASSWORD=your_password
   ```
3. Restart the backend server

Get free API keys:
- Yutori: https://yutori.com
- Neo4j Aura: https://neo4j.com/cloud/aura/
- Tavily: https://tavily.com
- OpenAI: https://platform.openai.com

## 📚 What to Explore

### Backend API Docs
Visit http://localhost:8000/docs for interactive API documentation

### Try These Companies
- Stripe (full mock data)
- OpenAI (full mock data)
- Any other company name (generic mock data)

### Explore Features
- Real-time progress updates (7 stages)
- Company overview with metrics
- Products & API catalog
- Competitor analysis
- And more!

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Make sure Python 3.11+ is installed
python3 --version

# Try manual setup
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend won't start?
```bash
# Make sure Node.js is installed
node --version

# Try manual setup
cd frontend
npm install
npm run dev
```

### Port already in use?
- Backend: Change port in start script (default: 8000)
- Frontend: Change port in vite.config.ts (default: 5173)

### WebSocket not connecting?
- Make sure backend is running on http://localhost:8000
- Check browser console for errors
- Try refreshing the page

## 🚀 Next Steps

1. **Read README.md** for full documentation
2. **Check PROJECT_SUMMARY.md** for technical details
3. **Explore the code** in backend/app and frontend/src
4. **Deploy to Render** using backend/render.yaml

## 💡 Tips

- The system works great with mock data for demos
- Add real API keys for production use
- Check /docs endpoint for API documentation
- Use Chrome DevTools to see WebSocket messages
- Redis and Neo4j are optional for basic functionality

## 🎯 Demo Script

Perfect for showing to others:

1. "This is CompanyIntel - AI agents that analyze companies in 30 seconds"
2. Type "Stripe" and click Analyze
3. "Watch 7 autonomous agents work in parallel"
4. Show the progress indicator updating in real-time
5. "Here's the complete intelligence report"
6. Click through the tabs showing different data
7. "All of this in 30 seconds, fully autonomous"

## 📧 Need Help?

- Check the README.md for detailed documentation
- Review PROJECT_SUMMARY.md for architecture details
- Open an issue on GitHub
- Check the /docs endpoint for API reference

---

**Happy Hacking! 🚀**
