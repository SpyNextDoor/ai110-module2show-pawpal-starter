import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Task, TaskType, Priority, HealthCondition


def test_mark_done_changes_task_status():
    task = Task(
        task_id="t1",
        name="Morning walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.MEDIUM,
    )
    assert task.done is False

    task.mark_done()

    assert task.done is True


def test_add_task_increases_pet_task_count():
    pet = Pet(
        pet_id="p1",
        name="Rex",
        species="Dog",
        health_condition=HealthCondition.HEALTHY,
    )
    assert len(pet.get_tasks()) == 0

    task = Task(
        task_id="t1",
        name="Morning walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.MEDIUM,
    )
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
