### Task 7: Remove old partial AC logic (c13)

**Files:**
- Modify: `judge/models/problem.py`
- Modify: `judge/utils/problems.py`
- Modify: `judge/views/problem.py`

**Interfaces:**
- Consumes: existing AC querysets with points comparison
- Produces: simplified AC querysets using result='AC' only

- [ ] **Step 1: Update Problem.update_stats in problem.py**

In `judge/models/problem.py`, find `update_stats` method (line ~509) and change:

```python
# BEFORE:
ac_queryset = all_queryset.filter(points__gte=self.points, result='AC')

# AFTER:
ac_queryset = all_queryset.filter(result='AC')
```

- [ ] **Step 2: Update contest_completed_ids in problems.py**

In `judge/utils/problems.py`, find `contest_completed_ids` (line ~24) and change:

```python
# BEFORE:
result = set(participation.submissions.filter(submission__result='AC', points__gte=F('problem__points'))
             .values_list('problem__problem_id', flat=True).distinct())

# AFTER:
result = set(participation.submissions.filter(submission__result='AC')
             .values_list('problem__problem_id', flat=True).distinct())
```

Also remove the `F` import if it's no longer used.

- [ ] **Step 3: Update hide_solved filter in problem.py**

In `judge/views/problem.py`, find the `hide_solved` filter (line ~622) and change:

```python
# BEFORE:
queryset = queryset.exclude(id__in=Submission.objects
                            .filter(user=self.profile, result='AC', case_points__gte=F('case_total'))
                            .values_list('problem_id', flat=True))

# AFTER:
queryset = queryset.exclude(id__in=Submission.objects
                            .filter(user=self.profile, result='AC')
                            .values_list('problem_id', flat=True))
```

Also remove the `F` import if it's no longer used.

- [ ] **Step 4: Verify F imports**

Run: `grep -n "from django.db.models import F" judge/utils/problems.py judge/views/problem.py`
Expected: Either no matches or F is still used elsewhere

- [ ] **Step 5: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 6: Commit**

```bash
cd /home/nomoka/site
git add judge/models/problem.py judge/utils/problems.py judge/views/problem.py
git commit -m "refactor: remove old partial AC logic, use result=AC only"
```

---

## Phase 2: Bug Fixes

