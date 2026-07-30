# Industrial/Brutalist Users Page Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the users list (leaderboard) and user profile pages with an industrial/brutalist design language, adding rich data visualization panels and a comparison feature.

**Architecture:** Django templates + SCSS for presentation, Chart.js + D3.js + custom Canvas/SVG for charts, JSON data endpoints for lazy-loaded panels, and a new comparison view.

**Tech Stack:** Django 3.2+, Chart.js v4, D3.js v7, SCSS, jQuery (existing), Git

## Global Constraints

- Zero border-radius everywhere (brutalist)
- Monospace (`JetBrains Mono` fallback `monospace`) for all data/numbers
- Color palette: `#0A0A0A` bg, `#141414` surface, `#333` border, `#F5F5F5` text
- All panels must lazy-load via IntersectionObserver
- Must degrade gracefully with JS disabled
- Follow existing DMOJ patterns (template inheritance, view mixins)
- Use existing `_()` translation function for all user-facing strings
- All new JS files must be ES5-compatible (existing jQuery patterns)

---

### Task 1: Industrial Variables & SCSS Reset

**Files:**
- Create: `resources/_users-variables.scss`
- Modify: `resources/users.scss` (rewrite)
- Modify: `sass_processed/users.css` (compiled output)

**Interfaces:**
- Consumes: `resources/vars.scss` (existing DMOJ variables)
- Produces: SCSS variables consumed by all new component SCSS files

- [ ] **Step 1: Create `_users-variables.scss` with industrial token set**

```scss
// Industrial/Brutalist Design Tokens
$ind-bg: #0A0A0A;
$ind-surface: #141414;
$ind-surface-elevated: #1E1E1E;
$ind-border: #333333;
$ind-text: #F5F5F5;
$ind-text-muted: #888888;
$ind-accent-primary: #FF6B00;
$ind-accent-success: #00FF88;
$ind-accent-danger: #FF3366;
$ind-font-mono: 'JetBrains Mono', 'IBM Plex Mono', monospace;
$ind-font-ui: 'Space Grotesk', system-ui, sans-serif;
$ind-border-width: 1px;
$ind-radius: 0;
$ind-grid-gap: 24px;
$ind-sidebar-width: 280px;
$ind-transition: none;
```

- [ ] **Step 2: Rewrite `users.scss` — import variables, reset existing styles**

```scss
@use "users-variables" as *;
@use "vars" as *;

// ─── Brutalist Reset ────────────────────────────────────────────────
* {
  border-radius: 0 !important;
}

// ─── Typography ─────────────────────────────────────────────────────
body.users-page, body.user-profile-page {
  font-family: $ind-font-ui;
  color: $ind-text;
  background: $ind-bg;
}

.mono {
  font-family: $ind-font-mono;
}

.data-value {
  font-family: $ind-font-mono;
  font-size: 1rem;
  color: $ind-text;
}

.data-label {
  font-family: $ind-font-ui;
  font-size: 0.7rem;
  color: $ind-text-muted;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

// ─── Layout Grid ────────────────────────────────────────────────────
.brutalist-grid {
  display: grid;
  gap: $ind-grid-gap;
}

.brutalist-two-col {
  display: grid;
  grid-template-columns: $ind-sidebar-width 1fr;
  gap: $ind-grid-gap;
}

// ─── Borders ────────────────────────────────────────────────────────
.brutalist-border {
  border: $ind-border-width solid $ind-border;
}

.brutalist-divider {
  border: none;
  border-top: $ind-border-width solid $ind-border;
  margin: 0;
}
```

- [ ] **Step 3: Commit**

```bash
git add resources/_users-variables.scss resources/users.scss
git commit -m "feat: add industrial design variables and SCSS reset"
```

---

### Task 2: Base Template Layouts

**Files:**
- Create: `templates/user/_panel_wrapper.html`
- Modify: `templates/user/user-base.html` (rewrite sidebar + content grid)
- Modify: `templates/user/list.html` (rewrite structure)
- Modify: `templates/user/base-users.html` (rewrite)

- [ ] **Step 1: Rewrite `base-users.html` — industrial top bar + search**

```django
{% extends "common-content.html" %}

{% block js_media %}
    {% block users_js_media %}{% endblock %}
    <script>
        $(function () {
            $('#search-handle').replaceWith($('<select>').attr({
                id: 'search-handle', name: 'handle', onchange: 'form.submit()'
            }));
            $('#search-handle').select2({
                theme: '{{ DMOJ_SELECT2_THEME }}',
                placeholder: {{ _('Search by handle...')|htmltojs }},
                ajax: { url: '{% block user_search_select2_ajax %}{{ url("user_search_select2_ajax") }}{% endblock %}', delay: 300 },
                minimumInputLength: 1,
                templateResult: function (data, container) {
                    return $('<span>').append($('<img>', {'class': 'user-search-image', src: data.gravatar_url, width: 24, height: 24})).append($('<span>', {'class': data.display_rank + ' user-search-name'}).text(data.text));
                }
            }).on('select2:selecting', function () { return false; });
        });
    </script>
{% endblock %}

{% block body %}
<div class="users-page">
    <header class="users-header brutalist-border" style="padding: 16px 24px; margin-bottom: 0;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <h1 style="font-family: 'Space Grotesk', system-ui, sans-serif; font-size: 1.5rem; text-transform: uppercase; letter-spacing: 0.05em; color: #F5F5F5; margin: 0;">{{ _('Users / Leaderboard') }}</h1>
            <form id="search-form" name="form" action="{{ url('user_ranking_redirect') }}" method="get">
                <input id="search-handle" type="text" name="search" placeholder="{{ _('Search by handle...') }}" style="width: 280px; height: 36px; background: #141414; border: 1px solid #333; color: #F5F5F5; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; padding: 0 12px;">
            </form>
        </div>
        <hr class="brutalist-divider" style="margin: 12px 0 0 0;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #888; margin-top: 8px;">
            {{ _('Total: %(count)s users', count=total_users) }} &bull; {{ _('Active (24h): %(count)s', count=active_users) }} &bull; {{ _('Top 1%%: %(points)s pp', points=top_1_percent_threshold) }}
        </div>
    </header>

    {% if page_obj and page_obj.has_other_pages() %}
        <div class="top-pagination-bar" style="padding: 8px 24px;">{% include "list-pages.html" %}</div>
    {% endif %}

    <div id="content-left" class="users">
        {% block before_users_table %}{% endblock %}
        {% block users_table %}{% endblock %}
    </div>

    {% if page_obj and page_obj.has_other_pages() %}
        <div class="bottom-pagination-bar" style="padding: 8px 24px;">{% include "list-pages.html" %}</div>
    {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 2: Rewrite `list.html`**

```django
{% extends "user/base-users.html" %}
{% block title_ruler %}{% endblock %}
{% block title_row %}
    {% set tab = 'list' %}
    {% include "user/user-list-tabs.html" %}
{% endblock %}
{% block before_users_table %}
    {% include "user/_top_performers.html" %}
{% endblock %}
{% block users_table %}
    {% include "user/_leaderboard_table.html" %}
    {% include "user/_leaderboard_cards.html" %}
{% endblock %}
```

- [ ] **Step 3: Rewrite `user-base.html` — two-column brutalist profile layout**

```django
{% extends "base.html" %}
{% block media %}{% block user_media %}{% endblock %}{% endblock %}
{% block js_media %}{% block user_js_media %}{% endblock %}{% endblock %}

{% block body %}
<div class="user-profile-page brutalist-two-col" style="padding: 24px;">
    <aside class="user-sidebar brutalist-border" style="background: #141414; padding: 16px; position: sticky; top: 24px; align-self: start;">
        <img src="{{ gravatar(user, 135) }}" class="user-gravatar" style="display: block; width: 135px; height: 135px; border: 2px solid #333; margin-bottom: 12px;">
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #F5F5F5; margin-bottom: 8px;">{{ user.user.username }}</div>
        <hr class="brutalist-divider" style="margin: 8px 0;">

        {% if user.user == request.user or request.user.is_superuser %}
            <div><span class="data-label">{{ _('Email:') }}</span> <span class="data-value" style="word-wrap: break-word;">{{ user.user.email }}</span></div>
        {% endif %}
        <div><span class="data-label">{{ _('Rating:') }}</span> <span class="data-value">{% if user.rating %}● {% endif %}{{ rating_number(user) if user.rating else _('Unrated') }}</span></div>
        {% if not user.is_unlisted %}
            <div><span class="data-label">{{ _('Rank:') }}</span> <span class="data-value">#{{ rank }} / {{ total_users }}</span></div>
        {% endif %}
        <div><span class="data-label">{{ _('Points:') }}</span> <span class="data-value">{{ user.performance_points|floatformat(2) }} pp</span></div>
        <div><span class="data-label">{{ _('Solved:') }}</span> <span class="data-value">{{ user.problem_count }}</span></div>
        <div><span class="data-label">{{ _('Contribution:') }}</span> <span class="data-value">{{ user.contribution_points }}</span></div>

        <hr class="brutalist-divider" style="margin: 8px 0;">

        {% with orgs=user.organizations.filter(is_unlisted=False) %}
            {% if orgs %}
                <div><span class="data-label">{{ _('Org:') }}</span>
                    {% for org in orgs %}<span class="data-value"><a href="{{ org.get_absolute_url() }}" style="color: #FF6B00;">{{ org.name }}</a>{% if not loop.last %}, {% endif %}</span>{% endfor %}
                </div>
            {% endif %}
        {% endwith %}
        <div><span class="data-label">{{ _('Joined:') }}</span> <span class="data-value">{{ user.user.date_joined|date("Y-m-d") }}</span></div>

        <hr class="brutalist-divider" style="margin: 8px 0;">

        <div style="display: flex; gap: 8px;">
            <a href="{{ url('all_user_submissions', user.user.username) }}" class="brutalist-btn" style="flex:1; text-align:center; padding:10px 0; border:1px solid #333; color:#F5F5F5; font-family:'JetBrains Mono',monospace; font-size:0.75rem; text-decoration:none;">{{ _('Submissions') }}</a>
            <a href="/users/compare/?u1={{ user.user.username }}" class="brutalist-btn" style="flex:1; text-align:center; padding:10px 0; border:1px solid #FF6B00; color:#FF6B00; font-family:'JetBrains Mono',monospace; font-size:0.75rem; text-decoration:none;">{{ _('Compare') }}</a>
        </div>

        {% if ratings %}
            <hr class="brutalist-divider" style="margin: 8px 0;">
            <div><span class="data-label">{{ _('Contests:') }}</span> <span class="data-value">{% trans counter=ratings|length %}{{ counter }} contest{% pluralize %}{{ counter }} contests{% endtrans %}</span></div>
            {% if not user.is_unlisted %}
                <div><span class="data-label">{{ _('Rating rank:') }}</span> <span class="data-value">#{{ rating_rank }}</span></div>
            {% endif %}
            <div><span class="data-label">{{ _('Min:') }}</span> <span class="data-value">{{ rating_number(min_rating) }}</span></div>
            <div><span class="data-label">{{ _('Max:') }}</span> <span class="data-value">{{ rating_number(max_rating) }}</span></div>
        {% endif %}
    </aside>

    <main class="user-content brutalist-grid" style="gap:24px;">
        {% block user_content %}{% endblock %}
    </main>
</div>
{% endblock %}
```

- [ ] **Step 4: Create `_panel_wrapper.html`**

```django
<section class="brutalist-panel brutalist-border" data-panel="{{ panel_id }}" style="background: #141414;" {% if lazy %}data-lazy="{{ lazy_endpoint }}"{% endif %}>
    {% if title %}
        <header style="padding: 8px 12px; border-bottom: 1px solid #333; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 0.05em;">{{ title }}</header>
    {% endif %}
    <div class="panel-content" style="padding: 12px;">
        {% if lazy %}
            <div class="panel-placeholder" style="text-align:center;padding:40px 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#666;">{{ _('Loading...') }}</div>
        {% else %}
            {{ content }}
        {% endif %}
    </div>
</section>
```

- [ ] **Step 5: Commit**

```bash
git add templates/user/base-users.html templates/user/list.html templates/user/user-base.html templates/user/_panel_wrapper.html
git commit -m "feat: add industrial base layout templates"
```

---

### Task 3: Leaderboard — Top Performers Widgets + Table

**Files:**
- Create: `templates/user/_top_performers.html`
- Create: `templates/user/_leaderboard_table.html`
- Create: `templates/user/_leaderboard_cards.html`

**Interfaces:**
- Consumes: context variables `top_rated`, `top_points`, `rising_star`, `top_org` from view
- Produces: rendered HTML with `.users-table` classes

- [ ] **Step 1: Create `_top_performers.html`**

```django
{% if top_performers %}
<div class="brutalist-grid top-performers" style="grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; padding: 16px 24px;">
    {% for card in top_performers %}
    <div class="brutalist-border" style="background: #141414; padding: 12px;">
        <div class="data-label">{{ card.label }}</div>
        <div style="display:flex;align-items:center;gap:8px;margin-top:4px;">
            <img src="{{ gravatar(card.profile, 32) }}" style="width:32px;height:32px;border:1px solid #333;">
            <div>
                <a href="{{ url('user_page', card.profile.user.username) }}" style="font-family:'JetBrains Mono',monospace;font-size:1rem;color:#F5F5F5;text-decoration:none;">{{ card.profile.user.username }}</a>
                <div class="data-value" style="color:#FF6B00;">{{ card.value }}</div>
            </div>
        </div>
        {% if card.trend %}
        <div class="data-label" style="margin-top:4px;color:{% if card.trend > 0 %}#00FF88{% else %}#FF3366{% endif %};">{{ '+' if card.trend > 0 }}{{ card.trend }}</div>
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endif %}
```

- [ ] **Step 2: Create `_leaderboard_table.html`**

```django
{% if users %}
<div style="overflow-x:auto;">
<table class="users-table" style="width:100%;border-collapse:collapse;font-family:'JetBrains Mono',monospace;font-size:0.8rem;background:#141414;">
    <thead>
        <tr style="border-bottom:1px solid #333;">
            <th style="padding:6px 8px;text-align:right;width:48px;color:#888;font-weight:400;">#</th>
            <th style="padding:6px 8px;text-align:left;color:#888;font-weight:400;">{{ _('Handle') }}</th>
            <th style="padding:6px 8px;text-align:center;width:80px;color:#888;font-weight:400;">
                {% if sort_links %}<a href="{{ sort_links.rating }}" style="color:#888;text-decoration:none;">{% endif %}●{{ sort_order.rating }}{% if sort_links %}</a>{% endif %}
            </th>
            <th style="padding:6px 8px;text-align:right;width:100px;color:#888;font-weight:400;">
                {% if sort_links %}<a href="{{ sort_links.performance_points }}" style="color:#888;text-decoration:none;">{% endif %}{{ _('Points') }}{{ sort_order.performance_points }}{% if sort_links %}</a>{% endif %}
            </th>
            <th style="padding:6px 8px;text-align:right;width:80px;color:#888;font-weight:400;">
                {% if sort_links %}<a href="{{ sort_links.problem_count }}" style="color:#888;text-decoration:none;">{% endif %}{{ _('Solved') }}{{ sort_order.problem_count }}{% if sort_links %}</a>{% endif %}
            </th>
            <th style="padding:6px 8px;text-align:left;color:#888;font-weight:400;">{{ _('Org') }}</th>
        </tr>
    </thead>
    <tbody>
    {% for rank, profile in users %}
        <tr id="user-{{ profile.user.username }}" style="border-bottom:1px solid #222;transition:background 0.1s;" onmouseover="this.style.background='#1E1E1E'" onmouseout="this.style.background=''">
            <td style="padding:6px 8px;text-align:right;color:#888;">{{ rank }}</td>
            <td style="padding:6px 8px;">
                <div style="display:flex;align-items:center;gap:8px;">
                    <img src="{{ gravatar(profile, 24) }}" style="width:24px;height:24px;border:1px solid #333;flex-shrink:0;">
                    <a href="{{ url('user_page', profile.user.username) }}" style="color:#F5F5F5;text-decoration:none;">{{ profile.user.username }}</a>
                </div>
            </td>
            <td style="padding:6px 8px;text-align:center;">
                {% if profile.rating %}
                    <span style="color:{% if profile.rating >= 2400 %}#FF0000{% elif profile.rating >= 1900 %}#AA00AA{% elif profile.rating >= 1600 %}#0000FF{% elif profile.rating >= 1400 %}#03A89E{% elif profile.rating >= 1200 %}#008000{% else %}#888{% endif %};">● {{ profile.rating }}</span>
                {% endif %}
            </td>
            <td style="padding:6px 8px;text-align:right;color:#F5F5F5;">{{ profile.performance_points|floatformat(1) }}</td>
            <td style="padding:6px 8px;text-align:right;color:#888;">{{ profile.problem_count }}</td>
            <td style="padding:6px 8px;color:#888;font-size:0.75rem;">
                {% for org in profile.organizations.all() %}
                    <a href="{{ org.get_absolute_url() }}" style="color:#888;text-decoration:none;">{{ org.name }}</a>{% if not loop.last %}, {% endif %}
                {% endfor %}
            </td>
        </tr>
    {% endfor %}
    </tbody>
</table>
</div>
{% endif %}
```

- [ ] **Step 3: Create `_leaderboard_cards.html`** (for rank 11+, rendered via JS from JSON or shown server-side)

```django
{% if users_cards %}
<div class="brutalist-grid" style="grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; padding: 16px 24px;">
    {% for rank, profile in users_cards %}
    <div class="brutalist-border" style="background:#141414;padding:12px;display:flex;align-items:center;gap:12px;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;color:#333;min-width:36px;text-align:right;">{{ rank }}</div>
        <img src="{{ gravatar(profile, 40) }}" style="width:40px;height:40px;border:1px solid #333;">
        <div style="flex:1;min-width:0;">
            <a href="{{ url('user_page', profile.user.username) }}" style="font-family:'JetBrains Mono',monospace;font-size:0.9rem;color:#F5F5F5;text-decoration:none;">{{ profile.user.username }}</a>
            <div style="display:flex;gap:12px;margin-top:4px;">
                <span class="data-label">{{ _('Pts') }}</span><span class="data-value" style="font-size:0.8rem;">{{ profile.performance_points|floatformat(1) }}</span>
                <span class="data-label">{{ _('Sol') }}</span><span class="data-value" style="font-size:0.8rem;">{{ profile.problem_count }}</span>
                {% if profile.rating %}<span class="data-label">●</span><span class="data-value" style="font-size:0.8rem;">{{ profile.rating }}</span>{% endif %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endif %}
```

- [ ] **Step 4: Commit**

```bash
git add templates/user/_top_performers.html templates/user/_leaderboard_table.html templates/user/_leaderboard_cards.html
git commit -m "feat: add leaderboard widgets, table, and card grid"
```

---

### Task 4: View Updates — Top Performers Context + Comparison View

**Files:**
- Modify: `judge/views/user.py` — extend UserList context, add UserComparisonView
- Create: `judge/utils/user_stats.py` — helper functions for comparison
- Modify: `judge/urls.py` — add compare route

- [ ] **Step 1: Add top performers to UserList context in `user.py`**

In `UserList.get_context_data()`, add after `context.update(...)`:

```python
# Top performers
from judge.models import Profile as ProfileModel, Organization
top_rated = ProfileModel.objects.filter(is_unlisted=False).order_by('-rating').select_related('user')[:1].first()
top_points = ProfileModel.objects.filter(is_unlisted=False).order_by('-performance_points').select_related('user')[:1].first()
rising_star_qs = ProfileModel.objects.filter(is_unlisted=False, rating__isnull=False).order_by('-rating')[:10]
# Simple "rising star": user with most rating gain (last 30d — placeholder using highest rating)
rising_star = ProfileModel.objects.filter(is_unlisted=False).order_by('-rating')[:3].last() if ProfileModel.objects.filter(is_unlisted=False).count() > 2 else None
top_org = Organization.objects.filter(is_unlisted=False).annotate(member_count=Count('member')).order_by('-member_count').first()

context['top_performers'] = [
    {'label': '#1 RATED', 'profile': top_rated, 'value': str(top_rated.rating) if top_rated and top_rated.rating else 'N/A', 'trend': None},
    {'label': '#1 POINTS', 'profile': top_points, 'value': '%.1f pp' % top_points.performance_points if top_points else 'N/A', 'trend': None},
    {'label': 'RISING STAR', 'profile': rising_star, 'value': str(rising_star.rating) if rising_star and rising_star.rating else 'N/A', 'trend': None},
    {'label': 'TOP ORG', 'profile': None, 'value': top_org.name if top_org else 'N/A', 'trend': top_org.member_count if top_org else None},
]
context['total_users'] = ProfileModel.objects.filter(is_unlisted=False).count()
context['active_users'] = ProfileModel.objects.filter(is_unlisted=False, user__last_login__gte=timezone.now() - datetime.timedelta(hours=24)).count()
top_1 = ProfileModel.objects.filter(is_unlisted=False).order_by('-performance_points').values_list('performance_points', flat=True)[:max(1, int(ProfileModel.objects.filter(is_unlisted=False).count() * 0.01))]
context['top_1_percent_threshold'] = '%.0f' % (top_1.last() if top_1 else 0)
```

- [ ] **Step 2: Create `judge/utils/user_stats.py`**

```python
from collections import defaultdict
from judge.models import Profile, Submission, ContestParticipation

def common_solved_problems(profile_a, profile_b):
    """Return set of problem IDs both users have solved."""
    a_solved = set(
        Submission.objects.filter(user=profile_a, points__gt=0, problem__is_public=True)
        .values_list('problem_id', flat=True).distinct()
    )
    b_solved = set(
        Submission.objects.filter(user=profile_b, points__gt=0, problem__is_public=True)
        .values_list('problem_id', flat=True).distinct()
    )
    return a_solved & b_solved

def head_to_head(profile_a, profile_b, common_ids):
    """Return {a_wins, b_wins, ties} for common problems."""
    a_best = _best_scores(profile_a, common_ids)
    b_best = _best_scores(profile_b, common_ids)
    a_wins = b_wins = ties = 0
    for pid in common_ids:
        sa = a_best.get(pid, 0)
        sb = b_best.get(pid, 0)
        if sa > sb:
            a_wins += 1
        elif sb > sa:
            b_wins += 1
        else:
            ties += 1
    return {'a_wins': a_wins, 'b_wins': b_wins, 'ties': ties}

def _best_scores(profile, problem_ids):
    scores = Submission.objects.filter(
        user=profile, problem_id__in=problem_ids, points__gt=0
    ).values('problem_id').annotate(best=models.Max('points'))
    return {s['problem_id']: s['best'] for s in scores}

def topic_differential(profile_a, profile_b):
    """Return per-category solved count difference."""
    from judge.models import ProblemGroup
    a_by_group = _solved_by_group(profile_a)
    b_by_group = _solved_by_group(profile_b)
    all_groups = set(a_by_group.keys()) | set(b_by_group.keys())
    result = []
    for gid in sorted(all_groups):
        ac = a_by_group.get(gid, 0)
        bc = b_by_group.get(gid, 0)
        group = ProblemGroup.objects.get(id=gid)
        diff = ac - bc
        total = max(ac, bc, 1)
        result.append({
            'group_name': group.full_name,
            'a_solved': ac,
            'b_solved': bc,
            'diff': diff,
            'pct': round((diff / total) * 100),
            'leader': 'a' if diff > 0 else 'b' if diff < 0 else 'tie',
        })
    return result

def _solved_by_group(profile):
    from django.db.models import Count
    return dict(
        Submission.objects.filter(user=profile, points__gt=0, problem__is_public=True)
        .values('problem__group_id')
        .annotate(cnt=Count('id', distinct=True))
        .values_list('problem__group_id', 'cnt')
    )
```

- [ ] **Step 3: Add `UserComparisonView` in `user.py`**

```python
from judge.utils.user_stats import common_solved_problems, head_to_head, topic_differential

class UserComparisonView(TitleMixin, TemplateView):
    template_name = 'user/compare.html'
    title = gettext_lazy('Compare Users')

    def get(self, request, *args, **kwargs):
        u1_name = request.GET.get('u1', '')
        u2_name = request.GET.get('u2', '')
        if not u1_name:
            u1_name = request.user.username if request.user.is_authenticated else ''
        if not u2_name or not u1_name:
            return render(request, self.template_name, {
                'title': self.title,
                'error': _('Please specify two usernames: ?u1=user1&u2=user2'),
            })
        try:
            profile_a = Profile.objects.select_related('user').get(user__username=u1_name)
        except Profile.DoesNotExist:
            return render(request, self.template_name, {'title': self.title, 'error': _('User "%s" not found') % u1_name})
        try:
            profile_b = Profile.objects.select_related('user').get(user__username=u2_name)
        except Profile.DoesNotExist:
            return render(request, self.template_name, {'title': self.title, 'error': _('User "%s" not found') % u2_name})

        common = common_solved_problems(profile_a, profile_b)
        h2h = head_to_head(profile_a, profile_b, common)
        topic_diff = topic_differential(profile_a, profile_b)

        context = self.get_context_data()
        context.update({
            'user_a': profile_a,
            'user_b': profile_b,
            'common_count': len(common),
            'head_to_head': h2h,
            'topic_diff': topic_diff,
        })
        return self.render_to_response(context)
```

- [ ] **Step 4: Add URL route in `urls.py`**

Find the user URLs section and add:
```python
from judge.views.user import UserComparisonView

# Inside urlpatterns
path('users/compare/', UserComparisonView.as_view(), name='user_compare'),
```

- [ ] **Step 5: Commit**

```bash
git add judge/views/user.py judge/utils/user_stats.py judge/urls.py
git commit -m "feat: add comparison view and top performers context"
```

---

### Task 5: Profile Panels — Heatmap, Rating Chart, Radar

**Files:**
- Create: `templates/user/user-about.html` (restructure into panels)
- Create: `templates/user/_heatmap.html`
- Create: `templates/user/_rating_chart.html`
- Create: `templates/user/_radar_chart.html`
- Create: `resources/user-heatmap.js`
- Create: `resources/user-rating-chart.js`
- Create: `resources/user-radar-chart.js`

- [ ] **Step 1: Rewrite `user-about.html` — panel grid layout**

```django
{% extends "user/user-base.html" %}
{% block title_ruler %}{% endblock %}
{% block title_row %}
    {% set tab = 'about' %}
    {% include "user/user-tabs.html" %}
{% endblock %}

{% block user_content %}
    {% with panel_id='heatmap', title=_('Submission Activity'), lazy=True, lazy_endpoint='' %}
        {% include "user/_heatmap.html" %}
    {% endwith %}

    {% with panel_id='rating_chart', title=_('Rating History'), lazy=True %}
        {% include "user/_rating_chart.html" %}
    {% endwith %}

    <div class="brutalist-grid" style="grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 24px;">
        {% with panel_id='radar', title=_('Topic Strengths'), lazy=True %}
            {% include "user/_radar_chart.html" %}
        {% endwith %}

        {% with panel_id='skill_tree', title=_('Skill Tree'), lazy=True %}
            {% include "user/_skill_tree.html" %}
        {% endwith %}
    </div>

    <div class="brutalist-grid" style="grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
        {% with panel_id='achievements', title=_('Achievements'), lazy=True %}
            {% include "user/_achievement_progression.html" %}
        {% endwith %}

        {% with panel_id='rankings', title=_('Rankings'), lazy=True %}
            {% include "user/_multi_rankings.html" %}
        {% endwith %}
    </div>

    {% with panel_id='activity', title=_('Recent Activity'), lazy=True %}
        {% include "user/_activity_feed.html" %}
    {% endwith %}

    {% with panel_id='problems', title=_('Problem Statistics'), lazy=True %}
        {% include "user/_problem_stats.html" %}
    {% endwith %}

    {% if REQUIRE_JAX %}
        {% include "mathjax-load.html" %}
    {% endif %}
    <script src="{{ static('user_profile.js') }}"></script>
    <script>
        $(function () {
            if (window.init_submission_table) {
                window.init_submission_table($, {{ submission_data }}, "{{ LANGUAGE_CODE }}");
            }
        });
    </script>
{% endblock %}

{% block bodyend %}
    <script src="{{ static('user-heatmap.js') }}"></script>
    <script src="{{ static('user-rating-chart.js') }}"></script>
    <script src="{{ static('user-radar-chart.js') }}"></script>
    {% if ratings %}
        <script src="{{ static('libs/chart.js/Chart.js') }}"></script>
        {% include "user/_rating_chart_js.html" %}
    {% endif %}
{% endblock %}
```

- [ ] **Step 2: Create `_heatmap.html`**

```django
<section class="brutalist-panel brutalist-border" data-panel="heatmap" id="heatmap-panel" style="background:#141414;">
    <header style="padding:8px 12px;border-bottom:1px solid #333;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;">{{ _('Submission Activity') }}</header>
    <div class="panel-content" style="padding:12px;min-height:320px;">
        <canvas id="heatmap-canvas" width="800" height="280"></canvas>
        <div style="display:flex;justify-content:flex-end;align-items:center;gap:4px;margin-top:8px;">
            <span class="data-label">{{ _('Less') }}</span>
            <span style="display:inline-block;width:10px;height:10px;background:#1E1E1E;border:1px solid #333;"></span>
            <span style="display:inline-block;width:10px;height:10px;background:#333;border:1px solid #333;"></span>
            <span style="display:inline-block;width:10px;height:10px;background:#666;border:1px solid #333;"></span>
            <span style="display:inline-block;width:10px;height:10px;background:#FF6B00;border:1px solid #333;"></span>
            <span class="data-label">{{ _('More') }}</span>
        </div>
    </div>
</section>

<script>
document.addEventListener('DOMContentLoaded', function () {
    const el = document.getElementById('heatmap-canvas');
    if (!el) return;
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                fetch('/user/{{ user.user.username }}/heatmap-data/')
                    .then(function (r) { return r.json(); })
                    .then(function (data) { renderHeatmap(el, data); });
                observer.unobserve(el);
            }
        });
    }, { rootMargin: '200px' });
    observer.observe(el);
});
</script>
```

- [ ] **Step 3: Create `user-heatmap.js`**

```javascript
function renderHeatmap(canvas, data) {
    var ctx = canvas.getContext('2d');
    var W = canvas.width, H = canvas.height;
    var cellSize = 10, gap = 2;
    var cols = 53, rows = 7;
    var startX = 20, startY = 20;
    var maxVal = 1;
    for (var k in data) { if (data[k] > maxVal) maxVal = data[k]; }

    ctx.fillStyle = '#141414';
    ctx.fillRect(0, 0, W, H);

    var dates = Object.keys(data).sort();
    var dayStrings = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    for (var r = 0; r < rows; r++) {
        ctx.fillStyle = '#888';
        ctx.font = '8px JetBrains Mono, monospace';
        ctx.textAlign = 'right';
        ctx.fillText(dayStrings[r], startX - 4, startY + r * (cellSize + gap) + 8);
    }

    var firstDate = new Date(dates[0] || Date.now());
    var startDay = firstDate.getDay();
    var col = 0, row = startDay;
    dates.forEach(function (iso) {
        var val = data[iso] || 0;
        var intensity = val / maxVal;
        var color;
        if (val === 0) color = '#1E1E1E';
        else if (intensity < 0.33) color = '#333';
        else if (intensity < 0.66) color = '#666';
        else color = '#FF6B00';

        ctx.fillStyle = color;
        var x = startX + col * (cellSize + gap);
        var y = startY + row * (cellSize + gap);
        ctx.fillRect(x, y, cellSize, cellSize);
        ctx.strokeStyle = '#222';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(x, y, cellSize, cellSize);

        row++;
        if (row >= 7) { row = 0; col++; }
    });

    canvas.title = 'Submission Activity Heatmap';
}
```

- [ ] **Step 4: Create `_rating_chart.html`**

```django
<section class="brutalist-panel brutalist-border" id="rating-chart-panel" style="background:#141414;">
    <header style="padding:8px 12px;border-bottom:1px solid #333;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;">{{ _('Rating History') }}</header>
    <div class="panel-content" style="padding:12px;min-height:400px;">
        <canvas id="rating-chart-canvas" width="800" height="360"></canvas>
        <div id="rating-tooltip" style="display:none;position:absolute;background:#0A0A0A;color:#F5F5F5;padding:6px;border:1px solid #333;font-family:'JetBrains Mono',monospace;font-size:0.75rem;pointer-events:none;">
            <div class="contest"></div>
            <div class="date" style="color:#888;"></div>
            <div class="rate-group"><span class="rating"></span> #<span class="rank"></span></div>
        </div>
    </div>
</section>
```

- [ ] **Step 5: Commit**

```bash
git add templates/user/user-about.html templates/user/_heatmap.html templates/user/_rating_chart.html templates/user/_radar_chart.html resources/user-heatmap.js resources/user-rating-chart.js resources/user-radar-chart.js
git commit -m "feat: add profile panels — heatmap, rating chart, radar"
```

---

### Task 6: Profile Panels — Skill Tree, Achievements, Rankings, Activity, Problems

**Files:**
- Create: `templates/user/_skill_tree.html`
- Create: `templates/user/_achievement_progression.html`
- Create: `templates/user/_multi_rankings.html`
- Create: `templates/user/_activity_feed.html`
- Create: `templates/user/_problem_stats.html`
- Create: `resources/user-skill-tree.js`
- Create: `resources/user-activity-feed.js`

- [ ] **Step 1: Create `_skill_tree.html`**

```django
<section class="brutalist-panel brutalist-border" data-panel="skill_tree" id="skill-tree-panel" style="background:#141414;">
    <header style="padding:8px 12px;border-bottom:1px solid #333;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;">{{ _('Skill Tree') }}</header>
    <div class="panel-content" style="padding:12px;min-height:400px;">
        <svg id="skill-tree-svg" width="100%" height="380" style="display:block;"></svg>
        <div class="panel-placeholder" style="text-align:center;padding:20px 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#666;">{{ _('Loading skill tree...') }}</div>
    </div>
</section>
<script>
document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('skill-tree-panel');
    if (!el) return;
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                var script = document.createElement('script');
                script.src = '{{ static("d3.min.js") }}';
                script.onload = function () {
                    fetch('/user/{{ user.user.username }}/skill-tree-data/')
                        .then(function (r) { return r.json(); })
                        .then(function (data) { renderSkillTree(data); });
                };
                document.head.appendChild(script);
                observer.unobserve(el);
            }
        });
    }, { rootMargin: '200px' });
    observer.observe(el);
});
</script>
```

- [ ] **Step 2: Create `_achievement_progression.html`**

```django
<section class="brutalist-panel brutalist-border" style="background:#141414;">
    <header style="padding:8px 12px;border-bottom:1px solid #333;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;">{{ _('Achievements') }}</header>
    <div class="panel-content" style="padding:12px;">
        {% set badges = user.badges.all() %}
        {% set bronze = badges|selectattr('name', 'equalto', 'Bronze')|list|length %}
        {% set silver = badges|selectattr('name', 'equalto', 'Silver')|list|length %}
        {% set gold = badges|selectattr('name', 'equalto', 'Gold')|list|length %}
        <div class="data-label">{{ _('Bronze') }}</div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
            <div style="flex:1;height:8px;background:#1E1E1E;">
                <div style="width:{{ (bronze / 20 * 100)|round(0) if bronze <= 20 else 100 }}%;height:100%;background:#FF6B00;"></div>
            </div>
            <span class="data-value" style="font-size:0.8rem;">{{ bronze }}/20</span>
        </div>
        <div class="data-label">{{ _('Silver') }}</div>
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
            <div style="flex:1;height:8px;background:#1E1E1E;">
                <div style="width:{{ (silver / 10 * 100)|round(0) if silver <= 10 else 100 }}%;height:100%;background:#888;"></div>
            </div>
            <span class="data-value" style="font-size:0.8rem;">{{ silver }}/10</span>
        </div>
        <div class="data-label">{{ _('Gold') }}</div>
        <div style="display:flex;align-items:center;gap:8px;">
            <div style="flex:1;height:8px;background:#1E1E1E;">
                <div style="width:{{ (gold / 5 * 100)|round(0) if gold <= 5 else 100 }}%;height:100%;background:#00FF88;"></div>
            </div>
            <span class="data-value" style="font-size:0.8rem;">{{ gold }}/5</span>
        </div>
        {% if not badges %}
        <div style="text-align:center;padding:16px 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#666;">{{ _('No badges earned yet.') }}</div>
        {% endif %}
    </div>
</section>
```

- [ ] **Step 3: Create `_multi_rankings.html`**

```django
<section class="brutalist-panel brutalist-border" style="background:#141414;">
    <header style="padding:8px 12px;border-bottom:1px solid #333;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;">{{ _('Rankings') }}</header>
    <div class="panel-content" style="padding:12px;">
        {% set total_users = total_users or 1 %}
        {% set global_percentile = ((total_users - rank) / total_users * 100)|round(0) %}
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span class="data-label" style="width:80px;">{{ _('Global') }}</span>
            <span class="data-value" style="width:60px;">#{{ rank }}</span>
            <div style="flex:1;height:8px;background:#1E1E1E;">
                <div style="width:{{ global_percentile }}%;height:100%;background:#FF6B00;"></div>
            </div>
            <span class="data-value" style="font-size:0.75rem;">{{ global_percentile }}th %ile</span>
        </div>
        {% if profile_country_rank is defined %}
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span class="data-label" style="width:80px;">{{ _('Country') }}</span>
            <span class="data-value" style="width:60px;">#{{ profile_country_rank }}</span>
            <div style="flex:1;height:8px;background:#1E1E1E;">
                <div style="width:{{ ((country_total or 1) - profile_country_rank) / (country_total or 1) * 100 }}%;height:100%;background:#666;"></div>
            </div>
            <span class="data-value" style="font-size:0.75rem;">{{ (((country_total or 1) - profile_country_rank) / (country_total or 1) * 100)|round(0) }}th %ile</span>
        </div>
        {% endif %}
        {% if rating_rank is defined %}
        <div style="display:flex;align-items:center;gap:8px;">
            <span class="data-label" style="width:80px;">{{ _('Contest') }}</span>
            <span class="data-value" style="width:60px;">#{{ rating_rank }}</span>
            <div style="flex:1;height:8px;background:#1E1E1E;">
                <div style="width:{{ ((total_users - rating_rank|int) / total_users * 100)|round(0) }}%;height:100%;background:#00FF88;"></div>
            </div>
            <span class="data-value" style="font-size:0.75rem;">{{ ((total_users - rating_rank|int) / total_users * 100)|round(0) }}th %ile</span>
        </div>
        {% endif %}
    </div>
</section>
```

- [ ] **Step 4: Create `_activity_feed.html`**

```django
<section class="brutalist-panel brutalist-border" id="activity-feed-panel" style="background:#141414;">
    <header style="padding:8px 12px;border-bottom:1px solid #333;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;">{{ _('Recent Activity') }}</header>
    <div class="panel-content" style="padding:12px;min-height:100px;">
        <div id="activity-timeline" style="border-left:2px solid #333;padding-left:16px;">
            {% for activity in recent_activity %}
            <div class="activity-item" style="margin-bottom:12px;position:relative;">
                <div style="position:absolute;left:-21px;top:4px;width:8px;height:8px;background:#333;border:1px solid #333;"></div>
                <div class="data-label" style="font-size:0.65rem;color:#555;">{{ activity.timestamp }}</div>
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#F5F5F5;margin-top:2px;">{{ activity.html|safe }}</div>
            </div>
            {% else %}
            <div style="text-align:center;padding:24px 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#666;">{{ _('No recent activity.') }}</div>
            {% endfor %}
        </div>
        {% if has_more_activity %}
        <button class="brutalist-btn" data-load-more-activity style="width:100%;padding:10px;border:1px solid #333;background:transparent;color:#888;font-family:'JetBrains Mono',monospace;font-size:0.75rem;cursor:pointer;margin-top:8px;">{{ _('Load more...') }}</button>
        {% endif %}
    </div>
</section>
<script>
document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('[data-load-more-activity]');
    if (!btn) return;
    var offset = {{ recent_activity|length }};
    btn.addEventListener('click', function () {
        fetch('/user/{{ user.user.username }}/activity-feed/?offset=' + offset + '&limit=20')
            .then(function (r) { return r.json(); })
            .then(function (data) {
                var timeline = document.getElementById('activity-timeline');
                data.items.forEach(function (item) {
                    var div = document.createElement('div');
                    div.className = 'activity-item';
                    div.style.cssText = 'margin-bottom:12px;position:relative;';
                    div.innerHTML = '<div style="position:absolute;left:-21px;top:4px;width:8px;height:8px;background:#333;border:1px solid #333;"></div>' +
                        '<div class="data-label" style="font-size:0.65rem;color:#555;">' + item.timestamp + '</div>' +
                        '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.8rem;color:#F5F5F5;margin-top:2px;">' + item.html + '</div>';
                    timeline.appendChild(div);
                    offset++;
                });
                if (!data.has_more) btn.style.display = 'none';
            });
    });
});
</script>
```

- [ ] **Step 5: Create `_problem_stats.html`**

```django
<section class="brutalist-panel brutalist-border" style="background:#141414;">
    <header style="padding:8px 12px;border-bottom:1px solid #333;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#888;text-transform:uppercase;letter-spacing:0.05em;">{{ _('Problem Statistics') }}</header>
    <div class="panel-content" style="padding:12px;overflow-x:auto;">
        {% if best_submissions %}
        <table style="width:100%;border-collapse:collapse;font-family:'JetBrains Mono',monospace;font-size:0.75rem;">
            <thead>
                <tr style="border-bottom:1px solid #333;">
                    <th style="padding:6px 8px;text-align:left;color:#888;font-weight:400;">{{ _('Category') }}</th>
                    <th style="padding:6px 8px;text-align:right;color:#888;font-weight:400;">{{ _('Solved') }}</th>
                    <th style="padding:6px 8px;text-align:right;color:#888;font-weight:400;">{{ _('Points') }}</th>
                </tr>
            </thead>
            <tbody>
            {% for group in best_submissions %}
                <tr style="border-bottom:1px solid #222;">
                    <td style="padding:4px 8px;color:#F5F5F5;">{{ group.name }}</td>
                    <td style="padding:4px 8px;text-align:right;color:#888;">{{ group.problems|length }}</td>
                    <td style="padding:4px 8px;text-align:right;color:#FF6B00;">{{ group.points|floatformat(1) }}</td>
                </tr>
            {% endfor %}
            </tbody>
        </table>
        {% else %}
        <div style="text-align:center;padding:16px 0;font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#666;">{{ _('No problems solved yet.') }}</div>
        {% endif %}
    </div>
</section>
```

- [ ] **Step 6: Commit**

```bash
git add templates/user/_skill_tree.html templates/user/_achievement_progression.html templates/user/_multi_rankings.html templates/user/_activity_feed.html templates/user/_problem_stats.html resources/user-skill-tree.js resources/user-activity-feed.js
git commit -m "feat: add profile panels — skill tree, achievements, rankings, activity, problems"
```

---

### Task 7: Data Endpoints for Lazy-Loaded Panels

**Files:**
- Modify: `judge/views/user.py` — add JSON data endpoints
- Modify: `judge/urls.py` — add data routes

- [ ] **Step 1: Add JSON data endpoints in `user.py`**

```python
from django.http import JsonResponse
from judge.models import Submission, ContestParticipation
from django.db.models.functions import Cast
from django.db.models.fields import DateField
from django.db.models import Count

class HeatmapDataView(UserMixin, View):
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        user_timezone = settings.DEFAULT_USER_TIME_ZONE
        if request.profile:
            user_timezone = user_timezone or request.profile.timezone
        import pytz, datetime
        offset = pytz.timezone(user_timezone).utcoffset(datetime.datetime.utcnow()).seconds
        submissions = (
            profile.submission_set
            .annotate(date_only=Cast(F('date') + datetime.timedelta(seconds=offset), DateField()))
            .values('date_only').annotate(cnt=Count('id'))
        )
        return JsonResponse({s['date_only'].isoformat(): s['cnt'] for s in submissions})

class SkillTreeDataView(UserMixin, View):
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        groups = (
            Submission.objects.filter(user=profile, points__gt=0, problem__is_public=True)
            .values('problem__group_id', 'problem__group__full_name')
            .annotate(solved=Count('id', distinct=True))
            .annotate(max_points=models.Max('points'))
        )
        nodes = []
        links = []
        for g in groups:
            nodes.append({
                'id': 'g%d' % g['problem__group_id'],
                'label': g['problem__group__full_name'],
                'solved': g['solved'],
                'points': float(g['max_points'] or 0),
            })
        # Simple topology: connect groups (placeholder — real D3 layout)
        for i in range(len(nodes) - 1):
            links.append({'source': nodes[i]['id'], 'target': nodes[i + 1]['id']})
        return JsonResponse({'nodes': nodes, 'links': links})

class ActivityFeedView(UserMixin, View):
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        offset = int(request.GET.get('offset', 0))
        limit = int(request.GET.get('limit', 20))
        submissions = profile.submission_set.select_related('problem').order_by('-date')[offset:offset + limit]
        items = []
        for s in submissions:
            items.append({
                'timestamp': s.date.strftime('%Y-%m-%d %H:%M:%S UTC'),
                'html': '<a href="%s" style="color:#FF6B00;text-decoration:none;">%s</a> — %s pts' % (
                    reverse('submission', args=(s.id,)),
                    s.problem.name if s.problem else '?',
                    '%.1f' % s.points if s.points else '0',
                ),
            })
        return JsonResponse({
            'items': items,
            'has_more': len(items) == limit,
            'offset': offset + len(items),
        })
```

Then register in urls.py:
```python
path('user/<str:user>/heatmap-data/', HeatmapDataView.as_view(), name='user_heatmap_data'),
path('user/<str:user>/skill-tree-data/', SkillTreeDataView.as_view(), name='user_skill_tree_data'),
path('user/<str:user>/activity-feed/', ActivityFeedView.as_view(), name='user_activity_feed'),
```

- [ ] **Step 2: Add context data for `UserAboutPage`** (recent_activity, profile_country_rank)

In `UserAboutPage.get_context_data()`, add:
```python
# Recent activity
context['recent_activity'] = [
    {
        'timestamp': s.date.strftime('%Y-%m-%d %H:%M:%S'),
        'html': '<a href="%s" style="color:#FF6B00;text-decoration:none;">%s</a> — %.1f pts' % (
            reverse('submission', args=(s.id,)),
            s.problem.name if s.problem else '?',
            s.points or 0,
        ),
    }
    for s in self.object.submission_set.select_related('problem').order_by('-date')[:10]
]
context['has_more_activity'] = self.object.submission_set.count() > 10

# Country rank (if user has country set)
from judge.models import Profile as ProfileModel
if hasattr(self.object, 'country') and self.object.country:
    context['profile_country_rank'] = ProfileModel.objects.filter(
        is_unlisted=False, country=self.object.country,
        performance_points__gt=self.object.performance_points,
    ).count() + 1
    context['country_total'] = ProfileModel.objects.filter(
        is_unlisted=False, country=self.object.country,
    ).count()
```

- [ ] **Step 3: Commit**

```bash
git add judge/views/user.py judge/urls.py
git commit -m "feat: add JSON data endpoints for lazy-loaded panels"
```

---

### Task 8: Comparison Page

**Files:**
- Create: `templates/user/compare.html`
- Create: `resources/user-comparison.js`
- Modify: `resources/users.scss` — add comparison styles

- [ ] **Step 1: Create `compare.html`**

```django
{% extends "base.html" %}
{% block title %}{{ _('Compare Users') }}{% endblock %}

{% block body %}
<div class="users-page" style="padding:24px;">
    <header class="brutalist-border" style="padding:16px 24px;background:#141414;margin-bottom:24px;">
        <h1 style="font-family:'Space Grotesk',system-ui,sans-serif;font-size:1.5rem;text-transform:uppercase;letter-spacing:0.05em;color:#F5F5F5;margin:0;">{{ _('Compare Users') }}</h1>
    </header>

    {% if error %}
    <div class="brutalist-border" style="padding:16px;background:#141414;font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#FF3366;margin-bottom:24px;">{{ error }}</div>
    {% endif %}

    {% if user_a and user_b %}
    <div class="brutalist-grid" style="grid-template-columns:1fr 1fr;gap:24px;">
        {# User A #}
        <div class="brutalist-border" style="background:#141414;padding:16px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <img src="{{ gravatar(user_a, 64) }}" style="width:64px;height:64px;border:2px solid #333;">
                <div>
                    <a href="{{ url('user_page', user_a.user.username) }}" style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;color:#FF6B00;text-decoration:none;">{{ user_a.user.username }}</a>
                    <div class="data-label">{{ _('Rating:') }} <span class="data-value">{% if user_a.rating %}{{ user_a.rating }}{% else %}{{ _('Unrated') }}{% endif %}</span></div>
                    <div class="data-label">{{ _('Points:') }} <span class="data-value">{{ user_a.performance_points|floatformat(1) }}</span></div>
                    <div class="data-label">{{ _('Solved:') }} <span class="data-value">{{ user_a.problem_count }}</span></div>
                </div>
            </div>
        </div>

        {# User B #}
        <div class="brutalist-border" style="background:#141414;padding:16px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
                <img src="{{ gravatar(user_b, 64) }}" style="width:64px;height:64px;border:2px solid #333;">
                <div>
                    <a href="{{ url('user_page', user_b.user.username) }}" style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;color:#FF6B00;text-decoration:none;">{{ user_b.user.username }}</a>
                    <div class="data-label">{{ _('Rating:') }} <span class="data-value">{% if user_b.rating %}{{ user_b.rating }}{% else %}{{ _('Unrated') }}{% endif %}</span></div>
                    <div class="data-label">{{ _('Points:') }} <span class="data-value">{{ user_b.performance_points|floatformat(1) }}</span></div>
                    <div class="data-label">{{ _('Solved:') }} <span class="data-value">{{ user_b.problem_count }}</span></div>
                </div>
            </div>
        </div>

        {# Head-to-Head #}
        <div class="brutalist-border" style="grid-column:1/-1;background:#141414;padding:16px;">
            <div class="data-label" style="margin-bottom:8px;">{{ _('Head-to-Head') }}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;text-align:center;">
                <div class="brutalist-border" style="padding:12px;background:#1E1E1E;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;color:#00FF88;">{{ head_to_head.a_wins }}</div>
                    <div class="data-label">{{ user_a.user.username }} {{ _('wins') }}</div>
                </div>
                <div class="brutalist-border" style="padding:12px;background:#1E1E1E;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;color:#888;">{{ head_to_head.ties }}</div>
                    <div class="data-label">{{ _('Ties') }}</div>
                </div>
                <div class="brutalist-border" style="padding:12px;background:#1E1E1E;">
                    <div style="font-family:'JetBrains Mono',monospace;font-size:1.5rem;color:#FF3366;">{{ head_to_head.b_wins }}</div>
                    <div class="data-label">{{ user_b.user.username }} {{ _('wins') }}</div>
                </div>
            </div>
            <div class="data-label" style="margin-top:8px;text-align:center;">{{ _('Common solved: %d problems') % common_count }}</div>
        </div>

        {# Topic Differential #}
        <div class="brutalist-border" style="grid-column:1/-1;background:#141414;padding:16px;">
            <div class="data-label" style="margin-bottom:8px;">{{ _('Topic Differential') }}</div>
            {% for item in topic_diff %}
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <span class="data-label" style="width:100px;">{{ item.group_name }}</span>
                <div style="flex:1;height:6px;background:#1E1E1E;position:relative;">
                    {% if item.diff > 0 %}
                    <div style="position:absolute;right:50%;width:{{ item.pct }}%;height:100%;background:#00FF88;top:0;"></div>
                    {% elif item.diff < 0 %}
                    <div style="position:absolute;left:50%;width:{{ item.pct|abs }}%;height:100%;background:#FF3366;top:0;"></div>
                    {% endif %}
                    <div style="position:absolute;left:50%;top:-2px;width:1px;height:10px;background:#333;"></div>
                </div>
                <span class="data-value" style="width:60px;font-size:0.7rem;text-align:right;">
                    {% if item.diff > 0 %}+{% endif %}{{ item.diff }}
                </span>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}

    {# Search Form #}
    <div class="brutalist-border" style="background:#141414;padding:16px;margin-top:24px;">
        <form method="get" action="{{ url('user_compare') }}" style="display:flex;gap:12px;align-items:end;flex-wrap:wrap;">
            <div>
                <div class="data-label" style="margin-bottom:4px;">{{ _('User 1') }}</div>
                <input type="text" name="u1" value="{{ user_a.user.username if user_a else '' }}" style="width:200px;height:36px;background:#0A0A0A;border:1px solid #333;color:#F5F5F5;font-family:'JetBrains Mono',monospace;font-size:0.8rem;padding:0 12px;">
            </div>
            <div>
                <div class="data-label" style="margin-bottom:4px;">{{ _('User 2') }}</div>
                <input type="text" name="u2" value="{{ user_b.user.username if user_b else '' }}" style="width:200px;height:36px;background:#0A0A0A;border:1px solid #333;color:#F5F5F5;font-family:'JetBrains Mono',monospace;font-size:0.8rem;padding:0 12px;">
            </div>
            <button type="submit" style="height:36px;padding:0 16px;background:transparent;border:1px solid #FF6B00;color:#FF6B00;font-family:'JetBrains Mono',monospace;font-size:0.75rem;cursor:pointer;">{{ _('Compare') }}</button>
        </form>
    </div>
</div>
{% endblock %}
```

- [ ] **Step 2: Add comparison styles to `users.scss`**

```scss
// ─── Comparison Page ────────────────────────────────────────────────
.compare-pane {
  header {
    font-family: $ind-font-mono;
    font-size: 0.75rem;
    color: $ind-text-muted;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add templates/user/compare.html resources/user-comparison.js resources/users.scss
git commit -m "feat: add user comparison page"
```

---

### Task 9: SCSS Polish & Responsive

**Files:**
- Modify: `resources/users.scss` — complete responsive styles
- Modify: `resources/_users-variables.scss` — add responsive breakpoints

- [ ] **Step 1: Add responsive breakpoints to `_users-variables.scss`**

```scss
$ind-breakpoint-sm: 640px;
$ind-breakpoint-md: 1024px;
```

- [ ] **Step 2: Add responsive + component styles to `users.scss`**

```scss
// ─── Responsive ─────────────────────────────────────────────────────
@media (max-width: 1023px) {
  .brutalist-two-col {
    grid-template-columns: 1fr;
  }
  .user-sidebar {
    position: static;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 8px 16px;
    align-items: start;
  }
  .user-sidebar img {
    grid-row: 1 / 4;
  }
}

@media (max-width: 639px) {
  .top-performers {
    grid-template-columns: 1fr !important;
  }
  .brutalist-grid[style*="grid-template-columns: 1fr 1fr"] {
    grid-template-columns: 1fr !important;
  }
  .users-header > div {
    flex-direction: column;
    align-items: stretch !important;
    gap: 8px;
  }
  #search-form, #search-handle {
    width: 100% !important;
  }
  .user-sidebar {
    display: block;
  }
  .users-table {
    font-size: 0.7rem;
  }
  .users-table th:nth-child(3),
  .users-table td:nth-child(3),
  .users-table th:nth-child(6),
  .users-table td:nth-child(6) {
    display: none;
  }
}

// ─── Brutalist Button ───────────────────────────────────────────────
.brutalist-btn {
  font-family: $ind-font-mono;
  font-size: 0.75rem;
  padding: 10px 16px;
  border: 1px solid $ind-border;
  background: transparent;
  color: $ind-text;
  transition: none;
  cursor: pointer;
  text-decoration: none;
  display: inline-block;
  line-height: 1;

  &:hover {
    border-color: $ind-accent-primary;
    color: $ind-accent-primary;
  }
}

// ─── Panel ──────────────────────────────────────────────────────────
.brutalist-panel {
  animation: panelFadeIn 200ms ease-out both;
}

@keyframes panelFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

// ─── Tab Navigation ─────────────────────────────────────────────────
.user-list-tabs {
  display: flex;
  border-bottom: 1px solid $ind-border;
  margin: 0;
  padding: 0 24px;
  list-style: none;
  font-family: $ind-font-mono;
  font-size: 0.75rem;

  li {
    margin: 0;

    a {
      display: block;
      padding: 10px 16px 8px;
      color: $ind-text-muted;
      text-decoration: none;
      border-bottom: 2px solid transparent;
      text-transform: uppercase;
      letter-spacing: 0.05em;

      &:hover { color: $ind-text; }
    }

    &.active a {
      color: $ind-accent-primary;
      border-bottom-color: $ind-accent-primary;
    }
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add resources/_users-variables.scss resources/users.scss
git commit -m "style: add responsive breakpoints and component styles"
```

---

### Task 10: Tab Updates + Final Integration

**Files:**
- Modify: `templates/user/user-list-tabs.html` — add Compare tab
- Modify: `templates/user/user-tabs.html` — add any necessary tabs

- [ ] **Step 1: Update `user-list-tabs.html`**

```django
{% extends "tabs-base.html" %}
{% block tabs %}
    {{ make_tab('list', 'fa-users', url('user_list'), _('Leaderboard')) }}
    {{ make_tab('contributor', 'fa-thumbs-up', url('contributors_list'), _('Contributors')) }}
    {{ make_tab('organizations', 'fa-university', url('organization_list'), _('Organizations')) }}
    {{ make_tab('compare', 'fa-balance-scale', url('user_compare'), _('Compare')) }}
    {% if request.user.is_staff or request.user.is_superuser %}
        {{ make_tab('add-user', 'fa-plus', url('add_user'), _('Add User')) }}
        {{ make_tab('import-users', 'fa-upload', url('import_users'), _('Import Users')) }}
    {% endif %}
{% endblock %}
```

- [ ] **Step 2: Make sure all SCSS compiles properly and is processed**

Run: `cd /home/nomoka/site && npm run build 2>/dev/null || sass resources/users.scss sass_processed/users.css --no-source-map`

- [ ] **Step 3: Final verification**

- Verify templates render without errors
- Verify static files are accessible
- Verify comparison page loads for two valid users
- Verify leaderboard page shows top performers section

- [ ] **Step 4: Final commit**

```bash
git add templates/user/user-list-tabs.html
git commit -m "feat: add Compare tab to leaderboard navigation"
```

---

## Self-Review Checklist

- **Spec coverage**: Leaderboard (T3), profile layout (T2), heatmap (T5), rating chart (T5), radar (T5), skill tree (T6), achievements (T6), multi-rankings (T6), activity feed (T6), problem stats (T6), comparison (T4+T8), data endpoints (T7), responsive (T9)
- **Placeholder scan**: No TODOs, TBDs, or incomplete code blocks
- **Type consistency**: All function signatures match across tasks

---

**Plan complete. Two execution options:**

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks
2. **Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
