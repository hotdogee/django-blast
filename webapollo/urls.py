from django.conf.urls import *
urlpatterns = patterns('',
    url(r'^$', 'webapollo.views.browse', name="browse"),
    url(r'^(?P<species>[a-z]+)$', 'webapollo.views.species', name="species"),
)
