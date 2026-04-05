import pymongo
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class ConversationMemory:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/", db_name: str = "voice_assistant"):
        """
        Khởi tạo kết nối MongoDB để lưu trữ lịch sử hội thoại
        """
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.conversations = self.db.conversations
        
    def create_session(self, user_id: str = None) -> str:
        """
        Tạo session mới cho cuộc hội thoại
        """
        session_id = str(uuid.uuid4())
        session_data = {
            "_id": session_id,
            "user_id": user_id or "default_user",
            "created_at": datetime.now(),
            "messages": [],
            "active": True
        }
        self.conversations.insert_one(session_data)
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, timestamp: datetime = None):
        """
        Thêm tin nhắn vào session
        role: 'user' hoặc 'assistant'
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp or datetime.now()
        }
        
        self.conversations.update_one(
            {"_id": session_id},
            {
                "$push": {"messages": message},
                "$set": {"last_updated": datetime.now()}
            }
        )
    
    def get_recent_context(self, session_id: str, limit: int = 6) -> List[Dict]:
        """
        Lấy ngữ cảnh gần đây (mặc định 6 tin nhắn cuối)
        """
        session = self.conversations.find_one({"_id": session_id})
        if not session:
            return []
        
        messages = session.get("messages", [])
        return messages[-limit:] if len(messages) > limit else messages
    
    def get_context_string(self, session_id: str, limit: int = 6) -> str:
        """
        Tạo chuỗi ngữ cảnh để đưa vào prompt
        """
        messages = self.get_recent_context(session_id, limit)
        context_parts = []
        
        for msg in messages:
            role = "Người dùng" if msg["role"] == "user" else "Trợ lý"
            context_parts.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def clear_session(self, session_id: str):
        """
        Xóa session hiện tại
        """
        self.conversations.delete_one({"_id": session_id})
    
    def get_all_sessions(self, user_id: str = "default_user") -> List[Dict]:
        """
        Lấy tất cả session của user
        """
        return list(self.conversations.find(
            {"user_id": user_id, "active": True}
        ).sort("created_at", -1))
    
    def close(self):
        """
        Đóng kết nối MongoDB
        """
        self.client.close()