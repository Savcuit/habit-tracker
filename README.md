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
