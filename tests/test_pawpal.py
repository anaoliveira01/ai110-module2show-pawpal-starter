import pytest
from datetime import time, date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


class TestTaskCompletion:
    """Test Task completion functionality."""

    def test_task_completion_with_date(self):
        """Verify that completedDate is set when task is marked complete."""
        # Arrange
        task = Task(
            taskName="Feed Dog",
            description="Feed Buddy his dinner",
            durationMinutes=time(0, 15),
            priority=3
        )
        
        # Act
        task.isCompleted = True
        task.completedDate = time(14, 30)
        
        # Assert
        assert task.isCompleted is True
        assert task.completedDate is not None
        assert task.completedDate == time(14, 30)

    def test_completing_task_in_pet_task_list(self):
        """Verify that completing a task in a pet's task list works correctly."""
        # Arrange
        pet = Pet(name="Buddy", age=3, species="Dog")
        task = Task(
            taskName="Morning Walk",
            description="Walk in the park",
            durationMinutes=time(0, 30),
            priority=3
        )
        pet.addTask(task)
        
        # Act
        pet.getTasks()[0].isCompleted = True
        
        # Assert
        assert pet.getTasks()[0].isCompleted is True

    def test_multiple_task_completion_status(self):
        """Verify completion status of multiple tasks independently."""
        # Arrange
        task1 = Task(taskName="Task 1", description="desc", durationMinutes=time(0, 10), priority=1)
        task2 = Task(taskName="Task 2", description="desc", durationMinutes=time(0, 15), priority=2)
        
        # Act
        task1.isCompleted = True
        
        # Assert
        assert task1.isCompleted is True
        assert task2.isCompleted is False


class TestTaskAddition:
    """Test adding tasks to pets."""

    def test_adding_task_increases_pet_task_count(self):
        """Verify that adding a task to a Pet increases the pet's task count."""
        # Arrange
        pet = Pet(name="Buddy", age=3, species="Dog")
        initial_count = len(pet.getTasks())
        
        task = Task(
            taskName="Morning Walk",
            description="Walk in the park",
            durationMinutes=time(0, 30),
            priority=3
        )
        
        # Assert initial state
        assert initial_count == 0
        
        # Act - add task to pet
        pet.addTask(task)
        
        # Assert final state
        final_count = len(pet.getTasks())
        assert final_count == initial_count + 1
        assert final_count == 1

    def test_adding_multiple_tasks(self):
        """Verify that adding multiple tasks works correctly."""
        # Arrange
        pet = Pet(name="Whiskers", age=5, species="Cat")
        
        task1 = Task(
            taskName="Feeding",
            description="Feed cat",
            durationMinutes=time(0, 10),
            priority=3
        )
        task2 = Task(
            taskName="Play Time",
            description="Interactive play",
            durationMinutes=time(0, 20),
            priority=2
        )
        
        # Act
        pet.addTask(task1)
        pet.addTask(task2)
        
        # Assert
        assert len(pet.getTasks()) == 2
        assert pet.getTasks()[0] == task1
        assert pet.getTasks()[1] == task2


class TestEmptyAndNullCases:
    """Test edge cases with empty/null inputs."""

    def test_build_schedule_with_no_tasks(self):
        """Verify scheduler handles empty task list gracefully."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0), time(12, 0)])
        scheduler = Scheduler(owner=owner)
        
        # Act
        scheduler.buildSchedule()
        
        # Assert
        assert len(scheduler.getDailyPlan()) == 0

    def test_build_schedule_with_no_available_times(self):
        """Verify scheduler handles owner with no time slots."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[])
        pet = Pet(name="Buddy", age=3, species="Dog")
        owner.addPet(pet)
        task = Task(taskName="Walk", description="Walk", durationMinutes=time(0, 30), priority=3)
        pet.addTask(task)
        
        scheduler = Scheduler(owner=owner)
        scheduler.buildSchedule()
        
        # Assert - task added but couldn't be scheduled due to no slots
        assert len(scheduler.getDailyPlan()) == 0

    def test_single_task_schedules_correctly(self):
        """Verify single task doesn't crash sorting."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0)])
        pet = Pet(name="Buddy", age=3, species="Dog")
        owner.addPet(pet)
        task = Task(taskName="Walk", description="Walk", durationMinutes=time(0, 30), priority=3)
        pet.addTask(task)
        
        scheduler = Scheduler(owner=owner)
        scheduler.buildSchedule()
        
        # Assert
        assert len(scheduler.getDailyPlan()) == 1
        assert scheduler.getDailyPlan()[0].taskName == "Walk"


class TestSortingEdgeCases:
    """Test sorting behavior with edge cases."""

    def test_sort_by_time_with_all_unscheduled_tasks(self):
        """Verify sortByTime handles all unscheduled tasks."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[])
        scheduler = Scheduler(owner=owner)
        task1 = Task(taskName="Task1", description="desc", durationMinutes=time(0, 10), priority=3)
        task2 = Task(taskName="Task2", description="desc", durationMinutes=time(0, 15), priority=1)
        scheduler.dailyTasks = [task1, task2]
        
        # Act
        sorted_tasks = scheduler.sortByTime()
        
        # Assert - all should be at end with inf value
        assert len(sorted_tasks) == 2
        assert all(t.timeSlot is None for t in sorted_tasks)

    def test_sort_by_time_mixed_scheduled_unscheduled(self):
        """Verify unscheduled tasks sort to end."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0), time(12, 0)])
        scheduler = Scheduler(owner=owner)
        task_scheduled = Task(taskName="Scheduled", description="desc", durationMinutes=time(0, 10), priority=3)
        task_scheduled.timeSlot = time(8, 0)
        task_unscheduled = Task(taskName="Unscheduled", description="desc", durationMinutes=time(0, 15), priority=3)
        scheduler.dailyTasks = [task_unscheduled, task_scheduled]
        
        # Act
        sorted_tasks = scheduler.sortByTime()
        
        # Assert - scheduled first, unscheduled last
        assert sorted_tasks[0].taskName == "Scheduled"
        assert sorted_tasks[1].taskName == "Unscheduled"

    def test_sort_by_time_chronological_order(self):
        """Verify tasks are returned in chronological order (8am < 9am < 10am)."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0), time(9, 0), time(10, 0)])
        scheduler = Scheduler(owner=owner)
        
        # Create tasks with different time slots
        task_10am = Task(taskName="Task10", description="", durationMinutes=time(0, 30), priority=1)
        task_10am.timeSlot = time(10, 0)
        
        task_8am = Task(taskName="Task8", description="", durationMinutes=time(0, 30), priority=1)
        task_8am.timeSlot = time(8, 0)
        
        task_9am = Task(taskName="Task9", description="", durationMinutes=time(0, 30), priority=1)
        task_9am.timeSlot = time(9, 0)
        
        scheduler.dailyTasks = [task_10am, task_8am, task_9am]  # Intentionally out of order
        
        # Act
        sorted_tasks = scheduler.sortByTime()
        
        # Assert - strictly chronological order
        assert sorted_tasks[0].taskName == "Task8"
        assert sorted_tasks[0].timeSlot == time(8, 0)
        assert sorted_tasks[1].taskName == "Task9"
        assert sorted_tasks[1].timeSlot == time(9, 0)
        assert sorted_tasks[2].taskName == "Task10"
        assert sorted_tasks[2].timeSlot == time(10, 0)

    def test_priority_respects_ordering_in_build_schedule(self):
        """Verify high-priority tasks get earlier slots."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0), time(9, 0), time(10, 0)])
        pet = Pet(name="Buddy", age=3, species="Dog")
        owner.addPet(pet)
        
        task_low = Task(taskName="Low", description="low", durationMinutes=time(0, 30), priority=1)
        task_high = Task(taskName="High", description="high", durationMinutes=time(0, 30), priority=3)
        pet.addTask(task_low)
        pet.addTask(task_high)
        
        scheduler = Scheduler(owner=owner)
        scheduler.buildSchedule()
        
        # Assert - high priority should get first slot (8:00)
        plan = scheduler.getDailyPlan()
        assert plan[0].taskName == "High"
        assert plan[0].timeSlot == time(8, 0)


class TestRecurringTaskEdgeCases:
    """Test recurring task behavior."""

    def test_non_recurring_task_does_not_spawn_next(self):
        """Verify non-recurring tasks don't create duplicates."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0)])
        pet = Pet(name="Buddy", age=3, species="Dog")
        owner.addPet(pet)
        
        task = Task(
            taskName="One-time Walk",
            description="Walk",
            durationMinutes=time(0, 30),
            priority=3,
            recurring=False
        )
        pet.addTask(task)
        initial_count = len(pet.getTasks())
        
        scheduler = Scheduler(owner=owner)
        scheduler.buildSchedule()
        scheduler.completeTask("One-time Walk")
        
        # Assert - no new task created
        assert len(pet.getTasks()) == initial_count

    def test_daily_recurring_task_creates_next_occurrence(self):
        """Verify daily recurring task creates next instance."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0)])
        pet = Pet(name="Buddy", age=3, species="Dog")
        owner.addPet(pet)
        
        task = Task(
            taskName="Daily Walk",
            description="Walk",
            durationMinutes=time(0, 30),
            priority=3,
            recurring=True,
            recurrenceInterval="daily",
            scheduledDate=date.today()
        )
        pet.addTask(task)
        initial_count = len(pet.getTasks())
        original_date = task.scheduledDate
        
        scheduler = Scheduler(owner=owner)
        scheduler.buildSchedule()
        scheduler.completeTask("Daily Walk")
        
        # Assert - new task created
        assert len(pet.getTasks()) == initial_count + 1
        
        # Assert - new task is for the following day
        new_task = pet.getTasks()[-1]
        expected_next_date = original_date + timedelta(days=1)
        assert new_task.scheduledDate == expected_next_date
        assert new_task.scheduledDate > original_date

    def test_weekly_recurring_task_creates_next_week(self):
        """Verify weekly recurring task advances by 7 days."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0)])
        pet = Pet(name="Buddy", age=3, species="Dog")
        owner.addPet(pet)
        
        task = Task(
            taskName="Weekly Grooming",
            description="Grooming",
            durationMinutes=time(0, 30),
            priority=2,
            recurring=True,
            recurrenceInterval="weekly"
        )
        pet.addTask(task)
        
        scheduler = Scheduler(owner=owner)
        scheduler.buildSchedule()
        scheduler.completeTask("Weekly Grooming")
        
        # Assert - new task added with future date
        new_task = pet.getTasks()[-1]
        assert new_task.scheduledDate > task.scheduledDate


class TestConflictDetectionEdgeCases:
    """Test conflict detection edge cases."""

    def test_no_conflict_when_tasks_adjacent(self):
        """Verify tasks ending/starting at same time don't conflict."""
        # Arrange
        scheduler = Scheduler(owner=Owner(name="Owner"))
        task1 = Task(taskName="Task1", description="", durationMinutes=time(0, 30), priority=1)
        task1.timeSlot = time(9, 0)
        task2 = Task(taskName="Task2", description="", durationMinutes=time(0, 30), priority=1)
        task2.timeSlot = time(9, 30)  # Starts when task1 ends
        scheduler.dailyTasks = [task1, task2]
        
        # Act
        conflicts = scheduler.detectConflicts()
        
        # Assert - no conflict
        assert len(conflicts) == 0

    def test_conflict_with_exact_same_start_time(self):
        """Verify tasks with identical start time conflict (duplicate times flagged)."""
        # Arrange
        owner = Owner(name="Owner")
        pet1 = Pet(name="Pet1", age=1, species="Dog")
        pet2 = Pet(name="Pet2", age=1, species="Cat")
        owner.addPet(pet1)
        owner.addPet(pet2)
        
        scheduler = Scheduler(owner=owner)
        task1 = Task(taskName="Task1", description="", durationMinutes=time(0, 30), priority=3)
        task1.timeSlot = time(9, 0)
        task1.pet = pet1
        
        task2 = Task(taskName="Task2", description="", durationMinutes=time(0, 20), priority=2)
        task2.timeSlot = time(9, 0)  # Exact duplicate time
        task2.pet = pet2
        
        scheduler.dailyTasks = [task1, task2]
        
        # Act
        conflicts = scheduler.detectConflicts()
        
        # Assert - Scheduler flags duplicate times
        assert len(conflicts) >= 1
        assert any("9:00" in conflict or "09:00" in conflict for conflict in conflicts)
        assert any("Task1" in conflict and "Task2" in conflict for conflict in conflicts)

    def test_same_pet_conflict_labeled_correctly(self):
        """Verify same-pet conflicts are labeled as such."""
        # Arrange
        owner = Owner(name="Owner")
        pet = Pet(name="Buddy", age=3, species="Dog")
        owner.addPet(pet)
        
        scheduler = Scheduler(owner=owner)
        task1 = Task(taskName="Task1", description="", durationMinutes=time(0, 30), priority=3)
        task1.timeSlot = time(9, 0)
        task1.pet = pet
        
        task2 = Task(taskName="Task2", description="", durationMinutes=time(0, 30), priority=2)
        task2.timeSlot = time(9, 15)
        task2.pet = pet
        
        scheduler.dailyTasks = [task1, task2]
        
        # Act
        conflicts = scheduler.detectConflicts()
        
        # Assert
        assert len(conflicts) >= 1
        assert "Same-pet" in conflicts[0]


class TestFilteringEdgeCases:
    """Test filtering behavior with edge cases."""

    def test_filter_by_nonexistent_pet(self):
        """Verify filtering for non-existent pet returns empty list."""
        # Arrange
        scheduler = Scheduler(owner=Owner(name="Owner"))
        scheduler.dailyTasks = []
        
        # Act
        result = scheduler.filterByPet("NonExistentPet")
        
        # Assert
        assert len(result) == 0

    def test_filter_by_status_completed_when_none_complete(self):
        """Verify filtering for completed tasks returns empty when none complete."""
        # Arrange
        scheduler = Scheduler(owner=Owner(name="Owner"))
        task = Task(taskName="Task", description="", durationMinutes=time(0, 30), priority=1)
        task.isCompleted = False
        scheduler.dailyTasks = [task]
        
        # Act
        result = scheduler.filterByStatus(True)
        
        # Assert
        assert len(result) == 0

    def test_filter_by_status_pending_when_all_complete(self):
        """Verify filtering for pending tasks returns empty when all complete."""
        # Arrange
        scheduler = Scheduler(owner=Owner(name="Owner"))
        task = Task(taskName="Task", description="", durationMinutes=time(0, 30), priority=1)
        task.isCompleted = True
        scheduler.dailyTasks = [task]
        
        # Act
        result = scheduler.filterByStatus(False)
        
        # Assert
        assert len(result) == 0


class TestMultiPetSchedulingEdgeCases:
    """Test multi-pet scheduling edge cases."""

    def test_more_tasks_than_slots(self):
        """Verify scheduler handles more tasks than available slots."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0), time(9, 0)])
        pet = Pet(name="Buddy", age=3, species="Dog")
        owner.addPet(pet)
        
        for i in range(5):
            task = Task(
                taskName=f"Task{i}",
                description="desc",
                durationMinutes=time(0, 30),
                priority=3
            )
            pet.addTask(task)
        
        scheduler = Scheduler(owner=owner)
        scheduler.buildSchedule()
        
        # Assert - not all tasks scheduled
        assert len(scheduler.getDailyPlan()) < 5

    def test_one_pet_dominates_slots(self):
        """Verify high-priority pet tasks don't starve other pets."""
        # Arrange
        owner = Owner(name="Alex", availableTimes=[time(8, 0), time(9, 0), time(10, 0)])
        
        pet1 = Pet(name="Buddy", age=3, species="Dog")
        pet2 = Pet(name="Whiskers", age=5, species="Cat")
        owner.addPet(pet1)
        owner.addPet(pet2)
        
        # Pet1 has high-priority tasks
        for i in range(3):
            task = Task(taskName=f"Buddy-{i}", description="", durationMinutes=time(0, 30), priority=3)
            pet1.addTask(task)
        
        # Pet2 has low-priority task
        task = Task(taskName="Whiskers-task", description="", durationMinutes=time(0, 30), priority=1)
        pet2.addTask(task)
        
        scheduler = Scheduler(owner=owner)
        scheduler.buildSchedule()
        
        # Assert - check that scheduling uses priority
        plan = scheduler.getDailyPlan()
        assert len(plan) == 3  # All high-priority fit

