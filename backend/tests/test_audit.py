# =============================================================================
# Test: Audit Service (Pre-6.2)
# =============================================================================
#
# Tests record_audit() function:
#   - Creates an AuditLog entry in the database
#   - Picks up trace_id from structlog contextvars
#   - Works without trace_id (system actions outside request)
#   - Stores data dict as JSONB
#
# Uses db_session directly (no HTTP endpoints for audit yet).
# =============================================================================

from uuid import uuid4

import pytest
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import AuditLog, record_audit


@pytest.mark.asyncio
async def test_record_audit_basic(db_session: AsyncSession) -> None:
    """record_audit creates an AuditLog row with all fields."""
    actor_id = uuid4()
    target_id = uuid4()

    entry = await record_audit(
        event="master_verified",
        actor_id=actor_id,
        actor_type="admin",
        target_type="master_profile",
        target_id=target_id,
        data={"notes": "Looks good"},
        session=db_session,
    )

    await db_session.flush()
    await db_session.refresh(entry)

    assert entry.id is not None
    assert entry.event == "master_verified"
    assert entry.actor_id == actor_id
    assert entry.actor_type == "admin"
    assert entry.target_type == "master_profile"
    assert entry.target_id == target_id
    assert entry.data == {"notes": "Looks good"}
    assert entry.created_at is not None

    # Verify it's actually in the database.
    stmt = select(AuditLog).where(AuditLog.id == entry.id)
    result = await db_session.execute(stmt)
    from_db = result.scalar_one()
    assert from_db.event == "master_verified"

    # Cleanup.
    await db_session.delete(from_db)
    await db_session.commit()


@pytest.mark.asyncio
async def test_record_audit_picks_up_trace_id(
    db_session: AsyncSession,
) -> None:
    """record_audit reads trace_id from structlog contextvars."""
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(trace_id="test-trace-999")

    target_id = uuid4()
    entry = await record_audit(
        event="purchase_created",
        actor_id=uuid4(),
        actor_type="user",
        target_type="purchase",
        target_id=target_id,
        session=db_session,
    )

    await db_session.flush()
    await db_session.refresh(entry)

    assert entry.trace_id == "test-trace-999"

    # Cleanup.
    structlog.contextvars.clear_contextvars()
    await db_session.delete(entry)
    await db_session.commit()


@pytest.mark.asyncio
async def test_record_audit_no_trace_id(
    db_session: AsyncSession,
) -> None:
    """record_audit works without trace_id (e.g. system cron job)."""
    structlog.contextvars.clear_contextvars()

    target_id = uuid4()
    entry = await record_audit(
        event="practice_cancelled",
        actor_id=None,
        actor_type="system",
        target_type="practice",
        target_id=target_id,
        session=db_session,
    )

    await db_session.flush()
    await db_session.refresh(entry)

    assert entry.trace_id is None
    assert entry.actor_id is None
    assert entry.actor_type == "system"

    # Cleanup.
    await db_session.delete(entry)
    await db_session.commit()


@pytest.mark.asyncio
async def test_record_audit_default_data(
    db_session: AsyncSession,
) -> None:
    """data defaults to empty dict when not provided."""
    target_id = uuid4()
    entry = await record_audit(
        event="role_changed",
        actor_id=uuid4(),
        actor_type="admin",
        target_type="user",
        target_id=target_id,
        session=db_session,
    )

    await db_session.flush()
    await db_session.refresh(entry)

    assert entry.data == {}

    # Cleanup.
    await db_session.delete(entry)
    await db_session.commit()
