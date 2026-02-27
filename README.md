# 🚀 CompanyIntel - Autonomous Company Intelligence Platform

**Built for Autonomous Agents Hackathon 2026**

CompanyIntel is an autonomous AI platform that analyzes any company in 30 seconds, providing comprehensive intelligence across 6 key categories using multiple AI agents working in parallel.

## ✨ Features

- **Company Overview** - Founding, headquarters, employees, mission, industry
- **Products & APIs** - 200+ API endpoints cataloged, pricing tiers, SDK languages
- **Market Intelligence** - Competitor analysis, market positioning, differentiation
- **Financial Data** - Funding rounds, valuation, revenue estimates, growth metrics
- **Team & Culture** - Leadership profiles, tech stack, hiring focus
- **News Sentiment** - Real-time sentiment analysis from 50+ sources
- **Knowledge Graph** - Interactive Neo4j visualization with 8+ relationship types

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **Neo4j Aura** - Graph database for knowledge relationships
- **Redis** - Caching layer for instant results
- **Yutori** - Research, Browsing, and Scouting APIs
- **Tavily** - AI-optimized search
- **OpenAI** - Sentiment analysis and insights

### Frontend
- **React 18** with TypeScript
- **Material-UI** - Component library
- **React Query** - Data fetching and caching
- **Recharts** - Data visualization
- **WebSocket** - Real-time progress updates

### Deployment
- **Render** - Web Service + Background Workers + Redis

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Redis (or use Render Redis)
- Neo4j Aura account (free tier)

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 🔑 API Keys Required

Get free API keys from:
- **Yutori**: https://yutori.com (Research, Browsing APIs)
- **Neo4j Aura**: https://neo4j.com/cloud/aura/ (Graph database)
- **Tavily**: https://tavily.com (AI search)
- **OpenAI**: https://platform.openai.com (GPT models)
- **Alpha Vantage**: https://www.alphavantage.co (Financial data - optional)

## 📊 How It Works

1. **User enters company name** (e.g., "Stripe")
2. **7 autonomous agents activate in parallel**:
   - Research Agent (Yutori Research API)
   - Browsing Agent (Yutori Browsing API)
   - Financial Agent (Multiple sources)
   - Competitor Agent (Tavily + Analysis)
   - Sentiment Agent (Tavily + OpenAI)
   - Team Agent (Web scraping)
   - Graph Agent (Neo4j)
3. **Real-time progress updates** via WebSocket
4. **Complete analysis in ~30 seconds**
5. **Interactive dashboard** with 6 tabs + knowledge graph

## 🎯 Use Cases

- **Developers** - Evaluate APIs before integration
- **Sales Teams** - Research prospects before outreach
- **Investors** - Due diligence on potential investments
- **Job Seekers** - Research companies before applying
- **Product Managers** - Competitive intelligence

## 📈 Demo Companies

Pre-configured with mock data for instant demos:
- Stripe
- OpenAI
- Shopify
- Twilio
- Vercel
- Supabase
- And more...

## 🏗️ Architecture

```
Frontend (React) → FastAPI Backend → Services:
                                     ├─ Yutori Research API
                                     ├─ Yutori Browsing API
                                     ├─ Tavily Search
                                     ├─ OpenAI Analysis
                                     ├─ Neo4j Graph DB
                                     └─ Redis Cache
```

## 🚢 Deployment

### Deploy to Render

1. Push code to GitHub
2. Connect Render to your repository
3. Use `backend/render.yaml` for configuration
4. Add environment variables in Render dashboard
5. Deploy!

Backend will auto-deploy on push to main branch.

### Frontend Deployment

```bash
cd frontend
npm run build
# Deploy dist/ folder to Render Static Site or Vercel
```

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

- `POST /api/analyze` - Start company analysis
- `GET /api/company/{id}` - Get analysis results
- `GET /api/graph/{id}` - Get knowledge graph
- `WS /ws/progress/{session_id}` - Real-time progress
- `GET /api/health` - Health check

## 🎨 Features Showcase

### Real-time Progress Tracking
7-stage progress indicator with WebSocket updates:
1. Researching company overview
2. Extracting API documentation
3. Analyzing competitors
4. Gathering financial data
5. Analyzing team & culture
6. Processing news & sentiment
7. Building knowledge graph

### Knowledge Graph
Interactive Neo4j visualization showing:
- Company → Products relationships
- Company → Competitors relationships
- Company → Technologies relationships
- Company → People relationships
- And more...

### Comprehensive Data
- 200+ API endpoints cataloged
- 5+ competitors analyzed
- 50+ news articles processed
- 8+ relationship types in graph
- 45+ data sources aggregated

## 🏆 Hackathon Compliance

### Sponsor Tools Used (6+)
✅ Yutori (Research, Browsing, Scouting APIs)
✅ Neo4j (Knowledge graph database)
✅ Tavily (AI-optimized search)
✅ OpenAI (Analysis and sentiment)
✅ Render (Web Service + Background Workers + Redis)

### Render Track (2+ features)
✅ Web Service - FastAPI backend
✅ Background Workers - Async processing
✅ Redis - Caching layer

### Autonomous Agents
✅ 7 agents working independently
✅ Parallel execution with asyncio
✅ No manual intervention required
✅ Real-time progress tracking

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Contact

Built by [Your Team Name] for Autonomous Agents Hackathon 2026

- GitHub: [Your GitHub]
- Demo: [Deployed URL]
- Video: [Demo Video URL]

## 🙏 Acknowledgments

- Yutori for powerful web agent APIs
- Neo4j for graph database technology
- Render for seamless deployment
- All hackathon sponsors and organizers

---

**⭐ Star this repo if you find it useful!**
