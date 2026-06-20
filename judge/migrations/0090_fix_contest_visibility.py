from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0089_submission_to_contest'),
    ]

    operations = [
        migrations.RunSQL("""
            UPDATE judge_contest
            SET is_private = false, is_organization_private = true
            WHERE is_private = true
        """, """
            UPDATE judge_contest
            SET is_private = is_organization_private
        """),
    ]
