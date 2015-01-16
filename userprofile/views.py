from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime

@login_required
def dashboard(request):
    return render(
        request,
        'userprofile/dashboard.html', {
        'year': datetime.now().year,
        'title': 'Dashboard'
    })

@login_required
def webapollo(request):
    return render(
        request,
        'userprofile/webapollo.html', {
        'year': datetime.now().year,
        'title': 'App/Web Apollo'
    })
@login_required
def settings(request):
    return render(
        request,
        'userprofile/settings.html', {
        'year': datetime.now().year,
        'title': 'Settings'
    })
