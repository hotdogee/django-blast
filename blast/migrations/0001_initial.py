# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import app.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlastDb',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fasta_file', app.fields.MediaPathField(max_length=100, verbose_name='FASTA file path')),
                ('title', models.CharField(help_text='This is passed into makeblast -title', unique=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('is_shown', models.BooleanField(default=None, help_text='Display this database in the BLAST submit form')),
            ],
            options={
                'verbose_name': 'BLAST database',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BlastQueryRecord',
            fields=[
                ('task_id', models.CharField(max_length=32, serialize=False, primary_key=True)),
                ('enqueue_date', models.DateTimeField(auto_now_add=True)),
                ('dequeue_date', models.DateTimeField(null=True)),
                ('result_date', models.DateTimeField(null=True)),
                ('result_status', models.CharField(default='WAITING', max_length=32)),
            ],
            options={
                'verbose_name': 'BLAST result',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JbrowseSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(help_text='The URL to Jbrowse using this reference', unique=True, verbose_name='Jbrowse URL')),
                ('blast_db', models.OneToOneField(verbose_name='reference', to='blast.BlastDb', help_text='The BLAST database used as the reference in Jbrowse', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(help_text='Scientific or common name', unique=True, max_length=200)),
                ('short_name', models.CharField(help_text='This is used for file names and variable names in code', unique=True, max_length=20)),
                ('description', models.TextField(blank=True)),
                ('tax_id', models.PositiveIntegerField(help_text='This is passed into makeblast', null=True, verbose_name='NCBI Taxonomy ID', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='blastdb',
            name='organism',
            field=models.ForeignKey(to='blast.Organism', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Sequence',
            fields=[
                ('key', models.AutoField(serialize=False, primary_key=True)),
                ('id', models.CharField(max_length=100)),
                ('length', models.PositiveIntegerField()),
                ('seq_start_pos', models.BigIntegerField()),
                ('seq_end_pos', models.BigIntegerField()),
                ('modified_date', models.DateTimeField(auto_now_add=True)),
                ('blast_db', models.ForeignKey(verbose_name='BLAST DB', to='blast.BlastDb', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sequence',
            unique_together=set([('blast_db', 'id')]),
        ),
        migrations.CreateModel(
            name='SequenceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('molecule_type', models.CharField(default='nucl', max_length=4, choices=[('nucl', 'Nucleotide'), ('prot', 'Peptide')])),
                ('dataset_type', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'verbose_name': 'sequence type',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='blastdb',
            name='type',
            field=models.ForeignKey(to='blast.SequenceType', on_delete=django.db.models.deletion.CASCADE),
            preserve_default=True,
        ),
    ]
