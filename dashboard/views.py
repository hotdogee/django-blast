from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps
from app.views import checkOAuth


@login_required
def dashboard(request):
    species_list = []
    if apps.is_installed('webapollo'):
        from webapollo.models import Species
        from django.contrib.contenttypes.models import ContentType
        content_type = ContentType.objects.get_for_model(Species)
        perms = request.user.user_permissions.filter(content_type=content_type)
        species_set = set()    
        for perm in perms:
            species_set.add(perm.name.split('_', 2)[0])
        for sname in species_set:
            s = Species.objects.get(name=sname)
            species_list.append({
                'name': s.name,
                'full_name': s.full_name,
            })
    return render(
        request,
        'dashboard/index.html', {
        'year': datetime.now().year,
        'title': 'Dashboard',
        'species_list': species_list,
        'isOAuth': checkOAuth(request.user),
    })
