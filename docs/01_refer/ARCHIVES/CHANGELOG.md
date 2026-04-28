# Velo — Cleanup Changelog

> Per-sprint Clean-Sync transfers from active docs.
> Created: 2026-04-28 (S1-Clean-Sync first run).

---

## S1 Cleanup — 2026-04-28

### From BACKLOG.md (6 items transferred)

- **#19 — D3 decision clarification** — RESOLVED via decision #024 (S1 P02 OPEN ratification: Vue-SVG baseline + bundle PNG decorative supplement). Originally surfaced by Governance scout C09; resolved before Clean-Sync. Detail in `ARCHIVES/AUDIT/S1-AUDIT.md` §9.
- **#25 — user-ai-summary feature gap** — RESOLVED in C06b: status now known (backend `AISummaryResponse` exists in `generated.ts:18`; no frontend wrapper yet). Superseded by S2 C24 (frontend wrapper implementation). Categorized as bundle-greenfield in `ARCHIVES/AUDIT/S1-AUDIT.md` §4 + closure note in §10 #6.
- **#29 — IconRuble candidate for removal** — RESOLVED in S1-Clean-Sync Step 3 §B: 0 consumers confirmed via grep across `frontend/src/`; cross-confirmed by S1-AUDIT.md §9 (not in current view inventory). Action: deleted `frontend/src/components/icons/IconRuble.vue`; removed barrel export from `index.ts`. Velo backend operates in EUR.
- **#31 — ENVIRONMENT.md path drift `D:\03_Projects` → `D:\02_Projects`** — RESOLVED in S1-Clean-Sync Step 2 §A1 + §A2 (2 sites: §System Project path table row + §Shell Notes prose).
- **#35 — ENVIRONMENT.md commit convention cleanup** — RESOLVED in S1-Clean-Sync Step 2 §A3: dropped 2 `cycle:`-prefix rows from §Git Workflow Commit convention table (rows never used during S1; phase-bundled commit policy supersedes per Phase-Builder CLOSE Step 4f).
- **#36 — Staging deploy flow doc clarification** — RESOLVED in S1-Clean-Sync Step 2 §A4 + §B1 per variant (d) framing (Human-confirmed): pointer to `SERVER-ACCESS.md` as live source of truth; S1 partner-joint deploy noted; S2+ self-deploy transition noted; «auto-pulls» phrasing removed from both ENVIRONMENT.md and ARCHITECTURE.md.

### From ARCHITECTURE.md

- **§Key Decisions count drift** — `Active decisions #001-#025 as of Phase 03 close (2026-04-26)` updated to `Active decisions #001-#026 as of S1 close (2026-04-28)`. Sprint-Closer Step 1+ added #026 (ProbeKit hardened to Velo paths); ARCHITECTURE.md was not refreshed at sprint close. Updated in S1-Clean-Sync Step 3 §A.

### Stale Files Archived

- **`frontend/src/components/icons/IconRuble.vue`** — deleted in S1-Clean-Sync Step 3 §B per BACKLOG #29 + decision #024 (D3 ratification): Velo backend operates in EUR; 0 consumers verified. Barrel export line removed from `frontend/src/components/icons/index.ts`.

---
