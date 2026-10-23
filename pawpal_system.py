"""PawPal+ core domain model.

Classes mirror diagrams/uml.mmd. No scheduling logic yet - stubs only.
"""

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

    def register(self) -> None:
        pass

    def set_available_minutes(self, minutes: int) -> None:
        pass

    def add_preference(self, key: str, value: str) -> None:
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
    def __init__(self, plan_date: date | None = None):
        self.plan_date = plan_date
        self.scheduled_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []
        self.reasoning: list[str] = []

    def generate(self, pet: Pet, owner: Owner, tasks: list[Task]) -> None:
        pass

    def _sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass

    def _fits_in_time(self, task: Task, remaining_minutes: int) -> bool:
        pass

    def add_task(self, task: Task, reason: str) -> None:
        pass

    def skip_task(self, task: Task, reason: str) -> None:
        pass

    def get_total_minutes(self) -> int:
        pass

    def explain(self) -> str:
        pass
