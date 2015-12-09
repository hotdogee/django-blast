from __future__ import absolute_import
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import PermsRequest, UserMapping
from django.contrib.auth.models import User
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
import i5k.settings
from  blast.models import Organism
import re
from Crypto.Cipher import AES
import base64

import json
import urllib2
import cookielib

def _get_login(request):
    opener = _get_url_open()
    response = opener.open(_get_url_request(request.session['apollo_url']+'/apollo/Login?operation=login'),
                           json.dumps(_get_robot_priviledge()))
    result = json.loads(response.read())
    if('error' in result):
        pass
    else:
        return opener

def _get_url_open():
    cookies = cookielib.LWPCookieJar()
    handlers = [
        urllib2.HTTPHandler(),
        urllib2.HTTPSHandler(),
        urllib2.HTTPCookieProcessor(cookies)
        ]
    opener = urllib2.build_opener(*handlers)
    return opener

def _get_url_request(url):
    req = urllib2.Request(url)
    req.add_header('Content-Type', 'application/json')
    return req

def _get_robot_priviledge():
    #get from configuration
    data = {'username':i5k.settings.ROBOT_ID, 'password':i5k.settings.ROBOT_PWD}
    return data

def _get_my_priviledge(request):
    um = UserMapping.objects.get(django_user=request.user)
    data = {'username':request.session['apollo_name'], 'password':decodeAES(um.apollo_user_pwd)}
    return data

def _django_user_to_apollo_name(user):
    user_mapping = UserMapping.objects.get(django_user=user)
    return user_mapping.apollo_user_name

def _apollo_name_to_django_user(name):
    user_mapping = UserMapping.objects.get(apollo_user_name=name)
    return user_mapping.django_user

@login_required
def create(request):
    request.session['apollo_url'] = i5k.settings.APOLLO_URL
    #who don't have apollo_account

    try:
        user_mapping = UserMapping.objects.get(django_user=request.user)
    except UserMapping.DoesNotExist:
        return render(request, 'webapollo_sso/main.html', {
                'title': 'SSO',
                'user_type': 'NEW',
                'i5k_usre_name': request.user.username,
                'I5K_URL': i5k.settings.I5K_URL,
                'APOLLO_URL': i5k.settings.APOLLO_URL,
        })

    if('apollo_name' not in request.session or 'apollo_user_id' not in request.session):
        #user_mapping = UserMapping.objects.get(django_user=request.user)
        apollo_name = user_mapping.apollo_user_name
        apollo_user_id = user_mapping.apollo_user_id
        request.session['apollo_name'] = apollo_name
        request.session['apollo_user_id'] = apollo_user_id
    else:
        apollo_user_id = request.session['apollo_user_id']

    if('user_type' not in request.session):
        opener = _get_login(request)
        req = _get_url_request(request.session['apollo_url']+'/apollo/user/loadUsers')
        response = opener.open(req, json.dumps({"userId" : apollo_user_id}))
        users = json.loads(response.read())
        request.session['user_type'] = 'ADMIN' if(users[0]['role'] == 'ADMIN') else 'USER'

    return render(request, 'webapollo_sso/main.html', {
            'title': 'SSO',
            'user_type': request.session['user_type'],
            'i5k_usre_name': request.user.username,
            'apollo_user_name': request.session['apollo_name'],
            'I5K_URL': i5k.settings.I5K_URL,
            'APOLLO_URL': i5k.settings.APOLLO_URL,
    })


@login_required
def get_users(request):

    opener = _get_login(request)
    response = opener.open(request.session['apollo_url']+'/apollo/user/loadUsers')
    users = json.loads(response.read())

    #retrieve user info for user management page of myOrganism
    if('organism' in request.GET):
        result = []
        organism = request.GET['organism']

        for user in users:
            del user['organismPermissions']
            del user['availableGroups']
            groups = map(lambda x:x['name'], user['groups'])
            if("_".join(["GROUP",organism,"ADMIN"]) in groups):
                user['admin'] = True
            else:
                user['admin'] = False

            if("_".join(["GROUP",organism,"ADMIN"]) in groups or "_".join(["GROUP",organism,"USER"]) in groups):
                result.append(user)

        return HttpResponse(json.dumps(result), content_type="application/json")

    #look up mapping between django_user and apollo_user
    for user in users:
        del user['organismPermissions']
        del user['availableGroups']
        try:
            user_info = UserMapping.objects.get(apollo_user_id=user['userId'])
            if(user_info.django_user != None):
                user['djangoUser'] = user_info.django_user.username
            else:
                user['djangoUser'] = "DISCONNECTED"
        except UserMapping.DoesNotExist:
            user['djangoUser'] = "DISCONNECTED"
        user['groups'] = sorted(user['groups'])

    return HttpResponse(json.dumps(users), content_type="application/json")

@login_required
def get_groups(request):

    opener = _get_login(request)
    response = opener.open(request.session['apollo_url']+'/apollo/group/loadGroups')
    groups = json.loads(response.read())

    result = []
    #trouble when weired group name
    for group in groups:
        m = re.match(r"GROUP_(\w+)_(USER|ADMIN)", group['name'])
        if(m != None):
            oname = m.group(1)
            group['permission'] = {u'organism': u'None', u'groupId': 0, u'permissions': u'[]'}
            #result.append(group)

            for organism_perm in group['organismPermissions']:
                if(oname == get_short_name(request,organism_perm['organism'])):
                    group['permission'] = organism_perm
                    group['fullname'] = organism_perm['organism']
                    del group['organismPermissions']
                    result.append(group)
                    break


    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def get_my_organism(request):

    opener = _get_login(request)
    req = _get_url_request(request.session['apollo_url']+'/apollo/user/loadUsers')
    response = opener.open(req, json.dumps({"userId" : request.session['apollo_user_id']}))
    users = json.loads(response.read())
    user = users[0]

    if('allOrganism' in request.session):
        organisms = request.session['allOrganism']
    else:
        response = opener.open(request.session['apollo_url']+'/apollo/organism/findAllOrganisms')
        organisms = json.loads(response.read())
        request.session['allOrganism'] = organisms

    result = {}
    user_groups = map(lambda x:x['name'], user['groups'])
    #print user_groups
    for organism in organisms:
        perms = PermsRequest.objects.filter(oid=organism['id'], status="PENDING").all();
        is_pending_request = True if (len(perms) != 0) else False;

        short_name = get_short_name(request, organism['commonName'], organism['id'])
        if(short_name != None):
            if("_".join(["GROUP",short_name,"ADMIN"]) in user_groups):
                result[organism['commonName']+"_"+str(organism['id'])] = [True,is_pending_request,short_name]
            elif("_".join(["GROUP",short_name,"USER"]) in user_groups):
                result[organism['commonName']+"_"+str(organism['id'])] = [False,is_pending_request,short_name]

    return HttpResponse(json.dumps(OrderedDict(sorted(result.items()))), content_type="application/json")

@login_required
def get_my_request(request):
    opener = _get_login(request)
    req = _get_url_request(request.session['apollo_url']+'/apollo/user/loadUsers')
    response = opener.open(req, json.dumps({"userId" : request.session['apollo_user_id']}))
    users = json.loads(response.read())
    user = users[0]

    if('allOrganism' in request.session):
        organisms = request.session['allOrganism']
    else:
        response = opener.open(request.session['apollo_url']+'/apollo/organism/findAllOrganisms')
        organisms = json.loads(response.read())
        request.session['allOrganism'] = organisms

    my_groups = map(lambda x:x['name'], user['groups'])

    result = []
    for organism in organisms:
        if('directory' in organism):
            del organism['directory']
            del organism['blatdb']
            del organism['species']
            del organism['genus']

        print organism['commonName']
        short_name = get_short_name(request, organism['commonName'], organism['id'])

        if(short_name == None):
            continue

        if("_".join(["GROUP",short_name,"ADMIN"]) in my_groups):
            organism['admin'] = True
            organism['action'] = None
        else:
            organism['admin'] = False
            try:
                perm_request = PermsRequest.objects.get(user_apply=request.user, oid=organism['id'],status="PENDING")
                organism['action'] = perm_request.action
            except PermsRequest.DoesNotExist:
                organism['action'] = "NONE"

            if("_".join(["GROUP",short_name,"USER"]) in my_groups):
                if(organism['action'] == "RELEASE"):
                    organism['action'] = "W_RELEASE"
                else:
                    organism['action'] = "RELEASE"
            else:
                if(organism['action'] == "REQUEST"):
                    organism['action'] = "W_REQUEST"
                else:
                    organism['action'] = "REQUEST"

        result.append(organism)

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def get_pending_request(request):
    oid = request.GET['oid']
    perm_request_array = PermsRequest.objects.filter(oid=oid, status="PENDING").all()
    user_action = {}
    for perm_request in perm_request_array:
        apollo_name = _django_user_to_apollo_name(perm_request.user_apply)
        user_action[apollo_name] = [perm_request.action, perm_request.apply_desc]

    if(len(user_action) == 0):
        return HttpResponse(json.dumps({}), content_type="application/json")

    data = {}
    data.update(_get_my_priviledge(request))
    req = _get_url_request(request.session['apollo_url']+'/apollo/user/loadUsers')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    users = json.loads(response.read())

    #opener = _get_login(request)
    #response = opener.open(request.session['apollo_url']+'/apollo/user/loadUsers')
    #users = json.loads(response.read())

    #may be improve efficency
    result = []
    for user in users:
        if(user['username'] in user_action):
            user['action'] = user_action[user['username']][0]
            user['desc'] = user_action[user['username']][1]
            del user['organismPermissions']
            del user['availableGroups']
            result.append(user)

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def make_request(request):
    oid =  request.POST['oid']
    action = request.POST['action']
    apply_desc = request.POST['apply_desc']

    try:
        perm_request = PermsRequest.objects.get(oid=oid, user_apply=request.user, status="PENDING")
        perm_request.delete()
    except PermsRequest.DoesNotExist:
        pass

    try:
        if(action == "RELEASE" or action == "REQUEST"):
            perm_request = PermsRequest.objects.create(action=action, oid=oid, user_apply=request.user, status="PENDING", apply_desc=apply_desc)
            perm_request.save()
        return HttpResponse(json.dumps({}), content_type="application/json")

    except:
        return HttpResponse(json.dumps({"error":"System error"}), content_type="application/json")

@login_required
def handle_request(request):
    action = request.POST['action']
    oid    = request.POST['oid']
    oname  = request.POST['oname']
    user_apollo   = request.POST['user']
    userId_apollo = request.POST['userId']
    user = _apollo_name_to_django_user(user_apollo)
    reply_desc = request.POST['reply_desc']

    perm_request = PermsRequest.objects.get(oid=oid, user_apply=user, status="PENDING")
    perm_request.reply_desc = reply_desc
    perm_request.user_reply = request.user

    if(perm_request.action == "REQUEST" and action=="ACCEPT"):
        perm_request.status = "ACCEPTED"

        data = {"group":"GROUP_"+oname+"_USER", "userId":userId_apollo}
        data.update(_get_my_priviledge(request))
        print _get_my_priviledge(request)
        req = _get_url_request(request.session['apollo_url']+'/apollo/user/addUserToGroup')
        opener = _get_url_open()
        response = opener.open(req, json.dumps(data))
        result = response.read()

        print result
        perm_request.save()
    elif(perm_request.action == "REQUEST" and action=="REFUSE"):
        perm_request.status = "REFUSED"
        perm_request.save()
    elif(perm_request.action == "RELEASE" and action=="ACCEPT"):
        perm_request.status = "ACCEPTED"
        data = {"group":"GROUP_"+oname+"_USER", "userId":userId_apollo}
        data.update(_get_my_priviledge(request))
        print _get_my_priviledge(request)
        req = _get_url_request(request.session['apollo_url']+'/apollo/user/removeUserFromGroup')
        opener = _get_url_open()
        response = opener.open(req, json.dumps(data))
        result = response.read()

        print result
        perm_request.save()
    elif(perm_request.action == "RELEASE" and action=="REFUSE"):
        perm_request.status = "REFUSED"
        perm_request.save()

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def add_user_to_group(request):
    group_name = request.POST['groupName']
    apollo_userId = request.POST['userId'] if('userId' in request.POST) else None
    apollo_userName = request.POST['userName'] if('userName' in request.POST) else None

    if(apollo_userId != None):
        data = {"group":group_name, "userId":apollo_userId}
    elif(apollo_userName != None):
        data = {"group":group_name, "user":apollo_userName}
    else:
        data = {} #fail

    data.update(_get_my_priviledge(request))

    req = _get_url_request(request.session['apollo_url']+'/apollo/user/addUserToGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = response.read()
    print result

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def remove_user_from_group(request):
    group_name = request.POST['groupName']
    apollo_userId = request.POST['userId'] if('userId' in request.POST) else None
    apollo_userName = request.POST['userName'] if('userName' in request.POST) else None

    if(apollo_userId != None):
        data = {"group":group_name, "userId":apollo_userId}
    elif(apollo_userName != None):
        data = {"group":group_name, "user":apollo_userName}
    else:
        data = {} #fail

    data.update(_get_my_priviledge(request))

    req = _get_url_request(request.session['apollo_url']+'/apollo/user/removeUserFromGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = response.read()
    print result

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def create_user(request):
    first_name = request.POST['firstName']
    last_name  = request.POST['lastName']
    email      = request.POST['userName']
    django_username = request.POST['djangoUserName']
    password = User.objects.make_random_password(length=20) if request.POST['password'] == '' else request.POST['password']

    #password format checking

    data = {"firstName" : first_name, "lastName" : last_name, "email": email, "new_password" : password, "role" : "USER"}
    data.update(_get_my_priviledge(request))

    req = _get_url_request(request.session['apollo_url']+'/apollo/user/createUser')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    print result

    if(len(result) == 0):
        response = opener.open(request.session['apollo_url']+'/apollo/user/loadUsers')
        users = json.loads(response.read())

        for user in users:
            if(user['username'] == email):
                userId = user['userId']
                break

        user_info = UserMapping.objects.create(apollo_user_id=userId,
                                               apollo_user_name=email,
                                               apollo_user_pwd=encodeAES(password),
                                               django_user=User.objects.get(username=django_username) if(django_username != '') else None)
        user_info.save()

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def delete_user(request):
    user_id = request.POST['userId']
    data = {"userId" : user_id}
    data.update(_get_my_priviledge(request))

    req = _get_url_request(request.session['apollo_url']+'/apollo/user/deleteUser')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    print result

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def update_user(request):
    user_id = request.POST['userId']
    email   = request.POST['userName']
    first_name = request.POST['firstName']
    last_name  = request.POST['lastName']
    role       = request.POST['role']
    new_password    = request.POST['password']
    django_username = request.POST['djangoUserName']
    #check password format

    data = {"userId" : user_id, "firstName" : first_name , "lastName" : last_name ,"email" : email, "role" : role}
    data.update(_get_my_priviledge(request))

    password = User.objects.make_random_password(length=20) if new_password == '' else new_password
    data['newpassword'] = password

    print data
    req = _get_url_request(request.session['apollo_url']+'/apollo/user/updateUser')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    if(len(result) == 0):
        try:
            user_info = UserMapping.objects.get(apollo_user_id=user_id)
            user_info.apollo_user_name = email
            if(new_password != ''):
                user_info.apollo_user_pwd = encodeAES(new_password)
            if(django_username != ''):
                user_info.django_user = User.objects.get(username=django_username)
            user_info.save()
        except UserMapping.DoesNotExist:
            password = encodeAES(User.objects.make_random_password(length=20)) if new_password == '' else encodeAES(new_password)
            user_info = UserMapping.objects.create(apollo_user_id=user_id,
                                                   apollo_user_name=email,
                                                   apollo_user_pwd=password,
                                                   django_user=User.objects.get(username=django_username) if(django_username != '') else None)
            user_info.save()

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def disconnect_user(request):
    user_info = UserMapping.objects.get(apollo_user_id=request.POST['userId'])
    user_info.django_user = None
    user_info.save()
    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def check_django_user_available(request):
    username = request.POST['userName']

    try:
        user = User.objects.get(username=username)
        user_mapping = UserMapping.objects.filter(django_user=user).all()

        if(len(user_mapping) == 0):
            return HttpResponse(json.dumps({}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({"error":"The account already connected"}), content_type="application/json")
    except:
        return HttpResponse(json.dumps({"error":"User doesn't exist"}), content_type="application/json")


@login_required
def create_group_for_organism(request):
    full_name =  request.POST['fullName']
    short_name = request.POST['shortName']

    print short_name

    group_admin = '_'.join(["GROUP", short_name, "ADMIN"])
    group_user  = '_'.join(["GROUP", short_name, "USER"])

    data = {"name" : group_admin}
    data.update(_get_my_priviledge(request))
    data2 = {"name" : group_user}
    data2.update(_get_my_priviledge(request))
    data_admin_perms = {"name": group_admin, "organism" : full_name, "ADMINISTRATE" : False, "WRITE" : False, "EXPORT" : False, "READ" : False}
    data_admin_perms.update(_get_my_priviledge(request))
    data_user_perms = {"name": group_user, "organism" : full_name, "ADMINISTRATE" : False, "WRITE" : True, "EXPORT" : True, "READ" : True}
    data_user_perms.update(_get_my_priviledge(request))

    req = _get_url_request(request.session['apollo_url']+'/apollo/group/createGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    print result

    print data_admin_perms
    req = _get_url_request(request.session['apollo_url']+'/apollo/group/updateOrganismPermission')
    response = opener.open(req, json.dumps(data_admin_perms))
    result = response.read()
    print result

    req = _get_url_request(request.session['apollo_url']+'/apollo/group/createGroup')
    response = opener.open(req, json.dumps(data2))
    result = json.loads(response.read())
    print result

    req = _get_url_request(request.session['apollo_url']+'/apollo/group/updateOrganismPermission')
    response = opener.open(req, json.dumps(data_user_perms))
    result = response.read()
    print result

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def delete_group_for_organism(request):
    oname = request.POST['oname']
    group_admin = '_'.join(["GROUP", oname, "ADMIN"])
    group_user  = '_'.join(["GROUP", oname, "USER"])

    data = {"name" : group_admin}
    data.update(_get_my_priviledge(request))
    data2 = {"name" : group_user}
    data2.update(_get_my_priviledge(request))

    req = _get_url_request(request.session['apollo_url']+'/apollo/group/deleteGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    req = _get_url_request(request.session['apollo_url']+'/apollo/group/deleteGroup')
    #opener = _get_url_open()
    response = opener.open(req, json.dumps(data2))
    result = json.loads(response.read())

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def get_all_groups(request):

    opener = _get_login(request)
    response = opener.open(request.session['apollo_url']+'/apollo/group/loadGroups')
    groups = json.loads(response.read())

    result = []
    for group in groups:
        m = re.match(r"GROUP_(\w+)_(USER|ADMIN)", group['name'])
        if(m != None):
            result.append(group['name'])

    return HttpResponse(json.dumps(sorted(result)), content_type="application/json")

@login_required
def check_organism_exist(request):
    organism_name = request.POST['oname']

    opener = _get_login(request)
    response = opener.open(request.session['apollo_url']+'/apollo/organism/findAllOrganisms')
    organisms = json.loads(response.read())

    for organism in organisms:
        if(organism['commonName'] == organism_name):
            short_name = get_short_name(request, organism['commonName'])
            if(short_name != None):
                return HttpResponse(json.dumps({"short_name" : short_name}), content_type="application/json")
            else:
                break

    return HttpResponse(json.dumps({"error":"Organism doesn't exist"}), content_type="application/json")

def get_short_name(request, display_name, OID=-1):
    if(display_name in request.session):
        return request.session[display_name]

    if("-" in display_name):
        display_name = display_name[0:display_name.index("-")].strip()
    try:
        o = Organism.objects.get(display_name=display_name);
        short_name = o.short_name
        short_name = short_name.upper()
    except Organism.DoesNotExist:
        short_name = None

    request.session[display_name] = short_name
    if(OID != -1):
        request.session['oid-'+str(OID)] = short_name

    return short_name

@login_required
def apollo_connect(request):
    user_mapping = UserMapping.objects.get(django_user=request.user)
    data = {'username':user_mapping.apollo_user_name, 'password':decodeAES(user_mapping.apollo_user_pwd)}
    req = urllib2.Request(request.session['apollo_url']+'/apollo/Login?operation=login')
    req.add_header('Content-Type', 'application/json')

    cookies = cookielib.LWPCookieJar()
    handlers = [
        urllib2.HTTPHandler(),
        urllib2.HTTPSHandler(),
        urllib2.HTTPCookieProcessor(cookies)
        ]
    opener = urllib2.build_opener(*handlers)

    response = opener.open(req, json.dumps(data))
    page = response.read()

    response = HttpResponseRedirect(request.session['apollo_url']+'/apollo/annotator/loadLink?organism='+request.GET['oid'])

    for cookie in cookies:
        if(cookie.name == 'JSESSIONID'):
            response.set_cookie(key=cookie.name, value=cookie.value, domain=cookie.domain, path=cookie.path, expires=cookie.expires)

    return response

@login_required
def get_pending_request_admin(request):

    perm_request_array = PermsRequest.objects.filter(status="PENDING").all()

    if(len(perm_request_array) > 0):
        result = []
        for perm_request in perm_request_array:
            apollo_name = _django_user_to_apollo_name(perm_request.user_apply)
            #result.append({'apollo_name':apollo_name, 'action':perm_request.action, 'oid':request.session['oid-'+str(perm_request.oid)], 'desc':perm_request.apply_desc, 'date':perm_request.apply_date.strftime("%Y-%m-%d %H:%M:%S")})
            result.append({'apollo_name':apollo_name, 'action':perm_request.action, 'oid':perm_request.oid, 'desc':perm_request.apply_desc, 'date':perm_request.apply_date.strftime("%Y-%m-%d %H:%M:%S")})

        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def register_newUser(request):
    uname = request.POST['userName']
    pwd = request.POST['password']

    try:
        user_mapping = UserMapping.objects.get(apollo_user_name=uname)
        if(user_mapping.django_user == None):
            is_empty_account = "RECORD"
        else:
            is_empty_account = "OTHERS"
    except UserMapping.DoesNotExist:
        is_empty_account = "NO_RECORD"

    if(is_empty_account == 'OTHERS'):
        return HttpResponse(json.dumps({'error':'This account is used by others.'}), content_type="application/json")
    else:
        opener = _get_url_open()
        response = opener.open(_get_url_request(request.session['apollo_url']+'/apollo/Login?operation=login'),
                               json.dumps({'username':uname, 'password':pwd}))
        result = json.loads(response.read())

        if(len(result)==0):
            if(is_empty_account == 'NO_RECORD'):
                    opener = _get_login(request)
                    response = opener.open(request.session['apollo_url']+'/apollo/user/loadUsers')
                    users = json.loads(response.read())
                    for user in users:
                        if(user['username'] == uname):
                            user_mapping = UserMapping.objects.create(apollo_user_id=user['userId'],
                                                                      apollo_user_name=uname,
                                                                      apollo_user_pwd=pwd,
                                                                      django_user=request.user)
                            break

            else:
                user_mapping.django_user=request.user

            user_mapping.save()
            return HttpResponse(json.dumps({}), content_type="application/json")
        else:

            return HttpResponse(json.dumps({'error':'Login fail'}), content_type="application/json")

@login_required
def get_my_reqhist(request):
    perms_request_array = PermsRequest.objects.filter(user_apply=request.user).all()

    encoded = encodeAES('ifish')
    decoded = decodeAES(encoded)
    print encoded
    print decoded

    result=[]
    for perms_request in perms_request_array:
        result.append({'req_type':perms_request.action, 'oid':perms_request.oid,
                       'apply_date':perms_request.apply_date.strftime("%Y-%m-%d %H:%M:%S"),
                       'apply_note':perms_request.apply_desc,
                       'reply_date':perms_request.end_date.strftime("%Y-%m-%d %H:%M:%S")
                       if perms_request.end_date.strftime("%Y-%m-%d %H:%M:%S") != perms_request.apply_date.strftime("%Y-%m-%d %H:%M:%S")
                       else None,
                       'reply_note':perms_request.reply_desc,
                       'reply_user':perms_request.user_reply.username if perms_request.user_reply !=None else None,
                       'status':perms_request.status})

    print result
    return HttpResponse(json.dumps(result), content_type="application/json")

def encodeAES(password):
    BLOCK_SIZE = 32
    PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    cipher = AES.new("1234567890123456")
    encoded = base64.b64encode(cipher.encrypt(pad(password)))
    return encoded

def decodeAES(encoded):
    PADDING = '{'
    cipher = AES.new("1234567890123456")
    decoded  = cipher.decrypt(base64.b64decode(encoded)).rstrip(PADDING)
    return decoded

@login_required
def update_group_permissions(request):
    read_p = request.POST['read_p']
    write_p = request.POST['write_p']
    export_p = request.POST['export_p']
    full_name = request.POST['fullName']
    group_name = request.POST['groupName']

    data = {"name": group_name, "organism" : full_name, "ADMINISTRATE" : False, "WRITE" : write_p, "EXPORT" : export_p, "READ" : read_p}
    #data.update(_get_robot_priviledge())
    data.update(_get_my_priviledge(request))

    opener = _get_url_open()
    req = _get_url_request(request.session['apollo_url']+'/apollo/group/updateOrganismPermission')
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    return HttpResponse(json.dumps({}), content_type="application/json")

