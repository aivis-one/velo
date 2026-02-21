# =============================================================================
# VELO Backend -- Admin Consistency Schemas (Phase 6.8)
# =============================================================================
#
# Response models for GET /api/v1/admin/consistency.
#
# SemaphoreResult: individual check outcome (OK or ALERT).
# ConsistencyResponse: aggregated response with all semaphore results.
# =============================================================================

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SemaphoreResult(BaseModel):
    """Single semaphore check result.

    name:        machine-readable identifier (e.g. "1.1_bookings_eq_purchases").
    category:    one of 5 categories from VELO-Data-Consistency-Semaphores.md.
    status:      OK if expected == actual, ALERT otherwise.
    expected:    what the check expects (human-readable string or number).
    actual:      what was found.
    details:     optional dict with extra context (e.g. mismatched IDs).
    criticality: how severe an ALERT is.
    """

    name: str
    category: str
    status: Literal["OK", "ALERT"]
    expected: str
    actual: str
    details: dict | None = None
    criticality: Literal["critical", "warning", "info"] = "critical"


class ConsistencyResponse(BaseModel):
    """GET /api/v1/admin/consistency -- response body."""

    items: list[SemaphoreResult]
    total: int = Field(description="Total number of semaphores executed")
    ok_count: int = Field(description="Semaphores that passed")
    alert_count: int = Field(description="Semaphores that failed")
    run_at: datetime = Field(description="Timestamp of this check run")
