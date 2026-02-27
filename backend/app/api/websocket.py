from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.cache import get_progress_updates, delete_progress
import asyncio
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/progress/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    """WebSocket for real-time progress updates"""
    await websocket.accept()
    logger.info(f"WebSocket connected for session {session_id}")
    
    try:
        while True:
            # Get progress from Redis
            progress = await get_progress_updates(session_id)
            
            if progress:
                await websocket.send_json(progress)
                
                # If completed or error, close connection
                if progress.get("type") in ["completed", "error"]:
                    logger.info(f"Analysis {progress.get('type')} for session {session_id}")
                    await asyncio.sleep(1)  # Give client time to receive
                    break
            
            await asyncio.sleep(0.5)
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass
        # Clean up progress data after some time
        await asyncio.sleep(60)
        await delete_progress(session_id)
