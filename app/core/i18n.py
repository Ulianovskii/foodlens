# app/core/i18n.py
from app.locales.ru.texts import RussianLocalization
import logging

logger = logging.getLogger(__name__)

class LocalizationManager:
    def __init__(self):
        self._localizations = {
            'ru': RussianLocalization()
        }
        self.default_lang = 'ru'
    
    def get_localization(self, lang: str = None):
        lang = lang or self.default_lang
        localization = self._localizations.get(lang)
        if not localization:
            logger.warning(f"Локализация для языка '{lang}' не найдена, используется '{self.default_lang}'")
            localization = self._localizations[self.default_lang]
        return localization

# Глобальный экземпляр менеджера локализации
localization_manager = LocalizationManager()

def get_localization(lang: str = None):
    """Получить объект локализации для указанного языка"""
    return localization_manager.get_localization(lang)