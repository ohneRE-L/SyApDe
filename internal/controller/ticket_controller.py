"""
HTTP-контроллер обращений (тикетов): создание, чтение по id, список, закрытие.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse

from internal.dto.schemas import CreateTicketRequest, TicketResponse
from internal.repository.postgres.category_pg_repository import PgCategoryRepository
from internal.repository.postgres.sla_policy_pg_repository import PgSlaPolicyRepository
from internal.repository.postgres.ticket_pg_repository import PgTicketRepository
from internal.repository.postgres.user_pg_repository import PgUserRepository
from internal.service.ticket_service import TicketService


def get_ticket_service(request: Request) -> TicketService:
    pool = request.app.state.db_pool
    return TicketService(
        tickets=PgTicketRepository(pool),
        categories=PgCategoryRepository(pool),
        users=PgUserRepository(pool),
        sla_policies=PgSlaPolicyRepository(pool),
    )


def create_ticket_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1/tickets", tags=["Tickets"])

    @router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
    async def create_ticket(
        body: CreateTicketRequest,
        svc: TicketService = Depends(get_ticket_service),
    ):
        created = await svc.create(
            subject=body.subject,
            description=body.description,
            priority=body.priority,
            category_id=str(body.category_id),
            requester_id=str(body.requester_id),
        )
        dto = TicketResponse.from_domain(created)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=dto.model_dump(mode="json"),
            headers={"Location": f"/api/v1/tickets/{created.id}"},
        )

    @router.get("", response_model=List[TicketResponse])
    async def list_tickets(
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        svc: TicketService = Depends(get_ticket_service),
    ) -> List[TicketResponse]:
        items = await svc.list(limit=limit, offset=offset)
        return [TicketResponse.from_domain(t) for t in items]

    @router.get("/{ticket_id}", response_model=TicketResponse)
    async def get_ticket(
        ticket_id: UUID,
        svc: TicketService = Depends(get_ticket_service),
    ) -> TicketResponse:
        ticket = await svc.get(str(ticket_id))
        return TicketResponse.from_domain(ticket)

    @router.post("/{ticket_id}/close", response_model=TicketResponse)
    async def close_ticket(
        ticket_id: UUID,
        svc: TicketService = Depends(get_ticket_service),
    ) -> TicketResponse:
        closed = await svc.close(str(ticket_id))
        return TicketResponse.from_domain(closed)

    return router
