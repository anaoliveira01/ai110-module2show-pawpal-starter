# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design models a pet care scheduling system with four classes: `Owner`, `Pet`, `Task`, and `Scheduler`.

- **Owner** — stores the owner's name and available times, and holds a list of pets. It is responsible for managing pets (`addPet`, `getPets`) and accessing the scheduler (`getSchedule`).
- **Pet** — stores the pet's name, age, and species, and maintains its own list of assigned tasks. It is responsible for managing tasks at the pet level (`addTask`, `getTasks`).
- **Task** — represents a single care activity with a name, description, duration in minutes, priority, and an assigned time slot.
- **Scheduler** — owns a reference to the `Owner` and manages the full list of daily tasks. It is responsible for building the schedule (`buildSchedule`), modifying tasks (`addTask`, `removeTask`), and returning the final daily plan (`getDailyPlan`).

`Owner` owns one or more `Pet`s, uses one `Scheduler`, and the `Scheduler` contains zero or more `Task`s. Each `Pet` can also be directly assigned zero or more `Task`s.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, significantly. The initial UML showed the class structure but didn't account for the sorting and filtering logic I implemented. I added dedicated methods (`sortByTime()`, `sortByPriority()`, `filterByPet()`, `filterByStatus()`, `detectConflicts()`, `getRecurringTasks()`) to keep the Scheduler class focused and testable. I also realized I needed to track the scheduler reference in Owner to enable proper data flow. The biggest change was recognizing that conflict detection required timestamp caching to avoid redundant calculations—this wasn't obvious from the initial design but became essential for performance.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers: (1) time constraints—each task has a fixed duration and must fit within available hours; (2) priority levels—tasks marked "High" or "Urgent" get scheduled first; (3) pet assignments—tasks are tied to specific pets and must be grouped appropriately; (4) conflict detection—no two tasks for the same pet can overlap. I decided priority mattered most because pet care has non-negotiable tasks (feeding, medication) that must always fit. Time was the hard constraint—if a task doesn't fit, it doesn't fit. Pet grouping was nice-to-have but less critical than ensuring high-priority tasks got slots.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes

My scheduler uses a greedy first-fit algorithm: it assigns high-priority tasks first, then moves down the list without reconsidering. This trades **optimal packing for O(n) speed**—some low-priority tasks may not fit even if rearranging would work.

- Why is that tradeoff reasonable for this scenario?

Pet owners need quick feedback, and "good enough fast" beats "perfect slow." High-priority tasks (feeding, meds) are always guaranteed slots, which matters more than fitting every task. Pet schedules are flexible anyway.


---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI for implementation across all phases: generating class stubs and algorithms (greedy scheduling, conflict detection, sorting/filtering), drafting 23 comprehensive tests, refactoring over-engineered code based on feedback, and building the Streamlit UI. The most helpful prompts were specific requests ("remove unnecessary things ") and algorithm-focused questions ("refactor this unreadable method"), which produced better results than vague suggestions. Explaining the "why" behind features (e.g., "recurring tasks should auto-generate when marked complete") helped AI implement the right solution.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I rejected AI's initial over-engineered implementation with dozens of convenience methods. Instead of accepting all suggestions, I verified the code against the project requirements, ran the test suite (23/23 tests pass), and kept only methods that were actually used. This taught me that AI generates working code quickly, but human judgment on scope and design is essential.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested 23 behaviors across 8 categories: task completion with date tracking, task addition, empty/null edge cases, sorting correctness (chronological order), recurrence logic (daily/weekly auto-generation), conflict detection (overlapping times), filtering (by pet and status), and multi-pet scheduling. These tests were critical because they validate the core algorithms (scheduling, sorting, conflict detection, recurrence) that define PawPal+ reliability. All tests passing (100%) confirms the system handles real-world scenarios and edge cases correctly.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Very confident (5/5 stars) - all 23 tests pass with explicit assertions on sorting order, date advancement, and conflict messages. If I had more time, I'd test: scheduling with more pets than time slots, conflicting recurring tasks, timezone handling, and long-term recurrence (monthly tasks, leap years).

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the test suite and the recurring task logic. Writing 23 comprehensive tests forced me to think through edge cases (empty lists, conflicting tasks, multi-pet scheduling) and gave me genuine confidence in the system. visually clear.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd redesign the constraint system to distinguish hard constraints (must satisfy) from soft constraints (prefer to satisfy). Currently, everything is hard, which can make scheduling fail even when partial solutions would be useful. I'd also add persistent storage so schedules survive a restart, and implement a more sophisticated scheduling algorithm—the greedy approach works well but a greedy with backtracking or even a simple optimization pass could pack schedules better. Timezone/DST handling for long-term recurring tasks would be important too.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

By keeping Owner, Pet, Task, and Scheduler as separate responsibilities, each backed by focused tests, I built something I could reason about and modify confidently. AI made rapid prototyping possible, but human judgment—deciding what to keep, what to cut, what tradeoffs matter—was essential. I also learned that tests aren't overhead; they're the actual proof that a system works. With 23 passing tests, I know my scheduler handles the real cases, not just the happy path.
