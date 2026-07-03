# =============================================================================
# Test: Master invite — one-time link (Batch-INVITE, C1=Б / TTL=В)
# =============================================================================
#
# POST /admin/masters/invite  (admin-auth): resolves the target by
#   telegram_id, stores sha256(token) in credentials.master_invite and
#   returns the full composed deeplink. No expiry (TTL=В): the link is
#   one-time until claimed; re-issue overwrites the previous token.
# POST /masters/invite/claim  (user-auth): binds structurally to the
#   CALLER'S OWN marker, consumes it on success (single use). Becoming a
#   master still goes through the regular apply + approval loop.
#
# telegram_bot_url is monkeypatched so the composed link is deterministic
# regardless of the ambient .env.
# =============================================================================

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.modules.users.models import User
from tests.helpers import auth_headers, full_cleanup_range, login_user

TID_MIN = 88300
TID_MAX = 88399

BOT_URL = "https://t.me/velo_testbot"
LINK_PREFIX = f"{BOT_URL}?startapp=master_onboarding__"


@pytest.fixture(autouse=True)
async def _cleanup(db_session: AsyncSession):
    """Wipe the invite telegram_id range before and after each test."""
    await full_cleanup_range(db_session, TID_MIN, TID_MAX)
    await db_session.commit()
    yield
    await full_cleanup_range(db_session, TID_MIN, TID_MAX)
    await db_session.commit()


@pytest.fixture(autouse=True)
def _bot_url(monkeypatch: pytest.MonkeyPatch):
    """Pin telegram_bot_url so the composed link is deterministic."""
    monkeypatch.setattr(settings, "telegram_bot_url", BOT_URL)


async def _get_user(db_session: AsyncSession, telegram_id: int) -> User:
    db_session.expire_all()
    return (
        await db_session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
    ).scalar_one()


async def _set_role(
    db_session: AsyncSession, telegram_id: int, role: str
) -> None:
    user = await _get_user(db_session, telegram_id)
    user.role = role
    await db_session.commit()


async def _login_admin(client: AsyncClient, db_session: AsyncSession) -> str:
    """Create + promote the acting admin, return their session token."""
    data = await login_user(client, telegram_id=88300, first_name="Inviter")
    await _set_role(db_session, 88300, "admin")
    return data["session_token"]


async def _issue(client: AsyncClient, token: str, telegram_id: int):
    return await client.post(
        "/api/v1/admin/masters/invite",
        headers=auth_headers(token),
        json={"telegram_id": telegram_id},
    )


async def _claim(client: AsyncClient, token: str, invite_token: str):
    return await client.post(
        "/api/v1/masters/invite/claim",
        headers=auth_headers(token),
        json={"token": invite_token},
    )


def _token_from_link(link: str) -> str:
    assert link.startswith(LINK_PREFIX), link
    return link[len(LINK_PREFIX):]


# ---------------------------------------------------------------------------
# Issue (admin side)
# ---------------------------------------------------------------------------


async def test_issue_non_admin_403(
    client: AsyncClient,
) -> None:
    """A plain user cannot issue invites."""
    data = await login_user(client, telegram_id=88301, first_name="Plain")
    response = await _issue(client, data["session_token"], 88301)
    assert response.status_code == 403


async def test_issue_unknown_telegram_id_404(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """No User row for the target -> 404 with the machine code."""
    admin_token = await _login_admin(client, db_session)

    response = await _issue(client, admin_token, 88399)
    assert response.status_code == 404
    assert response.json()["error"] == "invite_target_not_found"


async def test_issue_already_master_409(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Target already has role MASTER -> 409."""
    admin_token = await _login_admin(client, db_session)
    await login_user(client, telegram_id=88302, first_name="AlreadyM")
    await _set_role(db_session, 88302, "master")

    response = await _issue(client, admin_token, 88302)
    assert response.status_code == 409
    assert response.json()["error"] == "already_master"


async def test_issue_success_returns_composed_link(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Success returns the full server-composed deeplink + issued_at.

    Only the sha256 lands in credentials (never the plaintext token), and
    there is deliberately NO expiry field (TTL=В).
    """
    admin_token = await _login_admin(client, db_session)
    await login_user(client, telegram_id=88303, first_name="Invitee")

    response = await _issue(client, admin_token, 88303)
    assert response.status_code == 200
    body = response.json()
    assert body["invite_link"].startswith(LINK_PREFIX)
    assert body["issued_at"] is not None
    assert "expires_at" not in body

    token = _token_from_link(body["invite_link"])
    user = await _get_user(db_session, 88303)
    marker = (user.credentials or {}).get("master_invite")
    assert marker is not None
    assert marker["token_sha256"] != token  # hash stored, not plaintext
    assert marker["issued_by"]
    assert marker["issued_at"]


async def test_reissue_overwrites_old_token(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """Re-issue kills the previous link: old token 403s, new one claims."""
    admin_token = await _login_admin(client, db_session)
    invitee = await login_user(client, telegram_id=88304, first_name="Twice")

    first = await _issue(client, admin_token, 88304)
    old_token = _token_from_link(first.json()["invite_link"])
    second = await _issue(client, admin_token, 88304)
    new_token = _token_from_link(second.json()["invite_link"])
    assert old_token != new_token

    old_claim = await _claim(client, invitee["session_token"], old_token)
    assert old_claim.status_code == 403
    assert old_claim.json()["error"] == "invite_invalid"

    new_claim = await _claim(client, invitee["session_token"], new_token)
    assert new_claim.status_code == 200


# ---------------------------------------------------------------------------
# Claim (invitee side)
# ---------------------------------------------------------------------------


async def test_claim_success_consumes_single_use(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A valid claim records claimed_at, drops the hash; second claim 403s."""
    admin_token = await _login_admin(client, db_session)
    invitee = await login_user(client, telegram_id=88305, first_name="Claimer")
    issued = await _issue(client, admin_token, 88305)
    token = _token_from_link(issued.json()["invite_link"])

    response = await _claim(client, invitee["session_token"], token)
    assert response.status_code == 200
    assert response.json()["claimed_at"] is not None

    # Marker consumed: hash gone, claimed_at + audit fields kept.
    user = await _get_user(db_session, 88305)
    marker = (user.credentials or {}).get("master_invite")
    assert "token_sha256" not in marker
    assert marker["claimed_at"]
    assert marker["issued_by"]

    # Single use: the same (correct) token no longer claims.
    again = await _claim(client, invitee["session_token"], token)
    assert again.status_code == 403
    assert again.json()["error"] == "invite_invalid"


async def test_claim_foreign_token_403(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A stranger holding someone else's link cannot claim it."""
    admin_token = await _login_admin(client, db_session)
    await login_user(client, telegram_id=88306, first_name="Invited")
    stranger = await login_user(client, telegram_id=88307, first_name="Thief")
    issued = await _issue(client, admin_token, 88306)
    token = _token_from_link(issued.json()["invite_link"])

    response = await _claim(client, stranger["session_token"], token)
    assert response.status_code == 403
    assert response.json()["error"] == "invite_invalid"


async def test_claim_garbage_token_403(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """A well-formed but wrong token 403s even for an invited account."""
    admin_token = await _login_admin(client, db_session)
    invitee = await login_user(client, telegram_id=88308, first_name="Garbled")
    await _issue(client, admin_token, 88308)

    response = await _claim(
        client, invitee["session_token"], "x" * 43  # token_urlsafe(32) length
    )
    assert response.status_code == 403
    assert response.json()["error"] == "invite_invalid"


async def test_claim_already_master_409(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    """An account that already became a master cannot re-claim."""
    admin_token = await _login_admin(client, db_session)
    invitee = await login_user(client, telegram_id=88309, first_name="Fast")
    issued = await _issue(client, admin_token, 88309)
    token = _token_from_link(issued.json()["invite_link"])
    await _set_role(db_session, 88309, "master")

    response = await _claim(client, invitee["session_token"], token)
    assert response.status_code == 409
    assert response.json()["error"] == "already_master"
