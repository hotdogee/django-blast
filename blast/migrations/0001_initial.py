# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlastDb',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fasta_file', filebrowser.fields.FileBrowseField(max_length=100, verbose_name=b'FASTA file path')),
                ('title', models.CharField(help_text=b'This is passed into makeblast -title', unique=True, max_length=200)),
                ('description', models.TextField(blank=True)),
                ('is_shown', models.BooleanField(default=None, help_text=b'Display this database in the BLAST submit form')),
            ],
            options={
                'verbose_name': b'BLAST database',
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
                ('result_status', models.CharField(default=b'WAITING', max_length=32)),
            ],
            options={
                'verbose_name': b'BLAST result',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='JbrowseSetting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(help_text=b'The URL to Jbrowse using this reference', unique=True, verbose_name=b'Jbrowse URL')),
                ('blast_db', models.OneToOneField(verbose_name=b'reference', to='blast.BlastDb', help_text=b'The BLAST database used as the reference in Jbrowse')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('display_name', models.CharField(help_text=b'Scientific or common name', unique=True, max_length=200)),
                ('short_name', models.CharField(help_text=b'This is used for file names and variable names in code', unique=True, max_length=20)),
                ('description', models.TextField(blank=True)),
                ('tax_id', models.PositiveIntegerField(help_text=b'This is passed into makeblast', null=True, verbose_name=b'NCBI Taxonomy ID', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='blastdb',
            name='organism',
            field=models.ForeignKey(to='blast.Organism'),
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
                ('blast_db', models.ForeignKey(verbose_name=b'BLAST DB', to='blast.BlastDb')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='sequence',
            unique_together=set([(b'blast_db', b'id')]),
        ),
        migrations.CreateModel(
            name='SequenceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('molecule_type', models.CharField(default=b'nucl', max_length=4, choices=[(b'nucl', b'Nucleotide'), (b'prot', b'Peptide')])),
                ('dataset_type', models.CharField(unique=True, max_length=50)),
            ],
            options={
                'verbose_name': b'sequence type',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='blastdb',
            name='type',
            field=models.ForeignKey(to='blast.SequenceType'),
            preserve_default=True,
        ),
    ]
