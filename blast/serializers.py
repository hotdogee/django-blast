from rest_framework import serializers
from .models import Organism, SequenceType, BlastDb, Sequence

class OrganismSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='organism-detail', lookup_field='short_name')

    class Meta:
        model = Organism

class SequenceTypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='sequencetype-detail', lookup_field='dataset_type')

    class Meta:
        model = SequenceType

class BlastDbSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blastdb-detail', lookup_field='title')
    organism = serializers.HyperlinkedRelatedField(view_name='organism-detail', lookup_field='short_name')
    type = serializers.HyperlinkedRelatedField(view_name='sequencetype-detail', lookup_field='dataset_type')
    fasta_file_exists = serializers.Field()
    blast_db_files_exists = serializers.Field()
    sequence_set_exists = serializers.Field()
    db_ready = serializers.Field()

    class Meta:
        model = BlastDb
        fields = ('url', 'organism', 'type', 'fasta_file', 'title', 'description', 'is_shown', 'fasta_file_exists', 'blast_db_files_exists', 'sequence_set_exists', 'db_ready', )

class SequenceSerializer(serializers.HyperlinkedModelSerializer):
    blast_db = serializers.HyperlinkedRelatedField(view_name='blastdb-detail', lookup_field='title')
    fasta_seq = serializers.Field()

    class Meta:
        model = Sequence
        fields = ('blast_db', 'id', 'length', 'seq_start_pos', 'seq_end_pos', 'modified_date', 'fasta_seq', )