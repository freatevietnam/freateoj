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

