# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-04-08 14:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0002_auto_20190407_0941'),
    ]

    operations = [
        migrations.RenameField(
            model_name='oauthqquser',
            old_name='creae_time',
            new_name='create_time',
        ),
    ]
