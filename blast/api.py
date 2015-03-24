from rest_framework import renderers

class FASTARenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'fasta'

    def render(self, data, media_type=None, renderer_context=None):
        if 'results' in data:
            return ''.join([seq['fasta_seq'] for seq in data['results']])
        elif 'fasta_seq' in data:
            return data['fasta_seq']
        else:
            return ''

from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.decorators import action, link
from rest_framework.response import Response
from rest_framework import viewsets
from .models import Organism, SequenceType, BlastDb, Sequence, BlastQueryRecord
from .serializers import OrganismSerializer, SequenceTypeSerializer, BlastDbSerializer, SequenceSerializer, PaginatedSequenceSerializer, BlastQueryRecordSerializer

class OrganismViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve organisms.
    """
    queryset = Organism.objects.all()
    serializer_class = OrganismSerializer
    lookup_field = 'short_name'

class SequenceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve sequence types.
    """
    queryset = SequenceType.objects.all()
    serializer_class = SequenceTypeSerializer
    lookup_field = 'dataset_type'

class BlastDbViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve BLAST databases.
    """
    queryset = BlastDb.objects.all()
    serializer_class = BlastDbSerializer
    lookup_field = 'title'
    lookup_value_regex = '[^/]+'

    @link()
    def sequence_set(self, request, title=None):
        empty_error = "Empty list and '%(class_name)s.allow_empty' is False."
        blastdb = self.get_object()
        object_list = self.filter_queryset(blastdb.sequence_set.all())

        # Default is to allow empty querysets.  This can be altered by setting
        # `.allow_empty = False`, to raise 404 errors on empty querysets.
        if not self.allow_empty and not object_list:
            warnings.warn(
                'The `allow_empty` parameter is deprecated. '
                'To use `allow_empty=False` style behavior, You should override '
                '`get_queryset()` and explicitly raise a 404 on empty querysets.',
                DeprecationWarning
            )
            class_name = self.__class__.__name__
            error_msg = self.empty_error % {'class_name': class_name}
            raise Http404(error_msg)

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(object_list)
        if page is not None:
            serializer = PaginatedSequenceSerializer(instance=page, context={'request': request})
        else:
            serializer = SequenceSerializer(object_list, many=True, context={'request': request})

        return Response(serializer.data)

class SequenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve fasta sequences.
    """
    queryset = Sequence.objects.all()
    serializer_class = SequenceSerializer
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer, FASTARenderer)
    lookup_field = 'id'
    lookup_value_regex = '[^/]+'

class BlastQueryRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve organisms.
    """
    queryset = BlastQueryRecord.objects.all()
    serializer_class = BlastQueryRecordSerializer
    lookup_field = 'task_id'