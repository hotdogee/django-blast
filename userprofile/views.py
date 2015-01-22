from datetime import datetime
from sets import Set
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from .forms import InfoChangeForm
from webapollo.models import Species

@login_required
def dashboard(request):
    content_type = ContentType.objects.get_for_model(Species)
    perms = request.user.user_permissions.all()
    species_names = Set()
    for perm in perms:
        if perm.content_type == content_type:
            species_names.add(perm.name.split('_', 1)[0])
    species_list = []
    for sname in species_names:
        species = Species.objects.get(name=sname)
        species_list.append({'name': sname, 'full_name': species.full_name,})
    species_list.sort(key=lambda k:k['name'])
    return render(
        request,
        'userprofile/dashboard.html', {
        'year': datetime.now().year,
        'title': 'Dashboard',
        'species_list': species_list,
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

@login_required
def info_change(request):
    u = User.objects.get(pk=request.user.id)
    msg = ''
    if request.method == 'POST':
        form = InfoChangeForm(request.POST, instance=u)
        if form.is_valid():
            form.save()
            msg = 'Your personal info was changed.'
    else: # request.method == 'GET'
        form = InfoChangeForm(instance=u)

    return render(
        request,
        'userprofile/info_change.html', {
        'year': datetime.now().year,
        'title': 'Change Personal Info',
        'form': form,
        'msg': msg,
    })
