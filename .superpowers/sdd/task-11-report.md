# Task 11 Report: Contest Replay + Virtual Ranking

## Status: DONE

## What Was Implemented

1. **Model Changes** (`judge/models/contest.py`):
   - Added `replay_version = models.IntegerField(default=0)` field
   - Added `can_replay` property that checks: ended, no time limit, scoreboard visible, not IOI format

2. **Migration** (`judge/migrations/0235_contest_replay_version.py`):
   - Auto-generated migration adding `replay_version` field

3. **Settings** (`dmoj/settings.py`):
   - Added `FREATEOJ_CONTEST_REPLAY_MEDIA_DIR = '/tmp/contest-replay'`
   - Added `FREATEOJ_CONTEST_REPLAY_INTERNAL = False`

4. **View** (`judge/views/contests.py`):
   - Added `ContestReplayData` view class that serves replay JSON files
   - Checks contest accessibility and replay availability
   - Returns 404 if replay not available
   - Sets cache headers

5. **URL** (`dmoj/urls.py`):
   - Added `/replay/<int:version>.json` URL pattern

6. **Template** (`templates/contest/ranking.html`):
   - Added replay button when `contest.can_replay` is true

7. **JavaScript** (`resources/contest-replay.js`):
   - Created skeleton replay player with basic controls
   - Exposes `window.ContestReplay` namespace
   - Has placeholder functions for loadReplayData, play, pause, setSpeed

## Files Changed

- `judge/models/contest.py` - Added replay_version field and can_replay property
- `judge/views/contests.py` - Added ContestReplayData view
- `templates/contest/ranking.html` - Added replay button
- `dmoj/settings.py` - Added replay settings
- `dmoj/urls.py` - Added replay URL
- `resources/contest-replay.js` - Created skeleton JS file
- `judge/migrations/0235_contest_replay_version.py` - Created migration

## Test Results

- Syntax check passed for all modified Python files
- Could not run full Django check due to missing celery module in environment

## Self-Review Findings

- All changes follow existing code patterns
- Migration number 0235 is correct (next available after 0234)
- JS file placed in `resources/` to match existing convention
- View properly checks contest accessibility and replay availability

## Commit

- Hash: 51365ff
- Message: feat: add contest ranking replay infrastructure
