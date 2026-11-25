"""
DTO (Data Transfer Objects) для запросов и ответов REST API.

Отделены от доменных моделей: конфиденциальные поля (например, password_hash)
никогда не попадают в DTO ответа.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from internal.domain.models import Category, Ticket


class CategoryRequest(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: bool = True


class CategoryResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    @classmethod
    def from_domain(cls, category: Category) -> CategoryResponse:
        return cls(
            id=category.id,
            title=category.title,
            description=category.description,
            is_active=category.is_active,
            created_at=category.created_at,
        )


class CreateTicketRequest(BaseModel):
    subject: str
    description: str
    priority: str = "MEDIUM"
    category_id: UUID
    requester_id: UUID


class TicketResponse(BaseModel):
    id: str
    subject: str
    description: str
    status: str
    priority: str
    category_id: str
    requester_id: str
    assignee_id: Optional[str]
    sla_policy_id: str
    response_due_at: datetime
    resolution_due_at: datetime
    first_responded_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, ticket: Ticket) -> TicketResponse:
        return cls(
            id=ticket.id,
            subject=ticket.subject,
            description=ticket.description,
            status=ticket.status,
            priority=ticket.priority,
            category_id=ticket.category_id,
            requester_id=ticket.requester_id,
            assignee_id=ticket.assignee_id,
            sla_policy_id=ticket.sla_policy_id,
            response_due_at=ticket.response_due_at,
            resolution_due_at=ticket.resolution_due_at,
            first_responded_at=ticket.first_responded_at,
            resolved_at=ticket.resolved_at,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
        )


class ErrorResponse(BaseModel):
    error: str
