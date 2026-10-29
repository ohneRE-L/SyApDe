from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from internal.service.health_service import HealthService


def create_health_router(health_service: HealthService) -> APIRouter:
    router = APIRouter(tags=["Health"])

    async def _health_handler():
        payload, is_healthy = await health_service.get_health_status()
        status_code = status.HTTP_200_OK if is_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        return JSONResponse(content=payload, status_code=status_code)

    # Поддержка эндпоинта /health (из ТЗ Лабораторной работы №5)
    @router.get("/health", summary="Health check с проверкой доступности СУБД")
    async def get_health():
        return await _health_handler()

    # Поддержка версионированного пути /api/v1/health (из предыдущих лабораторных)
    @router.get("/api/v1/health", summary="Версионированный Health check")
    async def get_api_health():
        return await _health_handler()

    return router
