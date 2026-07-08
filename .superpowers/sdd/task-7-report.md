### Task 7: Remove old partial AC logic (c13)

**Status:** DONE

**What was implemented:**
Removed old `case_points >= case_total` / `points >= problem.points` comparisons from AC queryset filters in three files. AC is now determined solely by `result='AC'`, matching the new judge behavior from PR #619.

**Files changed:**
- `judge/models/problem.py:487` — `update_stats`: removed `points__gte=self.points` from AC filter
- `judge/utils/problems.py:28` — `contest_completed_ids`: removed `points__gte=F('problem__points')` from filter; `F` import kept (still used in `hot_problems`)
- `judge/views/problem.py:13` — Removed unused `F` import from `django.db.models`
- `judge/views/problem.py:624` — `get_normal_queryset` hide_solved: removed `case_points__gte=F('case_total')` from filter

**Testing:**
- All three files compile without errors (`py_compile`)
- Django `manage.py check` could not run due to missing `celery` module in the environment (pre-existing issue, unrelated to changes)

**Self-review findings:**
- `F` import was correctly removed from `judge/views/problem.py` (no other usages in that file)
- `F` import was correctly kept in `judge/utils/problems.py` (still used in `hot_problems` function)
- No other partial AC logic remains in the codebase (searched for `points__gte` and `case_points__gte` patterns)

**Commit:** `e30afd7` — `refactor: remove old partial AC logic, use result=AC only`
