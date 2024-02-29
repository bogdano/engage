# Generated by Django 5.0.1 on 2024-02-29 02:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('price', models.FloatField()),
                ('description', models.CharField(max_length=200)),
                ('created_at', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ItemColors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ItemSizes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('size', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Leaderboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leaderboard_name', models.CharField(max_length=200)),
                ('leaderboard_logo', models.CharField(max_length=200)),
                ('leaderboard_color', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='ItemVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='engage.itemcolors')),
                ('item_size', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='engage.itemsizes')),
                ('item_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='engage.item')),
            ],
        ),
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('address', models.CharField(max_length=200)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('event_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_at', models.DateField(auto_now_add=True)),
                ('photo', models.CharField(max_length=200)),
                ('points', models.IntegerField()),
                ('is_active', models.BooleanField(default=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('alert', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('leaderboards', models.ManyToManyField(related_name='leaderboards', to='engage.leaderboard')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('leader', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='team_leader', to=settings.AUTH_USER_MODEL)),
                ('member', models.ManyToManyField(related_name='team_member', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserInterested',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='engage.activity')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserParticipated',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_participated', models.DateField(auto_now_add=True)),
                ('activity_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='engage.activity')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]