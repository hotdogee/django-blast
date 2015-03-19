# coding: utf-8
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
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.utils import html
from .models import Species, SpeciesPassword, Registration, insert_species_permission, delete_species_permission
from userprofile.models import Profile
from userprofile.views import checkOAuth


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
        applicants = User.objects.filter(registration__species=species, registration__status='Pending').distinct()
        apply_records = []
        for applicant in applicants:
            apply_records.append(Registration.objects.select_related('user').filter(species=species, user=applicant).latest('submission_time'))
        species_owners = User.objects.filter(user_permissions__codename=sname+'_owner').distinct().order_by('last_name')
        species_users = User.objects.filter(~Q(user_permissions__codename=sname+'_owner'),Q(user_permissions__codename__startswith=sname)).distinct().order_by('last_name')
        species_list.append({'name': sname, 'full_name': species.full_name, 'is_owner': True, 'owners': species_owners, 'users': species_users, 'apply_records': apply_records,})
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
    interested_list = []
    for sname in unauth_set:     
        # check applying record first
        species = Species.objects.get(name=sname)
        apply_records = Registration.objects.filter(user=request.user, species=species).order_by('-submission_time')
        if not apply_records:
            unauth_list.append({'name': sname, 'full_name': species.full_name, 'status':'New',})
        elif apply_records[0].status == 'Pending':
            interested_list.append({'name': sname, 'full_name': species.full_name, 'status':'Pending', 'apply_records': apply_records,})
        elif apply_records[0].status == 'Rejected':
            interested_list.append({'name': sname, 'full_name': species.full_name, 'status':'Rejected', 'apply_records': apply_records,})
        elif apply_records[0].status == 'Removed':
            interested_list.append({'name': sname, 'full_name': species.full_name, 'status':'Removed', 'apply_records': apply_records,})
        else: # status is 'Approved' or 'Added'
            raise Exception('Shit happens')
    unauth_list.sort(key=lambda k:k['name'])

    return species_list, interested_list, unauth_list


@login_required
def index(request):
    species_list, interested_species_list, unauth_species_list = get_species(request)
    return render(
        request,
        'webapollo/webapollo.html', {
        'year': datetime.now().year,
        'title': 'Web Apollo',
        'species_list': species_list,
        'interested_species_list': interested_species_list,
        'unauth_species_list': unauth_species_list,
        'isOAuth': checkOAuth(request.user),
    })


def ajax_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        return HttpResponse(json.dumps({ 'invalid_request': True }), content_type='application/json')
    return wrapper


@ajax_login_required
def apply(request):
    if request.is_ajax():
        if request.method == 'POST':
            comment = html.escape(request.POST['comment'])
            comment = comment[:200] if len(comment) > 200 else comment
            try:
                _species = Species.objects.get(name=request.POST['species_name'])
                _registration = Registration(user=request.user, species=_species, submission_comment=comment)
                _registration.save()
                return HttpResponse(json.dumps({'succeeded': True, 'submission_time': _registration.submission_time.astimezone(timezone('US/Eastern')).strftime('%b. %d, %Y, %I:%M %p'), 'comment': comment,}), content_type='application/json')
            except: #ObjectDoesNotExist:
                print 'Exception in webapollo_apply: ', sys.exc_info()[0]
                return HttpResponse(json.dumps({'succeeded': False}), content_type='application/json')
    return HttpResponse(json.dumps({ 'succeeded': False }), content_type='application/json')

@ajax_login_required
def reject(request):
    if request.is_ajax():
        if request.method == 'POST':         
            comment = html.escape(request.POST['comment'])
            if comment:
                comment = comment[:200] if len(comment) > 200 else comment
            try:
                _species = Species.objects.get(name=request.POST['species_name'])
                _user = User.objects.get(username=request.POST['username'])
                _registration = Registration.objects.get(user=_user, species=_species, status='Pending')
                _registration.decision_comment = 'Reject by ' + request.user.username
                if comment:
                    _registration.decision_comment = 'from ' + request.user.username + ': '+ comment
                _registration.decision_time = datetime.now()
                _registration.status = 'Rejected'
                _registration.save()
                return HttpResponse(json.dumps({'succeeded': True}), content_type='application/json')
            except: #ObjectDoesNotExist:
                print 'Exception in webapollo_reject ', sys.exc_info()[0]
                return HttpResponse(json.dumps({'succeeded': False}), content_type='application/json')
                
    return HttpResponse(json.dumps({ 'succeeded': False }), content_type='application/json')

@ajax_login_required
def history(request):
    if request.is_ajax():
        if request.method == 'POST':
            try:
                _registrations = Registration.objects.filter(user__username=request.POST['username'], species__name=request.POST['species_name']).order_by('-submission_time')
                apply_records = []
                for reg in _registrations:
                    apply_records.append({
                        'submission_time': reg.submission_time.astimezone(timezone('US/Eastern')).strftime('%b. %d, %Y, %I:%M %p'),
                        'comment': reg.submission_comment,
                        'status': reg.status,
                        'msg': reg.decision_comment,
                    })
                return HttpResponse(json.dumps({'succeeded': True, 'apply_records': apply_records,}), content_type='application/json')
            except: #ObjectDoesNotExist:
                print 'Exception in webapollo_history ', sys.exc_info()[0]
                return HttpResponse(json.dumps({'succeeded': False}), content_type='application/json')
    return HttpResponse(json.dumps({ 'succeeded': False }), content_type='application/json')

@ajax_login_required
def eligible(request):
    if request.is_ajax():
        if request.method == 'POST':
            try:
                # selecte all users withour permissions, then remove users waiting for approval
                users = []
                eligible_users = Profile.objects.select_related('user').filter(
                    ~Q(user__user_permissions__codename__startswith=request.POST['species_name']),
                ).distinct()
                pending_users = Profile.objects.select_related('user').filter(
                    user__registration__species__name=request.POST['species_name'], 
                    user__registration__status='Pending'
                ).distinct()
                for p in pending_users:
                    eligible_users = eligible_users.filter(~Q(user=p.user))
                for u in eligible_users:
                    users.append({
                        'full_name': u.user.first_name + ' ' + u.user.last_name,
                        'username': u.user.username,
                        'institution': u.institution,
                    })
                return HttpResponse(json.dumps({'succeeded': True, 'users': users}), content_type='application/json')
            except: #ObjectDoesNotExist:
                print 'Exception in webapollo_eligible ', sys.exc_info()[0]
                return HttpResponse(json.dumps({'succeeded': False}), content_type='application/json')
    return HttpResponse(json.dumps({ 'succeeded': False }), content_type='application/json')

@ajax_login_required
def approve(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.has_perm('webapollo.' + request.POST['species_name'] + '_owner'):
                try:
                    _username = request.POST['username']
                    _species_name = request.POST['species_name']
                    _species = Species.objects.get(name=_species_name)
                    _perm_value = 3
                    _user = User.objects.get(username=_username)
                    
                    # using user_permissions.add() will trigger m2m_changed handler, which is undesirable, so write SQL directly to insert permissions
                    with connection.cursor() as c:
                        c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)', [_user.id, Permission.objects.get(codename=_species_name + '_read').id]) 
                        c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)', [_user.id, Permission.objects.get(codename=_species_name + '_write').id])                    
                    insert_species_permission(_username, _species.id, _perm_value)
                    _registration = Registration.objects.get(user__username=_username, species__name=_species_name, status='Pending')
                    _registration.status = 'Approved'
                    _registration.decision_time = datetime.now()
                    _registration.decision_comment = 'Approved by ' + request.user.username
                    _registration.save()
                    return HttpResponse(json.dumps({'succeeded': True, }), content_type='application/json')
                except: #ObjectDoesNotExist:
                    print 'Exception in webapollo_approve ', sys.exc_info()[0]
                    return HttpResponse(json.dumps({'succeeded': False}), content_type='application/json')
    return HttpResponse(json.dumps({ 'succeeded': False }), content_type='application/json')

@ajax_login_required
def adduser(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.has_perm('webapollo.' + request.POST['species_name'] + '_owner'):
                try:
                    _species_name = request.POST['species_name']
                    _usernames = request.POST.getlist('usernames[]')
                    _species = Species.objects.get(name=_species_name)
                    _perm_value = 3
                    _users = User.objects.filter(username__in=_usernames)
                    for u in _users: 
                        # using user_permissions.add() will trigger m2m_changed handler, which is undesirable, so write SQL directly to insert permissions
                        with connection.cursor() as c:
                            c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)', 
                                [u.id, Permission.objects.get(codename=_species_name + '_read').id]) 
                            c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)', 
                                [u.id, Permission.objects.get(codename=_species_name + '_write').id])                    
                        insert_species_permission(u.username, _species.id, _perm_value)
                        _registration = Registration(user=u, species=_species, decision_comment='Added by ' + request.user.username, status='Added', decision_time=datetime.now())
                        _registration.save()
                    return HttpResponse(json.dumps({'succeeded': True, 'usernames': _usernames }), content_type='application/json')
                except: #ObjectDoesNotExist:
                    print 'Exception in webapollo_adduser ', sys.exc_info()[0]
                    return HttpResponse(json.dumps({'succeeded': False}), content_type='application/json')
    return HttpResponse(json.dumps({ 'succeeded': False }), content_type='application/json')

@ajax_login_required
def remove(request):
    if request.is_ajax():
        if request.method == 'POST':
            if request.user.has_perm('webapollo.' + request.POST['species_name'] + '_owner'):
                try:
                    _username = request.POST['username']
                    _species_name = request.POST['species_name']
                    _species = Species.objects.get(name=_species_name)
                    _user = User.objects.get(username=_username)                
                    # using user_permissions.remove() will trigger m2m_changed handler, which is undesirable, so write SQL directly to remove permissions
                    with connection.cursor() as c:
                        perms = Permission.objects.filter(codename__startswith=_species_name)
                        for perm in perms:
                            c.execute('DELETE FROM auth_user_user_permissions WHERE user_id=%s AND permission_id=%s', [_user.id, perm.id]) 
                    delete_species_permission( _username, _species.id)
                    _registration = Registration(user=_user, species=_species, decision_comment='Removed by ' + request.user.username, status='Removed', decision_time=datetime.now())
                    _registration.save()
                    return HttpResponse(json.dumps({'succeeded': True, }), content_type='application/json')
                except: #ObjectDoesNotExist:
                    print 'Exception in webapollo_remove ', sys.exc_info()[0]
                    return HttpResponse(json.dumps({'succeeded': False}), content_type='application/json')
    return HttpResponse(json.dumps({ 'succeeded': False }), content_type='application/json')


@csrf_exempt
@staff_member_required
def manage(request):
    if request.method == 'GET':
        pendings = Registration.objects.filter(status='Pending').order_by('submission_time')
        #users = User.objects.all()
        profiles = Profile.objects.select_related('user').all()
        users = []
        for p in profiles:
            users.append({
                'id': p.user.id,
                'full_name': p.user.first_name + ' ' + p.user.last_name,
                'username': p.user.username,
                'institution': p.institution,
            })
        organisms = []
        species = Species.objects.all()
        for s in species:
            owner = User.objects.filter(user_permissions__codename=s.name+'_owner').distinct().count()
            annotator = User.objects.filter(user_permissions__codename__startswith=s.name).distinct().count()
            organisms.append({
                'name': s.name,
                'full_name': s.full_name,
                'owner': owner,
                'annotator': annotator,
            })
    return render(
        request,
        'webapollo/manage.html', {
            'pendings': pendings,
            'users': users,
            'species': organisms,
        }
    )


@csrf_exempt
@staff_member_required
def species_user(request, species_name):
    alert_success = False
    alert_fail = False
    alert_text = ''
    if request.method == 'POST':
        usernames = request.POST.get('usernames')
        if usernames:
            usernames = usernames.split(',')
        op = request.POST.get('operation')  # 'update', 'remove', 'adduser', 'addowner'
        try:
            for _username in usernames:
                u = User.objects.get(username=_username)
                if op == 'update' and u.has_perm('webapollo.' + species_name + '_owner'):
                    alert_text = 'Successfully Updated'
                    continue
                s = Species.objects.get(name=species_name)
                perms = Permission.objects.filter(codename__startswith=species_name)
                # if the user has a pending request, update it instead of adding a new record
                try:
                    r = Registration.objects.get(user=u, species=s, status='Pending')
                except:
                    r = Registration(user=u, species=s)

                if op.startswith('add'):  # 'adduser' or 'addowner'
                    perm_value = 15
                    # using user_permissions.add() will trigger m2m_changed handler, which is undesirable, so write SQL directly to insert permissions
                    if op == 'addowner':
                        with connection.cursor() as c:
                            for perm in perms:
                                c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)', [u.id, perm.id])
                    else:  # 'adduser'
                        with connection.cursor() as c:
                            c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)', 
                                [u.id, Permission.objects.get(codename=species_name + '_read').id])
                            c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)', 
                                [u.id, Permission.objects.get(codename=species_name + '_write').id])
                        perm_value = 3
                    insert_species_permission(u.username, s.id, perm_value)
                    r.status = 'Added'
                    r.decision_comment = 'Added by ' + request.user.username + ' (admin)'
                    alert_text = 'Successfully Added'
                else:  # 'remove' or 'update'
                    # using user_permissions.remove() will trigger m2m_changed handler, which is undesirable, so write SQL directly to remove permissions
                    with connection.cursor() as c:
                        for perm in perms:
                            c.execute('DELETE FROM auth_user_user_permissions WHERE user_id=%s AND permission_id=%s', [u.id, perm.id])
                    delete_species_permission(_username, s.id)                  
                    alert_text = 'Successfully Removed'

                    r.status = 'Removed'
                    r.decision_comment = 'Removed by ' + request.user.username + ' (admin)'
                    
                    # for update users to owner
                    if op == 'update':
                        with connection.cursor() as c:
                            for perm in perms:
                                c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)', [u.id, perm.id])
                        insert_species_permission(u.username, s.id, 15)
                        r.status = 'Added'
                        r.decision_comment = 'Added by ' + request.user.username + ' (admin)'
                        alert_text = 'Successfully Updated'

                r.decision_time = datetime.now()
                r.save()
            alert_success = True
        except:
            alert_text = 'Exception in webapollo_species_users ' + str(sys.exc_info()[0])
            alert_fail = True

    # for GET request
    profiles = Profile.objects.select_related('user').filter(user__user_permissions__codename__startswith=species_name).distinct()
    users = []
    for profile in profiles:
        users.append({
            'full_name': profile.user.first_name + ' ' + profile.user.last_name,
            'username': profile.user.username,
            'institution': profile.institution,
            'is_owner': profile.user.has_perm('webapollo.' + species_name + '_owner'),  # "<app label>.<permission codename>"
        })
    candidates = []
    profiles = Profile.objects.select_related('user').filter(
        ~Q(user__user_permissions__codename__startswith=species_name),
    ).distinct()
    for profile in profiles:
        candidates.append({
            'full_name': profile.user.first_name + ' ' + profile.user.last_name,
            'username': profile.user.username,
            'institution': profile.institution,
        })
    
    return render(
        request,
        'webapollo/species_user.html', {
        'users': users,
        'candidates': candidates,
        'species_name': species_name,
        'alert_success': alert_success,
        'alert_fail': alert_fail,
        'alert_text': alert_text,
        }
    )


@csrf_exempt
@staff_member_required
def user_permission(request, user_id):
    if request.method == 'GET':
        profile = Profile.objects.select_related('user').get(user__id=user_id)
        user = {
            'full_name': profile.user.first_name + ' ' + profile.user.last_name,
            'username': profile.user.username,
            'institution': profile.institution,
        }
        
        species = Species.objects.all()
        species_list = []
        for s in species:
            perms = profile.user.user_permissions.filter(codename__startswith=s.name)
            perm_values = {'read': False, 'write': False, 'publish': False, 'admin': False, 'owner': False}
            for perm in perms:
                perm_name = perm.name.split('_',2)[1]
                perm_values[perm_name] = True
                        
            species_list.append({
                'name': s.name,
                'full_name': s.full_name,
                'perm_values': perm_values
            })

        return render(
            request,
            'webapollo/user_permission.html', {
                'user': user,
                'species_list': species_list,
            }
        )
    elif request.is_ajax() and request.method == 'POST':
        s_perms = request.POST.get('species_permissions')
        s_perms = json.loads(s_perms)
        for s_perm in s_perms:
            try:
                u = User.objects.get(pk=user_id)
                s = Species.objects.get(name=s_perm['species_name'])
                # using user_permissions.remove() will trigger m2m_changed handler, which is undesirable, so write SQL directly to remove permissions
                with connection.cursor() as c:
                    perms = Permission.objects.filter(codename__startswith=s_perm['species_name'])
                    for perm in perms:
                        c.execute('DELETE FROM auth_user_user_permissions WHERE user_id=%s AND permission_id=%s', [user_id, perm.id])
                delete_species_permission(u.username, s.id)
                if s_perm['permission'] == 0:
                    # if the user has a pending request, update it instead of adding a new record
                    try:
                        r = Registration.objects.get(user=u, species=s, status='Pending')
                    except:
                        r = Registration(user=u, species=s)
                    r.status = 'Removed'
                    r.decision_comment = 'Removed by ' + request.user.username + ' (admin)'
                    r.decision_time = datetime.now()
                    r.save()
                else:
                    # using user_permissions.add() will trigger m2m_changed handler, which is undesirable, so write SQL directly to insert permissions
                    perm_table = {
                        1 : ['read'],
                        2 : ['write'],
                        4 : ['publish'],
                        8 : ['admin'],
                        3 : ['read', 'write'],
                        5 : ['read', 'publish'],
                        9 : ['read', 'admin'],
                        6 : ['write', 'publish'],
                        10: ['write', 'admin'],
                        12: ['publish', 'admin'],
                        7 : ['read', 'write', 'publish'],
                        14: ['write', 'publish', 'admin'],
                        15: ['read', 'write', 'publish', 'admin']
                    }                    
                    with connection.cursor() as c:
                        for perm_str in perm_table[s_perm['permission']]:
                            c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)',
                                [user_id, Permission.objects.get(codename=s_perm['species_name'] + '_' + perm_str).id])
                        if s_perm['is_owner']:
                            c.execute('INSERT INTO auth_user_user_permissions (user_id, permission_id) VALUES (%s, %s)',
                                [user_id, Permission.objects.get(codename=s_perm['species_name'] + '_owner').id])
                    insert_species_permission(u.username, s.id, s_perm['permission'])
                    # if the user has a pending request, update it instead of adding a new record
                    try:
                        r = Registration.objects.get(user=u, species=s, status='Pending')
                    except:
                        r = Registration(user=u, species=s)
                    r.status = 'Added'
                    r.decision_comment = 'Added by ' + request.user.username + ' (admin)'
                    r.decision_time = datetime.now()
                    r.save()
            except:
                print 'Exception in webapollo_user_permission ', sys.exc_info()[0]
                return HttpResponse(json.dumps({'succeeded': False}), content_type='application/json')
        return HttpResponse(json.dumps({'succeeded': True}), content_type='application/json')
    else:
        return HttpResponse('Error')
        

@login_required
def species(request, species_name):
    if not request.user.user_permissions.filter(codename__startswith=species_name):
        return HttpResponse('You do not have permissions to access the instance.')

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
                    cache.set( cache_id, {cookie.name: cookie.value}, 1800 ) # timeout = 30 mins
    else:
        k, v = cache.get(cache_id).items()[0] # always only one dict in the cache
        response.set_cookie(k, value=v, domain='.nal.usda.gov', path='/' + species_name + '/')
                
    return response
