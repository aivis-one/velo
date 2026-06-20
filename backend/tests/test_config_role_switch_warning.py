# =============================================================================
# VELO Backend -- Tests: role_switch startup warning (W-4, variant D)
# =============================================================================
#
# role_switch_enabled is a TEST-ONLY flag. app_env cannot distinguish the
# (prod-grade) TEST server from PROD, so we cannot hard-gate by environment;
# instead the settings validator emits a loud security warning whenever the
# flag is on. Expected noise on the TEST server, an alarm in production logs.
#
# We pass app_env="development" so the validator fills safe DB/secret defaults
# and constructs without a real .env; explicit init kwargs override any ambient
# environment (incl. ROLE_SWITCH_ENABLED on the test server).
# =============================================================================

import logging

from app.core.config import Settings

_WARNING_NEEDLE = "ROLE_SWITCH_ENABLED is ON"
_SECURITY_LOGGER = "velo.security"


def test_role_switch_enabled_logs_warning(caplog) -> None:
    """Enabling role_switch logs the loud security warning."""
    with caplog.at_level(logging.WARNING, logger=_SECURITY_LOGGER):
        Settings(app_env="development", role_switch_enabled=True)

    assert any(
        _WARNING_NEEDLE in record.message for record in caplog.records
    ), "expected a role-switch security warning when the flag is on"


def test_role_switch_disabled_no_warning(caplog) -> None:
    """No warning is emitted when the flag is off."""
    with caplog.at_level(logging.WARNING, logger=_SECURITY_LOGGER):
        Settings(app_env="development", role_switch_enabled=False)

    assert not any(
        _WARNING_NEEDLE in record.message for record in caplog.records
    ), "no role-switch warning expected when the flag is off"
