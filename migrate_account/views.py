from __future__ import absolute_import
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.conf import settings
from django.core.cache import cache
from uuid import uuid4
from os import path, makedirs, chmod
from blast.models import BlastDb, Organism, JbrowseSetting
from migrate_account.models import MigrateUserRecord
#from .tasks import run_clustal_task
#from clustal.models import ClustalQueryRecord
from datetime import datetime, timedelta
from pytz import timezone
import json
import traceback
import stat as Perm
import os
import re
import urllib2
import cookielib
from .forms import AddMigrationForm, ConfirmMigrationForm

# Create your views here.

def index(request):
    current_user = request.user
    organism_list = sorted([db.id, db.display_name, db.short_name] for db in Organism.objects.all())
    user_list = sorted([udb.id, udb.organism_id, udb.user_id, udb.username, udb.password] for udb in MigrateUserRecord.objects.all().filter(user_id=request.user.id))
    result_set = []

    for organism in organism_list:
        blastdb_list = sorted([bdb.id, bdb.organism_id] for bdb in BlastDb.objects.all().filter(organism_id=organism[0]))
        for blast in blastdb_list:
            jbrowse_list = sorted([jdb.id, jdb.url, jdb.blast_db_id] for jdb in JbrowseSetting.objects.all().filter(blast_db_id=blast[0]))
            for jbrowse in jbrowse_list:
                var = [organism[0], organism[1], organism[2], jbrowse[1], False, None, None]
                for user in user_list:
                    if organism[0] == user[1] and user[2] == request.user.id:
                        var = [organism[0], organism[1], organism[2], jbrowse[1], True, user[3], user[4] ]
                result_set.append(var)

    return render(request,'migrate_account/main.html',{
            'title': 'Organism Listing',
            'organism_id':organism[0], 
            'organism_display_name':organism[1], 
            'organism_short_name':organism[2], 
            'jbrowse_url':jbrowse[1],
#            'registered': True,
#            'username': user[3], 
#            'password':user[4],
            'result_set': result_set
            })

def add(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddMigrationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            organism_id = form.cleaned_data['organism_id']
            jbrowse_url =  form.cleaned_data['jbrowse_url']
            organism_display_name = form.cleaned_data['organism_display_name']
            organism_short_name = form.cleaned_data['organism_short_name']
            username =  form.cleaned_data['username']
            password =  form.cleaned_data['password']
#        return HttpResponseRedirect('/thanks/')
            m = MigrateUserRecord( username = username, password = password, organism_id = organism_id, user_id = request.user.id )
            m.save()
            return render(request, 'migrate_account/add.html', {
                    'organism_id': organism_id,
                    'organism_short_name': organism_short_name,
                    'organism_display_name': organism_display_name,
                    'jbrowse_url': jbrowse_url,
                    'username': username,
                    'password': password,
                    'title': 'Confirm something',
#                    'result_set': result_set,
                    'form': form                    
                    })
    # if a GET (or any other method) we'll create a blank form
        else:
            form = AddMigrationForm(request.POST)
#            form = AddMigrationForm()
            
            return render(request, 'migrate_account/add.html', {
                    'form': form
                    })

def confirm(request):
    return()
