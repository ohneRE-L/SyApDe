"""
Доменные модели (сущности предметной области Helpdesk).

Используют dataclass для простоты — без внешних зависимостей.
UUID хранятся как str, datetime — как datetime с tzinfo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: str
    name: str
    email: str
    password_hash: str
    role: str          # USER | SUPPORT_AGENT | ADMIN
    is_active: bool
    created_at: datetime


@dataclass
class Category:
    id: str
    title: str
    description: Optional[str]
    is_active: bool
    created_at: datetime


@dataclass
class SlaPolicy:
    id: str
    priority: str      # LOW | MEDIUM | HIGH | CRITICAL
    max_first_response_time_minutes: int
    max_resolution_time_minutes: int
    created_at: datetime


@dataclass
class Ticket:
    id: str
    subject: str
    description: str
    status: str        # OPEN | IN_PROGRESS | WAITING_FOR_USER | RESOLVED | CLOSED
    priority: str      # LOW | MEDIUM | HIGH | CRITICAL
    category_id: str
    requester_id: str
    sla_policy_id: str
    response_due_at: datetime
    resolution_due_at: datetime
    created_at: datetime
    updated_at: datetime
    assignee_id: Optional[str] = None
    first_responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None


@dataclass
class TicketMessage:
    id: str
    ticket_id: str
    sender_id: str
    body: str
    is_internal: bool
    created_at: datetime


@dataclass
class Attachment:
    id: str
    message_id: str
    file_name: str
    file_url: str
    file_size_bytes: int
    content_type: str
    created_at: datetime


@dataclass
class SlaAuditLog:
    id: str
    ticket_id: str
    breach_type: str   # RESPONSE_OVERDUE | RESOLUTION_OVERDUE
    breached_at: datetime
    note: Optional[str]
