# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-15 06:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wl_main', '0008_wildlifelicence_additional_information'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='wildlifelicence',
            name='regions',
            field=models.ManyToManyField(blank=True, to='wl_main.Region'),
        ),
    ]
