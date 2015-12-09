# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blast', '0006_auto_20150410_1038'),
        ('migrate_account', '0002_auto_20151016_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='MigrateUserRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=300)),
                ('password', models.CharField(max_length=70)),
                ('submission_date', models.DateTimeField(auto_now_add=True)),
                ('organism', models.ForeignKey(default=0, to='blast.Organism')),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='user_account',
            name='organism',
        ),
        migrations.DeleteModel(
            name='User_account',
        ),
    ]
