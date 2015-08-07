# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blast', '0006_auto_20150410_1038'),
    ]

    operations = [
        migrations.CreateModel(
            name='HmmerDB',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fasta_file', filebrowser.fields.FileBrowseField(default=b'', max_length=100, verbose_name=b'FASTA file path')),
                ('title', models.CharField(default=b'', help_text=b'This is passed into makeblast -title', unique=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('is_shown', models.BooleanField(default=None, help_text=b'Display this database in the BLAST submit form')),
                ('organism', models.ForeignKey(default=0, to='blast.Organism')),
            ],
        ),
        migrations.CreateModel(
            name='HmmerQueryRecord',
            fields=[
                ('task_id', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('enqueue_date', models.DateTimeField(auto_now_add=True)),
                ('dequeue_date', models.DateTimeField(null=True)),
                ('result_date', models.DateTimeField(null=True)),
                ('result_status', models.CharField(default=b'WAITING', max_length=32)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
