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

