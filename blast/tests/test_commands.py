import io

from django.core.management import call_command
from django.test import TestCase

from blast.models import BlastDb

from .helpers import TempMediaMixin, requires_blast


class LoadSampleDataTest(TempMediaMixin, TestCase):
    @requires_blast
    def test_load_sample_data(self):
        out = io.StringIO()
        call_command('load_sample_data', stdout=out)
        self.assertIn('Created AGLA_new_ids.faa: 22035 sequences', out.getvalue())
        self.assertIn('Created AGLA_sample_transcripts.fna: 3 sequences', out.getvalue())
        for db in BlastDb.objects.all():
            self.assertTrue(db.db_ready(), db)
            self.assertTrue(db.blast_db_files_exists(), db)
        # running it again changes nothing
        out = io.StringIO()
        call_command('load_sample_data', stdout=out)
        self.assertIn('Checked AGLA_new_ids.faa: 22035 sequences', out.getvalue())
        self.assertContains(self.client.get('/blast/'), 'AGLA_sample_transcripts.fna')
