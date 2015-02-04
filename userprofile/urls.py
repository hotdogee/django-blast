from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^app/webapollo$', views.webapollo, name='webapollo'),
    url(r'^app/webapollo/manage$', views.webapollo_manage, name='webapollo_manage'),
    url(r'^app/webapollo/apply$', views.webapollo_apply, name='webapollo_apply'),
    url(r'^info_change$', views.info_change, name='info_change'),
)
