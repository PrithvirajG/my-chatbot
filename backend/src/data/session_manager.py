import uuid
import json
from datetime import datetime

from redis import Redis
from loguru import logger

from backend.src.data.redis_manager import set_key, get_key, delete_key
SESSION_EXPIRATION = 3600

class SessionManager:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.session_ttl = 3600  # 1 hour in seconds

    def create_session(self) -> str:
        """Generate new session ID and initialize data structures"""
        session_id = str(uuid.uuid4())
        
        initial_data = {
            "history": [],
            "files": {},
            "metadata": {
                "created_at": str(datetime.utcnow()),
                "last_active": str(datetime.utcnow())
            }
        }
        
        # self.redis.setex(
        #     name=f"session:{session_id}",
        #     time=self.session_ttl,
        #     value=json.dumps(initial_data)
        # )
        set_key(session_id, json.dumps(initial_data), ex=SESSION_EXPIRATION)
        
        logger.info(f"Created new session: {session_id} with session data: {initial_data}")
        return session_id

    def get_session(self, session_id: str) -> dict:
        """Retrieve complete session data"""
        # session_data = self.redis.get(f"session:{session_id}")
        session_data = get_key(session_id)
        if not session_data:
            raise ValueError("Session not found")
            
        return json.loads(session_data)

    def update_session(self, session_id: str, update_fn: callable):
        """Atomic session update with locking"""
        with self.redis.lock(f"lock:{session_id}", timeout=5):
            data = self.get_session(session_id)
            update_fn(data)
            self.redis.setex(
                name=f"{session_id}",
                time=self.session_ttl,
                value=json.dumps(data)
            )
            logger.debug(f"Updated session: {session_id}")

    def add_chat_history(self, session_id: str, user_msg: str, ai_response: str):
        """Add conversation pair to session history"""
        def update_fn(data):
            data["history"].append({
                "user": user_msg,
                "ai": ai_response,
                "timestamp": str(datetime.utcnow())
            })
            data["metadata"]["last_active"] = str(datetime.utcnow())
            
        self.update_session(session_id, update_fn)

    def add_file_reference(self, session_id: str, file_id: str, file_meta: dict):
        """Store reference to processed file"""
        def update_fn(data):
            data["files"][file_id] = file_meta
            data["metadata"]["last_active"] = str(datetime.utcnow())
            
        self.update_session(session_id, update_fn)