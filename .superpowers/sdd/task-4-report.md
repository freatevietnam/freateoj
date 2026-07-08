# Task 4: Remove api_v2 REST API (c2) — Report

## What I Implemented

Removed the unused api_v2 REST API endpoints, keeping only the sync API:

1. **`judge/views/api/__init__.py`** — Simplified from explicit class imports to `from . import api_v2`
2. **`dmoj/urls.py`** — Removed the `FREATEOJ_ENABLE_API` block (12 endpoint paths for contests, problems, users, submissions, organizations, participations, languages, judges)
3. **`dmoj/settings.py`** — Already had `FREATEOJ_ENABLE_SYNC_API = True` and `FREATEOJ_ENABLE_API = False`, no changes needed

## What I Tested

- Both modified Python files compile without syntax errors (`py_compile`)
- Django `manage.py check` could not run due to missing dependencies (celery, etc.) in the environment
- Reviewed git diff to confirm only intended lines were removed

## Files Changed

| File | Change |
|------|--------|
| `judge/views/api/__init__.py` | Simplified import |
| `dmoj/urls.py` | Removed api_v2 REST endpoint block (18 lines) |

## Self-Review Findings

- The sync API endpoints under `FREATEOJ_ENABLE_SYNC_API` remain intact
- The `api_v2.py` file itself was NOT deleted (task brief listed it but keeping the module is needed for sync classes)
- `FREATEOJ_ENABLE_API` setting still exists in settings.py but is now unused — acceptable for backward compatibility

## Commit

- `ffd1fab` — feat: remove unused api_v2 REST API, keep only sync API
