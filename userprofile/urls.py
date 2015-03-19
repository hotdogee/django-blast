from datetime import datetime
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from . import views
from app.forms import BootstrapAuthenticationForm
from userprofile.forms import BootStrapPasswordChangeForm

urlpatterns = patterns('',
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^get_institution$', views.get_institution, name='get_institution'),
    url(r'^info_change$', views.info_change, name='info_change'),
    url(r'^login/$',
        'django.contrib.auth.views.login',
        {
            'template_name': 'app/login.html',
            'authentication_form': BootstrapAuthenticationForm,
            'extra_context':
            {
                'title':'Log in',
                'year':datetime.now().year,
            },
        },
        name='login'),
    url(r'^logout$', 'userprofile.views.logout_all', name='logout'),
    url(r'^password_change_done$',
        'django.contrib.auth.views.password_change_done',
        {
            'template_name': 'userprofile/password_change_done.html',
            'extra_context':
            {
                'title': 'Password Changed',
                'year': datetime.now().year,
            },
        },
        name='password_change_done'),
    url(r'^password_change$',
        'django.contrib.auth.views.password_change',
        {
            'template_name': 'userprofile/password_change.html',
            'password_change_form': BootStrapPasswordChangeForm,
            'post_change_redirect': 'userprofile:password_change_done',
            'extra_context':
            {
                'title': 'Change Password',
                'year': datetime.now().year,
            },
        },
        name='password_change'),
)
