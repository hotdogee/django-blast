from django.conf.urls import *
from . import views


urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^admin/manage$', views.manage, name="manage"),
    url(r'^admin/bulk-remind$', views.bulk_remind, name="bulk-remind"),
    url(r'^admin/user/(?P<user_id>[0-9]+)$', views.user_permission, name="user_permission"),
    url(r'^admin/species/(?P<species_name>[a-z]{6})$', views.species_user, name="species_user"),
    url(r'^apply$', views.apply, name='apply'),
    url(r'^reject$', views.reject, name='reject'),
    url(r'^bulk-reject$', views.bulk_reject, name='bulk-reject'),
    url(r'^history$', views.history, name='history'),
    url(r'^approve$', views.approve, name='approve'),
    url(r'^bulk-approve$', views.bulk_approve, name='bulk-approve'),
    url(r'^remind$', views.remind, name='remind'),
    url(r'^adduser$', views.adduser, name='adduesr'),
    url(r'^remove$', views.remove, name='remove'),
    url(r'^eligible$', views.eligible, name='eligible'),
    url(r'^(?P<species_name>[a-z]{6})$', views.species, name="species"),
)
