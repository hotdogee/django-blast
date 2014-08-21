# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def use_new_blastdb_location(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    BlastDb = apps.get_model("blast", "BlastDb")
    for blastdb in BlastDb.objects.all():
        blastdb.fasta_file = blastdb.fasta_file.url_save.replace('blastdb/', 'blast/db/')
        blastdb.save()

class Migration(migrations.Migration):

    dependencies = [
        ('blast', '0003_auto_20140820_1618'),
    ]

    operations = [
        migrations.RunPython(use_new_blastdb_location),
    ]
