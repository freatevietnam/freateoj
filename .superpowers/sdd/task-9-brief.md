### Task 9: Checker args validation (c6)

**Files:**
- Modify: `judge/utils/problem_data.py`

**Interfaces:**
- Consumes: existing make_checker function
- Produces: validation error when checker_args missing for bridged checker

- [ ] **Step 1: Add validation in make_checker**

In `judge/utils/problem_data.py`, find the `make_checker` function (around line 149) and add validation:

```python
def make_checker(case):
    if case.checker == 'bridged':
        if not case.checker_args:
            raise ProblemDataError(_('How did you corrupt the checker arguments?'))
        return {
            'name': case.checker,
            'args': json.loads(case.checker_args),
        }
    return case.checker
```

- [ ] **Step 2: Verify import**

Run: `grep -n "ProblemDataError" /home/nomoka/site/judge/utils/problem_data.py`
Expected: ProblemDataError is imported

- [ ] **Step 3: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 4: Commit**

```bash
cd /home/nomoka/site
git add judge/utils/problem_data.py
git commit -m "fix: validate checker_args for bridged checker"
```

---

