from datetime import datetime
from django.conf.urls import patterns, include, url
from app.forms import BootstrapAuthenticationForm, BootStrapPasswordChangeForm

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.sites.models import Site
admin.autodiscover()
#admin.site.unregister(Site)

#from filebrowser.sites import site

urlpatterns = patterns('',
    # Examples:
    url(r'^home$', 'app.views.dashboard', name='dashboard'),
    #url(r'^contact$', 'app.views.contact', name='contact'),
    url(r'^about', 'app.views.about', name='about'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/filebrowser/', include('filebrowser.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls'), name='doc'),
    url(r'^proxy/', include('proxy.urls', namespace='proxy')),
    #url(r'^user/', include('userprofile.urls', namespace='userprofile')),
    url(r'^webapollo/', include('webapollo.urls', namespace='webapollo')),

    # user authentication and profilei
    url(r'^get_institution$', 'app.views.get_institution', name='get_institution'),
    url(r'^info_change$', 'app.views.info_change', name='info_change'),
    url(r'^register$', 'app.views.register', name='register'),
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
    url(r'^logout$', 'app.views.logout_all', name='logout'),
    url(r'^password_reset_done$',
        'django.contrib.auth.views.password_reset_done',
        {
            'template_name': 'app/password_change_done.html',
            'extra_context':
            {
                'title': 'Password Changed',
                'year': datetime.now().year,
            },
        },
        name='password_reset_done'),
    url(r'^password_reset$', 'django.contrib.auth.views.password_reset', name='password_reset'),
    url(r'^password_change_done$',
        'django.contrib.auth.views.password_change_done',
        {
            'template_name': 'app/password_change_done.html',
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
            'template_name': 'app/password_change.html',
            'password_change_form': BootStrapPasswordChangeForm,
            'post_change_redirect': 'password_change_done',
            'extra_context':
            {
                'title': 'Change Password',
                'year': datetime.now().year,
            },
        },
        name='password_change'),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # BLAST
    url(r'^blast/', include('blast.urls', namespace='blast')),
)
from django.conf import settings
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
    )
