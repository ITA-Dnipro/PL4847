from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_passwordresetlifecycle_passwordresetauditevent"),
        ("users", "0004_alter_user_options_user_unique_lower_email"),
    ]

    operations = []
