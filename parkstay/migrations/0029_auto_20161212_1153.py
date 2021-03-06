# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-12-12 03:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0028_auto_20161208_1544'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='campground',
            name='bookable_online',
        ),
        migrations.RemoveField(
            model_name='campground',
            name='bookable_per_site',
        ),
        migrations.AlterField(
            model_name='campground',
            name='campground_type',
            field=models.SmallIntegerField(choices=[(0, 'Bookable Online'), (1, 'Not Bookable Online')], default=0),
        ),
        migrations.AlterField(
            model_name='campground',
            name='site_type',
            field=models.SmallIntegerField(choices=[(0, 'Bookable Per Site'), (1, 'Bookable Per Site Type')], default=0),
        ),
    ]
