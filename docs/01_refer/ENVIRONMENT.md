# Velo — Environment

> Loaded in every working chat. Bridge between framework rules and project reality.
> Updated: 2026-04-28 (S1-Clean-Sync).

---

## System

| Item | Value |
|---|---|
| OS | Windows 11 |
| Shell (Claude Code) | bash |
| Project path | `D:\02_Projects\velo` |
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
| Cannot push directly to production server | Staging deploy procedure (commands, host access, partner-coordination notes) lives in `SERVER-ACCESS.md` (gitignored; populated end of S1). The S1 deploy was performed jointly with the backend partner who handed over the procedure; from S2 onward we deploy independently per `SERVER-ACCESS.md`. Production promotion remains a separate manual step. |
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
- For Windows drive roots, `/d/02_Projects/velo/` style or `D:/02_Projects/velo/` both work in Git Bash.
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
- One cycle = one screen generation (one request = one screen, not batch-gen multiple screens in one prompt).
- One Claude Design project per product — VELO = one project with all screens + shared design system. See decisions.md #006.

### ProbeKit
- All skills invoked by name `/probekit-<skill>`. Lite profile runs automatically in Sprint-Closer Step 2.
- If a skill reports "not applicable" for current scope, record and skip.

---

## Test Infrastructure

### Staging server

Access details live in `docs/01_refer/SERVER-ACCESS.md` (gitignored). Deploy: push to `new_desing` → SSH to server → `velo update`. See SERVER-ACCESS.md for full procedure.

**Auth model (per decision #045):** SSH key (`~/.ssh/velo_staging_ed25519`, ed25519). Password retired to emergency-fallback. SSH config alias `velo-staging` available.

**Claude Code SSH method (per decision #044):** use `paramiko` (Python). Direct `ssh.exe` is sandboxed on Windows — does not work in Claude Code environment. Standard snippet:

```python
import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(
    hostname="37.1.204.171",
    username="root",
    key_filename="~/.ssh/velo_staging_ed25519",
)
stdin, stdout, stderr = client.exec_command("velo update")
out = stdout.read().decode()
err = stderr.read().decode()
exit_code = stdout.channel.recv_exit_status()
client.close()
print(f"exit={exit_code}\nstdout={out}\nstderr={err}")
```

Tested fallback chain (in order, use first that works in target env):
1. `paramiko` (pure Python, pip install) — primary, works in Claude Code sandbox
2. `plink -ssh -i key.ppk` — works but requires .ppk-format key (PuTTY conversion)
3. `ssh velo-staging` (OpenSSH alias) — works only outside Claude Code sandbox

### Telegram test bot

| Item | Value |
|------|-------|
| Bot | `@velo_testbot` |
| URL | https://t.me/velo_testbot |
| Auth flow | TMA `initData` via this bot |

### Test accounts

Telegram IDs registered with `@velo_testbot`. Source: `backend/scripts/test_telegram_send.py` (partner-owned).

| Telegram ID | Role | Purpose |
|------|------|---------|
| 526738615 | user (primary) | Primary visual testing — used by Human for per-cycle staging verification |
| 5130305756 | TBD | Additional dev/QA account |
| 5971989877 | TBD | Additional dev/QA account |
| 5478046601 | TBD | Additional dev/QA account |
| 7598677296 | TBD | Additional dev/QA account |

### Role switching

Backend partner can configure `role` (user / master / admin) per account on request. Used to test role-gated views without going through real master application flow.

To request: send Telegram ID + target role to partner.

---

## Anchor

```
[ENVIRONMENT.md | SPEC v3.2-velo]
Project environment — system, tools, git workflow, information map
Location: docs/01_refer/ENVIRONMENT.md
Referenced from: S{N}-SPRINT.md + loaded in every working chat
Update when: tools change, new pitfalls discovered, sprint close
```
