# Generated by Django 5.1.6 on 2025-03-24 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("library", "0002_reserve"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrow",
            name="scheduled_return_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
