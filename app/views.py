import requests, json
from datetime import datetime
from django.shortcuts import render, resolve_url
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import views as auth_views
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from functools import wraps
from .forms import InfoChangeForm, SetInstitutionForm, RegistrationForm
from .models import Profile
from social_django.models import UserSocialAuth

def home(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html', {
            'title': 'Home Page',
            #'year': datetime.now().year,
        })

def contact(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html', {
            'title': 'Contact',
            'message': 'National Agricultural Library',
            #'year': datetime.now().year,
        })

def about(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html', {
            'title': 'About i5k - BLAST',
            'message': 'django-blast',
            #'year': datetime.now().year,
        })

def checkOAuth(_user):
    return UserSocialAuth.objects.filter(user=_user).exists()

def is_ajax(request):
    # HttpRequest.is_ajax() was removed in Django 4.0
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return HttpResponse(json.dumps({ 'invalid_request': True }), content_type='application/json')
    return wrapper
    
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save();
            new_user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if new_user is not None:
                login(request, new_user)
            return HttpResponseRedirect(reverse('blast:create'))
    else:
        form = RegistrationForm()
    return render(request, "app/register.html", {
        'form': form,
        'title': 'Registration',
    })

class PasswordChangeView(auth_views.PasswordChangeView):
    '''Django's password change view, plus whether the user logged in with OAuth.'''
    def get_context_data(self, **kwargs):
        context = super(PasswordChangeView, self).get_context_data(**kwargs)
        context['isOAuth'] = checkOAuth(self.request.user)
        return context


@login_required
def set_institution(request):
    if request.method == 'POST':
        form = SetInstitutionForm(request.POST)
        if form.is_valid():
            p = Profile()
            p.user = request.user
            p.institution = form.cleaned_data['institution']
            p.save()
    else:
        form = SetInstitutionForm()

    try:
        p = Profile.objects.get(user=request.user)
        return HttpResponseRedirect(reverse('dashboard'))
    except ObjectDoesNotExist:
        return render(
            request,
            'app/set_institution.html', {
            'year': datetime.now().year,
            'title': 'Specify your institution',
            'form': form,
        })

@login_required
def info_change(request):
    isOAuth = checkOAuth(request.user)
    try: 
        p = Profile.objects.select_related('user').get(user=request.user)
        msg = ''
        errors = []
        if request.method == 'POST':
            if isOAuth:
                form = SetInstitutionForm(request.POST, instance=p)
            else:
                form = InfoChangeForm(request.POST, instance=p)
            if form.is_valid():
                form.save()
                if isOAuth:
                    msg = 'Your institution was updated.'
                else:
                    msg = 'Your account info was updated.'
            else:
                errors = str(form.errors)
        form = InfoChangeForm(instance=p)
        return render(
            request,
            'app/info_change.html', {
            'year': datetime.now().year,
            'title': 'Update Account Info',
            'form': form,
            'msg': msg,
            'isOAuth': isOAuth,
            'errors': errors,
        })
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('set_institution'))

@login_required
def logout_all(request):
    if apps.is_installed('webapollo'):
        from webapollo.views import logout_all_instances
        logout_all_instances(request)
    logout(request)
    return HttpResponseRedirect(reverse('login'))

