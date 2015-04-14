# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapollo', '0007_auto_20150205_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='decision_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
