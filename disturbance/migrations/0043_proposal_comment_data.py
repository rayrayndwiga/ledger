# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-04 04:44
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0042_auto_20170803_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='comment_data',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
