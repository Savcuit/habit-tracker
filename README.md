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

## iPhone and iPad

The same page is published as a web app, so it installs on iOS without a Mac or an App Store
account:

1. Open **https://savcuit.github.io/habit-tracker/** in Safari.
2. Tap **Share → Add to Home Screen**.

It then opens full screen with its own icon, keeps working offline, and stores everything on the
device exactly as the Android build does. To move existing history across, use **More → Export
backup** on the old device and **Import** on the new one.

The published copy lives in `docs/`; `index.html` there is the same file as `android/assets/index.html`
plus the Apple meta tags, `manifest.json` and a small service worker for offline use.

## Version 4.1 — daily reminders

Each habit can carry a time of day. The Android build registers a repeating alarm with the
system, so a notification arrives even when the app is closed:

- set the time in the habit editor (**Daily reminder**); clear it to stop the reminder
- the habit card shows the time next to its category
- **More → Reminders** shows how many habits are armed, offers a test notification one minute
  away, and can re-register everything
- alarms are restored after a reboot, and Android 13+ asks for notification permission on first launch

Honest limits: the alarm is deliberately inexact (`setInexactRepeating`), so a reminder can arrive a
few minutes late under battery saving; that choice avoids asking for the special exact-alarm
permission. The browser version has no reminders at all — a web page cannot wake a sleeping phone.

### Building the APK on Linux

`android/build.sh` produces a signed package with the Debian Android tools (`aapt2`, `zipalign`,
`apksigner`), `javac` and `d8` — no Gradle, no Android Studio, no Windows.

## Version 4.1.1 — scrolling fix

The pages were ending underneath the tab bar. The cause was `height:100%` on the page body: it pinned
the body to one screen, so the bottom padding sat *inside* that box and the overflowing content ran
straight past it. The body now grows with its content (`min-height:100%`), and the page measures the
tab bar after render and pads itself by exactly that height plus 28 px — so every page, at any screen
size, stops above the bar rather than behind it.

## Version 4.2 — sharper statistics and fewer taps

- **Streaks are now schedule-aware.** A Tuesday-only habit no longer breaks because Wednesday passed;
  today being unfinished does not end a streak either. The longest-streak figure follows the same rule.
- **A year heatmap** on Statistics: 27 weeks by 7 days, shaded by how much of each day was completed.
- **Insights**: momentum (this week against last), habits at risk of losing a streak today, active days
  in the last 90, and the weekday you are most reliable on.
- **Swipe a habit** right to complete it, left to edit it, with an Undo in the toast.
- **Three appearances**: Midnight, OLED black and Daylight, switched in More.
- **Starter habits** on the empty screen — one tap adds a sensible first habit, undoable.

## Version 4.2.1 — the day turns over at midnight

Completions were always stored against a calendar date, so a new day was already a clean slate for the
data — but a phone left running, or one that slept through midnight, kept showing yesterday's ticks.

Now the app follows the clock: a timer fires just after midnight, a twenty-second check catches any
drift, and returning to the app after a long sleep re-checks the date first. When the day changes the
screen redraws, counted habits return to zero, and a brief "A new day — habits reset" confirms it.

## Version 4.2.2 — the day can no longer go stale

The midnight timer only helped while the app was awake. Switching tabs redrew only the tab you moved
to, so the Today list could still be showing yesterday's state. Now every tab press re-reads the clock
and redraws the header and the Today list before anything else.

More also gained a plain line under **The app believes today is** showing the exact date and time the
app is working from, with a **Refresh** button beside it — so a mismatch between phone and app is
visible at a glance instead of guessed at.

## Version 4.3 — backup and restore actually work on Android

A WebView is not a browser: it refuses to open a file picker unless the app implements one, and it
silently ignores download links. Both buttons therefore did nothing on the phone.

- **Export** now hands the JSON to the app, which writes it to **Downloads/habits-backup-YYYY-MM-DD.json**
  (Android 10+ via MediaStore; older versions use the app's Downloads folder). The toast reports the path.
- **Import** opens the system file picker, reads the chosen file and restores habits and history.
- The data card says plainly that backups are JSON files.

## Version 4.4 — a proper web app for iPhone

- On an iPhone in Safari the app offers **Add to your Home Screen** with the exact two taps, and stops
  offering once dismissed.
- **Launch images** for eight screen sizes: opening from the home screen no longer flashes white.
- **Share the app** in More, using the system share sheet where it exists.
- The data card shows **when the last backup was taken**, in amber once it is more than a fortnight old.
- A service-worker update now announces itself instead of silently waiting.
- `tools/make_web.py` builds `docs/index.html` from the Android page, so the two cannot drift apart.

## Version 4.5 — Android polish, and a durable signing key

- **Adaptive launcher icon** (with a monochrome layer for themed icons) instead of a flat bitmap.
- **A proper splash screen** on Android 12+ and a dark window background below it — no white flash.
- **App shortcuts**: long-press the icon for *New habit* and *Statistics*.
- **Actionable reminders**: the notification now carries **Done** and **Snooze 15 min**. Done is queued
  and applied the moment the app is next opened, with a toast saying so.

### The signing key moved

The earlier packages were signed with a throwaway key in `/tmp`, which no longer exists. Builds are now
signed with `~/.hermes/keys/habittracker.p12` (password in `habittracker.pass`, both mode 600), so future
updates install cleanly over one another.

Because the key changed, this one build cannot install over the previous version. To keep the history:
**Export backup → uninstall the old app → install this APK → Import**.

## Version 4.5.1 — the reminder test, fixed

The test button used an **exact** alarm, which Android 12 and later refuse without the special
exact-alarm permission — hence "could not schedule the test". It now uses an ordinary alarm, which needs
no permission, and reports the real reason if it ever fails.

More → Reminders also states plainly when notifications are switched off for the app, with a button that
opens the right Android settings page.

## Version 4.6 — habits the phone can verify

A habit can now be a **step goal** (10,000 steps, say). The app reads the phone's own step counter, so the
tick is earned rather than claimed:

- **Steps** is a third goal type in the habit editor, with a target.
- The card shows live progress — `6,240 / 10,000 steps · from your phone` — and ticks itself the moment
  the target is reached, recording the day in the history like any other habit.
- It refreshes while the app is open (every 45 seconds) and whenever you switch tabs.
- Android 10 and later ask for **Physical activity** permission; without a step sensor the option is
  simply not offered.

Honest limits: the sensor counts from the last reboot, so the app keeps a daily baseline — taken at the
midnight rollover, or from the last reading if the phone was seen recently. If the phone is rebooted the
count restarts, which the app detects and handles. Steps taken in apps that block sensors are invisible.

## Version 4.7 — camera workout tracking, entirely on the phone

A fifth tab, **Train**, counts exercises from the camera. Nothing is uploaded: a pose model runs inside
the app, and only your own phone sees the frames.

- **Push-ups** — counts a repetition when the elbows pass below 100° and return above 150°, with a short
  debounce so a wobble cannot count twice.
- **Plank** — times the hold while the hip angle stays above 160°, and tells you to straighten when it
  drops.
- A live skeleton, a rep or second counter, and a **form percentage** are drawn over the picture.
- When you stop, choose a habit and it is marked done for the day.

Offline by design: TensorFlow.js, PoseNet (MobileNet 0.50) and its weights are bundled in the app, about
4 MB, so the model loads with no network at all.

Limits worth knowing: the pose model needs decent light and the whole body in frame; it recognises
posture and joint angles, not kit, so a rowing machine or a pull-up bar is beyond it. The floor is the
best place for the phone. The web version can do the same where the browser allows camera access.

## Version 4.7.1 — the front camera

The Train tab now opens on the **front camera**, which is the sensible one when the phone is propped
up facing you — and it is mirrored, like a mirror, so movement feels natural. A **Switch to back**
button swaps lenses mid-session.

The skeleton overlay also now sizes itself to the incoming picture, so joints sit exactly on the body
instead of drifting when the camera resolution changes.

## Version 4.7.2 — the model loads inside the app

The Train tab failed with "could not load the model: failed fetch" because a WebView blocks `fetch()`
against `file://` URLs by default — the scripts loaded, but the model weights did not.

Two changes, belt and braces:

- the WebView settings now permit file-URL access, which is what the model needs;
- if a fetch still fails, the page reads `model.json` and the weights with `XMLHttpRequest` and hands
  TensorFlow an in-memory loader, which needs no network stack at all.

## Version 4.8 — reps counted against your own range

Fixed angles were the wrong idea: a phone propped high, low or off to the side reads the elbow
differently, so a correct push-up could sit above the "down" threshold and never count.

The detector now learns your range during the session. It tracks the straightest and deepest elbow angles
it has seen, and calls a repetition only when you travel from the top quarter of that range to the bottom
and back — with a 200 ms debounce and a guard that ignores an arm that barely moves. The live angle is
printed under the counter, so the numbers are visible rather than guessed at.

The model also looks at a sharper input (257 px instead of 193), which steadies the joint positions.

## Version 4.9 — the reason nothing counted

The angle was being computed from the **average of both arms**, and that average was only produced when
both arms were visible. In a real push-up — watched from the side or from the floor — the far arm is
hidden by the body, so the angle came back empty and the app said "whole body in frame" even though it
was. Nothing could ever count.

Three changes:

- the angle now comes from **whichever arm is visible**, preferring the more bent one when both are;
- if the wrists are cut off, the elbow–shoulder–hip angle stands in, so a tight frame still yields a number;
- a second signal — **how far the shoulders sink towards the hips** — is blended in, so a repetition
  registers even when the arms are poorly tracked. The readout says `shoulders` when only that signal is live.

Verified with a side-on pose where the far arm is hidden (score 0.1): the near arm alone now yields 90°,
where the old code yielded nothing. A shoulder-only down-and-up sequence counted exactly one rep.
