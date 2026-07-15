# =============================================================================
# VELO Backend -- Practice Service (Phase 4.2 + 4.3/4.4, updated Phase 6.5,
#                                   updated Frontend F3 prep, + Calendar taxonomy)
# =============================================================================
#
# Business logic for practice CRUD (master-facing) and public listing.
#
# MASTER_NAME / MASTER_METHODS (Frontend F3 prep, DS-sprint):
#   practice_to_response() builds PracticeResponse with master_name and
#   master_methods. master_name is the full "First Last" name, built by
#   _master_full_name() from User.first_name + User.last_name in every JOIN /
#   mutation path (MVP rule: Telegram name, surname appended only if present).
#   master_methods come from MasterProfile.data via OUTER JOIN; get_practice()
#   outer-joins MasterProfile to return methods. If MasterProfile is missing,
#   master_methods defaults to [].
#   List functions pass master_methods=[] (methods not shown in list cards).
#
# CALENDAR TAXONOMY (Calendar iteration):
#   direction / style / difficulty are catalog facets stored in the
#   Practice.data JSONB sandbox under data.taxonomy (schema-on-read). They
#   are NOT columns:
#     - create_practice() writes them into data.taxonomy via set_jsonb().
#     - update_practice() handles them in a SEPARATE JSONB branch -- they are
#       pulled out of update_data BEFORE the setattr() loop, otherwise
#       setattr(practice, "direction", ...) would create a dead Python
#       attribute that never reaches the DB (same trap as onboarding_completed
#       in users/service.py).
#     - practice_to_response() extracts them back out for the API response.
#   JSONB SAFETY: always deepcopy + set_jsonb("data", ...). Never mutate
#   practice.data in place (SQLAlchemy would miss the change).
#
# OWNERSHIP:
#   All mutating operations (update, delete, cancel) verify master_id == user.id.
#   Non-owners receive 404 (P-08: do not reveal resource existence).
#   get_practice() applies visibility rules: draft/deleted only for owner.
#
# STATE MACHINE:
#   draft          -> scheduled, deleted   (via PATCH)
#   scheduled      -> live                  (auto, by schedule -- NOT via PATCH)
#   scheduled/live -> completed             (auto, by schedule -- NOT via PATCH)
#   completed      -> (terminal)
#   cancelled      -> (terminal)
#   deleted        -> (terminal)
#
# IMPORTANT (Phase 6.5):
#   scheduled -> cancelled and live -> cancelled are NOT allowed via PATCH.
#   The ONLY path to cancelled is through cancel_practice() which handles
#   refunds for all active bookings.
#
# IMPORTANT (Batch 1 -- lifecycle automation):
#   scheduled -> live and live -> completed are NO LONGER allowed via PATCH
#   either. Both are performed by the background lifecycle worker
#   (bookings/autofinalize.py) as the system, driven by the clock:
#     start:  scheduled -> live      once scheduled_at passes;
#     finish: scheduled/live -> completed once scheduled_at + duration passes
#             (auto_finalize_practice runs the full settlement core).
#   So PATCH only ever drives draft -> scheduled (publish) and draft -> deleted.
#
# PRICING (Phase 4.3/4.4):
#   is_free=True  -> price_cents forced to 0 (service overrides any value)
#   is_free=False -> price_cents must be > 0 (service raises 400)
#
# CONCURRENCY:
#   update_practice(), delete_practice(), and cancel_practice() use
#   with_for_update() (P-12) to prevent lost updates on status transitions.
#
# DELETE vs CANCEL:
#   DELETE sets status=deleted (only from draft).
#   CANCEL sets status=cancelled + refunds all bookings (Phase 6.5).
#
# SESSION RULES:
#   No session.commit() here (P-01). Router handles flush + refresh.
# =============================================================================

import copy
from datetime import UTC, date, datetime, timedelta
from typing import Literal
from uuid import UUID
from zoneinfo import ZoneInfo

import structlog
from sqlalchemy import and_, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.audit import record_audit
from app.core.config import settings
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
)
from app.modules.bookings.models import Booking, BookingStatus
# Checkin / CheckType power the E12 attendance counts below. Importing the
# public diary models here is cycle-free (diary.models imports no practices
# service), and mirrors masters/reviews_service importing diary.models.
from app.modules.diary.models import Checkin, CheckType
from app.modules.payments.refund import refund_all_bookings_for_practice
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.practices.schemas import (
    CreatePracticeRequest,
    PaginatedPracticesResponse,
    PracticeResponse,
    UpdatePracticeRequest,
)
from app.modules.practices.taxonomy_models import TaxonomyDirection, TaxonomyStyle
from app.modules.masters.models import MasterProfile
from app.modules.users.models import User

logger = structlog.get_logger()

# Statuses visible to any authenticated user.
_PUBLIC_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
    PracticeStatus.COMPLETED.value,
    PracticeStatus.CANCELLED.value,
}

# Statuses shown in public feed (4.3).
_FEED_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}

# Valid state transitions via PATCH. Terminal states (and states whose only
# remaining transitions are automated) have no outgoing edges here.
# Phase 6.5: cancelled is removed -- the ONLY way to reach cancelled is via
# cancel_practice() which handles refunds, preventing an accidental PATCH
# status=cancelled that would skip refund logic.
# Batch 1: scheduled -> live and live -> completed are removed too -- both are
# driven by the clock by the lifecycle worker (bookings/autofinalize.py:
# auto_start_practice / auto_finalize_practice) as the system, not by PATCH.
# So the ONLY PATCH-driven transitions left are draft -> scheduled (publish)
# and draft -> deleted.
_VALID_TRANSITIONS: dict[str, set[str]] = {
    PracticeStatus.DRAFT.value: {
        PracticeStatus.SCHEDULED.value,
        PracticeStatus.DELETED.value,
    },
}

# Statuses from which cancel_practice() is allowed.
_CANCELLABLE_PRACTICE_STATUSES = {
    PracticeStatus.SCHEDULED.value,
    PracticeStatus.LIVE.value,
}

# NOT NULL columns that cannot be set to None via PATCH (P-02).
_NOT_NULL_FIELDS = {
    "title",
    "scheduled_at",
    "duration_minutes",
    "timezone",
    "is_free",
    "price_cents",
    "currency",
}

# Booking statuses that count as "active" for the price-change guard.
_ACTIVE_BOOKING_STATUSES = {
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
}

# Booking statuses that mark a practice as "booked" for the requesting user
# in feed/detail responses (is_booked). Includes ATTENDED so a practice the
# user already attended still shows as theirs. Cancelled/no_show excluded.
_BOOKED_STATUSES = {
    BookingStatus.PENDING.value,
    BookingStatus.CONFIRMED.value,
    BookingStatus.ATTENDED.value,
}

# Booking statuses that grant a user access to the practice's zoom_link
# (M-3 access gate). STRICTER than _BOOKED_STATUSES above: a PENDING booking
# does NOT unlock the link -- only CONFIRMED or ATTENDED does. Used by
# get_practice_detail here and imported by GET /bookings/me to gate zoom_link;
# every other response leaves it None (see the PracticeResponse / PracticeSummary
# zoom_link validators).
ZOOM_VISIBLE_BOOKING_STATUSES = {
    BookingStatus.CONFIRMED.value,
    BookingStatus.ATTENDED.value,
}

# Calendar taxonomy facets -- stored in Practice.data.taxonomy (JSONB),
# NOT as columns. Handled separately from setattr-based column updates.
_TAXONOMY_FIELDS = ("direction", "style", "difficulty")


# ===================================================================
# Helpers
# ===================================================================


def _enforce_pricing(
    is_free: bool,
    price_cents: int,
) -> int:
    """Enforce pricing invariant.

    is_free=True  -> return 0 (override any client value).
    is_free=False -> price_cents must be > 0, else raise 400.
    """
    if is_free:
        return 0
    if price_cents <= 0:
        raise BadRequestError(
            "price_cents must be > 0 for paid practices"
        )
    return price_cents


def _build_taxonomy(
    direction: str,
    difficulty: str,
    style: str | None,
) -> dict:
    """Build the data.taxonomy dict for a practice.

    Calendar facets: direction + difficulty are required on create;
    style is optional (None when not provided).
    """
    return {
        "direction": direction,
        "difficulty": difficulty,
        "style": style,
    }


# ===================================================================
# Taxonomy union validation (T2, 2026-07-15)
# ===================================================================
#
# direction / style are valid if they're in config OR the active DB catalog
# (practice_directions / practice_styles) -- UNION, never replace (operator
# decision): the catalog was seeded 1:1 from this same config, so today both
# give identical results, but union can never reject a config-valid value
# while a replace could. Each VALUE is checked against config FIRST,
# unconditionally -- a config hit returns valid without touching the DB at
# all, so a broken/empty catalog can never affect a config-valid create/
# update. Only on a config MISS is the catalog queried, and that query is
# wrapped so ANY read error degrades to "not found" rather than propagating
# -- the only thing an outage can cost is a catalog-only value. Only ACTIVE
# catalog rows count, matching GET /api/v1/taxonomy's own contract.
# difficulty has no catalog table and is validated in schemas.py, unchanged.


async def _direction_in_catalog(
    direction: str,
    session: AsyncSession,
) -> bool:
    """Active-catalog fallback for direction membership (config already missed)."""
    try:
        stmt = select(TaxonomyDirection.id).where(
            TaxonomyDirection.value == direction,
            TaxonomyDirection.is_active.is_(True),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none() is not None
    except Exception:
        logger.warning(
            "taxonomy_catalog_direction_read_failed", direction=direction,
        )
        return False


async def _catalog_styles_for_direction(
    direction: str,
    session: AsyncSession,
) -> set[str]:
    """Active catalog style values under one active direction."""
    try:
        stmt = (
            select(TaxonomyStyle.value)
            .join(
                TaxonomyDirection,
                TaxonomyStyle.direction_id == TaxonomyDirection.id,
            )
            .where(
                TaxonomyDirection.value == direction,
                TaxonomyDirection.is_active.is_(True),
                TaxonomyStyle.is_active.is_(True),
            )
        )
        result = await session.execute(stmt)
        return set(result.scalars().all())
    except Exception:
        logger.warning(
            "taxonomy_catalog_style_read_failed", direction=direction,
        )
        return set()


async def _validate_style_choice(
    direction: str | None,
    style: str | None,
    session: AsyncSession,
) -> None:
    """Validate style membership for an ALREADY-valid direction (union).

    Does not re-check direction membership -- callers use this either for a
    direction just validated by _validate_taxonomy(), or for a practice's
    STORED direction (accepted back when the practice was created/last set).
    """
    if style is None:
        return
    config_styles = settings.practice_allowed_styles_by_direction.get(
        direction, (),
    )
    if style in config_styles:
        return
    catalog_styles = await _catalog_styles_for_direction(direction, session)
    if style in catalog_styles:
        return
    allowed = sorted(set(config_styles) | catalog_styles)
    if allowed:
        raise BadRequestError(
            f"style for direction '{direction}' must be one of {allowed}, "
            f"got '{style}'"
        )
    raise BadRequestError(
        f"direction '{direction}' does not admit a style; got '{style}'"
    )


async def _validate_taxonomy(
    direction: str,
    style: str | None,
    session: AsyncSession,
) -> None:
    """Validate a direction + optional style pair against the union."""
    if direction not in settings.practice_allowed_directions:
        if not await _direction_in_catalog(direction, session):
            raise BadRequestError(
                f"direction must be one of "
                f"{settings.practice_allowed_directions}, got '{direction}'"
            )
    await _validate_style_choice(direction, style, session)


async def _has_active_bookings(
    practice_id: UUID,
    session: AsyncSession,
) -> bool:
    """Check if a practice has any active (pending/confirmed) bookings.

    CQ-05: used to prevent price changes on practices that already
    have participants who paid the original price.
    """
    stmt = (
        select(func.count(Booking.id))
        .where(
            Booking.practice_id == practice_id,
            Booking.status.in_(_ACTIVE_BOOKING_STATUSES),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one() > 0


def _master_full_name(
    first_name: str | None,
    last_name: str | None,
) -> str:
    """Build the master's display name as "First Last".

    MVP rule (mirrors the frontend masterDisplayName helper): always use the
    Telegram first_name + last_name, ignoring MasterProfile.display_name.
    Telegram guarantees first_name but last_name is optional, so the surname
    is appended only when present; if both are empty we fall back to "Мастер".
    Empty parts are filtered out so there is no trailing space or "None".
    """
    parts = [p for p in (first_name, last_name) if p]
    return " ".join(parts) if parts else "Мастер"


def practice_to_response(
    practice: Practice,
    master_name: str | None = None,
    master_methods: list[str] | None = None,
    *,
    master_avatar_url: str | None = None,
    is_booked: bool = False,
    is_paid: bool = False,
    recurrence_days: list[int] | None = None,
    total_sessions: int | None = None,
    completed_sessions: int | None = None,
    checkin_count: int | None = None,
    attended: int | None = None,
    no_show: int | None = None,
    zoom_link_visible: bool = False,
) -> PracticeResponse:
    """Build PracticeResponse from ORM object with master_name and master_methods.

    master_name:       full "First Last" built via _master_full_name() from the
                       User row in the JOIN (or the mutation's User object).
    master_methods:    MasterProfile.data.profile.methods from outer join in
                       get_practice(). List endpoints pass [] (not shown on cards).
    master_avatar_url: User.avatar_url from JOIN in get_practice() (detail only).
                       List endpoints leave it None -- avatars are not shown on
                       feed cards (V3: feed is untouched).

    Calendar taxonomy (direction / style / difficulty) is extracted from
    practice.data.taxonomy. Missing keys (e.g. practices created before the
    Calendar iteration, whose data sandbox is empty) resolve to None.
    """
    resp = PracticeResponse.model_validate(practice)
    resp.master_name = master_name
    resp.master_avatar_url = master_avatar_url
    resp.master_methods = master_methods or []

    taxonomy = (practice.data or {}).get("taxonomy", {})
    resp.direction = taxonomy.get("direction")
    resp.style = taxonomy.get("style")
    resp.difficulty = taxonomy.get("difficulty")

    # Per-user state for the requesting user (default False -- see schema).
    resp.is_booked = is_booked
    resp.is_paid = is_paid

    # Series card meta (E3 batch 2). None unless the caller resolved it for a
    # series-with-spec; the public feed leaves all three None.
    resp.recurrence_days = recurrence_days
    resp.total_sessions = total_sessions
    resp.completed_sessions = completed_sessions

    # Attendance / check-in counts (E12 + aggregate). None unless the caller
    # resolved them for an owner-facing view (master list / owner detail); the
    # public feed and a non-owner's detail leave all three None.
    resp.checkin_count = checkin_count
    resp.attended = attended
    resp.no_show = no_show

    # zoom_link (M-3 access gate). model_validate auto-populated the real ORM
    # link; expose it ONLY when the caller authorized it (the practice owner,
    # or a requester with a confirmed/attended booking -- see
    # get_practice_detail), otherwise null it explicitly. This gate lives here,
    # not in a schema model_validator: FastAPI re-validates the response and
    # would re-run such a validator, wiping the value set here.
    resp.zoom_link = practice.zoom_link if zoom_link_visible else None

    return resp


async def _user_flags_for_practices(
    user_id: UUID,
    practice_ids: list[UUID],
    session: AsyncSession,
) -> dict[UUID, tuple[bool, bool]]:
    """Map practice_id -> (is_booked, is_paid) for the given user.

    One query over the user's bookings restricted to practice_ids on the
    current page (uses ix_bookings_user_id), joined to Practice for the price.

    is_booked -- the user has a booking in _BOOKED_STATUSES for the practice.
    is_paid   -- is_booked AND the practice is paid (price_cents > 0).
                 Definition note: a Booking always carries a purchase_id (even
                 free practices create a zero-amount Purchase), so purchase
                 presence is NOT a paid signal. "Paid" here means the user
                 holds a booking on a priced practice -- this drives the
                 "Оплачено" vs "Бесплатно" badge in the Calendar.

    Practices with no booking for this user are simply absent from the
    map -> caller treats them as (False, False).
    """
    if not practice_ids:
        return {}

    stmt = select(
        Booking.practice_id,
        Practice.price_cents,
    ).join(
        Practice, Booking.practice_id == Practice.id,
    ).where(
        Booking.user_id == user_id,
        Booking.practice_id.in_(practice_ids),
        Booking.status.in_(_BOOKED_STATUSES),
    )
    result = await session.execute(stmt)

    flags: dict[UUID, tuple[bool, bool]] = {}
    for practice_id, price_cents in result.all():
        flags[practice_id] = (True, price_cents > 0)
    return flags


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


def _series_meta_kwargs(meta: _SeriesMeta | None) -> dict:
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


async def _series_meta_for_practices(
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


def _attendance_counts_kwargs(counts: _AttendanceCounts | None) -> dict:
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


async def _attendance_counts_for_practices(
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


# ===================================================================
# CRUD
# ===================================================================


async def create_practice(
    user: User,
    body: CreatePracticeRequest,
    session: AsyncSession,
) -> Practice:
    """Create a new practice in draft status.

    Calendar taxonomy (direction / difficulty / style) is written into the
    data.taxonomy JSONB sandbox via set_jsonb() -- direction and difficulty
    are required by the schema, style is optional. direction/style membership
    (T2, 2026-07-15) is validated here against the config+catalog union --
    difficulty stays schema-validated (config only, no catalog table).
    """
    await _validate_taxonomy(body.direction, body.style, session)
    price_cents = _enforce_pricing(body.is_free, body.price_cents)

    practice = Practice(
        master_id=user.id,
        practice_type=body.practice_type,
        title=body.title,
        description=body.description,
        what_to_prepare=body.what_to_prepare,
        contraindications=body.contraindications,
        scheduled_at=body.scheduled_at,
        duration_minutes=body.duration_minutes,
        timezone=body.timezone,
        max_participants=body.max_participants,
        zoom_link=body.zoom_link,
        parent_practice_id=body.parent_practice_id,
        is_free=body.is_free,
        price_cents=price_cents,
        currency=body.currency,
    )

    # Calendar taxonomy -> data.taxonomy (JSONB sandbox).
    # set_jsonb() flags the column modified so SQLAlchemy emits the write;
    # a fresh dict is safe to assign on a not-yet-persisted object.
    data: dict = {
        "taxonomy": _build_taxonomy(
            body.direction, body.difficulty, body.style,
        ),
    }
    # E3: persist the recurrence spec on the series root (schema-on-read, the
    # same JSONB sandbox as taxonomy). Stored as plain JSON (dates -> ISO
    # strings via mode="json") so it round-trips through JSONB; generation
    # parses it back on publication. A series practice without a spec omits the
    # key entirely, and generation no-ops for it.
    if body.recurrence is not None:
        data["recurrence"] = body.recurrence.model_dump(mode="json")
    practice.set_jsonb("data", data)

    session.add(practice)

    logger.info(
        "practice_created",
        master_id=str(user.id),
        practice_type=body.practice_type,
        title=body.title,
        is_free=body.is_free,
        price_cents=price_cents,
        direction=body.direction,
        difficulty=body.difficulty,
    )

    return practice


# ===================================================================
# Series occurrence generation (E3)
# ===================================================================


def _series_occurrence_starts(
    root: Practice,
    spec: dict,
    cap: int,
) -> list[datetime]:
    """Compute UTC start datetimes for a series root's CHILD occurrences.

    The root itself is occurrence #1 (its scheduled_at); this returns the
    subsequent occurrences (#2..N) as tz-aware UTC datetimes.

    DST-safe: each occurrence is built at the root's LOCAL wall-clock time (same
    hour/minute as the root) in the root's IANA timezone, then converted to UTC
    per-occurrence -- so 19:00 local stays 19:00 local across a DST transition
    rather than drifting by an hour.

    period:
      daily    -- every calendar day after the root (days are ignored).
      weekly   -- on the spec's ISO weekdays (1=Mon..7=Sun), every week.
      biweekly -- on the spec's ISO weekdays, every OTHER week (parity measured
                  from the root's week, Monday-anchored).

    end / cap (root included in the total):
      after_count -- total occurrences is min(count, cap).
      until_date  -- occurrences through until_date (inclusive, local date),
                     truncated to the cap.
      never       -- exactly cap occurrences.
    The TOTAL (root + children) never exceeds `cap`, so at most cap-1 children
    are returned.
    """
    period = spec["period"]
    end = spec["end"]
    days = set(spec.get("days") or ())
    count = spec.get("count")
    until_raw = spec.get("until_date")
    until_date = date.fromisoformat(until_raw) if until_raw else None

    # Total occurrences (root included) we are allowed to emit.
    if end == "after_count" and count is not None:
        total_target = min(int(count), cap)
    else:  # never / until_date
        total_target = cap
    max_children = max(0, total_target - 1)
    if max_children == 0:
        return []

    tz = ZoneInfo(root.timezone)
    anchor_local = root.scheduled_at.astimezone(tz)
    anchor_date = anchor_local.date()
    anchor_monday = anchor_date - timedelta(days=anchor_date.weekday())

    # Absolute safety ceiling on the forward day-walk so a pathological spec can
    # never loop unbounded. cap=40 with biweekly single-day needs ~78 weeks;
    # five years of days is comfortably beyond any reachable case.
    safety_days = 366 * 5

    starts: list[datetime] = []
    cursor = anchor_date
    for _ in range(safety_days):
        cursor += timedelta(days=1)
        if until_date is not None and cursor > until_date:
            break

        if period == "daily":
            qualifies = True
        else:
            iso_weekday = cursor.isoweekday()  # 1=Mon .. 7=Sun
            if iso_weekday not in days:
                qualifies = False
            elif period == "weekly":
                qualifies = True
            else:  # biweekly: even week offset from the root's week
                cursor_monday = cursor - timedelta(days=cursor.weekday())
                week_offset = (cursor_monday - anchor_monday).days // 7
                qualifies = week_offset % 2 == 0

        if not qualifies:
            continue

        # Build the local wall-clock instant -- preserving the root's FULL
        # time-of-day (sub-minute included) so occurrences sit exactly one
        # recurrence interval apart -- then convert to UTC (DST-safe).
        local_dt = datetime(
            cursor.year, cursor.month, cursor.day,
            anchor_local.hour, anchor_local.minute,
            anchor_local.second, anchor_local.microsecond,
            tzinfo=tz,
        )
        starts.append(local_dt.astimezone(UTC))
        if len(starts) >= max_children:
            break

    return starts


def _build_child_occurrence(
    root: Practice,
    start_utc: datetime,
) -> Practice:
    """Build one child Practice for a series, copying the root's fields.

    The child links back via parent_practice_id=root.id, starts already
    SCHEDULED (it is created at publication time), and carries only the root's
    taxonomy in its data sandbox -- NOT the recurrence spec (that lives on the
    root alone) and NOT any seed marker. current_participants resets to 0 (the
    ORM default).
    """
    child = Practice(
        master_id=root.master_id,
        practice_type=PracticeType.SERIES.value,
        status=PracticeStatus.SCHEDULED.value,
        title=root.title,
        description=root.description,
        what_to_prepare=root.what_to_prepare,
        contraindications=root.contraindications,
        scheduled_at=start_utc,
        duration_minutes=root.duration_minutes,
        timezone=root.timezone,
        max_participants=root.max_participants,
        zoom_link=root.zoom_link,
        parent_practice_id=root.id,
        is_free=root.is_free,
        price_cents=root.price_cents,
        currency=root.currency,
    )
    taxonomy = (root.data or {}).get("taxonomy")
    if taxonomy is not None:
        child.set_jsonb("data", {"taxonomy": copy.deepcopy(taxonomy)})
    return child


async def _generate_series_occurrences(
    root: Practice,
    session: AsyncSession,
) -> int:
    """Generate child occurrences for a published series root.

    No-op (returns 0) unless the root carries a recurrence spec in
    data.recurrence. Idempotent: if children already exist for this root they
    are left untouched (defends against any re-entry, though draft -> scheduled
    is a one-way transition). Children are added to the session; the router's
    flush + refresh of the root persists them.

    Returns the number of children created.
    """
    spec = (root.data or {}).get("recurrence")
    if not spec:
        return 0

    # Idempotency guard: never double-generate for the same root.
    existing = (
        await session.execute(
            select(func.count(Practice.id)).where(
                Practice.parent_practice_id == root.id,
            )
        )
    ).scalar_one()
    if existing > 0:
        logger.info(
            "series_generation_skipped_existing",
            root_practice_id=str(root.id),
            existing_children=existing,
        )
        return 0

    cap = settings.practice_series_max_occurrences
    starts = _series_occurrence_starts(root, spec, cap)

    # W-1: an until_date earlier than the first recurring occurrence produces no
    # children, which would silently publish a "series" of just the root. Reject
    # it so the master gets clear feedback rather than a degenerate series. Only
    # until_date can be degenerate this way: never always fills to the cap, and
    # after_count with count=1 is an explicit single-occurrence choice.
    if not starts and spec.get("end") == "until_date":
        raise BadRequestError(
            "recurrence until_date is too early -- it yields no sessions "
            "after the first occurrence; choose a later date"
        )

    for start_utc in starts:
        session.add(_build_child_occurrence(root, start_utc))

    logger.info(
        "series_occurrences_generated",
        root_practice_id=str(root.id),
        master_id=str(root.master_id),
        period=spec.get("period"),
        end=spec.get("end"),
        children_created=len(starts),
    )

    return len(starts)


async def get_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> tuple[Practice, str | None, str | None, list[str]]:
    """Get a practice by id with visibility rules.

    Returns (Practice, master_name, master_avatar_url, master_methods) tuple.

    Uses OUTER JOIN to MasterProfile so that a practice is never hidden
    just because its master profile was deleted (review #3 finding).
    master_methods extracted from MasterProfile.data.profile.methods;
    defaults to [] when profile row is missing.
    master_avatar_url is User.avatar_url (synced from Telegram on login);
    None when the master has no Telegram photo.

    Draft/deleted practices are visible only to the owner master.
    All other statuses are visible to any authenticated user.
    """
    stmt = (
        select(
            Practice,
            User.first_name,
            User.last_name,
            User.avatar_url,
            MasterProfile.data,
        )
        .join(User, Practice.master_id == User.id)
        .outerjoin(MasterProfile, Practice.master_id == MasterProfile.user_id)
        .where(Practice.id == practice_id)
    )
    result = await session.execute(stmt)
    row = result.one_or_none()

    if not row:
        raise NotFoundError("Practice not found")

    practice, first_name, last_name, master_avatar_url, profile_data = row
    master_name = _master_full_name(first_name, last_name)

    # Draft/deleted visible only to owner (P-08: 404 not 403).
    if (
        practice.status not in _PUBLIC_STATUSES
        and practice.master_id != user.id
    ):
        raise NotFoundError("Practice not found")

    master_methods: list[str] = (
        profile_data.get("profile", {}).get("methods", [])
        if profile_data
        else []
    )

    return practice, master_name, master_avatar_url, master_methods


async def get_practice_detail(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> PracticeResponse:
    """Get a single practice as a ready PracticeResponse for the detail screen.

    Public service entry point for GET /practices/{id}. Encapsulates the
    visibility rules (get_practice), the per-user is_booked/is_paid flags,
    and response assembly so the router stays thin and does not reach into
    private helpers (C-1: no cross-layer import of _user_flags_for_practices).
    """
    practice, master_name, master_avatar_url, master_methods = (
        await get_practice(practice_id, user, session)
    )
    flags = await _user_flags_for_practices(user.id, [practice.id], session)
    is_booked, is_paid = flags.get(practice.id, (False, False))
    series_meta = await _series_meta_for_practices([practice], session)
    # E12 + aggregate: OWNER-ONLY on this shared detail endpoint. no_show is
    # sensitive, so a non-owner viewer never sees these -- skip the query and
    # leave all three None. (Series-meta above is innocuous and shown to all.)
    is_owner = practice.master_id == user.id
    attendance = (
        await _attendance_counts_for_practices([practice], session)
        if is_owner
        else {}
    )
    # zoom_link (M-3): the owner always sees it; a non-owner only with a
    # CONFIRMED / ATTENDED booking on this practice (a PENDING booking is not
    # enough). is_booked (pending/confirmed/attended) being False means no
    # booking at all -> skip the narrowing query. Everyone else -> None.
    zoom_visible = is_owner
    if not zoom_visible and is_booked:
        zoom_visible = (
            await session.execute(
                select(Booking.id)
                .where(
                    Booking.practice_id == practice.id,
                    Booking.user_id == user.id,
                    Booking.status.in_(ZOOM_VISIBLE_BOOKING_STATUSES),
                )
                .limit(1)
            )
        ).first() is not None
    return practice_to_response(
        practice,
        master_name,
        master_methods,
        master_avatar_url=master_avatar_url,
        is_booked=is_booked,
        is_paid=is_paid,
        zoom_link_visible=zoom_visible,
        **_series_meta_kwargs(series_meta.get(practice.id)),
        **_attendance_counts_kwargs(attendance.get(practice.id)),
    )


async def update_practice(
    practice_id: UUID,
    user: User,
    body: UpdatePracticeRequest,
    session: AsyncSession,
) -> Practice:
    """Update a practice. Only the owner master can edit.

    Uses FOR UPDATE to prevent lost updates on concurrent
    status transitions (P-12).

    Raises NotFoundError if not found or not owner (P-08).
    Raises BadRequestError if practice is deleted/terminal,
        if NOT NULL field set to null (P-02),
        if status transition is invalid,
        if pricing invariant is violated,
        or if price is changed with active bookings (CQ-05).

    Calendar taxonomy (direction / difficulty / style) is handled in a
    separate JSONB branch (data.taxonomy) -- see _TAXONOMY_FIELDS. These keys
    are pulled out of update_data BEFORE the column setattr loop so that
    setattr() never targets a non-existent column.
    """
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    # R-01 fix: 404 not 403 for non-owner (P-08).
    # Consistent with cancel_practice(), bookings, waitlist, reports.
    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    if practice.status == PracticeStatus.DELETED.value:
        raise BadRequestError("Cannot edit a deleted practice")

    update_data = body.model_dump(exclude_unset=True)

    # Separate Calendar taxonomy (JSONB) from plain column fields.
    # These are NOT columns: applying them via setattr would create dead
    # Python attributes that never persist (same trap as onboarding_completed
    # in users/service.py). They are merged into data.taxonomy below.
    taxonomy_updates = {
        field: update_data.pop(field)
        for field in _TAXONOMY_FIELDS
        if field in update_data
    }

    # Guard NOT NULL fields against explicit null (P-02).
    for field in _NOT_NULL_FIELDS:
        if field in update_data and update_data[field] is None:
            raise BadRequestError(f"{field} cannot be null")

    # Validate status transition if status is being changed.
    if "status" in update_data:
        new_status = update_data["status"]
        allowed = _VALID_TRANSITIONS.get(practice.status, set())
        if new_status not in allowed:
            raise BadRequestError(
                f"Cannot transition from "
                f"{practice.status} to {new_status}"
            )

    # CQ-05: prevent price/is_free changes when active bookings exist.
    # Participants paid the original price; changing it mid-flight
    # creates a mismatch between Purchase.paid_cents and Practice.price_cents.
    pricing_changed = (
        "is_free" in update_data
        and update_data["is_free"] != practice.is_free
    ) or (
        "price_cents" in update_data
        and update_data["price_cents"] != practice.price_cents
    )
    if pricing_changed and await _has_active_bookings(
        practice.id, session,
    ):
        raise BadRequestError(
            "Cannot change price with active bookings"
        )

    # Enforce pricing invariant after applying updates.
    # Resolve final is_free and price_cents from mix of
    # existing values and incoming updates.
    final_is_free = update_data.get("is_free", practice.is_free)
    final_price = update_data.get(
        "price_cents", practice.price_cents,
    )
    if "is_free" in update_data or "price_cents" in update_data:
        final_price = _enforce_pricing(final_is_free, final_price)
        update_data["price_cents"] = final_price

    # Capture the pre-update scheduled_at so we can detect a reschedule and
    # record old -> new in the diary feed projection below. Read BEFORE the
    # setattr loop overwrites practice.scheduled_at.
    old_scheduled_at = practice.scheduled_at
    # E3: capture status before the loop applies the new one, so we can detect a
    # draft -> scheduled publication and materialize series occurrences below.
    old_status = practice.status

    # Apply only provided column fields.
    for field, value in update_data.items():
        setattr(practice, field, value)

    # Apply Calendar taxonomy updates into data.taxonomy (JSONB).
    # deepcopy + set_jsonb so SQLAlchemy detects the change. Only the keys
    # actually sent are overwritten; the rest of data.taxonomy is preserved.
    if taxonomy_updates:
        # T2 (2026-07-15): direction/style membership is no longer checked by
        # Pydantic (it can't reach the async catalog), so both are validated
        # here, against the config+catalog union.
        if "direction" in taxonomy_updates:
            new_direction = taxonomy_updates["direction"]
            # Style paired with this same request validates against the NEW
            # direction (None if style isn't part of this update -- a no-op).
            await _validate_taxonomy(
                new_direction, taxonomy_updates.get("style"), session,
            )
        elif "style" in taxonomy_updates:
            # W-1: style changed WITHOUT direction in the same request --
            # validate against the direction actually STORED on the practice
            # (a style valid for a DIFFERENT direction, e.g. "silence" -- a
            # meditation style -- on a stored yoga practice, must still be
            # rejected). A direction change alone, without a style in the same
            # request, does not re-check the stored style -- unchanged from
            # before T2.
            stored_taxonomy = (practice.data or {}).get("taxonomy", {})
            stored_direction = stored_taxonomy.get("direction")
            await _validate_style_choice(
                stored_direction, taxonomy_updates["style"], session,
            )

        data = copy.deepcopy(practice.data) if practice.data else {}
        taxonomy = data.get("taxonomy", {})
        taxonomy.update(taxonomy_updates)
        data["taxonomy"] = taxonomy
        practice.set_jsonb("data", data)

    logger.info(
        "practice_updated",
        practice_id=str(practice_id),
        master_id=str(user.id),
        fields=list(update_data.keys()),
        taxonomy_fields=list(taxonomy_updates.keys()),
    )

    # Diary feed: if the master moved the time, fan out a reschedule event to
    # every booked user. Only when scheduled_at actually changed (a PATCH that
    # touches other fields must not spam reschedule cards). Lazy import keeps
    # the dependency one-way (practices -> diary).
    new_scheduled_at = practice.scheduled_at
    if (
        "scheduled_at" in update_data
        and new_scheduled_at != old_scheduled_at
    ):
        from app.modules.diary.projections import (
            project_practice_rescheduled,
        )
        # Master name for the diary card: full "First Last" (MVP rule), same
        # as practice cards. Load the User directly -- get_master_display_name
        # is for notifications and would return the profile display_name.
        master_user = await session.get(User, practice.master_id)
        master_name = _master_full_name(
            master_user.first_name if master_user else None,
            master_user.last_name if master_user else None,
        )
        await project_practice_rescheduled(
            session,
            practice=practice,
            master_name=master_name,
            old_scheduled_at=old_scheduled_at,
            new_scheduled_at=new_scheduled_at,
            occurred_at=datetime.now(UTC),
        )

    # E3: materialize series occurrences when a series ROOT is published
    # (draft -> scheduled). Gated inside the helper on the recurrence spec's
    # presence, so a series practice without a spec (seed demo) is a no-op. Only
    # roots generate (parent_practice_id is None); generated children are
    # created already-scheduled and never re-enter this path.
    if (
        old_status == PracticeStatus.DRAFT.value
        and practice.status == PracticeStatus.SCHEDULED.value
        and practice.practice_type == PracticeType.SERIES.value
        and practice.parent_practice_id is None
    ):
        await _generate_series_occurrences(practice, session)

    return practice


async def delete_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> Practice:
    """Soft-delete a draft practice (set status=deleted).

    Only drafts can be deleted. Published practices must be cancelled
    through cancel_practice() (Phase 6.5) which handles refunds.

    Uses FOR UPDATE to prevent concurrent state changes (P-12).

    Raises NotFoundError if not found or not owner (P-08).
    Raises BadRequestError if not a draft.
    """
    stmt = (
        select(Practice)
        .where(Practice.id == practice_id)
        .with_for_update()
    )
    result = await session.execute(stmt)
    practice = result.scalar_one_or_none()

    if not practice:
        raise NotFoundError("Practice not found")

    # R-01 fix: 404 not 403 for non-owner (P-08).
    # Consistent with cancel_practice(), bookings, waitlist, reports.
    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    if practice.status != PracticeStatus.DRAFT.value:
        raise BadRequestError(
            "Only draft practices can be deleted. "
            "Use cancel for published practices."
        )

    practice.status = PracticeStatus.DELETED.value

    logger.info(
        "practice_deleted",
        practice_id=str(practice_id),
        master_id=str(user.id),
    )

    return practice


# ===================================================================
# Phase 6.5: Cancel practice (master cancels, refund all bookings)
# ===================================================================


async def _cancel_one(
    practice: Practice,
    user: User,
    session: AsyncSession,
    *,
    occurred_at: datetime | None = None,
) -> int:
    """Cancel a single, already-locked + already-validated practice occurrence.

    Runs the full refund flow for ONE occurrence: collect booked users, refund
    all active bookings (+ clear waitlist), flip status to cancelled, audit, and
    project the diary "cancelled" event. The CALLER must have locked the row
    (FOR UPDATE), verified ownership, and confirmed the status is cancellable --
    this core does not re-check. Returns the number of refunded bookings.

    occurred_at is the diary timestamp for the projected "cancelled" event. A
    scope cancellation spanning several occurrences passes ONE shared instant so
    every diary card shares it (W-3); a lone call defaults to now.
    """
    # Diary feed: collect the booked users BEFORE the refund flow runs --
    # refund_all_bookings_for_practice transitions bookings to cancelled, so
    # reading them afterwards would yield an empty set. Inline ORM query
    # (Booking/BookingStatus are already imported) -- we do not import the
    # private _booked_user_ids from diary.projections (P: no cross-module
    # private import, consistent with calendar C-1).
    affected_ids_stmt = (
        select(Booking.user_id)
        .where(
            Booking.practice_id == practice.id,
            Booking.status != BookingStatus.CANCELLED.value,
        )
        .distinct()
    )
    affected_user_ids = list(
        (await session.execute(affected_ids_stmt)).scalars().all()
    )

    # Refund all active bookings + clear waitlist.
    refunded_count = await refund_all_bookings_for_practice(
        practice=practice,
        session=session,
    )

    practice.status = PracticeStatus.CANCELLED.value

    # Audit.
    await record_audit(
        event="practice_cancelled_by_master",
        actor_id=user.id,
        actor_type="user",
        target_type="practice",
        target_id=practice.id,
        data={
            "refunded_bookings": refunded_count,
        },
        session=session,
    )

    logger.info(
        "practice_cancelled",
        practice_id=str(practice.id),
        master_id=str(user.id),
        refunded_bookings=refunded_count,
    )

    # Diary feed: fan out "master cancelled the practice" to the users who were
    # booked (collected above, before the refund). occurred_at is now. Master
    # name for the diary card: full "First Last" (MVP rule). Load the User
    # directly rather than get_master_display_name (notification helper).
    from app.modules.diary.projections import project_practice_cancelled
    master_user = await session.get(User, practice.master_id)
    master_name = _master_full_name(
        master_user.first_name if master_user else None,
        master_user.last_name if master_user else None,
    )
    await project_practice_cancelled(
        session,
        practice=practice,
        master_name=master_name,
        user_ids=affected_user_ids,
        occurred_at=(
            occurred_at if occurred_at is not None else datetime.now(UTC)
        ),
    )

    return refunded_count


async def cancel_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
    *,
    scope: str = "this",
) -> Practice:
    """Cancel a scheduled/live practice with full refund to all participants.

    Master-only. This is the ONLY path to Practice.status=cancelled (PATCH
    status=cancelled is intentionally blocked in _VALID_TRANSITIONS).

    scope:
      "this"            -- cancel only this occurrence (the historical default).
      "this_and_future" -- for a SERIES, also cancel every LATER occurrence of
                           the same series (scheduled_at >= this one's) that is
                           still cancellable. A non-series practice has no
                           siblings, so it behaves like "this". Past, completed,
                           or already-cancelled occurrences are never touched.

    Each affected occurrence is locked FOR UPDATE (P-12), refunded via the same
    double-entry flow, audited, and projected to the diary. Returns the primary
    practice (the one addressed by practice_id).

    Raises NotFoundError if not found or not owner (P-08: 404 not 403).
    Raises BadRequestError if the primary practice is not in a cancellable state.
    """
    # Lock + validate the primary occurrence.
    primary = (
        await session.execute(
            select(Practice)
            .where(Practice.id == practice_id)
            .with_for_update()
        )
    ).scalar_one_or_none()

    if not primary:
        raise NotFoundError("Practice not found")

    # P-08: 404 not 403 for non-owner.
    if primary.master_id != user.id:
        raise NotFoundError("Practice not found")

    if primary.status not in _CANCELLABLE_PRACTICE_STATUSES:
        raise BadRequestError(
            f"Cannot cancel practice in status "
            f"{primary.status}"
        )

    # W-3: one shared instant for every occurrence this action cancels, so the
    # diary cards line up rather than drifting by microseconds.
    cancel_ts = datetime.now(UTC)
    await _cancel_one(primary, user, session, occurred_at=cancel_ts)

    if scope == "this_and_future":
        # Series identity = the root id (parent if this is a child, else its own
        # id). Cancel later siblings of the SAME series that are still
        # cancellable; non-series practices have no siblings, so this is empty
        # and the call reduces to "this".
        root_id = primary.parent_practice_id or primary.id
        root_expr = func.coalesce(Practice.parent_practice_id, Practice.id)
        siblings = (
            (
                await session.execute(
                    select(Practice)
                    .where(
                        root_expr == root_id,
                        Practice.id != primary.id,
                        Practice.scheduled_at >= primary.scheduled_at,
                        Practice.status.in_(_CANCELLABLE_PRACTICE_STATUSES),
                    )
                    .order_by(Practice.scheduled_at)
                    .with_for_update()
                )
            ).scalars().all()
        )
        for sibling in siblings:
            await _cancel_one(sibling, user, session, occurred_at=cancel_ts)

    return primary


# ===================================================================
# Listings
# ===================================================================


async def list_master_practices(
    user: User,
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
) -> PaginatedPracticesResponse:
    """List practices owned by the current master.

    R-04 fix: returns PaginatedPracticesResponse (with total count),
    consistent with list_public_practices().

    Excludes deleted practices. Master sees their own drafts.
    """
    base_filter = (
        Practice.master_id == user.id,
        Practice.status != PracticeStatus.DELETED.value,
    )

    # -- Total count --
    count_query = select(func.count(Practice.id)).where(*base_filter)
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # -- Paginated items with master name --
    stmt = (
        select(Practice, User.first_name, User.last_name)
        .join(User, Practice.master_id == User.id)
        .where(*base_filter)
        .order_by(Practice.scheduled_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    rows = result.all()

    # E3 batch 2: series card meta for the practices on this page (2 queries).
    page_practices = [p for p, _first, _last in rows]
    series_meta = await _series_meta_for_practices(page_practices, session)
    # E12 + aggregate: attendance counts for the same page (2 queries). This is
    # the master's own list (get_current_master), so the counts are shown
    # unconditionally here -- the owner-only gate lives on the shared public
    # detail endpoint (get_practice_detail) instead.
    attendance = await _attendance_counts_for_practices(page_practices, session)

    return PaginatedPracticesResponse(
        items=[
            practice_to_response(
                p,
                _master_full_name(first, last),
                # Z-6: the master's OWN list (get_current_master) -- every row
                # is owned by the requester, so expose zoom_link (the same owner
                # rule get_practice_detail applies). The master dashboard's
                # "Войти" button reads zoom_link from this list.
                zoom_link_visible=True,
                **_series_meta_kwargs(series_meta.get(p.id)),
                **_attendance_counts_kwargs(attendance.get(p.id)),
            )
            for p, first, last in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


def _local_hour(column_tz, column_ts):
    """Local hour (0-23) of a timestamp in a given timezone.

    `column_tz` may be a column (e.g. Practice.timezone) or a bound string
    (e.g. the viewer's timezone) -- func.timezone accepts both, and a string
    is emitted as a bound parameter, not an identifier.

    Postgres: EXTRACT(HOUR FROM (ts AT TIME ZONE tz_name)). Expressed via
    func.timezone(tz, ts) + extract() so it stays within the ORM (no raw
    SQL). func.timezone(text, timestamptz) returns the local wall-clock
    timestamp for that zone, from which we pull the hour.
    """
    return extract("hour", func.timezone(column_tz, column_ts))


def _time_of_day_filter(time_of_day: str, viewer_tz: str):
    """Build a half-open local-hour range condition for a time_of_day bucket.

    F5: the local hour is computed in the VIEWER'S timezone (passed in), not
    the practice's own timezone. The profile decides in which timezone the
    viewer sees practice times, so the "morning/day/evening" facet must bucket
    by the same wall-clock the card shows -- otherwise the filter and the
    displayed time disagree.

    Buckets (config-driven boundaries):
      night   [night_start,   morning_start)
      morning [morning_start, day_start)
      day     [day_start,     evening_start)
      evening [evening_start, 24)
    """
    night = settings.practice_time_night_start_hour
    morning = settings.practice_time_morning_start_hour
    day = settings.practice_time_day_start_hour
    evening = settings.practice_time_evening_start_hour

    ranges = {
        "night": (night, morning),
        "morning": (morning, day),
        "day": (day, evening),
        "evening": (evening, 24),
    }
    low, high = ranges[time_of_day]
    local_hour = _local_hour(viewer_tz, Practice.scheduled_at)
    return and_(local_hour >= low, local_hour < high)


async def list_public_practices(
    session: AsyncSession,
    *,
    user: User,
    limit: int = 20,
    offset: int = 0,
    master_id: UUID | None = None,
    practice_type: list[str] | None = None,
    direction: list[str] | None = None,
    difficulty: list[str] | None = None,
    style: list[str] | None = None,
    duration_bucket: Literal["short", "long"] | None = None,
    time_of_day: Literal[
        "night", "morning", "day", "evening",
    ] | None = None,
    status: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: Literal[
        "scheduled_at", "price_cents",
    ] = "scheduled_at",
    sort_order: Literal["asc", "desc"] = "asc",
) -> PaginatedPracticesResponse:
    """List practices visible in the public feed (Calendar feed).

    Default feed shows only UPCOMING bookable practices: status in
    scheduled/live AND scheduled_at strictly in the future. Practices that
    already started (including live) or are past are excluded -- they can no
    longer be booked. Passing an explicit `status` bypasses the time gate and
    matches that status exactly (no future-only restriction). Supports
    filtering by master, type, date range, and the Calendar facets
    (direction / difficulty / style / duration_bucket / time_of_day).

    Multi-value semantics (Calendar "Выбрать практики"):
      - Within one facet, values are OR-ed (.in_()).
      - Across facets, conditions are AND-ed (separate filter entries).

    Per-user flags (is_booked / is_paid) are computed for `user` over the
    practices on the returned page via a single bookings query.
    """
    # FIX 5.3: Build filter list once, apply to both queries (DRY).
    filters: list = []

    if status is not None:
        # Explicit status request (e.g. internal/master tooling): exact match,
        # no time gate -- the caller asked for a specific status on purpose.
        filters.append(Practice.status == status)
    else:
        # Default public feed: only practices a user can still BOOK.
        # "Bookable" = not yet started (scheduled_at strictly in the future).
        # This drops both past practices and ones that already started (incl.
        # live) -- you cannot sign up once a practice has begun. Bookings the
        # user already holds are surfaced elsewhere (dashboard / my bookings)
        # with a different, end-of-practice cutoff, so this gate does not hide
        # a practice the user is already attending.
        filters.append(Practice.status.in_(_FEED_STATUSES))
        filters.append(Practice.scheduled_at > datetime.now(UTC))

    if master_id is not None:
        filters.append(Practice.master_id == master_id)

    # practice_type: multi-select (OR within facet).
    if practice_type:
        filters.append(Practice.practice_type.in_(practice_type))

    # -- Calendar taxonomy facets (JSONB data.taxonomy, schema-on-read) --
    # direction / difficulty / style: multi-select (OR within facet).
    # B-4 (2026-05-29): style switched to list[str] + .in_() — was a single
    # exact match. Frontend sends one or more selected style chips.
    if direction:
        filters.append(
            Practice.data["taxonomy"]["direction"].as_string().in_(direction)
        )
    if difficulty:
        filters.append(
            Practice.data["taxonomy"]["difficulty"].as_string().in_(difficulty)
        )
    if style:
        filters.append(
            Practice.data["taxonomy"]["style"].as_string().in_(style)
        )

    # duration_bucket: short = < N minutes, long = >= N minutes.
    if duration_bucket is not None:
        threshold = settings.practice_duration_long_min_minutes
        if duration_bucket == "short":
            filters.append(Practice.duration_minutes < threshold)
        else:  # "long"
            filters.append(Practice.duration_minutes >= threshold)

    # time_of_day: local-hour bucket in the VIEWER'S timezone (F5). The
    # profile decides the display timezone, so the facet buckets by the same
    # wall-clock the card shows. `or "UTC"` guards an empty profile value with
    # the same neutral default the frontend format helpers use (never the
    # practice's own timezone, which would reintroduce the mismatch).
    if time_of_day is not None:
        filters.append(_time_of_day_filter(time_of_day, user.timezone or "UTC"))

    if date_from is not None:
        filters.append(Practice.scheduled_at >= date_from)

    if date_to is not None:
        filters.append(Practice.scheduled_at <= date_to)

    # -- Sort --
    sort_column = (
        Practice.price_cents
        if sort_by == "price_cents"
        else Practice.scheduled_at
    )
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    # -- Total count --
    count_query = select(func.count(Practice.id)).where(*filters)
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # -- Paginated items with master name --
    query = (
        select(Practice, User.first_name, User.last_name)
        .join(User, Practice.master_id == User.id)
        .where(*filters)
        .order_by(sort_column)
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(query)
    rows = result.all()

    # -- Per-user flags for the practices on this page (single query) --
    practice_ids = [p.id for p, _first, _last in rows]
    flags = await _user_flags_for_practices(user.id, practice_ids, session)

    return PaginatedPracticesResponse(
        items=[
            practice_to_response(
                p,
                _master_full_name(first, last),
                is_booked=flags.get(p.id, (False, False))[0],
                is_paid=flags.get(p.id, (False, False))[1],
            )
            for p, first, last in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )
