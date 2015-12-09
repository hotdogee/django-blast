# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Input',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=300)),
                ('password', models.CharField(max_length=70)),
                ('sub_date', models.DateTimeField(verbose_name=b'date submitted')),
                ('organism', models.CharField(max_length=200)),
            ],
        ),
    ]
