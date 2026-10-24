"""Demo script for the PawPal+ domain model."""

from pawpal_system import HealthCondition, Owner, Pet, Priority, Task, TaskType

owner = Owner(owner_name="Jean Marie")
owner.set_available_minutes(120)

dog = Pet(pet_id="p1", name="Rex", species="Dog", health_condition=HealthCondition.HEALTHY)
cat = Pet(pet_id="p2", name="Whiskers", species="Cat", health_condition=HealthCondition.SENIOR)

owner.add_pet(dog)
owner.add_pet(cat)

morning_walk = Task(
    task_id="t1",
    name="Morning Walk",
    task_type=TaskType.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    preferred_time="07:00",
)
feeding = Task(
    task_id="t2",
    name="Feeding",
    task_type=TaskType.FEEDING,
    duration_minutes=15,
    priority=Priority.HIGH,
    preferred_time="08:00",
)
medication = Task(
    task_id="t3",
    name="Medication",
    task_type=TaskType.MEDICATION,
    duration_minutes=10,
    priority=Priority.MEDIUM,
    preferred_time="18:30",
)

dog.add_task(morning_walk)
dog.add_task(feeding)
cat.add_task(medication)

print("Today's Schedule")
print("=================")

all_tasks = [task for pet in owner.get_pets() for task in pet.get_tasks()]
all_tasks.sort(key=lambda t: t.preferred_time or "")

for task in all_tasks:
    print(f"{task.preferred_time}  {task.pet.name:10s}  {task.name} ({task.duration_minutes} min, priority: {task.priority.name})")
