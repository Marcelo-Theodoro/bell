# Generated by Django 2.2 on 2019-07-22 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Report",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("subscriber", models.CharField(db_index=True, max_length=11)),
                ("destination", models.CharField(max_length=11)),
                ("call_started_at", models.DateTimeField()),
                ("call_ended_at", models.DateTimeField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        )
    ]