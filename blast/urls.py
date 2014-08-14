from django.conf.urls import patterns, url
from blast import views

urlpatterns = patterns('',
    # ex: /blast/
    url(r'^$', views.create, name='create'),
    url(r'^iframe$', views.create, {'iframe': True}, name='create'),
    # ex: /blast/5/
    url(r'^(?P<task_id>[0-9a-fA-F]+)/$', views.retrieve, name='retrieve'),
    url(r'^read_gff3/(?P<task_id>[0-9a-fA-F]*)/*(?P<dbname>[\w\-\|.]*)/*$', views.read_gff3, name='read_gff3'),
)