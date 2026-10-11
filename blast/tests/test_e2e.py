"""End-to-end BLAST jobs: makeblastdb, submit the form, run the Celery task
eagerly, then read the results pages and files.

Skipped when the BLAST+ executables cannot be run; CI installs ncbi-blast+.
"""
import json
import os
import re

from django.conf import settings
from django.test import TestCase

from blast.models import BlastQueryRecord, JbrowseSetting

from .helpers import TempMediaMixin, create_blastdb, random_dna, requires_blast

BLASTN_OPTIONS = {
    'program': 'blastn', 'max_target_seqs': '100', 'evalue': '10.0', 'word_size': '28', 'reward': '1', 'penalty': '-2',
    'gapopen': '0', 'gapextend': '0', 'strand': 'both', 'low_complexity': 'yes', 'soft_masking': 'true',
}
BLASTP_OPTIONS = {
    'program': 'blastp', 'max_target_seqs': '100', 'evalue': '10.0', 'word_size': '3', 'matrix': 'BLOSUM62', 'threshold': '11',
    'gapopen': '11', 'gapextend': '1', 'low_complexity': 'yes', 'soft_masking': 'false',
}
PROTEIN = ('MTPKDMKTVIVDSETSDRGRVSAAGKLPADIGTDYSFKRDIVWKNALGFLALHLAAVYGLYLCSYAHTATMLWMIFVALLSGEGVTVGAHRLYSHKSFKAKFSLRLALILLQTIAG'
           'QNCLYIWVRDHRQHHKFSDTDADPHNAHRGFFFSHVGWLMSKKHPAVIEKGKTIDMSDLEADWLVMFQKE')


@requires_blast
class EndToEndTest(TempMediaMixin, TestCase):
    def submit(self, options, query, *db_titles):
        data = dict(options, **{'query-sequence': query, 'db-name': list(db_titles)})
        response = self.client.post('/blast/', data)
        self.assertEqual(response.status_code, 302, response.content[:500])
        task_id = re.match(r'^/blast/([0-9a-f]{32})$', response['Location']).group(1)
        return task_id, response['Location']

    def results(self, task_id):
        prefix = os.path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id, task_id)
        with open(prefix + '.json') as f:
            return json.load(f)

    def test_blastn_job(self):
        genome = random_dna(3000, 11)
        db = create_blastdb('test_genome.fa', [('Scaffold1 test assembly', genome), ('Scaffold2', random_dna(2000, 12))], dataset_type='Genome Assembly')
        self.assertEqual(db.makeblastdb()[0], 0)
        self.assertEqual(db.index_fasta()[0], 0)
        JbrowseSetting.objects.create(blast_db=db, url='https://jbrowse.example.org/testor/')

        # the form lists the database once it is ready
        self.assertContains(self.client.get('/blast/'), 'test_genome.fa')

        query = genome[1000:1400]
        task_id, location = self.submit(BLASTN_OPTIONS, '>query1 a piece of Scaffold1\n%s\n' % query, 'test_genome.fa')
        record = BlastQueryRecord.objects.get(task_id=task_id)
        self.assertEqual(record.result_status, 'SUCCESS')
        self.assertIsNotNone(record.dequeue_date)

        hits = self.results(task_id)
        best = hits[0]
        self.assertEqual(best[:3], ['test_genome.fa', 'query1', 'Scaffold1'])
        self.assertEqual(best[3], 100.0)  # pident
        self.assertEqual(best[7:11], [1, 400, 1001, 1400])  # qstart qend sstart send

        task_dir = os.path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id)
        for ext in ('.0', '.html', '.1', '.3', '.xml', '.tsv', '.csv', '.asn'):
            self.assertTrue(os.path.getsize(os.path.join(task_dir, task_id + ext)) > 0, ext)
        with open(os.path.join(task_dir, 'status.json')) as f:
            self.assertEqual(json.load(f), {'status': 'done'})
        with open(os.path.join(task_dir, 'info.json')) as f:
            info = json.load(f)
        self.assertEqual(info['sseqid_db'], {'Scaffold1': 'test_genome.fa'})
        self.assertEqual(info['db_url'], {'test_genome.fa': 'https://jbrowse.example.org/testor/'})
        self.assertTrue(info['line_num_list'])

        # GFF3 for JBrowse
        with open(os.path.join(task_dir, 'test_genome.fa.gff')) as f:
            gff = [line.split('\t') for line in f.read().splitlines()]
        self.assertEqual(gff[0], ['##gff-version 3'])
        self.assertEqual(gff[1][:5], ['Scaffold1', 'blastn', 'match', '1001', '1400'])

        # results page
        response = self.client.get(location)
        self.assertContains(response, 'Query Coverage Graph')
        self.assertContains(response, task_id)
        status = self.client.get(location + '/status').json()
        self.assertEqual(status['status'], 'done')
        # the downloadable files are served from MEDIA_URL
        self.assertEqual(self.client.get('/media/blast/task/%s/%s.csv' % (task_id, task_id)).status_code, 200)

    def test_blastp_job_with_file_upload(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        db = create_blastdb('test_proteins.faa', [('AGLA000002-PA', PROTEIN), ('AGLA000003-PA', 'MKV' * 40)], molecule_type='prot')
        self.assertEqual(db.makeblastdb()[0], 0)
        self.assertEqual(db.index_fasta()[0], 0)
        query = SimpleUploadedFile('query.faa', ('>q\n%s\n' % PROTEIN[20:120]).encode())
        data = dict(BLASTP_OPTIONS, **{'query-file': query, 'db-name': 'test_proteins.faa'})
        response = self.client.post('/blast/', data)
        task_id = response['Location'].rsplit('/', 1)[1]
        self.assertEqual(BlastQueryRecord.objects.get(task_id=task_id).result_status, 'SUCCESS')
        best = self.results(task_id)[0]
        self.assertEqual(best[:3], ['test_proteins.faa', 'q', 'AGLA000002-PA'])
        # no JBrowse configured: no GFF file
        self.assertFalse(os.path.exists(os.path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id, 'test_proteins.faa.gff')))

    def test_no_hits(self):
        db = create_blastdb('nohits.fa', [('Scaffold1', random_dna(2000, 21))])
        db.makeblastdb()
        db.index_fasta()
        task_id, location = self.submit(BLASTN_OPTIONS, '>q\n%s\n' % random_dna(300, 22), 'nohits.fa')
        self.assertEqual(BlastQueryRecord.objects.get(task_id=task_id).result_status, 'CSV_EMPTY')
        self.assertContains(self.client.get(location), 'No Hits Found')
