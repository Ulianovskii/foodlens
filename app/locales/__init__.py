from app.locales.base import localization_manager
from app.locales.ru.texts import RussianLocalization

# Регистрируем русскую локализацию
localization_manager.register_locale('ru', RussianLocalization())

# Экспортируем удобные функции
def get_text(key: str, lang: str = None, **kwargs) -> str:
    return localization_manager.get_text(key, lang, **kwargs)

def get_button(key: str, lang: str = None) -> str:
    return localization_manager.get_button(key, lang)

__all__ = ['localization_manager', 'get_text', 'get_button']