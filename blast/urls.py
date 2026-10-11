from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from blast import views
from .api import BlastDbViewSet, BlastQueryRecordViewSet, OrganismViewSet, SequenceTypeViewSet, SequenceViewSet, UserViewSet

app_name = 'blast'

router = DefaultRouter()
router.register(r'organism', OrganismViewSet)
router.register(r'seqtype', SequenceTypeViewSet)
router.register(r'blastdb', BlastDbViewSet)
router.register(r'seq', SequenceViewSet)
router.register(r'task', BlastQueryRecordViewSet)
router.register(r'user', UserViewSet)

urlpatterns = [
    # ex: /blast/
    path('', views.create, name='create'),
    #url(r'^iframe$', views.create, {'iframe': True}, name='iframe'),
    # ex: /blast/5/
    re_path(r'^(?P<task_id>[0-9a-zA-Z]+)$', views.retrieve, name='retrieve'),
    re_path(r'^(?P<task_id>[0-9a-zA-Z]+)/status$', views.status, name='status'),
    #url(r'^read_gff3/(?P<task_id>[0-9a-fA-F]*)/*(?P<dbname>[\w\-\|.]*)/*$', views.read_gff3, name='read_gff3'),
    # OpenAPI schema and Swagger UI (drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api-docs/', SpectacularSwaggerView.as_view(url_name='blast:api-schema'), name='api-docs'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    re_path(r'^user-tasks/(?P<user_id>[0-9]+)$', views.user_tasks),
]
