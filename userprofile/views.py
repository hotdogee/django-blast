import requests, json, sys
from datetime import datetime
from functools import wraps
from pytz import timezone
from django.db import connection
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Permission
from django.contrib.auth.views import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils import html
from .forms import InfoChangeForm
from .models import Profile
from webapollo.views import get_species
from webapollo.models import Species, Registration, insert_species_permission, delete_species_permission


@login_required
def dashboard(request):
    species_list, interested_species_list, unauth_species_list = get_species(request)
    return render(
        request,
        'userprofile/dashboard.html', {
        'year': datetime.now().year,
        'title': 'Dashboard',
        'species_list': species_list,
    })


@login_required
def info_change(request):
    p = Profile.objects.select_related('user').get(user=request.user)
    #u = User.objects.get(pk=request.user.id)
    msg = ''
    if request.method == 'POST':
        form = InfoChangeForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            msg = 'Your account info was changed.'
    else: # request.method == 'GET'
        form = InfoChangeForm(instance=p)

    return render(
        request,
        'userprofile/info_change.html', {
        'year': datetime.now().year,
        'title': 'Update Account Info',
        'form': form,
        'msg': msg,
    })

@login_required
def logout_all(request):
    # logout all WebApollo instances
    content_type = ContentType.objects.get_for_model(Species)
    perms = request.user.user_permissions.all()
    cookie_ids = set()
    for perm in perms:
        if perm.content_type == content_type:
            cookie_ids.add(request.user.username + '_' + perm.name.split('_', 1)[0] + '_cookie')
    if cookie_ids:
        cached_cookies = cache.get_many(list(cookie_ids)) 
        # ex. cached_cookies would be
        #   {u'blast_admin_cercap_cookie': {'JSESSIONID': 'A56B4675E09E96CB4E30EA7931080CFB'}, 
        #    u'blast_admin_anogla_cookie': {'JSESSIONID': '48725B5463EC536C053973E56CFCB3F6'}}             
        if cached_cookies:
            for cache_id, cache_value in cached_cookies.iteritems():
                sname = cache_id.split('_')[-2]
                species = Species.objects.get(name=sname)
                logout_url = species.url + '/Login?operation=logout'
                requests.post(logout_url, cookies=cache_value)
            cache.delete_many(cached_cookies.keys())
        
    logout(request)
    return HttpResponseRedirect(reverse('blast:create'))
