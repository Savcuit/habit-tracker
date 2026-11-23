#!/usr/bin/env bash
# Builds one of the two editions from the same source:
#   tools/build_variant.sh plain   -> release/HabitTracker.apk
#   tools/build_variant.sh xp      -> release/HabitTrackerXP.apk   (separate package)
set -euo pipefail

VARIANT="${1:-plain}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$HOME/.hermes/cache/scratch/ht-build-$VARIANT}"

rm -rf "$WORK"
mkdir -p "$(dirname "$WORK")"
cp -r "$ROOT/android" "$WORK"

case "$VARIANT" in
  plain)
    OUT="$ROOT/release/HabitTracker.apk"
    ;;
  xp)
    grep -rl "com\.savcuit\.habittracker" "$WORK/src" "$WORK/AndroidManifest.xml" \
      | xargs sed -i 's/com\.savcuit\.habittracker/com.savcuit.habittracker.xp/g'
    sed -i 's/window\.HABIT_XP = false/window.HABIT_XP = true/' "$WORK/assets/index.html"
    sed -i 's#<string name="app_name">Habit Tracker</string>#<string name="app_name">Habit Tracker XP</string>#' "$WORK/res/values/strings.xml"
    OUT="$ROOT/release/HabitTrackerXP.apk"
    ;;
  *)
    echo "usage: $0 plain|xp" >&2; exit 2;;
esac

mkdir -p "$ROOT/release"
OUT="$OUT" bash "$WORK/build.sh"
