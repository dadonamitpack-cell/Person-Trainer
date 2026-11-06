# Person-Trainer

A personal training + nutrition coaching workspace. Claude acts as coach; every recommendation is tied to
research (position stands, meta-analyses), not anecdotes.

## How it works

| Step | What you do | What Claude does |
|---|---|---|
| 1. Intake | Fill in `profile/intake.md` | Screens safety, sets goals and baseline |
| 2. Your drills | List exercises you know/like in `drills/exercise-library.md` | Builds the program around them, fills gaps |
| 3. Baseline tests | Do the tests in the intake (section 7) | Sets starting loads and targets |
| 4. Plan | — | Writes training plan + nutrition targets in `plans/` |
| 5. Weekly check-in | Fill `logs/weekly-checkin-template.md` (copy per week) | Adjusts load, volume, calories |
| 6. Every 4–6 weeks | Re-test | Reviews progress, deloads, sets next block |

## Files
- `docs/evidence-base.md` — the research the coaching is based on, with references
- `profile/intake.md` — **start here**: the questionnaire
- `drills/exercise-library.md` — your exercises
- `physio/current.md` — paste your latest physio advice here; it goes into every week
- `logs/` — session log and weekly check-in templates
- `plans/` — your programs (created after intake)
- `logs/watch/` + `scripts/watch_summary.py` — automatic daily Apple Watch data (setup: `docs/apple-watch-sync.md`)
