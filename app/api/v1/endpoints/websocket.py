"""
WebSocket endpoints for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.services.websocket_service import manager, WebSocketMessageTypes
from app.core.logging import logger
from app.core.deps import get_current_user
from app.db.models import User
import json


router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/reviews")
async def websocket_reviews_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time review updates
    
    Query params:
        token: JWT access token for authentication
    
    Message format:
        Client -> Server:
        {
            "type": "subscribe",
            "review_id": "review-123"
        }
        
        Server -> Client:
        {
            "type": "review_progress",
            "review_id": "review-123",
            "status": "analyzing",
            "data": {...}
        }
    """
    user_id = None
    
    try:
        # Authenticate user from token
        from app.core.security import decode_token
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        # Accept connection
        await manager.connect(websocket, user_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "user_id": user_id
        })
        
        # Handle messages
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == WebSocketMessageTypes.SUBSCRIBE:
                review_id = data.get("review_id")
                if review_id:
                    await manager.subscribe_to_review(user_id, review_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "review_id": review_id
                    })
            
            elif message_type == WebSocketMessageTypes.UNSUBSCRIBE:
                review_id = data.get("review_id")
                if review_id:
                    await manager.unsubscribe_from_review(user_id, review_id)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "review_id": review_id
                    })
            
            elif message_type == WebSocketMessageTypes.PING:
                await websocket.send_json({"type": WebSocketMessageTypes.PONG})
    
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket disconnected: user {user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        if user_id:
            manager.disconnect(websocket, user_id)


@router.websocket("/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    token: str = Query(...)
):
    """
    WebSocket endpoint for real-time notifications
    """
    user_id = None
    
    try:
        # Authenticate
        from app.core.security import decode_token
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
        
        await manager.connect(websocket, user_id)
        
        await websocket.send_json({
            "type": "connected",
            "message": "Notifications WebSocket connected"
        })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == WebSocketMessageTypes.PING:
                await websocket.send_json({"type": WebSocketMessageTypes.PONG})
    
    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(websocket, user_id)
    
    except Exception as e:
        logger.error(f"Notifications WebSocket error: {e}", exc_info=True)
        if user_id:
            manager.disconnect(websocket, user_id)


@router.get("/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_connections": manager.get_connection_count(),
        "active_users": len(manager.active_connections),
        "active_subscriptions": len(manager.review_subscriptions)
    }
