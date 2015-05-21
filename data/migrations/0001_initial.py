# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Accession',
            fields=[
                ('accession', models.TextField(serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=b'Specifies which parser to use on this file', max_length=50)),
                ('name', filebrowser.fields.FileBrowseField(max_length=100, verbose_name=b'File path')),
                ('hash', models.TextField(blank=True)),
                ('processed_hash', models.TextField(blank=True)),
                ('processed_date', models.DateTimeField(auto_now_add=True)),
                ('attributes', django.contrib.postgres.fields.hstore.HStoreField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='FileRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=b'Relationship Type', max_length=50)),
                ('source', models.ForeignKey(related_name='+', to='data.File')),
                ('target', models.ForeignKey(related_name='+', to='data.File')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('index', models.PositiveIntegerField(null=True, blank=True)),
                ('text', models.TextField(blank=True)),
                ('attributes', django.contrib.postgres.fields.hstore.HStoreField(blank=True)),
                ('file', models.ForeignKey(to='data.File')),
            ],
        ),
        migrations.CreateModel(
            name='ItemRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=b'Relationship Type', max_length=50)),
                ('source', models.ForeignKey(related_name='relationships_to', to='data.Item')),
                ('target', models.ForeignKey(related_name='relationships_from', to='data.Item')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='related',
            field=models.ManyToManyField(related_name='itemrelationship_set', through='data.ItemRelationship', to='data.Item'),
        ),
        migrations.AddField(
            model_name='file',
            name='related',
            field=models.ManyToManyField(to='data.File', through='data.FileRelationship'),
        ),
        migrations.AddField(
            model_name='accession',
            name='item',
            field=models.ForeignKey(to='data.Item'),
        ),
    ]
