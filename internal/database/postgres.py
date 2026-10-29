import asyncio
import logging
from typing import Optional
import asyncpg
from internal.config.config import Config

logger = logging.getLogger("helpdesk.database")

MAX_ATTEMPTS = 10


async def connect_db(cfg: Config) -> asyncpg.Pool:
    """
    Создает пул соединений с PostgreSQL с ограничением размера
    и повторными попытками подключения (retry loop с растущей паузой).
    """
    min_conns = min(2, cfg.db_max_conns)
    last_error: Optional[Exception] = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        pool = None
        try:
            pool = await asyncpg.create_pool(
                dsn=cfg.dsn,
                min_size=min_conns,
                max_size=cfg.db_max_conns,
                max_inactive_connection_lifetime=300.0,
                command_timeout=10.0,
            )

            # Проверяем реальную доступность СУБД через ping (SELECT 1)
            async with pool.acquire() as conn:
                await asyncio.wait_for(conn.fetchval("SELECT 1"), timeout=3.0)

            logger.info(
                f"[DATABASE] Successfully connected to PostgreSQL at {cfg.db_host}:{cfg.db_port} (pool size: {min_conns}..{cfg.db_max_conns})"
            )
            return pool

        except Exception as err:
            last_error = err
            if pool is not None:
                await pool.close()

            wait_time = attempt * 1.0  # Линейно растущая пауза
            logger.warning(
                f"[DATABASE] Attempt {attempt}/{MAX_ATTEMPTS} failed: {err}; retry in {wait_time:.1f}s"
            )

            if attempt < MAX_ATTEMPTS:
                await asyncio.sleep(wait_time)

    raise ConnectionError(
        f"[DATABASE] Database is unavailable after {MAX_ATTEMPTS} attempts. Last error: {last_error}"
    )


async def check_db_health(pool: Optional[asyncpg.Pool]) -> bool:
    """
    Проверяет доступность базы данных выполнением легковесного запроса SELECT 1.
    Возвращает True, если соединение успешно, иначе False.
    """
    if pool is None:
        return False
    try:
        async with pool.acquire() as conn:
            val = await asyncio.wait_for(conn.fetchval("SELECT 1"), timeout=2.0)
            return val == 1
    except Exception as e:
        logger.error(f"[DATABASE] Health check failed: {e}")
        return False
