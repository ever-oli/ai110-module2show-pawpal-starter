# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML (`diagrams/uml_draft.mmd`) had four classes: **Task** (a care activity with time, duration, frequency, and priority), **Pet** (name, species, and its task list), **Owner** (manages pets and exposes all household tasks), and **Scheduler** (sorts, filters, detects conflicts, handles recurrence, and builds today's plan). I designed around three core actions: add a pet, schedule a task, and view today's sorted schedule.

**b. Design changes**

Yes. The biggest change was adding `due_date` and `next_occurrence()` to **Task** instead of keeping all recurrence logic in the Scheduler — that made daily/weekly re-queuing easier to test. I also added JSON persistence and priority sorting, which expanded the Scheduler beyond the draft UML (see `diagrams/uml_final.mmd`).

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers time (`HH:MM` sorting), priority (high → low), completion status, pet ownership, and recurrence frequency. Priority mattered most for the daily plan — a missed med is worse than a skipped play session — so `get_todays_schedule()` sorts by priority first, then time.

**b. Tradeoffs**

Conflict detection only flags tasks at the **exact same start time**, not overlapping durations (a 30-min walk at 08:00 won't warn about a task at 08:15). That's reasonable for a simple household planner: exact-time collisions are the most common real problem and the warnings stay easy to read.

---

## 3. AI Collaboration

**a. How you used AI**

I worked mobile-only, so Claude acted as my coding partner while I stayed the architect — answering design questions, then reviewing each phase (UML, logic, tests, Streamlit, CI) before committing via GitHub mobile. The most helpful prompts were structured and phased ("design the four classes," then "implement sorting," then "wire session_state") instead of one big vague request.

**b. Judgment and verification**

I chose exact-time conflict detection over overlap checking, insisted the Scheduler read through Owner → Pet → Task (one source of truth), and picked which extensions to build (priority, JSON, CLI formatting). I verified by reading every file, checking the CLI demo output, and relying on the 9-test pytest suite plus GitHub Actions — since Claude's sandbox couldn't run pytest without internet, CI became the real proof.

---

## 4. Testing and Verification

**a. What you tested**

Nine tests cover task completion, chronological and priority sorting, daily recurrence, non-recurrence of "once" tasks, exact-time conflict detection, and JSON save/load round-trip. These matter because they test the scheduling logic itself, independent of the Streamlit UI.

**b. Confidence**

**⭐⭐⭐⭐ (4/5)** — all nine tests pass locally and in CI. The main gap is overlapping-duration conflicts, which I intentionally left out of scope. Next I'd test weekly recurrence (+7 days), corrupted JSON files, and tasks spanning midnight.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the scheduling logic — priority ordering, conflict warnings, and daily/weekly recurrence all work together cleanly, and the CLI demo made it feel real before the UI was wired up.

**b. What you would improve**

Smarter conflict detection using start time + duration intervals, plus task edit/delete in the UI and filtering by due date instead of assuming "today."

**c. Key takeaway**

Design-first (UML) made implementation smoother — agreeing on class responsibilities early meant changes like moving recurrence into `Task.next_occurrence()` were obvious and easy to track in the final diagram.
