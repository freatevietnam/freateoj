from django.contrib.auth.models import Group
from django.db import migrations


def create_org_admin_group(apps, schema_editor):
    Group.objects.get_or_create(name='Org Admin')


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0229_fix_asia_saigon_timezone'),
        ('auth', '__first__'),
    ]

    operations = [
        migrations.RunPython(create_org_admin_group, migrations.RunPython.noop),
    ]
