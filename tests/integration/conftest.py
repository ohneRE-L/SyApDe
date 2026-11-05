"""
Вспомогательный conftest для интеграционных тестов репозиториев.

Переменные среды для подключения к тестовой БД берутся из .env
(тот же docker-compose postgres-сервис, что и для приложения).
"""

import asyncio
import os

import asyncpg
import pytest
import pytest_asyncio
from dotenv import load_dotenv

load_dotenv()


def _dsn() -> str:
    return (
        f"postgresql://{os.getenv('DB_USER', 'helpdesk_user')}"
        f":{os.getenv('DB_PASSWORD', 'helpdesk_pass')}"
        f"@{os.getenv('DB_HOST', 'localhost')}"
        f":{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME', 'helpdesk_db')}"
    )


@pytest_asyncio.fixture(scope="session")
async def pool():
    """Пул соединений на всю сессию тестов."""
    p = await asyncpg.create_pool(_dsn(), min_size=1, max_size=3)
    yield p
    await p.close()
