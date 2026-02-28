# Proposed Structure

```
kokoro/
├── __init__.py          # Monkey patching (gevent + psycogreen)
├── database.py          # Manual engine creation, session factory, pool config
├── models.py            # Empty - models to be defined later
└── app.py               # Flask app factory + basic routes

tests/
├── __init__.py
└── conftest.py          # Pytest fixtures (app, client, db session)
```

## Files Overview

| File | Purpose |
|------|---------|
| `kokoro/__init__.py` | Gevent monkey patching, runs first on import |
| `kokoro/database.py` | `create_engine()`, `get_session()`, `get_connection()`, pool helpers |
| `kokoro/models.py` | Empty `Base` declaration, models added later |
| `kokoro/app.py` | `create_app()` factory, health/pool status routes |
| `tests/conftest.py` | Fixtures for testing with/without gevent |
