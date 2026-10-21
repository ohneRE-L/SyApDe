# Служба поддержки и тикет-система (Helpdesk / Service Desk)

Репозиторий содержит материалы лабораторных работ по проектированию архитектуры программного обеспечения, описанию спецификации REST API, построению модульного бэкенда по принципам Clean Architecture и контейнеризации приложения с помощью Docker.

---

## Структура репозитория

```text
.
├── cmd/
│   └── app/
│       └── main.py                     # Точка входа в приложение (DI, инициализация и запуск)
├── internal/                           # Внутренний код приложения (Clean Architecture)
│   ├── config/                         # Чтение и типизация переменных окружения (.env)
│   ├── controller/                     # Transport Layer (HTTP роуты, контроллеры)
│   ├── service/                        # Service Layer (бизнес-логика)
│   └── repository/                     # Data Access Layer (интерфейсы доступа к данным)
├── diagrams/                           # Исходные файлы архитектурных диаграмм
│   ├── C4.png                          # C4 Container диаграмма
│   └── ER.png                          # ER-диаграмма базы данных (3NF)
├── .dockerignore                       # Исключения для контекста сборки Docker
├── .env.example                        # Публичный шаблон переменных окружения
├── .gitignore                          # Исключения для Git
├── ARCHITECTURE.md                     # Архитектурный отчет, спецификация БД и REST API
├── Dockerfile                          # Оптимизированный Multi-stage Dockerfile
├── openapi.yaml                        # Спецификация REST API (OpenAPI 3.0.3)
├── README.md                           # Общее описание проекта и инструкции
└── requirements.txt                    # Зависимости Python (FastAPI, Uvicorn, Pydantic)
```

---

## Назначение проекта

Система решает задачи автоматизации сервисного обслуживания:
* Прием, классификация и маршрутизация обращений клиентов.
* Контроль дедлайнов реагирования и решения инцидентов в соответствии с матрицей SLA.
* Ведение единой хронологической ленты диалога с поддержкой файлов-вложений и внутренних служебных заметок.
* Аудит нарушений регламентов обслуживания для аналитики качества сервиса.

---

## Запуск проекта через Docker (Лабораторная работа №4)

### 1. Сборка Docker-образа
Сборка оптимизированного легковесного образа на базе `python:3.11-slim` с использованием многоэтапной сборки (Multi-stage build):
```bash
docker build -t helpdesk-api:latest .
```

Проверка созданного образа:
```bash
docker images
```

### 2. Запуск контейнера
Запуск контейнера в фоновом режиме с пробросом порта `8080` и передачей переменных окружения:
```bash
docker run --name helpdesk-api-container -d -p 8080:8080 -e HTTP_PORT=8080 helpdesk-api:latest
```

### 3. Проверка работоспособности
Проверка эндпоинта состояния здоровья сервиса (Health Check):
```bash
curl http://localhost:8080/api/v1/health
```

Ожидаемый ответ:
```json
{
  "status": "pass",
  "app_name": "Helpdesk Service Desk API",
  "version": "1.0.0",
  "environment": "development"
}
```

### 4. Просмотр логов
```bash
docker logs -f helpdesk-api-container
```

### 5. Остановка и удаление контейнера
```bash
docker stop helpdesk-api-container
docker rm helpdesk-api-container
```
