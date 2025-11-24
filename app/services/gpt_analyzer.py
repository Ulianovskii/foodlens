# app/services/gpt_analyzer.py
import base64
import logging
import time
from openai import OpenAI
import os
from dotenv import load_dotenv
from app.prompts.food_analysis import get_system_prompt

load_dotenv()
logger = logging.getLogger(__name__)

class GPTAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.user_sessions = {}
    
    async def analyze_food_image(self, user_id: int, image_file, analysis_type: str = "nutrition", user_message: str = None) -> dict:
        try:
            print(f"🔍 DEBUG: Начало анализа, user_id: {user_id}")
            print(f"🔍 DEBUG: analysis_type: {analysis_type}")
            print(f"🔍 DEBUG: user_message: {user_message}")
            
            MAX_MESSAGES = 5
            
            # Если это первый запрос с фото - создаем сессию
            if image_file and user_id not in self.user_sessions:
                print("🔍 DEBUG: Первый запрос с фото")
                
                try:
                    if hasattr(image_file, 'getvalue'):  # Если это BytesIO
                        image_data = image_file.getvalue()
                    else:  # Если это обычный файл
                        image_file.seek(0)
                        image_data = image_file.read()
                    
                    print(f"🔍 DEBUG: Размер фото: {len(image_data)} байт")
                    
                    if len(image_data) == 0:
                        print("❌ DEBUG: Файл пустой!")
                        return None
                        
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    print(f"🔍 DEBUG: Base64 успешно создан, размер: {len(base64_image)} символов")
                    
                except Exception as e:
                    print(f"❌ DEBUG: Ошибка чтения файла: {e}")
                    return None
                
                # Формируем системный промт для первого запроса
                system_prompt = get_system_prompt(user_message, analysis_type)
                
                messages = [
                    {
                        "role": "system", 
                        "content": system_prompt
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
                
                # Если есть user_message (подпись) - добавляем ее
                if user_message:
                    messages.append({
                        "role": "user",
                        "content": f"Дополнительная информация от пользователя:\n{user_message}"
                    })
                
                self.user_sessions[user_id] = {
                    "messages": messages,
                    "last_activity": time.time(),
                    "messages_count": 1,
                    "base64_image": base64_image,  # Сохраняем фото для будущих запросов
                    "current_analysis_type": analysis_type
                }
                
            elif user_id in self.user_sessions:
                # Продолжение существующей сессии
                session = self.user_sessions[user_id]
                
                if session["messages_count"] >= MAX_MESSAGES:
                    return {"error": "message_limit_reached"}
                
                # Обновляем системный промт если тип анализа изменился
                if session["current_analysis_type"] != analysis_type:
                    print(f"🔍 DEBUG: Смена типа анализа с {session['current_analysis_type']} на {analysis_type}")
                    
                    # Обновляем системный промт
                    system_prompt = get_system_prompt(None, analysis_type)
                    session["messages"][0]["content"] = system_prompt
                    session["current_analysis_type"] = analysis_type
                
                # Добавляем пользовательское сообщение или запрос на анализ
                if user_message:
                    session["messages"].append({"role": "user", "content": user_message})
                    session["messages_count"] += 1
                else:
                    # Если просто нажали кнопку - добавляем запрос на анализ
                    analysis_request = {
                        "nutrition": "Проанализируй калорийность и БЖУ этого блюда:",
                        "recipe": "Дай рецепт приготовления этого блюда:"
                    }.get(analysis_type, f"Проанализируй {analysis_type}:")
                    
                    session["messages"].append({"role": "user", "content": analysis_request})
                    session["messages_count"] += 1
            
            else:
                return {"error": "session_not_found"}
            
            self.user_sessions[user_id]["last_activity"] = time.time()
            
            print("🔍 DEBUG: Отправляем запрос в OpenAI...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.user_sessions[user_id]["messages"],
                max_tokens=1200
            )
            
            gpt_response = response.choices[0].message.content
            self.user_sessions[user_id]["messages"].append({"role": "assistant", "content": gpt_response})
            
            messages_left = MAX_MESSAGES - self.user_sessions[user_id]["messages_count"]
            
            print(f"🔍 DEBUG: Анализ завершен успешно! Сообщений осталось: {messages_left}")
            
            return {
                "analysis": gpt_response,
                "analysis_type": analysis_type,
                "messages_left": messages_left
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа: {e}", exc_info=True)
            return None
    
    def cleanup_sessions(self):
        current_time = time.time()
        expired_users = [
            user_id for user_id, session in self.user_sessions.items()
            if current_time - session["last_activity"] > 3600
        ]
        for user_id in expired_users:
            del self.user_sessions[user_id]
    
    def has_active_session(self, user_id: int) -> bool:
        return user_id in self.user_sessions
    
    def end_session(self, user_id: int):
        """Завершает сессию анализа для пользователя"""
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
            print(f"🔍 DEBUG: Сессия завершена для user_id: {user_id}")