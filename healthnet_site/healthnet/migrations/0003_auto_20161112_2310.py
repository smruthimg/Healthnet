# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-11-12 23:10
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('healthnet', '0002_auto_20161112_1604'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='recipient',
        ),
        migrations.RemoveField(
            model_name='message',
            name='sender',
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]