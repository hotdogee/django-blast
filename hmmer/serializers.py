from rest_framework import serializers
from django.contrib.auth.models import User
from .models import HmmerQueryRecord

class BlastQueryRecordSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='blastqueryrecord-detail', lookup_field='task_id')

    class Meta:
        model = HmmerQueryRecord

class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='pk')
    class Meta:
        model = User
        fields = ('id',)

class UserHmmerQueryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HmmerQueryRecord
        fields = ('task_id', 'enqueue_date', 'result_status')