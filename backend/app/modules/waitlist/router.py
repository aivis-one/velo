# =============================================================================
# VELO Backend -- Waitlist Router (Phase 5.3, bugfix round)
# =============================================================================
#
# ENDPOINTS:
#   POST   /api/v1/practices/{id}/waitlist    -- join waitlist
#   DELETE /api/v1/waitlist/{id}              -- leave / decline
#   POST   /api/v1/waitlist/{id}/confirm      -- confirm spot
#
# AUTH: get_current_user on all endpoints.
# SESSION: All mutating -- get_db_session (write).
#
# BUGFIX: confirm endpoint returns JSONResponse(400) instead of raising
# when confirm_waitlist returns (entry, None). This ensures get_db_session
# commits the status changes (expired -> EXPIRED, spot taken -> WAITING).
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.waitlist.models import WaitlistStatus
from app.modules.waitlist.schemas import (
    WaitlistConfirmResponse,
    WaitlistEntryResponse,
)
from app.modules.waitlist.service import (
    confirm_waitlist,
    join_waitlist,
    leave_waitlist,
)

# Two routers: one for the nested practices path, one for direct waitlist.
practices_waitlist_router = APIRouter(
    prefix="/api/v1/practices", tags=["waitlist"],
)

waitlist_router = APIRouter(
    prefix="/api/v1/waitlist", tags=["waitlist"],
)


@practices_waitlist_router.post(
    "/{practice_id}/waitlist",
    response_model=WaitlistEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def join_waitlist_endpoint(
    practice_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> WaitlistEntryResponse:
    """Join the waitlist for a full practice."""
    entry = await join_waitlist(user, practice_id, session)
    return WaitlistEntryResponse.model_validate(entry)


@waitlist_router.delete(
    "/{waitlist_id}",
    response_model=WaitlistEntryResponse,
)
async def leave_waitlist_endpoint(
    waitlist_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> WaitlistEntryResponse:
    """Leave the waitlist or decline a spot offer."""
    entry = await leave_waitlist(waitlist_id, user, session)
    await session.flush()
    await session.refresh(entry)
    return WaitlistEntryResponse.model_validate(entry)


@waitlist_router.post(
    "/{waitlist_id}/confirm",
    response_model=WaitlistConfirmResponse,
    status_code=status.HTTP_201_CREATED,
)
async def confirm_waitlist_endpoint(
    waitlist_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> WaitlistConfirmResponse | JSONResponse:
    """Confirm a waitlist spot -- creates a booking.

    Returns 201 + booking on success.
    Returns 400 (as JSONResponse, NOT exception) when expired or spot
    taken. JSONResponse lets get_db_session commit the status changes
    (EXPIRED / back to WAITING) instead of rolling them back.
    """
    entry, booking = await confirm_waitlist(
        waitlist_id, user, session,
    )

    if booking is None:
        # Expired or spot taken -- entry status already updated.
        # Flush so get_db_session sees dirty state and commits.
        await session.flush()
        await session.refresh(entry)

        if entry.status == WaitlistStatus.EXPIRED.value:
            msg = "Waitlist offer has expired"
        else:
            # WAITING -- spot was taken by concurrent booking.
            msg = "Spot is no longer available, returned to waitlist"

        return JSONResponse(
            status_code=400,
            content={"error": "bad_request", "message": msg},
        )

    await session.flush()
    await session.refresh(entry)
    await session.refresh(booking)
    return WaitlistConfirmResponse(
        waitlist_entry=WaitlistEntryResponse.model_validate(entry),
        booking_id=booking.id,
    )
