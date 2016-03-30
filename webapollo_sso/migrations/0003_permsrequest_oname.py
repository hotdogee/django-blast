# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapollo_sso', '0002_usermapping'),
    ]

    operations = [
        migrations.AddField(
            model_name='permsrequest',
            name='oname',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
