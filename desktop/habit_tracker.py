"""Habit Tracker — a dark, quiet desktop app for keeping daily habits.

Interface only; all storage and statistics live in habit_store.py.
"""

from __future__ import annotations

import os
import shutil
import sys
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import filedialog, messagebox

from habit_store import Habit, HabitStore, PALETTE, today

# ------------------------------------------------------------------ palette --
BG        = "#0a1120"
PANEL     = "#101a2e"
PANEL_2   = "#0d1626"
BORDER    = "#1e2d47"
TEXT      = "#e6f1ff"
MUTED     = "#7c8ba6"
ACCENT    = "#22d3ee"
ACCENT_DK = "#0e7490"
DANGER    = "#f87171"
GOLD      = "#facc15"

FONT      = "Segoe UI"
F_TITLE   = (FONT, 19, "bold")
F_SUB     = (FONT, 9)
F_ROW     = (FONT, 11)
F_ROW_B   = (FONT, 11, "bold")
F_SMALL   = (FONT, 8)
F_STAT    = (FONT, 17, "bold")
F_BTN     = (FONT, 9, "bold")

WEEKDAYS = ["M", "T", "W", "T", "F", "S", "S"]


def dark_title_bar(window) -> None:
    """Ask Windows to paint the title bar dark, so it matches the app."""
    try:
        import ctypes
        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        for attribute in (20, 19):          # 20 on Windows 10 2004+, 19 on older builds
            value = ctypes.c_int(1)
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value)) == 0:
                break
    except Exception:
        pass


def resource_path(relative: str) -> str:
    """Find a bundled file both when run as a script and inside the built .exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def mix(c1: str, c2: str, t: float) -> str:
    """Blend two #rrggbb colours; t=0 gives c1, t=1 gives c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def rounded_rect(canvas: tk.Canvas, x1, y1, x2, y2, r, **kw):
    """A rectangle with soft corners, drawn as a smoothed polygon."""
    points = [
        x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
        x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, splinesteps=18, **kw)


class FlatButton(tk.Label):
    """A label that behaves like a button, so it can be styled freely."""

    def __init__(self, master, text, command, *, fg=TEXT, bg=PANEL, hover=None,
                 font=F_BTN, padx=14, pady=7, border=None):
        super().__init__(master, text=text, fg=fg, bg=bg, font=font,
                         padx=padx, pady=pady, cursor="hand2")
        self._command = command
        self._bg = bg
        self._hover = hover or mix(bg, ACCENT, 0.18)
        if border:
            self.configure(highlightbackground=border, highlightthickness=1)
        self.bind("<Enter>", lambda e: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda e: self.configure(bg=self._bg))
        self.bind("<Button-1>", self._click)

    def set_style(self, *, text=None, fg=None, bg=None, hover=None):
        """Change the look of the button without touching Tk options that do not exist."""
        if text is not None:
            self.configure(text=text)
        if fg is not None:
            self.configure(fg=fg)
        if bg is not None:
            self.configure(bg=bg)
            self._bg = bg
        if hover is not None:
            self._hover = hover

    def _click(self, _event=None):
        if self._command:
            self._command()


class ProgressRing(tk.Canvas):
    def __init__(self, master, size=54, **kw):
        super().__init__(master, width=size, height=size, bg=PANEL, highlightthickness=0, **kw)
        self.size = size
        self.value = 0.0
        self.text = "0%"
        self._draw()

    def set(self, value: float, text: str):
        self.value = max(0.0, min(1.0, value))
        self.text = text
        self._draw()

    def _draw(self):
        self.delete("all")
        pad = 5
        box = (pad, pad, self.size - pad, self.size - pad)
        self.create_oval(*box, outline=BORDER, width=5)
        if self.value > 0:
            extent = -359.9 * self.value
            self.create_arc(*box, start=90, extent=extent, style="arc",
                            outline=ACCENT, width=5)
        self.create_text(self.size / 2, self.size / 2, text=self.text,
                         fill=TEXT, font=(FONT, 10, "bold"))


class HabitRow(tk.Frame):
    """One habit in the left-hand list."""

    def __init__(self, master, habit: Habit, on_select, on_toggle, on_edit=None):
        super().__init__(master, bg=PANEL, cursor="hand2")
        self.habit = habit
        self.on_select = on_select
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.selected = False
        self.hovered = False

        self.inner = tk.Frame(self, bg=PANEL, padx=10, pady=8)
        self.inner.pack(fill="x")

        self.check = tk.Canvas(self.inner, width=26, height=26, bg=PANEL,
                               highlightthickness=0, cursor="hand2")
        self.check.pack(side="left")
        self.check.bind("<Button-1>", self._toggle)

        textwrap = tk.Frame(self.inner, bg=PANEL)
        textwrap.pack(side="left", fill="x", expand=True, padx=(10, 6))

        self.name = tk.Label(textwrap, text=habit.name, fg=TEXT, bg=PANEL,
                             font=F_ROW, anchor="w")
        self.name.pack(fill="x")

        self.sub = tk.Label(textwrap, text="", fg=MUTED, bg=PANEL,
                            font=F_SMALL, anchor="w")
        self.sub.pack(fill="x")

        self.streak = tk.Label(self.inner, text="", fg=GOLD, bg=PANEL, font=(FONT, 9, "bold"))
        self.streak.pack(side="right")

        for widget in (self, self.inner, textwrap, self.name, self.sub, self.streak):
            widget.bind("<Button-1>", self._select)
            widget.bind("<Double-Button-1>", self._edit)
            widget.bind("<Enter>", self._enter)
            widget.bind("<Leave>", self._leave)

        self.refresh()

    # ------------------------------------------------------------------ state
    def refresh(self):
        done = self.habit.is_done()
        streak = self.habit.streak()
        self.streak.configure(text=(f"{streak}d" if streak else ""),
                              fg=GOLD if streak else MUTED)
        week = self.habit.week_done()
        self.sub.configure(text=f"{week}/7 this week")
        self.name.configure(fg=TEXT if not done else mix(TEXT, ACCENT, 0.45))
        self._paint_check(done)
        self._paint_bg()

    def set_selected(self, flag: bool):
        self.selected = flag
        self._paint_bg()

    def _paint_bg(self):
        base = PANEL_2 if self.selected else PANEL
        if self.hovered and not self.selected:
            base = mix(PANEL, ACCENT, 0.08)
        for widget in (self, self.inner, *self._bg_widgets()):
            try:
                widget.configure(bg=base)
            except tk.TclError:
                pass
        self._paint_check(self.habit.is_done())

    def _bg_widgets(self):
        return [self.name, self.sub, self.streak]

    def _paint_check(self, done: bool):
        c = self.check
        base = PANEL_2 if self.selected else PANEL
        c.configure(bg=base)
        c.delete("all")
        colour = self.habit.color
        if done:
            c.create_oval(3, 3, 23, 23, outline=colour, fill=colour, width=2)
            c.create_line(8, 13, 12, 18, 19, 9, fill="#06131f", width=2.6,
                          capstyle="round", joinstyle="round")
        else:
            c.create_oval(3, 3, 23, 23, outline=mix(colour, base, 0.35), width=2)

    # ---------------------------------------------------------------- events
    def _enter(self, _e=None):
        self.hovered = True
        self._paint_bg()

    def _leave(self, _e=None):
        self.hovered = False
        self._paint_bg()

    def _select(self, _e=None):
        self.on_select(self.habit)

    def _edit(self, _e=None):
        if self.on_edit:
            self.on_edit(self.habit)
        return "break"

    def _toggle(self, _e=None):
        self.on_toggle(self.habit)
        return "break"


class DetailPanel(tk.Frame):
    """The right-hand side: statistics and a heatmap for the selected habit."""

    def __init__(self, master, app):
        super().__init__(master, bg=PANEL)
        self.app = app
        self.habit: Habit | None = None

        self.header = tk.Frame(self, bg=PANEL)
        self.header.pack(fill="x", padx=22, pady=(20, 6))

        self.chip = tk.Canvas(self.header, width=10, height=34, bg=PANEL, highlightthickness=0)
        self.chip.pack(side="left", padx=(0, 12))

        titles = tk.Frame(self.header, bg=PANEL)
        titles.pack(side="left", fill="x", expand=True)
        self.title = tk.Label(titles, text="", fg=TEXT, bg=PANEL, font=(FONT, 16, "bold"), anchor="w")
        self.title.pack(fill="x")
        self.subtitle = tk.Label(titles, text="", fg=MUTED, bg=PANEL, font=F_SMALL, anchor="w")
        self.subtitle.pack(fill="x")

        self.actions = tk.Frame(self.header, bg=PANEL)
        self.actions.pack(side="right")

        self.btn_today = FlatButton(self.actions, "Mark today", self._toggle_today,
                                    fg=BG, bg=ACCENT, hover=mix(ACCENT, "#ffffff", 0.25))
        self.btn_today.pack(side="left", padx=(0, 8))

        self.stats = tk.Frame(self, bg=PANEL)
        self.stats.pack(fill="x", padx=22, pady=(14, 8))

        self.heat_label = tk.Label(self, text="LAST 5 WEEKS", fg=MUTED, bg=PANEL,
                                   font=(FONT, 8, "bold"), anchor="w")
        self.heat_label.pack(fill="x", padx=22, pady=(10, 4))

        self._cells = []
        self.heat = tk.Canvas(self, bg=PANEL, highlightthickness=0, height=250, cursor="hand2")
        self.heat.pack(fill="x", padx=22, pady=(0, 6))
        self.heat.bind("<Button-1>", self._heat_click)

        self.weekday_label = tk.Label(self, text="SUCCESS BY WEEKDAY", fg=MUTED, bg=PANEL,
                                      font=(FONT, 8, "bold"), anchor="w")
        self.weekday_label.pack(fill="x", padx=22, pady=(6, 4))

        self.weekday_chart = tk.Canvas(self, bg=PANEL, highlightthickness=0, height=140)
        self.weekday_chart.pack(fill="both", expand=True, padx=22, pady=(0, 10))

        self.footer = tk.Frame(self, bg=PANEL)
        self.footer.pack(fill="x", padx=22, pady=(0, 18))
        self.btn_delete = FlatButton(self.footer, "Delete habit", self._delete,
                                     fg=DANGER, bg=PANEL, hover=mix(PANEL, DANGER, 0.18),
                                     border=BORDER)
        self.btn_delete.pack(side="right")
        self.btn_export = FlatButton(self.footer, "Export CSV", self._export,
                                     fg=MUTED, bg=PANEL, hover=mix(PANEL, ACCENT, 0.15),
                                     border=BORDER)
        self.btn_export.pack(side="right", padx=(0, 8))

        self.btn_backup = FlatButton(self.footer, "Backup", lambda: self.app.backup_json(),
                                     fg=MUTED, bg=PANEL, hover=mix(PANEL, ACCENT, 0.15),
                                     border=BORDER)
        self.btn_backup.pack(side="right", padx=(0, 8))

        self.btn_down = FlatButton(self.footer, "↓", lambda: self.app.move_habit(self.habit, +1),
                                   fg=MUTED, bg=PANEL, hover=mix(PANEL, ACCENT, 0.15),
                                   border=BORDER, padx=10)
        self.btn_up = FlatButton(self.footer, "↑", lambda: self.app.move_habit(self.habit, -1),
                                 fg=MUTED, bg=PANEL, hover=mix(PANEL, ACCENT, 0.15),
                                 border=BORDER, padx=10)
        self.btn_up.pack(side="left")
        self.btn_down.pack(side="left", padx=(8, 0))

        self.hint = tk.Label(self.footer, text="double-click a habit to edit · click a day to change it",
                             fg=MUTED, bg=PANEL, font=F_SMALL)
        self.hint.pack(side="left", padx=14)

        self._stat_cards = []
        self.show(None)

    # ------------------------------------------------------------------ build
    def _stat_card(self, parent, caption):
        card = tk.Frame(parent, bg=PANEL_2, highlightbackground=BORDER, highlightthickness=1)
        card.pack(side="left", fill="x", expand=True, padx=(0, 10))
        value = tk.Label(card, text="–", fg=TEXT, bg=PANEL_2, font=F_STAT)
        value.pack(pady=(12, 0))
        tk.Label(card, text=caption, fg=MUTED, bg=PANEL_2, font=F_SMALL).pack(pady=(0, 12))
        return value

    def _ensure_cards(self):
        if self._stat_cards:
            return
        self._stat_cards = [
            self._stat_card(self.stats, "CURRENT STREAK"),
            self._stat_card(self.stats, "BEST STREAK"),
            self._stat_card(self.stats, "THIS WEEK"),
            self._stat_card(self.stats, "30-DAY RATE"),
        ]

    # ------------------------------------------------------------------- view
    def show(self, habit: Habit | None):
        self.habit = habit
        if habit is None:
            self.title.configure(text="No habit selected")
            self.subtitle.configure(text="Add a habit with the button above.")
            self.btn_today.pack_forget()
            self.btn_delete.pack_forget()
            self.chip.delete("all")
            for card in self._stat_cards:
                card.configure(text="–")
            self.heat.delete("all")
            self.weekday_chart.delete("all")
            return

        self._ensure_cards()
        self.btn_today.pack(side="left", padx=(0, 8))
        self.btn_delete.pack(side="right")

        self.title.configure(text=habit.name)
        created = date.fromisoformat(habit.created)
        self.subtitle.configure(text=f"Started {created.strftime('%d %b %Y')} · target {habit.target} days a week")

        self.chip.delete("all")
        self.chip.configure(bg=PANEL)
        rounded_rect(self.chip, 2, 2, 8, 32, 3, fill=habit.color, outline=habit.color)

        values = [
            str(habit.streak()),
            str(habit.best_streak()),
            f"{habit.week_done()}/7",
            f"{round(habit.completion_rate(30) * 100)}%",
        ]
        for card, text in zip(self._stat_cards, values):
            card.configure(text=text, fg=ACCENT if card is self._stat_cards[0] and habit.streak() else TEXT)

        self._update_today_button()
        self._draw_heatmap()
        self._draw_weekday_chart()

    def _update_today_button(self):
        if not self.habit:
            return
        done = self.habit.is_done()
        self.btn_today.set_style(
            text="Undo today" if done else "Mark today",
            bg=PANEL_2 if done else ACCENT,
            fg=TEXT if done else BG,
            hover=mix(PANEL_2, ACCENT, 0.2) if done else mix(ACCENT, "#ffffff", 0.25),
        )

    def _draw_heatmap(self):
        c = self.heat
        c.delete("all")
        if not self.habit:
            return
        c.update_idletasks()
        width = max(c.winfo_width(), 420)
        height = max(c.winfo_height(), 190)
        days = self.habit.last_days(35)

        rows, cols = 7, 5
        gap = 6
        left = 34
        show_dates = True

        # grow the cells to use the space, but never beyond a comfortable size
        usable_w = width - left - 16
        usable_h = height - 34
        cell = min(34, (usable_w - gap * (cols - 1)) / cols, (usable_h - gap * (rows - 1)) / rows)
        cell = max(12, cell)
        if cell < 15:
            show_dates = False

        grid_w = cols * cell + (cols - 1) * gap
        grid_h = rows * cell + (rows - 1) * gap
        x0 = left + max(0, (usable_w - grid_w) / 2)
        y0 = 8 + max(0, (height - 20 - grid_h) / 2)

        for r in range(rows):
            c.create_text(left - 14, y0 + r * (cell + gap) + cell / 2,
                          text=WEEKDAYS[r], fill=MUTED, font=(FONT, 8))

        self._cells = []
        for index, (day, done) in enumerate(days):
            col = index // rows
            row = index % rows
            x1 = x0 + col * (cell + gap)
            y1 = y0 + row * (cell + gap)
            fill = self.habit.color if done else mix(PANEL_2, BORDER, 0.55)
            rounded_rect(c, x1, y1, x1 + cell, y1 + cell, min(5, cell / 4), fill=fill, outline=fill)
            if day == today():
                rounded_rect(c, x1 - 2, y1 - 2, x1 + cell + 2, y1 + cell + 2,
                             min(7, cell / 3.4), fill="", outline=ACCENT)

        if show_dates:
            step = 1 if (cell + gap) >= 44 else 2
            for col in range(0, cols, step):
                first = days[col * rows][0]
                c.create_text(x0 + col * (cell + gap) + cell / 2, y0 + grid_h + 14,
                              text=first.strftime("%d/%m"), fill=MUTED, font=(FONT, 8))

    def _heat_click(self, event):
        """Tap a square in the heatmap to tick or untick that particular day."""
        if not self.habit:
            return
        for x1, y1, x2, y2, day in self._cells:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.app.toggle_day(self.habit, day)
                return

    def _draw_weekday_chart(self):
        """Seven bars: how often each weekday was completed, as a percentage."""
        c = self.weekday_chart
        c.delete("all")
        if not self.habit:
            return
        c.update_idletasks()
        width = max(c.winfo_width(), 420)
        height = max(c.winfo_height(), 120)

        done_days = {date.fromisoformat(d) for d in self.habit.done}
        totals = [0] * 7
        hits = [0] * 7
        created = date.fromisoformat(self.habit.created)
        day = created
        end = today()
        while day <= end:
            totals[day.weekday()] += 1
            if day in done_days:
                hits[day.weekday()] += 1
            day += timedelta(days=1)

        left, right = 12, 12
        top, bottom = 18, 22
        chart_h = height - top - bottom
        slot = (width - left - right) / 7
        bar_w = min(38, slot * 0.55)

        for i in range(7):
            rate = (hits[i] / totals[i]) if totals[i] else 0.0
            x = left + slot * i + slot / 2
            h = max(3, min(chart_h, 150) * rate)
            y1 = height - bottom - h
            colour = self.habit.color if rate > 0 else mix(PANEL_2, BORDER, 0.6)
            rounded_rect(c, x - bar_w / 2, y1, x + bar_w / 2, height - bottom, 5,
                         fill=colour, outline=colour)
            c.create_text(x, y1 - 8, text=f"{round(rate * 100)}%",
                          fill=TEXT if rate else MUTED, font=(FONT, 8, "bold"))
            c.create_text(x, height - bottom + 10, text="MTWTFSS"[i],
                          fill=MUTED, font=(FONT, 8))
        c.create_line(left, height - bottom, width - right, height - bottom,
                      fill=BORDER)

    # ---------------------------------------------------------------- actions
    def _toggle_today(self):
        if self.habit:
            self.app.toggle_habit(self.habit)

    def _delete(self):
        if self.habit:
            self.app.delete_habit(self.habit)

    def _export(self):
        self.app.export_csv()


class HabitDialog(tk.Toplevel):
    """Create a new habit, or edit an existing one when `habit` is given."""

    def __init__(self, master, on_create, habit=None):
        super().__init__(master)
        self.on_create = on_create
        self.title("Edit habit" if habit else "New habit")
        self.configure(bg=PANEL)
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.existing = habit

        pad = tk.Frame(self, bg=PANEL, padx=24, pady=20)
        pad.pack(fill="both", expand=True)

        tk.Label(pad, text="EDIT HABIT" if habit else "NEW HABIT", fg=ACCENT, bg=PANEL,
                 font=(FONT, 9, "bold")).pack(anchor="w")

        self.entry = tk.Entry(pad, bg=PANEL_2, fg=TEXT, insertbackground=ACCENT,
                              relief="flat", font=(FONT, 12), width=28,
                              highlightthickness=1, highlightbackground=BORDER,
                              highlightcolor=ACCENT)
        self.entry.pack(fill="x", pady=(10, 14), ipady=6)
        self.entry.insert(0, habit.name if habit else "")

        tk.Label(pad, text="Colour", fg=MUTED, bg=PANEL, font=F_SMALL).pack(anchor="w")
        self.colour = habit.color if habit else PALETTE[0]
        swatches = tk.Frame(pad, bg=PANEL)
        swatches.pack(fill="x", pady=(4, 14))
        self._swatch_labels = {}
        for colour in PALETTE:
            lab = tk.Canvas(swatches, width=24, height=24, bg=PANEL, highlightthickness=0, cursor="hand2")
            lab.pack(side="left", padx=(0, 8))
            rounded_rect(lab, 2, 2, 22, 22, 6, fill=colour, outline=colour)
            lab.bind("<Button-1>", lambda e, col=colour: self._pick(colour))
            self._swatch_labels[colour] = lab

        tk.Label(pad, text="Days per week", fg=MUTED, bg=PANEL, font=F_SMALL).pack(anchor="w")
        self.target = tk.IntVar(value=habit.target if habit else 7)
        row = tk.Frame(pad, bg=PANEL)
        row.pack(fill="x", pady=(4, 16))
        for n in range(1, 8):
            rb = tk.Radiobutton(row, text=str(n), value=n, variable=self.target,
                                bg=PANEL, fg=TEXT, selectcolor=PANEL_2, activebackground=PANEL,
                                activeforeground=ACCENT, font=F_SMALL,
                                highlightthickness=0, bd=0)
            rb.pack(side="left", padx=(0, 6))

        buttons = tk.Frame(pad, bg=PANEL)
        buttons.pack(fill="x")
        FlatButton(buttons, "Save" if habit else "Create", self._create, fg=BG, bg=ACCENT,
                   hover=mix(ACCENT, "#ffffff", 0.25)).pack(side="right")
        FlatButton(buttons, "Cancel", self.destroy, fg=MUTED, bg=PANEL,
                   hover=mix(PANEL, ACCENT, 0.15)).pack(side="right", padx=(0, 8))

        self._pick(self.colour)
        self.bind("<Return>", lambda e: self._create())
        self.bind("<Escape>", lambda e: self.destroy())
        self.update_idletasks()
        self._centre(master)
        self.entry.focus_set()

    def _centre(self, master):
        x = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _pick(self, colour):
        self.colour = colour
        for col, canvas in self._swatch_labels.items():
            canvas.delete("all")
            rounded_rect(canvas, 2, 2, 22, 22, 6, fill=col, outline=col)
            if col == colour:
                canvas.create_oval(8, 8, 16, 16, outline=BG, width=2)

    def _create(self):
        name = self.entry.get().strip()
        if not name:
            self.entry.focus_set()
            return
        self.on_create(name, self.colour, self.target.get())
        self.destroy()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.store = HabitStore()
        self._last_deleted = None
        self.selected: Habit | None = self.store.habits[0] if self.store.habits else None

        self.title("Habit Tracker")
        self.configure(bg=BG)
        try:
            self.iconbitmap(resource_path(os.path.join("assets", "icon.ico")))
        except tk.TclError:
            pass
        self.geometry("1040x660")
        self.minsize(940, 600)
        self._build()
        self._refresh_all()
        self._bind_keys()

    # ------------------------------------------------------------------ build
    def _build(self):
        header = tk.Frame(self, bg=PANEL, height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        left = tk.Frame(header, bg=PANEL)
        left.pack(side="left", padx=22, pady=16)
        tk.Label(left, text="HABIT TRACKER", fg=TEXT, bg=PANEL, font=F_TITLE).pack(anchor="w")
        self.date_label = tk.Label(left, text="", fg=MUTED, bg=PANEL, font=F_SUB)
        self.date_label.pack(anchor="w")

        right = tk.Frame(header, bg=PANEL)
        right.pack(side="right", padx=22)

        self.ring = ProgressRing(right)
        self.ring.pack(side="left", padx=(0, 16))

        self.progress_text = tk.Label(right, text="", fg=MUTED, bg=PANEL, font=F_SMALL)
        self.progress_text.pack(side="left", padx=(0, 16))

        FlatButton(right, "+  New habit", self.new_habit, fg=BG, bg=ACCENT,
                   hover=mix(ACCENT, "#ffffff", 0.25)).pack(side="left")

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        listwrap = tk.Frame(body, bg=PANEL_2, width=330)
        listwrap.pack(side="left", fill="y")
        listwrap.pack_propagate(False)

        tk.Label(listwrap, text="TODAY", fg=MUTED, bg=PANEL_2, font=(FONT, 8, "bold"),
                 anchor="w").pack(fill="x", padx=16, pady=(14, 8))

        self.list_canvas = tk.Canvas(listwrap, bg=PANEL_2, highlightthickness=0)
        self.list_canvas.pack(fill="both", expand=True, padx=(8, 0), pady=(0, 10))
        scroll = tk.Scrollbar(listwrap, orient="vertical", command=self.list_canvas.yview,
                              width=8, bg=PANEL_2, troughcolor=PANEL_2, bd=0,
                              highlightthickness=0, relief="flat")
        scroll.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        self.list_canvas.configure(yscrollcommand=scroll.set)

        self.list_frame = tk.Frame(self.list_canvas, bg=PANEL_2)
        self.list_window = self.list_canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.list_frame.bind("<Configure>",
                             lambda e: self.list_canvas.configure(scrollregion=self.list_canvas.bbox("all")))
        self.list_canvas.bind("<Configure>",
                              lambda e: self.list_canvas.itemconfigure(self.list_window, width=e.width))
        self.list_canvas.bind_all("<MouseWheel>", self._on_wheel)

        tk.Frame(body, bg=BORDER, width=1).pack(side="left", fill="y")

        self.detail = DetailPanel(body, self)
        self.detail.pack(side="left", fill="both", expand=True)

        footer = tk.Frame(self, bg=PANEL_2, height=30)
        footer.pack(fill="x")
        footer.pack_propagate(False)
        self.status = tk.Label(footer, text="", fg=MUTED, bg=PANEL_2, font=F_SMALL)
        self.status.pack(side="left", padx=16)
        tk.Label(footer, text="Ctrl+N new · Space toggle · Del remove · Esc deselect",
                 fg=MUTED, bg=PANEL_2, font=F_SMALL).pack(side="right", padx=16)

    def _bind_keys(self):
        self.bind("<Control-n>", lambda e: self.new_habit())
        self.bind("<Control-N>", lambda e: self.new_habit())
        self.bind("<space>", lambda e: self._toggle_selected())
        self.bind("<Delete>", lambda e: self._delete_selected())
        self.bind("<Escape>", lambda e: self._select(None))
        self.bind("<Control-z>", lambda e: self.undo_delete())

    def _on_wheel(self, event):
        try:
            self.list_canvas.yview_scroll(int(-event.delta / 120), "units")
        except tk.TclError:
            pass

    # ------------------------------------------------------------------ state
    def _refresh_all(self):
        self.date_label.configure(text=date.today().strftime("%A, %d %B %Y"))
        self._rebuild_list()
        self.detail.show(self.selected)
        self._update_header()

    def _update_header(self):
        total = len(self.store.habits)
        done = self.store.done_today()
        share = self.store.progress_today()
        self.ring.set(share, f"{round(share * 100)}%")
        self.progress_text.configure(text=f"{done} of {total} done today" if total else "no habits yet")

    def _rebuild_list(self):
        for child in self.list_frame.winfo_children():
            child.destroy()
        self.rows = []
        if not self.store.habits:
            empty = tk.Label(self.list_frame, text="Nothing here yet.\nPress Ctrl+N to add a habit.",
                             fg=MUTED, bg=PANEL_2, font=F_SMALL, justify="left")
            empty.pack(anchor="w", padx=10, pady=16)
            return
        for habit in self.store.habits:
            row = HabitRow(self.list_frame, habit, self._select, self.toggle_habit, self.edit_habit)
            row.pack(fill="x", pady=1, padx=(0, 6))
            row.set_selected(self.selected is not None and habit.id == self.selected.id)
            self.rows.append(row)

    # ---------------------------------------------------------------- actions
    def _select(self, habit: Habit | None):
        self.selected = habit
        for row in self.rows:
            row.set_selected(habit is not None and row.habit.id == habit.id)
        self.detail.show(habit)

    def _toggle_selected(self):
        if self.selected:
            self.toggle_habit(self.selected)

    def _delete_selected(self):
        if self.selected:
            self.delete_habit(self.selected)

    def toggle_habit(self, habit: Habit):
        self.store.toggle(habit)
        self.selected = habit
        self._refresh_all()
        self._status(f"{'Done' if habit.is_done() else 'Cleared'}: {habit.name}")

    def toggle_day(self, habit: Habit, day):
        """Tick or untick one particular date (used by the heatmap)."""
        state = habit.toggle(day)
        self.store.save()
        self.selected = habit
        self._refresh_all()
        pretty = day.strftime("%d %b") if hasattr(day, "strftime") else str(day)
        self._status(f"{'Done' if state else 'Cleared'} {pretty}: {habit.name}")

    def edit_habit(self, habit: Habit):
        def applied(name, colour, target):
            habit.name, habit.color, habit.target = name, colour, target
            self.store.save()
            self._refresh_all()
            self._status(f"Updated {habit.name}")

        HabitDialog(self, applied, habit=habit)

    def move_habit(self, habit: Habit, offset: int):
        ids = [h.id for h in self.store.habits]
        i = ids.index(habit.id)
        j = i + offset
        if 0 <= j < len(self.store.habits):
            habits = self.store.habits
            habits[i], habits[j] = habits[j], habits[i]
            self.store.save()
            self._refresh_all()
            self._status("Reordered")

    def undo_delete(self):
        if not self._last_deleted:
            self._status("Nothing to undo")
            return
        habit, index = self._last_deleted
        self.store.habits.insert(min(index, len(self.store.habits)), habit)
        self.store.save()
        self.selected = habit
        self._last_deleted = None
        self._refresh_all()
        self._status(f"Restored {habit.name}")

    def delete_habit(self, habit: Habit):
        if not messagebox.askyesno("Delete habit",
                                   f"Delete “{habit.name}” and all of its history?",
                                   parent=self):
            return
        was_selected = self.selected is not None and self.selected.id == habit.id
        self._last_deleted = (habit, self.store.habits.index(habit))
        self.store.remove(habit)
        if was_selected:
            self.selected = self.store.habits[0] if self.store.habits else None
        self._refresh_all()
        self._status(f"Deleted {habit.name}")

    def new_habit(self):
        def created(name, colour, target):
            habit = self.store.add(name, colour, target)
            self.selected = habit
            self._refresh_all()
            self._status(f"Added {habit.name}")

        HabitDialog(self, created)

    def export_csv(self):
        path = filedialog.asksaveasfilename(
            parent=self, title="Export habits as CSV", defaultextension=".csv",
            initialfile=f"habits-{today().isoformat()}.csv",
            filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        try:
            self.store.export_csv(path)
            self._status(f"Exported to {os.path.basename(path)}")
        except OSError as exc:
            messagebox.showerror("Export failed", str(exc), parent=self)

    def backup_json(self):
        """Save a copy of the whole data file, habits and history included."""
        path = filedialog.asksaveasfilename(
            parent=self, title="Back up habits", defaultextension=".json",
            initialfile=f"habits-backup-{today().isoformat()}.json",
            filetypes=[("JSON file", "*.json")])
        if not path:
            return
        try:
            self.store.save()
            shutil.copyfile(self.store.path, path)
            self._status(f"Backup saved: {os.path.basename(path)}")
        except OSError as exc:
            messagebox.showerror("Backup failed", str(exc), parent=self)

    def _status(self, message: str):
        stamp = datetime.now().strftime("%H:%M")
        self.status.configure(text=f"Saved · {stamp} · {message}")


def _log_crash(exc: BaseException) -> None:
    try:
        folder = os.path.dirname(HabitStore().path)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, "error.log"), "a", encoding="utf-8") as fh:
            fh.write(f"{datetime.now():%Y-%m-%d %H:%M:%S}  {exc!r}\n")
    except Exception:
        pass


def main():
    try:
        app = App()
    except Exception as exc:                      # noqa: BLE001 - top-level guard
        _log_crash(exc)
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Habit Tracker", f"The app could not start:\n\n{exc}")
            root.destroy()
        except Exception:
            pass
        raise
    app.mainloop()


if __name__ == "__main__":
    main()
