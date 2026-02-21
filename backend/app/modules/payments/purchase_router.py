# =============================================================================
# VELO Backend -- Purchase Router (Phase 6.4 + Frontend Backlog, updated 6.7)
# =============================================================================
#
# ENDPOINTS:
#   POST /api/v1/practices/{practice_id}/purchase  -- purchase a practice
#   GET  /api/v1/purchases/me                      -- my purchases (Backlog)
#
# Two routers:
#   router                -- prefix /api/v1/practices (existing alias)
#   purchases_user_router -- prefix /api/v1/purchases (new user-facing)
#
# AUTH: get_current_user.
# SESSION: POST = get_db_session (write). GET = get_db_reader (read).
# =============================================================================

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.bookings.service import create_booking
from app.modules.payments.models import Purchase
from app.modules.payments.purchase import list_user_purchases
from app.modules.payments.schemas import (
    PaginatedPurchasesResponse,
    PurchaseResponse,
    PurchaseWithPracticeResponse,
)
from app.modules.practices.schemas import PracticeSummary
from app.modules.users.models import User

router = APIRouter(
    prefix="/api/v1/practices",
    tags=["purchases"],
)

purchases_user_router = APIRouter(
    prefix="/api/v1/purchases",
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


# ===================================================================
# Frontend Backlog: GET /me -- my purchases
# ===================================================================


@purchases_user_router.get(
    "/me",
    response_model=PaginatedPurchasesResponse,
)
async def list_my_purchases_endpoint(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
    status_filter: str | None = Query(
        default=None, alias="status",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedPurchasesResponse:
    """List purchases for the current user.

    Returns paginated list with embedded PracticeSummary so the
    frontend can render purchase history cards.

    Optional ``status`` filter (e.g. ``?status=completed``).
    """
    items, total = await list_user_purchases(
        user, session,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )

    return PaginatedPurchasesResponse(
        items=[
            PurchaseWithPracticeResponse(
                id=purchase.id,
                user_id=purchase.user_id,
                practice_id=purchase.practice_id,
                booking_id=purchase.booking_id,
                promo_id=purchase.promo_id,
                amount_cents=purchase.amount_cents,
                discount_cents=purchase.discount_cents,
                paid_cents=purchase.paid_cents,
                currency=purchase.currency,
                commission_cents=purchase.commission_cents,
                status=purchase.status,
                completed_at=purchase.completed_at,
                created_at=purchase.created_at,
                updated_at=purchase.updated_at,
                practice=PracticeSummary.model_validate(practice),
            )
            for purchase, practice in items
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
