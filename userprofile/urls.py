from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^app/webapollo$', views.webapollo, name='webapollo'),
    url(r'^app/webapollo/manage$', views.webapollo_manage, name='webapollo_manage'),
    url(r'^app/webapollo/apply$', views.webapollo_apply, name='webapollo_apply'),
    url(r'^app/webapollo/reject$', views.webapollo_reject, name='webapollo_reject'),
    url(r'^app/webapollo/history$', views.webapollo_history, name='webapollo_history'),
    url(r'^app/webapollo/approve$', views.webapollo_approve, name='webapollo_approve'),
    url(r'^app/webapollo/adduser$', views.webapollo_adduser, name='webapollo_adduesr'),
    url(r'^app/webapollo/remove$', views.webapollo_remove, name='webapollo_remove'),
    url(r'^app/webapollo/eligible$', views.webapollo_eligible, name='webapollo_eligible'),
    url(r'^info_change$', views.info_change, name='info_change'),
)
