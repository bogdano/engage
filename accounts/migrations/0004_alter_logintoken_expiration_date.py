# Generated by Django 5.0.1 on 2024-03-10 02:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_logintoken_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logintoken',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 10, 2, 51, 48, 972029, tzinfo=datetime.timezone.utc)),
        ),
    ]