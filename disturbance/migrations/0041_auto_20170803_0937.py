# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-08-03 01:37
from __future__ import unicode_literals

import disturbance.components.proposals.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('disturbance', '0040_proposal_proposal_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalLogDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('uploaded_date', models.DateTimeField(auto_now_add=True)),
                ('_file', models.FileField(upload_to=disturbance.components.proposals.models.update_proposal_comms_log_filename)),
                ('log_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='disturbance.ProposalLogEntry')),
            ],
        ),
        migrations.RemoveField(
            model_name='communicationslogentry',
            name='documents',
        ),
    ]
