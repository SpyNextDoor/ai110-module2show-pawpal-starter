"""PawPal+ core domain model.

Classes mirror diagrams/uml.mmd, with a few deviations noted inline where
this file stores additional back-references the diagram leaves implicit.
No scheduling logic yet - stubs only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
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


@dataclass
class Owner:
    owner_name: str
    available_minutes: int = 0
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def register(self) -> None:
        """Register this owner in the system."""
        pass

    def set_available_minutes(self, minutes: int) -> None:
        """Set how many minutes the owner has available for pet care today."""
        self.available_minutes = minutes

    def add_preference(self, key: str, value: str) -> None:
        """Store a scheduling preference for this owner."""
        self.preferences[key] = value

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
    recurring: bool = False
    done: bool = False  # not in uml.mmd: tracked by mark_done()
    pet: Pet | None = None  # not in uml.mmd: back-reference set by Pet.add_task()

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.done = True

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


class DailyPlan:
    def __init__(self, plan_id: str, plan_date: date | None = None):
        self.plan_id = plan_id
        self.plan_date = plan_date
        self.pet: Pet | None = None  # not in uml.mmd: set by generate() so explain()/get_total_minutes() know whose plan this is
        self.owner: Owner | None = None  # not in uml.mmd: set by generate()
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.reasoning: dict[str, str] = {}  # keyed by task_id; uml.mmd has this as a flat List~String~

    def generate(self, pet: Pet, owner: Owner) -> None:
        """Build this plan by scheduling the pet's tasks within the owner's available time."""
        self.pet = pet
        self.owner = owner
        self.scheduled_tasks = []
        self.skipped_tasks = []
        self.reasoning = {}

        remaining_minutes = owner.available_minutes
        for task in self._sort_by_priority(pet.get_tasks()):
            if self._fits_in_time(task, remaining_minutes):
                remaining_minutes -= task.duration_minutes
                self.add_task(task, f"fits in remaining {remaining_minutes + task.duration_minutes} min")
            else:
                self.skip_task(task, f"not enough time left ({remaining_minutes} min remaining)")

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks ordered from highest to lowest priority."""
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
        return "\n".join(lines)
