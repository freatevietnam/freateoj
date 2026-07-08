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

