# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-21 06:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0023_auto_20170721_1318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proposalrequirement',
            name='order',
        ),
    ]
