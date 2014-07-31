from django.contrib import admin
from blast.models import *

@admin.register(BlastQueryRecord)
class BlastQueryRecordAdmin(admin.ModelAdmin):
    pass

@admin.register(BlastDb)
class BlastDbAdmin(admin.ModelAdmin):
    pass

@admin.register(Organism)
class OrganismAdmin(admin.ModelAdmin):
    pass

@admin.register(BlastDbType)
class BlastDbTypeAdmin(admin.ModelAdmin):
    pass

@admin.register(Sequence)
class SequenceAdmin(admin.ModelAdmin):
    pass

@admin.register(JbrowseInfo)
class JbrowseInfoAdmin(admin.ModelAdmin):
    pass