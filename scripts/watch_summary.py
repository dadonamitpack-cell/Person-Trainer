#!/usr/bin/env python3
"""Summarize daily Apple Watch exports in logs/watch/*.json.

Each file is one day, written by the iPhone Shortcut (see docs/apple-watch-sync.md):
  {"date": "2026-11-06", "rhr": 44, "hrv": 72.5, "sleep_h": 7.4, "steps": 12850,
   "exercise_min": 65, "hr_max": 186, "vo2max": 55.1, "weight": 85.2}
Any field may be missing or empty.

Usage: python3 scripts/watch_summary.py [--days 28] [--dir logs/watch]
Prints a weekly table, compares the last 7 days with a personal baseline, and flags
trends (not single days) worth acting on.
"""
import argparse
import json
import statistics as st
from datetime import date, timedelta
from pathlib import Path

FIELDS = ["rhr", "hrv", "sleep_h", "steps", "exercise_min", "hr_max", "vo2max", "weight"]


def num(v):
    try:
        f = float(str(v).replace(",", "."))
        return f if f > 0 else None
    except (TypeError, ValueError):
        return None


def load(d: Path):
    rows = {}
    for p in sorted(d.glob("*.json")):
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
            day = date.fromisoformat(str(raw.get("date") or p.stem)[:10])
        except (ValueError, json.JSONDecodeError):
            print(f"skip unreadable file: {p.name}")
            continue
        r = {k: num(raw.get(k)) for k in FIELDS}
        # Shortcuts may report sleep duration in seconds or minutes instead of hours
        if r["sleep_h"] and r["sleep_h"] > 1440:
            r["sleep_h"] /= 3600
        elif r["sleep_h"] and r["sleep_h"] > 24:
            r["sleep_h"] /= 60
        rows[day] = r
    return rows


def mean(rows, days, key):
    vals = [rows[d][key] for d in days if d in rows and rows[d][key] is not None]
    return (st.mean(vals), len(vals)) if vals else (None, 0)


def fmt(v, nd=1):
    return "-" if v is None else f"{v:.{nd}f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=str(Path(__file__).resolve().parent.parent / "logs" / "watch"))
    ap.add_argument("--days", type=int, default=28, help="baseline window before the last 7 days")
    a = ap.parse_args()

    rows = load(Path(a.dir))
    if not rows:
        print("No watch data yet.")
        return
    end = max(rows)
    last7 = [end - timedelta(i) for i in range(7)]
    base = [end - timedelta(i) for i in range(7, 7 + a.days)]

    # Weekly table (ISO weeks), newest first
    weeks = {}
    for d in rows:
        weeks.setdefault(d.isocalendar()[:2], []).append(d)
    print(f"Data: {min(rows)} to {end} ({len(rows)} days)\n")
    print("Week      days  RHR   HRV   Sleep  Steps   Ex.min  HRmax  VO2max  Weight")
    for (y, w), ds in sorted(weeks.items(), reverse=True)[:8]:
        m = {k: mean(rows, ds, k)[0] for k in FIELDS}
        hrmax = max((rows[d]["hr_max"] for d in ds if rows[d]["hr_max"]), default=None)
        print(f"{y}-W{w:02d}  {len(ds):>4}  {fmt(m['rhr'],0):>4}  {fmt(m['hrv'],0):>4}  {fmt(m['sleep_h']):>5}"
              f"  {fmt(m['steps'],0):>6}  {fmt(m['exercise_min'],0):>6}  {fmt(hrmax,0):>5}"
              f"  {fmt(m['vo2max']):>6}  {fmt(m['weight']):>6}")

    print("\nLast 7 days vs baseline:")
    flags = []
    for key, label in [("rhr", "Resting HR"), ("hrv", "HRV (SDNN)"), ("sleep_h", "Sleep h")]:
        now, n_now = mean(rows, last7, key)
        ref, n_ref = mean(rows, base, key)
        if now is None or n_ref < 7:
            print(f"  {label:<11} {fmt(now)} (baseline needs 7+ days, have {n_ref})")
            continue
        print(f"  {label:<11} {fmt(now)} vs {fmt(ref)} ({now - ref:+.1f})")
        if key == "rhr" and now - ref >= 5:
            flags.append("Resting HR 5+ bpm above baseline for the week: reduce intensity, check sleep/illness.")
        if key == "hrv":
            vals = [rows[d][key] for d in base if d in rows and rows[d][key]]
            sd = st.stdev(vals) if len(vals) > 1 else 0
            if sd and now < ref - sd:
                flags.append("HRV week average below baseline by more than 1 SD: recovery is lagging.")
        if key == "sleep_h" and now < 7:
            flags.append("Sleep under 7 h average this week.")
    # RHR elevated on 3+ of last 7 days
    ref_rhr, n_ref = mean(rows, base, "rhr")
    if ref_rhr and n_ref >= 7:
        hi = sum(1 for d in last7 if d in rows and rows[d]["rhr"] and rows[d]["rhr"] - ref_rhr >= 5)
        if hi >= 3:
            flags.append(f"Resting HR 5+ bpm above baseline on {hi} of the last 7 days.")
    print("\nFlags:" if flags else "\nFlags: none")
    for f in dict.fromkeys(flags):
        print("  - " + f)


if __name__ == "__main__":
    main()
