### Task 9 Report: Checker args validation (c6)

**What you implemented:**
Added validation in `make_checker` function to raise `ProblemDataError` when `checker_args` is missing for a bridged checker. Also ensured that for bridged checkers, the function returns the dictionary with checker name and parsed args (rather than falling through to the generic check).

**What you tested and test results:**
1. Verified that `ProblemDataError` is defined in the file (line 44) and already used throughout.
2. Verified that required imports (`json`, `gettext as _`) are present.
3. Ran `python3 -c "import sys; sys.path.insert(0, '/home/nomoka/site'); import judge.utils.problem_data"` – no import errors.
4. Attempted `python3 manage.py check` but failed due to missing `celery` module (unrelated to our change). The import test confirms the module loads without syntax errors.

**Files changed:**
- `judge/utils/problem_data.py` (added 7 lines)

**Self-review findings:**
None. The change follows existing code patterns and adds the exact validation specified in the task brief.

**Any issues or concerns:**
The Django `check` command cannot be run due to missing `celery` dependency in the environment, but this is a pre-existing issue unrelated to the change. The module imports correctly.