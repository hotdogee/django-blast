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

from .forms import AddMigrationForm 

# Create your views here.

def index(request):


    organism_list = sorted([db.id, db.display_name, db.short_name] for db in Organism.objects.all())
    blastdb_list = sorted([bdb.id, bdb.organism_id] for bdb in BlastDb.objects.all())
    jbrowse_list = sorted([jdb.id, jdb.url, jdb.blast_db_id] for jdb in JbrowseSetting.objects.all())
    user_list = sorted([udb.id, udb.organism_id, udb.user_id] for udb in MigrateUserRecord.objects.all())

    return render(request,'migrate_account/main.html',{
            'title': 'Organism Listing', 
            'user_list': user_list,
            'blastdb_list': blastdb_list,
            'jbrowse_list': jbrowse_list,
            'organism_list': organism_list
        })

def add(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AddMigrationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            organism_id = form.cleaned_data['organism_id']
            jbrowse_url =  form.cleaned_data['jbrowse_url']
#            username =  form.cleaned_data['username']
#            password =  form.cleaned_data['password']
#        return HttpResponseRedirect('/thanks/')
        return render(request, 'migrate_account/add.html', {'form': form})
    # if a GET (or any other method) we'll create a blank form
    else:
        form = AddMigrationForm()
        
        return render(request, 'migrate_account/add.html', {'form': form})
