from app.core.database import get_neo4j_driver
from app.models import GraphData, GraphNode, GraphEdge, GraphMetadata
from typing import Dict, Any, List
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

class GraphService:
    def __init__(self):
        self.driver = get_neo4j_driver()
    
    async def build_knowledge_graph(
        self,
        company_id: str,
        overview: Dict[str, Any],
        apis: Dict[str, Any],
        competitors: Dict[str, Any],
        financials: Dict[str, Any],
        team: Dict[str, Any],
        news: Dict[str, Any]
    ):
        """Build Neo4j knowledge graph from all data"""
        if not self.driver:
            logger.warning("Neo4j not connected, skipping graph build")
            return
        
        logger.info(f"Building knowledge graph for {company_id}")
        
        try:
            async with self.driver.session() as session:
                # Create company node
                await session.run(
                    """
                    MERGE (c:Company {id: $id})
                    SET c.name = $name,
                        c.slug = $slug,
                        c.description = $description,
                        c.founded_year = $founded_year,
                        c.headquarters = $headquarters,
                        c.website = $website
                    """,
                    id=company_id,
                    name=overview.get("name"),
                    slug=overview.get("slug"),
                    description=overview.get("description"),
                    founded_year=overview.get("founded_year"),
                    headquarters=overview.get("headquarters"),
                    website=overview.get("website")
                )
                
                # Create product nodes and relationships
                for product in apis.get("products", [])[:5]:  # Limit to 5
                    product_id = str(uuid.uuid4())
                    await session.run(
                        """
                        MERGE (p:Product {id: $id})
                        SET p.name = $name,
                            p.description = $description,
                            p.category = $category
                        WITH p
                        MATCH (c:Company {id: $company_id})
                        MERGE (c)-[:OFFERS]->(p)
                        """,
                        id=product_id,
                        name=product.get("name"),
                        description=product.get("description"),
                        category=product.get("category"),
                        company_id=company_id
                    )
                
                # Create competitor nodes and relationships
                for competitor in competitors.get("competitors", [])[:5]:  # Limit to 5
                    comp_id = str(uuid.uuid4())
                    await session.run(
                        """
                        MERGE (comp:Company {id: $id})
                        SET comp.name = $name,
                            comp.slug = $slug
                        WITH comp
                        MATCH (c:Company {id: $company_id})
                        MERGE (c)-[r:COMPETES_WITH]->(comp)
                        SET r.overlap = $overlap,
                            r.relationship = $relationship
                        """,
                        id=comp_id,
                        name=competitor.get("name"),
                        slug=competitor.get("slug"),
                        company_id=company_id,
                        overlap=competitor.get("market_overlap_percent"),
                        relationship=competitor.get("relationship")
                    )
                
                # Create technology nodes
                for tech in team.get("tech_stack", [])[:10]:  # Limit to 10
                    tech_id = str(uuid.uuid4())
                    await session.run(
                        """
                        MERGE (t:Technology {name: $name})
                        WITH t
                        MATCH (c:Company {id: $company_id})
                        MERGE (c)-[:USES]->(t)
                        """,
                        name=tech,
                        company_id=company_id
                    )
                
                # Create leader nodes
                for leader in team.get("leadership", [])[:5]:  # Limit to 5
                    leader_id = str(uuid.uuid4())
                    await session.run(
                        """
                        MERGE (l:Person {id: $id})
                        SET l.name = $name,
                            l.title = $title,
                            l.background = $background
                        WITH l
                        MATCH (c:Company {id: $company_id})
                        MERGE (l)-[:LEADS]->(c)
                        """,
                        id=leader_id,
                        name=leader.get("name"),
                        title=leader.get("title"),
                        background=leader.get("background"),
                        company_id=company_id
                    )
                
                logger.info(f"✓ Knowledge graph built for {company_id}")
        
        except Exception as e:
            logger.error(f"Error building graph: {e}")
    
    async def get_graph_data(self, company_id: str, depth: int = 2) -> GraphData:
        """Query graph for visualization"""
        if not self.driver:
            logger.warning("Neo4j not connected, returning empty graph")
            return GraphData(
                nodes=[],
                edges=[],
                metadata=GraphMetadata(
                    node_count=0,
                    edge_count=0,
                    generated_at=datetime.utcnow().isoformat()
                )
            )
        
        try:
            async with self.driver.session() as session:
                # Get all nodes and relationships up to specified depth
                result = await session.run(
                    """
                    MATCH path = (c:Company {id: $company_id})-[*0..2]-(n)
                    RETURN DISTINCT c, n, relationships(path) as rels
                    LIMIT 100
                    """,
                    company_id=company_id
                )
                
                nodes_dict = {}
                edges_list = []
                
                async for record in result:
                    # Add company node
                    company = record["c"]
                    if company.element_id not in nodes_dict:
                        nodes_dict[company.element_id] = GraphNode(
                            id=company.element_id,
                            label="Company",
                            properties={
                                "name": company.get("name", ""),
                                "type": "company",
                                **dict(company)
                            }
                        )
                    
                    # Add related node
                    node = record["n"]
                    if node and node.element_id not in nodes_dict:
                        labels = list(node.labels)
                        nodes_dict[node.element_id] = GraphNode(
                            id=node.element_id,
                            label=labels[0] if labels else "Node",
                            properties={
                                "name": node.get("name", ""),
                                "type": labels[0].lower() if labels else "node",
                                **dict(node)
                            }
                        )
                    
                    # Add relationships
                    rels = record["rels"]
                    if rels:
                        for rel in rels:
                            edge_id = f"{rel.start_node.element_id}-{rel.end_node.element_id}"
                            edges_list.append(GraphEdge(
                                id=edge_id,
                                source=rel.start_node.element_id,
                                target=rel.end_node.element_id,
                                label=rel.type,
                                properties=dict(rel)
                            ))
                
                return GraphData(
                    nodes=list(nodes_dict.values()),
                    edges=edges_list,
                    metadata=GraphMetadata(
                        node_count=len(nodes_dict),
                        edge_count=len(edges_list),
                        generated_at=datetime.utcnow().isoformat()
                    )
                )
        
        except Exception as e:
            logger.error(f"Error getting graph data: {e}")
            return GraphData(
                nodes=[],
                edges=[],
                metadata=GraphMetadata(
                    node_count=0,
                    edge_count=0,
                    generated_at=datetime.utcnow().isoformat()
                )
            )
