from django.contrib import admin
from webapollo.models import *
from django.contrib.auth.admin import UserAdmin

class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', 'host', 'db_name', 'db_acct', 'db_pwd', 'url',)
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(Species, SpeciesAdmin)

class SpeciesPasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'species', 'pwd',)
admin.site.register(SpeciesPassword, SpeciesPasswordAdmin)

