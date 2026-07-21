// =============================================================================
// VELO Frontend -- Zoom link ladder (T21-1, ПРОМТ №541, owner decision D3)
// =============================================================================
//
// One place for the rule every Zoom entry point (user dashboard, practice-
// live, master dashboard) must follow, in this exact order:
//   1. the person's OWN registrant join_url (the ?tk= personal link) --
//      the only link Zoom will ever associate with them for attendance.
//   2. the manual Practice.zoom_link fallback -- ONLY if 1 is absent, and
//      the caller MUST mark it visibly distinct (attendance is not counted
//      for this state -- D1).
//   3. neither exists yet -- an honest "being prepared" state.
//
// A SILENT FALL-THROUGH TO STATE 2 IS FORBIDDEN: the whole defect being
// fixed is a user joining by a shared link with nothing telling them their
// attendance won't be recorded. `kind` exists so callers cannot skip that.
// =============================================================================

export type ZoomLinkKind = 'personal' | 'manual' | 'pending'

export interface ZoomLinkResolution {
  kind: ZoomLinkKind
  url: string | null
}

function isValidHttpsUrl(value: string | null | undefined): value is string {
  return !!value && value.startsWith('https://')
}

/** Resolve which link (if any) a Zoom entry point should offer right now. */
export function resolveZoomLink(
  personalJoinUrl: string | null | undefined,
  manualZoomLink: string | null | undefined,
): ZoomLinkResolution {
  if (isValidHttpsUrl(personalJoinUrl)) {
    return { kind: 'personal', url: personalJoinUrl }
  }
  if (isValidHttpsUrl(manualZoomLink)) {
    return { kind: 'manual', url: manualZoomLink }
  }
  return { kind: 'pending', url: null }
}
