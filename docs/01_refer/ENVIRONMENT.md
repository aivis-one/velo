# Velo — Environment

> Loaded in every working chat. Bridge between framework rules and project reality.
> Updated: 2026-04-23.

---

## System

| Item | Value |
|---|---|
| OS | Windows 11 |
| Shell (Claude Code) | bash |
| Project path | `D:\03_Projects\velo` |
| Prompt detail level | FULL |

Developer works on a single Windows laptop; Claude Code runs with bash as its shell. Prompts target bash syntax. PowerShell is not used.

---

## Tools

| Tool | Version | Notes |
|---|---|---|
| Node | 24.13.0 | Frontend runtime (Vite dev server, build) |
| npm | bundled with Node | Package manager |
| Vite | ^6.1 | Build tool |
| Vue | ^3.5 | Framework |
| TypeScript | ~5.7 | Strict mode |
| Pinia | ^2.3 | State |
| vue-router | ^4.5 | Routing |
| Vitest | ^3.0 | Test runner |
| ESLint | ^9.20 | Linter |
| Prettier | ^3.5 | Formatter |
| Docker | — | Compose v2 for local full-stack |
| cloc | — | Used in Sprint-Closer SNAPSHOT for LOC count |
| gh | 2.88.1 | GitHub CLI; auth: `abalyakno` (keyring) |
| Claude Design | claude.ai/design | UI generation surface (see ARCHITECTURE.md) |
| ProbeKit skills | probekit-* | Auto-run lite profile at sprint close |

Not required for frontend work: Python, pytest, Godot, PostgreSQL (runs in Docker), Stripe CLI.

---

## Quality Tools

| Tool | Command | Purpose |
|---|---|---|
| Linter | `cd frontend && npm run lint` | ESLint 9 |
| Formatter | `cd frontend && npm run format` | Prettier |
| Type checker | `cd frontend && npm run typecheck` | vue-tsc |
| Test runner | `cd frontend && npm run test` | Vitest |
| Pre-commit | (not configured) | Candidate for `BACKLOG.md` |

---

## Git Workflow

| Item | Value |
|---|---|
| Main branch | `main` |
| Active branch | `new_desing` (note: "desing" is the intentional branch name from S0; do not "correct") |
| Strategy | Work continues on `new_desing`; merge to `main` per milestone, no feature branches |
| Remote | GitHub (project repo; resolve with `gh repo view` when needed) |

### Commit convention

| Context | Format | Example |
|---|---|---|
| Cycle work | `cycle: C{NN} <short description>` | `cycle: C03 redesign UserDashboardView` |
| Cycle close | `cycle: C{NN} <short name> — DONE` | `cycle: C03 user-dashboard — DONE` |
| Phase close | `phase: P{NN} <name> — DONE` | `phase: P01 pilot — DONE` |
| Sprint close | `sprint: S{N} <name> — CLOSED` | `sprint: S1 pilot — CLOSED` |
| Doc update | `docs: <what changed>` | `docs: ARCHITECTURE.md — add coding standards` |
| Decision | `decision: <short title>` | `decision: choose vue 3.5 for Velo` |
| Refactor | `refactor: <short description>` | `refactor: extract topup error state` |
| Fix | `fix: <short description>` | `fix: topup webhook race condition` |
| Clean-Sync | `clean-sync: S{N} <description>` | `clean-sync: S1 FILE-TREE refresh` |
| Audit | `audit: CODE-AUDIT-S{N} <name>` | `audit: CODE-AUDIT-S1 pilot` |

### Rules

- Never force-push without explicit Human authorization (e.g., git history security remediation).
- Never commit secrets, API keys, server credentials. `SERVER-ACCESS.md` is gitignored.
- Commit messages must be meaningful.
- Execute prompts end with `git add ... && git commit ... && git push` unless the prompt explicitly states otherwise.

---

## Backlogs

Single backlog: `BACKLOG.md` at `docs/01_refer/BACKLOG.md`. All code issues, tech debt, features, tooling gaps go here. No separate SPEC backlog (we do not maintain SPEC in Velo profile).

---

## Known Limitations

| Limitation | Workaround |
|---|---|
| Cannot push directly to production server | Server deploys happen via `new_desing` push → staging auto-pulls. Production promotion requires manual Human action (see `SERVER-ACCESS.md` after it is populated). |
| Cannot edit backend | `backend/` is out of scope; friend owns it. Consume via `frontend/src/api/types.ts`. |
| Cannot browser-test frontend from Claude Code | Visual verification happens on staging after push (Sprint 1 trigger). Alternative: ask Human to screenshot local dev server. |
| Cannot guess missing API endpoints | If `frontend/src/api/types.ts` lacks the needed type, STOP and ask Human to coordinate with backend owner. |

---

## Information Map

Files under `docs/` and what they own:

| File | Contains | Does NOT Contain |
|---|---|---|
| `01_refer/ARCHITECTURE.md` | Project overview, components summary, coding standards, tools/pipelines, scope boundaries, links to root VELO-*.md | Implementation code, sprint plans, cycle detail |
| `01_refer/ENVIRONMENT.md` | System, tools, git workflow, commit convention, backlogs location, known limitations, information map | Architecture, decisions, sprint state |
| `01_refer/FILE-TREE.md` | `frontend/src/` + `docs/` tree with per-file notes | `backend/`, root-level files (referenced elsewhere) |
| `01_refer/BACKLOG.md` | Code issues, tech debt, features, tooling gaps | Protocol improvements (none kept) |
| `01_refer/decisions.md` | Flat table of key decisions (what/why/when) | Research artifacts, debates |
| `01_refer/SERVER-ACCESS.md` | Staging/prod endpoints, safe-command list, deploy procedure | Credentials as plaintext (use env refs) — gitignored regardless |
| `01_refer/GUIDES/claude-design-pipeline.md` | Operational playbook for design-gen cycles | Framework rules (→ `03_Phase-Builder.md`) |
| `03_sprint/S{N}-SPRINT.md` | Sprint goal, phases inline, protocol log, current state, next action | Cycle-level detail (in phase sections or separate `C{NN}.md` if large) |

---

## Shell Notes (bash)

- Forward slashes in paths everywhere.
- For Windows drive roots, `/d/03_Projects/velo/` style or `D:/03_Projects/velo/` both work in Git Bash.
- `npm` commands run from `frontend/` directory. Use `(cd frontend && npm run ...)` pattern to avoid leaving working directory.
- `docker compose` (v2 syntax, no hyphen).

---

## Tool Notes

### Vite dev server
- Config: `frontend/vite.config.ts`. PWA plugin enabled.
- Default port 5173 unless overridden.
- For API proxy behavior: check current `vite.config.ts` state before assuming.

### vue-tsc
- `npm run build` runs `vue-tsc --noEmit && vite build`. Build fails on any type error — do not bypass.

### Claude Design
- Access: claude.ai/design (Pro/Max/Team required).
- Brand lock language is mandatory (see `ARCHITECTURE.md` §Tools).
- One cycle = one screen. Do not batch multiple screens into one Claude Design project.

### ProbeKit
- All skills invoked by name `/probekit-<skill>`. Lite profile runs automatically in Sprint-Closer Step 2.
- If a skill reports "not applicable" for current scope, record and skip.

---

## Anchor

```
[ENVIRONMENT.md | SPEC v3.2-velo]
Project environment — system, tools, git workflow, information map
Location: docs/01_refer/ENVIRONMENT.md
Referenced from: S{N}-SPRINT.md + loaded in every working chat
Update when: tools change, new pitfalls discovered, sprint close
```
