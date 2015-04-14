# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('webapollo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='species',
            name='full_name',
            field=models.CharField(default=datetime.date(2015, 1, 22), unique=True, max_length=200),
            preserve_default=False,
        ),
    ]
