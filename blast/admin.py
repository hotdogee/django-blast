from django.contrib import admin
from blast.models import *

admin.site.register(BlastQueryRecord)
admin.site.register(BlastDb)
admin.site.register(Organism)
admin.site.register(BlastDbType)
admin.site.register(Sequence)
admin.site.register(JbrowseInfo)