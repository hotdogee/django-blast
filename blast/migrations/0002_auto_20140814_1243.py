# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blast', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequence',
            name='id',
            field=models.CharField(max_length=200),
        ),
    ]
