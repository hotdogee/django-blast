from django.contrib import admin
from .models import DrupalUserMapping

# Register your models here.

class DrupalUserMappingAdmin(admin.ModelAdmin):
    list_display = ('django_user', 'drupal_user_pwd','last_date')

admin.site.register(DrupalUserMapping, DrupalUserMappingAdmin)
