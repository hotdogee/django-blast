from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import renderers, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer

from .models import BlastDb, BlastQueryRecord, Organism, Sequence, SequenceType
from .serializers import (BlastDbSerializer, BlastQueryRecordSerializer, OrganismSerializer, SequenceSerializer,
                          SequenceTypeSerializer, UserSerializer)

class FASTARenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'fasta'
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        if isinstance(data, list):
            return ''.join([seq.get('fasta_seq', '') for seq in data])
        if not isinstance(data, dict):
            return ''
        if 'results' in data:
            return ''.join([seq.get('fasta_seq', '') for seq in data['results']])
        elif 'fasta_seq' in data:
            return data['fasta_seq']
        elif 'detail' in data:
            # errors
            return str(data['detail']) + '\n'
        else:
            return ''


FASTA_RENDERERS = (JSONRenderer, BrowsableAPIRenderer, FASTARenderer)


class OrganismViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve organisms.
    """
    queryset = Organism.objects.all().order_by('id')
    serializer_class = OrganismSerializer
    lookup_field = 'short_name'

class SequenceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve sequence types.
    """
    queryset = SequenceType.objects.all().order_by('id')
    serializer_class = SequenceTypeSerializer
    lookup_field = 'dataset_type'

class BlastDbViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve BLAST databases.
    """
    queryset = BlastDb.objects.select_related('organism', 'type').order_by('id')
    serializer_class = BlastDbSerializer
    lookup_field = 'title'
    lookup_value_regex = '[^/]+'

    @extend_schema(responses=SequenceSerializer(many=True))
    @action(detail=True, url_path='seq', url_name='sequence-set', renderer_classes=FASTA_RENDERERS)
    def sequence_set(self, request, title=None):
        """
        List the sequences of a BLAST database.
        """
        blastdb = self.get_object()
        queryset = Sequence.objects.select_related('blast_db').filter(blast_db=blastdb).order_by('key')
        page = self.paginate_queryset(queryset)
        serializer = SequenceSerializer(page, many=True, context=self.get_serializer_context())
        return self.get_paginated_response(serializer.data)

class SequenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve fasta sequences.
    """
    queryset = Sequence.objects.select_related('blast_db').order_by('key')
    serializer_class = SequenceSerializer
    renderer_classes = FASTA_RENDERERS
    lookup_field = 'id'
    lookup_value_regex = '[^/]+'

class BlastQueryRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve tasks.
    """
    queryset = BlastQueryRecord.objects.all().order_by('-enqueue_date')
    serializer_class = BlastQueryRecordSerializer
    lookup_field = 'task_id'

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve users.
    """
    queryset = User.objects.all().order_by('pk')
    serializer_class = UserSerializer
    lookup_field = 'pk'
