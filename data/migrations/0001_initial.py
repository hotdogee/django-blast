# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields.hstore
import django.contrib.postgres.operations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        django.contrib.postgres.operations.HStoreExtension(),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=b'Specifies which parser to use on this file', max_length=50)),
                ('name', models.TextField(blank=True)),
                ('hash', models.TextField(blank=True)),
                ('processed_hash', models.TextField(blank=True)),
                ('processed_date', models.DateTimeField(auto_now_add=True)),
                ('attributes', django.contrib.postgres.fields.hstore.HStoreField()),
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
                ('key', models.AutoField(serialize=False, primary_key=True)),
                ('id', models.PositiveIntegerField()),
                ('attributes', django.contrib.postgres.fields.hstore.HStoreField()),
                ('file', models.ForeignKey(to='data.File')),
            ],
        ),
        migrations.CreateModel(
            name='ItemRelationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(help_text=b'Relationship Type', max_length=50)),
                ('source', models.ForeignKey(related_name='+', to='data.Item')),
                ('target', models.ForeignKey(related_name='+', to='data.Item')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='related',
            field=models.ManyToManyField(to='data.Item', through='data.ItemRelationship'),
        ),
        migrations.AddField(
            model_name='file',
            name='related',
            field=models.ManyToManyField(to='data.File', through='data.FileRelationship'),
        ),
    ]
