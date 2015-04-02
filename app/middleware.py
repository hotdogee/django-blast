from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from social.exceptions import AuthCanceled
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return HttpResponseRedirect(reverse('login'))
            #return render(request, "pysocial/authcancelled.html", {})
        else:
            pass
