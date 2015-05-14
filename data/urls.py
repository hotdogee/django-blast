from django.conf.urls import patterns, url, include
from blast import views
from .api import FileViewSet, ItemViewSet, AccessionDetail
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

router = DefaultRouter()
router.register(r'file', FileViewSet)
router.register(r'item', ItemViewSet)

urlpatterns = format_suffix_patterns('',
    url(r'^api/', include(router.urls)),
    url(r'^api/accessions/(?P<accession>.+)/$', AccessionDetail.as_view()),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),
)
