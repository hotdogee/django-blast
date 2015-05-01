from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.apps import apps
from app.views import checkOAuth


@login_required
def dashboard(request):
    species_list = []
    if apps.is_installed('webapollo'):
        from webapollo.models import Species, Registration
        from django.contrib.contenttypes.models import ContentType

        # species with permission to access
        content_type = ContentType.objects.get_for_model(Species)
        perms = request.user.user_permissions.filter(content_type=content_type)
        species_set = set()
        owner_set = set() # species with coordinator/owner permission
        for perm in perms:
            p = perm.name.split('_', 2)
            species_set.add(p[0])
            if p[1] == 'owner':
                owner_set.add(p[0])
        for sname in species_set:
            s = Species.objects.get(name=sname)
            species_list.append({
                'name': s.name,
                'full_name': s.full_name,
            })
        species_list.sort(key=lambda x: x['name'])

        # pending requests for the owner
        pendings = Registration.objects.filter(species__name__in=owner_set, status='Pending').order_by('species', 'submission_time')

    return render(
        request,
        'dashboard/index.html', {
        'year': datetime.now().year,
        'title': 'Dashboard',
        'species_list': species_list,
        'pendings': pendings,
        'isOAuth': checkOAuth(request.user),
    })
