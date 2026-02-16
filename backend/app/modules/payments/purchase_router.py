# =============================================================================
# VELO Backend -- Purchase Router (Phase 6.4)
# =============================================================================
#
# ENDPOINTS:
#   POST /api/v1/practices/{practice_id}/purchase -- purchase a practice
#
# This is an alias for the booking flow: creates Booking + Purchase
# in a single transaction. Returns PurchaseResponse (richer than
# BookingResponse -- includes financial details).
#
# AUTH: get_current_user.
# SESSION: get_db_session (write).
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.bookings.service import create_booking
from app.modules.payments.models import Purchase
from app.modules.payments.schemas import PurchaseResponse
from app.modules.users.models import User

router = APIRouter(
    prefix="/api/v1/practices",
    tags=["purchases"],
)


@router.post(
    "/{practice_id}/purchase",
    response_model=PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def purchase_practice_endpoint(
    practice_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> PurchaseResponse:
    """Purchase a practice -- creates Booking + Purchase.

    For free practices: paid_cents=0, ledger entries with amount=0.
    For paid practices: checks balance, deducts from user, freezes at master.

    Returns full purchase details including financial info.
    """
    booking = await create_booking(user, practice_id, session)
    await session.flush()

    # Load the Purchase created inside create_booking.
    purchase = await session.get(Purchase, booking.purchase_id)
    await session.refresh(purchase)

    return PurchaseResponse.model_validate(purchase)
