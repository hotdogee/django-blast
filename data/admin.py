from django.contrib import admin
from django.contrib import messages
from django.forms import ModelForm
from .models import *

class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'hash', 'processed_hash', 'processed_date')
    readonly_fields = ('processed_date',)
    search_fields = ('id',)
    actions_on_top = True
    actions_on_bottom = True
    actions = ['process_file']

    def process_file(self, request, queryset):
        success_count = 0
        for file in queryset:
            returncode, error, output = file.process_file()
            if returncode != 0:
                self.message_user(request, "[%s] - [%s]" % (error, file.name.path_full), level=messages.ERROR)
            else:
                success_count += 1
        if success_count > 0:
            self.message_user(request, "%d entries successfully ran makeblastdb." % success_count)
    process_file.short_description = 'Process File'

    class Media:
        js = ('data/scripts/file-admin.js',)
admin.site.register(File, FileAdmin)

class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'attributes')
    search_fields = ('attributes',)
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(Item, ItemAdmin)

class AccessionAdmin(admin.ModelAdmin):
    list_display = ('accession', 'item')
    search_fields = ('accession',)
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(Accession, AccessionAdmin)