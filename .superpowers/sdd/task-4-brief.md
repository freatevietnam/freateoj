### Task 4: Remove api_v2 REST API (c2)

**Files:**
- Modify: `judge/views/api/__init__.py`
- Modify: `dmoj/urls.py`
- Modify: `dmoj/settings.py`
- Delete: `judge/views/api/api_v2.py`

**Interfaces:**
- Consumes: existing api_v2 module
- Produces: api_v2 removed, only sync API kept

- [ ] **Step 1: Simplify api/__init__.py**

Replace content of `judge/views/api/__init__.py`:
```python
from . import api_v2
```

- [ ] **Step 2: Remove api_v2 URL patterns from dmoj/urls.py**

In `dmoj/urls.py`, find the api_v2 URL section (around line 461-472) and remove all the non-sync API endpoints. Keep only the sync API endpoints.

Remove these lines:
```python
path('contests', api.api_v2.APIContestList.as_view()),
path('contest/<str:contest>', api.api_v2.APIContestDetail.as_view()),
path('problems', api.api_v2.APIProblemList.as_view()),
path('problem/<str:problem>', api.api_v2.APIProblemDetail.as_view()),
path('users', api.api_v2.APIUserList.as_view()),
path('user/<str:user>', api.api_v2.APIUserDetail.as_view()),
path('submissions', api.api_v2.APISubmissionList.as_view()),
path('submission/<int:submission>', api.api_v2.APISubmissionDetail.as_view()),
path('organizations', api.api_v2.APIOrganizationList.as_view()),
path('participations', api.api_v2.APIContestParticipationList.as_view()),
path('languages', api.api_v2.APILanguageList.as_view()),
path('judges', api.api_v2.APIJudgeList.as_view()),
```

Keep only the sync API endpoints (around line 474+).

- [ ] **Step 3: Add FREATEOJ_ENABLE_SYNC_API setting**

In `dmoj/settings.py`, add after `FREATEOJ_ENABLE_API`:
```python
FREATEOJ_ENABLE_SYNC_API = False
```

- [ ] **Step 4: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 5: Commit**

```bash
cd /home/nomoka/site
git add judge/views/api/__init__.py dmoj/urls.py dmoj/settings.py
git commit -m "feat: remove unused api_v2 REST API, keep only sync API"
```

---

