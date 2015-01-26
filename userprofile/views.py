import requests
from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.views import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.core.cache import cache
from django.core.urlresolvers import reverse
from .forms import InfoChangeForm
from webapollo.models import Species

@login_required
def dashboard(request):
    content_type = ContentType.objects.get_for_model(Species)
    perms = request.user.user_permissions.all()
    species_names = set()
    for perm in perms:
        if perm.content_type == content_type:
            species_names.add(perm.name.split('_', 1)[0])
    species_list = []
    for sname in species_names:
        species = Species.objects.get(name=sname)
        species_list.append({'name': sname, 'full_name': species.full_name,})
    species_list.sort(key=lambda k:k['name'])
    return render(
        request,
        'userprofile/dashboard.html', {
        'year': datetime.now().year,
        'title': 'Dashboard',
        'species_list': species_list,
    })

@login_required
def webapollo(request):
    return render(
        request,
        'userprofile/webapollo.html', {
        'year': datetime.now().year,
        'title': 'App/Web Apollo'
    })

@login_required
def info_change(request):
    u = User.objects.get(pk=request.user.id)
    msg = ''
    if request.method == 'POST':
        form = InfoChangeForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            msg = 'Your personal info was changed.'
    else: # request.method == 'GET'
        form = InfoChangeForm(instance=u)

    return render(
        request,
        'userprofile/info_change.html', {
        'year': datetime.now().year,
        'title': 'Change Personal Info',
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
