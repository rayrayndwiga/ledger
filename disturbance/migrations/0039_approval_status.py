# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-01 00:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0038_auto_20170731_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='approval',
            name='status',
            field=models.CharField(choices=[('current', 'Current'), ('expired', 'Expired'), ('cancelled', 'Cancelled'), ('surrendered', 'Surrendered'), ('suspended', 'Suspended')], default='current', max_length=40),
        ),
    ]
