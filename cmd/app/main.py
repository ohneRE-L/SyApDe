import uvicorn
from fastapi import FastAPI
from internal.config.config import load_config
from internal.service.health_service import HealthService
from internal.controller.health_controller import create_health_router

def create_app() -> FastAPI:
    cfg = load_config()
    
    app = FastAPI(
        title=cfg.app_name,
        version=cfg.app_version
    )
    
    # Dependency Injection
    health_svc = HealthService(cfg)
    health_router = create_health_router(health_svc)
    
    app.include_router(health_router)
    return app

app = create_app()

if __name__ == "__main__":
    cfg = load_config()
    uvicorn.run("cmd.app.main:app", host="0.0.0.0", port=cfg.http_port, reload=True)
