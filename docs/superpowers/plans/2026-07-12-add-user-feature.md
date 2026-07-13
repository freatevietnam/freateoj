# Add User Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add "Add User" buttons to `/users/` page allowing Staff/Admin to create users via GUI form or CSV import.

**Architecture:** Two new class-based views (`AddUserGUI`, `AddUserCSV`) with corresponding forms and templates. Views are permission-gated to staff/admin. CSV import uses preview-before-commit pattern.

**Tech Stack:** Django, Semantic UI, Python csv module, Django ORM (User + Profile)

## Global Constraints

- Permission: `request.user.is_staff or request.user.is_superuser` on all new views
- Login required on all new views
- Password hashing via `django.contrib.auth.hashers.make_password()`
- CSV encoding: UTF-8, max 5MB
- All templates extend `common-content.html` (consistent with user list pages)

---

## File Map

| File | Action | Purpose |
|------|--------|---------|
| `judge/forms.py` | Modify | Add `AddUserForm` class |
| `judge/views/user.py` | Modify | Add `AddUserGUI`, `AddUserCSV` views |
| `templates/user/add-user.html` | Create | GUI form template |
| `templates/user/import-user.html` | Create | CSV import template |
| `templates/user/user-list-tabs.html` | Modify | Add "Add User" tab |
| `dmoj/urls.py` | Modify | Add URL patterns |

---

### Task 1: Add `AddUserForm` to `judge/forms.py`

**Files:**
- Modify: `judge/forms.py`

**Interfaces:**
- Produces: `AddUserForm` class with fields `username`, `email`, `password`, `password_confirm`, `first_name`, `last_name`, `timezone`, `language`, `organizations`

- [ ] **Step 1: Add form class at end of `judge/forms.py`**

```python
class AddUserForm(Form):
    username = CharField(
        label=_('Username'),
        max_length=30,
        validators=[RegexValidator(r'^\w+$', _('Username must be alphanumeric or underscore'))],
    )
    email = CharField(label=_('Email'), widget=forms.EmailInput)
    password = CharField(label=_('Password'), widget=forms.PasswordInput, min_length=8)
    password_confirm = CharField(label=_('Confirm password'), widget=forms.PasswordInput)
    first_name = CharField(label=_('First name'), max_length=30, required=False)
    last_name = CharField(label=_('Last name'), max_length=150, required=False)
    timezone = CharField(label=_('Time zone'), max_length=50, required=False,
                         initial=settings.DEFAULT_USER_TIME_ZONE)
    language = forms.ModelChoiceField(label=_('Language'), queryset=Language.objects.all(),
                                      required=False)
    organizations = forms.ModelMultipleChoiceField(
        label=_('Organizations'), queryset=Organization.objects.all(), required=False,
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('Username already exists.'))
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Email already exists.'))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', _('Passwords do not match.'))
        organizations = cleaned_data.get('organizations')
        if organizations and organizations.count() > 3:
            self.add_error('organizations', _('A user can belong to at most 3 organizations.'))
        return cleaned_data
```

- [ ] **Step 2: Add imports at top of `judge/forms.py` if not present**

Check that these imports exist at the top of the file. Add any missing ones:

```python
from django.contrib.auth.hashers import make_password
```

(Note: `User`, `Language`, `Organization`, `Profile`, `settings` are already imported)

- [ ] **Step 3: Verify form loads without errors**

Run: `python /home/nomoka/site/manage.py shell -c "from judge.forms import AddUserForm; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add judge/forms.py
git commit -m "feat: add AddUserForm for user creation"
```

---

### Task 2: Add `AddUserGUI` view

**Files:**
- Modify: `judge/views/user.py`

**Interfaces:**
- Consumes: `AddUserForm` from Task 1
- Produces: `AddUserGUI` view class accessible at `/users/add/`

- [ ] **Step 1: Add imports at top of `judge/views/user.py`**

Check and add any missing imports:

```python
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from judge.forms import AddUserForm
```

(`messages` and `AddUserForm` may need to be added; `User`, `Profile`, `LoginRequiredMixin` are already imported)

- [ ] **Step 2: Add `AddUserGUI` view class before the `users` function (around line 660)**

```python
class AddUserGUI(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, _('You do not have permission to add users.'))
            return HttpResponseRedirect(reverse('user_list'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = AddUserForm()
        return render(request, 'user/add-user.html', {'form': form, 'title': _('Add User')})

    def post(self, request):
        form = AddUserForm(request.POST)
        if form.is_valid():
            user = User.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=make_password(form.cleaned_data['password']),
                first_name=form.cleaned_data.get('first_name', ''),
                last_name=form.cleaned_data.get('last_name', ''),
            )
            Profile.objects.create(user=user)
            profile = user.profile
            if form.cleaned_data.get('timezone'):
                profile.timezone = form.cleaned_data['timezone']
            if form.cleaned_data.get('language'):
                profile.language = form.cleaned_data['language']
            if form.cleaned_data.get('organizations'):
                profile.organizations.set(form.cleaned_data['organizations'])
            profile.save()
            messages.success(request, _('User %s created successfully.') % user.username)
            return HttpResponseRedirect(reverse('user_list'))
        return render(request, 'user/add-user.html', {'form': form, 'title': _('Add User')})
```

- [ ] **Step 3: Verify view loads without import errors**

Run: `python /home/nomoka/site/manage.py shell -c "from judge.views.user import AddUserGUI; print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add judge/views/user.py
git commit -m "feat: add AddUserGUI view for single user creation"
```

---

### Task 3: Add `AddUserCSV` view

**Files:**
- Modify: `judge/views/user.py`

**Interfaces:**
- Consumes: `AddUserForm` from Task 1 (for validation logic reuse)
- Produces: `AddUserCSV` view class accessible at `/users/import/`

- [ ] **Step 1: Add csv import at top of `judge/views/user.py`**

```python
import csv
import io
```

- [ ] **Step 2: Add `AddUserCSV` view class after `AddUserGUI`**

```python
class AddUserCSV(LoginRequiredMixin, View):
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    REQUIRED_COLUMNS = {'username', 'email', 'password'}

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, _('You do not have permission to add users.'))
            return HttpResponseRedirect(reverse('user_list'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'user/import-user.html', {'title': _('Import Users')})

    def post(self, request):
        if 'confirm' in request.POST:
            return self.do_import(request)

        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, _('Please select a CSV file.'))
            return render(request, 'user/import-user.html', {'title': _('Import Users')})

        if csv_file.size > self.MAX_FILE_SIZE:
            messages.error(request, _('File size must be less than 5MB.'))
            return render(request, 'user/import-user.html', {'title': _('Import Users')})

        try:
            decoded = csv_file.read().decode('utf-8')
        except UnicodeDecodeError:
            messages.error(request, _('CSV file must be UTF-8 encoded.'))
            return render(request, 'user/import-user.html', {'title': _('Import Users')})

        reader = csv.DictReader(io.StringIO(decoded))
        if not reader.fieldnames:
            messages.error(request, _('CSV file is empty.'))
            return render(request, 'user/import-user.html', {'title': _('Import Users')})

        missing = self.REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            messages.error(request, _('CSV must have columns: %(columns)s') % {
                'columns': ', '.join(sorted(self.REQUIRED_COLUMNS)),
            })
            return render(request, 'user/import-user.html', {'title': _('Import Users')})

        rows = []
        for i, row in enumerate(reader, start=2):
            errors = []
            username = row.get('username', '').strip()
            email = row.get('email', '').strip()
            password = row.get('password', '').strip()
            fullname = row.get('fullname', '').strip()

            if not username:
                errors.append(_('Username is required.'))
            elif len(username) > 30:
                errors.append(_('Username must be at most 30 characters.'))
            elif User.objects.filter(username=username).exists():
                errors.append(_('Username already exists.'))

            if not email:
                errors.append(_('Email is required.'))
            elif User.objects.filter(email=email).exists():
                errors.append(_('Email already exists.'))

            if not password:
                errors.append(_('Password is required.'))
            elif len(password) < 8:
                errors.append(_('Password must be at least 8 characters.'))

            first_name = ''
            last_name = ''
            if fullname:
                parts = fullname.split(None, 1)
                first_name = parts[0]
                last_name = parts[1] if len(parts) > 1 else ''

            rows.append({
                'row': i,
                'username': username,
                'email': email,
                'fullname': fullname,
                'first_name': first_name,
                'last_name': last_name,
                'timezone': row.get('timezone', '').strip(),
                'language': row.get('language', '').strip(),
                'organizations': row.get('organizations', '').strip(),
                'valid': len(errors) == 0,
                'errors': errors,
            })

        valid_count = sum(1 for r in rows if r['valid'])
        error_count = len(rows) - valid_count

        request.session['csv_import_data'] = {
            'rows': rows,
            'valid_count': valid_count,
            'error_count': error_count,
        }

        return render(request, 'user/import-user.html', {
            'title': _('Import Users'),
            'preview': True,
            'rows': rows,
            'valid_count': valid_count,
            'error_count': error_count,
            'total': len(rows),
        })

    def do_import(self, request):
        data = request.session.get('csv_import_data')
        if not data:
            messages.error(request, _('No import data found. Please upload again.'))
            return HttpResponseRedirect(reverse('user_import'))

        rows = data['rows']
        created = 0
        skipped = 0

        for row in rows:
            if not row['valid']:
                skipped += 1
                continue

            try:
                with transaction.atomic():
                    user = User.objects.create(
                        username=row['username'],
                        email=row['email'],
                        password=make_password(row['password']),
                        first_name=row.get('first_name', ''),
                        last_name=row.get('last_name', ''),
                    )
                    Profile.objects.create(user=user)
                    profile = user.profile

                    tz = row.get('timezone', '')
                    if tz:
                        profile.timezone = tz

                    lang_code = row.get('language', '')
                    if lang_code:
                        try:
                            profile.language = Language.objects.get(key=lang_code)
                        except Language.DoesNotExist:
                            pass

                    org_slugs = [s.strip() for s in row.get('organizations', '').split(';') if s.strip()]
                    if org_slugs:
                        orgs = Organization.objects.filter(slug__in=org_slugs)[:3]
                        profile.organizations.set(orgs)

                    profile.save()
                    created += 1
            except Exception:
                skipped += 1

        del request.session['csv_import_data']

        if skipped > 0:
            messages.warning(request, _('Imported %(created)d users, %(skipped)d errors.') % {
                'created': created, 'skipped': skipped,
            })
        else:
            messages.success(request, _('Imported %(created)d users successfully.') % {
                'created': created,
            })
        return HttpResponseRedirect(reverse('user_list'))
```

- [ ] **Step 3: Add `transaction` import if not present**

Check that `from django.db import transaction` is at the top of `judge/views/user.py`. Add if missing.

- [ ] **Step 4: Verify view loads without import errors**

Run: `python /home/nomoka/site/manage.py shell -c "from judge.views.user import AddUserCSV; print('OK')"`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add judge/views/user.py
git commit -m "feat: add AddUserCSV view for bulk user import"
```

---

### Task 4: Add URL patterns

**Files:**
- Modify: `dmoj/urls.py`

**Interfaces:**
- Consumes: `AddUserGUI`, `AddUserCSV` from Tasks 2-3
- Produces: URLs `/users/add/` and `/users/import/`

- [ ] **Step 1: Add URL patterns inside the `users/` include block**

In `dmoj/urls.py`, find the `path('users/', include([...` block (around line 187) and add two new paths:

```python
path('users/', include([
    path('', user.users, name='user_list'),
    path('add', user.AddUserGUI.as_view(), name='user_add'),
    path('import', user.AddUserCSV.as_view(), name='user_import'),
    path('<int:page>', lambda request, page:
         HttpResponsePermanentRedirect('%s?page=%s' % (reverse('user_list'), page))),
    path('find', user.user_ranking_redirect, name='user_ranking_redirect'),
])),
```

- [ ] **Step 2: Verify URL resolution**

Run: `python /home/nomoka/site/manage.py shell -c "from django.urls import reverse; print(reverse('user_add')); print(reverse('user_import'))"`
Expected:
```
/users/add/
/users/import/
```

- [ ] **Step 3: Commit**

```bash
git add dmoj/urls.py
git commit -m "feat: add URL patterns for user add and import"
```

---

### Task 5: Create `add-user.html` template

**Files:**
- Create: `templates/user/add-user.html`

**Interfaces:**
- Consumes: `AddUserForm` from Task 1
- Produces: Rendered HTML form

- [ ] **Step 1: Create template file**

```html
{% extends "common-content.html" %}

{% block title_row %}
    <div class="tabs">
        <h2>{{ _('Add User') }}</h2>
        <ul>
            <li class="tab"><a href="{{ url('user_list') }}"><i class="tab-icon fa fa-users"></i> {{ _('Leaderboard') }}</a></li>
            <li class="tab active"><i class="tab-icon fa fa-plus"></i> {{ _('Add User') }}</li>
        </ul>
    </div>
{% endblock %}

{% block body %}
    <div id="common-content">
        <div id="content-left" class="split-common-content">
            <div class="content-description screen">
                <form method="post" action="{{ url('user_add') }}">
                    {% csrf_token %}

                    {% for field in form %}
                        <div class="form-field" style="margin-bottom: 1em;">
                            <label for="{{ field.id_for_label }}" style="font-weight: bold;">
                                {{ field.label }}
                                {% if field.field.required %}<span style="color: red;">*</span>{% endif %}
                            </label>
                            {{ field }}
                            {% if field.errors %}
                                <div class="ui red pointing label">{{ field.errors.0 }}</div>
                            {% endif %}
                            {% if field.help_text %}
                                <div class="ui pointing grey label">{{ field.help_text }}</div>
                            {% endif %}
                        </div>
                    {% endfor %}

                    <div style="margin-top: 1.5em;">
                        <button type="submit" class="ui primary button">{{ _('Add User') }}</button>
                        <a href="{{ url('user_list') }}" class="ui button">{{ _('Cancel') }}</a>
                    </div>
                </form>
            </div>
        </div>
    </div>
{% endblock %}
```

- [ ] **Step 2: Verify template renders without errors**

Run: `python /home/nomoka/site/manage.py shell -c "from django.template.loader import get_template; get_template('user/add-user.html'); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add templates/user/add-user.html
git commit -m "feat: add user creation form template"
```

---

### Task 6: Create `import-user.html` template

**Files:**
- Create: `templates/user/import-user.html`

**Interfaces:**
- Consumes: CSV data from `AddUserCSV` view
- Produces: Upload form, preview table, import results

- [ ] **Step 1: Create template file**

```html
{% extends "common-content.html" %}

{% block title_row %}
    <div class="tabs">
        <h2>{{ _('Import Users') }}</h2>
        <ul>
            <li class="tab"><a href="{{ url('user_list') }}"><i class="tab-icon fa fa-users"></i> {{ _('Leaderboard') }}</a></li>
            <li class="tab active"><i class="tab-icon fa fa-upload"></i> {{ _('Import CSV') }}</li>
        </ul>
    </div>
{% endblock %}

{% block body %}
    <div id="common-content">
        <div id="content-left" class="split-common-content">
            <div class="content-description screen">

                {% if messages %}
                    {% for message in messages %}
                        <div class="ui {{ 'green' if message.tags == 'success' else 'red' if message.tags == 'error' else 'yellow' if message.tags == 'warning' else 'blue' }} message">
                            {{ message }}
                        </div>
                    {% endfor %}
                {% endif %}

                {% if not preview %}
                    {# Upload form #}
                    <p>{{ _('Upload a CSV file with the following columns:') }}</p>
                    <table class="ui celled table" style="margin-bottom: 1em;">
                        <thead>
                            <tr>
                                <th>{{ _('Column') }}</th>
                                <th>{{ _('Required') }}</th>
                                <th>{{ _('Description') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><td>username</td><td><span style="color:red;">*</span></td><td>{{ _('Alphanumeric or underscore, max 30 chars, unique') }}</td></tr>
                            <tr><td>email</td><td><span style="color:red;">*</span></td><td>{{ _('Valid email, unique') }}</td></tr>
                            <tr><td>password</td><td><span style="color:red;">*</span></td><td>{{ _('Min 8 characters') }}</td></tr>
                            <tr><td>fullname</td><td></td><td>{{ _('Full name (optional)') }}</td></tr>
                            <tr><td>timezone</td><td></td><td>{{ _('Default: UTC') }}</td></tr>
                            <tr><td>language</td><td></td><td>{{ _('Language code, e.g. en, vi') }}</td></tr>
                            <tr><td>organizations</td><td></td><td>{{ _('Semicolon-separated org slugs, max 3') }}</td></tr>
                        </tbody>
                    </table>

                    <p><strong>{{ _('Example:') }}</strong></p>
                    <pre style="background: #f5f5f5; padding: 1em; border-radius: 4px;">username,email,password,fullname,timezone,language,organizations
user1,user1@example.com,pass1234,User One,Asia/Ho_Chi_Minh,en,org1;org2
user2,user2@example.com,pass5678,User Two,UTC,vi,</pre>

                    <form method="post" action="{{ url('user_import') }}" enctype="multipart/form-data" style="margin-top: 1.5em;">
                        {% csrf_token %}
                        <div class="form-field" style="margin-bottom: 1em;">
                            <label style="font-weight: bold;">{{ _('CSV File') }} <span style="color: red;">*</span></label>
                            <input type="file" name="csv_file" accept=".csv" required style="display: block; margin-top: 0.5em;">
                        </div>
                        <button type="submit" class="ui primary button">{{ _('Preview') }}</button>
                        <a href="{{ url('user_list') }}" class="ui button">{{ _('Cancel') }}</a>
                    </form>

                {% else %}
                    {# Preview table #}
                    <p>
                        {{ _('Preview: %(valid)d valid, %(error)d errors, %(total)d total')|format(valid=valid_count, error=error_count, total=total) }}
                    </p>

                    <table class="ui celled striped table" style="margin-bottom: 1em;">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>{{ _('Username') }}</th>
                                <th>{{ _('Email') }}</th>
                                <th>{{ _('Fullname') }}</th>
                                <th>{{ _('Status') }}</th>
                                <th>{{ _('Errors') }}</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in rows %}
                                <tr class="{{ 'positive' if row.valid else 'negative' }}">
                                    <td>{{ row.row }}</td>
                                    <td>{{ row.username }}</td>
                                    <td>{{ row.email }}</td>
                                    <td>{{ row.fullname }}</td>
                                    <td>
                                        {% if row.valid %}
                                            <i class="green check icon"></i> OK
                                        {% else %}
                                            <i class="red times icon"></i> {{ _('Error') }}
                                        {% endif %}
                                    </td>
                                    <td>
                                        {% if row.errors %}
                                            {{ row.errors|join(', ') }}
                                        {% endif %}
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>

                    <form method="post" action="{{ url('user_import') }}" style="margin-top: 1em;">
                        {% csrf_token %}
                        <input type="hidden" name="confirm" value="1">
                        {% if valid_count > 0 %}
                            <button type="submit" class="ui primary button">
                                {{ _('Import %(count)d users')|format(count=valid_count) }}
                            </button>
                        {% endif %}
                        <a href="{{ url('user_import') }}" class="ui button">{{ _('Cancel') }}</a>
                    </form>
                {% endif %}

            </div>
        </div>
    </div>
{% endblock %}
```

- [ ] **Step 2: Verify template renders without errors**

Run: `python /home/nomoka/site/manage.py shell -c "from django.template.loader import get_template; get_template('user/import-user.html'); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add templates/user/import-user.html
git commit -m "feat: add CSV import user template"
```

---

### Task 7: Add "Add User" tab to user list

**Files:**
- Modify: `templates/user/user-list-tabs.html`

**Interfaces:**
- Consumes: existing tab structure
- Produces: New "Add User" tab visible to staff/admin

- [ ] **Step 1: Modify `templates/user/user-list-tabs.html`**

```html
{% extends "tabs-base.html" %}

{% block tabs %}
    {{ make_tab('list', 'fa-users', url('user_list'), _('Leaderboard')) }}
    {{ make_tab('contributor', 'fa-thumbs-up', url('contributors_list'), _('Contributors')) }}
    {{ make_tab('organizations', 'fa-university', url('organization_list'), _('Organizations')) }}
    {% if request.user.is_staff or request.user.is_superuser %}
        {{ make_tab('add_user', 'fa-plus', url('user_add'), _('Add User')) }}
        {{ make_tab('import_user', 'fa-upload', url('user_import'), _('Import CSV')) }}
    {% endif %}
{% endblock %}
```

- [ ] **Step 2: Verify template renders without errors**

Run: `python /home/nomoka/site/manage.py shell -c "from django.template.loader import get_template; get_template('user/user-list-tabs.html'); print('OK')"`
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add templates/user/user-list-tabs.html
git commit -m "feat: add Add User and Import CSV tabs to user list"
```

---

### Task 8: Final integration test

**Files:** None (verification only)

- [ ] **Step 1: Run Django check**

Run: `python /home/nomoka/site/manage.py check`
Expected: No errors

- [ ] **Step 2: Run URL resolution test**

Run: `python /home/nomoka/site/manage.py shell -c "
from django.urls import reverse
print('user_add:', reverse('user_add'))
print('user_import:', reverse('user_import'))
print('user_list:', reverse('user_list'))
"`
Expected:
```
user_add: /users/add/
user_import: /users/import/
user_list: /users/
```

- [ ] **Step 3: Run existing tests (if any)**

Run: `python /home/nomoka/site/manage.py test judge --parallel 2>&1 | tail -20`
Expected: Tests pass (or no tests found)

- [ ] **Step 4: Verify collectstatic works**

Run: `source /home/nomoka/freateojsite/bin/activate && python /home/nomoka/site/manage.py collectstatic --noinput 2>&1 | tail -3`
Expected: Static files collected without errors

- [ ] **Step 5: Final commit with all changes**

```bash
git add -A
git commit -m "feat: complete Add User feature with GUI and CSV import"
```
