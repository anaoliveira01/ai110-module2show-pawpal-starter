# PawPal+ User Interface Guide

## Streamlit App Features

The `app.py` Streamlit interface provides an intuitive way to interact with the smart scheduler:

### 🚨 Conflict Detection & Warnings
Real-time detection of overlapping tasks with actionable suggestions:
- Displays conflicting task pairs with time overlaps
- Shows whether conflicts are same-pet or cross-pet (different issues)
- Provides remediation suggestions (reschedule or remove tasks)

### 🔄 Smart Recurring Tasks
Visual table showing all recurring tasks:
- Displays which tasks repeat daily or weekly
- Explains that marked-complete recurring tasks auto-generate next occurrence
- Shows priority and duration for each recurring task

### 📊 Professional Sorting & Filtering
Multiple view modes to organize the schedule:
- **Chronological View:** Tasks sorted by time (8am < 9am < 10am) with unscheduled tasks at end
- **Priority View:** High-priority tasks first (🔴 High > 🟠 Medium > 🟡 Low)
- **Pet Filtering:** Multi-select specific pets or view all
- **Status Filtering:** View pending ⏳, completed ✅, or all tasks
- Real-time captions explain the sorting methodology

### 📋 Clear Task Display
Easy-to-scan schedule table with:
- Color-coded priority indicators (emojis for quick visual scanning)
- Time-formatted display (12-hour with AM/PM)
- Duration in minutes, recurring pattern, and completion status
- Auto-assignment indicator for tasks without pinned times

### ✅ Task Completion Workflow
Simple process for marking tasks done:
- Select pending tasks from a dropdown with context (pet name, time)
- Instant feedback on completion with recurring task notifications
- Auto-refresh to show updated schedule

### 💡 Algorithm Transparency
Learn how the scheduler works:
- Expander section explaining the scheduler's algorithm
- Details on priority-based assignment, conflict detection, and recurring task logic

## Running the App

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501` in your browser.

## Integration with Backend

The app uses these methods from `pawpal_system.py`:
- `Scheduler.buildSchedule()` — Generates the daily plan
- `Scheduler.sortByTime()` — Chronological sorting
- `Scheduler.detectConflicts()` — Detects overlapping tasks
- `Scheduler.filterByPet()` — Pet-name-based filtering
- `Scheduler.filterByStatus()` — Completion-status filtering
- `Scheduler.getRecurringTasks()` — Lists all recurring tasks
- `Scheduler.completeTask()` — Marks tasks done and auto-generates next recurrence
- `Task.markComplete()` — Updates completion date
- `Task.nextOccurrence()` — Creates next instance of recurring task
