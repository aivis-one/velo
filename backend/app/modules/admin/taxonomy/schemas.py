# =============================================================================
# VELO Backend -- Admin Taxonomy Schemas (R5, batch R stage 2)
# =============================================================================
#
# Request/response schemas for the direction/style catalog CRUD.
# `value` is a machine slug (matches the existing config/practiceOptions.ts
# convention, e.g. "sound_healing", "kundalini") -- admin-supplied, validated
# against the same pattern the seeded values already follow.
# =============================================================================

from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

# lowercase, starts with a letter, letters/digits/underscore -- matches every
# existing seeded value (e.g. "sound_healing", "kundalini", "womens").
SlugStr = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]{1,49}$")]
LabelStr = Annotated[str, StringConstraints(min_length=1, max_length=100)]


class TaxonomyStyleResponse(BaseModel):
    """A single style (Вид), scoped to its direction."""

    id: UUID
    direction_id: UUID
    value: str
    label: str
    display_order: int
    is_active: bool
    source: str

    model_config = {"from_attributes": True}


class TaxonomyDirectionResponse(BaseModel):
    """A direction (Направление) with its nested styles.

    Shape matches AdminCatalogView.vue's local CatalogDirection type
    (value/label/styles[]) so the stage-3 FE swap is a drop-in.
    """

    id: UUID
    value: str
    label: str
    display_order: int
    is_active: bool
    source: str
    styles: list[TaxonomyStyleResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class TaxonomyListResponse(BaseModel):
    """GET /admin/taxonomy -- full catalog, all directions + styles (incl.
    inactive -- this is the admin management view, not a public consumer)."""

    directions: list[TaxonomyDirectionResponse]


class CreateDirectionRequest(BaseModel):
    """POST /admin/taxonomy/directions."""

    value: SlugStr
    label: LabelStr
    display_order: int = Field(default=0)


class CreateStyleRequest(BaseModel):
    """POST /admin/taxonomy/directions/{direction_id}/styles."""

    value: SlugStr
    label: LabelStr
    display_order: int = Field(default=0)


class UpdateTaxonomyItemRequest(BaseModel):
    """PATCH direction/style -- partial update.

    Only the fields the client actually sends are applied (service reads
    model_dump(exclude_unset=True), same partial-PATCH contract as
    editMasterProfile). is_active=false is how a direction/style is
    deactivated -- there is no separate hard-delete endpoint.
    """

    label: LabelStr | None = None
    display_order: int | None = None
    is_active: bool | None = None
