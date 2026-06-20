# =============================================================================
# VELO Backend -- Admin Practices Service (E9 / 4c)
# =============================================================================
#
# Read-only global practices oversight.
#
# LIST (GET /admin/practices?scope=all|upcoming|past):
#   All platform practices except draft/deleted (matches the public
#   practices_count definition), joined to their master for name + verified
#   badge. scope filters on scheduled_at vs now; booked = non-cancelled
#   bookings per practice (one grouped query for the page). Newest first.
#
# DETAIL (GET /admin/practices/{id}):
#   Practice + master + booked/attended counts + full non-cancelled roster
#   (each entry carries its booking status; the frontend buckets attended /
#   no_show for past practices). 404 when missing or soft-deleted.
#
# SESSION RULES: read-only, no commit (P-01), ORM-only.
# =============================================================================

from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.modules.admin.practices.schemas import (
    AdminPracticeDetailResponse,
    AdminPracticeListItem,
    AdminRosterEntry,
    PaginatedAdminPracticesResponse,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.masters.models import MasterProfile
from app.modules.practices.models import Practice, PracticeStatus
from app.modules.users.helpers import display_name
from app.modules.users.models import User

logger = structlog.get_logger()

# Statuses never shown in the admin list (not "real" practices).
_HIDDEN_STATUSES = (
    PracticeStatus.DRAFT.value,
    PracticeStatus.DELETED.value,
)


def _temporal_status(scheduled_at: datetime, now: datetime) -> str:
    """upcoming if the practice has not happened yet, else past."""
    return "upcoming" if scheduled_at >= now else "past"


def _master_name(profile: MasterProfile, user: User) -> str:
    """Master display name: profile display_name -> first_name -> fallback."""
    display = profile.data.get("profile", {}).get("display_name")
    return display or user.first_name or "Мастер"


def _master_verified(profile: MasterProfile) -> bool:
    return profile.data.get("account", {}).get("status") == "verified"


async def list_admin_practices(
    session: AsyncSession,
    *,
    scope: str = "all",
    limit: int = 20,
    offset: int = 0,
) -> PaginatedAdminPracticesResponse:
    """List all platform practices (except draft/deleted), newest first."""
    now = datetime.now(UTC)

    conditions = [Practice.status.notin_(_HIDDEN_STATUSES)]
    if scope == "upcoming":
        conditions.append(Practice.scheduled_at >= now)
    elif scope == "past":
        conditions.append(Practice.scheduled_at < now)

    total = (
        await session.execute(
            select(func.count(Practice.id)).where(*conditions)
        )
    ).scalar_one()

    rows = (
        await session.execute(
            select(Practice, MasterProfile, User)
            .join(MasterProfile, Practice.master_id == MasterProfile.user_id)
            .join(User, MasterProfile.user_id == User.id)
            .where(*conditions)
            .order_by(Practice.scheduled_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()

    page_ids = [practice.id for practice, _profile, _user in rows]
    booked_map: dict[UUID, int] = {}
    if page_ids:
        booked_rows = (
            await session.execute(
                select(Booking.practice_id, func.count(Booking.id))
                .where(
                    Booking.practice_id.in_(page_ids),
                    Booking.status != BookingStatus.CANCELLED.value,
                )
                .group_by(Booking.practice_id)
            )
        ).all()
        booked_map = {pid: count for pid, count in booked_rows}

    items = [
        AdminPracticeListItem(
            id=practice.id,
            title=practice.title,
            direction=practice.direction,
            master_name=_master_name(profile, user),
            master_verified=_master_verified(profile),
            scheduled_at=practice.scheduled_at,
            duration_minutes=practice.duration_minutes,
            booked=booked_map.get(practice.id, 0),
            capacity=practice.max_participants,
            status=_temporal_status(practice.scheduled_at, now),
        )
        for practice, profile, user in rows
    ]

    return PaginatedAdminPracticesResponse(
        items=items, total=total, limit=limit, offset=offset,
    )


async def get_admin_practice_detail(
    practice_id: UUID,
    session: AsyncSession,
) -> AdminPracticeDetailResponse:
    """Practice detail + attendance counts + non-cancelled roster.

    Raises:
        NotFoundError: when the practice does not exist or is soft-deleted.
    """
    now = datetime.now(UTC)

    row = (
        await session.execute(
            select(Practice, MasterProfile, User)
            .join(MasterProfile, Practice.master_id == MasterProfile.user_id)
            .join(User, MasterProfile.user_id == User.id)
            .where(Practice.id == practice_id)
        )
    ).one_or_none()

    if row is None:
        raise NotFoundError("Practice not found")
    practice, profile, user = row
    if practice.status == PracticeStatus.DELETED.value:
        raise NotFoundError("Practice not found")

    # booked (non-cancelled) + attended in a single query via FILTER.
    booked, attended = (
        await session.execute(
            select(
                func.count(Booking.id).filter(
                    Booking.status != BookingStatus.CANCELLED.value
                ),
                func.count(Booking.id).filter(
                    Booking.status == BookingStatus.ATTENDED.value
                ),
            ).where(Booking.practice_id == practice_id)
        )
    ).one()

    roster_rows = (
        await session.execute(
            select(
                Booking.user_id,
                Booking.status,
                User.first_name,
                User.last_name,
                User.avatar_url,
            )
            .join(User, Booking.user_id == User.id)
            .where(
                Booking.practice_id == practice_id,
                Booking.status != BookingStatus.CANCELLED.value,
            )
            .order_by(Booking.created_at)
        )
    ).all()

    roster = [
        AdminRosterEntry(
            user_id=user_id,
            name=display_name(first_name, last_name),
            avatar_url=avatar_url,
            status=booking_status,
        )
        for user_id, booking_status, first_name, last_name, avatar_url
        in roster_rows
    ]

    return AdminPracticeDetailResponse(
        id=practice.id,
        title=practice.title,
        direction=practice.direction,
        master_name=_master_name(profile, user),
        master_verified=_master_verified(profile),
        scheduled_at=practice.scheduled_at,
        duration_minutes=practice.duration_minutes,
        booked=booked,
        capacity=practice.max_participants,
        status=_temporal_status(practice.scheduled_at, now),
        attended=attended,
        roster=roster,
    )
