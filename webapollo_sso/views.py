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

#global configuration
_APOLLO_URL = i5k.settings.APOLLO_URL

def _get_login(request, user_password = None):
    opener = _get_url_open()
    if user_password == None:
        response = opener.open(_get_url_request(request.session['apollo_url']+'/Login?operation=login'),
                           json.dumps(_get_robot_priviledge()))
    else:
        response = opener.open(_get_url_request(request.session['apollo_url']+'/Login?operation=login'),
                           json.dumps(user_password))

    result = json.loads(response.read())
    if('error' not in result):
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
    try:
        user_mapping = UserMapping.objects.get(django_user=user)
        return user_mapping.apollo_user_name
    except UserMapping.DoesNotExist:
        return None

def _apollo_name_to_django_user(name):
    try:
        user_mapping = UserMapping.objects.get(apollo_user_name=name)
        return user_mapping.django_user
    except UserMapping.DoesNotExist:
        return None

@login_required
def create(request):
    #session variable 'apollo_url' is setted for templates
    #in views.py, use global variable APOLLO_URL
    '''
    user variables in session
    1. apollo_name: apollo account name
    2. apollo_user_id: apollo account id
    3. user_type: (1) Admin (2) Users (3) New (don't have apollo account/change passwd)
    '''
    request.session['apollo_url'] = i5k.settings.APOLLO_URL


    try:
        #Login fail, maybe change password from Apollo
        user_mapping = UserMapping.objects.get(django_user=request.user)
        data = {'username':user_mapping.apollo_user_name, 'password':decodeAES(user_mapping.apollo_user_pwd)}
        opener = _get_login(request, data)
        if opener == None:
            return render(request, 'webapollo_sso/main.html', {
                'title': 'SSO',
                'user_type': 'PWD_CHANGED',
                'apollo_user_name': user_mapping.apollo_user_name,
                'i5k_user_name': request.user.username,
                'I5K_URL': i5k.settings.I5K_URL,
                'APOLLO_URL': i5k.settings.APOLLO_URL,
            })
        opener.close()
    except UserMapping.DoesNotExist:
        #NO record in UserMapping
        return render(request, 'webapollo_sso/main.html', {
                'title': 'SSO',
                'user_type': 'NEW',
                'i5k_user_name': request.user.username,
                'I5K_URL': i5k.settings.I5K_URL,
                'APOLLO_URL': i5k.settings.APOLLO_URL,
        })

    #Manatory variables
    if('apollo_name' not in request.session or 'apollo_user_id' not in request.session):
        request.session['apollo_name'] = user_mapping.apollo_user_name
        request.session['apollo_user_id'] = user_mapping.apollo_user_id

    if('user_type' not in request.session):
        opener = _get_login(request)
        req = _get_url_request(_APOLLO_URL+'/user/loadUsers')
        response = opener.open(req, json.dumps({"userId" : request.session['apollo_user_id']}))
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


    req = _get_url_request(_APOLLO_URL+'/user/loadUsers')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(_get_robot_priviledge()))
    users = json.loads(response.read())

    #User management page of myOrganism (User Collapsible)
    #check priviledge of different organisms, only return info with legal access
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

    #User management page of User Admin
    #look up mapping between django_user and apollo_user
    #DISCONNECTED means an unowned apollo account
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

    opener.close()
    return HttpResponse(json.dumps(users), content_type="application/json")

@login_required
def get_groups(request):

    req = _get_url_request(_APOLLO_URL+'/group/loadGroups')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(_get_robot_priviledge()))
    groups = json.loads(response.read())

    result = []
    '''
    This SSO system only recogize two kinds of organized group_name,
    others group will not be managed by SSO.

    1.'GROUP_(short_organism_name)_USER': none-admin
    2.'GROUP_(short_organism_name)_ADMIN': FULL of priviledges (ADMIN/WRITE/READ)
    '''
    for group in groups:
        m = re.match(r"GROUP_(\w+)_(USER|ADMIN)", group['name'])
        if(m != None):
            oname = m.group(1)

            for organism_perm in group['organismPermissions']:
                if(oname == get_short_name(request, organism_perm['organism'])):
                    group['permission'] = organism_perm
                    group['fullname'] = organism_perm['organism']
                    del group['organismPermissions']
                    result.append(group)
                    break

    opener.close()
    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def get_my_organism(request):

    req = _get_url_request(_APOLLO_URL+'/user/loadUsers')
    opener = _get_url_open()
    data = _get_robot_priviledge()
    data.update({"userId" : request.session['apollo_user_id']})
    response = opener.open(req, json.dumps(data))
    user = json.loads(response.read())[0]

    '''
    cache results of 'findAllOrganisms' in 
    session variable 'allOrganism' in first time query.
    '''
    if('allOrganism' in request.session):
        organisms = request.session['allOrganism']
    else:
        response = opener.open(_APOLLO_URL+'/organism/findAllOrganisms')
        organisms = json.loads(response.read())
        request.session['allOrganism'] = organisms

    result = {}
    user_groups = map(lambda x:x['name'], user['groups'])
   
    '''
    return objects format(dictionary)
    key, (organism_commonName)_(orgnism_id)
    value, [ADMIN or not, pending request or not, organism short name]
    '''
    for organism in organisms:
        perms = PermsRequest.objects.filter(oid=organism['id'], status="PENDING").all();
        is_pending_request = True if (len(perms) != 0) else False;

        short_name = get_short_name(request, organism['commonName'], organism['id'])
        if(short_name != None):
            if("_".join(["GROUP",short_name,"ADMIN"]) in user_groups):
                result[organism['commonName']+"_"+str(organism['id'])] = [True,is_pending_request,short_name]
            elif("_".join(["GROUP",short_name,"USER"]) in user_groups):
                result[organism['commonName']+"_"+str(organism['id'])] = [False,is_pending_request,short_name]

    opener.close()
    
    return HttpResponse(json.dumps(OrderedDict(sorted(result.items()))), content_type="application/json")

@login_required
def get_my_request(request):
    '''
    My Request page
    action: apply condition for each organism ('action' colume in table PermsRequest)
            'RELEASE': ask for leaving,
            'W_RELEASE': waiting for leaving approval,
            'REQUEST': ask for joining,
            'W_REQUEST': waiting for joining approval

    admin: admin or not
    '''
    req = _get_url_request(_APOLLO_URL+'/user/loadUsers')
    opener = _get_url_open()
    data = _get_robot_priviledge()
    data.update({"userId" : request.session['apollo_user_id']})
    response = opener.open(req, json.dumps(data))
    user = json.loads(response.read())[0]
   
    if('allOrganism' in request.session):
        organisms = request.session['allOrganism']
    else:
        response = opener.open(_APOLLO_URL+'/organism/findAllOrganisms')
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

        short_name = get_short_name(request, organism['commonName'], organism['id'])

        #NO short_name in Django table Organism
        if(short_name == None):
            continue

        if("_".join(["GROUP",short_name,"ADMIN"]) in my_groups):
            organism['admin'] = True
            organism['action'] = None
        else:
            organism['admin'] = False
            try:
                #query by current user and specific organism
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

    opener.close()
    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def get_pending_request(request):
    '''
    My Organism page, 'Pending Request Collapsible' click
    '''

    oid = request.GET['oid']
    #query specific organism
    perm_request_array = PermsRequest.objects.filter(oid=oid, status="PENDING").all()
    user_action = {}
    for perm_request in perm_request_array:
        apollo_name = _django_user_to_apollo_name(perm_request.user_apply)
        #key: apollo_name, value:[action, apply_desc]
        user_action[apollo_name] = [perm_request.action, perm_request.apply_desc]

    #no request record now.
    if(len(user_action) == 0):
        return HttpResponse(json.dumps({}), content_type="application/json")

    data = {}
    data.update(_get_my_priviledge(request))
    req = _get_url_request(_APOLLO_URL+'/user/loadUsers')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    users = json.loads(response.read())

    #efficency may be improved
    #query user involved one by one
    result = []
    count = len(user_action) #for efficency
    for user in users:
        if count == 0:
            break
        if(user['username'] in user_action):
            user['action'] = user_action[user['username']][0]
            user['desc'] = user_action[user['username']][1]
            del user['organismPermissions']
            del user['availableGroups']
            result.append(user)
            count-=1

    opener.close()
    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def make_request(request):
    '''
    Ask request or relase permission for specific organism
    '''
    oid =  request.POST['oid']
    oname = request.POST['oname']
    action = request.POST['action']
    apply_desc = request.POST['apply_desc']

    #remove record
    try:
        #for each user and organism pair, there should only one record in PermsRequest
        #delete old one, before insert new one.
        perm_request = PermsRequest.objects.get(oid=oid, user_apply=request.user, status="PENDING")
        perm_request.delete()
    except PermsRequest.DoesNotExist:
        pass

    try:
        if(action == "RELEASE" or action == "REQUEST"):
            perm_request = PermsRequest.objects.create(action=action, oid=oid, oname=oname, 
                    user_apply=request.user, status="PENDING", apply_desc=apply_desc)
            perm_request.save()
        return HttpResponse(json.dumps({}), content_type="application/json")

    except:
        return HttpResponse(json.dumps({"error":"System error"}), content_type="application/json")

@login_required
def handle_request(request):
    '''
    Approve/Deny other's request 
    '''
    action = request.POST['action'] #decision
    oid    = request.POST['oid'] #organism id
    oname  = request.POST['oname'] #organism name
    user_apollo   = request.POST['user']
    userId_apollo = request.POST['userId']
    user = _apollo_name_to_django_user(user_apollo)
    reply_desc = request.POST['reply_desc'] #reason of decision

    perm_request = PermsRequest.objects.get(oid=oid, user_apply=user, status="PENDING")
    perm_request.reply_desc = reply_desc
    perm_request.user_reply = request.user #who did this decision

    
    if(perm_request.action == "REQUEST" and action=="ACCEPT"):
        #ask for permission and get approved
        perm_request.status = "ACCEPTED"

        data = {"group":"GROUP_"+oname+"_USER", "userId":userId_apollo}
        data.update(_get_my_priviledge(request))
        req = _get_url_request(_APOLLO_URL+'/user/addUserToGroup')
        opener = _get_url_open()
        response = opener.open(req, json.dumps(data))
        result = json.loads(response.read())
        if len(result) == 0:
            perm_request.save()
        opener.close()
    elif(perm_request.action == "REQUEST" and action=="REFUSE"):
        #ask for permission and get refused
        perm_request.status = "REFUSED"
        perm_request.save()
    elif(perm_request.action == "RELEASE" and action=="ACCEPT"):
        #ask for leaving and get approved
        perm_request.status = "ACCEPTED"

        data = {"group":"GROUP_"+oname+"_USER", "userId":userId_apollo}
        data.update(_get_my_priviledge(request))
        req = _get_url_request(_APOLLO_URL+'/user/removeUserFromGroup')
        opener = _get_url_open()
        response = opener.open(req, json.dumps(data))
        result = json.loads(response.read())
        if len(result) == 0:
            perm_request.save()
        opener.close()
    elif(perm_request.action == "RELEASE" and action=="REFUSE"):
        #ask for leaving and get refused
        perm_request.status = "REFUSED"
        perm_request.save()

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def add_user_to_group(request):
    '''
    Used in two places
    1. User(Admin), Group tab, click group button
    2. Group(Admin), Member tab, Search User for recruit users.
    '''
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

    req = _get_url_request(request.session['apollo_url']+'/user/addUserToGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    opener.close()

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def remove_user_from_group(request):
    '''
    Used in two places
    1. User(Admin), Group tab, click group button
    2. Group(Admin), Member tab, click group button
    '''
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

    req = _get_url_request(_APOLLO_URL+'/user/removeUserFromGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())
    opener.close()

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def create_user(request):
    '''
    Used in User(Admin) page
    Create an apollo user (not manatory to bind a django user)
    '''
    first_name = request.POST['firstName']
    last_name  = request.POST['lastName']
    email      = request.POST['userName']
    django_username = request.POST['djangoUserName']
    #generate password randomly or get from user input.
    password = User.objects.make_random_password(length=20) if request.POST['password'] == '' else request.POST['password']

    #password format checking??

    data = {"firstName" : first_name, "lastName" : last_name, "email": email, "new_password" : password, "role" : "USER"}
    data.update(_get_my_priviledge(request))

    req = _get_url_request(_APOLLO_URL+'/user/createUser')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    opener.close()

    if(len(result) == 0):
        #query for new user id

        data = {"userId": email}
        data.update(_get_robot_priviledge())

        req = _get_url_request(_APOLLO_URL+'/user/loadUsers')
        opener = _get_url_open()
        response = opener.open(req, json.dumps(data))
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

    opener.close()
    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def delete_user(request):
    '''
    Used in User(Admin)
    '''
    user_id = request.POST['userId']
    data = {"userId" : user_id}
    data.update(_get_my_priviledge(request))

    req = _get_url_request(_APOLLO_URL+'/user/deleteUser')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    opener.close()

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def update_user(request):
    '''
    Used in User(Admin) page
    '''
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

    req = _get_url_request(_APOLLO_URL+'/user/updateUser')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())


    opener.close()

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
            #for secure
            #return HttpResponse(json.dumps({'error':'User not existed'}), content_type="application/json")
            
            password = encodeAES(User.objects.make_random_password(length=20)) if new_password == '' else encodeAES(new_password)
            user_info = UserMapping.objects.create(apollo_user_id=user_id,
                                                   apollo_user_name=email,
                                                   apollo_user_pwd=password,
                                                   django_user=User.objects.get(username=django_username) if(django_username != '') else None)
            user_info.save()
            

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def disconnect_user(request):
    '''
    Used in User(Admin) page
    '''
    user_info = UserMapping.objects.get(apollo_user_id=request.POST['userId'])
    user_info.django_user = None
    user_info.save()
    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def check_django_user_available(request):
    '''
    Used in User(Admin) page, called in AJAX
    check whether django_user whether is already binded to apollo_user
    '''
    username = request.POST['userName']

    if username == '':
        return HttpResponse(json.dumps({"empty":""}), content_type="application/json")

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
    '''
    Used in Group(Admin), Detail tab, Create button.
    Create GROUP_(name)_ADMIN and GROUP_(name)_USER at the same time.
    GROUP_(name)_ADMIN with no priviledge. 
    GROUP_(name)_USER with WRITE/EXPORT/READ
    '''
    full_name =  request.POST['fullName']
    short_name = request.POST['shortName']

    group_admin = '_'.join(["GROUP", short_name, "ADMIN"])
    group_user  = '_'.join(["GROUP", short_name, "USER"])

    data = {"name" : group_admin}
    data.update(_get_my_priviledge(request))
    data2 = {"name" : group_user}
    data2.update(_get_my_priviledge(request))

    data_admin_perms = {"name": group_admin, "organism" : full_name, 
            "ADMINISTRATE" : False, "WRITE" : False, "EXPORT" : False, "READ" : False}
    data_admin_perms.update(_get_my_priviledge(request))
    data_user_perms = {"name": group_user, "organism" : full_name, 
            "ADMINISTRATE" : False, "WRITE" : True,  "EXPORT" : True,  "READ" : True}
    data_user_perms.update(_get_my_priviledge(request))

    #create Admin group
    req = _get_url_request(_APOLLO_URL+'/group/createGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    #grant permission to Admin group
    req = _get_url_request(_APOLLO_URL+'/group/updateOrganismPermission')
    response = opener.open(req, json.dumps(data_admin_perms))
    result = json.loads(response.read())

    #create User group
    req = _get_url_request(_APOLLO_URL+'/group/createGroup')
    response = opener.open(req, json.dumps(data2))
    result = json.loads(response.read())

    #grant permission to User group
    req = _get_url_request(_APOLLO_URL+'/group/updateOrganismPermission')
    response = opener.open(req, json.dumps(data_user_perms))
    result = json.loads(response.read())

    opener.close()

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def delete_group_for_organism(request):
    '''
    Used in Group(Admin), Detail tab, delete button.
    Delete GROUP_(name)_ADMIN and GROUP_(name)_USER at the same time.
    ''' 
    oname = request.POST['oname']
    group_admin = '_'.join(["GROUP", oname, "ADMIN"])
    group_user  = '_'.join(["GROUP", oname, "USER"])

    data = {"name" : group_admin}
    data.update(_get_my_priviledge(request))
    data2 = {"name" : group_user}
    data2.update(_get_my_priviledge(request))

    #delete Admin group
    req = _get_url_request(_APOLLO_URL+'/group/deleteGroup')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    #delete User group
    req = _get_url_request(_APOLLO_URL+'/group/deleteGroup')
    response = opener.open(req, json.dumps(data2))
    result = json.loads(response.read())
    opener.close()

    return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def get_all_groups(request):
    '''
    Load existed groups shortname for User(Admin), Group table.
    Return a list of organism shortname
    '''
    req = _get_url_request(_APOLLO_URL+'/group/loadGroups')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(_get_robot_priviledge()))
    groups = json.loads(response.read())
    opener.close()

    result = []
    for group in groups:
        m = re.match(r"GROUP_(\w+)_(USER|ADMIN)", group['name'])
        if(m != None):
            result.append(group['name'])

    return HttpResponse(json.dumps(sorted(result)), content_type="application/json")

@login_required
def check_organism_exist(request):
    '''
    Used in Group(Admin) page, Detail tab, Organism Name inputbox, called in AJAX
    check whether organism(fullname) exist or not.
    ''' 
    organism_name = request.POST['oname']

    req = _get_url_request(_APOLLO_URL+'/organism/findAllOrganisms')
    opener = _get_url_open()
    response = opener.open(req, json.dumps(_get_robot_priviledge()))
    organisms = json.loads(response.read())
    opener.close()

    for organism in organisms:
        if(organism['commonName'] == organism_name):
            short_name = get_short_name(request, organism['commonName'])
            if(short_name != None):
                return HttpResponse(json.dumps({"short_name" : short_name}), content_type="application/json")
            else:
                break

    return HttpResponse(json.dumps({"error":"Organism doesn't exist"}), content_type="application/json")

@login_required
def apollo_connect(request):
    '''
    Used in My Organism, Launch, login into Apollo
    '''
    user_mapping = UserMapping.objects.get(django_user=request.user)
    #get account name and password
    data = {'username':user_mapping.apollo_user_name, 'password':decodeAES(user_mapping.apollo_user_pwd)}

    req = urllib2.Request(_APOLLO_URL+'/Login?operation=login')
    req.add_header('Content-Type', 'application/json')

    cookies = cookielib.LWPCookieJar()
    handlers = [
        urllib2.HTTPHandler(),
        urllib2.HTTPSHandler(),
        urllib2.HTTPCookieProcessor(cookies)
        ]
    opener = urllib2.build_opener(*handlers)

    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    if len(result) != 0:
        return HttpResponse(json.dumps(result), content_type="application/json")

    response = HttpResponseRedirect(request.session['apollo_url']+'/annotator/loadLink?organism='+request.GET['oid'])

    #set sookie
    for cookie in cookies:
        if(cookie.name == 'JSESSIONID'):
            print cookie.name
            print cookie.value
            print cookie.domain
            print cookie.path
            print cookie.expires
            response.set_cookie(key=cookie.name, value=cookie.value, domain=i5k.settings.APOLLO_COOKIE_DOMAIN, path=cookie.path, expires=cookie.expires)

    return response

@login_required
def get_pending_request_admin(request):
    '''
    Used in PendingReq(Admin)
    List all pending request 
    '''
    perm_request_array = PermsRequest.objects.filter(status="PENDING").all()

    if len(perm_request_array) > 0:
        result = []
        for perm_request in perm_request_array:
            apollo_name = _django_user_to_apollo_name(perm_request.user_apply)
            if apollo_name == None:
                continue
            result.append({'apollo_name':apollo_name, 
                'action':perm_request.action, 
                'oname':perm_request.oname, 
                'desc':perm_request.apply_desc, 
                'date':perm_request.apply_date.strftime("%Y-%m-%d %H:%M:%S")})

        return HttpResponse(json.dumps(result), content_type="application/json")
    else:
        return HttpResponse(json.dumps({}), content_type="application/json")

@login_required
def get_my_reqhist(request):
    '''
    Used in My Info page, Request History section
    '''
    perms_request_array = PermsRequest.objects.filter(user_apply=request.user).all()

    result=[]
    for perms_request in perms_request_array:
        result.append({'req_type':perms_request.action, 'oname':perms_request.oname,
                       'apply_date':perms_request.apply_date.strftime("%Y-%m-%d %H:%M:%S"),
                       'apply_note':perms_request.apply_desc,
                       'reply_date':perms_request.end_date.strftime("%Y-%m-%d %H:%M:%S")
                       if perms_request.end_date.strftime("%Y-%m-%d %H:%M:%S") != perms_request.apply_date.strftime("%Y-%m-%d %H:%M:%S")
                       else None,
                       'reply_note':perms_request.reply_desc,
                       'reply_user':perms_request.user_reply.username if perms_request.user_reply !=None else None,
                       'status':perms_request.status})

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def update_group_permissions(request):
    '''
    Used in Group(Admin), Organism tab, permission button
    currently update read/write/export 
    '''
    read_p = request.POST['read_p']
    write_p = request.POST['write_p']
    export_p = request.POST['export_p']
    full_name = request.POST['fullName']
    group_name = request.POST['groupName']

    data = {"name": group_name, "organism" : full_name, "ADMINISTRATE" : False, "WRITE" : write_p, "EXPORT" : export_p, "READ" : read_p}
    #personal priviledge
    data.update(_get_my_priviledge(request))

    opener = _get_url_open()
    req = _get_url_request(_APOLLO_URL+'/group/updateOrganismPermission')
    response = opener.open(req, json.dumps(data))
    result = json.loads(response.read())

    return HttpResponse(json.dumps(result), content_type="application/json")

@login_required
def register_newUser(request):
    '''
    Used in New User page
    When a django user who doesn't bind to a apollo account
    System asks user to register apollo account info or create a new apollo account
    '''
    uname = request.POST['userName']
    pwd = request.POST['password']

    is_empty_account = True
    try:
        user_mapping = UserMapping.objects.get(apollo_user_name=uname)
        if user_mapping.django_user == None:
            pass
        elif user_mapping.django_user != request.user:
            is_empty_account = "OTHERS"
    except UserMapping.DoesNotExist:
        is_empty_account = "NO_RECORD"

    if(is_empty_account == 'OTHERS'):
        return HttpResponse(json.dumps({'error':'This account is used by others.'}), content_type="application/json")
    else:
        opener = _get_url_open()
        response = opener.open(_get_url_request(request.session['apollo_url']+'/Login?operation=login'),
                               json.dumps({'username':uname, 'password':pwd}))
        result = json.loads(response.read())

        if(len(result)==0):
            if(is_empty_account == 'NO_RECORD'):
                    opener = _get_login(request)
                    response = opener.open(request.session['apollo_url']+'/user/loadUsers')
                    users = json.loads(response.read())
                    for user in users:
                        if(user['username'] == uname):
                            user_mapping = UserMapping.objects.create(apollo_user_id=user['userId'],
                                                                      apollo_user_name=uname,
                                                                      apollo_user_pwd=encodeAES(pwd),
                                                                      django_user=request.user)
                            break

            else:
                user_mapping.django_user=request.user
                user_mapping.apollo_user_pwd=encodeAES(pwd)

            user_mapping.save()
            return HttpResponse(json.dumps({}), content_type="application/json")
        else:
            return HttpResponse(json.dumps({'error':'Login fail'}), content_type="application/json")



def encodeAES(password):
    '''
    encodeAES and decodeAES
    Use AES to encrypt user password.
    The AES cipher must be either 16, 24, or 32 bytes long
    '''
    BLOCK_SIZE = 32
    PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    cipher = AES.new(i5k.settings.SSO_CIPHER)
    encoded = base64.b64encode(cipher.encrypt(pad(password)))
    return encoded

def decodeAES(encoded):
    PADDING = '{'
    cipher = AES.new(i5k.settings.SSO_CIPHER)
    decoded  = cipher.decrypt(base64.b64decode(encoded)).rstrip(PADDING)
    return decoded

def get_short_name(request, display_name, OID=-1):
    '''
    Organism: full_name to short_name
    Name mapping in Table Organism(display_name, short_name)
    Make caches with two keys (display_name and oid-(OID))
    '''
    if(display_name in request.session):
        return request.session[display_name]

    if("-" in display_name):
        #remove additional info after display_name
        #ex. Agrilus planipennis - xxxx xxxxx
        display_name = display_name[0:display_name.index("-")].strip()
    try:
        o = Organism.objects.get(display_name=display_name);
        short_name = o.short_name
        short_name = short_name.upper()
    except Organism.DoesNotExist:
        short_name = None
    
    #make short_name in cache
    request.session[display_name] = short_name
    if(OID != -1):
        request.session['oid-'+str(OID)] = short_name

    return short_name

