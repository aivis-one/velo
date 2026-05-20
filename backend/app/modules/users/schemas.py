# =============================================================================
# VELO Backend — User Schemas
# =============================================================================
#
# Pydantic models for user profile endpoints.
#
# UserResponse lives here (not in auth/) because it belongs to the users
# domain. auth/schemas.py imports it from here.
#
# ONBOARDING (welcome flow):
#   onboarding_completed is NOT a DB column. It lives inside the
#   credentials JSONB sandbox (key "onboarding_completed"), following the
#   "schema-on-read until it stabilizes, then extract to a column" pattern.
#   - UserResponse exposes it as a top-level bool (computed from credentials),
#     so the frontend never sees the raw credentials blob.
#   - UserUpdate accepts it so the welcome carousel can mark it done via
#     PATCH /users/me. The service writes it back into credentials.
# =============================================================================

from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, computed_field, field_validator

from app.modules.users.models import UserRole


class UserResponse(BaseModel):
    """User representation in API responses.

    onboarding_completed is derived from credentials (JSONB) rather than a
    dedicated column. The raw credentials blob is never exposed -- only this
    single boolean is surfaced. Validated from a User ORM instance via
    from_attributes; the computed_field reads self._credentials, populated
    from the ORM object's credentials dict.
    """

    id: UUID
    telegram_id: int | None
    role: UserRole
    first_name: str | None
    last_name: str | None
    avatar_url: str | None
    timezone: str
    language: str
    is_active: bool
    balance_cents: int
    created_at: datetime
    last_login_at: datetime | None

    # Private carrier for the raw credentials dict. Populated from the ORM
    # object's `credentials` attribute via from_attributes. Excluded from
    # serialization (leading underscore + PrivateAttr-like alias handling).
    # We keep it as a normal aliased field so from_attributes can fill it,
    # then derive onboarding_completed from it. It is excluded from output
    # by setting exclude=True.
    credentials_raw: dict = Field(
        default_factory=dict,
        validation_alias="credentials",
        exclude=True,
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def onboarding_completed(self) -> bool:
        """Whether the user has finished the welcome onboarding flow.

        Stored inside credentials JSONB. Missing key (new users) -> False.
        """
        return bool(self.credentials_raw.get("onboarding_completed", False))

    model_config = {"from_attributes": True, "populate_by_name": True}


class UserUpdate(BaseModel):
    """PATCH /api/v1/users/me — updatable profile fields.

    All fields are optional. Only provided fields are updated.
    avatar_url is excluded — managed by Telegram (future: Bot API).

    Empty strings are rejected (min_length=1). To clear a field,
    send null explicitly: {"last_name": null}.

    timezone and language are NOT NULL in DB — sending null for them
    is rejected by _reject_null_for_required_fields (mode="before").

    onboarding_completed is written into the credentials JSONB by the
    service layer (not a column). null is meaningless here, so only
    true/false are accepted; "not sent" leaves it untouched.
    """

    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    timezone: str | None = Field(default=None, min_length=1, max_length=50)
    language: str | None = Field(default=None, min_length=1, max_length=5)
    onboarding_completed: bool | None = Field(default=None)

    @field_validator("timezone", "language", mode="before")
    @classmethod
    def _reject_null_for_required_fields(cls, v: str | None) -> str | None:
        """Reject explicit null for NOT NULL DB columns.

        timezone and language have server defaults ("UTC", "en") but
        cannot be set to NULL. Sending null would cause IntegrityError.
        """
        if v is None:
            raise ValueError("This field cannot be set to null")
        return v

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str | None) -> str | None:
        """Validate timezone is a valid IANA timezone identifier.

        Runs after _reject_null_for_required_fields (mode="before"),
        so v is guaranteed to be a non-None string here.
        """
        if v is None:
            return v
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, KeyError):
            raise ValueError(
                f"Invalid IANA timezone: '{v}'. "
                "Examples: 'UTC', 'Europe/Moscow', 'America/New_York'"
            ) from None
        return v
