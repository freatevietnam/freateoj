### Task 11: Add contest replay + virtual ranking (c4)

**Files:**
- Modify: `judge/models/contest.py`
- Modify: `judge/views/contests.py`
- Modify: `templates/contest/ranking.html`
- Modify: `dmoj/settings.py`
- Create: `static/contest-replay.js`
- Create: `judge/migrations/0233_contest_replay_version.py`

**Interfaces:**
- Consumes: existing Contest model, ranking view
- Produces: replay feature with animated scoreboard playback

- [ ] **Step 1: Add replay_version field to Contest model**

In `judge/models/contest.py`, add to Contest model:

```python
replay_version = models.IntegerField(default=0)
```

- [ ] **Step 2: Add can_replay property**

In `judge/models/contest.py`, add property to Contest:

```python
@property
def can_replay(self):
    return (self.ended and not self.time_limit and 
            self.scoreboard_visibility and not self.is_ioi_format)
```

- [ ] **Step 3: Add replay settings**

In `dmoj/settings.py`, add:

```python
FREATEOJ_CONTEST_REPLAY_MEDIA_DIR = '/tmp/contest-replay'
FREATEOJ_CONTEST_REPLAY_INTERNAL = False
```

- [ ] **Step 4: Create migration**

Run: `cd /home/nomoka/site && python manage.py makemigrations judge --name contest_replay_version`

- [ ] **Step 5: Add ContestReplayData view**

In `judge/views/contests.py`, add new view class:

```python
class ContestReplayData(View):
    def get(self, request, contest, version):
        # Serve replay JSON files with caching
        ...
```

- [ ] **Step 6: Add replay URL**

In `dmoj/urls.py`, add:

```python
path('/replay/<int:version>.json', contests.ContestReplayData.as_view(), name='contest_replay_data'),
```

- [ ] **Step 7: Add replay button in ranking template**

In `templates/contest/ranking.html`, add replay button when contest.can_replay is true.

- [ ] **Step 8: Create contest-replay.js**

Create `static/contest-replay.js` with animated replay player functionality.

- [ ] **Step 9: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 10: Commit**

```bash
cd /home/nomoka/site
git add judge/models/contest.py judge/views/contests.py templates/contest/ranking.html dmoj/settings.py dmoj/urls.py static/contest-replay.js judge/migrations/
git commit -m "feat: add contest ranking replay and live virtual ranking"
```

---

