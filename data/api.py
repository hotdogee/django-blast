from rest_framework import renderers
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from django.contrib.auth.models import User
from django.http import Http404
from .models import File, Item, Accession
from .serializers import FileSerializer, ItemSerializer, AccessionSerializer

class FileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve organisms.
    """
    queryset = File.objects.all()
    serializer_class = FileSerializer
    #lookup_field = 'pk'

class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve sequence types.
    """
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    #lookup_field = 'id'

class AccessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieve sequence types.
    """
    queryset = Accession.objects.all()
    serializer_class = AccessionSerializer
    #lookup_field = 'accession'
    lookup_value_regex = '.+'

#class AccessionList(APIView):
#    """
#    List all snippets, or create a new snippet.
#    """
#    def get(self, request, format=None):
#        files = File.objects.all()
#        serializer = FileSerializer(files, many=True)
#        return Response(serializer.data)

#class AccessionDetail(APIView):
#    """
#    Retrieve, update or delete a snippet instance.
#    """
#    def get_file(self, id):
#        try:
#            return File.objects.get(id=id)
#        except File.DoesNotExist:
#            raise Http404

#    def get(self, request, accession, format=None):
#        ids = accession.split('/')
#        file = self.get_file(ids[0])
#        serializer = FileSerializer(file)
#        return Response(serializer.data)