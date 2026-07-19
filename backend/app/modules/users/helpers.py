# =============================================================================
# VELO Backend -- Users Helpers
# =============================================================================
#
# Small pure helpers for user presentation, defined once and shared across
# modules. display_name is the platform-wide formatter for a (non-master)
# person's display name with the neutral "Участник" fallback. Master display
# names are intentionally NOT routed here -- they fall back to "Мастер" and may
# prefer a MasterProfile display_name (see practices.master_full_name and
# admin.practices._master_name), which is a different rule.
# =============================================================================


def display_name(first_name: str | None, last_name: str | None) -> str:
    """Person display name: "First Last", else the neutral "Участник".

    Empty / None parts are dropped, so there is never a trailing space or a
    literal "None"; when both parts are empty the neutral participant label is
    used. Parts-based (not User-based) so callers holding only first/last --
    e.g. an admin roster row -- can use it without a User object.
    """
    name = " ".join(part for part in (first_name, last_name) if part).strip()
    return name or "Участник"
