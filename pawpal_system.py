import copy
from datetime import date, time, timedelta


class Task:
    def __init__(self, taskName: str, description: str, durationMinutes: time, priority: int,
                 timeSlot: time = None, recurring: bool = False, recurrenceInterval: str = None,
                 scheduledDate: date = None):
        """Initialize a new task with details and tracking properties."""
        self.taskName = taskName
        self.description = description
        self.durationMinutes = durationMinutes  # e.g. time(0, 30) = 30 min
        self.priority = priority                # 1 = low, 2 = medium, 3 = high
        self.timeSlot = timeSlot
        self.pet: "Pet" = None                  # back-reference to owning Pet
        self.isCompleted = False
        self.completedDate: date = None
        self.recurring = recurring              # True if this task repeats
        self.recurrenceInterval = recurrenceInterval  # "daily" or "weekly"
        self.scheduledDate: date = scheduledDate or date.today()

    def markComplete(self) -> bool:
        """Mark task as completed with current date."""
        self.isCompleted = True
        self.completedDate = date.today()
        return True

    def nextOccurrence(self) -> "Task | None":
        """Return a new Task for the next recurrence, or None if not recurring."""
        if not self.recurring or self.recurrenceInterval not in ("daily", "weekly"):
            return None
        delta = timedelta(days=1) if self.recurrenceInterval == "daily" else timedelta(weeks=1)
        next_task = Task(
            taskName=self.taskName,
            description=self.description,
            durationMinutes=self.durationMinutes,
            priority=self.priority,
            timeSlot=self.timeSlot,
            recurring=self.recurring,
            recurrenceInterval=self.recurrenceInterval,
            scheduledDate=self.scheduledDate + delta,
        )
        next_task.pet = self.pet
        return next_task


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

    def _assign_slots(self, tasks: list[Task]) -> list[Task]:
        """Assign time slots from owner.availableTimes to tasks that have no preset slot."""
        scheduled = []
        slots = sorted(self.owner.availableTimes)
        slot_idx = 0

        for task in tasks:
            task_mins = self._to_minutes(task.durationMinutes)

            while slot_idx < len(slots):
                slot = slots[slot_idx]
                slot_start = self._to_minutes(slot)

                if slot_idx + 1 < len(slots):
                    next_slot_start = self._to_minutes(slots[slot_idx + 1])
                    fits = slot_start + task_mins <= next_slot_start
                else:
                    fits = True  # last slot, no overlap possible

                slot_idx += 1
                if fits:
                    task.timeSlot = slot
                    scheduled.append(task)
                    break

        return scheduled

    def buildSchedule(self) -> None:
        """Build a daily schedule.

        Tasks with a preset timeSlot keep their slot. Tasks without one are
        sorted by priority (high first) then assigned to owner.availableTimes.
        """
        all_tasks = [copy.copy(task) for pet in self.owner.getPets() for task in pet.getTasks()]

        direct = [t for t in all_tasks if t.timeSlot is not None]
        unscheduled = [t for t in all_tasks if t.timeSlot is None]

        unscheduled_sorted = sorted(
            unscheduled,
            key=lambda t: (-t.priority, self._to_minutes(t.durationMinutes))
        )

        self.dailyTasks = direct + self._assign_slots(unscheduled_sorted)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------
    def sortByTimeString(self) -> list[Task]:
        """Return tasks sorted by scheduled start time in HH:MM format."""
        return sorted(
            self.dailyTasks,
            key=lambda t: t.timeSlot.strftime("%H:%M") if t.timeSlot else "23:59"
        )
    def sortByTime(self) -> list[Task]:
        """Return tasks sorted by scheduled start time (unscheduled tasks last)."""
        return sorted(
            self.dailyTasks,
            key=lambda t: self._to_minutes(t.timeSlot) if t.timeSlot else float('inf')
        )

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def filterByPet(self, pet_name: str) -> list[Task]:
        """Return scheduled tasks for a specific pet by name."""
        return [t for t in self.dailyTasks if t.pet and t.pet.name == pet_name]

    def filterByStatus(self, completed: bool) -> list[Task]:
        """Return scheduled tasks matching the given completion status."""
        return [t for t in self.dailyTasks if t.isCompleted == completed]

    # ------------------------------------------------------------------
    # Recurring tasks
    # ------------------------------------------------------------------

    def getRecurringTasks(self) -> list[Task]:
        """Return all recurring tasks in the current schedule."""
        return [t for t in self.dailyTasks if t.recurring]

    # ------------------------------------------------------------------
    # Conflict detection
    # ------------------------------------------------------------------

    def _get_task_window(self, task: Task) -> tuple[int, int] | None:
        """
        Get the time window for a task in minutes.

        Args:
            task (Task): The task to calculate the time window for.

        Returns:
            tuple[int, int] | None: A tuple containing (start_minutes, end_minutes) 
                representing the task's time window, or None if the task has no 
                time slot assigned or an error occurs during conversion.

        Raises:
            None: Exceptions are caught internally and None is returned instead.
        """
        """Return (start_minutes, end_minutes) for a task, or None if invalid."""
        try:
            if task.timeSlot is None:
                return None
            start = self._to_minutes(task.timeSlot)
            duration = self._to_minutes(task.durationMinutes)
            return (start, start + duration)
        except Exception:
            return None

    def _tasks_overlap(self, window_a: tuple[int, int], window_b: tuple[int, int]) -> bool:
        """
        Determine whether two time windows overlap.

        Args:
            window_a (tuple[int, int]): A time window represented as (start, end).
            window_b (tuple[int, int]): Another time window represented as (start, end).

        Returns:
            bool: True if the windows overlap (a.start < b.end AND b.start < a.end), False otherwise.

        Example:
            >>> _tasks_overlap((1, 5), (3, 7))
            True
            >>> _tasks_overlap((1, 3), (5, 7))
            False
        """
        """Check if two time windows overlap: a.start < b.end AND b.start < a.end."""
        a_start, a_end = window_a
        b_start, b_end = window_b
        return a_start < b_end and b_start < a_end

    def _format_conflict_message(self, task_a: Task, task_b: Task, window_a: tuple[int, int]) -> str:
        """
        Format a human-readable conflict message for overlapping tasks.

        Args:
            task_a (Task): The first task involved in the conflict.
            task_b (Task): The second task involved in the conflict.
            window_a (tuple[int, int]): A tuple containing the start and end time indices for task_a.

        Returns:
            str: A formatted conflict message indicating the type of conflict (same-pet or cross-pet),
                 the task names, pet names, time slot, and duration of the conflict.
                 
                 Format: "{label} conflict: '{task_a_name}' ({pet_a}, {time}, {duration}min) overlaps '{task_b_name}' ({pet_b})"
                 
                 Where:
                 - label is "Same-pet" if both tasks belong to the same pet, "Cross-pet" otherwise
                 - pet names default to "unknown" if not assigned
                 - time is formatted as HH:MM AM/PM
                 - duration is in minutes
        """
        """Format a human-readable conflict message."""
        a_pet = task_a.pet.name if task_a.pet else "unknown"
        b_pet = task_b.pet.name if task_b.pet else "unknown"
        label = "Same-pet" if task_a.pet is task_b.pet else "Cross-pet"
        a_start, a_end = window_a
        duration = a_end - a_start
        time_str = task_a.timeSlot.strftime("%I:%M %p")
        return f"{label} conflict: '{task_a.taskName}' ({a_pet}, {time_str}, {duration}min) overlaps '{task_b.taskName}' ({b_pet})"

    def detectConflicts(self) -> list[str]:
        """Detect and return a list of conflict messages for overlapping scheduled tasks.
        This method identifies time slot conflicts between pairs of tasks in the daily schedule.
        It uses a caching strategy to pre-calculate time windows for all scheduled tasks,
        avoiding redundant recalculations during pairwise comparisons.
        Algorithm:
        1. Filter tasks that have assigned time slots (scheduled tasks)
        2. Pre-calculate and cache time windows for each scheduled task
        3. Compare all pairs of tasks to detect overlapping time windows
        4. Generate conflict messages for each overlapping pair
        Returns:
            list[str]: A list of warning/conflict messages including:
                - Invalid time data warnings for tasks with unparseable time information
                - Conflict messages for each pair of overlapping tasks
                Returns an empty list if no conflicts or invalid data is detected."""

        warnings = []
        scheduled = [t for t in self.dailyTasks if t.timeSlot is not None]
        
        # Pre-calculate all time windows to avoid recalculation
        windows = {}
        for task in scheduled:
            window = self._get_task_window(task)
            if window is None:
                warnings.append(f"Skipped '{task.taskName}' — invalid time data.")
            else:
                windows[id(task)] = window
        
        # Check all pairs for overlap
        for i, task_a in enumerate(scheduled):
            if id(task_a) not in windows:
                continue
            window_a = windows[id(task_a)]
            for task_b in scheduled[i + 1:]:
                if id(task_b) not in windows:
                    continue
                window_b = windows[id(task_b)]
                if self._tasks_overlap(window_a, window_b):
                    msg = self._format_conflict_message(task_a, task_b, window_a)
                    warnings.append(msg)
        
        return warnings

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def completeTask(self, task_name: str, pet_name: str = None) -> bool:
        """Mark a scheduled task complete and auto-queue the next occurrence if recurring.

        If the task is recurring, a new instance is automatically created and added
        to the pet's task list and the daily schedule for the next occurrence date.
        Returns True if the task was found and marked, False otherwise.
        """
        for t in self.dailyTasks:
            if t.taskName == task_name and (pet_name is None or (t.pet and t.pet.name == pet_name)):
                t.markComplete()
                next_task = t.nextOccurrence()
                if next_task is not None and t.pet is not None:
                    # Add the next occurrence to both the pet's task list and scheduler
                    t.pet.addTask(next_task)
                    self.dailyTasks.append(next_task)
                return True
        return False

    def addTask(self, task: Task) -> bool:
        """Add a task to the daily schedule and re-sort with new time assignments."""
        self.dailyTasks.append(copy.copy(task))
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
