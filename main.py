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

    # Create Tasks OUT OF ORDER to test sorting
    # Task 3: Low priority cat task (added first)
    task3 = Task(
        taskName="Feeding - Breakfast",
        description="Feed Whiskers breakfast",
        durationMinutes=time(0, 10),  # 10 minutes
        priority=1,  # Low priority
    )
    whiskers.addTask(task3)

    # Task 1: High priority dog task (added second)
    task1 = Task(
        taskName="Morning Walk",
        description="Take Buddy for a walk in the park",
        durationMinutes=time(0, 30),  # 30 minutes
        priority=3,  # High priority
    )
    buddy.addTask(task1)

    # Task 2: High priority dog task (added third)
    task2 = Task(
        taskName="Feeding - Lunch",
        description="Feed Buddy lunch kibble",
        durationMinutes=time(0, 15),  # 15 minutes
        priority=3,  # High priority
    )
    buddy.addTask(task2)

    # Task 4: Medium priority cat task (added last)
    task4 = Task(
        taskName="Grooming",
        description="Brush Whiskers",
        durationMinutes=time(0, 20),  # 20 minutes
        priority=2,  # Medium priority
    )
    whiskers.addTask(task4)

    # Build the daily schedule
    scheduler = owner.getSchedule()
    scheduler.buildSchedule()

    # ========== SECTION 1: TODAY'S FULL SCHEDULE ==========
    print("=" * 50)
    print("TODAY'S FULL SCHEDULE (sorted by time)")
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
            status_str = "✓ Completed" if task.isCompleted else "○ Pending"
            
            print(f"{i}. {task.taskName} [{status_str}]")
            print(f"   Time: {time_str}")
            print(f"   Duration: {duration_str}")
            print(f"   Priority: {priority_str}")
            print(f"   Pet: {task.pet.name}")
            print(f"   Description: {task.description}")
            print()

    # ========== SECTION 2: FILTER BY PET ==========
    print("=" * 50)
    print("FILTERING BY PET")
    print("=" * 50)
    print()

    # Show tasks for each pet
    for pet in owner.getPets():
        pet_tasks = scheduler.filterByPet(pet.name)
        print(f"Tasks for {pet.name} ({len(pet_tasks)} tasks):")
        for task in pet_tasks:
            time_str = task.timeSlot.strftime("%I:%M %p") if task.timeSlot else "TBD"
            print(f"  • {task.taskName} at {time_str}")
        print()

    # ========== SECTION 3: MARK TASKS AS COMPLETED ==========
    print("=" * 50)
    print("COMPLETING SOME TASKS")
    print("=" * 50)
    print()

    # Mark first two tasks as completed
    daily_plan[0].markComplete()
    daily_plan[1].markComplete()
    
    print(f"Marked '{daily_plan[0].taskName}' as completed")
    print(f"Marked '{daily_plan[1].taskName}' as completed")
    print()

    # ========== SECTION 4: FILTER BY COMPLETION STATUS ==========
    print("=" * 50)
    print("FILTERING BY COMPLETION STATUS")
    print("=" * 50)
    print()

    # Show pending tasks
    pending_tasks = scheduler.filterByStatus(False)
    print(f"Pending tasks ({len(pending_tasks)} tasks):")
    for task in pending_tasks:
        time_str = task.timeSlot.strftime("%I:%M %p") if task.timeSlot else "TBD"
        print(f"  ○ {task.taskName} ({task.pet.name}) at {time_str}")
    print()

    # Show completed tasks
    completed_tasks = scheduler.filterByStatus(True)
    print(f"Completed tasks ({len(completed_tasks)} tasks):")
    for task in completed_tasks:
        time_str = task.timeSlot.strftime("%I:%M %p") if task.timeSlot else "TBD"
        print(f"  ✓ {task.taskName} ({task.pet.name}) at {time_str}")
    print()

    # ========== SECTION 5: SORT BY TIME ==========
    print("=" * 50)
    print("TASKS SORTED BY TIME")
    print("=" * 50)
    print()

    sorted_tasks = scheduler.sortByTime()
    for i, task in enumerate(sorted_tasks, 1):
        time_str = task.timeSlot.strftime("%I:%M %p") if task.timeSlot else "TBD"
        status_str = "✓" if task.isCompleted else "○"
        priority_mark = "!!!" if task.priority == 3 else ("!" if task.priority == 2 else "")
        print(f"{i}. [{time_str}] {status_str} {task.taskName} {priority_mark} ({task.pet.name})")
    print()

    # ========== SECTION 6: CONFLICT DETECTION ==========
    print("=" * 60)
    print("CONFLICT DETECTION")
    print("=" * 60)
    print()

    # Pin two tasks to the exact same start time to force a conflict.
    # task_conflict_a and task_conflict_b both start at 9:00 AM,
    # so their windows overlap regardless of duration.
    task_conflict_a = Task(
        taskName="Vet Appointment",
        description="Buddy annual checkup",
        durationMinutes=time(0, 45),  # 45 minutes
        priority=3,
        timeSlot=time(9, 0),          # pinned: 9:00 AM
    )
    buddy.addTask(task_conflict_a)

    task_conflict_b = Task(
        taskName="Nail Trim",
        description="Whiskers nail trim",
        durationMinutes=time(0, 20),  # 20 minutes
        priority=2,
        timeSlot=time(9, 0),          # pinned: 9:00 AM — same slot, triggers cross-pet conflict
    )
    whiskers.addTask(task_conflict_b)

    # Rebuild so the scheduler picks up the two new pinned tasks
    scheduler.buildSchedule()

    conflicts = scheduler.detectConflicts()
    if conflicts:
        print(f"WARNING: {len(conflicts)} conflict(s) found:")
        for msg in conflicts:
            print(f"  ⚠ {msg}")
    else:
        print("No conflicts detected.")
    print()

    # ========== SECTION 7: OWNER & PETS SUMMARY  ==========
    print("=" * 50)
    print("OWNER & PETS SUMMARY")
    print("=" * 50)
    print(f"Owner: {owner.name}")
    print(f"Number of Pets: {len(owner.getPets())}")
    for pet in owner.getPets():
        print(f"  - {pet.name} ({pet.species}), Age: {pet.age}")
        print(f"    Total Tasks: {len(pet.getTasks())}")
    print()


if __name__ == "__main__":
    main()

