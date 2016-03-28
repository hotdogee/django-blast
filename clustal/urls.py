from django.conf.urls import patterns, url, include
from clustal import views
#from .api import *

urlpatterns = patterns('',
    # ex: /clustal/
    url(r'^$', views.create, name='create'),
    # ex: /clustal/5/
    url(r'^(?P<task_id>[0-9a-zA-Z]+)$', views.retrieve, name='retrieve'),
    url(r'^(?P<task_id>[0-9a-zA-Z]+)/status$', views.status, name='status'),
    #url(r'^api/', include(router.urls)),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^api-docs/', include('rest_framework_swagger.urls')),
    url('^user-tasks/(?P<user_id>[0-9]+)$', views.user_tasks),
    url(r'^manual/', views.manual, name='manual'),
)
