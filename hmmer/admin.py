from django.contrib import admin
from .models import *
from django.forms import ModelForm
from suit.widgets import AutosizedTextarea

class HmmerDbForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 10, 'class': 'input-xxlarge'}),
        }

class HmmerDbAdmin(admin.ModelAdmin):
    form = HmmerDbForm
    list_display = ('title', 'organism', 'fasta_file', 'fasta_file_exists', 'description', 'is_shown')
    list_editable = ('is_shown',)
    list_filter = ('organism', 'is_shown',)
    search_fields = ('fasta_file','title',)
    actions_on_top = True
    actions_on_bottom = True

admin.site.register(HmmerDB, HmmerDbAdmin)

class HmmerQueryRecordAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date', 'result_status', 'user')
    fields = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date', 'result_status', 'user')
    readonly_fields = ('enqueue_date',)
    date_hierarchy = 'enqueue_date'
    list_filter = ('enqueue_date', 'dequeue_date', 'result_date', 'result_status',)
    search_fields = ('task_id',)
    ordering = ('-enqueue_date',) # descending
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(HmmerQueryRecord, HmmerQueryRecordAdmin)


