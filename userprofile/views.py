import requests, json
from datetime import datetime
from functools import wraps
from pytz import timezone
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
from webapollo.models import Species, Registration

@login_required
def get_species(request):
    content_type = ContentType.objects.get_for_model(Species)
    perms = request.user.user_permissions.filter(content_type=content_type)
    owner_set = set()
    access_set = set()
    for perm in perms:
        # example of perm.name: 'cercap_write', 'anogla_owner'
        s = perm.name.split('_', 2)[0]
        p = perm.name.split('_', 2)[1]
        if p == 'owner':
            owner_set.add(s)
        else:
            access_set.add(s)
    access_set = access_set.difference(owner_set)
    
    # generate the list of authorized species
    species_list = []
    for sname in owner_set:
        species = Species.objects.get(name=sname)
        species_list.append({'name': sname, 'full_name': species.full_name, 'is_owner': True,})
    species_list.sort(key=lambda k:k['name'])
    access_list = []
    for sname in access_set:
        species = Species.objects.get(name=sname)
        species_owners = User.objects.filter(user_permissions__codename=sname+'_owner').distinct().order_by('last_name')
        species_users = User.objects.filter(~Q(user_permissions__codename=sname+'_owner'),Q(user_permissions__codename__startswith=sname)).distinct().order_by('last_name')
        access_list.append({'name': sname, 'full_name': species.full_name, 'is_owner': False, 'owners': species_owners, 'users': species_users, })
    access_list.sort(key=lambda k:k['name'])
    species_list.extend(access_list)
    
    # generate the list of unauthorized species
    unauth_set = set()
    all_species = Species.objects.all()
    for s in all_species: 
        unauth_set.add(s.name)
    unauth_set = unauth_set.difference(owner_set)
    unauth_set = unauth_set.difference(access_set)
    unauth_list = []
    for sname in unauth_set:     
        # check applying record first
        species = Species.objects.get(name=sname)
        apply_records = Registration.objects.filter(user=request.user, species=species).order_by('-submission_time')
        if not apply_records:
            unauth_list.append({'name': sname, 'full_name': species.full_name, 'status':'New',})
        elif apply_records[0].status == 'Pending':
            unauth_list.append({'name': sname, 'full_name': species.full_name, 'status':'Pending', 'submission_time': apply_records[0].submission_time.astimezone(timezone('US/Eastern')).strftime('%b %d %Y, %H:%M %Z'),})
        elif apply_records[0].status == 'Rejected':
            unauth_list.append({'name': sname, 'full_name': species.full_name, 'status':'Rejected', 'submission_time:': apply_records[0].submission_time.astimezone(timezone('US/Eastern')).strftime('%b %d %Y, %H:%M %Z'), 'decision_comment': apply_records[0].decision_comment,})
        else:
            raise Exception('Shit happens')           
    unauth_list.sort(key=lambda k:k['name'])

    return species_list, unauth_list

@login_required
def dashboard(request):
    species_list, unauth_species_list = get_species(request)
    return render(
        request,
        'userprofile/dashboard.html', {
        'year': datetime.now().year,
        'title': 'Dashboard',
        'species_list': species_list,
    })

@login_required
def webapollo(request):
    species_list, unauth_species_list = get_species(request)
    return render(
        request,
        'userprofile/webapollo.html', {
        'year': datetime.now().year,
        'title': 'Web Apollo',
        'species_list': species_list,
        'unauth_species_list': unauth_species_list,
    })

@login_required
def webapollo_manage(request):
    return render(
        request,
        'userprofile/webapollo_manage.html', {
        'year': datetime.now().year,
        'title': 'Web Apollo Manage',
        #'species_list': species_list,
    })

def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        return HttpResponse(json.dumps({ 'invalid_request': True }), content_type='application/json')
    return wrapper

@ajax_login_required
def webapollo_apply(request):
    if request.is_ajax():
        if request.method == 'POST':
            comment = html.escape(request.POST['comment'])
            comment = comment[:300] if len(comment) > 300 else comment
            species = Species.objects.get(name=request.POST['species_name'])
            registration = Registration(user=request.user, species=species, submission_comment=comment)
            registration.save()
            return HttpResponse(json.dumps({'submission_time': registration.submission_time.astimezone(timezone('US/Eastern')).strftime('%b %d %Y, %H:%M %Z')}), content_type='application/json')
    return HttpResponse(json.dumps({ 'invalid_request': True }), content_type='application/json')

@login_required
def info_change(request):
    p = Profile.objects.get(user=request.user)
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
