"""Load a small demo data set: the i5k Anoplophora glabripennis proteins and a
few transcripts from example/blastdb, ready to BLAST.

    python manage.py load_sample_data

Safe to run repeatedly; databases that are up to date are left alone.
"""
import os

from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command

from blast.models import BlastDb, Organism, SequenceType

EXAMPLE_DIR = os.path.join(settings.PROJECT_ROOT, 'example', 'blastdb')
SAMPLES = [
    # (file in example/blastdb, sequence type, description)
    ('AGLA_new_ids.faa', 'Protein', 'Anoplophora glabripennis proteins (i5k, sample data)'),
    ('AGLA_sample_transcripts.fna', 'Transcript', 'Anoplophora glabripennis contig and transcripts (sample data)'),
]


class Command(BaseCommand):
    help = 'Create sample BLAST databases from example/blastdb (organisms, sequence types, makeblastdb, Sequences table).'

    def handle(self, *args, **options):
        if not SequenceType.objects.exists():
            call_command('loaddata', 'sequencetype', verbosity=0)
        if not Organism.objects.filter(short_name='anogla').exists():
            call_command('loaddata', 'organism', verbosity=0)
        organism = Organism.objects.get(short_name='anogla')
        for filename, dataset_type, description in SAMPLES:
            fasta_file = 'blast/db/sample/' + filename
            db, created = BlastDb.objects.get_or_create(title=filename, defaults={
                'organism': organism,
                'type': SequenceType.objects.get(dataset_type=dataset_type),
                'fasta_file': fasta_file,
                'description': description,
                'is_shown': True,
            })
            if not db.fasta_file_exists():
                copy_fasta(os.path.join(EXAMPLE_DIR, filename), db.fasta_file.path_full)
            if not db.blast_db_files_exists():
                returncode, error, output = db.makeblastdb()
                if returncode != 0:
                    raise CommandError('makeblastdb failed for %s: %s' % (filename, error))
            if not db.sequence_set_exists():
                returncode, error, output = db.index_fasta()
                if returncode != 0:
                    raise CommandError('Indexing %s failed: %s' % (filename, error))
            self.stdout.write('%s %s: %d sequences' % ('Created' if created else 'Checked', filename, db.sequence_set.count()))


def copy_fasta(source, target):
    '''Copy with Unix line endings (a Windows checkout may have CRLF).'''
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(source, 'rb') as src, open(target, 'wb') as dst:
        for line in src:
            dst.write(line.rstrip(b'\r\n') + b'\n')
