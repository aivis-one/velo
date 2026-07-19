# =============================================================================
# VELO Backend -- Practice Enrichment Service (W26 split from service.py)
# =============================================================================
#
# Series card meta (E3 batch 2) and attendance / check-in counts (E12 +
# aggregate) for a page of practices. Leaf area: no dependency on
# practices/service.py. Consumed by practices/service.py (get_practice_detail)
# and practices/listing_service.py (list_master_practices).
# =============================================================================

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bookings.models import Booking, BookingStatus
from app.modules.diary.models import Checkin, CheckType
from app.modules.practices.models import Practice, PracticeStatus

# -- Series card meta (E3 batch 2) -----------------------------------------
# Resolve recurrence_days / total_sessions / completed_sessions for a page of
# practices in two bounded queries (no N+1). Meta describes the SERIES (root +
# children), so every occurrence of one series reports the same trio; only
# series whose ROOT carries a recurrence spec get values, everything else stays
# None on the response.

# Tuple shape returned per practice: (recurrence_days, total, completed).
_SeriesMeta = tuple[list[int] | None, int | None, int | None]


def _recurrence_days_from_spec(spec: dict) -> list[int]:
    """Card weekday list for a recurrence spec (ISO 1=Mon..7=Sun).

    daily is surfaced as the full week [1..7] (the card renders "Ежедневно");
    weekly/biweekly return the spec's selected days. The set/clamp keeps the
    output well-formed even if the stored spec is unusual.
    """
    if spec.get("period") == "daily":
        return [1, 2, 3, 4, 5, 6, 7]
    return sorted({d for d in (spec.get("days") or []) if 1 <= d <= 7})


def series_meta_kwargs(meta: _SeriesMeta | None) -> dict:
    """Unpack a series-meta tuple into practice_to_response kwargs.

    None (not a series-with-spec) -> empty dict, so the response keeps its None
    defaults for all three fields.
    """
    if meta is None:
        return {}
    recurrence_days, total_sessions, completed_sessions = meta
    return {
        "recurrence_days": recurrence_days,
        "total_sessions": total_sessions,
        "completed_sessions": completed_sessions,
    }


async def series_meta_for_practices(
    practices: list[Practice],
    session: AsyncSession,
) -> dict[UUID, _SeriesMeta]:
    """Map practice_id -> (recurrence_days, total, completed) for a page.

    Only practices belonging to a series whose ROOT carries a recurrence spec
    (data.recurrence) appear in the map; the caller renders the rest as all
    None. Two bounded queries regardless of page size:

      1. roots: id + data for the page's distinct root ids -> recurrence_days
         and which roots actually carry a spec.
      2. counts: occurrences grouped by root id (coalesce(parent_practice_id,
         id)), excluding cancelled -> total and completed (status=completed).
    """
    if not practices:
        return {}

    # root_id for each row: parent if a child, else its own id (it IS the root).
    # No query -- the rows are already in hand.
    root_id_of: dict[UUID, UUID] = {
        p.id: (p.parent_practice_id or p.id) for p in practices
    }
    root_ids = set(root_id_of.values())

    # -- Query 1: recurrence spec on each candidate root --
    root_rows = (
        await session.execute(
            select(Practice.id, Practice.data).where(Practice.id.in_(root_ids))
        )
    ).all()
    days_by_root: dict[UUID, list[int]] = {}
    for root_id, data in root_rows:
        spec = (data or {}).get("recurrence")
        if spec:
            days_by_root[root_id] = _recurrence_days_from_spec(spec)

    spec_root_ids = set(days_by_root)
    if not spec_root_ids:
        # No series-with-spec on this page -- skip the count query entirely.
        return {}

    # -- Query 2: occurrence counts per series (cancelled excluded) --
    root_expr = func.coalesce(Practice.parent_practice_id, Practice.id)
    count_rows = (
        await session.execute(
            select(
                root_expr.label("root"),
                func.count(Practice.id),
                func.count(Practice.id).filter(
                    Practice.status == PracticeStatus.COMPLETED.value,
                ),
            )
            .where(
                root_expr.in_(spec_root_ids),
                Practice.status != PracticeStatus.CANCELLED.value,
            )
            .group_by(root_expr)
        )
    ).all()
    counts_by_root: dict[UUID, tuple[int, int]] = {
        root_id: (total, completed)
        for root_id, total, completed in count_rows
    }

    # -- Assemble per-practice meta (same trio for every occurrence) --
    meta: dict[UUID, _SeriesMeta] = {}
    for p in practices:
        root_id = root_id_of[p.id]
        if root_id not in spec_root_ids:
            continue
        total, completed = counts_by_root.get(root_id, (0, 0))
        meta[p.id] = (days_by_root[root_id], total, completed)
    return meta


# -- Attendance / check-in counts (E12 + aggregate) ------------------------
# Resolve checkin_count / attended / no_show for a page of practices in two
# bounded queries (no N+1), grouped by practice_id -- the same shape as the
# series-meta helper above. These are OWNER-facing figures: the caller wires
# them into the master's own list + the owner's detail only; the public feed
# and a non-owner's detail leave all three None (no_show is sensitive).

# Tuple shape returned per practice: (checkin_count, attended, no_show).
_AttendanceCounts = tuple[int, int, int]


def attendance_counts_kwargs(counts: _AttendanceCounts | None) -> dict:
    """Unpack an attendance-counts tuple into practice_to_response kwargs.

    None (the caller did not resolve counts for this practice -- e.g. the
    requester is not the owner) -> empty dict, so the response keeps its None
    defaults for all three fields.
    """
    if counts is None:
        return {}
    checkin_count, attended, no_show = counts
    return {
        "checkin_count": checkin_count,
        "attended": attended,
        "no_show": no_show,
    }


async def attendance_counts_for_practices(
    practices: list[Practice],
    session: AsyncSession,
) -> dict[UUID, _AttendanceCounts]:
    """Map practice_id -> (checkin_count, attended, no_show) for a page.

    checkin_count counts DISTINCT users with a PRE check-in for the practice
    (POST is a future socket and is excluded, matching the card badge and the
    attendance view). attended / no_show are booking counts in the ATTENDED /
    NO_SHOW statuses. Two bounded queries regardless of page size -- one over
    checkins, one over bookings, both grouped by practice_id. Every practice
    on the page gets a tuple (missing rows default to 0), so the owner always
    sees concrete numbers rather than None.
    """
    if not practices:
        return {}

    practice_ids = [p.id for p in practices]

    # -- Query 1: distinct PRE check-in users per practice --
    checkin_rows = (
        await session.execute(
            select(
                Checkin.practice_id,
                func.count(func.distinct(Checkin.user_id)),
            )
            .where(
                Checkin.practice_id.in_(practice_ids),
                Checkin.check_type == CheckType.PRE.value,
            )
            .group_by(Checkin.practice_id)
        )
    ).all()
    checkin_by_practice: dict[UUID, int] = {
        practice_id: count for practice_id, count in checkin_rows
    }

    # -- Query 2: attended / no_show booking counts per practice --
    booking_rows = (
        await session.execute(
            select(
                Booking.practice_id,
                func.count(Booking.id).filter(
                    Booking.status == BookingStatus.ATTENDED.value,
                ),
                func.count(Booking.id).filter(
                    Booking.status == BookingStatus.NO_SHOW.value,
                ),
            )
            .where(Booking.practice_id.in_(practice_ids))
            .group_by(Booking.practice_id)
        )
    ).all()
    booking_by_practice: dict[UUID, tuple[int, int]] = {
        practice_id: (attended, no_show)
        for practice_id, attended, no_show in booking_rows
    }

    # -- Assemble per-practice counts (missing rows default to 0) --
    counts: dict[UUID, _AttendanceCounts] = {}
    for practice_id in practice_ids:
        checkin_count = checkin_by_practice.get(practice_id, 0)
        attended, no_show = booking_by_practice.get(practice_id, (0, 0))
        counts[practice_id] = (checkin_count, attended, no_show)
    return counts
