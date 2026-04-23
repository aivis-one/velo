# Claude Design Pipeline — Velo Playbook

> Operational notes for design-gen cycles. Updated from Sprint 1 lessons onward.
> Governed by `docs/02_spec/03_Phase-Builder.md` § Design-Gen Cycle Type.
> Updated: 2026-04-23 (install — initial skeleton).

## Pre-flight per screen

- [ ] Figma reference open and approved
- [ ] Target route/view file identified in `FILE-TREE.md`
- [ ] Sponsor scope confirms screen is in scope
- [ ] Existing tokens in `Design_prototype/tokens.md` reviewed
- [ ] claude.ai/design project named `VELO / <screen> / <YYYY-MM-DD>`

## Claude Design prompt template (6 slots)

```
Artifact: high-fidelity clickable prototype of a single mobile screen.
Product: Velo — mobile Vue 3 PWA for wellness/meditation practices;
         three roles (user, master, admin).
Stage: MVP, continuing on branch new_desing.
Structure: screen "<name>", states: <default | loading | empty | error | success>;
           route: <path>; role: <role>.
Tone: soft glassmorphism, spacious, wellness-first, not marketing-fluffy.
Audience: mobile-first end users (Russian-first locale).

BRAND LOCK (mandatory):
NEVER use: cream/beige backgrounds, serif display fonts (Georgia, Fraunces,
Playfair), italic word accents, terracotta/amber accent colors.
USE: Marmelad font only, blue-slate base #4c6589, teal/peach/pink accents
per Design_prototype/tokens.md, glassmorphism with backdrop-blur(2px),
radii 15/200/5/100 strictly, shadow 0 0 20.9px 7px white on buttons.

References attached: codebase link, Figma link, tokens file,
screenshot of Figma target.
```

## Attachments to include before first generation

1. Codebase (GitHub repo or `frontend/` folder)
2. Figma file link
3. `Design_prototype/tokens.md` as a separate file (if tool doesn't parse md subfolders)
4. Screenshot of the Figma target screen

## Iteration rules

- First generation: single variant only (token economy).
- Revise via Edit / Comment / Tweaks. Regenerate only if direction is fundamentally wrong.
- If output drifts to default Opus 4.7 aesthetic (cream, serif, italic) — stop, re-paste brand lock, regenerate.

## Handoff

- Use "Handoff to Claude Code" export.
- In the extra instructions field, specify the target file path and reuse-existing-tokens rule.

## Post-handoff verification

- [ ] `npm run typecheck` passes
- [ ] `npm run lint` passes
- [ ] `npm run test` passes
- [ ] Visual parity with Figma in local dev server
- [ ] Push to `new_desing` → staging deploys → visual verification on staging URL

## Lessons (populated from Sprint 1 onward)

_None yet. First entries will land during Sprint 1 pilot._
