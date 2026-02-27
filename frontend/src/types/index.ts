// Request/Response Types
export interface AnalyzeOptions {
  include_apis: boolean;
  include_financials: boolean;
  include_competitors: boolean;
  include_team: boolean;
  include_news: boolean;
  include_graph: boolean;
}

export interface AnalyzeRequest {
  company_name: string;
  options: AnalyzeOptions;
}

export interface AnalyzeResponse {
  session_id: string;
  status: string;
  estimated_time_seconds: number;
  websocket_url: string;
}

// Company Data Types
export interface CompanyOverview {
  name: string;
  slug: string;
  description: string;
  founded_year?: number;
  headquarters: string;
  employee_count: string;
  website: string;
  logo_url: string;
  industry: string[];
  mission: string;
  status: string;
}

export interface Product {
  name: string;
  description: string;
  category: string;
  launch_date?: string;
}

export interface APIEndpoint {
  path: string;
  method: string;
  description: string;
  category: string;
  authentication_required: boolean;
}

export interface PricingTier {
  name: string;
  price: string;
  features: string[];
  target_audience: string;
}

export interface ProductsAPIs {
  products: Product[];
  apis: APIEndpoint[];
  documentation_quality: number;
  sdk_languages: string[];
  pricing: PricingTier[];
}

export interface Competitor {
  name: string;
  slug: string;
  relationship: string;
  strengths: string[];
  weaknesses: string[];
  market_overlap_percent: number;
}

export interface MarketIntelligence {
  competitors: Competitor[];
  market_position: string;
  market_share_percent?: number;
  niche: string;
  differentiation: string[];
  target_market: string[];
}

export interface FundingRound {
  round: string;
  amount: number;
  date: string;
  investors: string[];
  valuation: number;
}

export interface Financials {
  status: string;
  stock_symbol?: string;
  stock_price?: number;
  market_cap?: number;
  last_funding_round?: FundingRound;
  total_funding?: number;
  valuation?: number;
  revenue_estimate?: number;
  revenue_growth_yoy?: number;
  profitability_status: string;
  burn_rate?: string;
}

export interface Leader {
  name: string;
  title: string;
  background: string;
  linkedin_url?: string;
  photo_url?: string;
}

export interface TeamCulture {
  leadership: Leader[];
  tech_stack: string[];
  culture_signals: string[];
  work_model: string;
  open_positions_count: number;
  hiring_focus: string[];
}

export interface NewsArticle {
  title: string;
  url: string;
  source: string;
  published_date: string;
  sentiment: number;
  summary: string;
  topics: string[];
}

export interface SentimentPoint {
  date: string;
  sentiment: number;
  event?: string;
}

export interface ReviewSummary {
  average_rating: number;
  review_count: number;
  pros: string[];
  cons: string[];
  sources: string[];
}

export interface NewsSentiment {
  overall_sentiment: number;
  sentiment_label: string;
  recent_news: NewsArticle[];
  sentiment_timeline: SentimentPoint[];
  topics: string[];
  customer_reviews?: ReviewSummary;
}

export interface CompanyData {
  overview: CompanyOverview;
  products_apis: ProductsAPIs;
  market_intelligence: MarketIntelligence;
  financials: Financials;
  team_culture: TeamCulture;
  news_sentiment: NewsSentiment;
}

export interface CompanyMetadata {
  sources_count: number;
  confidence_score: number;
  last_updated: string;
}

export interface CompanyResponse {
  id: string;
  company_name: string;
  slug: string;
  analyzed_at: string;
  status: string;
  enrichment_status?: string;
  data: CompanyData;
  metadata: CompanyMetadata;
}

// Progress Types
export interface ProgressMessage {
  type: 'progress' | 'completed' | 'error';
  session_id: string;
  stage: string;
  progress: number;
  message: string;
  timestamp: string;
}

// Graph Types
export interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, any>;
  x?: number;
  y?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  properties: Record<string, any>;
}

export interface GraphMetadata {
  node_count: number;
  edge_count: number;
  generated_at: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: GraphMetadata;
}
