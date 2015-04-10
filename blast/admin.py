from django.contrib import admin
from blast.models import *
from django.forms import ModelForm
from suit.widgets import AutosizedTextarea
from django.contrib import messages

class BlastQueryRecordAdmin(admin.ModelAdmin):
    list_display = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date', 'result_status', 'user', 'is_shown')
    fields = ('task_id', 'enqueue_date', 'dequeue_date', 'result_date', 'result_status', 'user', 'is_shown')
    readonly_fields = ('enqueue_date',)
    date_hierarchy = 'enqueue_date'
    list_filter = ('enqueue_date', 'dequeue_date', 'result_date', 'result_status',)
    search_fields = ('task_id',)
    ordering = ('-enqueue_date',) # descending
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(BlastQueryRecord, BlastQueryRecordAdmin)

class BlastDbForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 10, 'class': 'input-xxlarge'}),
        }

class BlastDbAdmin(admin.ModelAdmin):
    form = BlastDbForm
    list_display = ('title', 'organism', 'type', 'fasta_file', 'fasta_file_exists', 'blast_db_files_exists', 'sequence_set_exists','description', 'is_shown',)
    list_editable = ('is_shown',)
    list_filter = ('organism', 'type', 'is_shown',)
    search_fields = ('fasta_file','title',)
    actions_on_top = True
    actions_on_bottom = True
    # file_exist
    # db_status
    # (re)makeblastdb - delete existing database files if exist
    # (re)populate sequence table - delete existing sequence entries if exist
    # sequence table status?
    # fasta file change date
    # makeblastdb date
    # populate sequence table date
    actions = ['makeblastdb', 'index_fasta']

    def makeblastdb(self, request, queryset):
        success_count = 0
        for blastdb in queryset:
            returncode, error, output = blastdb.makeblastdb()
            if returncode != 0:
                self.message_user(request, "[%s] - [%s]" % (error, blastdb.fasta_file.path_full), level=messages.ERROR)
            else:
                success_count += 1
        if success_count > 0:
            self.message_user(request, "%d entries successfully ran makeblastdb." % success_count)
    makeblastdb.short_description = 'Run makeblastdb on selected entries, replaces existing files'

    def index_fasta(self, request, queryset):
        success_count = 0
        for blastdb in queryset:
            returncode, error, output = blastdb.index_fasta()
            if returncode != 0:
                self.message_user(request, "[%s] - [%s]" % (error, blastdb.fasta_file.path_full), level=messages.ERROR)
            else:
                success_count += 1
        if success_count > 0:
            self.message_user(request, "%d entries successfully added to Sequences table." % success_count)
    index_fasta.short_description = 'Populate Sequences table, replaces existing Sequence entries'

    class Media:
        js = ('blast/scripts/blastdb-admin.js',)
admin.site.register(BlastDb, BlastDbAdmin)

class OrganismForm(ModelForm):
    class Meta:
        widgets = {
            'description': AutosizedTextarea(attrs={'rows': 10, 'class': 'input-xxlarge'}),
        }

class OrganismAdmin(admin.ModelAdmin):
    form = OrganismForm
    list_display = ('display_name', 'short_name', 'tax_id', 'short_description',)
    search_fields = ('display_name', 'short_name', 'tax_id', 'description',)
    actions_on_top = True
    actions_on_bottom = True

    def short_description(self, obj):
        if len(obj.description) < 100:
            return obj.description
        else:
            return obj.description[:100] + '...'
    short_description.short_description = 'description'
    class Media:
        css = {
            'all': ('blast/css/organism-admin.css',)
        }
        js = ('blast/scripts/organism-admin.js',)
admin.site.register(Organism, OrganismAdmin)

class SequenceTypeAdmin(admin.ModelAdmin):
    list_display = ('molecule_type', 'dataset_type',)
    search_fields = ('molecule_type', 'dataset_type',)
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(SequenceType, SequenceTypeAdmin)

class SequenceForm(ModelForm):
    class Meta:
        widgets = {
            'sequence': AutosizedTextarea(attrs={'rows': 10, 'class': 'input-xxlarge'}),
        }

class SequenceAdmin(admin.ModelAdmin):
    #form = SequenceForm
    list_display = ('id', 'blast_db', 'length', 'modified_date',)
    readonly_fields = ('modified_date',)
    list_filter = ('blast_db',)
    search_fields = ('id',)
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(Sequence, SequenceAdmin)

class JbrowseSettingAdmin(admin.ModelAdmin):
    list_display = ('blast_db', 'url',)
    actions_on_top = True
    actions_on_bottom = True
admin.site.register(JbrowseSetting, JbrowseSettingAdmin)
