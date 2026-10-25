# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Implementation Summary

PawPal+'s domain model lives in `pawpal_system.py` and is exercised by the demo script in `main.py`. The classes work together like this:

- **`Owner`** holds the pet owner's name, available minutes for the day, free-form preferences, and the list of `Pet` objects they're responsible for (`add_pet`, `get_pets`).
- **`Pet`** belongs to an `Owner` and keeps its own list of `Task` objects (`add_task`, `remove_task`, `get_tasks`). Adding a task sets a back-reference from the task to its pet.
- **`Task`** is a single care item (walk, feeding, medication, etc.) with a duration, `Priority`, optional preferred time, and a `done` flag toggled by `mark_done()`.
- **`DailyPlan`** ties everything together: `generate(pet, owner)` sorts a pet's tasks by priority (`_sort_by_priority`), then greedily schedules each task if it fits in the owner's remaining minutes (`_fits_in_time`), recording a reason for every decision via `add_task`/`skip_task`. `get_total_minutes()` and `explain()` then report the resulting schedule and the reasoning behind it in plain language.
- `HealthCondition`, `TaskType`, and `Priority` are enums that constrain the valid values for pet health, task category, and task importance.

In short: an `Owner` has `Pet`s, each `Pet` has `Task`s, and a `DailyPlan` consumes a pet's tasks plus the owner's available time to produce a prioritized, explainable schedule. `main.py` demonstrates this end-to-end by building an owner, two pets, and a few tasks, then printing a simple sorted schedule. Unit tests in `tests/test_pawpal.py` cover the core `Task`/`Pet` behaviors (`mark_done`, `add_task`).

Beyond the priority-first greedy scheduling described above, `pawpal_system.py` also implements status filtering, conflict detection, and daily/weekly recurrence, all wired up to the Streamlit UI in `app.py` — see the "✨ Features" and "📐 Smarter Scheduling" sections below for details.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

> **Current status:** All steps are done — see [Implementation Summary](#implementation-summary) above. `main.py` is a CLI demo of the domain model; `app.py` is the Streamlit UI (step 6), wired directly to `pawpal_system.py`.

## 🖥️ Sample Output

Output of `python main.py`:

```
Today's Schedule
=================
07:00  Rex         Morning Walk (30 min, priority: HIGH)
08:00  Rex         Feeding (15 min, priority: HIGH)
18:30  Whiskers    Medication (10 min, priority: MEDIUM)
```

## 🧪 Testing PawPal+

sample test output:

```bash
====================================== test session starts =======================================
platform darwin -- Python 3.14.6, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/jeanmariengabonziza/CodePath/ai110-module2show-pawpal-starter
collected 2 items                                                                            

tests/test_pawpal.py ..                                                                    [100%]

======================================= 2 passed in 0.01s ========================================
```

## 📐 Smarter Scheduling

The behaviors below live in `pawpal_system.py` (wired up to the UI in `app.py`), which extends the base domain model with priority-aware filtering, conflict detection, and recurrence.

| Feature            | Method(s)                                               | Notes                                                                                                                                             |
| ------------------ | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sorting behavior   | `DailyPlan._sort_by_priority`                           | Maps each `Priority` to a rank (HIGH=0 … LOW=2) and runs a stable sort over a pet's tasks, so same-priority tasks keep their original order before scheduling. |
| Filtering behavior | `Pet.get_tasks_by_status`, `DailyPlan._fits_in_time`    | `get_tasks_by_status(done)` filters a pet's tasks by completion state in one O(n) pass. During scheduling, `_fits_in_time` filters which sorted tasks are greedily accepted into `scheduled_tasks` vs. `skipped_tasks` based on the owner's remaining minutes. |
| Conflict detection | `DailyPlan.detect_conflicts`                            | After scheduling, groups the scheduled tasks by `preferred_time` in a single O(n) pass and emits a warning string for any time slot with more than one task — surfaced via `DailyPlan.explain()`. |
| Recurring tasks    | `Task.mark_done`, `Task._next_occurrence`, `RecurrenceInterval` | `mark_done()` checks the task's `RecurrenceInterval` (`DAILY`/`WEEKLY`); if it recurs, it calls `_next_occurrence()` to build and attach the next `Task` instance, with `due_date` advanced by `RecurrenceInterval.days`. |

## ✨ Features

PawPal+'s scheduling logic (`pawpal_system.py`) is built from a handful of small, focused algorithms:

- **Priority-based sorting** — `DailyPlan._sort_by_priority` maps each `Priority` (HIGH/MEDIUM/LOW) to a numeric rank and runs a stable sort (Timsort, O(n log n)) over a pet's tasks, so higher-priority tasks are always scheduled first and same-priority tasks keep their original order.
- **Greedy time-boxed scheduling** — `DailyPlan.generate` walks the priority-sorted task list and uses `_fits_in_time` to greedily accept each task into `scheduled_tasks` while it still fits in the owner's remaining minutes, otherwise moving it to `skipped_tasks`. This guarantees higher-priority tasks get first claim on available time.
- **Status filtering** — `Pet.get_tasks_by_status(done)` does a single O(n) pass to split a pet's tasks into pending vs. completed, used by both the UI's "Show: All/Pending/Done" filter and the CLI demo.
- **Conflict detection** — `DailyPlan.detect_conflicts` groups tasks by `preferred_time` in one O(n) pass and flags any time slot with more than one task (within a pet, or across every pet an owner has) as a warning string, surfaced in `DailyPlan.explain()`.
- **Daily/weekly recurrence** — `Task.mark_done()` checks the task's `RecurrenceInterval`; if it recurs, `_next_occurrence()` clones the task with its `due_date` advanced by the interval's day count (1 for DAILY, 7 for WEEKLY) and attaches it to the same pet automatically.
- **Explainable output** — `DailyPlan.explain()` renders scheduled, skipped, and conflicting tasks together with the owner-supplied reason for each task's priority level, so every scheduling decision is traceable back to a reason.
- **Multi-pet support** — `Owner.get_pets()` is the single source of truth for an owner's pets; the UI keeps only the *currently selected* pet's id in session state, so each `Pet` is a distinct object with its own name, species, health condition, and task list. Editing one pet's name or adding tasks never touches another pet's data.

## 📸 Demo Walkthrough

### Main UI features

The Streamlit app (`app.py`, wired directly to `pawpal_system.py`) lets a user:

- Edit the owner's name and available minutes for the day.
- Pick which pet is "current" from a **pet selector**, and add new pets on the fly via the "➕ Add a new pet" expander — each pet keeps its own name, species, health condition, and task list, independent of every other pet.
- Edit the current pet's name, species, and health condition without affecting any other pet.
- Add a task to the current pet with a title, type, duration, priority, preferred time, and recurrence (none/daily/weekly), plus a free-text reason for why that priority level matters (stored per priority and reused as the schedule's reasoning).
- Filter the current pet's task list by status ("All" / "Pending" / "Done"), always shown sorted by priority (High → Low).
- Generate a schedule for the current pet, which shows scheduled vs. skipped task counts, total minutes scheduled, any conflict warnings, and a full scheduled/skipped table (with a **Pet** column so it's clear which pet each row belongs to) alongside each task's reason.
- Check off tasks as done directly in the schedule table — completing a recurring task automatically spawns its next occurrence.

### Example workflow

1. Add a pet ("Rex", a healthy dog) via the pet selector's "➕ Add a new pet" expander.
2. Add a few tasks for Rex: a high-priority Morning Walk at 07:00, a high-priority Feeding at 08:00, a medium-priority Medication at 18:30 (daily), and a low-priority Grooming (weekly).
3. Add a second pet ("Whiskers", a senior cat) and switch to it with the pet selector — notice Rex's name, species, and tasks are untouched.
4. Switch back to Rex and click "Generate schedule" to produce a `DailyPlan` for Rex against the owner's available minutes.
5. Review today's schedule: scheduled tasks are listed highest-priority first (with the **Pet** column confirming they're Rex's), skipped tasks show why they didn't fit, and any double-booked time slots are flagged as conflicts.
6. Mark the Morning Walk and Medication done — since both recur, tomorrow's instances appear automatically in the pending list.

### Key Scheduler behaviors shown

- **Sorting by priority** — HIGH tasks (Morning Walk, Feeding) are scheduled before MEDIUM (Medication) and LOW (Grooming, Brushing) tasks.
- **Greedy time-fit skipping** — once the owner's available minutes run out, remaining low-priority tasks (e.g. Brushing) are skipped rather than scheduled.
- **Conflict warnings** — two tasks on the same pet sharing a `preferred_time` (Morning Walk/Feeding clashing with Brushing at 08:00, or Medication recurring onto the same slot) are flagged, and the same check runs across an owner's *other* pets too (Rex's Feeding/Brushing conflicting with Whiskers' Vet Checkup, both at 08:00) — the schedule table's **Pet** column makes it immediately clear which pet each conflicting task belongs to.
- **Daily recurrence** — completing Morning Walk and Medication (both `DAILY`) spawns next-day instances with `due_date` advanced by one day.

### Sample CLI output

`python main.py` builds an owner with two pets (Rex, Whiskers), adds several tasks — including two that are deliberately scheduled for the same time slot to trigger conflict warnings — marks a few done to exercise recurrence, then prints the sorted tasks, completed/pending lists, the generated `DailyPlan` (with conflicts), and a cross-pet conflict check:

```
Today's Schedule (sorted by priority)
======================================
HIGH    Morning Walk   id=t1           due=2026-10-25
HIGH    Feeding        id=t2           due=None
HIGH    Morning Walk   id=t1-2026-10-26 due=2026-10-26
MEDIUM  Medication     id=t3           due=2026-10-25
MEDIUM  Medication     id=t3-2026-10-26 due=2026-10-26
LOW     Grooming       id=t4           due=2026-10-25
LOW     Brushing       id=t6           due=None

Completed tasks
================
  Medication (id=t3)
  Morning Walk (id=t1)
  Feeding (id=t2)

Pending tasks
=============
  Grooming (id=t4, due=2026-10-25)
  Brushing (id=t6, due=None)
  Morning Walk (id=t1-2026-10-26, due=2026-10-26)
  Medication (id=t3-2026-10-26, due=2026-10-26)

Daily plan with conflict detection (same pet)
==============================================
Daily plan plan-rex (115 min scheduled):
  SCHEDULED Morning Walk: no reason given for this task.
  SCHEDULED Feeding: no reason given for this task.
  SCHEDULED Morning Walk: no reason given for this task.
  SCHEDULED Medication: no reason given for this task.
  SCHEDULED Medication: no reason given for this task.
  SCHEDULED Grooming: no reason given for this task.
  SKIPPED   Brushing: no reason given for this task.
  WARNING   Conflict at 07:00: Morning Walk (Rex), Morning Walk (Rex)
  WARNING   Conflict at 18:30: Medication (Rex), Medication (Rex)

Cross-pet conflict check (Rex + Whiskers)
==========================================
  WARNING   Conflict at 18:30: Medication (Rex), Medication (Rex)
  WARNING   Conflict at 07:00: Morning Walk (Rex), Morning Walk (Rex)
  WARNING   Conflict at 08:00: Feeding (Rex), Brushing (Rex), Vet Checkup (Whiskers)
```

> Note: Morning Walk and Medication are marked done *before* the schedule is generated, so their recurring next-day instances are already in Rex's task list and get scheduled too (115 of the owner's 120 available minutes are used in total). That leaves only 5 minutes free, so the low-priority Brushing task (10 min) is skipped — a direct example of the greedy time-fit algorithm in action.
