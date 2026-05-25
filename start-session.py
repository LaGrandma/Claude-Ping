#!/usr/bin/env python3
"""
start-session.py — Ping Claude Code to start the usage window timer.

Usage:
  start-session                        # ping Claude now
  start-session 08:30                  # ping every day at 08:30
  start-session 08:30 mon              # ping every Monday at 08:30
  start-session 08:30 mon,wed,fri      # ping on multiple days
  start-session --list                 # show all scheduled pings
  start-session --remove               # remove all scheduled pings
  start-session --remove mon           # remove ping for specific day(s)
"""

import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

SCRIPT_PATH = str(Path(__file__).resolve())

DAYS = {
    "sun": 0, "sunday": 0,
    "mon": 1, "monday": 1,
    "tue": 2, "tuesday": 2,
    "wed": 3, "wednesday": 3,
    "thu": 4, "thursday": 4,
    "fri": 5, "friday": 5,
    "sat": 6, "saturday": 6,
}

DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def ping_claude():
    print(f"Starting Claude session at {datetime.now()}...")
    subprocess.run(
        ["claude", "-p", "Session start", "--output-format", "text"],
        stderr=subprocess.DEVNULL,
    )
    print(f"Session activated at {datetime.now().strftime('%H:%M:%S')}")


def get_crontab() -> list[str]:
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        return []
    return result.stdout.splitlines()


def set_crontab(lines: list[str]):
    content = "\n".join(lines) + "\n" if lines else ""
    subprocess.run(["crontab", "-"], input=content, text=True, check=True)


def our_lines(lines: list[str]) -> list[str]:
    return [l for l in lines if SCRIPT_PATH in l]


def parse_days(day_str: str) -> list[int]:
    parts = [d.strip().lower() for d in day_str.split(",")]
    result = []
    for p in parts:
        if p not in DAYS:
            print(f"Unknown day: '{p}'. Use mon, tue, wed, thu, fri, sat, sun.")
            sys.exit(1)
        result.append(DAYS[p])
    return sorted(set(result))


def schedule(hour: int, minute: int, days: list[int] | None):
    lines = get_crontab()

    if days is None:
        # Daily — remove all our entries then add one
        lines = [l for l in lines if SCRIPT_PATH not in l]
        lines.append(f"{minute} {hour} * * * /usr/bin/env python3 {SCRIPT_PATH}")
        label = "every day"
    else:
        day_field = ",".join(str(d) for d in days)
        day_label = ", ".join(DAY_NAMES[d] for d in days)
        # Remove existing entries for these specific days
        lines = [
            l for l in lines
            if not (SCRIPT_PATH in l and _line_day(l) in [str(d) for d in days])
        ]
        lines.append(f"{minute} {hour} * * {day_field} /usr/bin/env python3 {SCRIPT_PATH}")
        label = day_label

    set_crontab(lines)
    print(f"Scheduled session ping at {hour:02d}:{minute:02d} on {label}.")
    print(f"Run 'start-session --list' to see all schedules.")


def _line_day(line: str) -> str:
    """Extract the day-of-week field from a cron line."""
    parts = line.strip().split()
    return parts[4] if len(parts) >= 5 else "*"


def list_schedules():
    lines = our_lines(get_crontab())
    if not lines:
        print("No scheduled pings.")
        return
    print("Scheduled pings:")
    for line in lines:
        parts = line.strip().split()
        minute, hour, _, _, day = parts[:5]
        time_str = f"{int(hour):02d}:{int(minute):02d}"
        if day == "*":
            day_str = "every day"
        else:
            day_str = ", ".join(DAY_NAMES[int(d)] for d in day.split(","))
        print(f"  {time_str}  —  {day_str}")


def remove(days: list[int] | None):
    lines = get_crontab()
    if days is None:
        lines = [l for l in lines if SCRIPT_PATH not in l]
        print("Removed all scheduled pings.")
    else:
        lines = [
            l for l in lines
            if not (SCRIPT_PATH in l and _line_day(l) in [str(d) for d in days])
        ]
        day_label = ", ".join(DAY_NAMES[d] for d in days)
        print(f"Removed scheduled ping for {day_label}.")
    set_crontab(lines)


def parse_time(s: str) -> tuple[int, int]:
    hour, minute = map(int, s.split(":"))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        print("Invalid time. Use HH:MM in 24-hour format.")
        sys.exit(1)
    return hour, minute


def main():
    args = sys.argv[1:]

    if not args:
        ping_claude()

    elif args[0] == "--list":
        list_schedules()

    elif args[0] == "--remove":
        days = parse_days(args[1]) if len(args) > 1 else None
        remove(days)

    elif re.fullmatch(r"\d{1,2}:\d{2}", args[0]):
        hour, minute = parse_time(args[0])
        days = parse_days(args[1]) if len(args) > 1 else None
        schedule(hour, minute, days)

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
