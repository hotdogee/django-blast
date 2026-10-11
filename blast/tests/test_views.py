import json
import os
from datetime import timedelta
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from blast.models import BlastQueryRecord
from blast.views import clean_blast_option

from .helpers import TempMediaMixin, create_blastdb
from .test_e2e import BLASTN_OPTIONS


def touch_db_files(db):
    for ext in ('hr', 'in', 'sq'):
        with open(db.fasta_file.path_full + '.' + db.type.molecule_type[0] + ext, 'w'):
            pass


class CreateViewTest(TempMediaMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.db = create_blastdb('ready.fa', [('s1', 'ACGT' * 10)], description='<b>Transcripts</b>')
        touch_db_files(self.db)
        self.db.index_fasta()
        create_blastdb('not_indexed.fa', [('s1', 'ACGT')])

    def test_form_lists_ready_databases(self):
        response = self.client.get('/blast/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ready.fa')
        self.assertNotContains(response, 'not_indexed.fa')
        # JSON in the page is escaped for <script>
        self.assertContains(response, '\\u003Cb\\u003ETranscripts')

    @mock.patch('blast.views.run_blast_task.delay')
    def test_submit_queues_a_task(self, delay):
        response = self.client.post('/blast/', dict(BLASTN_OPTIONS, **{'query-sequence': '>q1\nACGTACGTAC\n>q2\nACGT', 'db-name': 'ready.fa'}))
        self.assertEqual(response.status_code, 302)
        task_id, args_list, file_prefix, blast_info = delay.call_args[0]
        self.assertEqual(response['Location'], '/blast/%s' % task_id)
        self.assertTrue(BlastQueryRecord.objects.filter(task_id=task_id, result_status='WAITING').exists())
        blastn = args_list[0]
        self.assertEqual(os.path.splitext(os.path.basename(blastn[0]))[0], 'blastn')
        self.assertIn(self.db.fasta_file.path_full, blastn)
        self.assertEqual(blastn[blastn.index('-word_size') + 1], '28')
        self.assertEqual(blastn[blastn.index('-dust') + 1], 'yes')
        with open(file_prefix + '.in') as f:
            self.assertEqual(f.read(), '>q1\nACGTACGTAC\n>q2\nACGT')
        with open(os.path.join(os.path.dirname(file_prefix), 'status.json')) as f:
            self.assertEqual(json.load(f), {'status': 'pending', 'seq_count': 2})
        self.assertEqual(self.client.get(response['Location'] + '/status').json()['status'], 'pending')

    @mock.patch('blast.views.run_blast_task.delay')
    def test_logged_in_user_is_recorded(self, delay):
        user = User.objects.create_user('alice', password='secret-password')
        self.client.force_login(user)
        self.client.post('/blast/', dict(BLASTN_OPTIONS, **{'query-sequence': 'ACGT', 'db-name': 'ready.fa'}))
        self.assertEqual(BlastQueryRecord.objects.get().user, user)

    @mock.patch('blast.views.run_blast_task.delay')
    def test_invalid_submissions(self, delay):
        cases = [
            dict(BLASTN_OPTIONS, **{'query-sequence': '', 'db-name': 'ready.fa'}),           # no query
            dict(BLASTN_OPTIONS, **{'query-sequence': 'ACGT', 'db-name': 'not_indexed.fa'}),  # database not ready
            dict(BLASTN_OPTIONS, **{'query-sequence': 'ACGT', 'db-name': 'ready.fa', 'evalue': '-out /tmp/x'}),
            dict(BLASTN_OPTIONS, **{'query-sequence': 'ACGT', 'db-name': 'ready.fa', 'strand': 'sideways'}),
        ]
        for data in cases:
            response = self.client.post('/blast/', data)
            self.assertEqual(response.status_code, 400, data)
            self.assertContains(response, 'Invalid Query', status_code=400)
        response = self.client.post('/blast/', dict(BLASTN_OPTIONS, **{'program': 'rm', 'query-sequence': 'ACGT', 'db-name': 'ready.fa'}))
        self.assertEqual(response.status_code, 404)
        delay.assert_not_called()

    def test_clean_blast_option(self):
        self.assertEqual(clean_blast_option('evalue', ' 1e-5 '), '1e-5')
        self.assertIsNone(clean_blast_option('evalue', 'abc'))
        self.assertIsNone(clean_blast_option('word_size', '1.5'))
        self.assertEqual(clean_blast_option('matrix', 'PAM30'), 'PAM30')
        self.assertIsNone(clean_blast_option('unknown', '1'))


class RetrieveViewTest(TempMediaMixin, TestCase):
    def test_unknown_task(self):
        self.assertEqual(self.client.get('/blast/0123456789abcdef0123456789abcdef').status_code, 404)

    def test_waiting_and_expired(self):
        record = BlastQueryRecord.objects.create(task_id='a' * 32)
        self.assertContains(self.client.get('/blast/' + 'a' * 32), 'Query Submitted')
        record.result_date = timezone.now() - timedelta(days=settings.BLAST_RESULT_RETENTION_DAYS + 1)
        record.result_status = 'SUCCESS'
        record.save()
        self.assertContains(self.client.get('/blast/' + 'a' * 32), 'Query Expired')

    def test_status_of_unknown_task(self):
        self.assertEqual(self.client.get('/blast/%s/status' % ('b' * 32)).json(), {'status': 'unknown'})


class UserTasksTest(TestCase):
    def test_only_the_user_and_staff_can_list_tasks(self):
        alice = User.objects.create_user('alice', password='x')
        bob = User.objects.create_user('bob', password='x')
        staff = User.objects.create_user('staff', password='x', is_staff=True)
        BlastQueryRecord.objects.create(task_id='c' * 32, user=alice)
        url = '/blast/user-tasks/%d' % alice.id
        self.assertEqual(self.client.get(url).status_code, 403)
        self.client.force_login(bob)
        self.assertEqual(self.client.get(url).status_code, 403)
        for user in (alice, staff):
            self.client.force_login(user)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual([t['task_id'] for t in response.json()], ['c' * 32])
