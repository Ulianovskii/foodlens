# tests/test_gpt_analyzer.py
import pytest
import asyncio
from app.services.gpt_analyzer import GPTAnalyzer

class TestGPTAnalyzer:
    """Тесты для GPT анализатора"""
    
    @pytest.fixture
    def analyzer(self, openai_api_key):
        """Создает экземпляр анализатора"""
        return GPTAnalyzer()
    
    @pytest.mark.asyncio
    async def test_analyzer_creation(self, analyzer):
        """Тест создания анализатора"""
        assert analyzer is not None
        assert hasattr(analyzer, 'client')
        assert hasattr(analyzer, 'user_sessions')
    
    @pytest.mark.asyncio
    async def test_openai_connection(self, analyzer):
        """Тест подключения к OpenAI API"""
        # Простой текстовый запрос для проверки соединения
        response = analyzer.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Ответь 'тест пройден'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        assert "тест" in result.lower() or "test" in result.lower()
    
    @pytest.mark.asyncio 
    async def test_session_management(self, analyzer):
        """Тест управления сессиями"""
        user_id = 12345
        
        # Очищаем на всякий случай
        if user_id in analyzer.user_sessions:
            del analyzer.user_sessions[user_id]
        
        # Проверяем что сессии очищаются
        analyzer.cleanup_sessions()
        assert user_id not in analyzer.user_sessions
        
        # Проверяем проверку активной сессии
        assert not analyzer.has_active_session(user_id)

if __name__ == "__main__":
    # Запуск тестов напрямую
    pytest.main([__file__, "-v"])