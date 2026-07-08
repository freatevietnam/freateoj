### Task 6: Remove participation tab (c8)

**Files:**
- Modify: `judge/views/contests.py`
- Modify: `judge/views/select2.py`
- Modify: `dmoj/urls.py`
- Modify: `templates/contest/contest-tabs.html`
- Modify: `templates/contest/ranking.html`

**Interfaces:**
- Consumes: existing ContestParticipationList, ContestUserSearchSelect2View
- Produces: participation feature removed

- [ ] **Step 1: Remove ContestParticipationList from contests.py**

In `judge/views/contests.py`, find the `ContestParticipationList` class (line ~1164) and remove the entire class.

- [ ] **Step 2: Remove ContestUserSearchSelect2View from select2.py**

In `judge/views/select2.py`, find `ContestUserSearchSelect2View` (line ~173) and remove the entire class.

- [ ] **Step 3: Remove participation URLs from dmoj/urls.py**

In `dmoj/urls.py`, find and remove these lines (around line 267-268):
```python
# DELETE THESE LINES:
path('/participations/', contests.ContestParticipationList.as_view(), name='contest_participation_own'),
path('/participations/<str:user>', ...),
```

- [ ] **Step 4: Remove contest_users select2 URL**

In `dmoj/urls.py`, find and remove (around line 360):
```python
# DELETE THIS LINE:
path('contest_users/<str:contest>', ContestUserSearchSelect2View.as_view(), ...),
```

- [ ] **Step 5: Remove participation tab from contest-tabs.html**

In `templates/contest/contest-tabs.html`, find and remove (around line 27-29):
```html
<!-- DELETE THESE LINES: -->
{% if request.user.is_authenticated %}
    {{ make_tab('participation', 'fa-users', url('contest_participation_own', contest.key), _('Participation')) }}
{% endif %}
```

- [ ] **Step 6: Remove participation search from ranking.html**

In `templates/contest/ranking.html`, find and remove (around line 488-491):
```html
<!-- DELETE THESE LINES: -->
{% if tab == 'participation' %}
    {% if contest.can_see_full_scoreboard(request.user) %}
        <input id="search-contest" type="text" placeholder="{{ _('View user participation') }}">
    {% endif %}
{% endif %}
```

- [ ] **Step 7: Remove ContestParticipationList from __all__**

In `judge/views/contests.py`, find the `__all__` list and remove `'ContestParticipationList'` from it.

- [ ] **Step 8: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 9: Commit**

```bash
cd /home/nomoka/site
git add judge/views/contests.py judge/views/select2.py dmoj/urls.py templates/contest/contest-tabs.html templates/contest/ranking.html
git commit -m "feat: remove participation tab from contest pages"
```

---

