# app/services/gpt_analyzer.py
import base64
import logging
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
from app.prompts import get_system_prompt

load_dotenv()
logger = logging.getLogger(__name__)

class GPTAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.user_sessions = {}  # Храним только сессии, НЕ фото
    
    async def analyze_food_image(self, user_id: int, image_file, user_description: str = None, analysis_type: str = "nutrition", user_message: str = None) -> dict:
        """Анализирует фото или продолжает диалог в контексте"""
        try:
            # Если это первый запрос - конвертируем фото в base64
            if image_file and user_id not in self.user_sessions:
                # Перематываем файл в начало
                image_file.seek(0)
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                
                messages = [
                    {
                        "role": "system", 
                        "content": get_system_prompt(user_description, analysis_type)
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Проанализируй это фото еды:"},
                            {
                                "type": "image_url", 
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ]
                
                self.user_sessions[user_id] = {
                    "messages": messages,
                    "last_activity": time.time(),
                    "refinements_used": 0
                }
                
            elif user_id in self.user_sessions:
                # Продолжаем существующую сессию
                session = self.user_sessions[user_id]
                
                if user_message:  # Уточнение
                    session["messages"].append({"role": "user", "content": user_message})
                    session["refinements_used"] += 1
                else:  # Смена типа анализа
                    session["messages"][0]["content"] = get_system_prompt(user_description, analysis_type)
                    session["messages"].append({"role": "user", "content": f"Проанализируй {analysis_type}:"})
            
            else:
                return {"error": "Сессия не найдена"}
            
            # Обновляем время и делаем запрос
            self.user_sessions[user_id]["last_activity"] = time.time()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.user_sessions[user_id]["messages"],
                max_tokens=1000
            )
            
            gpt_response = response.choices[0].message.content
            self.user_sessions[user_id]["messages"].append({"role": "assistant", "content": gpt_response})
            
            refinements_left = 3 - self.user_sessions[user_id]["refinements_used"]
            
            return {
                "analysis": gpt_response,
                "refinements_left": max(0, refinements_left),
                "analysis_type": analysis_type
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа: {e}")
            return None
    
    def cleanup_sessions(self):
        """Очищает сессии старше 1 часа"""
        current_time = time.time()
        expired_users = [
            user_id for user_id, session in self.user_sessions.items()
            if current_time - session["last_activity"] > 3600
        ]
        for user_id in expired_users:
            del self.user_sessions[user_id]
    
    def has_active_session(self, user_id: int) -> bool:
        """Проверяет есть ли активная сессия"""
        return user_id in self.user_sessions