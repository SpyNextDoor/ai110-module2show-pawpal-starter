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
    HEALTHY = auto() # 1
    SICK = auto() # 2
    RECOVERING = auto() # 3
    SENIOR = auto() # 4


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
        pass

    def set_available_minutes(self, minutes: int) -> None:
        pass

    def add_preference(self, key: str, value: str) -> None:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> list[Pet]:
        pass


@dataclass
class Task:
    task_id: str
    name: str
    task_type: TaskType
    duration_minutes: int
    priority: Priority
    preferred_time: str | None = None
    recurring: bool = False
    pet: Pet | None = None  # not in uml.mmd: back-reference set by Pet.add_task()

    def mark_done(self) -> None:
        pass

    def update_priority(self, priority: Priority) -> None:
        pass


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    health_condition: HealthCondition
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


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
        pass

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def _fits_in_time(self, task: Task, remaining_minutes: int) -> bool:
        pass

    def add_task(self, task: Task, reason: str) -> None:
        # stores reason in self.reasoning[task.task_id]
        pass

    def skip_task(self, task: Task, reason: str) -> None:
        # stores reason in self.reasoning[task.task_id]
        pass

    def get_total_minutes(self) -> int:
        pass

    def explain(self) -> str:
        pass
