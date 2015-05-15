from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer
from django.contrib.auth.models import User
from .models import *

class FileSerializer(serializers.HyperlinkedModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name='file-detail', lookup_field='id')

    class Meta:
        model = File

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name='item-detail', lookup_field='id')
    #file = serializers.HyperlinkedRelatedField(view_name='file-detail', lookup_field='id')

    class Meta:
        model = Item

class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name='accession-detail', lookup_field='accession')
    #item = serializers.HyperlinkedRelatedField(view_name='item-detail', lookup_field='id')

    class Meta:
        model = Accession
        extra_kwargs = {
            'url': {'view_name': 'accession-detail', 'lookup_field': 'accession'}
        }
