# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='name',
            field=filebrowser.fields.FileBrowseField(max_length=100, verbose_name=b'File path'),
        ),
    ]
