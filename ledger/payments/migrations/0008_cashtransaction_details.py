# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-04 07:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0007_update_payments'),
    ]

    operations = [
        migrations.AddField(
            model_name='cashtransaction',
            name='details',
            field=models.TextField(blank=True, null=True),
        ),
    ]
