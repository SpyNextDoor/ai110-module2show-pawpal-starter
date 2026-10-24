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

Scheduling logic currently uses a simple priority-first greedy algorithm; the Streamlit UI and more advanced conflict/recurrence handling are not yet implemented (see the "Smarter Scheduling" section below for what's planned).

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

> **Current status:** Steps 1-5 are done — see [Implementation Summary](#implementation-summary) above. `main.py` is a CLI demo of the domain model; the Streamlit UI (step 6) is still to come.

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

| Feature           | Method(s)                                           | Notes                                                                     |
| ----------------- | --------------------------------------------------- | ------------------------------------------------------------------------- |
| Task sorting      | `DailyPlan._sort_by_priority`                     | Orders a pet's tasks HIGH → MEDIUM → LOW before scheduling              |
| Filtering         | `DailyPlan._fits_in_time`, `DailyPlan.generate` | Greedily schedules tasks while time remains; skips the rest with a reason |
| Conflict handling | *(not yet implemented)*                           | `Task.preferred_time` exists but overlapping time slots aren't detected |
| Recurring tasks   | *(not yet implemented)*                           | `Task.recurring` flag exists but isn't used by the scheduler yet        |

## 📸 Demo Walkthrough

Running `python main.py` does the following:

1. Creates an `Owner` ("Jean Marie") with 120 available minutes.
2. Creates two `Pet`s — Rex (a healthy dog) and Whiskers (a senior cat) — and adds them to the owner.
3. Creates three `Task`s (Morning Walk, Feeding, Medication) with durations, priorities, and preferred times, and assigns them to the appropriate pet.
4. Collects all tasks across the owner's pets and sorts them by preferred time.
5. Prints the resulting schedule to the console (see [Sample Output](#-sample-output) above).

A Streamlit UI that lets a user interactively manage owners/pets/tasks and view a `DailyPlan`'s generated schedule is planned but not yet built.

**Screenshot or video** *(optional)*:
