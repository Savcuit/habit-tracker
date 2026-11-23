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

## Version 5.0 — streak freezes, and a nudge at the right hour

Two freezes, in the spirit of Duolingo, so an accidental day does not erase months of work.

- **Two freezes** sit in inventory. When a scheduled day goes by unfinished, one is spent
  automatically and the day is recorded as frozen — the streak carries on.
- A frozen day is drawn in **icy blue with a ❄** in the calendar and the year heatmap, so it is
  never mistaken for a day you actually did.
- The habit card shows `🔥 12` with `❄ 1` beneath it when part of that streak was protected.
- **One freeze is earned every fourteen days**, up to a maximum of fourteen.
- The `❄ n freezes` chip under the date opens a short explanation of the rules.
- A freeze is only spent when the streak before the missed day is worth at least two — a habit you
  have barely started is not protected, so the freezes are not wasted.

Notifications:

- **20:30, streak at risk** — fires only if something scheduled for today is still unfinished, and
  names the habits (`Reading, Stretch — finish them before midnight`). Completing everything
  cancels it.
- **Milestones** — 3, 7, 14, 21, 30, 50, 75, 100, 150, 200 and 365 days open a celebration screen
  with confetti and a line of encouragement. Each milestone is celebrated once per habit.

Android 5.0 (`versionCode 17`) and the web build in `docs/` both carry it.

## Version 5.1 — one a fortnight, up to fourteen

The freeze economy, adjusted as asked:

- you begin with **two**;
- you earn **one more every 14 days**, whether or not you used any;
- the ceiling is **fourteen**, and while you sit at fourteen the fortnightly clock keeps moving,
  so using three at once does not reset your progress towards the next one.

Existing saves are lifted to the new ceiling automatically; the count itself is untouched.

## Version 6.0 — Pip, and colours that follow the weather

A guide, and a choice of mood for the app.

- **Pip** sits at the top of Today and says something useful each time you open it: what is left
  today, that you should start with the task you least want to do, that a miss will cost a freeze,
  or simply that everything is done and you should put the phone down. The bubble follows the
  accent colour of the theme.
- **First launch asks how you want it to look.** *Casual* is the cyan one. *Cosy* is warm and soft —
  cream and peach by day, deep indigo at night, and its accent colour is chosen from today's sky:
  amber for clear, slate for cloud, blue for rain, ice for snow, violet for storms.
- **Temperature nudges the palette.** Below 6 °C the accent leans cold; above 26 °C it leans warm.
- Cosy asks **where you are**, once. The Android app asks for coarse location permission; the web
  version uses the browser's. If permission is refused, it asks for a town instead. Coordinates go
  to **Open-Meteo** and nowhere else, and the answer is cached for thirty minutes.
- Both can be changed at any time in **More → Pip & colours**, where the current weather and city
  are shown, with buttons to refresh or change the place.

Verified in a real browser: the welcome appears on a fresh install, choosing Cosy set the cream
palette, rain at 11 °C produced the blue accent `#5B8DEF`, choosing a city fetched the weather and
stored it, and switching back to Casual restored midnight with the cyan accent.

## Version 7.0 — surprise nudges

Reminders at times the app chooses, in the spirit of Duolingo, so a fixed 9 a.m. alarm cannot be
tuned out.

- A new card in **More → Surprise nudges**: on or off, with the time of the next one.
- Android arms the first nudge between **09:00 and 10:30**, then waits a random **90 to 170
  minutes** before the next, and stops at **21:30** — typically three to five a day.
- Each nudge reschedules the following one itself, so the rhythm continues even if the app is never
  opened; nothing depends on the page being alive.
- The text knows what is still open: the app writes today's unfinished habit names to the phone, and
  the notification reads *"Still open: Reading. Two minutes now is worth more than a perfect plan
  later."* Titles and encouragement rotate from a small pool so no two nudges read alike.
- Separate notification channel (*Surprise nudges*), so they can be silenced without touching habit
  reminders.
- The web build shows the card but explains that a browser cannot wake the phone.

Verified with a stubbed Android bridge in a real browser: the card renders, the toggle calls through
to the phone, the next-nudge time appears, and today's open habits are passed across as text.

## Version 8.0 — the things the good ones have

Researched against current habit apps (HabitKit, Streaks, Habitify, Strides, Loop, jeden.day), the
three features cited most often and missing here are now in.

**Home-screen widget.** A dark panel showing today's count, a bar, and up to three habits still open.
Tap it to open the app. Add it from the launcher's widget list; the page writes the state to the
phone each time it redraws, so the widget follows the app without opening it.

**Times a week, not fixed days.** A habit can now be "3 times a week" instead of Monday/Wednesday/
Friday. Any days count, the card shows `2/3 this week`, and the streak counts **consecutive weeks
meeting the target** — displayed with a small `w`, because a weekly habit's streak is weeks, not days.

**Pause.** *Pause for a week* (or resume) in the habit sheet. While paused the habit is not due, is
not counted as missed, and does not break a streak — which is what Streaks calls a holiday mode and
what most trackers get wrong.

Verified in a browser: a 3×/week habit showed `0/3 this week` and a two-week streak; a paused habit
left today's list entirely; the widget payload is sent to the phone on every redraw.

## Version 8.1 — two editions

Everything above is in both. The difference is a single flag and, for the second, its own
package, so both can be installed side by side.

### Habit Tracker (`com.savcuit.habittracker`)

The clean tracker. No points, no levels, no shop. If you would rather not be gamified, this is the one.

### Habit Tracker XP (`com.savcuit.habittracker.xp`)

Habitica's idea, without the pets: finishing a habit earns **XP and gold**, scaled by the streak
(`10 + 2 per day of streak`, capped at 30), gold `3`, plus `2` extra whenever the streak hits a
multiple of five. XP accumulates into **levels** on a rising curve — 100 XP for level 2, 200 more for
level 3, and so on — shown as a live chip under the greeting and a bar in **More**. Gold buys
**streak freezes at 40 each**, which turns the economy into something useful: a good week can pay for
one bad day.

Both editions are built from one source by `tools/build_variant.sh plain` and `tools/build_variant.sh xp`.
