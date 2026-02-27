# Quick Reference - Hackathon Day

## ⏰ Timeline
- **9:30 AM** - Doors open
- **9:45 AM** - Keynote
- **11:00 AM** - START CODING
- **1:30 PM** - Lunch
- **4:30 PM** - SUBMISSION DEADLINE (HARD STOP)
- **5:00 PM** - Presentations
- **7:00 PM** - Awards

## ✅ Requirements Checklist
- [ ] Use 3+ sponsor tools (you use 6-8)
- [ ] Build autonomous agents
- [ ] Submit by 4:30 PM
- [ ] 3-minute demo video
- [ ] GitHub repo
- [ ] Devpost submission

## 🎯 Your Project: CompanyIntel

**Elevator Pitch:** Autonomous AI agents that analyze any company in 30 seconds - extracting APIs, competitors, financials, team, news, and building a knowledge graph.

**Sponsor Tools (MVP):**
1. Yutori (Research + Browsing + Scouting)
2. Neo4j (Knowledge graph)
3. Tavily (Search)
4. OpenAI (Analysis)
5. Render (5 features: Web Service, Workers, Cron, PostgreSQL, Redis)

**Optional Extensions:**
6. Modulate (Voice analysis) - Hour 5
7. Fastino Labs (Entity extraction) - Hour 6

## 🏆 Prize Tracks

### Render Track ($1,000 / $600 / $400 credits)
**Requirement:** 2+ Render features
**You use:** 5 features ✅

### Yutori Track ($1,500 + $1,000 credits / $1,000 + $500 credits)
**Requirement:** Creative use of Yutori APIs
**You use:** All 3 APIs uniquely ✅

### Neo4j Track ($1,000 / $500 / $250 gift cards)
**Requirement:** Advanced graph usage
**You use:** 8 relationship types, visual exploration ✅

## 📋 Implementation Plan

### Hour 1: Core Infrastructure
- [ ] FastAPI project setup
- [ ] Environment variables
- [ ] Basic API endpoints (analyze, get_company, health)
- [ ] Neo4j and Redis connections
- [ ] Test with mock data

### Hour 2: Services Implementation
- [ ] ResearchService (Yutori Research API)
- [ ] BrowsingService (Yutori Browsing API)
- [ ] Basic caching
- [ ] Test end-to-end with one company

### Hour 3: Advanced Features
- [ ] FinancialService
- [ ] CompetitorService
- [ ] SentimentService
- [ ] GraphService (Neo4j)

### Hour 4: Integration & Polish
- [ ] WebSocket progress updates
- [ ] Pre-cache 10-15 demo companies
- [ ] Test all endpoints
- [ ] Deploy to Render

### Hour 5 (Optional): Modulate
- [ ] Voice analysis service
- [ ] API endpoint
- [ ] Frontend voice tab

### Hour 6 (Optional): Fastino Labs
- [ ] Entity extraction service
- [ ] Enhanced research/competitor services
- [ ] Frontend entity visualization

## 🎬 3-Minute Demo Script

### 0:00-0:30 - Opening
"Hi, I'm [name]. We built CompanyIntel - autonomous AI agents that analyze any company in 30 seconds. Imagine you're evaluating APIs, researching prospects, or doing due diligence. This normally takes 5+ hours. Watch this..."

### 0:30-2:00 - Live Demo
[Type "Stripe"]
- Show real-time progress (7 stages)
- Dashboard appears
- Click through tabs: Overview, APIs, Market, Financials, Team, News
- Show Neo4j knowledge graph

### 2:00-2:45 - Technical
"Under the hood:
- 3 Yutori APIs in parallel
- Neo4j with 8 relationship types
- Tavily searches 8+ sources
- OpenAI analyzes sentiment
- Render: 5 features (Web Service, Workers, Cron, PostgreSQL, Redis)
- 30 seconds, fully autonomous"

### 2:45-3:00 - Business Value
"Saves 5+ hours per company. Serves sales, developers, investors, job seekers. $500M+ market opportunity. Thank you!"

## 🔑 API Keys Needed

```bash
# Yutori
YUTORI_API_KEY=your_key

# Neo4j Aura (free tier)
NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Tavily
TAVILY_API_KEY=your_key

# OpenAI
OPENAI_API_KEY=your_key

# Render (auto-configured)
REDIS_URL=redis://...
DATABASE_URL=postgresql://...

# Optional (Step 2)
MODULATE_API_KEY=your_key

# Optional (Step 3)
FASTINO_API_KEY=your_key
```

## 🚀 Deployment Commands

### Backend (Render Web Service)
```bash
# render.yaml already configured
git push origin main
# Render auto-deploys
```

### Frontend (Render Static Site)
```bash
npm run build
# Render auto-deploys from dist/
```

### Pre-cache Companies
```bash
python scripts/cache_companies.py
```

## 🎯 Demo Companies (Pre-cache These)

1. **Stripe** - Best demo (payments, APIs)
2. **OpenAI** - AI company
3. **Shopify** - E-commerce
4. **Twilio** - API company
5. **Vercel** - Developer tools
6. **Supabase** - Database
7. **Cloudflare** - Infrastructure
8. **Datadog** - Monitoring
9. **MongoDB** - Database
10. **Snowflake** - Data warehouse

## 🐛 Backup Plans

### If Live Demo Fails
1. Switch to pre-cached Stripe (instant)
2. Show video recording
3. Walk through screenshots

### If API Rate Limits
1. Use cached companies only
2. Explain: "Production would have higher limits"

### If Graph Doesn't Render
1. Show data in table format
2. Show Neo4j Aura dashboard

## 📊 Judging Criteria (20% each)

1. **Autonomy** - Agents act independently ✅
2. **Idea** - Solves real problem ✅
3. **Technical** - Quality implementation ✅
4. **Tool Use** - 6+ sponsor tools ✅
5. **Presentation** - 3-minute demo ✅

## 🎤 Judges to Impress

### Render Judges
- Ojus Save, Shiffra Williams
- **Pitch:** "We use 5 Render features..."

### Yutori Judge
- Dhruv Batra (Co-founder)
- **Pitch:** "We use all 3 Yutori APIs uniquely..."

### Neo4j Judge
- Nyah Macklin
- **Pitch:** "8 relationship types, interactive graph..."

### Technical Judges
- Jon Turdiev (AWS), Vladimir de Turckheim (Node.js), Sahil Sachdeva (LinkedIn)
- **Pitch:** "FastAPI async, Neo4j graph, Redis cache, scales horizontally..."

### Business Judges
- Anushk Mittal (Shapes), Andrew Bihl (Numeric), Carter Huffman (Modulate)
- **Pitch:** "Saves 5+ hours, $500M+ market, serves 4 user types..."

## ❓ Common Questions & Answers

**Q: How do you handle API rate limits?**
A: Exponential backoff, caching (1 hour), API key rotation for production.

**Q: What if Yutori is slow?**
A: Parallel execution with asyncio, timeout handling, fallback to cache.

**Q: How does Neo4j scale?**
A: Indexed queries, depth limit 2-3, pagination for large graphs.

**Q: Who would pay for this?**
A: Sales teams ($50/user/mo), developers ($500/mo), investors ($1000/mo), recruiters ($200/mo).

**Q: What's your competitive advantage?**
A: Only platform combining API extraction, competitor analysis, and knowledge graphs autonomously.

**Q: What would you build next?**
A: Comparison mode, alerts for competitor changes, export to PDF/Notion/Slack.

## ✅ Pre-Demo Checklist

### 1 Hour Before
- [ ] Test all pre-cached companies
- [ ] Verify API keys have credits
- [ ] Check deployment is live
- [ ] Test on Chrome, Firefox, Safari
- [ ] Record backup video
- [ ] Take backup screenshots
- [ ] Practice 3-minute pitch (time it!)
- [ ] Charge laptop fully
- [ ] Phone hotspot ready

### During Demo
- [ ] Start with Stripe
- [ ] Have OpenAI as backup
- [ ] Dev tools closed
- [ ] Postman ready
- [ ] Stay calm
- [ ] Smile at judges

## 🎯 Success Metrics

### Must Have
- [ ] 5+ companies working
- [ ] Real-time progress
- [ ] 3+ tabs working
- [ ] Graph renders
- [ ] Deployed
- [ ] 3-min demo rehearsed

### Should Have
- [ ] All 6 tabs working
- [ ] Interactive graph
- [ ] 10+ companies cached
- [ ] Error handling
- [ ] Video backup

### Nice to Have
- [ ] 15+ companies cached
- [ ] Modulate integration
- [ ] Fastino integration
- [ ] Export feature

## 🚨 Critical Reminders

1. **SUBMIT BY 4:30 PM** - Late submissions cut off
2. **3 MINUTES MAX** - Judges will cut you off
3. **PRE-CACHE COMPANIES** - Don't rely on live APIs
4. **PRACTICE DEMO** - Time it multiple times
5. **BACKUP PLANS** - Video, screenshots, cached data
6. **STAY CALM** - Demos always break, have fallbacks

## 📱 Emergency Contacts

- **Hackathon Organizers:** Check Luma page
- **Render Support:** community.render.com
- **Yutori Support:** Check docs.yutori.com
- **Neo4j Support:** community.neo4j.com

## 🎉 After Demo

- [ ] Note bugs/issues
- [ ] Collect judge feedback
- [ ] Network with teams
- [ ] Celebrate! 🚀

---

## 💡 Key Insights

**Your Strengths:**
- Comprehensive (6 data categories)
- Autonomous (no manual intervention)
- Multi-tool (6-8 sponsor tools)
- Visual (knowledge graph)
- Practical (real problem)
- Scalable (proper architecture)

**Your Pitch:**
"Autonomous AI agents that save 5+ hours of company research by analyzing APIs, competitors, financials, team, and news in 30 seconds - powered by Yutori, Neo4j, and Render."

**Your Differentiator:**
"Only platform combining API documentation extraction, competitor analysis, and knowledge graphs in one autonomous system."

---

**Good luck! You've got this! 🚀**
