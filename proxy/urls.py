from django.urls import re_path
from .views import proxy_view

app_name = 'proxy'

urlpatterns = [
    re_path(r'^(?P<url>.*)$', proxy_view, name='proxy_view'),
]
