# AICA-005 Theory-to-Lab Mapping

Classification is based on observed relevance during the actual
implementation of S001-S003 against PulseOps, not preference. Where the
benchmark provides no direct evidence either way, that is stated
explicitly rather than left implicit.

| Concept | Classification | Evidence |
|---|---|---|
| AI -> LLM -> Agent progression | APPENDIX | Never came up as a decision point while implementing any slice. Useful orientation before the lab, not needed during it. |
| Coding agent execution loop (read/edit/run/test/observe) | CORE | This is literally the loop I ran for every slice: read the slice spec and relevant files, edit code, run `make verify`, observe the output, repeat. Directly descriptive of lab behavior. |
| Task specification (Objective/Context/Scope/Constraints/Acceptance Criteria/Verification) | CORE | Every slice spec's "Relevant Context" section directly determined which files I read; "Constraints" directly prevented scope creep (e.g. S001's "do not add status logic" kept me from prematurely touching S002 territory). |
| Slices | CORE | The entire exercise is slicing. Without bounded slices, "implement PulseOps assignment/workflow/audit" would have been one unbounded task instead of three verifiable ones. |
| Token economics (context x steps x model x rework, as a mental model) | CORE, with a caveat | Real token/context telemetry is NOT_OBSERVABLE from this methodology (no live agent session was measured). However, the *behavioral* teaching - "budget attempts, not tokens" - is directly validated: real rework counts were 2, 1, and 2 across the three slices, matching the proposed "up to 2 repair iterations" heuristic. Keep the mental model in core theory; keep specific pricing/token arithmetic in appendix. |
| Context engineering / context boundaries | CORE | The "Relevant Context" list in each slice spec is what context engineering looks like in practice - it is the artifact, not an abstraction. Staying inside it was straightforward for all three slices; nothing required exploring outside the stated scope. |
| Project memory (general concept) | CORE | Validated directly by the context-kill exercise: a fresh clone with zero shared state was bootstrapped and verified successfully using only the repository's own files. |
| CLAUDE.md | CORE | Both S002 (lifecycle + P1 invariant) and S003 (atomicity note) relied on rules stated once in CLAUDE.md rather than re-derived per slice. Removing CLAUDE.md would have meant re-explaining these rules in every slice spec. |
| ACTIVE_SLICE.md | CORE | Load-bearing at every slice boundary - its "Current State/Handoff" section is what made the context-kill exercise's fresh clone legible without any conversation history. |
| Model selection | CORE (recommended), evidence-limited | This benchmark used one implementer (me) throughout, so it provides no comparative evidence about switching models mid-task. Recommend keeping the *concept* (use more reasoning where rework is expensive, e.g. S003's atomicity design) in core theory on first-principles grounds, but do not claim this benchmark validates it empirically. |
| Attempt budget | CORE | See "token economics" row - directly validated by real rework counts across all three slices, all within the proposed budget. |
| Verification (`make verify`, Generated != Done) | CORE - the strongest-evidenced concept in this entire benchmark | Every one of the 7 real failures recorded in the benchmark report (baseline mypy bug, S001 x2, S002 x1, S003 x2, plus the deliberately reintroduced atomicity regression) was caught by `make verify`, not by inspection or by an agent's self-report. This is the single most validated teaching point in the whole exercise. |
| Git checkpoints | CORE | Used at every slice boundary: `feature/S00N-*` branch, verify, `git merge --ff-only` into `main`. This lightweight workflow was sufficient for all three slices with no PR or CI at any point. |
| Permissions / safety boundaries (MAY/MUST/MUST NOT/MUST ASK) | CORE (recommended), evidence-limited | Never triggered during this benchmark - I never attempted a destructive operation or an out-of-scope change that the boundaries would have blocked. No direct evidence they changed a decision *in this run*, but they are cheap to keep and matter most exactly when something starts to go wrong, which a single clean implementer benchmark won't surface. Recommend keeping as core reference material (already embedded in CLAUDE.md) without expanding it into a dedicated lecture. |
| Skills | APPENDIX | None of the three slices needed a reusable, cross-cutting workflow - each was a one-off vertical slice. No evidence Skills would have helped here; may matter on a longer-running real project. |
| Subagents | REMOVE (from lab-relevant material) | No use case arose in any of the three slices. Unlike Skills, I see no plausible near-term relevance for a 3-slice workshop lab. Keep out of the core lab entirely; appendix-only if the presentation wants to mention it exists. |
| PR / CI | APPENDIX (confirmed) | Confirmed by actually not needing either at any point - branch -> verify -> fast-forward-merge was sufficient. Keep as instructor-demo or appendix material only, consistent with the slice's own stated preference. |
| Session hygiene / context-kill / CONTINUE-COMPACT-CLEAR-RESCOPE | CORE | Directly and literally exercised via the fresh-clone test. This is not a theoretical framework in PulseOps's case - it is a testable, tested proposition, and it held. |

## Summary for the presentation optimization pass

**Move to CORE if not already there:** the agent execution loop framed
concretely (read/edit/verify/observe, not abstractly), attempt budget
with the real observed numbers from this benchmark, and verification
framed around "the one thing that caught every real bug in this
benchmark" rather than as a generic best practice.

**Keep in APPENDIX:** AI/LLM/Agent taxonomy, detailed token/pricing
arithmetic, Skills syntax, model comparison detail, PR/CI mechanics.

**Consider REMOVE from lab-relevant core material entirely:**
subagents - zero evidence of relevance from this benchmark, and no
obvious path to relevance within a 3-slice, single-repository lab.

**Flag as evidence-limited, not evidence-contradicted:** model
selection and permissions/safety boundaries. Both are reasonable to
keep on first-principles grounds; neither was actually exercised by
this single-implementer benchmark, and that gap should not be papered
over.
