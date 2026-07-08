# Task 1: Disable style in markdown (c11) - Report

## What you implemented
Implemented security fix for GHSA-cpfp-xm8c-cx6m by disabling inline style tags in markdown rendering.

### Changes made:
1. Removed `'style'` from `BLEACH_USER_SAFE_TAGS` list in `dmoj/settings.py` (line 638)
2. Removed `'style'` from `BLEACH_USER_SAFE_ATTRS['*']` list in `dmoj/settings.py` (line 642)
3. Changed `'styles': True` to `'styles': False` in three markdown configurations:
   - `MARKDOWN_STAFF_EDITABLE_STYLE` (line 666)
   - `MARKDOWN_DEFAULT_STYLE` (line 686)
   - `MARKDOWN_USER_LARGE_STYLE` (line 699)

## What you tested and test results
- **Verification**: Ran `grep -n "styles.*True" dmoj/settings.py` - no matches found
- **Django check**: Ran `python manage.py check` - System check identified no issues (88 silenced)
- **Commit verification**: Verified changes via `git diff HEAD~1 -- dmoj/settings.py`

## Files changed
- `dmoj/settings.py` (5 insertions, 5 deletions)

## Self-review findings
- All three markdown configurations with bleach sections have been updated
- `MARKDOWN_ADMIN_EDITABLE_STYLE` does not have a bleach section, so no changes needed there
- No other `'styles': True` occurrences remain in the file
- Django check passes with no errors

## Issues or concerns
- None identified. The changes are minimal and targeted, addressing only the specific security vulnerability.

## Commit information
- **Commit SHA**: ac7c25b
- **Commit message**: security: disable style tags in markdown bleach config
- **Files modified**: dmoj/settings.py