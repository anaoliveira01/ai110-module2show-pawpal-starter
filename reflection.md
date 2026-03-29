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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
