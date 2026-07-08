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
