# =============================================================================
# VELO Backend — Users Router
# =============================================================================
#
# ENDPOINTS:
#   GET   /api/v1/users/me  — Get current user profile
#   PATCH /api/v1/users/me  — Update current user profile
#
# TD-029 fix: PATCH /users/me now uses get_current_user_write instead of
#   get_current_user. Both the dependency and the router declare
#   Depends(get_db_session), so FastAPI reuses the same session instance
#   for the entire request — one DB connection instead of two.
#   The service no longer needs session.merge().
#
# MASTER NOTIFICATIONS (E8): UserResponse.master_notifications is exposed only
#   when the caller has master capability (a verified MasterProfile). That
#   check needs the MasterProfile table, which UserResponse cannot read on its
#   own, so EVERY endpoint here that returns a UserResponse carrying
#   master_notifications (GET / PATCH /me, POST /me/role) funnels through
#   _user_response_with_capability(), which computes the capability and sets the
#   response carrier. Capability -- not strict role==master -- so an admin who
#   is also a verified master keeps the screen. DELETE /me returns 204 (no
#   body) and does not need it.
# =============================================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_reader, get_db_session
from app.modules.auth.dependencies import get_current_user, get_current_user_write
from app.modules.users.models import User
from app.modules.users.schemas import RoleSwitchRequest, UserResponse, UserUpdate
from app.modules.users.service import (
    reset_user_to_onboarding,
    switch_user_role,
    update_user,
    user_has_master_capability,
)

router = APIRouter(prefix="/api/v1/users", tags=["users"])


async def _user_response_with_capability(
    user: User,
    session: AsyncSession,
) -> UserResponse:
    """Serialize a user and set the master_notifications capability gate.

    master_notifications is shown only when the user has master capability (a
    verified MasterProfile); UserResponse cannot derive that on its own, so any
    endpoint returning a UserResponse that carries master_notifications routes
    through here to set the master_capability_in carrier. Without this the
    block would silently come back null (the gate defaults to "no capability").

    The session may be the read or the write session for the request -- the
    capability lookup is a plain SELECT and works on either.
    """
    response = UserResponse.model_validate(user)
    response.master_capability_in = await user_has_master_capability(
        user, session
    )
    return response


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_reader),
) -> UserResponse:
    """Return the authenticated user's profile.

    The user is loaded by get_current_user (read-only session). The same
    get_db_reader session is reused here (FastAPI caches Depends within a
    request, so this is one DB connection, not two) to check master capability,
    which gates the master_notifications block (see
    _user_response_with_capability).
    """
    return await _user_response_with_capability(user, session)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    user: User = Depends(get_current_user_write),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Update the authenticated user's profile.

    TD-029: get_current_user_write and Depends(get_db_session) share
    the same session instance (FastAPI caches Depends within a request).
    The user is already bound to the write session — no merge needed.

    Only fields present in the request body are updated. The response carries
    master_notifications gated by master capability, same as GET /me, so the
    frontend can read back the freshly-saved master prefs.
    """
    updated = await update_user(user, body, session)
    return await _user_response_with_capability(updated, session)


@router.post("/me/role", response_model=UserResponse)
async def switch_my_role(
    body: RoleSwitchRequest,
    user: User = Depends(get_current_user_write),
    session: AsyncSession = Depends(get_db_session),
) -> UserResponse:
    """Switch the caller's own role (capability-derived, A1=Б).

    Always on -- no feature flag. Security rests on the derived policy in
    switch_user_role: the allowed target set is computed from the caller's
    current role and master capability (derive_allowed_roles, shared with the
    role_switch block in GET /me). A plain user derives {USER} only, so the
    endpoint grants nothing; a non-admin can never switch to ADMIN. Targets
    outside the derived set -> 403. The role is rewritten on the User row in
    place, so every existing role guard keeps working unchanged on
    subsequent requests.

    get_current_user_write + Depends(get_db_session) share one session
    (TD-029), so the mutation and the user load use the same connection. The
    response gates master_notifications by master capability (a verified
    MasterProfile), which is role-independent, like GET /me.
    """
    updated = await switch_user_role(user, body.role, session)
    return await _user_response_with_capability(updated, session)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user: User = Depends(get_current_user_write),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Delete the authenticated user's account.

    MVP SEMANTICS (see reset_user_to_onboarding): this does NOT erase data or
    deactivate the account. It resets the onboarding flag so the next login
    sends the user through the welcome flow again, with their old data intact.
    The endpoint contract ("DELETE my account") is kept so that real deletion
    can later be implemented by changing only the service body.

    Returns 204 No Content. The frontend then logs the user out (which closes
    the Mini App in Telegram / redirects in standalone).
    """
    await reset_user_to_onboarding(user, session)
