import copy
from datetime import date, time


class Task:
    def __init__(self, taskName: str, description: str, durationMinutes: time, priority: int, timeSlot: time = None):
        """Initialize a new task with details and tracking properties."""
        self.taskName = taskName
        self.description = description
        self.durationMinutes = durationMinutes  # e.g. time(0, 30) = 30 min
        self.priority = priority                # 1 = low, 2 = medium, 3 = high
        self.timeSlot = timeSlot
        self.pet: "Pet" = None                  # back-reference to owning Pet
        self.isCompleted = False
        self.completedDate: date = None
    
    def markComplete(self) -> bool:
        """Mark task as completed with current date."""
        self.isCompleted = True
        self.completedDate = date.today()
        return True


class Pet:
    def __init__(self, name: str, age: int, species: str):
        """Initialize a pet with basic information and an empty task list."""
        self.name = name
        self.age = age
        self.species = species
        self.tasks: list[Task] = []
        self.owner: "Owner" = None              # back-reference to owning Owner

    def addTask(self, task: Task) -> bool:
        """Add a task to the pet's task list."""
        task.pet = self
        self.tasks.append(task)
        return True

    def getTasks(self) -> list[Task]:
        """Return the list of tasks assigned to this pet."""
        return self.tasks


class Scheduler:
    def __init__(self, owner: "Owner", schedule_date: date = None):
        """Initialize a scheduler for an owner on a given date."""
        self.owner = owner
        self.date = schedule_date or date.today()
        self.dailyTasks: list[Task] = []

    def _to_minutes(self, t: time) -> int:
        """Convert a time object to minutes since midnight."""
        return t.hour * 60 + t.minute

    def _assign_slots(self, sorted_tasks: list[Task]) -> list[Task]:
        """Assign time slots to tasks, skipping slots where the task duration causes a conflict."""
        scheduled = []
        slots = sorted(self.owner.availableTimes)
        slot_idx = 0

        for task in sorted_tasks:
            task_mins = self._to_minutes(task.durationMinutes)

            while slot_idx < len(slots):
                slot = slots[slot_idx]
                slot_start = self._to_minutes(slot)

                # Check task fits before next slot starts
                if slot_idx + 1 < len(slots):
                    next_slot_start = self._to_minutes(slots[slot_idx + 1])
                    fits = slot_start + task_mins <= next_slot_start
                else:
                    fits = True  # last slot, no conflict possible

                slot_idx += 1
                if fits:
                    task.timeSlot = slot
                    scheduled.append(task)
                    break  # move to next task

        return scheduled

    def buildSchedule(self) -> None:
        """Build a daily schedule by assigning tasks to available time slots."""
        # Work on copies so original Task objects on Pet are never mutated
        all_tasks = [copy.copy(task) for pet in self.owner.getPets() for task in pet.getTasks()]

        sorted_tasks = sorted(
            all_tasks,
            key=lambda t: (-t.priority, self._to_minutes(t.durationMinutes))
        )

        self.dailyTasks = self._assign_slots(sorted_tasks)

    def addTask(self, task: Task) -> bool:
        """Add a task to the daily schedule and re-sort with new time assignments."""
        self.dailyTasks.append(copy.copy(task))
        # Re-sort and re-assign slots to keep the list consistent
        self.dailyTasks = sorted(
            self.dailyTasks,
            key=lambda t: (-t.priority, self._to_minutes(t.durationMinutes))
        )
        self.dailyTasks = self._assign_slots(self.dailyTasks)
        return True

    def removeTask(self, task: Task) -> bool:
        """Remove a task from the daily schedule by name and pet."""
        for t in self.dailyTasks:
            if t.taskName == task.taskName and t.pet == task.pet:
                self.dailyTasks.remove(t)
                return True
        return False

    def getDailyPlan(self) -> list[Task]:
        """Return the list of scheduled tasks for the day."""
        return self.dailyTasks


class Owner:
    def __init__(self, name: str, availableTimes: list[time] = None):
        """Initialize an owner with name, availability, and empty pet list."""
        self.name = name
        self.availableTimes = availableTimes or []
        self.pets: list[Pet] = []
        self._scheduler: Scheduler = None

    def addPet(self, pet: Pet) -> bool:
        """Add a pet to the owner's collection."""
        pet.owner = self
        self.pets.append(pet)
        return True

    def getPets(self) -> list[Pet]:
        """Return the list of pets owned by this owner."""
        return self.pets

    def getSchedule(self) -> Scheduler:
        """Return or create the scheduler for this owner."""
        if self._scheduler is None:
            self._scheduler = Scheduler(owner=self)
        return self._scheduler
