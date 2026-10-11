import django_filters
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import renderers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import BlastDb, BlastQueryRecord, Organism, Sequence, SequenceType
from .serializers import (BlastDbSerializer, BlastQueryRecordSerializer, OrganismSerializer, SequenceSerializer,
                          SequenceTypeSerializer, UserSerializer)

# How many candidates to list when a sequence id is ambiguous
MAX_CHOICES = 50


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
            # errors, e.g. an ambiguous sequence id
            lines = [str(data['detail'])] + [str(choice['url']) for choice in data.get('choices', [])]
            return '\n'.join(lines) + '\n'
        else:
            return ''


FASTA_RENDERERS = (JSONRenderer, BrowsableAPIRenderer, FASTARenderer)


class MultipleSequencesFound(APIException):
    '''HTTP 300 Multiple Choices: the sequence id exists in more than one BLAST database (#19).'''
    status_code = status.HTTP_300_MULTIPLE_CHOICES
    default_code = 'multiple_choices'

    def __init__(self, sequences, request):
        self.detail = {
            'detail': 'Sequence id "%s" exists in %s BLAST databases. Add ?blast_db=<title> or use one of the URLs below.'
                      % (sequences[0].id, len(sequences) if len(sequences) <= MAX_CHOICES else 'more than %d' % MAX_CHOICES),
            'choices': [{
                'blast_db': sequence.blast_db.title,
                'url': reverse('blast:blastdb-sequence-detail', kwargs={'title': sequence.blast_db.title, 'seq_id': sequence.id}, request=request),
            } for sequence in sequences[:MAX_CHOICES]],
        }


class SequenceFilter(django_filters.FilterSet):
    blast_db = django_filters.CharFilter(field_name='blast_db__title', help_text='Title of the BLAST database')
    organism = django_filters.CharFilter(field_name='blast_db__organism__short_name', help_text='Short name of the organism')

    class Meta:
        model = Sequence
        fields = ['id', 'blast_db', 'organism']


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

    @extend_schema(responses=SequenceSerializer)
    @action(detail=True, url_path=r'seq/(?P<seq_id>[^/]+)', url_name='sequence-detail', renderer_classes=FASTA_RENDERERS)
    def sequence_detail(self, request, title=None, seq_id=None):
        """
        Retrieve one sequence of a BLAST database. Unlike /seq/{id}/, this is never ambiguous.
        """
        blastdb = self.get_object()
        sequence = get_object_or_404(Sequence.objects.select_related('blast_db'), blast_db=blastdb, id=seq_id)
        return Response(SequenceSerializer(sequence, context=self.get_serializer_context()).data)

@extend_schema_view(
    retrieve=extend_schema(
        description='Retrieve a sequence by id. The same id can exist in several BLAST databases: '
                    'pass `blast_db` to choose one, otherwise an ambiguous id returns HTTP 300 with the candidate URLs.',
        parameters=[OpenApiParameter('blast_db', OpenApiTypes.STR, description='Title of the BLAST database')],
        responses={200: SequenceSerializer, 300: OpenApiResponse(description='The id exists in more than one BLAST database')},
    ),
)
class SequenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve fasta sequences.
    """
    queryset = Sequence.objects.select_related('blast_db').order_by('key')
    serializer_class = SequenceSerializer
    renderer_classes = FASTA_RENDERERS
    filterset_class = SequenceFilter
    lookup_field = 'id'
    lookup_value_regex = '[^/]+'

    def get_object(self):
        # Sequence ids are only unique within a BLAST database (#19).
        queryset = self.filter_queryset(self.get_queryset()).filter(id=self.kwargs[self.lookup_field])
        matches = list(queryset[:MAX_CHOICES + 1])
        if not matches:
            raise NotFound()
        if len(matches) > 1:
            raise MultipleSequencesFound(matches, self.request)
        obj = matches[0]
        self.check_object_permissions(self.request, obj)
        return obj

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
