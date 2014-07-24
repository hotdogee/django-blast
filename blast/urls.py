from django.conf.urls import patterns, url

from blast import views

urlpatterns = patterns('',
    # ex: /blast/
    url(r'^$', views.create, name='create'),
    # ex: /blast/5/
    url(r'^(?P<task_id>[0-9a-fA-F]+)/$', views.retrieve, name='retrieve'),
)