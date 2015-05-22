from rest_framework import serializers
from .models import FileRelationship, File, ItemRelationship, Item, Accession

class FileRelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileRelationship
        #fields = ('type', )

class FileSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='data:api:file-detail')
    item_set = serializers.HyperlinkedRelatedField(view_name='data:api:item-detail', many=True, read_only=True)

    class Meta:
        model = File
        #exclude = ('url', )

class ItemRelationshipSerializer(serializers.ModelSerializer):
    item = serializers.HyperlinkedRelatedField(source='target.accession_set', view_name='data:api:accession-detail', read_only=True, many=True)

    class Meta:
        model = ItemRelationship
        fields = ('type', 'item')

class ItemSerializer(serializers.HyperlinkedModelSerializer):
    #url = serializers.HyperlinkedIdentityField(view_name='data:api:item-detail')
    file = serializers.HyperlinkedRelatedField(view_name='data:api:file-detail', read_only=True)
    related = ItemRelationshipSerializer(source='relationships_to', many=True, read_only=True)

    class Meta:
        model = Item
        exclude = ('url', )

class AccessionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='data:api:accession-detail')
    item = ItemSerializer(read_only=True)
    #item = ItemSerializer()

    class Meta:
        model = Accession
