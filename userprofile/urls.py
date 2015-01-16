from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^app/webapollo$', views.webapollo, name='webapollo'),
    url(r'^settings$', views.settings, name='settings'),
)
