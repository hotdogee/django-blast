from django.contrib import admin
from blast.models import *
from django.forms import ModelForm
from suit.widgets import AutosizedTextarea

class BlastQueryRecordAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date')
    fields = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date')
    readonly_fields = ('enqueue_date',)
    list_filter = ('enqueue_date', 'dequeue_date', 'result_date')
    search_fields = ('task_id',)
    ordering = ('-enqueue_date',) # descending
admin.site.register(BlastQueryRecord, BlastQueryRecordAdmin)

class BlastDbAdmin(admin.ModelAdmin):
    pass
admin.site.register(BlastDb, BlastDbAdmin)

class OrganismForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 10, 'class': 'input-xxlarge'}),
        }

class OrganismAdmin(admin.ModelAdmin):
    form = OrganismForm
    #fieldsets = (
    #    (None, {
    #        'fields': ('display_name', 'short_name', 'tax_id')
    #    }),
    #    ('Description', {
    #        'classes': ('full-width',),
    #        'fields': ('description',)
    #    }),
    #)
    class Media:
        js = ('blast/scripts/organism-admin.js',)
admin.site.register(Organism, OrganismAdmin)

class BlastDbTypeAdmin(admin.ModelAdmin):
    list_display = ('molecule_type', 'dataset_type')
    pass
admin.site.register(BlastDbType, BlastDbTypeAdmin)

class SequenceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Sequence, SequenceAdmin)

class JbrowseInfoAdmin(admin.ModelAdmin):
    pass
admin.site.register(JbrowseInfo, JbrowseInfoAdmin)