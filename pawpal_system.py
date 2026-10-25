"""PawPal+ core domain model.

Classes mirror diagrams/uml.mmd, with a few deviations noted inline where
this file stores additional back-references the diagram leaves implicit.
No scheduling logic yet - stubs only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, auto


class HealthCondition(Enum):
    HEALTHY = auto()
    SICK = auto()
    RECOVERING = auto()
    SENIOR = auto()


class TaskType(Enum):
    WALK = auto()
    FEEDING = auto()
    MEDICATION = auto()
    ENRICHMENT = auto()
    GROOMING = auto()
    OTHER = auto()


class Priority(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class RecurrenceInterval(Enum):
    NONE = auto()
    DAILY = auto()
    WEEKLY = auto()

    @property
    def days(self) -> int:
        """Number of days to advance due_date by for this interval."""
        return {RecurrenceInterval.DAILY: 1, RecurrenceInterval.WEEKLY: 7}[self]


@dataclass
class Owner:
    owner_name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)
    # not in uml.mmd: lets the owner explain, in their own words, why a given
    # priority level matters (used as the plan's reasoning instead of a
    # time-based message)
    priority_reasons: dict[Priority, str] = field(default_factory=dict)

    def register(self) -> None:
        """Register this owner in the system."""
        pass

    def set_available_minutes(self, minutes: int) -> None:
        """Set how many minutes the owner has available for pet care today."""
        self.available_minutes = minutes

    def add_preference(self, key: str, value: str) -> None:
        """Store a scheduling preference for this owner."""
        self.preferences[key] = value

    def set_priority_reason(self, priority: Priority, reason: str) -> None:
        """Record the owner's explanation for why a priority level matters."""
        self.priority_reasons[priority] = reason

    def get_priority_reason(self, priority: Priority) -> str:
        """Return the owner's explanation for a priority level, if any."""
        return self.priority_reasons.get(
            # priority, f"no reason given for {priority.name.lower()} priority"
            priority, f"no reason given for this task."
        )

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return this owner's pets."""
        return self.pets


@dataclass
class Task:
    task_id: str
    name: str
    task_type: TaskType
    duration_minutes: int
    priority: Priority
    preferred_time: str | None = None
    # replaces the old `recurring: bool` - a flag alone can't say daily vs.
    # weekly, so recurrence now carries the interval itself
    recurrence: RecurrenceInterval = RecurrenceInterval.NONE
    due_date: date | None = None  # anchor date mark_done() advances from
    done: bool = False  # not in uml.mmd: tracked by mark_done()
    pet: Pet | None = None  # not in uml.mmd: back-reference set by Pet.add_task()

    def mark_done(self) -> None:
        """Mark this task as completed, spawning the next occurrence if recurring."""
        self.done = True
        if self.recurrence is not RecurrenceInterval.NONE and self.pet is not None:
            self.pet.add_task(self._next_occurrence())

    def _next_occurrence(self) -> Task:
        """Build the next instance of this task, advanced by its recurrence interval."""
        anchor = self.due_date or date.today()
        return Task(
            task_id=f"{self.task_id}-{anchor + timedelta(days=self.recurrence.days)}",
            name=self.name,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            recurrence=self.recurrence,
            due_date=anchor + timedelta(days=self.recurrence.days),
        )

    def update_priority(self, priority: Priority) -> None:
        """Change this task's priority."""
        self.priority = priority


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    health_condition: HealthCondition
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's care list."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id from this pet's care list."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return this pet's tasks."""
        return self.tasks

    def get_tasks_by_status(self, done: bool) -> list[Task]:
        """Return this pet's tasks filtered by completion status.

        Single O(n) pass over the task list via list comprehension, keeping
        the original relative order of matching tasks.
        """
        return [t for t in self.tasks if t.done == done]


class DailyPlan:
    def __init__(self, plan_id: str, plan_date: date | None = None):
        self.plan_id = plan_id
        self.plan_date = plan_date
        self.pet: Pet | None = None  # not in uml.mmd: set by generate() so explain()/get_total_minutes() know whose plan this is
        self.owner: Owner | None = None  # not in uml.mmd: set by generate()
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.reasoning: dict[str, str] = {}  # keyed by task_id; uml.mmd has this as a flat List~String~
        self.conflicts: list[str] = []  # not in uml.mmd: warnings from detect_conflicts()

    def generate(self, pet: Pet, owner: Owner) -> None:
        """Build this plan by scheduling the pet's tasks within the owner's available time."""
        self.pet = pet
        self.owner = owner
        self.scheduled_tasks = []
        self.skipped_tasks = []
        self.reasoning = {}
        self.conflicts = []

        remaining_minutes = owner.available_minutes
        for task in self._sort_by_priority(pet.get_tasks()):
            reason = owner.get_priority_reason(task.priority)
            if self._fits_in_time(task, remaining_minutes):
                remaining_minutes -= task.duration_minutes
                self.add_task(task, reason)
            else:
                self.skip_task(task, reason)

        self.conflicts = self.detect_conflicts(self.scheduled_tasks)

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Group scheduled tasks by preferred_time and warn when more than one lands on the same slot.

        Lightweight by design: a single pass grouping tasks into a dict keyed by
        preferred_time (O(n), no pairwise overlap math), so it can never raise -
        it only ever returns warning strings for the caller to surface.
        """
        by_time: dict[str, list[Task]] = {}
        for task in tasks:
            if not task.preferred_time:
                continue  # unscheduled/flexible tasks can't conflict
            by_time.setdefault(task.preferred_time, []).append(task)

        warnings = []
        for time, clashing in by_time.items():
            if len(clashing) > 1:
                names = ", ".join(f"{t.name} ({t.pet.name if t.pet else 'unknown pet'})" for t in clashing)
                warnings.append(f"Conflict at {time}: {names}")
        return warnings

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks ordered from highest to lowest priority.

        Maps each Priority enum value to a sort rank (HIGH=0 ... LOW=2) and
        runs Python's Timsort (O(n log n)) over that key, so tasks sharing a
        priority keep their original relative order.
        """
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: order[t.priority])

    def _fits_in_time(self, task: Task, remaining_minutes: int) -> bool:
        """Check whether a task's duration fits within the remaining minutes."""
        return task.duration_minutes <= remaining_minutes

    def add_task(self, task: Task, reason: str) -> None:
        """Schedule a task into this plan with the reason it was scheduled."""
        self.scheduled_tasks.append(task)
        self.reasoning[task.task_id] = reason

    def skip_task(self, task: Task, reason: str) -> None:
        """Skip a task from this plan with the reason it was skipped."""
        self.skipped_tasks.append(task)
        self.reasoning[task.task_id] = reason

    def get_total_minutes(self) -> int:
        """Return the total duration in minutes of all scheduled tasks."""
        return sum(task.duration_minutes for task in self.scheduled_tasks)

    def explain(self) -> str:
        """Return a human-readable summary of scheduled and skipped tasks."""
        lines = [f"Daily plan {self.plan_id} ({self.get_total_minutes()} min scheduled):"]
        for task in self.scheduled_tasks:
            lines.append(f"  SCHEDULED {task.name}: {self.reasoning.get(task.task_id, '')}")
        for task in self.skipped_tasks:
            lines.append(f"  SKIPPED   {task.name}: {self.reasoning.get(task.task_id, '')}")
        for warning in self.conflicts:
            lines.append(f"  WARNING   {warning}")
        return "\n".join(lines)
