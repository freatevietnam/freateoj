# Design: Patch VNOI-Admin/OJ Updates

## Goal
Apply 13 commits from VNOI-Admin/OJ to the freateoj codebase while preserving Socket.IO event system and adapting `VNOJ_` settings to `FREATEOJ_` prefix.

## Commits to Apply (all 13)

| # | Commit | Description | Priority |
|---|--------|-------------|----------|
| c1 | a61d88a | Remove suggester feature | High |
| c2 | 703ca05 | Remove api_v2 REST API | High |
| c3 | b9c8bb1 | Fix dark mode chart colors | Low |
| c4 | 9b609c5 | Add contest replay + virtual ranking | High |
| c5 | 1fb76e8 | Improve problem picker | Medium |
| c6 | 26892ea | Checker args validation | Low |
| c7 | a42c67d | Remove manifest.json | Low |
| c8 | 1dafffc | Remove participation tab | Medium |
| c9 | c2598f1 | Infinite pagination for contrib list | Low |
| c10 | bb38391 | Hide submission links in ranking | Medium |
| c11 | 44fb88e | Disable style in markdown (security) | High |
| c12 | d31dce6 | Update bleach tests | High |
| c13 | 9488517 | Remove old partial AC logic | Medium |

## What Gets Preserved
- Socket.IO event system (daemon.js, event_poster.py, template integration)
- All `FREATEOJ_` setting names (adapted from `VNOJ_`)
- Django 5.2 compatibility

## Implementation Order

### Phase 1: Security & Cleanup
1. **c11** - Disable style in markdown (`dmoj/settings.py`)
2. **c12** - Update bleach tests (`judge/jinja2/markdown/test_markdown.py`)
3. **c1** - Remove suggester feature (model, views, URLs, templates, permissions, migrations)
4. **c2** - Remove api_v2 REST API (views, URLs, settings)
5. **c7** - Remove manifest.json
6. **c8** - Remove participation tab (views, URLs, templates)
7. **c13** - Remove old partial AC logic (models, utils, views)

### Phase 2: Bug Fixes
8. **c3** - Fix dark mode chart colors (`templates/stats/media-js.html`)
9. **c6** - Checker args validation (`judge/utils/problem_data.py`)
10. **c10** - Hide submission links in ranking (views, templates, JS)

### Phase 3: Features
11. **c4** - Add contest replay + virtual ranking (model, views, templates, JS, settings)
12. **c5** - Improve problem picker (select2 views, URLs, templates)
13. **c9** - Infinite pagination for contrib list (`judge/views/user.py`)

## Key Adaptations

### Settings Translation
| VNOJ_ setting | FREATEOJ_ setting |
|---------------|-------------------|
| `VNOJ_ENABLE_API` | `FREATEOJ_ENABLE_API` |
| `VNOJ_ENABLE_SYNC_API` | `FREATEOJ_ENABLE_SYNC_API` |
| `VNOJ_CP_PROBLEM` | `FREATEOJ_CP_PROBLEM` |
| `CONTEST_REPLAY_MEDIA_DIR` | `FREATEOJ_CONTEST_REPLAY_MEDIA_DIR` |
| `DMOJ_CONTEST_REPLAY_INTERNAL` | `FREATEOJ_CONTEST_REPLAY_INTERNAL` |

### Socket.IO Preservation
- Do NOT touch `websocket/daemon.js`
- Do NOT touch `judge/event_poster.py`
- Do NOT touch `judge/template_context.py` (comet_location)
- Do NOT touch `templates/base.html` Socket.IO initialization
- Do NOT touch `dmoj/settings.py` EVENT_DAEMON_* settings
- Do NOT touch `dmoj/local_settings.py` EVENT_DAEMON_* overrides

## Verification
- Run `python manage.py check` after each phase
- Run existing test suite
- Verify Socket.IO still works (check daemon.js, event_poster imports)
- Verify no `VNOJ_` references remain (should all be `FREATEOJ_`)
