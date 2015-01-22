# coding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
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
def species(request, species):
    response = HttpResponseRedirect('http://gmod-dev.nal.usda.gov:8080/' + species + '/selectTrack.jsp')
    return response
