# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-01 02:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0005_proposaltype_site'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposaltype',
            name='site',
            field=models.OneToOneField(default='1', on_delete=django.db.models.deletion.CASCADE, to='sites.Site'),
        ),
    ]