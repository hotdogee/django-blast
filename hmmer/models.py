from django.db import models
from django.contrib.auth.models import User
from blast.models import Organism
from filebrowser.fields import FileBrowseField
import os.path
import i5k.settings

class HmmerQueryRecord(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)
    result_status = models.CharField(max_length=32, default='WAITING') # ex. WAITING, SUCCESS, NO_ASN, ASN_EMPTY, NO_CSV, CSV_EMPTY
    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        verbose_name = 'Hmmer result'

class HmmerDB(models.Model):
    organism = models.ForeignKey(Organism, default=0) #
    fasta_file = FileBrowseField('FASTA file path', max_length=100, directory='hmmer/db/', extensions='FASTA', format='FASTA', default='')
    title = models.CharField(max_length=200, unique=True, default='') # makeblastdb -title
    description = models.TextField(blank=True) # shown in hmmer db selection ui
    is_shown = models.BooleanField(default=None, help_text='Display this database in the HMMER submit form') # to temporarily remove from hmmer db selection ui

    def fasta_file_exists(self):
        return os.path.isfile(self.fasta_file.path_full)

    fasta_file_exists.boolean = True
    fasta_file_exists.short_description = 'fasta file exists'
# Create your models here.
