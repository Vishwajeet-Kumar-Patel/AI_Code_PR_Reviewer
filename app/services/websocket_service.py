"""
WebSocket service for real-time updates
"""
from typing import Dict, Set, List
from fastapi import WebSocket, WebSocketDisconnect
from app.core.logging import logger
import json
import asyncio


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # Map of user_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of review_id -> Set of user_ids subscribed
        self.review_subscriptions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"WebSocket connected: user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        logger.info(f"WebSocket disconnected: user {user_id}")
    
    async def subscribe_to_review(self, user_id: str, review_id: str):
        """Subscribe user to review updates"""
        if review_id not in self.review_subscriptions:
            self.review_subscriptions[review_id] = set()
        
        self.review_subscriptions[review_id].add(user_id)
        logger.info(f"User {user_id} subscribed to review {review_id}")
    
    async def unsubscribe_from_review(self, user_id: str, review_id: str):
        """Unsubscribe user from review updates"""
        if review_id in self.review_subscriptions:
            self.review_subscriptions[review_id].discard(user_id)
            
            if not self.review_subscriptions[review_id]:
                del self.review_subscriptions[review_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            dead_connections = set()
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    dead_connections.add(connection)
            
            # Remove dead connections
            for conn in dead_connections:
                self.active_connections[user_id].discard(conn)
    
    async def broadcast_review_update(self, review_id: str, message: dict):
        """Broadcast update to all users subscribed to a review"""
        if review_id in self.review_subscriptions:
            for user_id in self.review_subscriptions[review_id]:
                await self.send_personal_message(message, user_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()


class WebSocketMessageTypes:
    """WebSocket message types"""
    REVIEW_STARTED = "review_started"
    REVIEW_PROGRESS = "review_progress"
    REVIEW_COMPLETED = "review_completed"
    REVIEW_FAILED = "review_failed"
    FILE_ANALYZED = "file_analyzed"
    SECURITY_ISSUE_FOUND = "security_issue_found"
    NOTIFICATION = "notification"
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"


async def send_review_update(review_id: str, status: str, data: dict):
    """Send review update to subscribers"""
    message = {
        "type": WebSocketMessageTypes.REVIEW_PROGRESS,
        "review_id": review_id,
        "status": status,
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await manager.broadcast_review_update(review_id, message)


async def send_review_completed(review_id: str, result: dict):
    """Notify subscribers that review is completed"""
    message = {
        "type": WebSocketMessageTypes.REVIEW_COMPLETED,
        "review_id": review_id,
        "result": result,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await manager.broadcast_review_update(review_id, message)


async def send_notification(user_id: str, notification: dict):
    """Send notification to specific user"""
    message = {
        "type": WebSocketMessageTypes.NOTIFICATION,
        "notification": notification,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    await manager.send_personal_message(message, user_id)
