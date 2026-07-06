"""PawPal+ logic layer: Task, Pet, Owner, and Scheduler classes."""

import json
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
PRIORITY_ICON = {"high": "🔴", "medium": "🟡", "low": "🟢"}


@dataclass
class Task:
    """A single pet care activity (walk, feeding, meds, etc.)."""

    description: str
    time: str  # "HH:MM" 24-hour format
    duration_minutes: int = 15
    frequency: str = "once"  # once | daily | weekly
    priority: str = "medium"  # low | medium | high
    completed: bool = False
    due_date: str = field(default_factory=lambda: date.today().isoformat())

    def mark_complete(self):
        """Mark this task as done."""
        self.completed = True

    def next_occurrence(self):
        """Return a fresh copy of this task due at its next recurrence,
        or None if it doesn't repeat."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        next_due = date.fromisoformat(self.due_date) + delta
        return Task(
            description=self.description,
            time=self.time,
            duration_minutes=self.duration_minutes,
            frequency=self.frequency,
            priority=self.priority,
            completed=False,
            due_date=next_due.isoformat(),
        )


@dataclass
class Pet:
    """A pet with a name, species, and a list of care tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """Attach a task to this pet."""
        self.tasks.append(task)

    def get_tasks(self):
        """Return all tasks for this pet."""
        return self.tasks

    def task_count(self):
        """Return how many tasks this pet has."""
        return len(self.tasks)


class Owner:
    """A pet owner who manages one or more pets."""

    def __init__(self, name: str):
        self.name = name
        self.pets = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str):
        """Find a pet by name (case-insensitive), or None if not found."""
        for pet in self.pets:
            if pet.name.lower() == name.lower():
                return pet
        return None

    def get_all_tasks(self):
        """Return (pet, task) pairs across all pets."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The brain: organizes, sorts, filters, and checks tasks."""

    def __init__(self, owner: Owner):
        self.owner = owner

    # ---------- Sorting ----------

    def sort_by_time(self):
        """Return all (pet, task) pairs in chronological order."""
        return sorted(self.owner.get_all_tasks(), key=lambda pair: pair[1].time)

    def sort_by_priority(self):
        """Return (pet, task) pairs sorted by priority (high first), then time."""
        return sorted(
            self.owner.get_all_tasks(),
            key=lambda pair: (PRIORITY_RANK.get(pair[1].priority, 1), pair[1].time),
        )

    # ---------- Filtering ----------

    def filter_by_status(self, completed: bool):
        """Return (pet, task) pairs matching a completion status."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if task.completed == completed
        ]

    def filter_by_pet(self, pet_name: str):
        """Return (pet, task) pairs belonging to a specific pet."""
        return [
            (pet, task)
            for pet, task in self.owner.get_all_tasks()
            if pet.name.lower() == pet_name.lower()
        ]

    # ---------- Conflict detection ----------

    def detect_conflicts(self):
        """Return warning strings for incomplete tasks that share the
        exact same time. Lightweight: warns instead of raising."""
        seen = {}
        warnings = []
        for pet, task in self.owner.get_all_tasks():
            if task.completed:
                continue
            if task.time in seen:
                other_pet, other_task = seen[task.time]
                warnings.append(
                    f"⚠️  Conflict at {task.time}: "
                    f"'{other_task.description}' ({other_pet.name}) and "
                    f"'{task.description}' ({pet.name})"
                )
            else:
                seen[task.time] = (pet, task)
        return warnings

    # ---------- Completion + recurrence ----------

    def mark_task_complete(self, task: Task):
        """Complete a task; daily/weekly tasks spawn their next occurrence
        on the same pet. Returns the new task or None."""
        task.mark_complete()
        new_task = task.next_occurrence()
        if new_task is not None:
            for pet in self.owner.pets:
                if task in pet.tasks:
                    pet.add_task(new_task)
                    break
        return new_task

    # ---------- Schedule display ----------

    def get_todays_schedule(self):
        """Return incomplete (pet, task) pairs sorted by priority then time."""
        return [
            (pet, task)
            for pet, task in self.sort_by_priority()
            if not task.completed
        ]

    def format_schedule(self):
        """Return today's schedule as a pretty CLI string with any
        conflict warnings appended."""
        lines = [f"📋 Today's Schedule for {self.owner.name}", "=" * 46]
        schedule = self.get_todays_schedule()
        if not schedule:
            lines.append("Nothing to do — all caught up! 🎉")
        for pet, task in schedule:
            icon = PRIORITY_ICON.get(task.priority, "🟡")
            lines.append(
                f"{task.time}  {icon} {task.description:<24} "
                f"{pet.name} ({pet.species}) · {task.duration_minutes} min · {task.frequency}"
            )
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("-" * 46)
            lines.extend(conflicts)
        return "\n".join(lines)

    # ---------- Persistence (JSON) ----------

    def save_to_json(self, filepath: str):
        """Save the owner, pets, and tasks to a JSON file."""
        data = {
            "owner": self.owner.name,
            "pets": [
                {
                    "name": pet.name,
                    "species": pet.species,
                    "tasks": [asdict(task) for task in pet.tasks],
                }
                for pet in self.owner.pets
            ],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str):
        """Rebuild a Scheduler (with its Owner, Pets, Tasks) from JSON."""
        with open(filepath) as f:
            data = json.load(f)
        owner = Owner(data["owner"])
        for pet_data in data["pets"]:
            pet = Pet(pet_data["name"], pet_data["species"])
            for task_data in pet_data["tasks"]:
                pet.add_task(Task(**task_data))
            owner.add_pet(pet)
        return cls(owner)
