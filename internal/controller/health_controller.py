from fastapi import APIRouter
from internal.service.health_service import HealthService

def create_health_router(health_service: HealthService) -> APIRouter:
    router = APIRouter(prefix="/api/v1", tags=["Health"])

    @router.get("/health", status_code=200)
    async def get_health():
        return health_service.get_health_status()

    return router
