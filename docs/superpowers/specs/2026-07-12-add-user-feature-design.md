# Add User Feature Design

**Date:** 2026-07-12
**Status:** Approved
**Author:** opencode

## Overview

Add a web-based "Add User" feature to the `/users/` page, allowing Staff and Admin users to create new users via two methods:
1. **GUI Form** — manual entry of user details
2. **CSV Import** — bulk creation from a CSV file

## Access Control

- **Allowed roles:** `is_staff` or `is_superuser`
- **Denied behavior:** Redirect to `/users/` with error message
- **Login required:** Yes, all views require `@login_required`

## URL Structure

| URL | View | Name | Purpose |
|-----|------|------|---------|
| `/users/add/` | `AddUserGUI` | `user_add` | GUI form for single user creation |
| `/users/import/` | `AddUserCSV` | `user_import` | CSV upload and bulk import |

The existing `/users/` leaderboard page gets a new tab/link "Add User" visible to staff/admin users.

## GUI Form (`/users/add/`)

### Fields

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `username` | CharField | Yes | Alphanumeric + underscore, max 30 chars, unique |
| `email` | EmailField | Yes | Valid format, unique |
| `password` | PasswordInput | Yes | Min 8 chars |
| `password_confirm` | PasswordInput | Yes | Must match password |
| `first_name` | CharField | No | Max 30 chars |
| `last_name` | CharField | No | Max 150 chars |
| `timezone` | Select | No | Dropdown, default = UTC |
| `language` | Select | No | Dropdown from Language model |
| `organizations` | SelectMultiple | No | Multi-select, max 3 orgs |

### Behavior

1. GET: Render empty form
2. POST: Validate all fields
3. On success:
   - Create `django.contrib.auth.models.User` with `make_password()`
   - Create `judge.models.Profile` linked to the User
   - Set Profile fields: timezone, language, organizations
   - Redirect to `/users/` with success message
4. On failure: Re-render form with errors

### Template: `user/add-user.html`

- Extends `base.html`
- Uses Semantic UI form styling (consistent with existing forms)
- Form fields with error display
- Submit button "Add User"
- Cancel link back to `/users/`

## CSV Import (`/users/import/`)

### CSV Format

```csv
username,email,password,fullname,timezone,language,organizations
user1,user1@example.com,pass1234,User One,Asia/Ho_Chi_Minh,en,org1;org2
user2,user2@example.com,pass5678,User Two,UTC,vi,
```

**Column details:**

| Column | Required | Description |
|--------|----------|-------------|
| `username` | Yes | Alphanumeric + underscore, max 30 chars, unique |
| `email` | Yes | Valid email format, unique |
| `password` | Yes | Min 8 chars |
| `fullname` | No | Split into `first_name` (first word) and `last_name` (rest) |
| `timezone` | No | Default = UTC if empty or invalid |
| `language` | No | Language code (e.g., `en`, `vi`), default = first Language if empty |
| `organizations` | No | Semicolon-separated org slugs, max 3 |

### Behavior

1. **Upload step (GET):**
   - Show file upload form (accept `.csv`)
   - Instructions: format description, example CSV

2. **Preview step (POST with file):**
   - Parse CSV, validate each row
   - Show preview table with columns: `#`, `username`, `email`, `fullname`, `status` (OK/Error), `errors`
   - Show summary: X valid, Y errors
   - "Import" button to confirm, "Cancel" to go back

3. **Import step (POST confirm):**
   - Create users for valid rows, skip error rows
   - Use `transaction.atomic()` for each user (partial import allowed)
   - Redirect to `/users/` with summary message: "Imported X users, Y errors"

### Template: `user/import-user.html`

- Extends `base.html`
- Upload form with file input (accept `.csv`, max 5MB)
- CSV must be UTF-8 encoded
- Preview table (after upload)
- Import/Cancel buttons (after preview)
- Results summary (after import)

## Views

### `AddUserGUI`

```python
class AddUserGUI(LoginRequiredMixin, View):
    def get(self, request):
        # Check staff/admin permission
        # Render empty form
        pass

    def post(self, request):
        # Check staff/admin permission
        # Validate form
        # Create User + Profile
        # Redirect with message
        pass
```

### `AddUserCSV`

```python
class AddUserCSV(LoginRequiredMixin, View):
    def get(self, request):
        # Check staff/admin permission
        # Render upload form
        pass

    def post(self, request):
        # Check staff/admin permission
        # If file uploaded: parse CSV, validate, show preview
        # If confirm clicked: import users, show results
        pass
```

## Template Changes

### `user/list.html`

Add a new tab "Add User" (visible to staff/admin only):

```html
{% if request.user.is_staff or request.user.is_superuser %}
<a class="item" data-tab="add-user-tab">
    <i class="add icon"></i> Add User
</a>
{% endif %}
```

Or add buttons next to existing tabs:
- "Add User" button → links to `/users/add/`
- "Import CSV" button → links to `/users/import/`

## Error Handling

| Scenario | Handling |
|----------|----------|
| Duplicate username | Field error: "Username already exists" |
| Duplicate email | Field error: "Email already exists" |
| Invalid email format | Field error: "Enter a valid email address" |
| Weak password | Field error: "Password must be at least 8 characters" |
| Password mismatch | Field error: "Passwords do not match" |
| Invalid timezone | Use default UTC |
| Invalid language | Use default language |
| Invalid org slug | Skip org, continue with user creation |
| CSV parse error | Show error message with line number |
| Empty CSV | Show error: "CSV file is empty" |
| Wrong CSV columns | Show error: "CSV must have columns: username, email, password" |
| File too large | Show error: "File size must be less than 5MB" |
| Wrong encoding | Show error: "CSV file must be UTF-8 encoded" |

## Files to Modify/Create

| File | Action | Description |
|------|--------|-------------|
| `judge/views/user.py` | Modify | Add `AddUserGUI` and `AddUserCSV` views |
| `judge/forms.py` | Modify | Add `AddUserForm` and `UserImportForm` |
| `templates/user/add-user.html` | Create | GUI form template |
| `templates/user/import-user.html` | Create | CSV import template |
| `templates/user/list.html` | Modify | Add "Add User" tab/buttons |
| `dmoj/urls.py` | Modify | Add URL patterns |
| `judge/constants.py` | Check | Verify language/timezone choices |

## Security Considerations

- Permission check on every view (staff/admin only)
- CSRF protection via Django middleware
- File upload validation (CSV only, max size limit)
- Password hashing with `make_password()`
- No SQL injection risk (Django ORM)
- XSS protection via Django template escaping

## Testing

1. **GUI Form:**
   - Create user with valid data → success
   - Create user with duplicate username → error
   - Create user with invalid email → error
   - Create user with weak password → error
   - Non-staff user访问 → redirect

2. **CSV Import:**
   - Import valid CSV → all users created
   - Import CSV with some errors → partial import
   - Import empty CSV → error
   - Import wrong format → error
   - Import large CSV (1000 rows) → performance acceptable

3. **Permissions:**
   - Admin can access both views
   - Staff can access both views
   - Regular user → redirect
   - Anonymous user → login page
