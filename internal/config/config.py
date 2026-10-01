import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

@dataclass(frozen=True)
class Config:
    app_name: str
    app_env: str
    app_version: str
    http_port: int

def load_config() -> Config:
    return Config(
        app_name=os.getenv("APP_NAME", "Helpdesk Service Desk API"),
        app_env=os.getenv("APP_ENV", "development"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        http_port=int(os.getenv("HTTP_PORT", "8080"))
    )
