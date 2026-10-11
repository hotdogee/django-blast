from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path, reverse_lazy
from django.views.generic import RedirectView
from django.views.static import serve

from app import views as app_views
from app.forms import BootstrapAuthenticationForm, BootStrapPasswordChangeForm, BootStrapPasswordResetForm, BootStrapSetPasswordForm
from dashboard import views as dashboard_views

admin.site.site_header = 'i5k Admin'
admin.site.site_title = 'i5k Admin'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='blast:create', permanent=False)),
    path('home', dashboard_views.dashboard, name='dashboard'),
    re_path(r'^about', app_views.about, name='about'),
    path('', include('social_django.urls', namespace='social')),
    # Uncomment the admin/doc line below to enable admin documentation:
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('captcha/', include('captcha.urls')),
    path('proxy/', include('proxy.urls', namespace='proxy')),
    path('webapollo/', include('webapollo.urls', namespace='webapollo')),

    # user authentication
    path('set_institution', app_views.set_institution, name='set_institution'),
    path('info_change', app_views.info_change, name='info_change'),
    path('register', app_views.register, name='register'),
    path('login/',
        auth_views.LoginView.as_view(
            template_name='app/login.html',
            authentication_form=BootstrapAuthenticationForm,
            extra_context={'title': 'Log in'},
        ),
        name='login'),
    path('logout', app_views.logout_all, name='logout'),
    path('password_reset',
        auth_views.PasswordResetView.as_view(
            template_name='app/password_reset.html',
            form_class=BootStrapPasswordResetForm,
            extra_context={'title': 'Password reset'},
        ),
        name='password_reset'),
    path('password_reset_done',
        auth_views.PasswordResetDoneView.as_view(
            template_name='app/password_reset_done.html',
            extra_context={'title': 'Password reset sent'},
        ),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='app/password_reset_confirm.html',
            form_class=BootStrapSetPasswordForm,
        ),
        name='password_reset_confirm'),
    path('reset_complete',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='app/password_reset_complete.html',
            extra_context={'title': 'Password reset complete'},
        ),
        name='password_reset_complete'),
    path('password_change_done',
        auth_views.PasswordChangeDoneView.as_view(
            template_name='app/password_change_done.html',
            extra_context={'title': 'Password changed'},
        ),
        name='password_change_done'),
    path('password_change',
        app_views.PasswordChangeView.as_view(
            template_name='app/password_change.html',
            form_class=BootStrapPasswordChangeForm,
            success_url=reverse_lazy('password_change_done'),
            extra_context={'title': 'Change password'},
        ),
        name='password_change'),

    path('admin/', admin.site.urls),

    # BLAST
    path('blast/', include('blast.urls', namespace='blast')),
    # Data
    path('data/', include('data.urls', namespace='data')),
]

if settings.SERVE_MEDIA:
    urlpatterns += [
        re_path(r'^%s(?P<path>.*)$' % settings.MEDIA_URL.lstrip('/'), serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]
