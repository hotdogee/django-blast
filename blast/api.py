from rest_framework import renderers

class FASTARenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'fasta'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)


from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
#from rest_framework.response import Response
#from rest_framework.views import APIView

#class UserCountView(APIView):
#    """
#    A view that returns the count of active users, in JSON or YAML.
#    """
#    renderer_classes = (JSONRenderer, YAMLRenderer)

#    def get(self, request, format=None):
#        user_count = User.objects.filter(active=True).count()
#        content = {'user_count': user_count}
#        return Response(content)


from rest_framework import viewsets
from .models import Sequence
from .serializers import SequenceSerializer

class SequenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A ViewSet for retrieving fasta sequences.
    """
    queryset = Sequence.objects.all()
    serializer_class = SequenceSerializer
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    lookup_field = 'id'
    lookup_value_regex = '[^/]+'