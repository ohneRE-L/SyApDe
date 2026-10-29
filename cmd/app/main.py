from contextlib import asynccontextmanager
import logging
import uvicorn
from fastapi import FastAPI
from internal.config.config import load_config
from internal.database.postgres import connect_db
from internal.service.health_service import HealthService
from internal.controller.health_controller import create_health_router

# Настройка логирования приложения
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("helpdesk.app")


def create_app() -> FastAPI:
    cfg = load_config()
    logger.info("[CONFIG] Environment variables loaded successfully")
    logger.info(f"[CONFIG] Connecting to database: {cfg.masked_dsn}")

    # Создаем сервис с начальной привязкой к конфигурации
    health_svc = HealthService(cfg)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: подключение к PostgreSQL через пул соединений с retry-логикой
        db_pool = None
        try:
            db_pool = await connect_db(cfg)
            health_svc.set_db_pool(db_pool)
            app.state.db_pool = db_pool
        except Exception as e:
            logger.error(f"[DATABASE] Initial connection to database failed: {e}")
            health_svc.set_db_pool(None)

        yield

        # Shutdown: корректное закрытие пула соединений (Graceful Shutdown)
        if db_pool is not None:
            logger.info("[DATABASE] Closing PostgreSQL connection pool...")
            await db_pool.close()
            logger.info("[DATABASE] PostgreSQL connection pool closed.")

    app = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version,
        lifespan=lifespan,
    )

    # Регистрация маршрутизатора
    health_router = create_health_router(health_svc)
    app.include_router(health_router)

    return app


app = create_app()

if __name__ == "__main__":
    cfg = load_config()
    uvicorn.run("cmd.app.main:app", host="0.0.0.0", port=cfg.http_port, reload=False)
