# coding: utf-8
import requests, json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.cache import cache
from .models import Species, SpeciesPassword

@csrf_exempt
@staff_member_required
def browse(request):
    if request.method == 'GET':
        users = User.objects.all()

    return render(
        request,
        'webapollo/list.html', {
            'users': users,
        }
    )

@login_required
def species(request, species_name):
    species = Species.objects.get(name=species_name)
    response = HttpResponseRedirect(species.url)
    login_url = species.url + '/Login?operation=login'
    
    spe_pwd = SpeciesPassword.objects.get(user=request.user, species=species)
    user = { 'username': request.user.username, 'password': spe_pwd.pwd }

    # store cookie value (ex. JSESSION=08D90CDE33092788F7462A969D2C398E) in memcached
    # to avoid multiple sessions when logging in WebApollo
    cache_id = request.user.username + '_' + species_name + '_cookie' # an unique cache id
    if cache.get(cache_id) is None:
        with requests.Session() as s:
            s.post(login_url, json.dumps(user))
            for cookie in s.cookies:
                if cookie.name == 'JSESSIONID':
                    response.set_cookie(cookie.name, value=cookie.value, domain='.nal.usda.gov', path='/' + species_name + '/')
                    cache.add( cache_id, {cookie.name: cookie.value} )
                    #cc = {cookie.name: cookie.value}
                    #requests.post( species.url + '/Login?operation=logout', cookies=cc)            
    else:
        k, v = cache.get(cache_id).items()[0] # always only one dict in the cache
        response.set_cookie(k, value=v, domain='.nal.usda.gov', path='/' + species_name + '/')
                
    return response
