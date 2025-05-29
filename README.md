# Seequell

> A Django middleware for inspecting SQL queries in development.

Seequell logs and analyzes SQL queries for every HTTP request, helping you identify N+1s, slow queries, and duplicate patterns — all directly in your terminal using rich formatting.

---

## Features

- Logs every SQL query in a request
- Highlights slow queries exceeding a configurable threshold
- Detects duplicate queries (normalized SQL analysis)
- Pluggable analyzer system for custom checks
- Beautiful output using [Rich](https://github.com/Textualize/rich)

---

## Requirements

- Django >= 3.2
- Python >= 3.8
- Only tested w/ relational dbs (postgres, mysql, sqlite)
- Only use this in dev, not prod

---

## Installation

```bash
pip install seequell
```

or with Poetry:

```bash
poetry add --dev seequell
```

---

## Setup

1. Add `SeequellMiddleware` to your middleware list in `settings.py`

```py
MIDDLEWARE = [
    # ...
    "seequell.middleware.SeequellMiddleware",
]
```

2. (Optional) Customize settings using the `SEEQUELL` dict in your `settings.py`

```py
SEEQUELL = {
    "ENABLED": True,
    "MAX_QUERY_THRESHOLD": 0.01,  # seconds
    "ENABLED_ANALYZERS": [
        "seequell.analyzers.slow_query.SlowQueryAnalyzer",
        "seequell.analyzers.duplicate_query.DuplicateQueryAnalyzer",
    ],
}
```
