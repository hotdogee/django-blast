# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webapollo_sso', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('apollo_user_id', models.IntegerField(unique=True)),
                ('apollo_user_name', models.CharField(max_length=100)),
                ('apollo_user_pwd', models.CharField(max_length=50)),
                ('last_date', models.DateTimeField(auto_now=True)),
                ('django_user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
