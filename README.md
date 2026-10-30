# Habit Tracker

A quiet daily habit tracker in two forms: a **Windows desktop app** and an **Android app**.
Dark interface, cyan accents, no account, no internet connection, no telemetry. Everything is
stored on your own device.

## What it does

- Add habits with a colour and a target of 1–7 days a week
- Tick one off with a click (desktop) or a tap (Android)
- **Current streak**, **best streak**, days done **this week**, and a **30-day rate**
- A five-week heatmap for the selected habit, with today ringed in cyan
- A weekday bar chart showing which days you actually keep
- Delete asks first; everything saves automatically

## The two versions

| Folder | What it is | Runs on |
|---|---|---|
| `desktop/` | Python + tkinter app, built with PyInstaller | Windows 10 / 11 |
| `android/` | Single-activity WebView app, built with the Android SDK tools | Android 7.0+ |
| `release/` | The built files: `HabitTracker.exe` and `HabitTracker.apk` | — |

Both share the same behaviour and the same statistics — the Android version is the same
interface rebuilt for touch.

## Where the data lives

- **Desktop:** `%APPDATA%\NexusHabitTracker\data.json`
- **Android:** app storage (`localStorage` of the WebView)

A single readable file on the desktop. If it is ever corrupted, the desktop app sets it aside
as `data.json.corrupt` and starts fresh instead of crashing.

## Building

**Desktop**

```
cd desktop
build.bat
```

Produces `dist\HabitTracker.exe` — one file, no installation, no admin rights.

**Android**

The `android/` folder is built with the Android SDK command-line tools only (no Gradle):
`javac` → `d8` → `aapt2` → `zipalign` → `apksigner`. The page lives in `android/assets/` and the
Java wrapper is a single `WebView`. Requires JDK, Android SDK platform and build-tools.

## Controls

| Action | Desktop | Android |
|---|---|---|
| new habit | `Ctrl + N` | “+ New habit” |
| tick / untick | `Space` or click the circle | tap the circle |
| delete | `Delete` | “Delete habit” |
| deselect | `Esc` | — |

## Notes

- A streak counts consecutive days **up to today**; a day not yet ticked does not break it.
- The 30-day rate counts from the day the habit was created, so a new habit is not punished
  for the days before it existed.
- The Android build requests **no permissions** — it has no internet access at all.

## Version 2 — what is new

**Desktop**

- **Click any square in the heatmap** to tick or untick that exact day — correct a missed day
  without touching the menu.
- **Double-click a habit** to edit its name, colour and weekly target.
- **↑ / ↓ buttons** reorder habits in the list.
- **Ctrl+Z restores a deleted habit**, together with all of its history.
- **Backup** button writes a copy of the whole data file.

**Android**

- Tap any heatmap square to change that day.
- **Edit** button on the habit card — rename, recolour, retarget.
- Deleting shows an **UNDO** bar for six seconds.

## Version 3 — statistics and pages

The app is now three pages, switched from the bar at the bottom (Android) or the tabs at the top
(desktop):

**Today** — the habit list and the selected habit's detail, as before.

**Statistics** — totals for all habits: number of ticks, longest current streak, best streak ever,
30-day completion, a 30-day completion line chart, and a bar per habit showing its own 30-day rate.

**Calendar** — a month grid coloured by how much of that day was completed, with arrows to page
back through the months, and overall performance for each weekday.

Colour intensity in the calendar means: pale = a little of the day completed, bright cyan = all of it.

## Building without a Windows machine

The Android package is now assembled on a Linux host with only Java installed:

1. `repack_apk.py` (in `tools/`) rewrites the archive with a fresh page, keeping
   `resources.arsc` stored and 4-byte aligned the way zipalign would.
2. `apksigner` signs the result with the debug key.

This means a new APK can be produced on the Raspberry Pi itself — no Android SDK and no
Windows PC required. The desktop `.exe` still needs PyInstaller on Windows.

## Version 4 — rebuilt as a proper application

The phone app was rewritten rather than patched.

**Structure** — four sections behind a fixed tab bar: Today, Stats, Calendar, More.

**Habits** — each habit has a category, a colour, its own repeat days (Monday to Sunday),
and either a yes/no goal or a counted one (e.g. 30 reps, 8 glasses). Counted habits open a
stepper instead of a blunt tick.

**Today** — a greeting that follows the clock and your name, a progress ring for the day,
habits grouped into to-do, completed and not-scheduled-today, a streak badge on each card,
and a week strip showing which days that habit runs.

**Stats** — 7 / 30 / 90-day ranges, completion rate, current streak, best streak, total ticks,
a daily completion chart, a weekday breakdown and a sorted per-habit table.

**Calendar** — a month grid shaded by how much of each day was completed, with a legend and
month arrows. Tapping any day opens that day's habits, so a forgotten day can be corrected.

**More** — your name, the accent colour for the whole interface, JSON export and import,
and an erase option. All data stays on the device; the storage format is versioned and older
files are migrated automatically.
