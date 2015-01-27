from django.contrib import admin
from webapollo.models import *
from django.contrib.auth.admin import UserAdmin

class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', 'host', 'db_name', 'db_acct', 'db_pwd', 'url',)
    search_fields = ['name', 'full_name']
    ordering = ['name']
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(Species, SpeciesAdmin)

class SpeciesPasswordAdmin(admin.ModelAdmin):
    search_fields = ['user__username', 'species__name', 'species__full_name']
    ordering = ['user__username']
    list_display = ('user', 'species', 'pwd',)
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(SpeciesPassword, SpeciesPasswordAdmin)

