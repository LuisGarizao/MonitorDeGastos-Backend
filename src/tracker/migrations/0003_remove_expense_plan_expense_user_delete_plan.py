import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0002_rename_plan_id_expense_plan_rename_user_id_plan_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="expense",
            name="plan",
        ),
        migrations.AddField(
            model_name="expense",
            name="user",
            field=models.ForeignKey(
                db_column="user_id",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.DeleteModel(
            name="Plan",
        ),
    ]

