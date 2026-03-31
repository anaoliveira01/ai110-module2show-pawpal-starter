# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The Scheduler class includes advanced features for intelligent task planning:

- **Priority-based assignment:** High-priority tasks (feeding, meds) always get scheduled first using a greedy first-fit algorithm
- **Conflict detection:** Automatically detects overlapping tasks across pets and provides clear warnings
- **Flexible sorting:** Sort tasks by time or priority for different views
- **Pet-based filtering:** Filter the schedule by specific pets or completion status
- **Recurring tasks:** Daily/weekly tasks automatically generate the next occurrence when marked complete
- **Optimized performance:** Caches time window calculations to avoid redundant computation

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### Running Tests

Execute the comprehensive test suite with:

```bash
python -m pytest tests/test_pawpal.py -v
```

### Test Coverage

The test suite includes **23 comprehensive tests** covering:

- **Task Completion (3 tests):** Verify tasks mark complete with date tracking, and completion status works independently across tasks
- **Task Addition (2 tests):** Confirm tasks correctly add to pets' task lists with proper ordering
- **Empty/Null Cases (3 tests):** Ensure scheduler handles edge cases like no tasks, no available time slots, and single tasks
- **Sorting Correctness (4 tests):** Verify tasks return in chronological order (8am < 9am < 10am), handle mixed scheduled/unscheduled tasks, and respect priority-based ordering
- **Recurrence Logic (3 tests):** Confirm daily/weekly recurring tasks create next occurrences with proper date advancement, and non-recurring tasks don't duplicate
- **Conflict Detection (3 tests):** Verify scheduler flags duplicate times, detects overlaps, and distinguishes same-pet vs cross-pet conflicts
- **Filtering Behavior (3 tests):** Test filtering by pet name and completion status, including nonexistent pets and empty result sets
- **Multi-Pet Scheduling (2 tests):** Ensure fair task distribution and proper handling of more tasks than available slots

### Test Results

**All 23 tests pass** with no failures or warnings

### Confidence Level: (5/5)

The comprehensive test suite validates all critical system behaviors:
- **Sorting:** Chronological ordering verified with explicit time assertions
- **Recurrence:** Next-occurrence dates validated with `timedelta` calculations
- **Conflict Detection:** Duplicate times flagged and reported with specific time references
- **Edge Cases:** Empty inputs, boundary conditions, and multi-pet scenarios all tested
- **Integration:** Task completion, addition, filtering, and scheduling all work together correctly

The system has high confidence in reliability across all major features.
