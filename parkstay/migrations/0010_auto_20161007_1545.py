# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-07 07:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkstay', '0009_park_district'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='park',
            unique_together=set([('name',)]),
        ),       
        migrations.RemoveField(
            model_name='park',
            name='region',
        ),
        migrations.AddField(
            model_name='campground',
            name='ratis_id',
            field=models.IntegerField(default=-1),
        ),


    ]