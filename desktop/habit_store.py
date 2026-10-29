"""Data layer for the habit tracker: storage, streaks and statistics.

Kept separate from the interface so it can be tested without a screen.
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import Iterable

DATA_DIR_NAME = "NexusHabitTracker"


def data_path() -> str:
    """Where the habits file lives: %APPDATA% on Windows, ~/.local/share elsewhere."""
    base = os.environ.get("APPDATA")
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".local", "share")
    return os.path.join(base, DATA_DIR_NAME, "data.json")


def today() -> date:
    return date.today()


def parse_day(s: str) -> date:
    return date.fromisoformat(s)


@dataclass
class Habit:
    name: str
    color: str = "#22d3ee"
    target: int = 7                      # intended days per week, 1-7
    created: str = field(default_factory=lambda: today().isoformat())
    done: list[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    # ---------------------------------------------------------------- queries
    def is_done(self, day: date | str | None = None) -> bool:
        day = day or today()
        if isinstance(day, date):
            day = day.isoformat()
        return day in self.done

    def toggle(self, day: date | str | None = None) -> bool:
        day = day or today()
        if isinstance(day, date):
            day = day.isoformat()
        if day in self.done:
            self.done.remove(day)
            return False
        self.done.append(day)
        self.done.sort()
        return True

    def streak(self) -> int:
        """Consecutive days up to today; a missing today does not break a streak."""
        count = 0
        cursor = today()
        if not self.is_done(cursor):
            cursor -= timedelta(days=1)
        while self.is_done(cursor):
            count += 1
            cursor -= timedelta(days=1)
        return count

    def best_streak(self) -> int:
        if not self.done:
            return 0
        days = sorted({parse_day(d) for d in self.done})
        best = run = 1
        for prev, cur in zip(days, days[1:]):
            run = run + 1 if (cur - prev).days == 1 else 1
            best = max(best, run)
        return best

    def total_done(self) -> int:
        return len(set(self.done))

    def week_done(self, ending: date | None = None) -> int:
        """How many days were completed in the seven days ending today."""
        end = ending or today()
        return sum(1 for i in range(7) if self.is_done(end - timedelta(days=i)))

    def completion_rate(self, window: int = 30) -> float:
        """Fraction of the last `window` days completed, counting from creation."""
        end = today()
        created = parse_day(self.created)
        start = max(created, end - timedelta(days=window - 1))
        span = (end - start).days + 1
        if span <= 0:
            return 0.0
        hits = sum(1 for i in range(span) if self.is_done(end - timedelta(days=i)))
        return hits / span

    def last_days(self, days: int = 35) -> list[tuple[date, bool]]:
        end = today()
        return [(end - timedelta(days=i), self.is_done(end - timedelta(days=i)))
                for i in range(days - 1, -1, -1)]


class HabitStore:
    def __init__(self, path: str | None = None):
        self.path = path or data_path()
        self.habits: list[Habit] = []
        self.load()

    # ------------------------------------------------------------ persistence
    def load(self) -> None:
        if not os.path.exists(self.path):
            self.habits = []
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            self.habits = [Habit(**item) for item in raw.get("habits", [])]
        except (json.JSONDecodeError, TypeError, ValueError):
            # A corrupt file must never lose the user's history: rename and start fresh.
            try:
                os.replace(self.path, self.path + ".corrupt")
            except OSError:
                pass
            self.habits = []

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        payload = {
            "version": 1,
            "saved": today().isoformat(),
            "habits": [asdict(h) for h in self.habits],
        }
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        os.replace(tmp, self.path)

    # --------------------------------------------------------------- mutation
    def add(self, name: str, color: str, target: int = 7) -> Habit:
        habit = Habit(name=name.strip() or "New habit", color=color, target=target)
        self.habits.append(habit)
        self.save()
        return habit

    def remove(self, habit: Habit) -> None:
        self.habits = [h for h in self.habits if h.id != habit.id]
        self.save()

    def toggle(self, habit: Habit) -> bool:
        state = habit.toggle()
        self.save()
        return state

    # -------------------------------------------------------------- aggregate
    def done_today(self) -> int:
        return sum(1 for h in self.habits if h.is_done())

    def progress_today(self) -> float:
        if not self.habits:
            return 0.0
        return self.done_today() / len(self.habits)

    def export_csv(self, path: str) -> None:
        import csv
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(["habit", "date", "done"])
            for habit in self.habits:
                created = parse_day(habit.created)
                end = today()
                span = (end - created).days + 1
                for i in range(span):
                    day = end - timedelta(days=i)
                    writer.writerow([habit.name, day.isoformat(), int(habit.is_done(day))])


PALETTE = ["#22d3ee", "#38bdf8", "#a78bfa", "#f472b6", "#facc15", "#4ade80", "#fb923c"]
