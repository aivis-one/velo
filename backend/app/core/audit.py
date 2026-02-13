# =============================================================================
# VELO Backend -- Audit Service (Pre-6.2)
# =============================================================================
#
# Immutable audit log for financial and administrative operations.
# Required by law for financial transactions (5-year retention).
#
# MODEL:
#   AuditLog -- append-only table. No UPDATE, no DELETE in application code.
#   Not using UUIDMixin/TimestampMixin because:
#     - No updated_at (immutable records)
#     - Explicit column definitions for clarity in an audit context
#
# SERVICE:
#   record_audit() -- creates an AuditLog entry in the current session.
#   Does NOT commit (P-01) -- caller's session handles it.
#   Reads trace_id from structlog contextvars (Pre-6.1 middleware).
#
# ACTOR TYPES:
#   "user"   -- regular user performing an action
#   "admin"  -- admin performing moderation/verification
#   "system" -- automated action (cron, listener, webhook)
#
# MANDATORY EVENTS (Phase 6+):
#   balance_topup, purchase_created, purchase_refunded,
#   withdrawal_requested, withdrawal_confirmed,
#   master_verified, master_rejected, role_changed,
#   user_blocked, practice_cancelled
#
# TRACE ID LINKAGE:
#   trace_id, ip_address, and user_agent are read from structlog
#   contextvars, populated by TraceIdMiddleware (Pre-6.1).
#   This links audit entries to application logs and captures
#   request origin for security forensics.
# =============================================================================

from datetime import datetime
from uuid import UUID, uuid4

import structlog
from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

logger = structlog.get_logger()


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


class AuditLog(Base):
    """Immutable audit log entry.

    Append-only -- application code must never UPDATE or DELETE rows.
    Retention: 5 years (legal requirement for financial operations).
    """

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )

    # -- What happened --
    event: Mapped[str] = mapped_column(String(100), index=True)

    # -- Who did it --
    # actor_id is None for system actions (cron, webhooks).
    actor_id: Mapped[UUID | None] = mapped_column()
    actor_type: Mapped[str] = mapped_column(String(20))

    # -- What was affected --
    target_type: Mapped[str] = mapped_column(String(50))
    target_id: Mapped[UUID] = mapped_column()

    # -- Context --
    data: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        server_default="{}",
    )

    # -- Request context (populated from middleware / contextvars) --
    ip_address: Mapped[str | None] = mapped_column(String(45))
    user_agent: Mapped[str | None] = mapped_column(String(500))
    trace_id: Mapped[str | None] = mapped_column(String(36))

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.id} event={self.event} "
            f"actor={self.actor_type}:{self.actor_id}>"
        )


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


async def record_audit(
    *,
    event: str,
    actor_id: UUID | None,
    actor_type: str,
    target_type: str,
    target_id: UUID,
    data: dict | None = None,
    session: AsyncSession,
) -> AuditLog:
    """Record an audit log entry.

    Creates an AuditLog row in the current session. Does NOT commit
    (P-01) -- the caller's transaction handles commit/rollback.

    trace_id is read from structlog contextvars automatically
    (set by TraceIdMiddleware in Pre-6.1).

    Args:
        event: Event name (e.g. "master_verified", "purchase_created").
        actor_id: UUID of the user/admin performing the action. None for system.
        actor_type: "user", "admin", or "system".
        target_type: Type of affected entity (e.g. "master_profile", "purchase").
        target_id: UUID of the affected entity.
        data: Additional context as dict (stored in JSONB).
        session: AsyncSession -- must be an active write session.

    Returns:
        The created AuditLog entry (not yet committed).
    """
    # Read request context from structlog contextvars (Pre-6.1).
    ctx = structlog.contextvars.get_contextvars()
    trace_id = ctx.get("trace_id")
    ip_address = ctx.get("ip_address")
    user_agent = ctx.get("user_agent")

    entry = AuditLog(
        event=event,
        actor_id=actor_id,
        actor_type=actor_type,
        target_type=target_type,
        target_id=target_id,
        data=data or {},
        trace_id=trace_id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    session.add(entry)

    logger.info(
        "audit_recorded",
        event=event,
        actor_type=actor_type,
        actor_id=str(actor_id) if actor_id else None,
        target_type=target_type,
        target_id=str(target_id),
        trace_id=trace_id,
    )

    return entry
