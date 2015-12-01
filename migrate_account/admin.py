from django.contrib import admin

# Register your models here.

#from .models import User_account
from .models import *


class MigrateUserRecordAdmin(admin.ModelAdmin):
    list_display = ('username', 'password', 'submission_date', 'organism', 'user')
    fields = ('username', 'password', 'submission_date', 'organism', 'user')
    readonly_fields = ('submission_date',)
    date_hierarchy = 'submission_date'
    list_filter = ('submission_date', 'username', 'organism')
    search_fields = ('organism',)
    ordering = ('-organism',) # descending
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(MigrateUserRecord, MigrateUserRecordAdmin)



