# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-01 02:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20170531_1241'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailuser',
            old_name='organisation_name',
            new_name='organisation',
        ),
    ]