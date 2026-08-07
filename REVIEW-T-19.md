# REVIEW T-19 — order coupling after the class-2 sweep

**Verdict: the T-19 delivery is not guilty. H1 and H2 are refuted, H3 is confirmed
in a stronger form than stated.** The two failures are a pre-existing defect in
`tests/test_admin_stats_overview.py`; `pytest-randomly` only exposes it. The
"base is green on the same seed" observation is a run-history artifact, not
evidence about the diff.

Reproduced locally on a real Postgres 16 + Redis, Python 3.12, with
`pytest-randomly` installed only in the throwaway venv (nothing added to
`pyproject.toml`, nothing changed in prod code).

---

## 1. What actually fails

The brief reads the pytest repr as "actual count is higher than expected". It is
the opposite — the count does not move at all:

```
>       assert resp.json()["new_users"] - base["new_users"] == 2
E       assert (239 - 239) == 2
```

Two users are registered between the two `GET /admin/stats/overview` calls (the
log shows `user_upserted telegram_id=94010` and `=94011`), and `new_users` stays
put. The delta is **0, not >2**. That inversion is what sends H1/H2 down the
wrong path: nothing is leaking *in*, something is failing to be *created*.

The two failures are also not two defects but one. In `test_new_masters_counts`
the `new_masters` assert (`:365`) **passes** — it is the `new_users` line right
after it that fails:

```
        assert body["new_masters"] - base["new_masters"] == 1     # passes
>       assert body["new_users"] - base["new_users"] == 1
E       assert (16 - 16) == 1
```

Both reported failures are the same single assertion: `new_users` does not move.

## 2. Guilty position

| | |
|---|---|
| **Defect** | `tests/test_admin_stats_overview.py:70` |
| **Failing asserts** | `tests/test_admin_stats_overview.py:348`, `:365`, `:367` |
| **Counterparty** | `tests/test_admin_practices.py:69-73` |

`tests/test_admin_stats_overview.py:70`

```python
await full_cleanup_range(session, _TID_MIN, _TID_MAX, delete_users=False)
```

`_TID_MIN/_TID_MAX` are `94000/94999` (`:51-52`). With `delete_users=False`,
`full_cleanup_range` takes the role-reset branch (`tests/helpers.py:423-428`) and
**the user rows survive the file**. `tests/test_admin_practices.py` declares the
*identical* band `94000-94999` (`:36-37`) and its autouse cleanup **hard-deletes**
them (`:69-73`).

Neither file is in the T-19 delivery. `test_admin_practices.py` was never touched
by the sweep; `test_admin_stats_overview.py` is explicitly listed as untouched
(brief §5) and I confirmed it — the commit's file list contains neither.

## 3. Mechanism

Three facts compose:

1. **`login_user` is an upsert, not an insert.** `app/modules/auth/service.py:260-300`
   is `pg_insert(User).on_conflict_do_update(index_elements=["telegram_id"], set_={...})`.
   `created_at` is **not** in `set_` — a returning user keeps their original
   `created_at` and no new row appears.
2. **`new_users` counts by `created_at`.** `app/modules/admin/stats/overview_service.py:95-98`:
   `WHERE created_at >= start AND created_at < end`.
3. **The band is never emptied by the file itself** (§2).

So `test_new_users_counts` silently assumes telegram_ids 94010/94011 do not yet
exist. If they do — from any earlier run, or from any earlier test in the same
session — the two `login_user` calls are UPDATEs, `new_users` does not move, and
`assert delta == 2` fails. Same for `test_new_masters_counts` with 94800
(`:367`, the `new_users` half of the assert; `new_masters` alone would still pass,
since cleanup resets the role and `_make_master` re-sets it).

The band only gets emptied by **`test_admin_practices.py`**. That gives the
ordering rule:

> `test_admin_stats_overview` is green iff `test_admin_practices` ran between the
> last population of the 94xxx band and this test.

In the default order that is free: `test_admin_practices.py` sorts alphabetically
**before** `test_admin_stats_overview.py`, so it always wipes the band first. The
suite has been leaning on collection order for its cleanup. At seed `375403175`
the order inverts — stats-overview lands at collection index **621-632**,
practices at **856-865** — and the leftovers from the previous run survive into
the assertion.

## 4. Evidence

### 4a. It is not the diff — controlled A/B, identical precondition

Same DB reset, same priming step (run the stats file once to populate the band),
same seed. Only the tests tree differs:

| Build | Result at seed 375403175 |
|---|---|
| **Delivery** (`0343341`) | `2 failed, 991 passed, 3 skipped` |
| **Base** (`6187c1e7` tests) | `2 failed, 991 passed, 3 skipped` |

Identical failures, identical two test ids. The base is **not** green on this seed
once the precondition is held constant.

### 4b. Why the brief saw "base green, delivery red"

The DB is stateful across runs and the stats file never deletes its users, so
`git stash → run → unstash → run` does not hold the precondition constant — each
run mutates the state the next one starts from. Confirmed both directions:

- **Clean DB, delivery, seed 375403175 → `993 passed, 3 skipped`.** The seed alone
  reproduces nothing.
- Re-running the same build at the same seed on the carried-over DB is *also*
  green, because at this seed practices (index 856) runs after stats and leaves
  the band empty for the next run.

The red/green flip tracks what the *previous* run left in the 94xxx band, not
which tests tree is checked out.

### 4b-bis. The seed is not the variable — an 8-seed sweep

Eight seeds run back-to-back on a carried-over DB, delivery tree throughout,
which is what the executor's shared VPS database actually looks like:

| seed | result |
|---|---|
| 375403175 | 993 passed *(clean DB)* |
| 1 | 993 passed |
| **42** | **2 failed**, 991 passed |
| 12345 | 993 passed |
| 999 | 993 passed |
| 777777 | 993 passed |
| 20260807 | 993 passed |
| **5150** | **2 failed**, 991 passed |

Two failing seeds out of the batch — the brief's own "2 of 5" rate, and always
the same two test ids. Note the reported seed `375403175` passes here and seed
`42` fails, which is the reverse of the brief. The seed is not the variable.

Driven home by re-running seed **42** on its own afterwards, with nothing changed
but the incoming band state:

```
band users now: 0
993 passed, 3 skipped
```

Same seed, same tests tree, same everything — red in the sweep, green now, because
the run before it happened to leave the band empty. A seed does not carry a
verdict in this suite; the state it inherits does.

Re-priming the band and running seed 42 once more turns it red again and prints
the brief's own number:

```
band users left: 16
E       assert (386 - 386) == 1
E       assert (386 - 386) == 2
FAILED tests/test_admin_stats_overview.py::test_new_users_counts - assert (38...
```

The `assert (38...` quoted in the brief is the **truncated one-line summary** of
`assert (386 - 386) == 2`. It was read as "actual 38 against an expected 2"; it is
386 minus 386, i.e. a delta of zero. That single misreading is what pointed the
investigation at leakage (H1/H2) instead of at a count that never moved.

### 4c. Minimal reproducer — no `pytest-randomly` involved

After priming the band once, ordering alone decides it. Runs in ~3 seconds:

```bash
# prime: leaves 16 users in the 94xxx band
pytest tests/test_admin_stats_overview.py -p no:randomly

# stats BEFORE practices  -> 2 failed, 20 passed
pytest tests/test_admin_stats_overview.py tests/test_admin_practices.py -p no:randomly

# practices BEFORE stats  -> 22 passed
pytest tests/test_admin_practices.py tests/test_admin_stats_overview.py -p no:randomly
```

`pytest-randomly` is not a participant in the defect. It is a coin that happens to
land on the bad order.

## 5. Verdict on H1 / H2 / H3

**H1 (removed `refresh()` held the order of side-effects) — refuted.**
Two independent kills. Empirically, the base fails identically with every removed
`refresh()` back in place (§4a). Structurally, the diff removes *only reads*:

```
29  await db_session.execute(       # reads
13  await db_session.refresh(...)   # reads
10  profile = await db_session.get(...)
 …  import lines
```

Grepping the removed lines for `commit(|flush(|.add(|add_all(|delete(|update(|insert(`
returns **nothing**. A read cannot change what is committed, so it cannot change
what any autouse cleanup sees. The premise "refresh synchronised the fixture
session so its cleanup deleted more rows" does not survive contact with
`full_cleanup_range`, which opens with an unconditional `session.rollback()`
(`tests/helpers.py:217`) and deletes by `telegram_id` range via subquery — never
via the identity map.

**H2 (fixture-session read as an identity-map "anchor" for cascading cleanup) — refuted.**
Same structural argument. `full_cleanup_range` issues bulk `DELETE ... WHERE
telegram_id BETWEEN` statements; nothing in it is driven by session-resident
objects, so no read anywhere can widen or narrow its reach. `fresh_get` /
`fresh_execute` are additionally read-only by construction — `async with
factory() as s` around a single `get`/`execute`, no commit — so they cannot alter
committed state for anyone.

**H3 (the stats test counts without isolation) — confirmed, and sharper.**
The brief's reservation ("H3 explains 'base green on the same seed' worst of all")
dissolves once §4b removes that fact from the table: the base is *not* green on
that seed under a held precondition. The refinement to H3 is that the defect is
not "no filter by its own band" in general — the file does capture a baseline and
assert a delta, which correctly neutralises foreign seed data. The defect is
narrower and entirely local: **the delta is only meaningful if the fixture's own
users are new, and the file's cleanup guarantees they are not.**

## 6. The other 79 positions — same-class sweep

**No further instances.** Two passes:

**Structural.** The sweep cannot produce this class of defect at all. `fresh_get`
and `fresh_execute` (`tests/helpers.py`) open a session, run one read, and close
without committing; the diff removes no write, no commit and no flush (§5). Row
*visibility* for a foreign autouse cleanup is a function of committed state only,
and the delivery does not touch committed state.

**Empirical.** I audited every test file for the actual risk pattern — a file that
asserts on counts of newly-created entities while its own cleanup keeps users
alive:

```
test_admin_metrics.py         band=92000-92999   hard-deletes users: True
test_admin_stats.py           band=57000-57999   hard-deletes users: True
test_admin_stats_overview.py  band=94000-94999   hard-deletes users: False   <-- unique
```

`test_admin_stats_overview.py` is the only file in the suite that asserts on
`new_users`/`new_masters` at all, and the only one of the three counting files that
keeps its users. The other two already do the right thing — and
`full_cleanup_range`'s own docstring names the rule: *"`delete_users`: Use for
tests that count absolute user totals (e.g. test_admin_stats)."* This file missed
that memo.

For completeness, 31 telegram_id band overlaps exist across the suite (full list
reproducible from the audit script). They are latent order couplings of a related
shape, but none of the other 30 pairs combines an overlap with a
newly-created-entity count, so none can fail this way today.

## 7. Recommendation

**Nothing to roll back in T-19.** The delivery is clean on this finding; ship it.
The `MissingGreenlet` result stands independently.

**File a separate наряд against `tests/test_admin_stats_overview.py`.** The
one-line form:

```python
# tests/test_admin_stats_overview.py:70
await full_cleanup_range(session, _TID_MIN, _TID_MAX, delete_users=True)
```

This matches what its two sibling counting files already do, and makes the file
self-sufficient instead of dependent on `test_admin_practices.py` running first.
I validated it on a scratch database and then reverted it — with the flag flipped,
the priming step leaves **0** users in the 94xxx band instead of 16, and the
previously-red order goes green:

```
pytest tests/test_admin_stats_overview.py tests/test_admin_practices.py -p no:randomly
#   before: 2 failed, 20 passed
#   after:  22 passed
```

Worth pairing with a comment naming the reason, because the coupling is invisible:
the ids the assertions depend on being new are 94010/94011 (`:343-344`) and 94800
(`:360`), and the band is shared with `test_admin_practices.py`.

Two things worth raising with the наряд, out of scope here:

- **The band collision itself.** Two unrelated files owning `94000-94999` with
  opposite cleanup policies is the root condition; giving stats-overview its own
  sub-band would remove the coupling even without the flag change.
- **The suite leans on alphabetical collection order for cleanup.** That is the
  general lesson from this seed, and it is what the remaining 30 band overlaps are
  sitting on. Not urgent — none of them can fail today — but it is why a random
  order found this and the default order never will.

---

### Appendix — how to reproduce

```bash
# throwaway venv; pytest-randomly stays OUT of pyproject.toml
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python <pyproject deps> pytest-randomly
# local Postgres 16 on :5433 + Redis on :6379
export DATABASE_URL="postgresql+asyncpg://velo:velo@127.0.0.1:5433/velo"
export REDIS_URL="redis://localhost:6379/0"

# clean DB -> green, the seed alone proves nothing
pytest -p randomly --randomly-seed=375403175 -q          # 993 passed

# prime the band, then the same seed -> the reported pair, on EITHER tests tree
pytest tests/test_admin_stats_overview.py -p no:randomly
pytest -p randomly --randomly-seed=375403175 -q          # 2 failed, 991 passed
```

Scope kept: no prod-code change, no `pyproject.toml` change, no test fix applied.
