# Industrial/Brutalist Users Page Redesign — Design Specification

**Date**: 2026-07-30  
**Branch**: `redesign/users-page`  
**Scope**: Complete redesign of `/users/` (leaderboard) and `/user/<username>/` (profile) pages

---

## 1. Design Direction: Industrial/Brutalist

### Visual Language
- **Typography**: 
  - Data/monospace: `JetBrains Mono` / `IBM Plex Mono` (fallback: `monospace`)
  - UI labels: `Space Grotesk` (fallback: `system-ui, sans-serif`)
- **Color Palette**:
  - Background: `#0A0A0A` (near-black)
  - Surface: `#141414` / `#1E1E1E` (elevated panels)
  - Border: `#333333` (1px, no rounded corners)
  - Text primary: `#F5F5F5`
  - Text muted: `#888888`
  - Accent (rating/primary): `#FF6B00` (orange)
  - Accent (success/growth): `#00FF88` (green)
  - Accent (warning/decline): `#FF3366` (red)
- **Spacing**: 8px baseline grid, visible 12-column layout grid
- **Borders**: 1px solid `#333`, **zero border-radius** everywhere
- **Shadows**: None (flat, raw aesthetic)
- **Motion**: Instant (0ms), `prefers-reduced-motion` → no transitions

### Component Principles
- Exposed structure: visible grid lines, raw table borders
- Monospace for all numbers, codes, technical data
- Sharp corners, no rounding
- High contrast, no subtle gradients
- Functional over decorative

---

## 2. Users List Page (`/users/`)

### 2.1 Header Section (120px, full-bleed)
```
┌─────────────────────────────────────────────────────────────────┐
│  USERS / LEADERBOARD                                    [SEARCH] │
│  ──────────────────────────────────────────────────────────────  │
│  Total: 12,847 users  •  Active (24h): 342  •  Top 1%: ≥2400 pp  │
└─────────────────────────────────────────────────────────────────┘
```
- Title: `Space Grotesk`, 1.5rem, uppercase, letter-spacing 0.05em
- Stats bar: `JetBrains Mono`, 0.75rem, `color: #888`
- Search: brutalist input, 280px wide, 1px border `#333`, no radius, placeholder mono

### 2.2 Top Performers Widget Row (4 cards, 3-col desktop / 2-col tablet / 1-col mobile)
Each card:
- Rank badge: `#1 RATED` / `#1 POINTS` / `RISING STAR` / `TOP ORG` — uppercase mono, 0.6rem, accent border
- Visual: Raw progress bar (height 4px, no radius) or avatar
- Handle: mono, 1rem, link style
- Metric: large mono number (2rem) with unit label
- Org card: member count, total org points

### 2.3 Hybrid Leaderboard

**Top 10 (ranks 1–10)**: Compact data table
| Rank | Handle | Rating ● | Points | Solved | Org | Trend |
|------|--------|----------|--------|--------|-----|-------|
| 1    | `user_abc`  | 2847 | 3241.2 | 1,247 | HCMUS | ↗ +12 |

- Row height: 40px
- Rank: mono, right-aligned, width 48px
- Handle: `font-family: monospace`, `font-size: 0.875rem`
- Rating: colored dot (●) + number, dot color by rating class
- Trend: mono arrow + number, green/red

**Ranks 11+**: Card grid (3-col desktop, 2-col tablet, 1-col mobile)
Card content:
- Avatar (32px, square)
- Handle + rating dot
- 3 key metrics: Points, Solved, Rating
- Mini sparkline (40×20px, canvas, mono tooltip on hover)

### 2.4 Tab Navigation
Brutalist underline style:
```
LEADERBOARD    CONTRIBUTORS    ORGANIZATIONS    COMPARE
───────────────────────────────────────────────────────
```
- Active: 2px bottom border `#FF6B00`, text `#FF6B00`
- Inactive: 1px bottom border `#333`, text `#888`
- Hover: text `#F5F5F5`

### 2.5 Pagination
Bottom bar: `Page 1 of 129` (mono) + `[Prev] [1] [2] [3] ... [129] [Next]`
- Buttons: border only, 32×32px, mono labels

---

## 3. User Profile Page (`/user/<username>/`)

### 3.1 Layout: Two-Column Brutalist Grid
```
┌──────────────┬────────────────────────────────────────┐
│   SIDEBAR    │           CONTENT AREA                 │
│   (280px)    │           (1fr, min-width 0)           │
│   sticky     │                                        │
└──────────────┴────────────────────────────────────────┘
```
- Gap: 24px
- Responsive: `< 1024px` → stacked (sidebar becomes header panel)

### 3.2 Sidebar Module (Fixed, sticky top: 24px)
```
┌────────────────────────┐
│  ████████████████████  │  135×135px avatar, square, border 2px #333
│  █ USER_HANDLE █████  │
│  ────────────────────  │  1px border #333
│  RATING  ● 2847        │  Label: mono 0.7rem #888 | Value: mono 1rem #F5F5F5
│  RANK   #1 / 12,847    │  Rating dot: 8px, color by class
│  POINTS 3241.2 pp      │
│  SOLVED  1,247         │
│  ────────────────────  │
│  ORG:  HCMUS ▼         │  Dropdown: brutalist select
│  JOINED: 2023-03-15    │
│  ────────────────────  │
│  [COMPARE] [FOLLOW]    │  Buttons: 1px border, 40px height, mono 0.75rem
└────────────────────────┘
```
- Width: 280px fixed
- Background: `#141414`, border: 1px `#333`

### 3.3 Content Area: Modular Panels (CSS Grid, auto-flow dense)

#### Panel 1: ACTIVITY HEATMAP (Full-width, 320px tall)
- Canvas-based, 53 weeks × 7 days
- Cell: 10×10px, gap 2px
- Colors: `#1E1E1E` (0) → `#333` → `#666` → `#FF6B00` (4+)
- Hover tooltip: absolute positioned, mono, `2026-07-15: 12 submissions`
- Legend: 4 swatches with mono labels `Less` / `More`

#### Panel 2: RATING HISTORY CHART (Full-width, 360px tall)
- Chart.js line chart, **no fill**, stroke only (2px)
- Grid lines: `#333` (major), `#222` (minor)
- Axes: mono labels, no axis lines
- Rating bands: horizontal rules at 1200, 1400, 1600, 1900, 2200, 2400, 2600, 2900
  - Band labels: mono 0.6rem, `#555`, right-aligned
- Points: 4px squares, hover → tooltip with contest name, date, rating, rank
- Click point → navigate to contest ranking

#### Panel 3: TOPIC STRENGTHS RADAR (6-col, 360px tall)
- SVG radar chart, 6 axes: DP, Graph, Math, Geometry, Strings, Ad-hoc
- Axes: `#333` lines, mono labels at 120% radius
- Data polygon: stroke `#FF6B00` (2px), fill `rgba(255,107,0,0.1)`
- Percentile markers: 25/50/75/90% concentric polygons, `#222`
- Tooltip on vertex: `DP: 847 solved • 92nd %ile • 1,241 pp`

#### Panel 4: SKILL TREE (6-col, 400px tall)
- D3.js force-directed graph (lazy-loaded via IntersectionObserver)
- Nodes: problem tags, radius = log(solved_count) × 3, min 8px max 40px
- Node color: mastery gradient `#333` → `#FF6B00`
- Links: `#222` lines, 0.5px
- Click node → filters Panel 8 (Problem Statistics) to that tag
- Fallback: static SVG if JS fails / prefers-reduced-motion

#### Panel 5: ACHIEVEMENT PROGRESSION (4-col, 200px tall)
```
BRONZE  ████████░░  12/20
SILVER  ████░░░░░░  5/10
GOLD    █░░░░░░░░░  1/5
```
- Raw progress bars: height 8px, bg `#1E1E1E`, fill accent, no radius
- Labels: mono 0.75rem, right-aligned counts

#### Panel 6: MULTI-DIMENSIONAL RANKINGS (4-col, 280px tall)
```
GLOBAL      #1,247  ████████░░  90th %ile
VIETNAM     #89     █████████░  95th %ile
HCMUS       #3      ██████████  99th %ile
CONTEST     #234    ██████░░░░  78th %ile
```
- Each row: label (mono 0.7rem #888), rank (mono 1rem #F5F5F5), bar (120px), percentile (mono 0.7rem accent)

#### Panel 7: RECENT ACTIVITY FEED (Full-width, infinite scroll)
- Brutalist timeline: left rail (2px `#333` vertical line), right cards
- Item types: submission, contest, badge, blog, follow
- Timestamp: mono 0.7rem `#888`, `2026-07-29 14:32:11 UTC`
- Card: border 1px `#333`, padding 12px, mono content
- Load more: button at bottom, brutalist style

#### Panel 8: PROBLEM STATISTICS (Full-width, collapsible table)
- Grouped by category (DP, Graph, Math, etc.)
- Columns: Problem, Category, Score, Total, %ile, First AC
- Sortable headers (click → resort)
- Filterable by tag (via Panel 4 interaction)
- Expandable rows → show submission history for that problem

---

## 4. Comparison Feature (`/users/compare/?u1=<u1>&u2=<u2>`)

### 4.1 Route & View
- URL: `/users/compare/` with query params `u1`, `u2`
- View: `UserComparisonView` (new class-based view)
- Template: `user/compare.html` (extends `base.html`)

### 4.2 Layout: Split-Screen Brutalist
```
┌─────────────────────────┬─────────────────────────┐
│       USER_A            │       USER_B            │
│  ████████████████       │  ████████████           │
│  Rating:  2847 ●        │  Rating:  2612 ●        │
│  Points:  3241.2        │  Points:  2987.5        │
│  Solved:  1247          │  Solved:  1089          │
├─────────────────────────┼─────────────────────────┤
│  HEAD-TO-HEAD           │  HEAD-TO-HEAD           │
│  Common solved:  847    │  Common solved:  847    │
│  A beat B:      234     │  B beat A:      189     │
│  Same score:    424     │  Same score:    424     │
├─────────────────────────┼─────────────────────────┤
│  TOPIC DIFFERENTIAL     │  TOPIC DIFFERENTIAL     │
│  ████████░░ DP +15%     │  ██████░░░░ Graph -12%  │
│  ██████░░░░ Math +8%    │  ████████░░ Strings +18%│
└─────────────────────────┴─────────────────────────┘
```
- Each pane: 50% width, border-right 1px `#333` on left pane
- Mobile: stacked, full-width panes
- Header link from profile sidebar `[COMPARE]` → opens with current user + target user

### 4.3 Data Computation
- Common solved: intersection of AC problem sets
- Head-to-head: compare best submission score per common problem
- Topic differential: per-category (group) solved count difference, normalized

---

## 5. Technical Implementation

### 5.1 New/Modified Files

#### Templates
- `templates/user/list.html` — complete rewrite
- `templates/user/user-base.html` — complete rewrite (profile layout)
- `templates/user/user-about.html` — restructure into panels
- `templates/user/compare.html` — new
- `templates/user/_heatmap.html` — partial
- `templates/user/_rating_chart.html` — partial
- `templates/user/_radar_chart.html` — partial
- `templates/user/_skill_tree.html` — partial
- `templates/user/_activity_feed.html` — partial
- `templates/user/_problem_stats.html` — partial
- `templates/user/_achievement_progression.html` — partial
- `templates/user/_multi_rankings.html` — partial
- `templates/user/_leaderboard_table.html` — partial
- `templates/user/_leaderboard_cards.html` — partial
- `templates/user/_top_performers.html` — partial

#### Static (SCSS)
- `resources/users.scss` — complete rewrite (industrial variables, grid, components)
- `resources/_users-variables.scss` — new (industrial color/spacing tokens)
- `resources/_users-charts.scss` — new (chart-specific styles)

#### JavaScript
- `resources/user-heatmap.js` — new (canvas heatmap)
- `resources/user-rating-chart.js` — new (Chart.js wrapper)
- `resources/user-radar-chart.js` — new (SVG radar)
- `resources/user-skill-tree.js` — new (D3 force graph, lazy)
- `resources/user-activity-feed.js` — new (infinite scroll)
- `resources/user-comparison.js` — new (comparison page interactions)
- `resources/user-profile.js` — refactor (panel lazy-loading, IntersectionObserver)

#### Python (Django)
- `judge/views/user.py` — add `UserComparisonView`, extend `UserPage` context
- `judge/utils/user_stats.py` — new (stat computation helpers: heatmap data, radar data, skill tree data, comparison logic)
- `judge/urls.py` — add `/users/compare/` route

### 5.2 Chart Libraries
- **Chart.js v4** — rating history line chart (already in project)
- **D3.js v7** — skill tree force graph (lazy-loaded via dynamic import)
- **Custom Canvas** — activity heatmap (no external dep)
- **Custom SVG** — radar chart (no external dep)

### 5.3 Data Endpoints (JSON)
- `GET /user/<username>/heatmap-data/` → `{ "2026-07-15": 12, ... }`
- `GET /user/<username>/rating-history/` → `[{timestamp, rating, contest, rank}, ...]`
- `GET /user/<username>/topic-strengths/` → `{ "DP": {solved, percentile, pp}, ... }`
- `GET /user/<username>/skill-tree/` → `{ nodes: [...], links: [...] }`
- `GET /user/<username>/activity-feed/?offset=0&limit=20` → `[{type, timestamp, data}, ...]`
- `GET /users/compare-data/?u1=x&u2=y` → `{ user1: {...}, user2: {...}, head_to_head: {...}, topic_diff: {...} }`

### 5.4 Performance Strategy
- All charts lazy-loaded via `IntersectionObserver` (rootMargin: "200px")
- Chart JS bundles code-split (dynamic `import()`)
- Heatmap/radar: inline SVG/Canvas, no extra JS
- Activity feed: HTMX-style fragment replacement via `fetch()`
- Profile data: cached 5min (Redis/django-cache)
- Comparison: computed on-demand, cached 2min

### 5.5 Responsive Breakpoints
- `< 640px`: Single column, sidebar → header panel, cards stack
- `640–1024px`: Two-col sidebar|content, panels 2-col grid
- `> 1024px`: Full layout, 4-col performer widgets, 6-col radar/skill-tree

### 5.6 Accessibility
- Semantic HTML: `<table>` for leaderboard, `<section>` for panels
- ARIA labels on all icon-only buttons
- Color contrast: AAA for text, AA for UI elements
- `prefers-reduced-motion`: disable all transitions, static chart fallbacks
- Keyboard navigation: focus visible (2px `#FF6B00` outline)
- Screen readers: hidden text for visual-only elements (sparklines, progress bars)

---

## 6. Migration Path

1. **Phase 1**: Create branch, add industrial variables, rewrite `users.scss`
2. **Phase 2**: Implement leaderboard page (templates + partials + JS)
3. **Phase 3**: Implement profile sidebar + panel system
4. **Phase 4**: Build each panel (heatmap, rating chart, radar, skill tree, achievements, rankings, activity, problems)
5. **Phase 5**: Comparison feature (view, template, data endpoint, JS)
6. **Phase 6**: Responsive testing, accessibility audit, performance profiling
7. **Phase 7**: Polish, edge cases, documentation

---

## 7. Success Criteria

- [ ] Leaderboard loads < 200ms (p95) on 100 rows
- [ ] Profile panels lazy-load, no layout shift (CLS < 0.1)
- [ ] Heatmap renders < 100ms (canvas)
- [ ] Comparison page computes < 500ms for 2 users with 1000+ solved
- [ ] Zero console errors, no layout shift on all breakpoints
- [ ] WCAG 2.1 AA compliant
- [ ] Works with JS disabled (graceful degradation: static tables, no charts)

---

## 8. Open Questions (Resolved)

| Question | Decision |
|----------|----------|
| Leaderboard layout | Hybrid: table top 10, cards 11+ |
| Profile layout | Two-col grid (sidebar + modular panels) |
| Chart library | Chart.js (rating), D3 (skill tree), custom Canvas/SVG (heatmap, radar) |
| Comparison URL | `/users/compare/?u1=x&u2=y` |
| Skill tree | D3 force graph, click filters problem stats |
| Activity feed | Infinite scroll, brutalist timeline |

---

*Spec written: 2026-07-30*  
*Branch: `redesign/users-page`*  
*Next: Invoke `writing-plans` skill for implementation plan*