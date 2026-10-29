# Habit Tracker

A small, quiet desktop app for keeping daily habits. Dark interface, cyan accents,
no account, no internet, no telemetry. Everything is stored in one JSON file on your
own machine.

![icon](assets/icon.png)

## What it does

- Add habits with a colour and a target of 1-7 days a week
- Tick a habit off with a single click, or with the space bar
- **Current streak**, **best streak**, days done **this week**, and a **30-day rate**
- A five-week heatmap for the selected habit, today outlined in cyan
- Export everything to CSV
- Saves automatically after every change

## Where your data lives

```
%APPDATA%\NexusHabitTracker\data.json
```

A single readable file. Back it up by copying it. If it is ever corrupted, the app
renames it to `data.json.corrupt` and starts fresh rather than crashing.

## Keyboard

| Key | Action |
|---|---|
| `Ctrl + N` | new habit |
| `Space` | tick / untick the selected habit |
| `Delete` | delete the selected habit (asks first) |
| `Esc` | deselect |
| mouse wheel | scroll the list |

## Running it

Double-click `HabitTracker.exe`. Nothing to install, no dependencies, no admin rights.
Windows 10 or 11.

## Building it yourself

The app is plain Python with `tkinter`, so the only build dependency is PyInstaller.

```
build.bat
```

That produces `dist\HabitTracker.exe` — a single file you can copy anywhere.

## Files

| File | Purpose |
|---|---|
| `habit_tracker.py` | the interface |
| `habit_store.py` | storage, streaks and statistics (no screen needed, tested on its own) |
| `make_icon.py` | generates `assets/icon.ico` with no image library |
| `build.bat` | builds the single-file executable |

## Notes on behaviour

- A streak counts consecutive days **up to today**; a day not yet ticked does not break it.
- The 30-day rate starts counting from the day the habit was created, so a new habit
  is not punished for the days before it existed.
- Deleting a habit deletes its history, and asks for confirmation first.
