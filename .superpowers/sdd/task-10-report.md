# Task 10: Hide submission links in ranking (c10)

## What I implemented

Added visibility gating so submission links in the contest ranking table are hidden when the current user doesn't have permission to view submission lists.

### Step 1: `judge/views/contests.py`
Added `can_see_full_submission_list` to the ranking view context in `ContestRanking.get_context_data`:
```python
context['can_see_full_submission_list'] = self.object.can_see_full_submission_list(self.request.user)
```

### Step 2: `templates/contest/ranking.html`
Added JS variable before the script section:
```html
window.CONTEST_CAN_SEE_SUBMISSIONS = {{ can_see_full_submission_list|tojson }};
```

### Step 3: `resources/contest-ranking.js`
- Updated `makeSubmissionUrl` and `makeAllSubmissionsUrl` to return `null` when `CONTEST_CAN_SEE_SUBMISSIONS` is false or `url_templates` is missing
- Updated `wrapProblemCell` to render a plain `<td>` (no `<a>` link) when URL is `null`
- Updated `standardResultCell` to render score text without a link when URL is `null`
- Updated ICPC renderer's `renderResultCell` to handle null URL

## What I tested and test results

- Python syntax check: PASSED (`ast.parse` validated on `judge/views/contests.py`)
- Django check: FAILED due to pre-existing environment issue (`ModuleNotFoundError: No module named 'celery'`) - unrelated to this change

## Files changed

- `judge/views/contests.py` - Added `can_see_full_submission_list` to ranking context
- `templates/contest/ranking.html` - Added `window.CONTEST_CAN_SEE_SUBMISSIONS` JS variable
- `resources/contest-ranking.js` - Conditional link rendering based on permission

## Self-review findings

- The existing `Contest.can_see_full_submission_list()` method is already used elsewhere (stats page, submission views), so this reuses a proven permission check
- All renderers that create links (default, ICPC, freateoj) are covered by the changes to `makeSubmissionUrl`, `makeAllSubmissionsUrl`, `wrapProblemCell`, and `standardResultCell`
- The `tojson` filter ensures proper JSON serialization of the boolean context variable

## Commit

- `a099a9a` - fix: hide submission links in ranking when user can't see submissions
