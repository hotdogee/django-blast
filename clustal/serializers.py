from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ClustalQueryRecord

class UserSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail', lookup_field='pk')
    class Meta:
        model = User
        fields = ('id',)

class UserClustalQueryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClustalQueryRecord
        fields = ('task_id', 'enqueue_date', 'result_status')
