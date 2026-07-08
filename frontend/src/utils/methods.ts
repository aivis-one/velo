// =============================================================================
// VELO Frontend -- Practice methods (shared source)
// =============================================================================
//
// The flat set of practice methods a master can declare. Single source of
// truth for both the application wizard (MasterApplyView, step 2) and the
// method change-request picker (EditProfileView, master variant / M3).
//
// FLAT branch (M3): plain human-readable strings. The two-level
// direction->kind taxonomy (E19) is deferred / out of scope.
// =============================================================================

export const AVAILABLE_METHODS = [
  'Медитация',
  'Mindfulness / MBSR',
  'Дыхательные практики',
  'Йога',
  'Кундалини йога',
  'Звукотерапия',
] as const
