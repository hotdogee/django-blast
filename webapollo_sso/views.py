from __future__ import absolute_import
from django.http import HttpResponse
from django.shortcuts import render
from .models import PermsRequest, UserMapping
from django.contrib.auth.models import User
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
import i5k.settings

import json
import urllib2
import cookielib

def _get_login():
    opener = _get_url_open()
    response = opener.open(_get_url_request('http://localhost:8085/apollo/Login?operation=login'),
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

def _django_user_to_apollo_name(user):
    user_mapping = UserMapping.objects.get(django_user=user)
    return user_mapping.apollo_user_name

def _apollo_name_to_django_user(name):
    user_mapping = UserMapping.objects.get(apollo_user_name=name)
    return user_mapping.django_user

@login_required
def create(request):
    #who don't have apollo_account
    if('apollo_name' not in request.session or 'apollo_user_id' not in request.session):
        user_mapping = UserMapping.objects.get(django_user=request.user)
        apollo_name = user_mapping.apollo_user_name
        apollo_user_id = user_mapping.apollo_user_id
        request.session['apollo_name'] = apollo_name
        request.session['apollo_user_id'] = apollo_user_id
    else:
        apollo_name = request.session['apollo_name']
        apollo_user_id = request.session['apollo_user_id']

    if('is_admin' not in request.session):
        opener = _get_login()
        req = _get_url_request('http://localhost:8085/apollo/user/loadUsers')
        response = opener.open(req, json.dumps({"userId" : apollo_user_id}))
        users = json.loads(response.read())

        request.session['is_admin'] = True if(users[0]['role'] == 'ADMIN') else False

    return render(request, 'webapollo_sso/main.html', {
            'title': 'SSO',
            'is_admin': request.session['is_admin'],
    })

@login_required
def get_users(request):

    opener = _get_login()
    response = opener.open("http://localhost:8085/apollo/user/loadUsers")
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

    return HttpResponse(json.dumps(users), content_type="application/json")

@login_required
def get_groups(request):

    opener = _get_login()
    response = opener.open("http://localhost:8085/apollo/group/loadGroups")
    groups = json.loads(response.read())

    #trouble when weired group name
    for group in groups:
        oname = group['name'].split('_')[1]
        group['permission'] = {u'organism': u'None', u'groupId': 0, u'permissions': u'[]'}
        for organism_perm in group['organismPermissions']:
            if(oname == organism_perm['organism']):
                group['permission'] = organism_perm
                del group['organismPermissions']
                break

        #print group

    return HttpResponse(json.dumps(groups), content_type="application/json")

@login_required
def get_my_organism(request):

    opener = _get_login()
    req = _get_url_request('http://localhost:8085/apollo/user/loadUsers')
    response = opener.open(req, json.dumps({"userId" : request.session['apollo_user_id']}))
    users = json.loads(response.read())
    user = users[0]

    response = opener.open("http://localhost:8085/apollo/organism/findAllOrganisms")
    organisms = json.loads(response.read())

    result = {}
    user_groups = map(lambda x:x['name'], user['groups'])
    #print user_groups
    for organism in organisms:
        perms = PermsRequest.objects.filter(oid=organism['id'], status="PENDING").all();
        is_pending_request = True if (len(perms) != 0) else False;

        if("_".join(["GROUP",organism['commonName'],"ADMIN"]) in user_groups):
            result[organism['commonName']+"_"+str(organism['id'])] = [True,is_pending_request]
        elif("_".join(["GROUP",organism['commonName'],"USER"]) in user_groups):
            result[organism['commonName']+"_"+str(organism['id'])] = [False,is_pending_request]

    return HttpResponse(json.dumps(OrderedDict(sorted(result.items()))), content_type="application/json")

@login_required
def get_my_request(request):

    opener = _get_login()
    req = _get_url_request('http://localhost:8085/apollo/user/loadUsers')
    response = opener.open(req, json.dumps({"userId" : request.session['apollo_user_id']}))
    users = json.loads(response.read())
    user = users[0]

    response = opener.open("http://localhost:8085/apollo/organism/findAllOrganisms")
    organisms = json.loads(response.read())

    my_groups = map(lambda x:x['name'], user['groups'])

    for organism in organisms:
        if("_".join(["GROUP",organism['commonName'],"ADMIN"]) in my_groups):
            organism['admin'] = True
            organism['action'] = "NONE"
        else:
            organism['admin'] = False
            try:
                perm_request = PermsRequest.objects.get(user_apply=request.user, oid=organism['id'],status="PENDING")
                organism['action'] = perm_request.action
            except PermsRequest.DoesNotExist:
                organism['action'] = "NONE"

            if("_".join(["GROUP",organism['commonName'],"USER"]) in my_groups):
                if(organism['action'] == "RELEASE"):
                    organism['action'] = "W_RELEASE"
                else:
                    organism['action'] = "RELEASE"
            else:
                if(organism['action'] == "REQUEST"):
                    organism['action'] = "W_REQUEST"
                else:
                    organism['action'] = "REQUEST"

    return HttpResponse(json.dumps(organisms), content_type="application/json")

@login_required
def get_pending_request(request):
    oid = request.GET['oid']
    perm_request_array = PermsRequest.objects.filter(oid=oid, status="PENDING").all()
    user_action = {}
    for perm_request in perm_request_array:
        apollo_name = _django_user_to_apollo_name(perm_request.user_apply)
        user_action[apollo_name] = perm_request.action

    if(len(user_action) == 0):
        return HttpResponse(json.dumps({}), content_type="application/json")

    opener = _get_login()
    response = opener.open("http://localhost:8085/apollo/user/loadUsers")
    users = json.loads(response.read())

    #may be improve efficency
    result = []
    for user in users:
        if(user['username'] in user_action):
           user['action'] = user_action[user['username']]
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
        data.update(_get_robot_priviledge())
        req = _get_url_request('http://localhost:8085/apollo/user/addUserToGroup')
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
        data.update(_get_robot_priviledge())

        req = _get_url_request('http://localhost:8085/apollo/user/removeUserFromGroup')
        opener = _get_url_open()
        response = opener.open(req, json.dumps(data))
        result = response.read()

        print result
        perm_request.save()
    elif(perm_request.action == "RELEASE" and action=="REFUSE"):
        perm_request.status = "REFUSED"
        perm_request.save()

    return HttpResponse(json.dumps({}), content_type="application/json")

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

    data.update(_get_robot_priviledge())
    req = _get_url_request('http://localhost:8085/apollo/user/addUserToGroup')
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

    data.update(_get_robot_priviledge())
    req = _get_url_request('http://localhost:8085/apollo/user/removeUserFromGroup')
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
    data.update(_get_robot_priviledge())
    req = _get_url_request('http://localhost:8085/apollo/user/createUser')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    print result

    if(len(result) == 0):
        response = opener.open("http://localhost:8085/apollo/user/loadUsers")
        users = json.loads(response.read())

        for user in users:
            if(user['username'] == email):
                userId = user['userId']
                break

        user_info = UserMapping.objects.create(apollo_user_id=userId,
                                               apollo_user_name=email,
                                               apollo_user_pwd=password,
                                               django_user=User.objects.get(username=django_username) if(django_username != '') else None)
        user_info.save()

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def delete_user(request):
    user_id = request.POST['userId']
    data = {"userId" : user_id}
    data.update(_get_robot_priviledge())
    req = _get_url_request('http://localhost:8085/apollo/user/deleteUser')
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
    data.update(_get_robot_priviledge())
    if(new_password != ''):
        data['newpassword'] = new_password

    req = _get_url_request('http://localhost:8085/apollo/user/updateUser')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    print result

    if(len(result) == 0):
        try:
            user_info = UserMapping.objects.get(apollo_user_id=user_id)
            if(new_password != ''):
                user_info.apollo_user_pwd = new_password
            if(django_username != ''):
                user_info.django_user = User.objects.get(username=django_username)
            user_info.save()
        except UserMapping.DoesNotExist:
            password = User.objects.make_random_password(length=20) if request.POST['password'] == '' else request.POST['password']
            user_info = UserMapping.objects.create(apollo_user_id=user_id,
                                                   apollo_user_name=email,
                                                   apollo_user_pwd=password,
                                                   django_user=User.objects.get(username=django_username) if(django_username != '') else None)
            user_info.save()

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def disconnect_user(request):
    userId = request.POST['userId']

    user_info = UserMapping.objects.get(apollo_user_id=userId)
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
    oname = request.POST['oname']

    print oname

    group_admin = '_'.join(["GROUP", oname, "ADMIN"])
    group_user  = '_'.join(["GROUP", oname, "USER"])

    data = {"name" : group_admin}
    data.update(_get_robot_priviledge())
    data2 = {"name" : group_user}
    data2.update(_get_robot_priviledge())
    data_admin_perms = {"name": group_admin, "organism" : oname, "ADMINISTRATE" : False, "WRITE" : False, "EXPORT" : False, "READ" : False}
    data_admin_perms.update(_get_robot_priviledge())
    data_user_perms = {"name": group_user, "organism" : oname, "ADMINISTRATE" : False, "WRITE" : True, "EXPORT" : True, "READ" : True}
    data_user_perms.update(_get_robot_priviledge())

    req = _get_url_request('http://localhost:8085/apollo/group/createGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    #print result

    #req = _get_url_request('http://localhost:8085/apollo/group/updateOrganismPermission')
    #response = opener.open(req, json.dumps(data_admin_perms))
    #result = response.read()
    #print result

    req = _get_url_request('http://localhost:8085/apollo/group/createGroup')
    response = opener.open(req, json.dumps(data2))
    result = json.loads(response.read())
    #print result

    #req = _get_url_request('http://localhost:8085/apollo/group/updateOrganismPermission')
    #response = opener.open(req, json.dumps(data_user_perms))
    #result = response.read()
    #print result

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def delete_group_for_organism(request):
    oname = request.POST['oname']
    group_admin = '_'.join(["GROUP", oname, "ADMIN"])
    group_user  = '_'.join(["GROUP", oname, "USER"])

    data = {"name" : group_admin}
    data.update(_get_robot_priviledge())
    data2 = {"name" : group_user}
    data2.update(_get_robot_priviledge())

    req = _get_url_request('http://localhost:8085/apollo/group/deleteGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    print result

    req = _get_url_request('http://localhost:8085/apollo/group/deleteGroup')
    #opener = _get_url_open()
    response = opener.open(req, json.dumps(data2))
    result = json.loads(response.read())
    print result

    return HttpResponse(json.dumps({}), content_type="application/json")

def get_all_groups(request):

    opener = _get_login()
    response = opener.open("http://localhost:8085/apollo/group/loadGroups")
    groups = json.loads(response.read())

    result = []
    for group in groups:
        result.append(group['name'])

    return HttpResponse(json.dumps(result), content_type="application/json")

def check_organism_exist(request):
    organism_name = request.POST['oname']

    opener = _get_login()
    response = opener.open("http://localhost:8085/apollo/organism/findAllOrganisms")
    organisms = json.loads(response.read())

    for organism in organisms:
        print organism['commonName']
        if(organism['commonName'] == organism_name):
            return HttpResponse(json.dumps({}), content_type="application/json")

    return HttpResponse(json.dumps({"error":"Organism doesn't exist"}), content_type="application/json")
