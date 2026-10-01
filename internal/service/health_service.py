from internal.config.config import Config

class HealthService:
    def __init__(self, cfg: Config):
        self._cfg = cfg

    def get_health_status(self) -> dict:
        return {
            "status": "pass",
            "app_name": self._cfg.app_name,
            "version": self._cfg.app_version,
            "environment": self._cfg.app_env
        }
