# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-31 04:41
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_merge_20170531_1241'),
    ]

    operations = [
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('abn', models.CharField(blank=True, max_length=50, null=True, verbose_name='ABN')),
                ('identification', models.FileField(blank=True, null=True, upload_to='uploads/%Y/%m/%d')),
            ],
        ),
        migrations.RenameField(
            model_name='emailuser',
            old_name='organisation',
            new_name='organisation_name',
        ),
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(blank=True, default='WA', max_length=255),
        ),
        migrations.AlterField(
            model_name='address',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_adresses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='organisation',
            name='billing_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='org_billing_address', to='accounts.Address'),
        ),
        migrations.AddField(
            model_name='organisation',
            name='postal_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='org_postal_address', to='accounts.Address'),
        ),
    ]