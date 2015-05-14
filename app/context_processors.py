from django.conf import settings

def is_login_enabled(request):
    return {
        'isLoginEnabled': settings.LOGIN_ENABLED,
    }

def is_analytics_enabled(request):
    return {
        'isAnalyticsEnabled': settings.ANALYTICS_ENABLED,
    }
