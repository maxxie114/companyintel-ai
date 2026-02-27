# Additional Sections for DESIGN.md

## Insert after "Project Structure" section (around line 622)

---

## MVP Implementation (Hours 1-4)

The MVP focuses on core functionality with 5+ sponsor tools to meet hackathon requirements.

### MVP Features
- Company search and analysis
- 6 data categories (Overview, APIs, Market, Financials, Team, News)
- Real-time progress tracking via WebSocket
- Neo4j knowledge graph visualization
- Render deployment with 2+ features (Web Service + Background Workers)

### MVP Sponsor Tool Usage
1. **Yutori Research API** - Company overview and deep research
2. **Yutori Browsing API** - API documentation extraction
3. **Neo4j** - Knowledge graph storage and queries
4. **Tavily** - News search and data gathering
5. **OpenAI** - Sentiment analysis and data processing
6. **Render** - Web Service + Background Workers deployment

---

## Step 2: Modulate Integration (Hour 5)

**Goal:** Add voice-based company analysis and audio sentiment detection for earnings calls and interviews.

### What Modulate Adds

Modulate's ToxMod SDK provides voice intelligence capabilities:
- Analyze CEO/executive interview audio for sentiment
- Process earnings call recordings for tone analysis
- Detect confidence levels in company communications
- Voice-based fraud detection for company verification

### Implementation

**New Service: `services/voice_analysis.py`**
```python
import httpx
from app.config import settings

class VoiceAnalysisService:
    def __init__(self):
        self.api_key = settings.modulate_api_key
        self.base_url = "https://api.modulate.ai/v1"
    
    async def analyze_earnings_call(self, company_name: str, audio_url: str) -> dict:
        """Analyze earnings call audio for sentiment and confidence"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/analyze",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "audio_url": audio_url,
                    "analysis_types": ["sentiment", "confidence", "stress_detection"]
                }
            )
            return response.json()
    
    async def get_executive_voice_profile(self, company_name: str) -> dict:
        """Build voice profile from multiple interviews/calls"""
        # Use Yutori to find audio sources
        # Use Modulate to analyze each audio
        # Aggregate results
        pass
```

**New API Endpoint: `POST /api/voice-analysis/{company_id}`**
```python
@router.post("/voice-analysis/{company_id}")
async def analyze_voice(company_id: str, audio_urls: List[str]):
    """Analyze company voice communications"""
    voice_service = VoiceAnalysisService()
    results = []
    
    for url in audio_urls:
        analysis = await voice_service.analyze_earnings_call(company_id, url)
        results.append(analysis)
    
    return {
        "company_id": company_id,
        "voice_analyses": results,
        "overall_sentiment": calculate_average_sentiment(results),
        "confidence_score": calculate_confidence(results)
    }
```

**Frontend Addition: New Tab "Voice Intelligence"**
```typescript
interface VoiceIntelligenceTabProps {
  data: VoiceAnalysisData;
}

export const VoiceIntelligenceTab: React.FC<VoiceIntelligenceTabProps> = ({ data }) => {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6">Earnings Call Sentiment</Typography>
            <LineChart data={data.sentiment_timeline} />
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Executive Confidence</Typography>
            <Typography variant="h3">{data.confidence_score}%</Typography>
            <Typography variant="body2" color="text.secondary">
              Based on {data.analyzed_calls} earnings calls
            </Typography>
          </CardContent>
        </Card>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6">Stress Indicators</Typography>
            <List>
              {data.stress_indicators.map((indicator, i) => (
                <ListItem key={i}>
                  <ListItemText 
                    primary={indicator.type}
                    secondary={`Detected in ${indicator.frequency}% of calls`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};
```

### Data Model Addition

```typescript
interface VoiceAnalysisData {
  company_id: string;
  analyzed_calls: number;
  sentiment_timeline: SentimentPoint[];
  confidence_score: number;
  stress_indicators: StressIndicator[];
  voice_authenticity: number;  // Fraud detection score
  key_phrases: string[];
}

interface StressIndicator {
  type: string;  // e.g., "vocal_tension", "speech_rate_increase"
  frequency: number;  // Percentage of calls where detected
  severity: "low" | "medium" | "high";
}
```

### Integration with MVP

Add to orchestrator:
```python
# Stage 8: Voice Analysis (optional, if audio available)
if options.get("include_voice_analysis"):
    await self.update_progress(0.85, "analyzing_voice")
    voice_data = await self.voice.analyze_company_audio(company_name)
```

---

## Step 3: Fastino Labs Integration (Hour 6)

**Goal:** Use fine-tuned models for better entity extraction and agentic analysis of company data.

### What Fastino Labs Adds

Fastino provides:
- **GLiNER 2-XL** - Zero-shot entity extraction (people, companies, products)
- **Pioneer Fine-tuning** - Custom models for company analysis
- **Personalization Layer** - Context-aware agent responses

### Implementation

**New Service: `services/entity_extraction.py`**
```python
import httpx
from app.config import settings

class EntityExtractionService:
    def __init__(self):
        self.api_key = settings.fastino_api_key
        self.base_url = "https://api.fastino.com"
    
    async def extract_entities(self, text: str, entity_types: List[str]) -> dict:
        """Extract entities using GLiNER 2-XL"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/run",
                headers={"x-api-key": self.api_key},
                json={
                    "model_id": "gliner-2-xl",
                    "input": [{"text": text}],
                    "labels": entity_types
                }
            )
            return response.json()
    
    async def analyze_with_finetuned_model(self, company_data: dict) -> dict:
        """Use fine-tuned model for company analysis"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/run",
                headers={"x-api-key": self.api_key},
                json={
                    "model_id": "company-analyzer-v1",  # Custom fine-tuned model
                    "input": [{"data": company_data}]
                }
            )
            return response.json()
```

**Enhanced Research Service**
```python
class EnhancedResearchService(ResearchService):
    def __init__(self):
        super().__init__()
        self.entity_extractor = EntityExtractionService()
    
    async def get_company_overview(self, company_name: str) -> dict:
        """Enhanced with entity extraction"""
        # Get raw research data
        raw_data = await super().get_company_overview(company_name)
        
        # Extract entities from description
        entities = await self.entity_extractor.extract_entities(
            raw_data["description"],
            entity_types=["PERSON", "ORGANIZATION", "PRODUCT", "TECHNOLOGY", "LOCATION"]
        )
        
        # Enrich data with extracted entities
        raw_data["extracted_entities"] = entities
        raw_data["key_people"] = [e for e in entities if e["type"] == "PERSON"]
        raw_data["technologies"] = [e for e in entities if e["type"] == "TECHNOLOGY"]
        
        return raw_data
```

**Fine-tuned Competitor Analysis**
```python
class EnhancedCompetitorService(CompetitorService):
    def __init__(self):
        super().__init__()
        self.entity_extractor = EntityExtractionService()
    
    async def find_competitors(self, company_name: str) -> dict:
        """Use fine-tuned model for better competitor detection"""
        # Get initial competitor list
        competitors = await super().find_competitors(company_name)
        
        # Use fine-tuned model to analyze competitive positioning
        enhanced_analysis = await self.entity_extractor.analyze_with_finetuned_model({
            "company": company_name,
            "competitors": competitors,
            "task": "competitive_positioning"
        })
        
        # Merge results
        return {
            **competitors,
            "ai_insights": enhanced_analysis["insights"],
            "market_gaps": enhanced_analysis["opportunities"],
            "threat_level": enhanced_analysis["threat_assessment"]
        }
```

**New API Endpoint: `POST /api/entity-extraction`**
```python
@router.post("/entity-extraction")
async def extract_entities(request: EntityExtractionRequest):
    """Extract entities from text using Fastino GLiNER"""
    service = EntityExtractionService()
    entities = await service.extract_entities(
        request.text,
        request.entity_types
    )
    return {"entities": entities}
```

### Frontend Enhancement

**Enhanced Overview Tab with Entity Visualization**
```typescript
export const EnhancedOverviewTab: React.FC<OverviewTabProps> = ({ data }) => {
  return (
    <Grid container spacing={3}>
      {/* Existing overview content */}
      
      {/* New: Extracted Entities Section */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Key Entities (AI-Extracted)
            </Typography>
            
            <Box display="flex" gap={2} flexWrap="wrap">
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Key People
                </Typography>
                {data.extracted_entities.key_people.map((person, i) => (
                  <Chip key={i} label={person.text} color="primary" sx={{ m: 0.5 }} />
                ))}
              </Box>
              
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Technologies
                </Typography>
                {data.extracted_entities.technologies.map((tech, i) => (
                  <Chip key={i} label={tech.text} color="secondary" sx={{ m: 0.5 }} />
                ))}
              </Box>
            </Box>
          </CardContent>
        </Card>
      </Grid>
      
      {/* New: AI Insights Section */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              AI-Powered Insights
            </Typography>
            <List>
              {data.ai_insights?.map((insight, i) => (
                <ListItem key={i}>
                  <ListItemIcon>
                    <LightbulbIcon color="warning" />
                  </ListItemIcon>
                  <ListItemText primary={insight} />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};
```

### Data Model Additions

```typescript
interface ExtractedEntities {
  key_people: Entity[];
  technologies: Entity[];
  products: Entity[];
  locations: Entity[];
}

interface Entity {
  text: string;
  type: string;
  confidence: number;
  context: string;
}

interface AIInsights {
  insights: string[];
  market_gaps: string[];
  threat_level: "low" | "medium" | "high";
  recommendations: string[];
}
```

### Integration with MVP

Update orchestrator to use enhanced services:
```python
class EnhancedCompanyOrchestrator(CompanyOrchestrator):
    def __init__(self, session_id: str):
        super().__init__(session_id)
        self.research = EnhancedResearchService()
        self.competitor = EnhancedCompetitorService()
        self.entity_extractor = EntityExtractionService()
```

---

## Implementation Timeline

### MVP (Hours 1-4)
- Hour 1: Core infrastructure + basic endpoints
- Hour 2: Yutori integration + caching
- Hour 3: All services + Neo4j graph
- Hour 4: Frontend + deployment

### Step 2: Modulate (Hour 5)
- 20 min: Voice analysis service implementation
- 20 min: API endpoint + data models
- 20 min: Frontend voice intelligence tab

### Step 3: Fastino Labs (Hour 6)
- 20 min: Entity extraction service
- 20 min: Enhanced research/competitor services
- 20 min: Frontend entity visualization

---

## Sponsor Tool Usage Summary

### MVP (Required 3+, Using 6)
1. **Yutori Research API** ⭐ - Deep company research
2. **Yutori Browsing API** ⭐ - API docs extraction
3. **Neo4j** ⭐ - Knowledge graph
4. **Tavily** ⭐ - News search
5. **OpenAI** ⭐ - Analysis
6. **Render** ⭐ - Deployment (Web Service + Background Workers)

### Step 2 (Hour 5)
7. **Modulate** ⭐ - Voice intelligence

### Step 3 (Hour 6)
8. **Fastino Labs** ⭐ - Entity extraction + fine-tuned models

### Total: 8 Sponsor Tools

---

## Render Track Compliance (2+ Features Required)

✅ **Feature 1: Web Service**
- FastAPI backend deployment
- Auto-scaling based on traffic
- Zero-downtime deployments

✅ **Feature 2: Background Workers**
- Async company analysis processing
- Queue-based job processing
- Separate worker instances

✅ **Feature 3: Cron Jobs** (Bonus)
- Scheduled data refresh for cached companies
- Daily competitor monitoring updates
- Weekly trend analysis

✅ **Feature 4: PostgreSQL** (Bonus)
- Historical analysis storage
- User query tracking
- Analytics data

✅ **Feature 5: Redis** (Bonus)
- Response caching
- Session management
- Real-time progress tracking

---
