from django.db import migrations


def fix_asia_saigon(apps, schema_editor):
    Profile = apps.get_model('judge', 'Profile')
    Profile.objects.filter(timezone='Asia/Saigon').update(timezone='Asia/Ho_Chi_Minh')


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0228_email_verification'),
    ]

    operations = [
        migrations.RunPython(fix_asia_saigon, migrations.RunPython.noop),
    ]
