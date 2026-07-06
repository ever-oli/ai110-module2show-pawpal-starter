"""Automated tests for the PawPal+ system."""

from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


def make_household():
    """Helper: one owner, two pets, no tasks yet."""
    owner = Owner("Test Owner")
    owner.add_pet(Pet("Biscuit", "Dog"))
    owner.add_pet(Pet("Noodle", "Cat"))
    return owner, Scheduler(owner)


def test_mark_complete_changes_status():
    task = Task("Walk", "08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_count():
    pet = Pet("Biscuit", "Dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "08:00"))
    assert pet.task_count() == 1


def test_sort_by_time_returns_chronological_order():
    owner, scheduler = make_household()
    owner.get_pet("Biscuit").add_task(Task("Dinner", "18:00"))
    owner.get_pet("Noodle").add_task(Task("Breakfast", "07:00"))
    owner.get_pet("Biscuit").add_task(Task("Walk", "12:30"))
    times = [task.time for _, task in scheduler.sort_by_time()]
    assert times == ["07:00", "12:30", "18:00"]


def test_priority_sort_puts_high_first():
    owner, scheduler = make_household()
    owner.get_pet("Biscuit").add_task(Task("Play", "09:00", priority="low"))
    owner.get_pet("Biscuit").add_task(Task("Meds", "10:00", priority="high"))
    first_task = scheduler.sort_by_priority()[0][1]
    assert first_task.description == "Meds"


def test_completing_daily_task_creates_tomorrow_occurrence():
    owner, scheduler = make_household()
    pet = owner.get_pet("Noodle")
    task = Task("Feed", "07:30", frequency="daily")
    pet.add_task(task)

    new_task = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert pet.task_count() == 2
    assert new_task.completed is False
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    assert new_task.due_date == tomorrow


def test_once_task_does_not_recur():
    owner, scheduler = make_household()
    pet = owner.get_pet("Biscuit")
    task = Task("Vet visit", "14:00", frequency="once")
    pet.add_task(task)
    assert scheduler.mark_task_complete(task) is None
    assert pet.task_count() == 1


def test_conflict_detected_for_duplicate_times():
    owner, scheduler = make_household()
    owner.get_pet("Biscuit").add_task(Task("Walk", "08:00"))
    owner.get_pet("Noodle").add_task(Task("Feed", "08:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_no_conflict_for_different_times():
    owner, scheduler = make_household()
    owner.get_pet("Biscuit").add_task(Task("Walk", "08:00"))
    owner.get_pet("Noodle").add_task(Task("Feed", "09:00"))
    assert scheduler.detect_conflicts() == []


def test_json_round_trip(tmp_path):
    owner, scheduler = make_household()
    owner.get_pet("Biscuit").add_task(Task("Walk", "08:00", priority="high"))
    filepath = tmp_path / "data.json"

    scheduler.save_to_json(str(filepath))
    restored = Scheduler.load_from_json(str(filepath))

    assert restored.owner.name == "Test Owner"
    assert len(restored.owner.pets) == 2
    restored_task = restored.owner.get_pet("Biscuit").get_tasks()[0]
    assert restored_task.description == "Walk"
    assert restored_task.priority == "high"
