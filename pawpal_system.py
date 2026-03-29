from datetime import date, time


class Task:
    def __init__(self, taskName: str, description: str, durationMinutes: time, priority: int, timeSlot: time = None):
        self.taskName = taskName
        self.description = description
        self.durationMinutes = durationMinutes  # e.g. time(0, 30) = 30 min
        self.priority = priority                # 1 = low, 2 = medium, 3 = high
        self.timeSlot = timeSlot


class Pet:
    def __init__(self, name: str, age: int, species: str):
        self.name = name
        self.age = age
        self.species = species
        self.tasks: list[Task] = []

    def addTask(self, task: Task) -> bool:
        self.tasks.append(task)
        return True

    def getTasks(self) -> list[Task]:
        return self.tasks


class Scheduler:
    def __init__(self, owner: "Owner", date: date = None):
        self.owner = owner
        self.date = date or date.today()
        self.dailyTasks: list[Task] = []

    def buildSchedule(self) -> None:
        all_tasks = [task for pet in self.owner.getPets() for task in pet.getTasks()]

        # Sort by priority descending, then by duration ascending (shorter tasks first at same priority)
        self.dailyTasks = sorted(
            all_tasks,
            key=lambda t: (-t.priority, t.durationMinutes.hour * 60 + t.durationMinutes.minute)
        )

        # Assign available time slots in order
        for i, task in enumerate(self.dailyTasks):
            if i < len(self.owner.availableTimes):
                task.timeSlot = self.owner.availableTimes[i]

    def addTask(self, task: Task) -> bool:
        self.dailyTasks.append(task)
        return True

    def removeTask(self, task: Task) -> bool:
        if task in self.dailyTasks:
            self.dailyTasks.remove(task)
            return True
        return False

    def getDailyPlan(self) -> list[Task]:
        return self.dailyTasks


class Owner:
    def __init__(self, name: str, availableTimes: list[time] = None):
        self.name = name
        self.availableTimes = availableTimes or []
        self.pets: list[Pet] = []
        self._scheduler: Scheduler = None

    def addPet(self, pet: Pet) -> bool:
        self.pets.append(pet)
        return True

    def getPets(self) -> list[Pet]:
        return self.pets

    def getSchedule(self) -> Scheduler:
        if self._scheduler is None:
            self._scheduler = Scheduler(owner=self)
        return self._scheduler
