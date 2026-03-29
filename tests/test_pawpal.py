import pytest
from datetime import time
from pawpal_system import Task, Pet, Owner


class TestTaskCompletion:
    """Test Task completion functionality."""

    def test_task_completion_status(self):
        """Verify that a task's isCompleted status changes when marked complete."""
        # Arrange
        task = Task(
            taskName="Feed Dog",
            description="Feed Buddy his dinner",
            durationMinutes=time(0, 15),
            priority=3
        )
        
        # Assert initial state
        assert task.isCompleted is False
        assert task.completedDate is None
        
        # Act - mark task as complete
        task.isCompleted = True
        
        # Assert final state
        assert task.isCompleted is True


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
