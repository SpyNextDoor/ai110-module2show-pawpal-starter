"""Demo script for the PawPal+ domain model."""

from datetime import date

from pawpal_system_1 import (
    DailyPlan,
    HealthCondition,
    Owner,
    Pet,
    Priority,
    RecurrenceInterval,
    Task,
    TaskType,
)

owner = Owner(owner_name="Jean Marie")
owner.set_available_minutes(120)

dog = Pet(pet_id="p1", name="Rex", species="Dog", health_condition=HealthCondition.HEALTHY)
cat = Pet(pet_id="p2", name="Whiskers", species="Cat", health_condition=HealthCondition.SENIOR)

owner.add_pet(dog)
owner.add_pet(cat)

# Tasks are added out of priority order on purpose, to exercise _sort_by_priority.
medication = Task(
    task_id="t3",
    name="Medication",
    task_type=TaskType.MEDICATION,
    duration_minutes=10,
    priority=Priority.MEDIUM,
    preferred_time="18:30",
    recurrence=RecurrenceInterval.DAILY,
    due_date=date.today(),
)
grooming = Task(
    task_id="t4",
    name="Grooming",
    task_type=TaskType.GROOMING,
    duration_minutes=20,
    priority=Priority.LOW,
    preferred_time="16:00",
    recurrence=RecurrenceInterval.WEEKLY,
    due_date=date.today(),
)
morning_walk = Task(
    task_id="t1",
    name="Morning Walk",
    task_type=TaskType.WALK,
    duration_minutes=30,
    priority=Priority.HIGH,
    preferred_time="07:00",
    recurrence=RecurrenceInterval.DAILY,
    due_date=date.today(),
)
feeding = Task(
    task_id="t2",
    name="Feeding",
    task_type=TaskType.FEEDING,
    duration_minutes=15,
    priority=Priority.HIGH,
    preferred_time="08:00",
)
# Deliberately clashes with Feeding (same pet, same preferred_time) to exercise
# DailyPlan.detect_conflicts().
brushing = Task(
    task_id="t6",
    name="Brushing",
    task_type=TaskType.GROOMING,
    duration_minutes=10,
    priority=Priority.LOW,
    preferred_time="08:00",
)

dog.add_task(medication)
dog.add_task(grooming)
dog.add_task(morning_walk)
dog.add_task(feeding)
dog.add_task(brushing)

cat_checkup = Task(
    task_id="t5",
    name="Vet Checkup",
    task_type=TaskType.OTHER,
    duration_minutes=25,
    priority=Priority.HIGH,
    # Also clashes with Feeding/Brushing above, but for a *different* pet.
    preferred_time="08:00",
)
cat.add_task(cat_checkup)

# Mark some tasks done. Morning Walk and Medication recur, so completing them
# should spawn tomorrow's (or next week's) instance automatically.
feeding.mark_done()
morning_walk.mark_done()
medication.mark_done()

print("Today's Schedule (sorted by priority)")
print("======================================")

plan = DailyPlan(plan_id="plan-rex")
sorted_tasks = plan._sort_by_priority(dog.get_tasks())

for task in sorted_tasks:
    print(f"{task.priority.name:6s}  {task.name:14s} id={task.task_id:12s} due={task.due_date}")

print()
print("Completed tasks")
print("================")
for task in dog.get_tasks_by_status(done=True):
    print(f"  {task.name} (id={task.task_id})")

print()
print("Pending tasks")
print("=============")
for task in dog.get_tasks_by_status(done=False):
    print(f"  {task.name} (id={task.task_id}, due={task.due_date})")

print()
print("Daily plan with conflict detection (same pet)")
print("==============================================")
plan.generate(dog, owner)
print(plan.explain())

print()
print("Cross-pet conflict check (Rex + Whiskers)")
print("==========================================")
cross_pet_conflicts = plan.detect_conflicts(dog.get_tasks() + cat.get_tasks())
if cross_pet_conflicts:
    for warning in cross_pet_conflicts:
        print(f"  WARNING   {warning}")
else:
    print("  No conflicts found.")
