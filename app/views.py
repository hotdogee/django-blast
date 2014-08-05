# Create your views here.
from django.shortcuts import render
from django.http import HttpRequest
from django.template import RequestContext
from datetime import datetime
from django.conf import settings

def home(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        RequestContext(request,
        {
            'title': 'Home Page',
            'year': datetime.now().year,
        })
    )

def contact(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        RequestContext(request,
        {
            'title': 'Contact',
            'message': 'National Agricultural Library',
            'year': datetime.now().year,
        })
    )

def about(request):
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        RequestContext(request,
        {
            'title': 'About i5k - BLAST',
            'message': 'django-blast',
            'year': datetime.now().year,
        })
    )
