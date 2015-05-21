from rest_framework import serializers
from .models import FileRelationship, File, ItemRelationship, Item, Accession

class FileRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileRelationship
        #fields = ('type', )

class FileSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='data:api:file-detail')
    #related = FileRelationshipSerializer(many=True, read_only=True)

    class Meta:
        model = File
        #exclude = ('url', )

class ItemRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        #fields = ('type', )

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='data:api:item-detail')
    file = serializers.HyperlinkedRelatedField(view_name='data:api:file-detail', read_only=True)
    related = ItemRelationshipSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        #exclude = ('url', )

class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='data:api:accession-detail')
    item = serializers.HyperlinkedRelatedField(view_name='data:api:item-detail', read_only=True)
    #item = ItemSerializer()

    class Meta:
        model = Accession
