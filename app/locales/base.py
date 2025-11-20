from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseLocalization(ABC):
    """Базовый класс для локализации"""
    
    @abstractmethod
    def get_text(self, key: str, **kwargs) -> str:
        """Получить текст по ключу"""
        pass
    
    @abstractmethod
    def get_button_text(self, key: str) -> str:
        """Получить текст кнопки по ключу"""
        pass


class LocalizationManager:
    """Менеджер локализации"""
    
    def __init__(self, default_lang: str = 'ru'):
        self._locales: Dict[str, BaseLocalization] = {}
        self.default_lang = default_lang
    
    def register_locale(self, lang: str, locale: BaseLocalization):
        """Зарегистрировать локализацию для языка"""
        self._locales[lang] = locale
    
    def get_locale(self, lang: str = None) -> BaseLocalization:
        """Получить объект локализации для языка"""
        lang = lang or self.default_lang
        return self._locales.get(lang, self._locales[self.default_lang])
    
    def get_text(self, key: str, lang: str = None, **kwargs) -> str:
        """Получить текст по ключу для языка"""
        locale = self.get_locale(lang)
        return locale.get_text(key, **kwargs)
    
    def get_button(self, key: str, lang: str = None) -> str:
        """Получить текст кнопки по ключу для языка"""
        locale = self.get_locale(lang)
        return locale.get_button_text(key)


# Глобальный менеджер локализации
localization_manager = LocalizationManager()