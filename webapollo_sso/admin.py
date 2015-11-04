from django.contrib import admin
from .models import PermsRequest, UserMapping


class PermsRequestAdmin(admin.ModelAdmin):
    list_display = ('action', 'oid', 'user_apply', 'status', 'apply_date', 'apply_desc', 'reply_desc','user_reply', 'end_date')

class UserMappingAdmin(admin.ModelAdmin):
    list_display = ('apollo_user_id', 'apollo_user_name', 'apollo_user_pwd', 'django_user', 'last_date')

admin.site.register(PermsRequest, PermsRequestAdmin)
admin.site.register(UserMapping, UserMappingAdmin)
# Register your models here.
