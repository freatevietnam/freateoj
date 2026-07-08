# Patch VNOI-Admin/OJ Updates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply 13 commits from VNOI-Admin/OJ to the freateoj codebase while preserving Socket.IO event system and adapting `VNOJ_` settings to `FREATEOJ_` prefix.

**Architecture:** Manual patching of each commit's changes, adapting to freateoj conventions (FREATEOJ_ prefix, Django 5.2). Socket.IO files are never touched.

**Tech Stack:** Django 5.2, Python 3.14, JavaScript (Chart.js, Socket.IO), Jinja2 templates

## Global Constraints
- Socket.IO event system must be preserved (daemon.js, event_poster.py, template integration)
- All settings use `FREATEOJ_` prefix (not `VNOJ_`)
- Django 5.2 compatibility must be maintained
- Run `python manage.py check` after each phase

---

## Phase 1: Security & Cleanup

### Task 1: Disable style in markdown (c11)

**Files:**
- Modify: `dmoj/settings.py`

**Interfaces:**
- Consumes: existing BLEACH_USER_SAFE_TAGS, BLEACH_USER_SAFE_ATTRS, MARKDOWN_*_STYLE settings
- Produces: updated bleach/markdown settings with style disabled

- [ ] **Step 1: Remove 'style' from BLEACH_USER_SAFE_TAGS**

In `dmoj/settings.py`, find `BLEACH_USER_SAFE_TAGS` (line ~629) and remove `'style'` from the list:

```python
BLEACH_USER_SAFE_TAGS = [
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'b', 'i', 'strong', 'em', 'tt', 'del', 'kbd', 's', 'abbr', 'cite', 'mark', 'q', 'samp', 'small',
    'u', 'var', 'wbr', 'dfn', 'ruby', 'rb', 'rp', 'rt', 'rtc', 'sub', 'sup', 'time', 'data',
    'p', 'br', 'pre', 'span', 'div', 'blockquote', 'code', 'hr',
    'ul', 'ol', 'li', 'dd', 'dl', 'dt', 'address', 'section', 'details', 'summary',
    'table', 'thead', 'tbody', 'tfoot', 'tr', 'th', 'td', 'caption', 'colgroup', 'col', 'tfoot',
    'img', 'audio', 'video', 'source',
    'a', 'strike',
    'noscript', 'center', 'object', 'iframe',
]
```

- [ ] **Step 2: Remove 'style' from BLEACH_USER_SAFE_ATTRS['*']**

In `dmoj/settings.py`, find `BLEACH_USER_SAFE_ATTRS` (line ~641) and remove `'style'` from the `'*'` key:

```python
BLEACH_USER_SAFE_ATTRS = {
    '*': ['id', 'class', 'data', 'height'],
    # ... rest unchanged
}
```

- [ ] **Step 3: Set styles to False in MARKDOWN configs**

Find all `MARKDOWN_*_STYLE` sections and change `'styles': True` to `'styles': False`:

```python
# In MARKDOWN_STAFF_EDITABLE_STYLE (line ~658)
'styles': False,

# In MARKDOWN_ADMIN_EDITABLE_STYLE (line ~671)
'styles': False,

# In MARKDOWN_DEFAULT_STYLE (line ~678)
'styles': False,

# In MARKDOWN_USER_LARGE_STYLE (line ~691)
'styles': False,
```

- [ ] **Step 4: Verify no other 'styles': True remain**

Run: `grep -n "styles.*True" dmoj/settings.py`
Expected: No matches

- [ ] **Step 5: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK (0 errors)

- [ ] **Step 6: Commit**

```bash
cd /home/nomoka/site
git add dmoj/settings.py
git commit -m "security: disable style tags in markdown bleach config"
```

---

### Task 2: Update bleach tests (c12)

**Files:**
- Modify: `judge/jinja2/markdown/test_markdown.py`

**Interfaces:**
- Consumes: updated bleach config from Task 1
- Produces: tests that pass with style stripping

- [ ] **Step 1: Update test_bleach to expect style stripped**

In `judge/jinja2/markdown/test_markdown.py`, update the `test_bleach` method (line ~118):

```python
def test_bleach(self):
    self.assertHTMLEqual(markdown('<script>void(0)</script>', self.BLEACHED_STYLE),
                         '&lt;script&gt;void(0)&lt;/script&gt;')
    self.assertHTMLEqual(markdown('<img style="display: block; margin: 0 auto">', self.BLEACHED_STYLE),
                         '<p><img></p>')
```

- [ ] **Step 2: Add test for style tag being stripped**

Add a new test method after `test_bleach`:

```python
def test_bleach_style_tag(self):
    result = markdown('<style>body { color: red; }</style>', self.BLEACHED_STYLE)
    self.assertNotIn('<style>', result)
```

- [ ] **Step 3: Run tests**

Run: `cd /home/nomoka/site && python -m pytest judge/jinja2/markdown/test_markdown.py -v`
Expected: All tests pass

- [ ] **Step 4: Commit**

```bash
cd /home/nomoka/site
git add judge/jinja2/markdown/test_markdown.py
git commit -m "test: update bleach tests for style stripping"
```

---

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

### Task 5: Remove manifest.json (c7)

**Files:**
- Delete: `resources/icons/manifest.json`
- Modify: `templates/base.html`

**Interfaces:**
- Consumes: existing manifest.json and base.html
- Produces: manifest.json removed, base.html updated

- [ ] **Step 1: Delete manifest.json**

Run: `rm /home/nomoka/site/resources/icons/manifest.json`

- [ ] **Step 2: Remove manifest link from base.html**

In `templates/base.html`, find and remove line 27:
```html
<!-- DELETE THIS LINE: -->
<link rel="manifest" href="{{ static('icons/manifest.json') }}">
```

- [ ] **Step 3: Verify deletion**

Run: `ls /home/nomoka/site/resources/icons/manifest.json`
Expected: No such file

- [ ] **Step 4: Commit**

```bash
cd /home/nomoka/site
git rm resources/icons/manifest.json
git add templates/base.html
git commit -m "chore: remove unused manifest.json"
```

---

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

### Task 8: Fix dark mode chart colors (c3)

**Files:**
- Modify: `templates/stats/media-js.html`

**Interfaces:**
- Consumes: existing chart rendering code
- Produces: theme-aware chart legend colors

- [ ] **Step 1: Add chartFontColor helper function**

In `templates/stats/media-js.html`, add at the top of the script (after the `<script>` tag):

```javascript
function chartFontColor() {
    return document.body.classList.contains('dark') ? '#eee' : '#666';
}
```

- [ ] **Step 2: Update pie chart fontColor**

In `draw_pie_chart` function, change:
```javascript
// BEFORE:
fontColor: 'black',

// AFTER:
fontColor: chartFontColor(),
```

- [ ] **Step 3: Update bar chart legend fontColor**

In `draw_bar_chart` function, add `fontColor: chartFontColor()` to the legend labels configuration.

- [ ] **Step 4: Update stacked bar chart legend fontColor**

In `draw_stacked_bar_chart` function, add `fontColor: chartFontColor()` to the legend labels configuration.

- [ ] **Step 5: Update vertical stacked bar chart legend fontColor**

In `draw_vertical_stacked_bar_chart` function, add `fontColor: chartFontColor()` to the legend labels configuration.

- [ ] **Step 6: Update line chart legend fontColor**

In `draw_line_chart` function, add `fontColor: chartFontColor()` to the legend labels configuration.

- [ ] **Step 7: Verify changes**

Run: `grep -n "chartFontColor" /home/nomoka/site/templates/stats/media-js.html`
Expected: Multiple matches (pie, bar, stacked, vertical stacked, line charts)

- [ ] **Step 8: Commit**

```bash
cd /home/nomoka/site
git add templates/stats/media-js.html
git commit -m "fix: make chart legend text color theme-aware for dark mode"
```

---

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

### Task 10: Hide submission links in ranking (c10)

**Files:**
- Modify: `judge/views/contests.py`
- Modify: `templates/contest/ranking.html`
- Modify: `static/contest-ranking.js` (or wherever the JS is)

**Interfaces:**
- Consumes: existing ranking view and template
- Produces: submission links hidden when user can't see submissions

- [ ] **Step 1: Add can_see_full_submission_list to ranking context**

In `judge/views/contests.py`, find the ranking view and add to context:

```python
context['can_see_full_submission_list'] = contest.can_see_full_submission_list(request.user)
```

- [ ] **Step 2: Add JS variable in ranking.html**

In `templates/contest/ranking.html`, add before the script section:

```html
<script>
    window.CONTEST_CAN_SEE_SUBMISSIONS = {{ can_see_full_submission_list|tojson }};
</script>
```

- [ ] **Step 3: Update contest-ranking.js**

In the contest ranking JavaScript file, update the URL template handling:

```javascript
// In makeSubmissionUrl and makeAllSubmissionsUrl:
// Return null when url_templates is missing or CONTEST_CAN_SEE_SUBMISSIONS is false

// In wrapProblemCell:
// Render plain <td> when URL is null (no <a> link)

// In standardResultCell:
// Wrap score in <a> only when URL is available
```

- [ ] **Step 4: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 5: Commit**

```bash
cd /home/nomoka/site
git add judge/views/contests.py templates/contest/ranking.html static/contest-ranking.js
git commit -m "fix: hide submission links in ranking when user can't see submissions"
```

---

## Phase 3: Features

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

### Task 12: Improve problem picker (c5)

**Files:**
- Modify: `judge/views/select2.py`
- Modify: `dmoj/urls.py`
- Modify: `judge/views/contest.py` (contest edit view)
- Modify: `templates/contest/edit.html`

**Interfaces:**
- Consumes: existing ProblemSelect2View
- Produces: improved problem picker with code display and org split

- [ ] **Step 1: Update ProblemSelect2View.get_name**

In `judge/views/select2.py`, update `ProblemSelect2View.get_name` to return `[code] name` format:

```python
def get_name(self, obj):
    return f'[{obj.code}] {obj.name}'
```

- [ ] **Step 2: Add PublicProblemSelect2View**

In `judge/views/select2.py`, add:

```python
class PublicProblemSelect2View(ProblemSelect2View):
    def get_queryset(self):
        return super().get_queryset().filter(is_public=True)
```

- [ ] **Step 3: Add OrganizationProblemSelect2View**

In `judge/views/select2.py`, add:

```python
class OrganizationProblemSelect2View(ProblemSelect2View):
    def get_queryset(self):
        org_pk = self.kwargs.get('org_pk')
        return super().get_queryset().filter(organizations__pk=org_pk)
```

- [ ] **Step 4: Add new select2 URLs**

In `dmoj/urls.py`, add:

```python
path('/select2/problem/public/', select2.PublicProblemSelect2View.as_view(), name='problem_select2_public'),
path('/select2/problem/org/<int:org_pk>/', select2.OrganizationProblemSelect2View.as_view(), name='problem_select2_org'),
```

- [ ] **Step 5: Update contest edit template**

In `templates/contest/edit.html`, update problem picker to use the new split pickers.

- [ ] **Step 6: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 7: Commit**

```bash
cd /home/nomoka/site
git add judge/views/select2.py dmoj/urls.py templates/contest/edit.html
git commit -m "feat: improve problem picker with code display and org split"
```

---

### Task 13: Infinite pagination for contrib list (c9)

**Files:**
- Modify: `judge/views/user.py`

**Interfaces:**
- Consumes: existing ContribList class
- Produces: ContribList with infinite scroll pagination

- [ ] **Step 1: Add InfinitePaginationMixin to ContribList**

In `judge/views/user.py`, find `ContribList` class (line ~615) and add `InfinitePaginationMixin` to its base classes:

```python
class ContribList(QueryStringSortMixin, DiggPaginatorMixin, InfinitePaginationMixin, TitleMixin, ListView):
```

- [ ] **Step 2: Verify InfinitePaginationMixin import**

Run: `grep -n "InfinitePaginationMixin" /home/nomoka/site/judge/views/user.py`
Expected: Import exists or is added

- [ ] **Step 3: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 4: Commit**

```bash
cd /home/nomoka/site
git add judge/views/user.py
git commit -m "feat: use infinite pagination for contributors list"
```

---

## Verification

### Final Verification

- [ ] **Step 1: Run full test suite**

Run: `cd /home/nomoka/site && python -m pytest`
Expected: All tests pass

- [ ] **Step 2: Run Django check**

Run: `cd /home/nomoka/site && python manage.py check`
Expected: OK

- [ ] **Step 3: Verify Socket.IO preserved**

Run: `grep -r "socket.io" /home/nomoka/site/templates/base.html`
Expected: Socket.IO script tag still present

- [ ] **Step 4: Verify no VNOJ_ references**

Run: `grep -r "VNOJ_" /home/nomoka/site/dmoj/`
Expected: No matches (all should be FREATEOJ_)

- [ ] **Step 5: Verify api_v2 removed**

Run: `ls /home/nomoka/site/judge/views/api/api_v2.py`
Expected: File should not exist (or be empty)

- [ ] **Step 6: Verify suggester removed**

Run: `grep -n "suggester" /home/nomoka/site/judge/models/problem.py`
Expected: No matches
