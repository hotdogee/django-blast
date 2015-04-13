from django.conf import settings

def is_login_enabled(request):
    return {
        'isLoginEnabled': settings.LOGIN_ENABLED,
    }
