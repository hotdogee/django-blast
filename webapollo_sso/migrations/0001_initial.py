# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PermsRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.CharField(max_length=100)),
                ('oid', models.IntegerField()),
                ('apply_date', models.DateTimeField(auto_now_add=True)),
                ('apply_desc', models.CharField(max_length=120, blank=True)),
                ('reply_desc', models.CharField(max_length=120, blank=True)),
                ('end_date', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(max_length=20)),
                ('user_apply', models.ForeignKey(related_name='user_apply', to=settings.AUTH_USER_MODEL)),
                ('user_reply', models.ForeignKey(related_name='user_reply', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
