from datetime import datetime
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from . import views
from app.forms import BootstrapAuthenticationForm
from app.forms import BootStrapPasswordChangeForm

#urlpatterns = patterns('',
#    url(r'^$', views.dashboard, name='dashboard'),
#)
