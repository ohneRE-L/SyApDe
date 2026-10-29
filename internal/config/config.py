import os
import urllib.parse
from dataclasses import dataclass
from dotenv import load_dotenv

# Загрузка переменных из локального .env файла при его наличии
load_dotenv()


@dataclass(frozen=True)
class Config:
    app_name: str
    app_env: str
    app_version: str
    http_port: int

    # Параметры подключения к PostgreSQL
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str
    db_max_conns: int

    @property
    def dsn(self) -> str:
        """Формирует строку подключения DSN с безопасным экранированием спецсимволов."""
        encoded_user = urllib.parse.quote_plus(self.db_user)
        encoded_password = urllib.parse.quote_plus(self.db_password)
        return f"postgresql://{encoded_user}:{encoded_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def masked_dsn(self) -> str:
        """DSN со скрытым паролем для безопасного логирования."""
        return f"postgresql://{self.db_user}:******@{self.db_host}:{self.db_port}/{self.db_name}"


def get_env(key: str, fallback: str = "") -> str:
    val = os.getenv(key)
    return val if val is not None and val != "" else fallback


def load_config() -> Config:
    """
    Загружает конфигурацию приложения из переменных окружения.
    Проверяет наличие всех обязательных параметров подключения к БД.
    """
    app_name = get_env("APP_NAME", "Helpdesk Service Desk API")
    app_env = get_env("APP_ENV", "development")
    app_version = get_env("APP_VERSION", "1.0.0")

    try:
        http_port = int(get_env("HTTP_PORT", "8080"))
    except ValueError:
        raise ValueError("[CONFIG] HTTP_PORT must be a valid integer")

    db_host = get_env("DB_HOST")
    db_user = get_env("DB_USER")
    db_password = get_env("DB_PASSWORD")
    db_name = get_env("DB_NAME")

    # Валидация обязательных параметров подключения к БД
    required = {
        "DB_HOST": db_host,
        "DB_USER": db_user,
        "DB_PASSWORD": db_password,
        "DB_NAME": db_name,
    }

    for name, value in required.items():
        if not value:
            raise ValueError(f"[CONFIG] Required environment variable '{name}' is not set")

    try:
        db_port = int(get_env("DB_PORT", "5432"))
        if db_port < 1 or db_port > 65535:
            raise ValueError
    except ValueError:
        raise ValueError("[CONFIG] DB_PORT must be an integer between 1 and 65535")

    try:
        db_max_conns = int(get_env("DB_MAX_CONNS", "10"))
        if db_max_conns < 1:
            raise ValueError
    except ValueError:
        raise ValueError("[CONFIG] DB_MAX_CONNS must be a positive integer")

    return Config(
        app_name=app_name,
        app_env=app_env,
        app_version=app_version,
        http_port=http_port,
        db_host=db_host,
        db_port=db_port,
        db_user=db_user,
        db_password=db_password,
        db_name=db_name,
        db_max_conns=db_max_conns,
    )
