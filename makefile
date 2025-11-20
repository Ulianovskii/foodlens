.PHONY: run stop restart logs install venv clean check-env

# Активация venv
venv:
	source venv/bin/activate && bash

# Установка зависимостей
install:
	python -m pip install -r requirements.txt

# Проверка окружения
check-env:
	@if ! grep -q "BOT_TOKEN=" .env || grep -q "BOT_TOKEN=your_bot_token_here" .env; then \
		echo "❌ Ошибка: BOT_TOKEN не настроен в .env файле!"; \
		echo "   Получите токен у @BotFather и добавьте в .env"; \
		exit 1; \
	fi
	@echo "✅ Окружение настроено корректно"

# Запуск бота
run: check-env
	source venv/bin/activate && python -m app.bot

# Запуск с авто-перезагрузкой при изменениях кода
dev: check-env
	source venv/bin/activate && watchmedo auto-restart --pattern="*.py" --recursive -- python -m app.bot

# Остановка бота
stop:
	pkill -f "python.*app.bot" || true
	echo "✅ Бот остановлен"

# Перезапуск бота
restart: stop
	sleep 2
	source venv/bin/activate && python -m app.bot

# Просмотр логов
logs:
	tail -f bot.log 2>/dev/null || echo "📝 Лог-файл не найден. Запустите бота сначала."

# Очистка кэша Python
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	echo "✅ Кэш очищен"

# Помощь
help:
	@echo "🍕 FoodLens Bot - Доступные команды:"
	@echo "  make run      - Запуск бота"
	@echo "  make dev      - Запуск с авто-перезагрузкой"
	@echo "  make stop     - Остановка бота"
	@echo "  make restart  - Перезапуск бота"
	@echo "  make logs     - Просмотр логов"
	@echo "  make install  - Установка зависимостей"
	@echo "  make venv     - Активация виртуального окружения"
	@echo "  make clean    - Очистка кэша Python"
	@echo "  make check-env - Проверка настроек окружения"