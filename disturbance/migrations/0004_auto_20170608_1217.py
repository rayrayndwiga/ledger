# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-08 04:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0003_organisationrequestdeclineddetails_organisationrequestuseraction'),
    ]

    operations = [
        migrations.RenameField(
            model_name='proposal',
            old_name='proposal_schema',
            new_name='schema',
        ),
    ]