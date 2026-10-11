import json
import os
import time
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from blast.models import BlastDb, Organism, Sequence, SequenceType

from .helpers import TempMediaMixin, create_blastdb, random_dna, requires_blast, write_fasta


class NaturalKeyTest(TestCase):
    def test_natural_keys(self):
        organism = Organism.objects.create(display_name='Anoplophora glabripennis', short_name='anogla', tax_id=217634)
        seq_type = SequenceType.objects.create(molecule_type='prot', dataset_type='Protein')
        self.assertEqual(Organism.objects.get_by_natural_key('anogla'), organism)
        self.assertEqual(SequenceType.objects.get_by_natural_key('Protein'), seq_type)
        self.assertEqual(str(seq_type), 'Peptide - Protein')
        self.assertEqual(organism.natural_key(), ('anogla',))

    def test_fixtures_load(self):
        from django.core.management import call_command
        call_command('loaddata', 'sequencetype', 'organism', verbosity=0)
        self.assertEqual(SequenceType.objects.count(), 3)
        self.assertTrue(Organism.objects.filter(short_name='anogla').exists())


class IndexFastaTest(TempMediaMixin, TestCase):
    def test_index_fasta_offsets_and_records(self):
        records = [('seq1 first sequence', random_dna(130, 1)), ('seq2', random_dna(61, 2)), ('gnl|Org|seq3 desc', random_dna(5, 3))]
        db = create_blastdb('test.fa', records)
        returncode, error, output = db.index_fasta()
        self.assertEqual((returncode, error), (0, ''))
        self.assertEqual(output, '3 sequences added.')
        self.assertEqual(list(db.sequence_set.order_by('key').values_list('id', 'length')), [('seq1', 130), ('seq2', 61), ('gnl|Org|seq3', 5)])
        seq1 = db.sequence_set.get(id='seq1')
        self.assertEqual(seq1.get_header(), '>seq1 first sequence')
        self.assertEqual(seq1.get_sequence().replace('\n', ''), records[0][1])
        fasta = db.sequence_set.get(id='gnl|Org|seq3').fasta_seq()
        self.assertEqual(fasta, '>gnl|Org|seq3 desc\n%s\n' % records[2][1])
        self.assertTrue(db.sequence_set_exists())

    def test_index_fasta_with_crlf_and_blank_lines(self):
        db = create_blastdb('crlf.fa', [])
        write_fasta(db.fasta_file.path_full, [('a', 'ACGT' * 20), ('b', 'TTTT')], newline='\r\n')
        with open(db.fasta_file.path_full, 'ab') as f:
            f.write(b'\r\n\r\n>c\r\nGG\r\n')
        self.assertEqual(db.index_fasta()[0], 0)
        self.assertEqual(list(db.sequence_set.order_by('key').values_list('id', 'length')), [('a', 80), ('b', 4), ('c', 2)])
        self.assertEqual(db.sequence_set.get(id='c').fasta_seq(), '>c\nGG\n')
        self.assertEqual(db.sequence_set.get(id='b').get_sequence().strip(), 'TTTT')

    def test_missing_fasta_file(self):
        db = create_blastdb('gone.fa', [('a', 'ACGT')])
        os.remove(db.fasta_file.path_full)
        self.assertFalse(db.fasta_file_exists())
        self.assertEqual(db.index_fasta(), (1, 'FASTA file not found', ''))
        self.assertEqual(db.makeblastdb()[:2], (1, 'FASTA file not found'))
        self.assertFalse(db.db_ready())


class BlastDbFilesTest(TempMediaMixin, TestCase):
    def touch(self, path):
        with open(path, 'w'):
            pass

    def test_version_4_and_5_files(self):
        db = create_blastdb('v.fa', [('a', 'ACGT')])
        base = db.fasta_file.path_full
        self.assertFalse(db.blast_db_files_exists())
        for ext in ('nhr', 'nin', 'nsq'):  # the files every BLAST+ version writes
            self.touch(base + '.' + ext)
        self.assertTrue(db.blast_db_files_exists())

    def test_multi_volume_alias(self):
        db = create_blastdb('p.faa', [('a', 'MKV')], molecule_type='prot')
        self.touch(db.fasta_file.path_full + '.pal')
        self.assertTrue(db.blast_db_files_exists())

    def test_db_ready(self):
        db = create_blastdb('r.fa', [('a', 'ACGT')])
        for ext in ('nhr', 'nin', 'nsq'):
            self.touch(db.fasta_file.path_full + '.' + ext)
        self.assertFalse(db.db_ready())
        db.index_fasta()
        self.assertTrue(db.db_ready())


class MakeblastdbTest(TempMediaMixin, TestCase):
    @requires_blast
    def test_makeblastdb(self):
        db = create_blastdb('mk.fa', [('contig1', random_dna(500, 4)), ('contig2', random_dna(300, 5))])
        returncode, error, output = db.makeblastdb()
        self.assertEqual(returncode, 0, error)
        self.assertTrue(db.blast_db_files_exists())
        self.assertIn('mk.fa', output)

    @requires_blast
    def test_makeblastdb_reports_errors(self):
        db = create_blastdb('bad.faa', [('p1', 'MKV' * 10)], molecule_type='prot')
        with open(db.fasta_file.path_full, 'w') as f:
            f.write('this is not a FASTA file\n')
        returncode, error, output = db.makeblastdb()
        self.assertNotEqual(returncode, 0)
        self.assertTrue(error)


class SequenceStrTest(TestCase):
    def test_str(self):
        organism = Organism.objects.create(display_name='X y', short_name='xy')
        seq_type = SequenceType.objects.create(molecule_type='nucl', dataset_type='Genome Assembly')
        db = BlastDb.objects.create(organism=organism, type=seq_type, fasta_file='blast/db/x.fa', title='x.fa', is_shown=True)
        seq = Sequence.objects.create(blast_db=db, id='s1', length=1, seq_start_pos=0, seq_end_pos=4)
        self.assertEqual(str(db), 'x.fa')
        self.assertEqual(str(seq), 's1')
        self.assertEqual(db.fasta_file.path_relative, 'blast/db/x.fa')
        self.assertTrue(db.fasta_file.path_full.replace('\\', '/').endswith('blast/db/x.fa'))


class MakeblastdbLogTest(TempMediaMixin, TestCase):
    '''#8: the output of makeblastdb is saved in a log file.'''

    @requires_blast
    def test_log_is_written(self):
        db = create_blastdb('log.fa', [('contig1', random_dna(500, 6))])
        self.assertEqual(db.makeblastdb_log(), '')
        self.assertEqual(db.makeblastdb()[0], 0)
        log = db.makeblastdb_log()
        self.assertEqual(db.makeblastdb_log_path(), db.fasta_file.path_full + '.makeblastdb.log')
        lines = log.splitlines()
        self.assertIn('makeblastdb', lines[1])
        self.assertIn('-title log.fa', lines[1])
        self.assertIn('Adding sequences from FASTA', log)
        self.assertEqual(lines[-1], '# exit code 0')

    @requires_blast
    def test_failure_is_logged(self):
        db = create_blastdb('broken.faa', [('p1', 'MKV')], molecule_type='prot')
        with open(db.fasta_file.path_full, 'w') as f:
            f.write('not FASTA\n')
        returncode, error, output = db.makeblastdb()
        self.assertNotEqual(returncode, 0)
        self.assertIn('full log: ' + db.makeblastdb_log_path(), error)
        self.assertNotIn('# exit code 0', db.makeblastdb_log())

    def test_missing_executable_is_logged(self):
        db = create_blastdb('noexe.fa', [('a', 'ACGT')])
        with self.settings(BLAST_BIN_DIR=self.media_path('no-such-dir')):
            returncode, error, output = db.makeblastdb()
        self.assertEqual(returncode, 1)
        self.assertIn('Could not run makeblastdb', error)
        self.assertIn('Could not run makeblastdb', db.makeblastdb_log())

    def test_admin_shows_the_log(self):
        from django.contrib.auth.models import User
        db = create_blastdb('admin.fa', [('a', 'ACGT')])
        with open(db.makeblastdb_log_path(), 'w') as f:
            f.write('# now\nAdding sequences from FASTA; added 1 sequences\n# exit code 0\n')
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.org', 'x'))
        response = self.client.get('/admin/blast/blastdb/%d/change/' % db.pk)
        self.assertContains(response, 'Adding sequences from FASTA; added 1 sequences')


class StaleDatabaseTest(TempMediaMixin, TestCase):
    '''#15: replacing the FASTA source of a BLAST database must show that the
    database files and the Sequences table need to be rebuilt.'''

    def setUp(self):
        super().setUp()
        self.db = create_blastdb('old.fa', [('old1', random_dna(100, 41))])
        self.db.index_fasta()
        self.fake_makeblastdb(self.db)

    def fake_makeblastdb(self, db):
        for ext in ('hr', 'in', 'sq'):
            with open(db.fasta_file.path_full + '.n' + ext, 'w'):
                pass
        with open(db.makeblastdb_info_path(), 'w') as f:
            json.dump({'fingerprint': db._fingerprint()}, f)

    def test_up_to_date(self):
        self.assertTrue(self.db.blast_db_files_exists())
        self.assertTrue(self.db.sequence_set_exists())
        self.assertTrue(self.db.db_ready())

    def test_changing_the_fasta_file_clears_the_index(self):
        write_fasta(self.media_path('blast', 'db', 'new.fa'), [('new1', 'ACGT')])
        db = BlastDb.objects.get(pk=self.db.pk)
        db.fasta_file = 'blast/db/new.fa'
        db.save()
        self.assertEqual(db.sequence_set.count(), 0)
        self.assertFalse(db.blast_db_files_exists())
        self.assertFalse(db.sequence_set_exists())
        self.assertFalse(db.db_ready())
        # other changes keep the index
        db = BlastDb.objects.get(pk=self.db.pk)
        db.index_fasta()
        db.description = 'changed'
        db.save()
        self.assertEqual(db.sequence_set.count(), 1)

    def test_replacing_the_file_contents_is_detected(self):
        # the sequences were indexed a while ago, then the file was overwritten
        self.db.sequence_set.update(modified_date=timezone.now() - timedelta(minutes=5))
        write_fasta(self.db.fasta_file.path_full, [('replaced', random_dna(150, 42))])
        self.assertFalse(self.db.blast_db_files_exists())
        self.assertFalse(self.db.sequence_set_exists())
        # still searchable until it is rebuilt
        self.assertTrue(self.db.db_ready())

    def test_databases_built_elsewhere_compare_timestamps(self):
        os.remove(self.db.makeblastdb_info_path())
        self.assertTrue(self.db.blast_db_files_exists())
        past = time.time() - 3600
        for ext in ('hr', 'in', 'sq'):
            os.utime(self.db.fasta_file.path_full + '.n' + ext, (past, past))
        self.assertFalse(self.db.blast_db_files_exists())

    def test_admin_status_and_rebuild_action(self):
        from django.contrib.auth.models import User
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.org', 'x'))
        os.remove(self.db.fasta_file.path_full + '.nin')
        response = self.client.get('/admin/blast/blastdb/%d/change/' % self.db.pk)
        self.assertContains(response, 'BLAST database files up to date: <strong>no - run the &quot;Rebuild&quot; action</strong>', html=False)
        response = self.client.get('/admin/blast/blastdb/')
        self.assertContains(response, 'Rebuild: run makeblastdb and populate the Sequences table')

    @requires_blast
    def test_rebuild(self):
        write_fasta(self.db.fasta_file.path_full, [('rebuilt1', random_dna(300, 43)), ('rebuilt2', random_dna(300, 44))])
        self.assertFalse(self.db.blast_db_files_exists())
        from django.contrib.auth.models import User
        self.client.force_login(User.objects.create_superuser('admin', 'admin@example.org', 'x'))
        response = self.client.post('/admin/blast/blastdb/', {'action': 'rebuild', '_selected_action': [self.db.pk]}, follow=True)
        self.assertContains(response, '1 entries successfully rebuilt.')
        self.assertTrue(self.db.blast_db_files_exists())
        self.assertTrue(self.db.sequence_set_exists())
        self.assertEqual(sorted(self.db.sequence_set.values_list('id', flat=True)), ['rebuilt1', 'rebuilt2'])
