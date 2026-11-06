# Apple Watch daily data

One JSON file per day (`YYYY-MM-DD.json`), written automatically by the iPhone Shortcut described in
`docs/apple-watch-sync.md`. Do not edit by hand.

```json
{"date": "2026-11-06", "rhr": 44, "hrv": 72.5, "sleep_h": 7.4, "steps": 12850,
 "exercise_min": 65, "hr_max": 186, "vo2max": 55.1, "weight": 85.2}
```

| Field | Meaning | How Claude uses it |
|---|---|---|
| `rhr` | Resting HR (bpm) | Week trend vs 4-week baseline; 5+ bpm up on several days = back off |
| `hrv` | HRV, SDNN (ms), daily average | Trend only vs personal baseline; never one day |
| `sleep_h` | Hours asleep last night | Weekly average; < 7 h is a flag |
| `steps`, `exercise_min` | Daily activity | Context for load |
| `hr_max` | Highest HR of the day | Match/HIIT intensity check (max HR ~190) |
| `vo2max` | Apple cardio-fitness estimate | Slow trend only (error ~10–15%) |
| `weight` | Latest weigh-in, if any | Occasional trend |

Summary: `python3 scripts/watch_summary.py`
