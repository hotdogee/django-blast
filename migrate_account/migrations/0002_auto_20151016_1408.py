# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blast', '0006_auto_20150410_1038'),
        ('migrate_account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User_account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=300)),
                ('password', models.CharField(max_length=70)),
                ('sub_date', models.DateTimeField(verbose_name=b'date submitted')),
                ('organism', models.ForeignKey(default=0, to='blast.Organism')),
            ],
        ),
        migrations.DeleteModel(
            name='Input',
        ),
    ]
