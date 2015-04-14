# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blast', '0005_auto_20140822_1248'),
    ]

    operations = [
        migrations.AddField(
            model_name='blastqueryrecord',
            name='is_shown',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='blastqueryrecord',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
