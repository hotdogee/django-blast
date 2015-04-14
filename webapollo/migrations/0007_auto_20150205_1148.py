# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapollo', '0006_auto_20150203_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='decision_comment',
            field=models.TextField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='decision_time',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='status',
            field=models.CharField(default=b'Pending', max_length=10, choices=[(b'Pending', b'Pending'), (b'Approved', b'Approved'), (b'Rejected', b'Rejected')]),
        ),
        migrations.AlterField(
            model_name='registration',
            name='submission_comment',
            field=models.TextField(max_length=200, blank=True),
        ),
    ]
