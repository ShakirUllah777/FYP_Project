from django.db import migrations


def no_op(apps, schema_editor):
    """No default communities per user requirements."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0001_initial'),
        ('accounts', '0003_profile_resume_profile_resume_updated_at'),
    ]

    operations = [
        migrations.RunPython(no_op, no_op),
    ]

