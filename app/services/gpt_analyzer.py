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
        self.user_sessions = {}
    
    async def analyze_food_image(self, user_id: int, image_file, analysis_type: str = "nutrition", user_message: str = None) -> dict:
        try:
            print(f"🔍 DEBUG: Начало анализа, user_id: {user_id}")
            print(f"🔍 DEBUG: Тип image_file: {type(image_file)}")
            print(f"🔍 DEBUG: analysis_type: {analysis_type}")
            
            MAX_MESSAGES = 5
            
            # Если это первый запрос - конвертируем фото в base64
            if image_file and user_id not in self.user_sessions:
                print("🔍 DEBUG: Первый запрос с фото")
                
                # Проверим что файл можно читать
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
                
                messages = [
                    {
                        "role": "system", 
                        "content": get_system_prompt(None, analysis_type)
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
                    "messages_count": 1
                }
                
            elif user_id in self.user_sessions:
                session = self.user_sessions[user_id]
                if session["messages_count"] >= MAX_MESSAGES:
                    return {"error": "message_limit_reached"}
                
                if user_message:
                    session["messages"].append({"role": "user", "content": user_message})
                    session["messages_count"] += 1
                else:
                    session["messages"][0]["content"] = get_system_prompt(None, analysis_type)
                    session["messages"].append({"role": "user", "content": f"Проанализируй {analysis_type}:"})
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
            
            print(f"🔍 DEBUG: Анализ завершен успешно!")
            
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