#!/usr/bin/env python3
"""
start-session.py — Ping Claude Code to start the usage window timer.

Usage:
  python start-session.py              # ping Claude now
  python start-session.py 08:30        # schedule daily ping at 8:30am via cron
  python start-session.py --remove     # remove scheduled cron job
"""

import subprocess
import sys
import re
from datetime import datetime
from pathlib import Path

SCRIPT_PATH = str(Path(__file__).resolve())


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


def schedule(hour: int, minute: int):
    lines = [l for l in get_crontab() if SCRIPT_PATH not in l]
    lines.append(f"{minute} {hour} * * * /usr/bin/env python3 {SCRIPT_PATH}")
    set_crontab(lines)
    print(f"Scheduled daily session ping at {hour:02d}:{minute:02d}.")
    print(f"Run 'python {SCRIPT_PATH} --remove' to cancel.")


def remove():
    lines = [l for l in get_crontab() if SCRIPT_PATH not in l]
    set_crontab(lines)
    print("Removed scheduled session ping.")


def main():
    if len(sys.argv) == 1:
        ping_claude()

    elif sys.argv[1] == "--remove":
        remove()

    elif re.fullmatch(r"\d{1,2}:\d{2}", sys.argv[1]):
        hour, minute = map(int, sys.argv[1].split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            print("Invalid time. Use HH:MM in 24-hour format.")
            sys.exit(1)
        schedule(hour, minute)

    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
