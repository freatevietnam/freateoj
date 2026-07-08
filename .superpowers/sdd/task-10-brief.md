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

