import uuid

import streamlit as st

from pawpal_system import (
    DailyPlan,
    HealthCondition,
    Owner,
    Pet,
    Priority,
    RecurrenceInterval,
    Task,
    TaskType,
)

PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

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

# --- Pets (owner.pets holds every pet; st.session_state only tracks which one is selected) ---
st.subheader("Pet")

if not owner.get_pets():
    default_pet = Pet(
        pet_id=str(uuid.uuid4()),
        name="Mochi",
        species="dog",
        health_condition=HealthCondition.HEALTHY,
    )
    owner.add_pet(default_pet)
    st.session_state.selected_pet_id = default_pet.pet_id

pet_by_id = {p.pet_id: p for p in owner.get_pets()}
if st.session_state.get("selected_pet_id") not in pet_by_id:
    st.session_state.selected_pet_id = owner.get_pets()[0].pet_id

selected_pet_id = st.selectbox(
    "Current pet",
    list(pet_by_id.keys()),
    index=list(pet_by_id.keys()).index(st.session_state.selected_pet_id),
    format_func=lambda pid: pet_by_id[pid].name,
)
st.session_state.selected_pet_id = selected_pet_id
pet: Pet = pet_by_id[selected_pet_id]

pet.name = st.text_input("Pet name", value=pet.name, key=f"pet_name_{pet.pet_id}")
pet.species = st.selectbox(
    "Species",
    ["dog", "cat", "other"],
    index=["dog", "cat", "other"].index(pet.species),
    key=f"pet_species_{pet.pet_id}",
)
pet.health_condition = st.selectbox(
    "Health condition",
    list(HealthCondition),
    index=list(HealthCondition).index(pet.health_condition),
    format_func=lambda h: h.name.title(),
    key=f"pet_health_{pet.pet_id}",
)

with st.expander("➕ Add a new pet"):
    new_pet_name = st.text_input("New pet's name", value="", key="new_pet_name")
    new_pet_species = st.selectbox(
        "New pet's species", ["dog", "cat", "other"], key="new_pet_species"
    )
    if st.button("Create pet"):
        if new_pet_name.strip():
            new_pet = Pet(
                pet_id=str(uuid.uuid4()),
                name=new_pet_name.strip(),
                species=new_pet_species,
                health_condition=HealthCondition.HEALTHY,
            )
            owner.add_pet(new_pet)
            st.session_state.selected_pet_id = new_pet.pet_id
            st.rerun()
        else:
            st.warning("Give the new pet a name first.")

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

col6, col7 = st.columns(2)
with col6:
    preferred_time = st.text_input(
        "Preferred time (optional, e.g. 08:00)", value="", key="preferred_time"
    )
with col7:
    recurrence = st.selectbox(
        "Recurrence",
        list(RecurrenceInterval),
        format_func=lambda r: r.name.title(),
        key="recurrence",
    )

if st.button("Add task"):
    new_task = Task(
        task_id=str(uuid.uuid4()),
        name=task_title,
        task_type=task_type,
        duration_minutes=int(duration),
        priority=priority,
        preferred_time=preferred_time or None,
        recurrence=recurrence,
    )
    pet.add_task(new_task)
    owner.set_priority_reason(priority, priority_reason)

if pet.get_tasks():
    status_filter = st.radio(
        "Show", ["All", "Pending", "Done"], horizontal=True, key="task_status_filter"
    )
    if status_filter == "Pending":
        filtered_tasks = pet.get_tasks_by_status(done=False)
    elif status_filter == "Done":
        filtered_tasks = pet.get_tasks_by_status(done=True)
    else:
        filtered_tasks = pet.get_tasks()

    sorted_tasks = sorted(filtered_tasks, key=lambda t: PRIORITY_ORDER[t.priority])

    if sorted_tasks:
        st.success(f"Showing {len(sorted_tasks)} task(s), sorted by priority (High → Low).")
    else:
        st.warning(f"No tasks match the '{status_filter}' filter.")

    st.table(
        [
            {
                "title": t.name,
                "type": t.task_type.name,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority.name,
                "preferred_time": t.preferred_time or "-",
                "recurrence": t.recurrence.name,
                "reason": owner.get_priority_reason(t.priority),
                "done": t.done,
            }
            for t in sorted_tasks
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

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Scheduled tasks", len(plan.scheduled_tasks))
    metric_col2.metric("Skipped tasks", len(plan.skipped_tasks))
    metric_col3.metric("Minutes scheduled", plan.get_total_minutes())

    if plan.scheduled_tasks:
        st.success(
            f"Scheduled {len(plan.scheduled_tasks)} task(s) totaling "
            f"{plan.get_total_minutes()} minutes."
        )
    if plan.skipped_tasks:
        st.error(
            f"Skipped {len(plan.skipped_tasks)} task(s) — not enough time remaining."
        )
    if plan.conflicts:
        for warning in plan.conflicts:
            st.warning(warning)
    else:
        st.info("No scheduling conflicts detected.")

    schedule_rows = []
    for t in plan.scheduled_tasks:
        schedule_rows.append(
            {
                "task_id": t.task_id,
                "Status": "Scheduled",
                "Pet": t.pet.name if t.pet else "-",
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
                "Pet": t.pet.name if t.pet else "-",
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
        disabled=["Status", "Pet", "Task", "Type", "Duration (min)", "Priority", "Reason"],
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
