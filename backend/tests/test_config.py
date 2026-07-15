"""W6 hotfix: settings.is_stripe_stub_blocked, the guard behind lifespan()'s
startup RuntimeError in main.py.

Exercised directly against the property rather than through the `client`
fixture's ASGITransport: ASGITransport never sends a "lifespan" scope (only
"http"), so lifespan() -- and this guard -- never runs during the test
suite regardless of what APP_ENV/ALLOW_STRIPE_STUB are set to. That also
means the guard has no way to break the test suite itself; testing the
property directly is the only practical way to cover its actual logic.
"""

import pytest

from app.core.config import settings


@pytest.mark.parametrize(
    ("app_env", "stripe_secret_key", "allow_stripe_stub", "expected_blocked"),
    [
        # Dev laptop: stub key, no flag needed -- always allowed.
        ("development", "TEST", False, False),
        ("development", "TEST", True, False),
        # TEST server (calls itself "production"): stub key, flag set --
        # the case the original app_env-only guard broke.
        ("production", "TEST", True, False),
        # TEST server without the flag configured yet: must still refuse,
        # the flag is what makes the opt-in explicit.
        ("production", "TEST", False, True),
        # Prod with a real key: never blocked, flag irrelevant either way.
        ("production", "sk_live_real_key", False, False),
        ("production", "sk_live_real_key", True, False),
    ],
)
def test_is_stripe_stub_blocked(
    monkeypatch: pytest.MonkeyPatch,
    app_env: str,
    stripe_secret_key: str,
    allow_stripe_stub: bool,
    expected_blocked: bool,
) -> None:
    monkeypatch.setattr(settings, "app_env", app_env)
    monkeypatch.setattr(settings, "stripe_secret_key", stripe_secret_key)
    monkeypatch.setattr(settings, "allow_stripe_stub", allow_stripe_stub)

    assert settings.is_stripe_stub_blocked is expected_blocked
