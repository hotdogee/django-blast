# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blast', '0004_auto_20140821_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequence',
            name='id',
            field=models.CharField(unique=True, max_length=200),
        ),
    ]
