from datetime import time
from pawpal_system import Task, Pet, Owner


def main():
    # Create an Owner with available time slots
    owner = Owner(
        name="Alex",
        availableTimes=[
            time(8, 0),   # 8:00 AM
            time(12, 0),  # 12:00 PM
            time(17, 0),  # 5:00 PM
            time(20, 0),  # 8:00 PM
        ]
    )

    # Create Pets
    buddy = Pet(name="Buddy", age=3, species="Dog")
    whiskers = Pet(name="Whiskers", age=5, species="Cat")

    # Add pets to owner
    owner.addPet(buddy)
    owner.addPet(whiskers)

    # Create Tasks for Buddy (Dog)
    task1 = Task(
        taskName="Morning Walk",
        description="Take Buddy for a walk in the park",
        durationMinutes=time(0, 30),  # 30 minutes
        priority=3,  # High priority
    )
    buddy.addTask(task1)

    task2 = Task(
        taskName="Feeding - Lunch",
        description="Feed Buddy lunch kibble",
        durationMinutes=time(0, 15),  # 15 minutes
        priority=3,  # High priority
    )
    buddy.addTask(task2)

    # Create Tasks for Whiskers (Cat)
    task3 = Task(
        taskName="Feeding - Breakfast",
        description="Feed Whiskers breakfast",
        durationMinutes=time(0, 10),  # 10 minutes
        priority=3,  # High priority
    )
    whiskers.addTask(task3)

    # Build the daily schedule
    scheduler = owner.getSchedule()
    scheduler.buildSchedule()

    # Print Today's Schedule
    print("=" * 50)
    print("TODAY'S SCHEDULE")
    print("=" * 50)
    print()

    daily_plan = scheduler.getDailyPlan()

    if not daily_plan:
        print("No tasks scheduled for today.")
    else:
        for i, task in enumerate(daily_plan, 1):
            time_str = task.timeSlot.strftime("%I:%M %p") if task.timeSlot else "TBD"
            duration_str = f"{task.durationMinutes.hour}h {task.durationMinutes.minute}m" if task.durationMinutes.hour > 0 else f"{task.durationMinutes.minute}m"
            priority_str = ["Low", "Medium", "High"][task.priority - 1] if task.priority in [1, 2, 3] else "Unknown"
            
            print(f"{i}. {task.taskName}")
            print(f"   Time: {time_str}")
            print(f"   Duration: {duration_str}")
            print(f"   Priority: {priority_str}")
            print(f"   Pet: {task.pet.name}")
            print(f"   Description: {task.description}")
            print()

    # Print owner and pets summary
    print("=" * 50)
    print("OWNER & PETS SUMMARY")
    print("=" * 50)
    print(f"Owner: {owner.name}")
    print(f"Number of Pets: {len(owner.getPets())}")
    for pet in owner.getPets():
        print(f"  - {pet.name} ({pet.species}), Age: {pet.age}")
        print(f"    Tasks: {len(pet.getTasks())}")
    print()


if __name__ == "__main__":
    main()
