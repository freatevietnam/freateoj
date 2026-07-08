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

