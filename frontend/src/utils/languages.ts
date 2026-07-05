// =============================================================================
// VELO Frontend -- Practice languages (shared source, E16)
// =============================================================================
//
// The flat set of languages a master can run practices in. Single source of
// truth for the application wizard (MasterApplyView step 2) and the profile
// editor (EditProfileView, master variant). Plain human-readable strings,
// stored on the master profile as data.profile.languages (mirrors methods).
// =============================================================================

export const LANGUAGES = ['Русский', 'English'] as const
