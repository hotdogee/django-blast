import os
import random
import shutil
import subprocess
import tempfile
import unittest
from functools import lru_cache

from django.conf import settings
from django.test import override_settings

from blast.models import BlastDb, Organism, SequenceType
from blast.utils import blast_bin


def random_dna(length, seed):
    rnd = random.Random(seed)
    return ''.join(rnd.choice('ACGT') for _ in range(length))


def reverse_complement(seq):
    return seq[::-1].translate(str.maketrans('ACGT', 'TGCA'))


def write_fasta(path, records, line_width=60, newline='\n'):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='') as f:
        for header, seq in records:
            f.write('>' + header + newline)
            for i in range(0, len(seq), line_width):
                f.write(seq[i:i + line_width] + newline)


@lru_cache(maxsize=None)
def blast_available():
    '''True when blastn (BLAST_BIN_DIR, PATH or the bundled copy) runs.'''
    try:
        result = subprocess.run([blast_bin('blastn'), '-version'], capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def requires_blast(test):
    '''Skip the test when BLAST+ is not available, unless BLAST_TESTS_REQUIRED
    is set (as in CI), in which case the test runs and fails.'''
    try:
        import pytest
        test = pytest.mark.blast(test)
    except ImportError:  # manage.py test without pytest installed
        pass
    if os.environ.get('BLAST_TESTS_REQUIRED'):
        return test
    return unittest.skipUnless(blast_available(), 'BLAST+ executables are not available (install ncbi-blast+ or set BLAST_BIN_DIR)')(test)


class TempMediaMixin:
    '''Give every test its own MEDIA_ROOT.'''

    def setUp(self):
        super().setUp()
        self.media_root = tempfile.mkdtemp(prefix='django-blast-media-')
        override = override_settings(MEDIA_ROOT=self.media_root.replace('\\', '/'))
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

    def media_path(self, *parts):
        return os.path.join(settings.MEDIA_ROOT, *parts)


def create_blastdb(title, records, molecule_type='nucl', dataset_type=None, organism=None, fasta_name=None, **kwargs):
    '''Write records to MEDIA_ROOT/blast/db/<fasta_name> and create the BlastDb row.'''
    if organism is None:
        organism, _ = Organism.objects.get_or_create(short_name='testor', defaults={'display_name': 'Testus organismus', 'tax_id': 9606})
    dataset_type = dataset_type or ('Transcript' if molecule_type == 'nucl' else 'Protein')
    seq_type, _ = SequenceType.objects.get_or_create(dataset_type=dataset_type, defaults={'molecule_type': molecule_type})
    fasta_name = fasta_name or title
    write_fasta(os.path.join(settings.MEDIA_ROOT, 'blast', 'db', fasta_name), records)
    kwargs.setdefault('is_shown', True)
    return BlastDb.objects.create(organism=organism, type=seq_type, fasta_file='blast/db/' + fasta_name, title=title, **kwargs)
