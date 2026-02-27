# 🚀 START HERE - CompanyIntel Build Instructions

## For the Coding Agent

You are building **CompanyIntel** - an autonomous company intelligence platform for a hackathon. This is a complete full-stack application that must be built in 5.5 hours.

---

## 📋 Your Task

Build a production-ready application where autonomous AI agents analyze any company in 30 seconds, providing:
- Company overview and metrics
- API documentation catalog (200+ endpoints)
- Competitor analysis
- Financial data
- Team intelligence
- News sentiment
- Interactive Neo4j knowledge graph

---

## 📚 Step 1: Read Documentation (15 minutes)

**Read these files in this exact order:**

### 1. DESIGN.md (PRIMARY SPEC - READ COMPLETELY)
- 2000+ lines of complete technical specification
- **API Contract section is CRITICAL** - follow it exactly
- Backend implementation guide with code examples
- Frontend implementation guide with React components
- Data models (TypeScript interfaces)
- Deployment configuration

### 2. QUICK_REFERENCE.md (TIMELINE)
- Hour-by-hour implementation plan
- Priority checklist
- Demo script
- Success metrics

### 3. DESIGN_ADDITIONS.md (OPTIONAL EXTENSIONS)
- Step 2: Modulate integration (Hour 5)
- Step 3: Fastino Labs integration (Hour 6)
- Only implement if you finish MVP early

### 4. HACKATHON_ANALYSIS.md (CONTEXT)
- Hackathon requirements
- Sponsor tool details
- Judge profiles
- Strategy and tips

---

## 🔍 Step 2: Research APIs (30 minutes)

**Before writing any code, research these APIs:**

### Core APIs (Required for MVP)

**Yutori - Web Agents**
- Main Docs: https://docs.yutori.com/
- Research API: https://docs.yutori.com/research
- Browsing API: https://docs.yutori.com/browsing
- Scouting API: https://docs.yutori.com/scouting
- Authentication: https://docs.yutori.com/authentication
- Python SDK: Check if available
- **What to learn:** How to create research tasks, browse websites, monitor changes

**Neo4j - Graph Database**
- Main Docs: https://neo4j.com/docs/
- Python Driver: https://neo4j.com/docs/python-manual/current/
- Aura Cloud: https://neo4j.com/cloud/aura/
- Cypher Queries: https://neo4j.com/docs/cypher-manual/current/
- **What to learn:** How to create nodes, relationships, query graphs

**Tavily - AI Search**
- Main Docs: https://docs.tavily.com/
- Introduction: https://docs.tavily.com/guides/introduction
- API Reference: https://docs.tavily.com/api-reference
- Python SDK: https://pypi.org/project/tavily-python/
- **What to learn:** How to search, extract content, filter results

**OpenAI - LLM Analysis**
- Main Docs: https://platform.openai.com/docs/
- API Reference: https://platform.openai.com/docs/api-reference
- Python SDK: https://pypi.org/project/openai/
- **What to learn:** How to analyze text, extract sentiment, generate insights

**Render - Deployment**
- Main Docs: https://docs.render.com/
- Web Services: https://docs.render.com/web-services
- Background Workers: https://docs.render.com/background-workers
- Cron Jobs: https://docs.render.com/cronjobs
- PostgreSQL: https://docs.render.com/databases
- Redis: https://docs.render.com/redis
- Blueprints: https://docs.render.com/blueprint-spec
- **What to learn:** How to deploy FastAPI, configure workers, use managed services

### Optional APIs (Extensions)

**Modulate - Voice Intelligence (Hour 5)**
- Website: https://www.modulate.ai/
- SDK Docs: https://sdk-docs.modulate.ai/
- **What to learn:** Voice sentiment analysis, confidence detection

**Fastino Labs - Entity Extraction (Hour 6)**
- Website: https://www.fastino.ai/
- Docs: https://fastino-1.gitbook.io/docs
- API Reference: https://fastino.ai/api-reference/gliner-2
- **What to learn:** GLiNER entity extraction, fine-tuning

---

## 🏗️ Step 3: Build the Project (4 hours)

### Hour 1: Core Infrastructure (CRITICAL - MUST COMPLETE)

**Backend Setup:**
```bash
# Create project structure
mkdir -p backend/app/{api,services,core,utils}
cd backend

# Create requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0
httpx==0.26.0
redis==5.0.1
neo4j==5.16.0
python-dotenv==1.0.0
websockets==12.0
```

**Tasks:**
1. ✅ Create FastAPI app in `app/main.py` with CORS
2. ✅ Create `app/config.py` for environment variables
3. ✅ Create `app/models.py` with Pydantic models
4. ✅ Create basic endpoints in `app/api/routes.py`:
   - POST /api/analyze
   - GET /api/company/{id}
   - GET /api/health
5. ✅ Create `app/core/database.py` for Neo4j connection
6. ✅ Create `app/core/cache.py` for Redis connection
7. ✅ Test with mock data

**Success Criteria:**
- FastAPI server runs on localhost:8000
- Health endpoint returns 200
- CORS allows frontend requests
- Neo4j and Redis connections work

### Hour 2: Services Implementation (CRITICAL - MUST COMPLETE)

**Tasks:**
1. ✅ Create `app/services/research.py`:
   - ResearchService class
   - get_company_overview() method
   - Integrate Yutori Research API
   - Parse and structure response

2. ✅ Create `app/services/browsing.py`:
   - BrowsingService class
   - extract_api_docs() method
   - Integrate Yutori Browsing API
   - Extract API endpoints and pricing

3. ✅ Create `app/core/cache.py`:
   - Redis caching functions
   - get_cached_company()
   - cache_company()
   - TTL: 1 hour

4. ✅ Test end-to-end:
   - Call /api/analyze with "Stripe"
   - Verify data is fetched and cached
   - Check Redis for cached data

**Success Criteria:**
- Yutori Research API returns company data
- Yutori Browsing API extracts API docs
- Data is cached in Redis
- End-to-end test with "Stripe" works

### Hour 3: Advanced Features (CRITICAL - MUST COMPLETE)

**Tasks:**
1. ✅ Create `app/services/financial.py`:
   - FinancialService class
   - get_financial_data() method
   - Use Yutori Research + Tavily for financial data

2. ✅ Create `app/services/competitor.py`:
   - CompetitorService class
   - find_competitors() method
   - Analyze market positioning

3. ✅ Create `app/services/sentiment.py`:
   - SentimentService class
   - analyze_news() method
   - Use Tavily for news search
   - Use OpenAI for sentiment analysis

4. ✅ Create `app/services/graph.py`:
   - GraphService class
   - build_knowledge_graph() method
   - Create 8+ relationship types in Neo4j
   - get_graph_data() for visualization

5. ✅ Create `app/core/orchestrator.py`:
   - CompanyOrchestrator class
   - analyze() method that coordinates all services
   - Run services in parallel with asyncio.gather()
   - Update progress in Redis

**Success Criteria:**
- All 6 data categories are collected
- Neo4j graph is built with nodes and relationships
- Services run in parallel
- Total analysis time < 60 seconds

### Hour 4: Frontend & Deployment (CRITICAL - MUST COMPLETE)

**Frontend Setup:**
```bash
# Create React + TypeScript + Vite project
npm create vite@latest frontend -- --template react-ts
cd frontend

# Install dependencies
npm install @mui/material @emotion/react @emotion/styled
npm install @tanstack/react-query axios
npm install recharts react-force-graph-2d
npm install react-router-dom
```

**Tasks:**
1. ✅ Create `src/api/client.ts` - Axios instance
2. ✅ Create `src/api/endpoints.ts` - API functions
3. ✅ Create `src/api/websocket.ts` - WebSocket client
4. ✅ Create `src/hooks/useWebSocket.ts` - WebSocket hook
5. ✅ Create `src/hooks/useCompanyAnalysis.ts` - Analysis hook
6. ✅ Create `src/components/CompanySearch.tsx` - Search input
7. ✅ Create `src/components/LoadingProgress.tsx` - Progress indicator
8. ✅ Create `src/components/Dashboard.tsx` - Main dashboard
9. ✅ Create `src/components/tabs/OverviewTab.tsx` - Overview tab
10. ✅ Create `src/components/tabs/APIsTab.tsx` - APIs tab
11. ✅ Create `src/components/tabs/MarketTab.tsx` - Market tab
12. ✅ Create `src/components/KnowledgeGraph.tsx` - Graph visualization
13. ✅ Create `src/App.tsx` - Main app with state management
14. ✅ Test frontend with backend

**WebSocket Implementation:**
```typescript
// CRITICAL: Implement WebSocket in app/api/websocket.py
@router.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            progress = await get_progress_updates(session_id)
            if progress:
                await websocket.send_json(progress)
                if progress.get("type") == "completed":
                    break
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        pass
```

**Deployment:**
1. ✅ Create `backend/render.yaml` (see DESIGN.md)
2. ✅ Create `frontend/render.yaml` (see DESIGN.md)
3. ✅ Push to GitHub
4. ✅ Connect Render to GitHub
5. ✅ Add environment variables in Render dashboard
6. ✅ Deploy backend and frontend
7. ✅ Test deployed application

**Pre-cache Companies:**
```python
# Create scripts/cache_companies.py
DEMO_COMPANIES = [
    "Stripe", "OpenAI", "Shopify", "Twilio", "Vercel",
    "Supabase", "Cloudflare", "Datadog", "MongoDB", "Snowflake"
]

async def cache_all():
    for company in DEMO_COMPANIES:
        orchestrator = CompanyOrchestrator(f"cache-{company}")
        await orchestrator.analyze(company, {...})
```

**Success Criteria:**
- Frontend displays search interface
- Real-time progress updates via WebSocket
- Dashboard shows all 6 tabs
- Knowledge graph renders
- Application is deployed to Render
- 10+ companies are pre-cached

---

## 🎯 Step 4: Testing & Polish (30 minutes)

**Test Checklist:**
- [ ] Search for "Stripe" works end-to-end
- [ ] WebSocket shows real-time progress (7 stages)
- [ ] Dashboard displays with all 6 tabs
- [ ] Each tab shows correct data
- [ ] Knowledge graph is interactive
- [ ] Error handling works (invalid company)
- [ ] Loading states display properly
- [ ] Pre-cached companies load instantly
- [ ] Deployment is live and accessible
- [ ] Mobile responsive (basic)

**Polish:**
- Add error messages
- Improve loading states
- Add tooltips
- Fix any UI bugs
- Test on different browsers

---

## 📦 Step 5: Documentation & Submission

**Create README.md:**
```markdown
# CompanyIntel - Autonomous Company Intelligence Platform

🏆 Built for Autonomous Agents Hackathon 2026

## What It Does
Autonomous AI agents analyze any company in 30 seconds...

## Tech Stack
- Yutori (Research, Browsing, Scouting)
- Neo4j (Knowledge graph)
- Tavily (AI search)
- OpenAI (Analysis)
- Render (Deployment)

## Demo
[Link to deployed app]

## Setup
[Installation instructions]
```

**GitHub:**
- Repository name: `companyintel-ai`
- Description: "Autonomous AI agents that analyze companies in 30 seconds"
- Topics: `ai`, `agents`, `yutori`, `neo4j`, `render`, `hackathon`

**Devpost Submission:**
- Title: CompanyIntel - Autonomous Company Intelligence Platform
- Tagline: AI agents that analyze companies in 30 seconds using Yutori, Neo4j, and Render
- Demo video: 3 minutes
- GitHub link
- Live demo link

---

## ⚠️ Critical Requirements

### MUST HAVE (or you fail):
✅ Use 3+ sponsor tools (you use 6+)
✅ Follow API contract in DESIGN.md exactly
✅ Implement WebSocket for real-time updates
✅ Deploy to Render with 2+ features
✅ Pre-cache 10+ demo companies
✅ Submit by 4:30 PM sharp

### MUST NOT DO:
❌ Don't deviate from API contract
❌ Don't skip error handling
❌ Don't forget CORS configuration
❌ Don't hardcode API keys
❌ Don't skip WebSocket
❌ Don't submit late

---

## 🎬 Demo Script (3 Minutes)

**0:00-0:30 - Opening:**
"We built CompanyIntel - autonomous AI agents that analyze any company in 30 seconds. Watch this..."

**0:30-2:00 - Live Demo:**
- Type "Stripe"
- Show 7-stage progress
- Click through tabs
- Show knowledge graph

**2:00-2:45 - Technical:**
"3 Yutori APIs, Neo4j with 8 relationships, Tavily search, OpenAI analysis, Render with 5 features..."

**2:45-3:00 - Value:**
"Saves 5+ hours per company. $500M+ market opportunity. Thank you!"

---

## 🆘 Emergency Fallbacks

**If Yutori API is slow:**
- Use pre-cached data
- Show cached companies only

**If Neo4j is complex:**
- Start with simple graph
- Add complexity later

**If WebSocket fails:**
- Use polling as fallback
- Show progress bar without real-time

**If deployment fails:**
- Deploy backend first
- Frontend can run locally

**If time runs out:**
- Focus on 3 tabs instead of 6
- Skip optional features

---

## 📊 Success Metrics

### Minimum (MUST HAVE):
- [ ] 5+ companies working
- [ ] Real-time progress
- [ ] 3+ tabs working
- [ ] Graph renders
- [ ] Deployed

### Competitive (SHOULD HAVE):
- [ ] All 6 tabs working
- [ ] Interactive graph
- [ ] 10+ companies cached
- [ ] Error handling

### Winning (NICE TO HAVE):
- [ ] 15+ companies cached
- [ ] Modulate integration
- [ ] Fastino integration

---

## 🚀 NOW START BUILDING!

1. **Read** all specification files (15 min)
2. **Research** APIs (30 min)
3. **Build** Hour 1: Core infrastructure (60 min)
4. **Build** Hour 2: Services (60 min)
5. **Build** Hour 3: Advanced features (60 min)
6. **Build** Hour 4: Frontend & deployment (60 min)
7. **Test** & polish (30 min)
8. **Document** & submit (30 min)

**Total: 5.5 hours**

---

## 💡 Key Insights

**Your Strengths:**
- Comprehensive (6 data categories)
- Autonomous (no manual intervention)
- Multi-tool (6+ sponsor tools)
- Visual (knowledge graph)
- Practical (real problem)

**Your Pitch:**
"Autonomous AI agents that save 5+ hours of company research by analyzing APIs, competitors, financials, team, and news in 30 seconds."

**Your Differentiator:**
"Only platform combining API documentation extraction, competitor analysis, and knowledge graphs in one autonomous system."

---

**GOOD LUCK! BUILD FAST, DEMO WELL, WIN PRIZES! 🚀**
