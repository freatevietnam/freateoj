### Task 3: Remove suggester feature (c1)

**Files:**
- Modify: `judge/models/problem.py`
- Modify: `judge/views/problem.py`
- Modify: `judge/urls.py` (dmoj/urls.py)
- Modify: `templates/contest/list.html` (if suggest tabs exist)
- Create: `judge/migrations/0232_remove_problem_suggester.py`

**Interfaces:**
- Consumes: existing Problem model with suggester field
- Produces: Problem model without suggester, no suggest URLs

- [ ] **Step 1: Remove suggester field from Problem model**

In `judge/models/problem.py`, remove line 240:
```python
# DELETE THIS LINE:
suggester = models.ForeignKey(Profile, blank=True, null=True, related_name='suggested_problems', on_delete=SET_NULL)
```

- [ ] **Step 2: Remove is_suggesting property**

In `judge/models/problem.py`, remove lines 273-275:
```python
# DELETE THIS PROPERTY:
@property
def is_suggesting(self):
    return self.suggester is not None and not self.is_public
```

- [ ] **Step 3: Update get_editable_problems method**

In `judge/models/problem.py`, update `get_editable_problems` (line ~427):

```python
@classmethod
def get_editable_problems(cls, user):
    if not user.has_perm('judge.edit_own_problem'):
        return cls.objects.none()
    if user.has_perm('judge.edit_all_problem'):
        return cls.objects.all()

    q = Q(authors=user.profile) | Q(curators=user.profile)

    if user.has_perm('judge.edit_public_problem'):
        q |= Q(is_public=True)

    return cls.objects.filter(q)
```

- [ ] **Step 4: Update editor_ids property**

In `judge/models/problem.py`, update `editor_ids` (line ~452):

```python
@cached_property
def editor_ids(self):
    editors = self.author_ids.union(
        Problem.curators.through.objects.filter(problem=self).values_list('profile_id', flat=True))
    return editors
```

- [ ] **Step 5: Remove suggest_list and suggest URLs**

In `dmoj/urls.py`, find and remove these lines (around line 110-111):
```python
# DELETE THESE LINES:
path('/suggest_list/', problem.SuggestList.as_view(), name='problem_suggest_list'),
path('/suggest', problem.ProblemSuggest.as_view(), name='problem_suggest'),
```

- [ ] **Step 6: Remove SuggestList and ProblemSuggest imports**

In `dmoj/urls.py`, find where `problem.SuggestList` and `problem.ProblemSuggest` are imported and remove those imports.

- [ ] **Step 7: Create migration**

Run: `cd /home/nomoka/site && python manage.py makemigrations judge --name remove_problem_suggester`
Expected: Creates migration file removing suggester field

- [ ] **Step 8: Verify migration**

Run: `cd /home/nomoka/site && python manage.py showmigrations judge | grep 0232`
Expected: Migration exists

- [ ] **Step 9: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 10: Commit**

```bash
cd /home/nomoka/site
git add judge/models/problem.py judge/urls.py judge/migrations/
git commit -m "feat: remove suggester feature"
```

---

