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

