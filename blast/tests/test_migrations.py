from django.db import IntegrityError, connection, models, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

BEFORE = [('blast', '0006_auto_20150410_1038')]
AFTER = [('blast', '0007_sequence_id_unique_per_database')]


class SequenceIdMigrationTest(TransactionTestCase):
    '''0007 drops the unique constraint on Sequence.id (#19), whether or not the
    database actually has it.'''

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def tearDown(self):
        self.migrate(executor_leaf_nodes())

    def id_constraints(self):
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, 'blast_sequence').values()
        return [c for c in constraints if c['columns'] == ['id'] and not c['primary_key']]

    def add_duplicate_ids(self, apps):
        Organism = apps.get_model('blast', 'Organism')
        SequenceType = apps.get_model('blast', 'SequenceType')
        BlastDb = apps.get_model('blast', 'BlastDb')
        Sequence = apps.get_model('blast', 'Sequence')
        organism = Organism.objects.create(display_name='Mayetiola destructor', short_name='maydes')
        seq_type = SequenceType.objects.create(dataset_type='Transcript')
        dbs = [BlastDb.objects.create(organism=organism, type=seq_type, fasta_file='blast/db/%d.fa' % i, title='%d.fa' % i, is_shown=True) for i in (110, 111)]
        for db in dbs:
            Sequence.objects.create(blast_db=db, id='Mdes013216-RA', length=1, seq_start_pos=0, seq_end_pos=1)

    def test_with_unique_constraint(self):
        apps = self.migrate(BEFORE)
        self.assertTrue(any(c['unique'] for c in self.id_constraints()))
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.add_duplicate_ids(apps)
        apps = self.migrate(AFTER)
        self.assertFalse(any(c['unique'] for c in self.id_constraints()))
        self.assertTrue(any(c['index'] for c in self.id_constraints()))
        self.add_duplicate_ids(apps)
        self.assertEqual(apps.get_model('blast', 'Sequence').objects.filter(id='Mdes013216-RA').count(), 2)

    def test_without_unique_constraint(self):
        # deployments with duplicate ids in production never had the constraint
        apps = self.migrate(BEFORE)
        Sequence = apps.get_model('blast', 'Sequence')
        old_field = Sequence._meta.get_field('id')
        plain = models.CharField(max_length=200)
        plain.set_attributes_from_name('id')
        plain.model = Sequence
        with connection.schema_editor() as editor:
            editor.alter_field(Sequence, old_field, plain)
        self.assertEqual(self.id_constraints(), [])
        apps = self.migrate(AFTER)
        self.assertTrue(any(c['index'] and not c['unique'] for c in self.id_constraints()))
        self.add_duplicate_ids(apps)


def executor_leaf_nodes():
    executor = MigrationExecutor(connection)
    return executor.loader.graph.leaf_nodes()
