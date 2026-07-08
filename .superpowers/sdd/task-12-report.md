# Task 12 Report: Improve problem picker

## What I implemented

1. **Updated `ProblemSelect2View.get_name`** to return `[code] name` format
2. **Added `PublicProblemSelect2View`** - filters to public problems only
3. **Added `OrganizationProblemSelect2View`** - filters to organization problems
4. **Added new select2 URLs** for the new views
5. **Updated `ProposeContestProblemForm`** to accept `org_pk` and set the appropriate `data_url` on the problem widget

## Files changed

- `judge/views/select2.py` - Added new views and updated get_name
- `dmoj/urls.py` - Added new select2 URLs and imports
- `judge/forms.py` - Updated ProposeContestProblemForm to handle org_pk
- `judge/views/contests.py` - Updated get_contest_problem_formset to pass org_pk

## Testing

- All modified files compile successfully with `py_compile`
- Django check failed due to missing celery module (environment issue, not code issue)

## Self-review findings

No issues found. The implementation follows existing patterns in the codebase (similar to how `ContestForm` handles org_pk for private_contestants).

## Notes

The template `templates/contest/edit.html` did not require changes because the form widget automatically uses the correct `data_url` based on whether the contest has an organization.
