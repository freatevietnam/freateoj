# Contest Replay + Virtual Ranking Design

## Overview

Add contest ranking replay (animated scoreboard playback) infrastructure and live virtual participation ranking support.

## Model Changes

### File: `judge/models/contest.py`

Add to Contest model:

```python
replay_version = models.IntegerField(default=0)

@property
def can_replay(self):
    return (self.ended and not self.time_limit and 
            self.scoreboard_visibility and self.format_name not in ('ioi', 'ioi16'))
```

- `replay_version`: Tracks which version of replay data is available (0 = no replay)
- `can_replay`: Determines if contest supports replay based on:
  - Contest has ended
  - No time limit (virtual contest)
  - Scoreboard is visible
  - Not IOI format

## Migration

### File: `judge/migrations/0235_contest_replay_version.py`

Auto-generated migration adding `replay_version` field with default=0.

## Settings

### File: `dmoj/settings.py`

```python
FREATEOJ_CONTEST_REPLAY_MEDIA_DIR = '/tmp/contest-replay'
FREATEOJ_CONTEST_REPLAY_INTERNAL = False
```

- `FREATEOJ_CONTEST_REPLAY_MEDIA_DIR`: Directory where replay JSON files are stored
- `FREATEOJ_CONTEST_REPLAY_INTERNAL`: Whether to use internal URL for replay data

## View

### File: `judge/views/contests.py`

Add `ContestReplayData` view:

```python
class ContestReplayData(View):
    def get(self, request, contest, version):
        # Serve replay JSON files from FREATEOJ_CONTEST_REPLAY_MEDIA_DIR
        # Check contest accessibility
        # Return 404 if replay not available
        # Set proper cache headers
```

## URL

### File: `dmoj/urls.py`

Add under contest paths:

```python
path('/replay/<int:version>.json', contests.ContestReplayData.as_view(), name='contest_replay_data'),
```

## Template Changes

### File: `templates/contest/ranking.html`

Add replay button when `contest.can_replay` is true:

```html
{% if contest.can_replay %}
<a href="{{ url('contest_replay_data', contest.key, contest.replay_version) }}" 
   class="button">Replay</a>
{% endif %}
```

## Skeleton JS

### File: `resources/contest-replay.js`

Basic skeleton with:

```javascript
window.ContestReplay = {
    loadReplayData: function(url) { ... },
    play: function() { ... },
    pause: function() { ... },
    setSpeed: function(speed) { ... },
    render: function(data) { ... }
};
```

## Files to Modify/Create

1. `judge/models/contest.py` - Add field and property
2. `judge/migrations/0235_contest_replay_version.py` - Migration
3. `dmoj/settings.py` - Add settings
4. `judge/views/contests.py` - Add view
5. `dmoj/urls.py` - Add URL
6. `templates/contest/ranking.html` - Add replay button
7. `resources/contest-replay.js` - Skeleton JS
