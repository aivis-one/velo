# =============================================================================
# VELO Backend -- Admin Masters Router (Phase 2.3, moved Phase 3.1)
# =============================================================================
#
# ENDPOINTS:
#   POST /api/v1/admin/masters/{user_id}/verify -- approve application
#   POST /api/v1/admin/masters/{user_id}/reject -- reject application
#
# AUTH: get_current_admin on every endpoint.
# SESSION: flush() + refresh(), no commit (P-01).
# =============================================================================

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.modules.admin.masters.schemas import (
    AdminMasterActionResponse,
    InviteMasterRequest,
    InviteMasterResponse,
    RejectMasterRequest,
    VerifyMasterRequest,
)
from app.modules.admin.masters.service import (
    issue_master_invite,
    reject_master,
    verify_master,
)
from app.modules.auth.dependencies import get_current_admin
from app.modules.users.models import User

logger = structlog.get_logger()

router = APIRouter(prefix="/masters")


@router.post(
    "/invite",
    response_model=InviteMasterResponse,
)
async def invite_master_endpoint(
    body: InviteMasterRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> InviteMasterResponse:
    """Issue a one-time master invite link (Batch-INVITE).

    The target must have opened the bot at least once (User row exists,
    else 404) and must not already be a master (else 409). The full deeplink
    is composed server-side from telegram_bot_url; only the token's sha256
    is stored. Re-issuing overwrites the previous (unclaimed) link.
    """
    invite_link, issued_at = await issue_master_invite(
        body.telegram_id, admin, session
    )
    await session.flush()
    return InviteMasterResponse(invite_link=invite_link, issued_at=issued_at)


@router.post(
    "/{user_id}/verify",
    response_model=AdminMasterActionResponse,
)
async def verify_master_endpoint(
    user_id: UUID,
    body: VerifyMasterRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> AdminMasterActionResponse:
    """Verify a pending master application.

    Updates profile status to 'verified' and promotes user role to MASTER.
    """
    profile = await verify_master(user_id, admin, body.notes, session)

    await session.flush()
    await session.refresh(profile)

    return AdminMasterActionResponse(
        user_id=profile.user_id,
        status=profile.data["account"]["status"],
    )


@router.post(
    "/{user_id}/reject",
    response_model=AdminMasterActionResponse,
)
async def reject_master_endpoint(
    user_id: UUID,
    body: RejectMasterRequest,
    admin: User = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db_session),
) -> AdminMasterActionResponse:
    """Reject a pending master application.

    Stores rejection reason. User can reapply later.
    """
    profile = await reject_master(user_id, admin, body.reason, session)

    await session.flush()
    await session.refresh(profile)

    return AdminMasterActionResponse(
        user_id=profile.user_id,
        status=profile.data["account"]["status"],
    )
