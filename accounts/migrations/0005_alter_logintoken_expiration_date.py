# Generated by Django 5.0.1 on 2024-04-06 20:34

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_logintoken_expiration_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="logintoken",
            name="expiration_date",
            field=models.DateTimeField(
                default=datetime.datetime(
                    2024, 4, 6, 20, 49, 25, 183869, tzinfo=datetime.timezone.utc
                )
            ),
        ),
    ]