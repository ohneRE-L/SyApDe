from typing import Optional, Tuple
import asyncpg
from internal.config.config import Config
from internal.database.postgres import check_db_health


class HealthService:
    def __init__(self, cfg: Config, db_pool: Optional[asyncpg.Pool] = None):
        self._cfg = cfg
        self._db_pool = db_pool

    def set_db_pool(self, db_pool: Optional[asyncpg.Pool]) -> None:
        self._db_pool = db_pool

    async def get_health_status(self) -> Tuple[dict, bool]:
        """
        Проверяет доступность базы данных и возвращает словарь со статусом
        и булев флаг доступности (True = 200 OK, False = 503 Service Unavailable).
        """
        db_is_up = await check_db_health(self._db_pool)

        payload = {
            "status": "ok" if db_is_up else "unavailable",
            "db": "up" if db_is_up else "down",
            "app_name": self._cfg.app_name,
            "version": self._cfg.app_version,
            "environment": self._cfg.app_env,
        }
        return payload, db_is_up
