# ==========================================
# Этап 1: Сборка зависимостей (Builder)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Переменные окружения для сборки Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Создаем изолированное виртуальное окружение
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копируем файл зависимостей отдельно для эффективного кэширования слоев Docker
COPY requirements.txt .

# Устанавливаем зависимости без сохранения кэша pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# Этап 2: Финальный легковесный образ (Runner)
# ==========================================
FROM python:3.11-slim AS runner

WORKDIR /app

# Переменные окружения для работы в продакшене:
# - PYTHONDONTWRITEBYTECODE: не засорять контейнер .pyc файлами
# - PYTHONUNBUFFERED: немедленный вывод логов в stdout/stderr (важно для docker logs)
# - HTTP_PORT: порт по умолчанию для сервиса
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    HTTP_PORT=8080

# Создаем непривилегированного пользователя для безопасности (non-root)
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -s /bin/sh appuser

# Копируем готовое виртуальное окружение из этапа сборщика
COPY --from=builder /opt/venv /opt/venv

# Копируем исходный код приложения с назначением прав непривилегированному пользователю
COPY --chown=appuser:appuser . .

# Переключаемся на непривилегированного пользователя
USER appuser

# Декларируем рабочий порт приложения
EXPOSE 8080

# Команда запуска FastAPI-приложения через ASGI-сервер Uvicorn
CMD ["uvicorn", "cmd.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
