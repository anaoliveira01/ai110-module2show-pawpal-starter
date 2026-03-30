import streamlit as st
from datetime import time as dtime
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Session state must be initialized before any widget reads it
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pet" not in st.session_state:
    st.session_state.pet = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # Create the Owner if it doesn't exist yet
    if st.session_state.owner is None or st.session_state.owner.name != owner_name:
        st.session_state.owner = Owner(owner_name)
    # Create the Pet and register it with the Owner via addPet()
    pet = Pet(name=pet_name, age=0, species=species)
    st.session_state.owner.addPet(pet)   # <-- links pet.owner and appends to owner.pets
    st.session_state.pet = pet
    st.session_state.scheduler = None    # reset so next build reflects new pet

# Show all registered pets live from owner.getPets()
if st.session_state.owner:
    pets = st.session_state.owner.getPets()
    if pets:
        st.write("Registered pets:")
        st.table([{"name": p.name, "species": p.species} for p in pets])

# --- Owner Availability (for tasks without a pinned start time) ---
st.markdown("### Owner Availability")
st.caption("Add free time slots. Tasks without a pinned start time are assigned here in priority order.")
avail_col1, avail_col2 = st.columns([3, 1])
with avail_col1:
    avail_time = st.time_input("Available slot", value=dtime(8, 0), key="avail_time_input")
with avail_col2:
    st.write("")
    st.write("")
    if st.button("Add slot"):
        if st.session_state.owner is None:
            st.session_state.owner = Owner(owner_name)
        if avail_time not in st.session_state.owner.availableTimes:
            st.session_state.owner.availableTimes.append(avail_time)
            st.session_state.scheduler = None

if st.session_state.owner and st.session_state.owner.availableTimes:
    slots = sorted(st.session_state.owner.availableTimes)
    st.write("Slots:", ", ".join(s.strftime("%I:%M %p") for s in slots))

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

r_col1, r_col2, r_col3 = st.columns(3)
with r_col1:
    use_start_time = st.checkbox("Pin start time")
with r_col2:
    task_start = st.time_input("Start time", value=dtime(8, 0))
with r_col3:
    recurring = st.checkbox("Recurring task")

recurrence_interval = None
if recurring:
    recurrence_interval = st.selectbox("Repeats", ["daily", "weekly"])

# Pet selector when multiple pets exist
task_pet_name = pet_name
if st.session_state.owner and len(st.session_state.owner.getPets()) > 1:
    task_pet_name = st.selectbox(
        "Assign to pet",
        [p.name for p in st.session_state.owner.getPets()]
    )

if st.button("Add task"):
    # Keep the owner and pet in sync with whatever is currently typed in the inputs
    if st.session_state.owner is None or st.session_state.owner.name != owner_name:
        st.session_state.owner = Owner(owner_name)

    # Find or create the target pet
    target_pet = next(
        (p for p in st.session_state.owner.getPets() if p.name == task_pet_name),
        None
    )
    if target_pet is None:
        target_pet = Pet(name=task_pet_name, age=0, species=species)
        st.session_state.owner.addPet(target_pet)
    st.session_state.pet = target_pet

    priority_map = {"low": 1, "medium": 2, "high": 3}
    h, m = divmod(int(duration), 60)
    task_obj = Task(
        taskName=task_title,
        description=task_title,
        durationMinutes=dtime(h, m),
        priority=priority_map[priority],
        timeSlot=task_start if use_start_time else None,
        recurring=recurring,
        recurrenceInterval=recurrence_interval,
    )
    st.session_state.pet.addTask(task_obj)
    st.session_state.scheduler = None      # reset scheduler so next build is fresh

    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.owner:
    all_pet_tasks = []
    for p in st.session_state.owner.getPets():
        for t in p.getTasks():
            mins = t.durationMinutes.hour * 60 + t.durationMinutes.minute
            all_pet_tasks.append({
                "pet": p.name,
                "task": t.taskName,
                "duration": f"{mins} min",
                "priority": {1: "low", 2: "medium", 3: "high"}.get(t.priority, str(t.priority)),
                "start time": t.timeSlot.strftime("%I:%M %p") if t.timeSlot else "auto",
                "recurring": t.recurrenceInterval if t.recurring else "—",
            })
    if all_pet_tasks:
        st.write("Current tasks:")
        # Read directly from pet.getTasks() — the live object, not a copy
        st.table(all_pet_tasks)
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    # Store the Scheduler in session state so it survives re-runs
    if st.session_state.owner is not None:
        scheduler = Scheduler(owner=st.session_state.owner)
        scheduler.buildSchedule()
        st.session_state.scheduler = scheduler

    st.warning(
        "Not implemented yet. Next step: create your scheduling logic (classes/functions) and call it here."
    )
    st.markdown(
        """
Suggested approach:
1. Design your UML (draft).
2. Create class stubs (no logic).
3. Implement scheduling behavior.
4. Connect your scheduler here and display results.
"""
    )

# Display the schedule if one has been built and stored in session state
if st.session_state.scheduler:
    scheduler = st.session_state.scheduler
    plan = scheduler.getDailyPlan()
    if plan:
        st.success("Schedule ready!")

        # --- Conflict Detection ---
        conflicts = scheduler.detectConflicts()
        if conflicts:
            st.error(f"⚠️ {len(conflicts)} conflict(s) detected:")
            for msg in conflicts:
                st.markdown(f"- {msg}")
        else:
            st.info("No scheduling conflicts detected.")

        # --- Recurring Tasks Summary ---
        recurring_tasks = scheduler.getRecurringTasks()
        if recurring_tasks:
            with st.expander(f"Recurring tasks in this schedule ({len(recurring_tasks)})"):
                for t in recurring_tasks:
                    pet_label = t.pet.name if t.pet else "?"
                    st.markdown(f"- **{t.taskName}** ({pet_label}) — repeats {t.recurrenceInterval}")

        # --- Sort & Filter Controls ---
        st.markdown("#### Sort & Filter")
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            sort_mode = st.radio("Sort by", ["Time", "Priority"], horizontal=True)
        with f_col2:
            pet_names = sorted({t.pet.name for t in plan if t.pet})
            pet_filter = st.selectbox("Filter by pet", ["All"] + pet_names)
        with f_col3:
            status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"])

        # Apply sort using the new sortByTime() algorithm
        if sort_mode == "Time":
            display_tasks = scheduler.sortByTime()
        else:
            display_tasks = sorted(plan, key=lambda t: -t.priority)

        # Apply pet filter using filterByPet() logic
        if pet_filter != "All":
            display_tasks = [t for t in display_tasks if t.pet and t.pet.name == pet_filter]

        # Apply status filter using filterByStatus() logic
        if status_filter == "Pending":
            display_tasks = [t for t in display_tasks if not t.isCompleted]
        elif status_filter == "Completed":
            display_tasks = [t for t in display_tasks if t.isCompleted]

        priority_label = {1: "low", 2: "medium", 3: "high"}
        if display_tasks:
            st.table(
                [
                    {
                        "time": t.timeSlot.strftime("%I:%M %p") if t.timeSlot else "—",
                        "pet": t.pet.name if t.pet else "—",
                        "task": t.taskName,
                        "duration": f"{t.durationMinutes.hour * 60 + t.durationMinutes.minute} min",
                        "priority": priority_label.get(t.priority, str(t.priority)),
                        "recurring": f"↻ {t.recurrenceInterval}" if t.recurring else "",
                        "status": "done" if t.isCompleted else "pending",
                    }
                    for t in display_tasks
                ]
            )
        else:
            st.info("No tasks match the current filters.")

        # --- Mark a task complete ---
        st.markdown("#### Mark Task Complete")
        pending = [t for t in plan if not t.isCompleted]
        if pending:
            mc_col1, mc_col2 = st.columns([3, 1])
            with mc_col1:
                task_to_complete = st.selectbox(
                    "Select task",
                    [t.taskName for t in pending],
                    key="complete_select"
                )
            with mc_col2:
                st.write("")
                st.write("")
                if st.button("Mark done"):
                    scheduler.completeTask(task_to_complete)
                    st.rerun()
        else:
            st.success("All tasks are done!")
