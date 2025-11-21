# app/services/gpt_analyzer.py
import base64
import logging
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
from app.prompts import get_system_prompt

logger = logging.getLogger(__name__)

class GPTAnalyzer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    async def analyze_food_image(self, image_path: str, user_description: str = None) -> dict:
        """Анализирует фото еды и возвращает пищевую ценность + рецепт"""
        try:
            # Кодируем изображение в base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            system_prompt = get_system_prompt(user_description)
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
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
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1200
            )
            
            analysis_text = response.choices[0].message.content
            return {
                "analysis": analysis_text,
                "user_description": user_description
            }
            
        except Exception as e:
            logger.error(f"Ошибка анализа изображения: {e}")
            return None