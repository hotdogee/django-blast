from django.conf.urls import *
urlpatterns = patterns('',
    url(r'^browse$', 'webapollo.views.manage', name="manage"),
    url(r'^user/(?P<user_id>[0-9]+)$', 'webapollo.views.user_permission', name="user_permission"),
    url(r'^(?P<species_name>[a-z]+)$', 'webapollo.views.species', name="species"),
)
