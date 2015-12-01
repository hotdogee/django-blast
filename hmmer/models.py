from django.db import models
from django.contrib.auth.models import User
from blast.models import Organism
from filebrowser.fields import FileBrowseField

class HmmerQueryRecord(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)
    result_status = models.CharField(max_length=32, default='WAITING') # ex. WAITING, SUCCESS, NO_ASN, ASN_EMPTY, NO_CSV, CSV_EMPTY
    user = models.ForeignKey(User, null=True, blank=True)

class HmmerDB(models.Model):
    organism = models.ForeignKey(Organism, default=0) #
    fasta_file = FileBrowseField('FASTA file path', max_length=100, directory='hmmer/db/', extensions='FASTA', format='FASTA', default='')
    title = models.CharField(max_length=200, unique=True, help_text='This is passed into makeblast -title', default='') # makeblastdb -title
    description = models.TextField(blank=True) # shown in hmmer db selection ui
    is_shown = models.BooleanField(default=None, help_text='Display this database in the HMMER submit form') # to temporarily remove from hmmer db selection ui
# Create your models here.
