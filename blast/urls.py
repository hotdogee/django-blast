from django.conf.urls import patterns, url, include
from blast import views
from .api import *
from rest_framework import routers, serializers, viewsets
#from .serializers import UserSerializer

router = routers.DefaultRouter()
router.register(r'organism', OrganismViewSet)
router.register(r'seqtype', SequenceTypeViewSet)
router.register(r'blastdb', BlastDbViewSet)
router.register(r'seq', SequenceViewSet)
router.register(r'task', BlastQueryRecordViewSet)
router.register(r'user', UserViewSet)

urlpatterns = patterns('',
    # ex: /blast/
    url(r'^$', views.create, name='create'),
    #url(r'^iframe$', views.create, {'iframe': True}, name='iframe'),
    # ex: /blast/5/
    url(r'^(?P<task_id>[0-9a-zA-Z]+)$', views.retrieve, name='retrieve'),
    url(r'^(?P<task_id>[0-9a-zA-Z]+)/status$', views.status, name='status'),
    #url(r'^read_gff3/(?P<task_id>[0-9a-fA-F]*)/*(?P<dbname>[\w\-\|.]*)/*$', views.read_gff3, name='read_gff3'),
    url(r'^api/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^api-docs/', include('rest_framework_swagger.urls')),
    url('^user-tasks/(?P<user_id>[0-9]+)$', views.user_tasks),
)
