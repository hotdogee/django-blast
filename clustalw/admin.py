from django.contrib import admin
from .models import *

class ClustalwQueryRecordAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date', 'result_status', 'user')
    fields = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date', 'result_status', 'user')
    readonly_fields = ('enqueue_date',)
    date_hierarchy = 'enqueue_date'
    list_filter = ('enqueue_date', 'dequeue_date', 'result_date', 'result_status',)
    search_fields = ('task_id',)
    ordering = ('-enqueue_date',) # descending
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(ClustalwQueryRecord, ClustalwQueryRecordAdmin)
