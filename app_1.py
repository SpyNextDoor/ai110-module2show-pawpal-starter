import uuid

import streamlit as st

from pawpal_system_1 import DailyPlan, HealthCondition, Owner, Pet, Priority, Task, TaskType

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+ (wired to pawpal_system.py)")

st.markdown(
    """
This version connects the UI directly to the real `Owner`, `Pet`, `Task`, and `DailyPlan`
classes in `pawpal_system.py` — compare it against `app.py` to see the difference.
"""
)

st.divider()

# --- Owner (created once per session, persisted in st.session_state) ---
st.subheader("Owner")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name="Jordan")

owner: Owner = st.session_state.owner

owner_name = st.text_input("Owner name", value=owner.owner_name)
owner.owner_name = owner_name

available_minutes = st.number_input(
    "Available minutes today", min_value=0, max_value=600, value=owner.available_minutes or 120
)
owner.set_available_minutes(int(available_minutes))

st.divider()

# --- Pet (created once per session, persisted in st.session_state) ---
st.subheader("Pet")

if "pet" not in st.session_state:
    pet = Pet(
        pet_id=str(uuid.uuid4()),
        name="Mochi",
        species="dog",
        health_condition=HealthCondition.HEALTHY,
    )
    owner.add_pet(pet)
    st.session_state.pet = pet

pet: Pet = st.session_state.pet

pet.name = st.text_input("Pet name", value=pet.name)
pet.species = st.selectbox(
    "Species", ["dog", "cat", "other"], index=["dog", "cat", "other"].index(pet.species)
)
pet.health_condition = st.selectbox(
    "Health condition",
    list(HealthCondition),
    index=list(HealthCondition).index(pet.health_condition),
    format_func=lambda h: h.name.title(),
)

st.divider()

# --- Tasks (real Task objects, attached to the Pet) ---
st.markdown("### Tasks")
st.caption(
    "Tasks are added directly to this pet's task list via Pet.add_task(). "
    "After picking a priority, say why that priority matters — this is stored "
    "per priority level (Owner.set_priority_reason) and reused as the schedule's reasoning."
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_type = st.selectbox(
        "Task type", list(TaskType), format_func=lambda t: t.name.title()
    )
with col3:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col4:
    priority = st.selectbox(
        "Priority", list(Priority), index=2, format_func=lambda p: p.name.title()
    )
with col5:
    priority_reason = st.text_input(
        f"Why {priority.name.title()} priority?",
        value=owner.priority_reasons.get(priority, ""),
        key=f"reason_{priority.name}",
    )

if st.button("Add task"):
    new_task = Task(
        task_id=str(uuid.uuid4()),
        name=task_title,
        task_type=task_type,
        duration_minutes=int(duration),
        priority=priority,
    )
    pet.add_task(new_task)
    owner.set_priority_reason(priority, priority_reason)

if pet.get_tasks():
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": t.name,
                "type": t.task_type.name,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority.name,
                "reason": owner.get_priority_reason(t.priority),
                "done": t.done,
            }
            for t in pet.get_tasks()
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule (DailyPlan.generate against the real Owner/Pet) ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    plan = DailyPlan(plan_id=str(uuid.uuid4()))
    plan.generate(pet, owner)
    st.session_state.plan = plan

if "plan" in st.session_state:
    plan: DailyPlan = st.session_state.plan
    st.write(f"Total scheduled minutes: {plan.get_total_minutes()}")

    schedule_rows = []
    for t in plan.scheduled_tasks:
        schedule_rows.append(
            {
                "task_id": t.task_id,
                "Status": "Scheduled",
                "Task": t.name,
                "Type": t.task_type.name.title(),
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority.name.title(),
                "Reason": plan.reasoning.get(t.task_id, ""),
                "Done": t.done,
            }
        )
    for t in plan.skipped_tasks:
        schedule_rows.append(
            {
                "task_id": t.task_id,
                "Status": "Skipped",
                "Task": t.name,
                "Type": t.task_type.name.title(),
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority.name.title(),
                "Reason": plan.reasoning.get(t.task_id, ""),
                "Done": t.done,
            }
        )

    edited_rows = st.data_editor(
        schedule_rows,
        column_config={
            "task_id": None,
            "Done": st.column_config.CheckboxColumn("Done"),
        },
        disabled=["Status", "Task", "Type", "Duration (min)", "Priority", "Reason"],
        hide_index=True,
        use_container_width=True,
        key="schedule_editor",
    )

    task_lookup = {t.task_id: t for t in pet.get_tasks()}
    for row in edited_rows:
        task = task_lookup.get(row["task_id"])
        if task is not None and row["Done"] != task.done:
            if row["Done"]:
                task.mark_done()
            else:
                task.done = False

    st.text(plan.explain())
