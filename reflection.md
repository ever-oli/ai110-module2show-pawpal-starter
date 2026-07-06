# PawPal+ Project Reflection

## 1. System Design

### a. Initial design

My initial UML (`diagrams/uml_draft.mmd`) modeled four classes with clear separation of concerns:

- **Task** — a single care activity with description, time, duration, frequency, priority, and completion status. Responsible for knowing how to mark itself complete.
- **Pet** — name, species, and a list of tasks. Responsible for adding and counting tasks belonging to that pet.
- **Owner** — manages multiple pets, can look up a pet by name, and exposes all tasks across the household.
- **Scheduler** — the planning layer: sort tasks, filter by pet or status, detect conflicts, mark tasks complete (with recurrence), and produce today's schedule.

The three core user actions I designed around were: **add a pet**, **schedule a task for a pet**, and **view today's sorted schedule**. Everything else (filtering, conflicts, persistence) extends those basics.

### b. Design changes

Yes — the design evolved during implementation.

The biggest change was giving **Task** a `due_date` field and a `next_occurrence()` method, and adding `save_to_json` / `load_from_json` to **Scheduler**. The draft UML treated recurrence as something the Scheduler would handle alone; in practice, having each Task know how to clone itself for the next day or week kept the recurrence logic localized and easier to test.

I also added `sort_by_priority()`, `format_schedule()`, and JSON persistence — extensions I chose up front — which expanded the Scheduler beyond the initial diagram. The final UML in `diagrams/uml_final.mmd` (and `diagrams/uml.mmd`) reflects what was actually built.

---

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and priorities

The scheduler considers:

| Constraint | How it's handled |
|---|---|
| **Time** | Tasks have an `HH:MM` start time; `sort_by_time()` orders chronologically |
| **Priority** | `low` / `medium` / `high`; `sort_by_priority()` ranks high first, then by time |
| **Completion status** | `filter_by_status()` hides or shows done tasks |
| **Pet ownership** | `filter_by_pet()` scopes the view to one animal |
| **Recurrence** | `frequency` of `daily` or `weekly` re-queues the next occurrence on completion |

**Priority mattered most** for the daily plan view — a missed medication is worse than a skipped play session — so `get_todays_schedule()` sorts by priority first, then time. Chronological order is still available when that's the more useful lens (e.g., the "Mark Complete" dropdown).

### b. Tradeoffs

**Tradeoff:** conflict detection only flags tasks that start at the **exact same time**, not tasks whose durations overlap (a 30-minute walk at 08:00 does not conflict with a 5-minute feeding at 08:15).

**Why it's reasonable:** for a household pet-care app at this scale, exact-time collisions are the most common real problem (two things scheduled for 08:00), and the warning is easy to understand. Full interval-overlap checking would need duration-aware logic, more edge cases, and harder-to-read warnings — worthwhile in a calendar product, but overkill here. I would improve this in a future iteration (see section 5b).

---

## 3. AI Collaboration

### a. How you used AI

I worked **mobile-only**, so Claude in the Claude app acted as my coding partner while I stayed in the **architect** role. The workflow:

1. Claude asked design questions (conflict strategy, extensions, demo data).
2. I answered with concrete decisions.
3. Claude implemented each phase — UML, logic layer, CLI demo, tests, Streamlit UI, CI, docs — and showed real terminal output from its sandbox.
4. I reviewed every file and committed through GitHub's mobile web editor.

The most helpful prompts were **structured and phased**: "design the four classes," then "implement sorting," then "wire Streamlit with session_state." Breaking the project into phases kept each interaction focused and mirrored the course's suggested workflow.

### b. Judgment and verification

I did not accept AI output blindly — several architect-level decisions were mine:

- **Exact-time conflict detection** instead of overlap checking (see tradeoff above).
- **Scheduler reads through Owner → Pet → Task** rather than storing its own task list, so there is one source of truth.
- **Which extensions to build:** priority scheduling, JSON save/load, and formatted CLI output.
- **Phased commits** so the git history reflects the actual build order, even though Claude generated most of the code.

I verified by reading each file before committing, running the CLI demo mentally against the spec, and relying on the **9-test pytest suite** plus **GitHub Actions** for automated proof on every push. Claude's sandbox couldn't install pytest (no internet), so CI became the authoritative test run — a good lesson in not trusting environment-limited AI verification alone.

---

## 4. Testing and Verification

### a. What you tested

Nine tests in `tests/test_pawpal.py` cover the behaviors that matter most:

- Task completion toggles `completed`
- Adding tasks increases a pet's task count
- Chronological sort returns correct time order
- Priority sort puts high-priority tasks first
- Completing a daily task creates tomorrow's occurrence with the right due date
- "Once" tasks do not recur
- Exact-time conflicts are detected; different times are not flagged
- JSON save/load round-trips the full household without data loss

These tests matter because they exercise the **scheduling logic** — the core of the project — independent of the Streamlit UI. If sorting, recurrence, or persistence break, the app looks fine but plans wrong tasks.

### b. Confidence

**Confidence: ⭐⭐⭐⭐ (4 out of 5)**

All nine tests pass locally and in CI. I'm confident the scheduler handles the designed behaviors correctly. The main gap is **overlapping-duration conflicts** — intentionally out of scope, so untested. If I had more time, I'd add tests for: weekly recurrence (+7 days), completing tasks across multiple pets, loading a corrupted or empty JSON file, and edge cases like midnight-crossing durations.

---

## 5. Reflection

### a. What went well

I'm most satisfied with the **scheduling logic** — priority-first ordering, chronological sort, conflict warnings, and daily/weekly recurrence all work together cleanly. The `Scheduler` reading through the Owner's pets rather than duplicating data kept the design simple, and seeing the CLI demo print a realistic household schedule (with a conflict banner at 08:00) made the logic feel real before the UI was even wired up.

### b. What you would improve

**Smarter conflict detection.** I'd extend `detect_conflicts()` to compare time *intervals* (start + duration) so a 30-minute walk at 08:00 properly warns about a feeding at 08:15. That would need interval math and clearer warning messages, but it would make the planner genuinely useful on busy mornings.

I'd also add task edit/delete in the Streamlit UI and filter the schedule by due date instead of assuming "today."

### c. Key takeaway

**Design-first (UML) makes implementation smoother.** Sketching classes and responsibilities before writing logic meant Claude and I agreed on the shape of the system early. When implementation details changed (like moving recurrence into `Task.next_occurrence()`), I could update the diagram and see exactly what shifted. Starting with design questions — not code — kept me in control as architect even while AI wrote most of the files.
