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
#   draft      -> scheduled, deleted
#   scheduled  -> live
#   live       -> completed
#   completed  -> (terminal)
#   cancelled  -> (terminal)
#   deleted    -> (terminal)
#
# IMPORTANT (Phase 6.5):
#   scheduled -> cancelled and live -> cancelled are NO LONGER allowed
#   via PATCH. The ONLY path to cancelled is through
#   cancel_practice() which handles refunds for all active bookings.
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
from app.modules.payments.refund import refund_all_bookings_for_practice
from app.modules.practices.models import Practice, PracticeStatus, PracticeType
from app.modules.practices.schemas import (
    CreatePracticeRequest,
    PaginatedPracticesResponse,
    PracticeResponse,
    UpdatePracticeRequest,
    _validate_style_for_direction,
)
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

# Valid state transitions via PATCH. Terminal states have no outgoing edges.
# Phase 6.5: cancelled is removed from scheduled/live transitions.
# The ONLY way to reach cancelled is via cancel_practice() which
# handles refunds. This prevents accidental PATCH status=cancelled
# that would skip refund logic.
_VALID_TRANSITIONS: dict[str, set[str]] = {
    PracticeStatus.DRAFT.value: {
        PracticeStatus.SCHEDULED.value,
        PracticeStatus.DELETED.value,
    },
    PracticeStatus.SCHEDULED.value: {
        PracticeStatus.LIVE.value,
    },
    PracticeStatus.LIVE.value: {
        PracticeStatus.COMPLETED.value,
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
    are required by the schema, style is optional.
    """
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
    hour, minute = anchor_local.hour, anchor_local.minute

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

        # Build the local wall-clock instant, then convert to UTC (DST-safe).
        local_dt = datetime(
            cursor.year, cursor.month, cursor.day, hour, minute, tzinfo=tz,
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
    return practice_to_response(
        practice,
        master_name,
        master_methods,
        master_avatar_url=master_avatar_url,
        is_booked=is_booked,
        is_paid=is_paid,
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
        # W-1: when style is changed WITHOUT direction in the same request,
        # the Pydantic model validator only checked it against the flattened
        # union (it has no stored direction context), so a style valid for a
        # DIFFERENT direction would slip through (e.g. setting "silence", a
        # meditation style, on a stored yoga practice). Re-validate here
        # against the direction actually stored on the practice. When direction
        # IS part of this update, the model validator already checked the pair.
        if "style" in taxonomy_updates and "direction" not in taxonomy_updates:
            stored_taxonomy = (practice.data or {}).get("taxonomy", {})
            stored_direction = stored_taxonomy.get("direction")
            try:
                _validate_style_for_direction(
                    stored_direction, taxonomy_updates["style"],
                )
            except ValueError as exc:
                raise BadRequestError(str(exc)) from exc

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


async def cancel_practice(
    practice_id: UUID,
    user: User,
    session: AsyncSession,
) -> Practice:
    """Cancel a scheduled/live practice with full refund to all participants.

    Master-only. This is the ONLY path to Practice.status=cancelled.
    PATCH status=cancelled is intentionally blocked in _VALID_TRANSITIONS.

    Steps:
    1. Lock practice with FOR UPDATE (P-12).
    2. Verify ownership (P-08: 404 not 403).
    3. Verify status is cancellable (scheduled or live).
    4. Refund all active bookings (100% to each user).
    5. Clear waitlist (all active entries -> left).
    6. Set practice status -> cancelled.
    7. Audit log.

    Raises NotFoundError if not found or not owner.
    Raises BadRequestError if practice is not in a cancellable state.
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

    # P-08: 404 not 403 for non-owner.
    if practice.master_id != user.id:
        raise NotFoundError("Practice not found")

    if practice.status not in _CANCELLABLE_PRACTICE_STATUSES:
        raise BadRequestError(
            f"Cannot cancel practice in status "
            f"{practice.status}"
        )

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
        practice_id=str(practice_id),
        master_id=str(user.id),
        refunded_bookings=refunded_count,
    )

    # Diary feed: fan out "master cancelled the practice" to the users who
    # were booked (collected above, before the refund). occurred_at is now.
    # Diary feed: fan out "master cancelled the practice" to the users who
    # were booked (collected above, before the refund). occurred_at is now.
    from app.modules.diary.projections import project_practice_cancelled
    # Master name for the diary card: full "First Last" (MVP rule). Load the
    # User directly rather than get_master_display_name (notification helper).
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
        occurred_at=datetime.now(UTC),
    )

    return practice


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

    return PaginatedPracticesResponse(
        items=[
            practice_to_response(p, _master_full_name(first, last))
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
