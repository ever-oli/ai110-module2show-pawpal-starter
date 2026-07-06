# 🐾 PawPal+

A smart pet care management system. PawPal+ tracks daily routines — feedings, walks, medications, appointments — and uses simple scheduling algorithms to organize and prioritize them for a busy pet owner.

Built with a **CLI-first workflow**: all logic lives in `pawpal_system.py`, verified through `main.py` and an automated pytest suite before being connected to the Streamlit UI in `app.py`.

## Architecture

Four classes, one source of truth:

- **`Task`** (dataclass) — a single activity: description, time (`HH:MM`), duration, frequency (`once`/`daily`/`weekly`), priority (`low`/`medium`/`high`), completion status, and due date. Knows how to produce its own `next_occurrence()`.
- **`Pet`** (dataclass) — name, species, and a list of Tasks.
- **`Owner`** — manages multiple Pets and exposes all their tasks.
- **`Scheduler`** — the "brain." It stores no tasks itself; it reads through Owner → Pets → Tasks so data can never get out of sync, and provides sorting, filtering, conflict detection, recurrence, and persistence.

UML diagrams: `diagrams/uml_draft.mmd` (initial design) and `diagrams/uml_final.mmd` (as built).

## Features

- Add pets and schedule care tasks for each one
- **Priority-based scheduling** — high-priority tasks surface first
- **Chronological sorting** of any task list
- **Filtering** by pet or by completion status
- **Conflict warnings** when two tasks share the same time
- **Recurring tasks** — completing a daily/weekly task auto-queues the next one
- **Persistence** — save and reload the whole household as JSON
- **Friendly CLI output** — emoji priority markers and aligned schedule tables

## Smarter Scheduling

| Feature | Method |
|---|---|
| Sort tasks chronologically | `Scheduler.sort_by_time()` — `sorted()` with a lambda key on the `HH:MM` string |
| Priority-first ordering | `Scheduler.sort_by_priority()` — sorts by priority rank, then time |
| Filter by completion status | `Scheduler.filter_by_status(completed)` |
| Filter by pet | `Scheduler.filter_by_pet(pet_name)` |
| Conflict detection | `Scheduler.detect_conflicts()` — flags exact same-time collisions and returns warning strings instead of crashing |
| Recurring tasks | `Scheduler.mark_task_complete()` + `Task.next_occurrence()` — daily tasks re-queue for `today + 1 day`, weekly for `+ 7 days`, using `timedelta` |

**Design tradeoff:** conflict detection only flags *exact* time matches, not overlapping durations (a 30-minute walk at 08:00 won't conflict with a task at 08:15). This keeps the algorithm simple and predictable at the cost of missing partial overlaps.

## Persistence

`Scheduler.save_to_json(filepath)` converts the Owner → Pets → Tasks tree into a dictionary (using `dataclasses.asdict` for tasks) and writes `data.json`. `Scheduler.load_from_json(filepath)` rebuilds the full object graph from that file. Files involved: `pawpal_system.py` (both methods) and `app.py` (Save/Load buttons in the sidebar).

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py
```

Run the CLI demo instead with:

```bash
python main.py
```

## Demo Walkthrough

**UI features (`app.py`):**
- **Sidebar** — set the owner name, add pets (name + species), and Save/Load the household to `data.json`
- **Schedule a Task** — pick a pet, describe the task, set time, duration, repeat frequency, and priority
- **Today's Schedule** — a table sorted by priority then time, with filters for pet and completed tasks
- **Conflict banners** — `st.warning` messages appear automatically when two tasks share a time
- **Mark Complete** — pick a task and complete it; recurring tasks show a success message with the next queued date

**Example workflow:** add a pet in the sidebar → schedule a "Morning walk" at 08:00 (high priority, daily) → schedule "Meds" at 08:00 → a conflict warning appears → mark the walk complete → tomorrow's walk is auto-queued → save to JSON.

**Sample CLI output** from `python main.py`:

```
📋 Today's Schedule for Ever
==============================================
07:30  🔴 Feed breakfast           Noodle (Tabby Cat) · 5 min · daily
08:00  🔴 Morning walk             Biscuit (Golden Retriever) · 30 min · daily
08:00  🔴 Heartworm meds           Biscuit (Golden Retriever) · 5 min · weekly
18:30  🟡 Evening walk             Biscuit (Golden Retriever) · 30 min · daily
20:00  🟡 Clean litter box         Noodle (Tabby Cat) · 10 min · daily
16:00  🟢 Laser pointer play       Noodle (Tabby Cat) · 15 min · once
----------------------------------------------
⚠️  Conflict at 08:00: 'Morning walk' (Biscuit) and 'Heartworm meds' (Biscuit)

🔎 Just Biscuit's tasks:
  18:30  Evening walk
  08:00  Morning walk
  08:00  Heartworm meds

✅ Completing 'Feed breakfast' (daily)...
   New occurrence created for 2026-07-04 at 07:30
   Noodle's task count is now 4

💾 Saved and reloaded: Ever has 2 pets and 7 tasks.
```

Note the priority-based ordering above: all 🔴 high-priority tasks come first (sorted by time within the group), then 🟡 medium, then 🟢 low — which is why 16:00 appears after 20:00.

## CLI Output Formatting

The schedule uses emoji priority markers (🔴 high / 🟡 medium / 🟢 low), aligned columns via f-string padding (`{task.description:<24}`), and divider lines — all implemented in `Scheduler.format_schedule()` with no external libraries.

## Testing PawPal+

Run the suite with:

```bash
python -m pytest
```

The 9 tests in `tests/test_pawpal.py` cover: task completion, task addition, chronological sort correctness, priority ordering, daily recurrence (new task due tomorrow), non-recurrence of "once" tasks, conflict detection for duplicate times, the no-conflict happy path, and a full JSON save/load round trip. Tests also run automatically on every push via GitHub Actions (`.github/workflows/tests.yml`).

```
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
collected 9 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 11%]
tests/test_pawpal.py::test_adding_task_increases_pet_count PASSED        [ 22%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 33%]
tests/test_pawpal.py::test_priority_sort_puts_high_first PASSED          [ 44%]
tests/test_pawpal.py::test_completing_daily_task_creates_tomorrow_occurrence PASSED [ 55%]
tests/test_pawpal.py::test_once_task_does_not_recur PASSED               [ 66%]
tests/test_pawpal.py::test_conflict_detected_for_duplicate_times PASSED  [ 77%]
tests/test_pawpal.py::test_no_conflict_for_different_times PASSED        [ 88%]
tests/test_pawpal.py::test_json_round_trip PASSED                        [100%]

============================== 9 passed in 0.02s ===============================
```

**Confidence Level:** ⭐⭐⭐⭐ (4/5) — all core behaviors are covered by passing tests; the main untested gap is overlapping-duration conflicts, which are out of scope by design.
