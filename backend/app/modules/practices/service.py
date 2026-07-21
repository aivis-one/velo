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
#   master_full_name() from User.first_name + User.last_name in every JOIN /
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
from datetime import UTC, datetime
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    BadRequestError,
    NotFoundError,
)
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.practices.enrichment_service import (
    attendance_counts_for_practices,
    attendance_counts_kwargs,
    series_meta_for_practices,
    series_meta_kwargs,
)
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.practices.schemas import (
    CreatePracticeRequest,
    PracticeResponse,
    UpdatePracticeRequest,
)
from app.modules.practices.series_service import generate_series_occurrences
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


def master_full_name(
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
    zoom_host_join_url: str | None = None,
) -> PracticeResponse:
    """Build PracticeResponse from ORM object with master_name and master_methods.

    master_name:       full "First Last" built via master_full_name() from the
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

    # T21-1: host join_url -- caller decides whether to fetch/pass it (owner-
    # facing responses only); everyone else gets the schema default (None).
    resp.zoom_host_join_url = zoom_host_join_url

    return resp


async def user_flags_for_practices(
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
    master_name = master_full_name(first_name, last_name)

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
    private helpers (C-1: no cross-layer import of user_flags_for_practices).
    """
    practice, master_name, master_avatar_url, master_methods = (
        await get_practice(practice_id, user, session)
    )
    flags = await user_flags_for_practices(user.id, [practice.id], session)
    is_booked, is_paid = flags.get(practice.id, (False, False))
    series_meta = await series_meta_for_practices([practice], session)
    # E12 + aggregate: OWNER-ONLY on this shared detail endpoint. no_show is
    # sensitive, so a non-owner viewer never sees these -- skip the query and
    # leave all three None. (Series-meta above is innocuous and shown to all.)
    is_owner = practice.master_id == user.id
    attendance = (
        await attendance_counts_for_practices([practice], session)
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
    # T21-1: host join_url, owner-only -- same is_owner gate as the
    # attendance counts above (a non-owner must never see the master's
    # personal link either).
    host_join_url = None
    if is_owner:
        from app.modules.zoom.service import get_host_join_url
        host_join_url = await get_host_join_url(practice.id, session)
    return practice_to_response(
        practice,
        master_name,
        master_methods,
        master_avatar_url=master_avatar_url,
        is_booked=is_booked,
        is_paid=is_paid,
        zoom_link_visible=zoom_visible,
        zoom_host_join_url=host_join_url,
        **series_meta_kwargs(series_meta.get(practice.id)),
        **attendance_counts_kwargs(attendance.get(practice.id)),
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
        master_name = master_full_name(
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

        # E21: keep the Zoom meeting's start time in sync, then re-fetch and
        # overwrite stored registrant join links -- self-healing regardless
        # of whether Zoom actually invalidates them on reschedule (unresolved
        # question, see zoom/service.py docstring). Best-effort: never raises.
        from app.modules.zoom.service import sync_meeting_reschedule
        await sync_meeting_reschedule(practice, session)

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
        await generate_series_occurrences(practice, session)

    # E21: create the practice's Zoom meeting on publish (draft -> scheduled),
    # for ANY practice type -- not gated on series, unlike the block above.
    # Best-effort: create_meeting_for_practice never raises, so publish
    # always succeeds regardless of Zoom's outcome (ПРОМТ №519 amendment 2 --
    # confirmed as the intended reading). KNOWN GAP: series CHILDREN are
    # created directly inside generate_series_occurrences() with
    # status=scheduled and never pass through this branch, so they do not
    # get a Zoom meeting from this step -- out of scope for this prompt
    # (would touch series_service.py), flagged rather than silently patched.
    if (
        old_status == PracticeStatus.DRAFT.value
        and practice.status == PracticeStatus.SCHEDULED.value
    ):
        from app.modules.zoom.service import create_meeting_for_practice
        await create_meeting_for_practice(practice, session)

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
