# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-07 11:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_auto_20171107_1719'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='staff',
            options={},
        ),
        migrations.AlterModelManagers(
            name='staff',
            managers=[
            ],
        ),
        migrations.RemoveField(
            model_name='staff',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='email',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='is_staff',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='is_superuser',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='password',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='user_permissions',
        ),
        migrations.RemoveField(
            model_name='staff',
            name='username',
        ),
        migrations.AlterField(
            model_name='bookingrecord',
            name='cause',
            field=models.TextField(null=True, verbose_name='预定事由'),
        ),
        migrations.AlterField(
            model_name='bookingrecord',
            name='proposer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app01.Staff', verbose_name='预定人'),
        ),
    ]