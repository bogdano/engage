# Generated by Django 5.0.1 on 2024-03-11 00:53

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_logintoken_used_alter_logintoken_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logintoken',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 3, 11, 1, 8, 51, 727633, tzinfo=datetime.timezone.utc)),
        ),
    ]