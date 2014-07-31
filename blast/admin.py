from django.contrib import admin
from blast.models import *

class BlastQueryRecordAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date')
    fields = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date')
    readonly_fields = ('enqueue_date',)
    list_filter = ('enqueue_date', 'dequeue_date', 'result_date')
    search_fields = ('task_id',)
admin.site.register(BlastQueryRecord, BlastQueryRecordAdmin)

class BlastDbAdmin(admin.ModelAdmin):
    pass
admin.site.register(BlastDb, BlastDbAdmin)

class OrganismAdmin(admin.ModelAdmin):
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