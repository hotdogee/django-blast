from django.conf.urls import patterns, url, include
from blast import views
from .api import SequenceViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'seq', SequenceViewSet)

urlpatterns = patterns('',
    # ex: /blast/
    url(r'^$', views.create, name='create'),
    #url(r'^iframe$', views.create, {'iframe': True}, name='iframe'),
    # ex: /blast/5/
    url(r'^(?P<task_id>[0-9a-fA-F]+)$', views.retrieve, name='retrieve'),
    #url(r'^read_gff3/(?P<task_id>[0-9a-fA-F]*)/*(?P<dbname>[\w\-\|.]*)/*$', views.read_gff3, name='read_gff3'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)