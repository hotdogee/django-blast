from social_django.middleware import SocialAuthExceptionMiddleware
from social_core.exceptions import AuthCanceled
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled:
            return HttpResponseRedirect(reverse('login'))
            #return render(request, "pysocial/authcancelled.html", {})
        else:
            pass
