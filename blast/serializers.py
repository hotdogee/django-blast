from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from .models import Organism, SequenceType, BlastDb, Sequence, BlastQueryRecord

class OrganismSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:organism-detail', lookup_field='short_name')

    class Meta:
        model = Organism
        fields = ('url', 'display_name', 'short_name', 'description', 'tax_id', )

class SequenceTypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:sequencetype-detail', lookup_field='dataset_type')

    class Meta:
        model = SequenceType
        fields = ('url', 'molecule_type', 'dataset_type', )

class BlastDbSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:blastdb-detail', lookup_field='title')
    organism = serializers.HyperlinkedRelatedField(view_name='blast:organism-detail', lookup_field='short_name', read_only=True)
    type = serializers.HyperlinkedRelatedField(view_name='blast:sequencetype-detail', lookup_field='dataset_type', read_only=True)
    fasta_file = serializers.CharField(read_only=True)
    sequence_set = serializers.HyperlinkedIdentityField(view_name='blast:blastdb-sequence-set', lookup_field='title')
    fasta_file_exists = serializers.BooleanField(read_only=True)
    blast_db_files_exists = serializers.BooleanField(read_only=True)
    sequence_set_exists = serializers.BooleanField(read_only=True)
    db_ready = serializers.BooleanField(read_only=True)

    class Meta:
        model = BlastDb
        fields = ('url', 'organism', 'type', 'fasta_file', 'title', 'description', 'is_shown', 'seqid_prefix', 'fasta_file_exists', 'blast_db_files_exists', 'sequence_set_exists', 'db_ready', 'sequence_set', )

class SequenceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField(help_text='Unambiguous URL of this sequence')
    blast_db = serializers.HyperlinkedRelatedField(view_name='blast:blastdb-detail', lookup_field='title', read_only=True)
    fasta_seq = serializers.CharField(read_only=True)

    class Meta:
        model = Sequence
        fields = ('url', 'blast_db', 'id', 'length', 'seq_start_pos', 'seq_end_pos', 'modified_date', 'fasta_seq', )

    @extend_schema_field(OpenApiTypes.URI)
    def get_url(self, obj):
        return reverse('blast:blastdb-sequence-detail', kwargs={'title': obj.blast_db.title, 'seq_id': obj.id}, request=self.context.get('request'))

class BlastQueryRecordSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:blastqueryrecord-detail', lookup_field='task_id')

    class Meta:
        model = BlastQueryRecord
        fields = ('url', 'task_id', 'enqueue_date', 'dequeue_date', 'result_date', 'result_status', 'is_shown', )

class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:user-detail', lookup_field='pk')
    class Meta:
        model = User
        fields = ('url', 'id',)

class UserBlastQueryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlastQueryRecord
        fields = ('task_id', 'enqueue_date', 'result_status')
