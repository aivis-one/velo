# Velo — Environment

> Loaded in every working chat. Bridge between framework rules and project reality.
> Updated: 2026-04-30 (S2-S3-Speedrun closure).

---

## System

| Item | Value |
|---|---|
| OS | Windows 11 |
| Shell (Claude Code) | bash |
| Project path | `D:\02_Projects\velo` |
| Prompt detail level | FULL |

Developer works on a single Windows laptop; Claude Code runs with bash as its shell. Prompts target bash syntax. PowerShell is not used.

**Windows + WSL2 setup note (added 2026-04-30 from S2 P05 C15)**: when setting up Velo on a fresh Windows 11 dev host, install the Ubuntu WSL distro **before** first Docker Desktop launch. Docker Desktop's default minimal `docker-desktop` distro does not mount `/mnt/c/...` and cannot clean up Linux-style Unix-socket files (`dockerInference`, `userAnalyticsOtlpHttp.sock`) when they end up on NTFS — they appear with corrupt `?????????` attributes from Win32 (cmd `del`, PowerShell `Remove-Item`, `chkdsk` all refuse to operate on them) and block engine boot indefinitely. **Mitigation**: with full Ubuntu WSL distro installed (`wsl --install -d Ubuntu --no-launch`), cleanup works through `/mnt/c/...` mount via `wsl -d Ubuntu -u root -e rm -f /mnt/c/Users/<user>/AppData/Local/Docker/run/<sock>`. Discovered during the first self-host docker bring-up (decision #046) when initial `docker compose up -d postgres redis app` hit cleanup issues across multiple recovery attempts. No-op on Mac/Linux dev hosts.

---

## Operator Role + Workflow Model

> Codifies who does what. Read at the start of every working chat.

### Three-actor model

| Actor | Role | Touch surface |
|---|---|---|
| **Claude Chat** (this assistant in claude.ai) | Plans, writes prompts, validates outputs, makes decisions | Markdown artifacts in `/mnt/user-data/outputs/` (later: chat clipboard) |
| **Claude Code** (CLI agent on operator's laptop) | Executes prompts: file edits, builds, tests, paramiko SSH, `velo *` commands, DB probes | Local repo + staging server via paramiko |
| **Operator** (human) | Relays prompts Chat→Code, types `proceed` at Server Action Plan pauses, performs visual verify in Telegram WebApp, answers business decisions | Telegram WebApp + chat reply box |

**Operator does NOT**: open terminals, type SSH commands, run `velo seed` / `velo update` / `psql` interactively, edit files, execute git commands. All of that is Claude Code's job, driven by Chat-issued prompts.

**Operator DOES**: copy-paste Chat's prompt artifacts into Claude Code, paste Code's output back into Chat, type `proceed` when Chat requests it, walk visual verify checklists in Telegram, answer "A/B/C" or yes/no questions Chat poses.

### Why this model

Operator is busy and prefers minimal context-switching. Terminal access is available but not preferred. Every workflow Chat issues should respect this:

1. **No "open terminal and run X" instructions** unless the operation is impossible via paramiko (genuinely interactive UIs that resist PTY-emulation, etc. — escalate to Chat decision before asking operator).
2. **No "type Y at the prompt" instructions** — Chat prompts Code to handle PTY interaction autonomously (`paramiko.invoke_shell()` + heuristic prompt detection or scripted input).
3. **No "ssh manually" instructions** — paramiko is the default; key path + alias in §Test Infrastructure → Staging server.
4. **No "edit this file in your editor" instructions** — Code uses Edit/str_replace/Write tools.
5. **No tool-installation instructions** — assume the toolchain in §Tools is already installed; if a new tool is needed, Chat issues an explicit Server Action Plan for installation first.

### Server Action Plan PAUSE protocol

Per Rule 28: any modifying server-side operation requires a Server Action Plan + PAUSE awaiting `proceed`. The operator's role at the PAUSE point:

1. Read Chat's plan output (what will be modified, expected outcome, failure modes, recovery)
2. If plan looks correct → reply `proceed` in Code's chat
3. If plan looks wrong → reply with concern, Chat reissues

The operator does NOT need to understand every line of code in the plan — just the high-level intent, expected outcome, and the specific failure modes the plan flags.

### Visual verify gates

Visual verify is the only point at which the operator interacts directly with the product. Format:
- Plain Markdown (`.md`) checklist artifact, **always in Russian** (operator's working language for product copy + UX),
- Per-view instructions: where to tap, what to look at, what's expected vs blocked,
- Empty checkboxes for operator to mark `✓ / ✗ / ~ / - / !`,
- Reply format: `A` / `B + items` / `C + items` short-hand triggers Hybrid policy routing.

Chat NEVER asks operator to "run velo seed manually" or "ssh and check X" inside a verify checklist — those operations are Code's job, performed before the checklist is delivered.

### Anti-patterns (Chat must avoid)

- "Open terminal → run `ssh velo-staging` → type `velo seed` → answer 526738615 three times" — Code does this via paramiko PTY; operator never sees terminal.
- "Run `git log` to confirm commit SHA" — Code reports SHA in completion signal; operator gets the SHA from Chat's summary.
- "Connect to the database and run `SELECT ...`" — Code does this via paramiko + psql one-shot; operator gets the result in plain text.
- "Install paramiko if not installed" — assumed installed per §Tools; if missing, Chat issues separate install Server Action Plan first.
- "Edit `frontend/src/views/admin/AdminFooView.vue` and change line 42 ..." — Code does the edit; operator never opens an editor.

### When operator is genuinely needed

Only these reasons should require operator action:

| Reason | Example |
|---|---|
| `proceed` relay at Server Action Plan PAUSE | "Plan looks correct, proceed" |
| Visual verify reply | `A clean` / `B: M6 — кнопка удаления не работает` |
| Business decision | "Do we ship MasterReview as degraded v1 or block on backend?" |
| Ambiguous spec clarification | "Should pending-verifications card show '0' or hide entirely?" |
| New protocol input | Loading framework / project / sprint files at chat boot |
| Manual partner coordination | When backend partner needs to be contacted out-of-band |

Anything else → Chat → Code, operator unaware.

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
| 526738615 | user (primary) → admin/master/user (post `velo seed` provisioning) | Primary visual testing — used by Human for per-cycle staging verification; `velo seed` provisions all 3 roles via paramiko PTY (highest-wins → ADMIN; admin always also master) |
| 5130305756 | TBD | Additional dev/QA account |
| 5971989877 | TBD | Additional dev/QA account |
| 5478046601 | TBD | Additional dev/QA account |
| 7598677296 | TBD | Additional dev/QA account |

### Role switching

**Primary path**: Claude Code runs `velo seed` via paramiko PTY (interactive command answered programmatically) — provisions admin/master/user roles on operator's chosen Telegram IDs without requiring operator terminal access. See §velo CLI commands → Seed row + Operator Role + Workflow Model section above.

**Fallback path**: If seed provisioning fails OR a specific role transition is needed that seed doesn't support, backend partner can configure `role` per account on request. To request: send Telegram ID + target role to partner via out-of-band channel.

**Per-session role switching within app**: TD-FE-ROLE-SWITCH frontend feature lets operator toggle between user/master/admin modes via profile screens (provided account has the role assigned). This is product-level navigation, not backend role mutation.

### velo CLI commands (staging)

Available on staging via paramiko `exec_command`. Modifying operations require Server Action Plan pause per Rule 28.

| Group | Commands |
|---|---|
| Service | `velo start` / `velo stop` / `velo restart [app]` / `velo status` |
| Logs | `velo logs [app\|db\|redis\|frontend\|all]` (default: app) |
| Test | `velo test` / `velo test backend` / `velo test frontend` / `velo lint` |
| Deploy | `velo update` (alias `velo deploy`) / `velo gen-types` |
| DB | `velo db connect` (alias `psql`) / `velo db dump` / `velo db restore <file>` / `velo db migrate` |
| Seed | `velo seed` (append fixtures) / `velo seed --reset` (destructive — wipe DB + re-seed; affects ALL test accounts including 526738615) |
| Maintenance | `velo backup` (DB + .env, 7-day rotation) / `velo ssl renew` / `velo ssl status` / `velo nginx reload` / `velo nginx status` / `velo version` |

**Cross-references:**
- `velo gen-types`: regenerates `frontend/src/api/generated.ts` from backend OpenAPI; second path to regen alongside partner-signal flow (decision #031) + frontend self-host fallback (decision #046).
- `velo db connect`: read-only inspection safe; modifying SQL requires Server Action Plan.
- `velo update`: known transient ("Uncommitted changes detected") fires on commits ≥600 LOC per BACKLOG #96 (hypothesis CONFIRMED 4/4 deploys post-MEGA-1); retry pattern via fresh paramiko session resolves.
- Demo data prep + role provisioning: `velo seed` appends fixtures DB-wide and provisions admin/master/user roles per interactive prompts. **Actual prompt structure** (verified 2026-05-04): 5 slots per role × 3 roles in order **Master → User → Admin** (15 slots total; empty newline at slot N terminates that role's loop early). Claude Code drives this via paramiko PTY (`invoke_shell()` + slot-aware heuristic regex `(Master|Admin|User)\s+(\d+)\s+Telegram\s*ID` + scripted input) — operator does NOT run interactively. Idempotent on repeat (existing accounts skipped per highest-wins rule). See §Operator Role + Workflow Model.

---

## Anchor

```
[ENVIRONMENT.md | SPEC v3.2-velo]
Project environment — system, tools, git workflow, information map
Location: docs/01_refer/ENVIRONMENT.md
Referenced from: S{N}-SPRINT.md + loaded in every working chat
Update when: tools change, new pitfalls discovered, sprint close
```
