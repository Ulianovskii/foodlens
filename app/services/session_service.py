# app/services/session_service.py
from typing import Optional, Dict
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio

@dataclass
class AnalysisSession:
    user_id: int
    photo_file_id: str
    photo_text: Optional[str] = None
    messages_count: int = 0
    created_at: datetime = None
    is_active: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def can_add_message(self) -> bool:
        return self.is_active and self.messages_count < 5
    
    def increment_message(self):
        self.messages_count += 1

class SessionService:
    def __init__(self):
        self.analysis_sessions: Dict[int, AnalysisSession] = {}
        self.cleanup_interval = 3600  # 1 час
    
    def start_analysis_session(self, user_id: int, photo_file_id: str, photo_text: str = None) -> AnalysisSession:
        """Начинает новую сессию анализа"""
        session = AnalysisSession(
            user_id=user_id,
            photo_file_id=photo_file_id,
            photo_text=photo_text,
            is_active=True
        )
        self.analysis_sessions[user_id] = session
        return session
    
    def get_analysis_session(self, user_id: int) -> Optional[AnalysisSession]:
        """Получает активную сессию анализа"""
        session = self.analysis_sessions.get(user_id)
        if session and session.is_active:
            return session
        return None
    
    def end_analysis_session(self, user_id: int):
        """Завершает сессию анализа"""
        if user_id in self.analysis_sessions:
            self.analysis_sessions[user_id].is_active = False
            del self.analysis_sessions[user_id]
    
    def is_user_in_analysis(self, user_id: int) -> bool:
        """Проверяет, находится ли пользователь в режиме анализа"""
        session = self.get_analysis_session(user_id)
        return session is not None and session.is_active
    
    async def cleanup_expired_sessions(self):
        """Очистка устаревших сессий"""
        now = datetime.now()
        expired_users = []
        
        for user_id, session in self.analysis_sessions.items():
            if now - session.created_at > timedelta(hours=1):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self.end_analysis_session(user_id)
        
        if expired_users:
            print(f"🧹 Очищено {len(expired_users)} устаревших сессий")

# Глобальный экземпляр
session_service = SessionService()