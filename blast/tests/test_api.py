from django.core.management import call_command
from django.test import TestCase

from .helpers import TempMediaMixin, create_blastdb, random_dna


class ApiTest(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.seq = random_dna(120, 7)
        self.db = create_blastdb('Agla_transcripts.fna', [('AGLA000012-RA transcript', self.seq), ('AGLA000013-RA', random_dna(80, 8))])
        self.db.index_fasta()

    def test_api_root(self):
        response = self.client.get('/blast/api/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {'organism', 'seqtype', 'blastdb', 'seq', 'task', 'user'})

    def test_blastdb_detail_has_working_links(self):
        response = self.client.get('/blast/api/blastdb/Agla_transcripts.fna/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'Agla_transcripts.fna')
        self.assertEqual(data['fasta_file'], 'blast/db/Agla_transcripts.fna')
        self.assertTrue(data['sequence_set_exists'])
        self.assertTrue(data['organism'].endswith('/blast/api/organism/testor/'))
        for link in ('url', 'organism', 'type', 'sequence_set'):
            self.assertEqual(self.client.get(data[link]).status_code, 200, link)

    def test_blastdb_sequence_set(self):
        data = self.client.get('/blast/api/blastdb/Agla_transcripts.fna/seq/').json()
        self.assertEqual(data['count'], 2)
        self.assertEqual([s['id'] for s in data['results']], ['AGLA000012-RA', 'AGLA000013-RA'])

    def test_sequence_detail_json_and_fasta(self):
        response = self.client.get('/blast/api/seq/AGLA000012-RA/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['length'], 120)
        self.assertTrue(data['fasta_seq'].startswith('>AGLA000012-RA transcript\n'))
        response = self.client.get('/blast/api/seq/AGLA000012-RA/', {'format': 'fasta'})
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
        self.assertEqual(response.content.decode().replace('\n', ''), '>AGLA000012-RA transcript' + self.seq)

    def test_sequence_list_fasta(self):
        response = self.client.get('/blast/api/seq/', {'format': 'fasta'})
        self.assertEqual(response.content.decode().count('>'), 2)

    def test_unknown_sequence(self):
        response = self.client.get('/blast/api/seq/nope/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/blast/api/seq/nope/', {'format': 'fasta'})
        self.assertEqual(response.status_code, 404)

    def test_api_is_read_only(self):
        response = self.client.post('/blast/api/organism/', {'display_name': 'x', 'short_name': 'x'})
        self.assertEqual(response.status_code, 403)
        from django.contrib.auth.models import User
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.org', 'x'))
        response = self.client.post('/blast/api/organism/', {'display_name': 'x', 'short_name': 'x'})
        self.assertEqual(response.status_code, 405)

    def test_openapi_schema_and_docs(self):
        response = self.client.get('/blast/api/schema/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'/blast/api/seq/{id}/', response.content)
        self.assertEqual(self.client.get('/blast/api-docs/').status_code, 200)

    def test_schema_generation_has_no_errors(self):
        import io
        out, err = io.StringIO(), io.StringIO()
        call_command('spectacular', '--validate', '--fail-on-warn', '--file', self.media_path('schema.yml'), stdout=out, stderr=err)
