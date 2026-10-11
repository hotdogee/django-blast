from django.db import migrations, models


def drop_unique_sequence_id(apps, schema_editor):
    """Sequence ids are only unique within a BLAST database (#19).

    Migration 0005 made Sequence.id unique, but deployments are known to have
    duplicate ids in different databases, i.e. some never had (or already
    dropped) that constraint. Look at the actual schema instead of letting
    AlterField fail on a constraint that does not exist.
    """
    Sequence = apps.get_model('blast', 'Sequence')
    old_field = Sequence._meta.get_field('id')
    new_field = models.CharField(max_length=200, db_index=True)
    new_field.set_attributes_from_name('id')
    new_field.model = Sequence
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        constraints = connection.introspection.get_constraints(cursor, Sequence._meta.db_table).values()
    on_column = [c for c in constraints if c['columns'] == [old_field.column] and not c['primary_key']]
    if any(c['unique'] for c in on_column):
        # drops the unique constraint and creates a plain index
        schema_editor.alter_field(Sequence, old_field, new_field)
    elif not any(c['index'] for c in on_column):
        unindexed = models.CharField(max_length=200)
        unindexed.set_attributes_from_name('id')
        unindexed.model = Sequence
        schema_editor.alter_field(Sequence, unindexed, new_field)


def restore_unique_sequence_id(apps, schema_editor):
    """Reverse: fails if a sequence id now exists in more than one database."""
    Sequence = apps.get_model('blast', 'Sequence')
    unique_field = Sequence._meta.get_field('id')
    indexed_field = models.CharField(max_length=200, db_index=True)
    indexed_field.set_attributes_from_name('id')
    indexed_field.model = Sequence
    schema_editor.alter_field(Sequence, indexed_field, unique_field)


class Migration(migrations.Migration):

    dependencies = [
        ('blast', '0006_auto_20150410_1038'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(drop_unique_sequence_id, restore_unique_sequence_id),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name='sequence',
                    name='id',
                    field=models.CharField(db_index=True, max_length=200),
                ),
            ],
        ),
    ]
