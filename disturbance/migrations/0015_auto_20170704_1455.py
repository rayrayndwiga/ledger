# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-04 06:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0014_auto_20170703_1241'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='referral',
            name='referral_email',
        ),
        migrations.RemoveField(
            model_name='referral',
            name='referral_name',
        ),
    ]