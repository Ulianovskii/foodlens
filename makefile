.PHONY: run stop restart logs install venv clean check-env setup

# Создание и настройка виртуального окружения
setup:
	python -m venv venv
	@echo "✅ Виртуальное окружение создано"
	@echo "🤖 Для активации выполните: source venv/bin/activate"
	@echo "📦 Затем установите зависимости: make install"

# Установка зависимостей
install:
	@if [ -d "venv" ]; then \
		source venv/bin/activate && python -m pip install -r requirements.txt; \
		echo "✅ Зависимости установлены"; \
	else \
		echo "❌ Виртуальное окружение не найдено. Сначала выполните: make setup"; \
		exit 1; \
	fi

# Проверка окружения
check-env:
	@if ! grep -q "BOT_TOKEN=" .env || grep -q "BOT_TOKEN=your_bot_token_here" .env; then \
		echo "❌ Ошибка: BOT_TOKEN не настроен в .env файле!"; \
		echo "   Получите токен у @BotFather и добавьте в .env"; \
		exit 1; \
	fi
	@echo "✅ Окружение настроено корректно"

# Проверка venv
check-venv:
	@if [ ! -d "venv" ]; then \
		echo "❌ Виртуальное окружение не найдено"; \
		echo "🤖 Выполните: make setup"; \
		exit 1; \
	fi

# Запуск бота
run: check-env check-venv
	source venv/bin/activate && python -m app.bot

# Запуск с авто-перезагрузкой при изменениях кода
dev: check-env check-venv
	@if ! source venv/bin/activate && python -c "import watchdog" 2>/dev/null; then \
		echo "📦 Устанавливаем watchdog..."; \
		source venv/bin/activate && pip install watchdog; \
	fi
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

# Активация venv
venv:
	@if [ -d "venv" ]; then \
		source venv/bin/activate && bash; \
	else \
		echo "❌ Виртуальное окружение не найдено. Выполните: make setup"; \
	fi

# Помощь
help:
	@echo "🍕 FoodLens Bot - Доступные команды:"
	@echo "  make setup    - Создать виртуальное окружение"
	@echo "  make install  - Установить зависимости"
	@echo "  make run      - Запуск бота"
	@echo "  make dev      - Запуск с авто-перезагрузкой"
	@echo "  make stop     - Остановка бота"
	@echo "  make restart  - Перезапуск бота"
	@echo "  make logs     - Просмотр логов"
	@echo "  make venv     - Активация виртуального окружения"
	@echo "  make clean    - Очистка кэша Python"
	@echo "  make check-env - Проверка настроек окружения"