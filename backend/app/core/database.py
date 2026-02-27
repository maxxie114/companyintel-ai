from neo4j import AsyncGraphDatabase
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class Neo4jConnection:
    def __init__(self):
        self.driver = None
    
    async def connect(self):
        """Initialize Neo4j connection"""
        try:
            if settings.neo4j_uri and settings.neo4j_password:
                self.driver = AsyncGraphDatabase.driver(
                    settings.neo4j_uri,
                    auth=(settings.neo4j_user, settings.neo4j_password)
                )
                # Test connection
                async with self.driver.session() as session:
                    result = await session.run("RETURN 1 as test")
                    await result.single()
                logger.info("✓ Neo4j connected successfully")
            else:
                logger.warning("Neo4j credentials not configured, skipping connection")
        except Exception as e:
            logger.error(f"Neo4j connection failed: {e}")
            self.driver = None
    
    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            logger.info("Neo4j connection closed")
    
    def get_driver(self):
        """Get Neo4j driver instance"""
        return self.driver

# Global instance
neo4j_conn = Neo4jConnection()

async def init_neo4j():
    """Initialize Neo4j connection"""
    await neo4j_conn.connect()

async def close_neo4j():
    """Close Neo4j connection"""
    await neo4j_conn.close()

def get_neo4j_driver():
    """Get Neo4j driver"""
    return neo4j_conn.get_driver()
