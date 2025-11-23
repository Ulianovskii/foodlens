# tests/quick_test.py
import sys
import os
import asyncio
from dotenv import load_dotenv

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

async def quick_test():
    """Быстрый тест API без pytest"""
    from app.services.gpt_analyzer import GPTAnalyzer
    
    print("🧪 Быстрый тест GPT анализатора...")
    
    analyzer = GPTAnalyzer()
    print("✅ GPTAnalyzer создан")
    
    try:
        # Простой текстовый запрос
        response = analyzer.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Скажи 'привет'"}],
            max_tokens=10
        )
        print(f"✅ OpenAI API работает: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Ошибка OpenAI API: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(quick_test())
    exit(0 if result else 1)