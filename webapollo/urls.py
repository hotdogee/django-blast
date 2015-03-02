from django.conf.urls import *
urlpatterns = patterns('',
    url(r'^$', 'webapollo.views.manage', name="manage"),
    url(r'^(?P<species_name>[a-z]+)$', 'webapollo.views.species', name="species"),
)
