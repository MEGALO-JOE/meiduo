# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2019-04-12 06:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0003_auto_20190408_2243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauthqquser',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='oauthqquser',
            name='update_time',
            field=models.DateTimeField(auto_now=True, verbose_name='修改时间'),
        ),
    ]
