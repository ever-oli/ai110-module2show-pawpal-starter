"""PawPal+ CLI demo: builds a sample household and exercises the Scheduler."""

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # 1. Create an owner and two pets
    owner = Owner("Ever")
    biscuit = Pet("Biscuit", "Golden Retriever")
    noodle = Pet("Noodle", "Tabby Cat")
    owner.add_pet(biscuit)
    owner.add_pet(noodle)

    # 2. Add tasks OUT of order to prove sorting works
    biscuit.add_task(Task("Evening walk", "18:30", 30, "daily", "medium"))
    biscuit.add_task(Task("Morning walk", "08:00", 30, "daily", "high"))
    biscuit.add_task(Task("Heartworm meds", "08:00", 5, "weekly", "high"))
    noodle.add_task(Task("Clean litter box", "20:00", 10, "daily", "medium"))
    noodle.add_task(Task("Feed breakfast", "07:30", 5, "daily", "high"))
    noodle.add_task(Task("Laser pointer play", "16:00", 15, "once", "low"))

    scheduler = Scheduler(owner)

    # 3. Today's schedule (priority first, then time) + conflict warning
    print(scheduler.format_schedule())

    # 4. Filtering demos
    print("\n🔎 Just Biscuit's tasks:")
    for pet, task in scheduler.filter_by_pet("Biscuit"):
        print(f"  {task.time}  {task.description}")

    # 5. Recurrence demo: complete a daily task, next one appears
    print("\n✅ Completing 'Feed breakfast' (daily)...")
    breakfast = noodle.get_tasks()[1]
    new_task = scheduler.mark_task_complete(breakfast)
    print(f"   New occurrence created for {new_task.due_date} at {new_task.time}")
    print(f"   Noodle's task count is now {noodle.task_count()}")

    # 6. Persistence demo
    scheduler.save_to_json("data.json")
    restored = Scheduler.load_from_json("data.json")
    print(f"\n💾 Saved and reloaded: {restored.owner.name} has "
          f"{len(restored.owner.pets)} pets and "
          f"{len(restored.owner.get_all_tasks())} tasks.")


if __name__ == "__main__":
    main()
