from rest_framework import serializers
#from rest_framework.pagination import PaginationSerializer
from django.contrib.auth.models import User
from .models import Organism, SequenceType, BlastDb, Sequence, BlastQueryRecord

class OrganismSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:organism-detail', lookup_field='short_name')

    class Meta:
        model = Organism

class SequenceTypeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:sequencetype-detail', lookup_field='dataset_type')

    class Meta:
        model = SequenceType

class BlastDbSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:blastdb-detail', lookup_field='title')
    organism = serializers.HyperlinkedRelatedField(view_name='blast:organism-detail', lookup_field='short_name', read_only=True)
    type = serializers.HyperlinkedRelatedField(view_name='blast:sequencetype-detail', lookup_field='dataset_type', read_only=True)
    sequence_set = serializers.HyperlinkedRelatedField(view_name='blast:blastdb-sequence-set', lookup_field='title', read_only=True)
    fasta_file_exists = serializers.Field()
    blast_db_files_exists = serializers.Field()
    sequence_set_exists = serializers.Field()
    db_ready = serializers.Field()

    class Meta:
        model = BlastDb
        fields = ('url', 'organism', 'type', 'fasta_file', 'title', 'description', 'is_shown', 'fasta_file_exists', 'blast_db_files_exists', 'sequence_set_exists', 'db_ready', 'sequence_set', )

class SequenceSerializer(serializers.HyperlinkedModelSerializer):
    blast_db = serializers.HyperlinkedRelatedField(view_name='blast:blastdb-detail', lookup_field='title', read_only=True)
    fasta_seq = serializers.Field()

    class Meta:
        model = Sequence
        fields = ('blast_db', 'id', 'length', 'seq_start_pos', 'seq_end_pos', 'modified_date', 'fasta_seq', )

#class PaginatedSequenceSerializer(PaginationSerializer):
    #class Meta:
        #object_serializer_class = SequenceSerializer

class BlastQueryRecordSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:blastqueryrecord-detail', lookup_field='task_id')

    class Meta:
        model = BlastQueryRecord

class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blast:user-detail', lookup_field='pk')
    class Meta:
        model = User
        fields = ('id','url',)


class UserBlastQueryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlastQueryRecord
        fields = ('task_id', 'enqueue_date', 'result_status')
