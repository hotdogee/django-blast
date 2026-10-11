from django.core.management import call_command
from django.test import TestCase

from blast.models import Sequence

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


class SharedSequenceIdTest(TempMediaMixin, TestCase):
    '''#19: MultipleObjectsReturned from /blast/api/seq/<id>/ when two BLAST
    databases contain the same sequence id (e.g. Mdes013216-RA).'''

    def setUp(self):
        super().setUp()
        self.genome = create_blastdb('Mdes_genome.fa', [('Mdes013216-RA', 'ACGT' * 50)], dataset_type='Genome Assembly')
        self.transcripts = create_blastdb('Mdes_transcripts.fna', [('Mdes013216-RA', 'TTGG' * 40), ('Mdes007966-RA', 'GGCC' * 10)])
        for db in (self.genome, self.transcripts):
            self.assertEqual(db.index_fasta()[0], 0)  # used to fail on the unique constraint

    def test_same_id_in_two_databases(self):
        self.assertEqual(Sequence.objects.filter(id='Mdes013216-RA').count(), 2)

    def test_ambiguous_id_lists_the_choices(self):
        response = self.client.get('/blast/api/seq/Mdes013216-RA/')
        self.assertEqual(response.status_code, 300)
        data = response.json()
        self.assertIn('exists in 2 BLAST databases', data['detail'])
        self.assertEqual(sorted(c['blast_db'] for c in data['choices']), ['Mdes_genome.fa', 'Mdes_transcripts.fna'])
        for choice in data['choices']:
            self.assertEqual(self.client.get(choice['url']).json()['blast_db'].rsplit('/', 2)[-2], choice['blast_db'])
        fasta = self.client.get('/blast/api/seq/Mdes013216-RA/', {'format': 'fasta'})
        self.assertEqual(fasta.status_code, 300)
        self.assertIn('/blast/api/blastdb/Mdes_genome.fa/seq/Mdes013216-RA/', fasta.content.decode())

    def test_choose_the_database(self):
        response = self.client.get('/blast/api/seq/Mdes013216-RA/', {'blast_db': 'Mdes_transcripts.fna', 'format': 'fasta'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode().replace('\n', ''), '>Mdes013216-RA' + 'TTGG' * 40)
        response = self.client.get('/blast/api/blastdb/Mdes_genome.fa/seq/Mdes013216-RA/')
        self.assertEqual(response.json()['length'], 200)
        self.assertEqual(self.client.get('/blast/api/blastdb/Mdes_genome.fa/seq/Mdes007966-RA/').status_code, 404)
        self.assertEqual(self.client.get('/blast/api/seq/Mdes013216-RA/', {'blast_db': 'other.fa'}).status_code, 404)

    def test_unique_id_still_works_without_database(self):
        response = self.client.get('/blast/api/seq/Mdes007966-RA/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['url'].endswith('/blast/api/blastdb/Mdes_transcripts.fna/seq/Mdes007966-RA/'))

    def test_filter_sequence_list(self):
        data = self.client.get('/blast/api/seq/', {'id': 'Mdes013216-RA', 'blast_db': 'Mdes_genome.fa'}).json()
        self.assertEqual(data['count'], 1)

    def test_task_lookup_only_uses_searched_databases(self):
        from blast.tasks import lookup_subject_databases
        ids = ['Mdes013216-RA', 'Mdes007966-RA']
        self.assertEqual(lookup_subject_databases(ids, ['Mdes_genome.fa']), {'Mdes013216-RA': 'Mdes_genome.fa'})
        self.assertEqual(lookup_subject_databases(ids, ['Mdes_transcripts.fna']),
                         {'Mdes013216-RA': 'Mdes_transcripts.fna', 'Mdes007966-RA': 'Mdes_transcripts.fna'})
        # still ambiguous when both are searched: deterministic choice
        self.assertEqual(lookup_subject_databases(ids, ['Mdes_genome.fa', 'Mdes_transcripts.fna'])['Mdes013216-RA'], 'Mdes_genome.fa')
