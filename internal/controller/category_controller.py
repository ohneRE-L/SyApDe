"""
HTTP-контроллер категорий обращений (полный CRUD).
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import JSONResponse

from internal.dto.schemas import CategoryRequest, CategoryResponse
from internal.repository.postgres.category_pg_repository import PgCategoryRepository
from internal.service.category_service import CategoryService


def get_category_service(request: Request) -> CategoryService:
    pool = request.app.state.db_pool
    return CategoryService(PgCategoryRepository(pool))


def create_category_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

    @router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
    async def create_category(
        body: CategoryRequest,
        svc: CategoryService = Depends(get_category_service),
    ):
        created = await svc.create(title=body.title, description=body.description)
        dto = CategoryResponse.from_domain(created)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=dto.model_dump(mode="json"),
            headers={"Location": f"/api/v1/categories/{created.id}"},
        )

    @router.get("", response_model=List[CategoryResponse])
    async def list_categories(
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        svc: CategoryService = Depends(get_category_service),
    ) -> List[CategoryResponse]:
        items = await svc.list(limit=limit, offset=offset)
        return [CategoryResponse.from_domain(c) for c in items]

    @router.get("/{category_id}", response_model=CategoryResponse)
    async def get_category(
        category_id: UUID,
        svc: CategoryService = Depends(get_category_service),
    ) -> CategoryResponse:
        category = await svc.get(str(category_id))
        return CategoryResponse.from_domain(category)

    @router.put("/{category_id}", response_model=CategoryResponse)
    async def update_category(
        category_id: UUID,
        body: CategoryRequest,
        svc: CategoryService = Depends(get_category_service),
    ) -> CategoryResponse:
        updated = await svc.update(
            category_id=str(category_id),
            title=body.title,
            description=body.description,
            is_active=body.is_active,
        )
        return CategoryResponse.from_domain(updated)

    @router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_category(
        category_id: UUID,
        svc: CategoryService = Depends(get_category_service),
    ) -> Response:
        await svc.delete(str(category_id))
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return router
