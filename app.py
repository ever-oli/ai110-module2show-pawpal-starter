"""PawPal+ Streamlit UI, wired to the logic layer in pawpal_system.py."""

import os

import streamlit as st

from pawpal_system import Task, Pet, Owner, Scheduler, PRIORITY_ICON

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

DATA_FILE = "data.json"

# ---------- Session state: create the Owner + Scheduler exactly once ----------
# Streamlit reruns this script top-to-bottom on every click, so the Owner
# must live in st.session_state or it would be recreated (empty) each time.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
    st.session_state.scheduler = Scheduler(st.session_state.owner)

owner = st.session_state.owner
scheduler = st.session_state.scheduler


def rows_for(pairs):
    """Turn (pet, task) pairs into table-friendly dicts."""
    return [
        {
            "Time": task.time,
            "Priority": f"{PRIORITY_ICON.get(task.priority, '')} {task.priority}",
            "Task": task.description,
            "Pet": pet.name,
            "Duration (min)": task.duration_minutes,
            "Repeats": task.frequency,
            "Done": "✅" if task.completed else "—",
        }
        for pet, task in pairs
    ]


# ---------- Sidebar: household setup + persistence ----------
with st.sidebar:
    st.header("Household")
    new_owner_name = st.text_input("Owner name", value=owner.name)
    if new_owner_name != owner.name:
        owner.name = new_owner_name

    st.subheader("Add a pet")
    pet_name = st.text_input("Pet name", key="pet_name_input")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    if st.button("Add pet"):
        if not pet_name.strip():
            st.error("Give your pet a name first!")
        elif owner.get_pet(pet_name):
            st.error(f"{pet_name} is already in the household.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species))
            st.success(f"Added {pet_name}!")

    if owner.pets:
        st.caption("Pets: " + ", ".join(p.name for p in owner.pets))

    st.divider()
    st.subheader("Save / Load")
    if st.button("💾 Save to data.json"):
        scheduler.save_to_json(DATA_FILE)
        st.success("Saved!")
    if st.button("📂 Load from data.json"):
        if os.path.exists(DATA_FILE):
            st.session_state.scheduler = Scheduler.load_from_json(DATA_FILE)
            st.session_state.owner = st.session_state.scheduler.owner
            st.success("Loaded! Refreshing...")
            st.rerun()
        else:
            st.error("No saved data found yet.")

# ---------- Add a task ----------
st.subheader("Schedule a Task")
if not owner.pets:
    st.info("Add a pet in the sidebar to start scheduling tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        target_pet = st.selectbox("Pet", [p.name for p in owner.pets])
        description = st.text_input("Task", value="Morning walk")
        time_str = st.time_input("Time").strftime("%H:%M")
    with col2:
        duration = st.number_input("Duration (minutes)", 1, 240, 20)
        frequency = st.selectbox("Repeats", ["once", "daily", "weekly"])
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)

    if st.button("Add task"):
        task = Task(description, time_str, int(duration), frequency, priority)
        owner.get_pet(target_pet).add_task(task)
        st.success(f"Scheduled '{description}' for {target_pet} at {time_str}.")

st.divider()

# ---------- Today's schedule ----------
st.subheader("📋 Today's Schedule")
st.caption("Sorted by priority (high → low), then by time.")

# Conflict warnings from the Scheduler, surfaced in the UI
for warning in scheduler.detect_conflicts():
    st.warning(warning)

col_a, col_b = st.columns(2)
with col_a:
    pet_filter = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
with col_b:
    show_done = st.checkbox("Show completed tasks")

pairs = scheduler.sort_by_priority()
if pet_filter != "All":
    pairs = [(p, t) for p, t in pairs if p.name == pet_filter]
if not show_done:
    pairs = [(p, t) for p, t in pairs if not t.completed]

if pairs:
    st.table(rows_for(pairs))
else:
    st.info("No tasks to show. Schedule one above!")

# ---------- Mark tasks complete ----------
incomplete = [(p, t) for p, t in scheduler.sort_by_time() if not t.completed]
if incomplete:
    st.subheader("Mark Complete")
    labels = [f"{t.time} — {t.description} ({p.name})" for p, t in incomplete]
    choice = st.selectbox("Task to complete", labels)
    if st.button("✅ Complete"):
        pet, task = incomplete[labels.index(choice)]
        new_task = scheduler.mark_task_complete(task)
        if new_task:
            st.success(
                f"Done! Since it repeats {task.frequency}, the next one is "
                f"queued for {new_task.due_date}."
            )
        else:
            st.success("Done!")
        st.rerun()
