from datetime import datetime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def dashboard(request):
    return render(
        request,
        'dashboard/index.html', {
        'year': datetime.now().year,
        'title': 'Dashboard',
    })

from rest_framework.renderers import JSONRenderer
class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

