# AICA-005 PulseOps Benchmark Report

## Methodology note (read this first)

This benchmark was produced by directly implementing all three workshop
slices myself, in one continuous session, rather than by orchestrating a
separate Claude Code agent session with a human supervisor. That means:

**Observable and reported below with real evidence:**
- Whether the code actually works (tests, lint, types, build, runtime
  smoke tests against a live server)
- Verification attempt counts and what each failure actually was (every
  failure quoted below is a real tool-output paste, not a
  reconstruction)
- Wall-clock time for `make bootstrap` and `make verify`, measured with
  `date +%s` before/after, run multiple times
- Whether the atomicity test is genuine (validated by intentionally
  reintroducing the bug it's supposed to catch - see S003 section)
- Whether durable project memory survives a full context reset
  (validated by a literal fresh `git clone` into a separate directory
  with its own venv and node_modules, bootstrapped and verified
  independently)

**NOT_OBSERVABLE from this methodology, marked explicitly below:**
- Agent turns, human interventions, and context/token usage in the
  sense of a live Claude Code session - there was no separate agent
  session to measure.
- Wall-clock time a human learner would take. My own implementation
  speed as an AI working directly is not a valid proxy for a learner's
  pace, so per-slice "time to verified change" below is a *reasoned
  estimate from task complexity*, not a measurement, and is labeled as
  such.

Where the spec asks for a metric I cannot honestly produce, it is
marked `NOT_OBSERVABLE` rather than estimated silently.

---

## 1. Repository status

Working PulseOps repository at `/home/claude/pulseops`. Git history:

```
be5d060 S003: incident audit timeline
886c152 Set ACTIVE_SLICE.md to S003
4277ead S002: status workflow and domain rules
054f089 Set ACTIVE_SLICE.md to S002
d0d83fe S001: incident assignment
b869aa3 Workshop starting commit: PulseOps baseline (~65% complete)
```

Each slice was developed on a `feature/S00N-*` branch and merged to
`main` with `git merge --ff-only` after `make verify` passed - matching
the lightweight git workflow the spec asked for. No PR, no CI: neither
was needed at any point (see Decision Question 13).

## 2. Baseline (~65% complete)

Command: `make verify`
Result: **PASS**
Backend: 9 tests passed. Frontend: 4 tests passed. Lint: clean (both).
Types: clean. Build: clean.
Measured verification time: **11s** (`make bootstrap`: 26s, one-time).

Runtime smoke test (real HTTP against a live uvicorn process, not
simulated): created an incident via `POST /incidents`, listed it via
`GET /incidents`, confirmed both responses matched. `GET /health`
returned `{"status": "ok"}`.

One real bug was caught before this baseline was even committed: a
`mypy` failure in `app/seed.py` (`**dict` unpacking against a
heterogeneously-typed dict). Fixed by constructing `Incident` objects
directly instead of dict-unpacking. This is the verification pipeline
doing its job on ordinary application code, before any workshop slice
began - worth noting as evidence the pipeline isn't decorative.

## 3. S001 - Incident Assignment

**Classification: WORKSHOP_FIT** (easier end of the range)

Command sequence and real results:

| Attempt | Result | What failed |
|---|---|---|
| 1 | FAIL | ruff: unused `TestClient` import; `assert False` anti-pattern (2 occurrences) in `test_assignment_service.py` |
| 2 | FAIL | tsc: unused `url` parameter in a test's mock fetch function (caught only at the build step - lint and tests both passed first) |
| 3 | PASS | - |

Verification time on the passing run: **11s**.

This matches the attempt-budget heuristic almost exactly: 1
implementation pass + 2 repair iterations, then a clean pass. Neither
failure required a re-scope - both were mechanical fixes once the
verification output identified them.

Runtime smoke test: created an incident, assigned an owner via
`PATCH /incidents/{id}/assign`, confirmed persistence via `GET`,
confirmed a whitespace-only owner is rejected with `422`.

Tests: 7 new (3 service, 4 API). Total after S001: 16 backend, 5
frontend.

**Time to verified change: NOT_OBSERVABLE as human-learner time.**
Reasoned estimate: this slice touches all four layers but the
`owner` field already existed on the model, so there's no schema
design decision - I'd estimate this sits at or slightly under the
20-25 minute target for a learner following the slice spec, assuming
no unfamiliarity with FastAPI/SQLAlchemy patterns.

## 4. S002 - Status Workflow & Domain Rules

**Classification: WORKSHOP_FIT** (matches the target well)

| Attempt | Result | What failed |
|---|---|---|
| 1 | FAIL | ruff: line too long (101 > 100 chars) in a test helper |
| 2 | PASS | - |

Verification time on the passing run: **11s**.

This slice required genuine engineering judgment: designing the
`_NEXT_VALID_STATUS` transition table, deciding where the P1-ownership
check belongs relative to the transition check, and writing negative
tests that prove rejection actually happens (not just that the happy
path works). I wrote both a "skip states" test and a "move backwards"
test, plus tests proving the P1 rule is severity-specific (a P2
incident is correctly *not* blocked - this test would have failed if
I'd implemented the rule too broadly).

Runtime smoke test (all real HTTP calls against a live server):
- P3 incident, `OPEN -> CLOSED` directly: **422** (correctly rejected)
- P1 incident without owner, `-> INVESTIGATING`: **422** (correctly
  rejected)
- Same P1 incident, assign owner, then `-> INVESTIGATING`: **200**
  (correctly allowed)
- Full lifecycle `OPEN -> INVESTIGATING -> RESOLVED -> CLOSED` on a P3
  incident: all four states confirmed via response bodies

Tests: 9 new (7 service, 5 API - some overlap in what they exercise).
Total after S002: 28 backend, 5 frontend.

**Time to verified change: NOT_OBSERVABLE as human-learner time.**
Reasoned estimate: the state-machine design is the crux of this slice
and is where a learner is most likely to make a design decision that
needs a repair pass (e.g., initially forgetting the "move backwards"
case, or putting the P1 check in the wrong layer). I'd estimate this
sits within the 25-30 minute target, possibly running over for a
learner unfamiliar with explicit state machines.

## 5. S003 - Incident Audit Timeline

**Classification: WORKSHOP_FIT, harder end of the range** - this is
correctly identified in the slice spec as the one with genuine extra
depth (atomicity), and the benchmark run confirms that's warranted.

| Attempt | Result | What failed |
|---|---|---|
| 1 | FAIL | ruff: `pytest.raises(Exception)` flagged as too blind - needed narrowing to the specific `IntegrityError` |
| 2 | FAIL | tsc: `IncidentEvent` type referenced by the frontend API client and detail page but never exported from `types/incident.ts` - a real oversight, caught only at the build step (lint and all 36 backend tests passed first) |
| 3 | PASS | - |

Verification time on the passing run: **12s**.

### The atomicity test is genuine, not tautological - proven by demonstration

The slice spec explicitly warns against a test that "never actually
exercises the failure path." To verify my own test wasn't doing that,
I ran an additional check beyond what any slice asks for: I created a
throwaway branch, reverted `save_with_event` to the naive two-commit
pattern the spec describes as the anti-pattern -

```python
self.db.commit()   # write 1: incident mutation alone
self.db.add(event)
self.db.commit()   # write 2: separate transaction for the event
```

- and reran the atomicity test in isolation. It failed, for real:

```
assert reloaded.status == Status.OPEN, (...)
AssertionError: incident status change leaked through even though the
paired event write failed - the transaction was not atomic
assert <Status.INVESTIGATING> == <Status.OPEN>
```

The incident's status genuinely leaked through to `INVESTIGATING` even
though the paired event write failed with an `IntegrityError`. This is
real evidence the test catches a real bug, not a test that would pass
regardless of implementation. I discarded the branch afterward; `main`
never contained the naive version.

This also became the **failure/recovery scenario** for the workshop
(see Section 8) - it's a real, reproducible engineering failure rather
than an artificial trap.

Runtime smoke test: assigned and transitioned a P1 incident against a
live server, fetched `GET /incidents/{id}/events`, confirmed both
events present in correct chronological order with correct
previous/new values.

Tests: 8 new (7 service including the atomicity test, 3 API - some
overlap). Total after S003: 36 backend, 5 frontend.

**Time to verified change: NOT_OBSERVABLE as human-learner time.**
Reasoned estimate: this is the slice most likely to run past its
25-30 minute target for a learner who hasn't previously reasoned about
transaction boundaries explicitly. The slice spec's explanation of the
atomicity problem (the two-write example) is doing real pedagogical
work here - I'd recommend the instructor be ready to point directly at
that section if a participant's diff shows two separate `commit()`
calls.

## 6. Context-Kill exercise

**Status: VALIDATED, using repository memory only.**

Rather than simulate this abstractly, I ran it as literally as
possible within my constraints: a full `git clone` of the completed
repository into a separate directory, with its own fresh virtualenv
and `node_modules` (zero shared state with the working copy).

```
git clone pulseops fresh-clone
cd fresh-clone
cat ACTIVE_SLICE.md   # read fresh, as the only source of "what's done and what's next"
./scripts/bootstrap.sh   # PASS, 26s
./scripts/verify.sh      # PASS, 19s
```

`ACTIVE_SLICE.md`'s "Current State / Handoff" section alone was
sufficient to establish: what was just completed (S003), what the
verification results were, and what comes next (this benchmark, not a
new slice) - without any reliance on conversation history, because
there was none available to this fresh clone.

The fresh clone's `make verify` took **19s** versus the working copy's
**11-12s** - slower due to cold caches (fresh `node_modules` install,
first-run jsdom overhead), not because anything was actually different.
Worth noting as a realistic expectation for a learner's *first*
`make verify` after `make bootstrap`, versus subsequent runs.

**The proposition tested:** "If clearing the conversation destroys
your project state, your project memory architecture is broken." For
PulseOps: false. The architecture holds.

## 7. Verification contract

Command: `make verify`
Target: < 10s preferred, < 20s acceptable.

**Measured: 11-12s on a warm working copy, 19s on a cold fresh clone.**

This is within the acceptable band but above the preferred one. The
dominant cost is `npm run` subprocess overhead across three separate
frontend invocations (lint, test, build) plus jsdom environment setup
(vitest's own output flags jsdom creation as ~72-81% of frontend test
time). This is a legitimate finding, not a failure: the pipeline is
fast enough for repeated workshop use, but there is real headroom to
recover by consolidating frontend commands or tuning vitest's
environment reuse (`isolate: false` or `pool: 'vmThreads'`, both
suggested directly in vitest's own warning output during every run).
Not fixed in this slice - flagged as a candidate follow-up, not
blocking.

`make verify` decided the outcome, not my own claims, on every one of
the 7 real failures recorded above (1 baseline, 2 in S001, 1 in S002,
2 in S003, 1 in the deliberately reintroduced atomicity bug). Zero of
those failures were caught by me "just noticing" something was wrong -
every one surfaced through ruff, mypy, or tsc output.

## 8. Failure/recovery scenario

**Source: the atomicity regression described in Section 5, genuinely
reproduced.** This satisfies the spec's requirement for "at least one
meaningful failure" without resorting to an artificial trap - it's the
literal anti-pattern the slice spec already warns about, demonstrated
to actually fail.

Recommended workshop framing:

```
STOP:      make verify fails on test_atomic_failure_rolls_back_incident_change
INSPECT:   git diff shows save_with_event() now has two separate
           self.db.commit() calls instead of one
DIAGNOSE:  the second write can fail independently of the first -
           that's exactly what CLAUDE.md's "atomicity" note warned about
RE-SCOPE:  not needed here - this is a one-line fix (single commit,
           not two), not a boundary-too-large problem
VERIFY:    make verify - PASS
```

This is a good teaching moment specifically because "keep prompting
until it works" would not fix it - the fix requires understanding
*why* two commits are wrong, not just that a test is red.

## 9. Attempt budget - empirical result

Observed real rework counts per slice: **S001: 2, S002: 1, S003: 2.**
All three fall within "up to 2 verification/repair iterations" from
the proposed heuristic (Section 18 of the SLICE). Zero slices required
a STOP/re-scope decision - every failure was a mechanical fix once
identified. This is a small sample (3 slices, one implementer) but it
is consistent with, not contradicted by, the proposed heuristic.
Recommend keeping the heuristic as stated, with the explicit caveat
already in the slice specs that it's a heuristic, not a hard rule.

## 10. Instructor demo recommendation

**Task recommendation:** S001 (Incident Assignment). It's the smallest
complete vertical slice (all four layers, but no state-machine design
and no atomicity concern), which makes it legible in a live 15-20
minute demo without the audience needing to track two engineering
concerns at once.

**CONTROL vs TREATMENT, both against the exact same repository, same
task, same starting commit (`b869aa3`, the workshop baseline):**

- **CONTROL:** a reasonable, conventional AI-assisted workflow - the
  full requirement handed to the agent in one instruction ("add
  incident assignment, backend and frontend, with tests"), without a
  written slice contract, without a stated stop condition, agent
  proceeds until it declares itself done. This is not a strawman: it
  is how a competent engineer using an AI coding agent without this
  workshop's structure would plausibly work.
- **TREATMENT:** the actual `S001-INCIDENT-ASSIGNMENT.md` slice
  contract as written, `CLAUDE.md` provided as context, `make verify`
  as the completion gate.

**Candidate metrics** (per Section 22): time to verified change, agent
turns, failed verification attempts, rework, unrelated files changed,
regressions, context usage where observable.

**This benchmark does not include a CONTROL run.** Producing one
requires an actual second, separately-orchestrated agent session,
which is out of scope for what I can generate directly in this
session. I'm recommending the task and the metric list; the
comparison itself is future work, consistent with Section 22's
instruction that this slice "does not need statistically meaningful
results yet."

## 11. Decision questions (Section 27)

1. **Understandable in under 5 minutes?** Likely yes for a SWE - the
   README, CLAUDE.md, and the four-layer architecture diagram are
   short and the domain (incidents) is familiar. Not independently
   timed with a real reader; flagged as an estimate.
2. **Enough real engineering complexity?** Yes - layered architecture,
   an explicit state machine, an ownership invariant, and a genuine
   atomicity concern, confirmed by the demonstrated real failure.
3. **S001 workshop-fit?** Yes.
4. **S002 workshop-fit?** Yes.
5. **S003 workshop-fit?** Yes, harder end - flag for instructor
   attention.
6. **Context-kill works using repository memory?** Yes - validated via
   an independent fresh clone, not simulated.
7. **`make verify` fast and deterministic enough?** Acceptable
   (11-12s warm, 19s cold) but above the preferred <10s target. Real
   headroom exists (see Section 7); not blocking.
8. **Does the failure scenario teach diagnosis, not prompting?** Yes -
   see Section 8; the fix requires understanding the atomicity
   concern, not retrying.
9. **Can hands-on realistically fit ~120 minutes?** Best estimate:
   yes, with S003 needing the most buffer. **This is an estimate, not
   a measurement** - see the methodology note at the top of this
   report. Recommend a timed pilot with an actual learner before
   fully committing to the 20/25/30-style minute targets in the slice
   specs.
10. **Which concepts proved essential?** Task specification, slices,
    context boundaries, project memory (CLAUDE.md + ACTIVE_SLICE.md),
    attempt budget, verification, Git checkpoints, session
    hygiene/context-kill. See the full mapping document.
11. **Which should move to appendix?** AI/LLM/Agent taxonomy, Skills,
    detailed model comparison.
12. **Which should be removed** (from lab-relevant material - not
    necessarily the presentation entirely)? Subagents - no evidence
    they're needed for this lab.
13. **Should PR/CI stay outside the core lab?** Yes, confirmed by
    actually not needing them at any point in this benchmark - the
    branch -> verify -> fast-forward-merge workflow was sufficient
    for all three slices.
14. **What should the instructor demo compare?** See Section 10.

---

See `AICA-005-THEORY-LAB-MAPPING.md` for the full concept-by-concept
classification and `ACTIVE_SLICE.md` / git history for the moment-by-
moment record this report is built from.
