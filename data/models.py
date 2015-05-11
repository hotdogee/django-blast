from django.db import models
from django.contrib.postgres.fields import HStoreField
from filebrowser.fields import FileBrowseField
from file_types.gff3 import Gff3
import os

class File(models.Model):
    '''A File is a self-contained List, Tree, or Graph of Items.
    '''
    #id = models.AutoField(primary_key=True) # auto
    type = models.CharField(max_length=50, help_text='Specifies which parser to use on this file') # gi|45478711|ref|NC_005816.1|
    name = FileBrowseField('File path', max_length=100, directory='data/')
    hash = models.TextField(blank=True)
    processed_hash = models.TextField(blank=True)
    processed_date = models.DateTimeField(auto_now_add=True)
    attributes = HStoreField()
    related = models.ManyToManyField('self', through='FileRelationship', through_fields=('source', 'target'), symmetrical=False)
    
    def process_file(self):
        if not os.path.isfile(self.name.path_full):
            return 1, 'File not found', ''
        from sys import platform
        from subprocess import Popen, PIPE
        if self.type == 'gff3':
            gff = Gff3(str(self.name.path_full))
            #return p.returncode, error, output
            return 1, 'Gff3 lines = {}'.format(len(gff.lines)), ''
        else:
            return 1, 'File type not supported', ''

    def __unicode__(self):
        return str(self.id)

class FileRelationship(models.Model):
    '''source.type = target
    '''
    source = models.ForeignKey(File, related_name='+')
    type = models.CharField(max_length=50, help_text='Relationship Type')
    target = models.ForeignKey(File, related_name='+')

class Item(models.Model):
    '''Accessions are assigned to Items.
    '''
    key = models.AutoField(primary_key=True) # auto
    id = models.PositiveIntegerField() # 
    file = models.ForeignKey(File)
    attributes = HStoreField()
    related = models.ManyToManyField('self', through='ItemRelationship', through_fields=('source', 'target'), symmetrical=False)
    
    def __unicode__(self):
        return str(self.key)

class ItemRelationship(models.Model):
    '''source.type = target
    '''
    source = models.ForeignKey(Item, related_name='+')
    type = models.CharField(max_length=50, help_text='Relationship Type')
    target = models.ForeignKey(Item, related_name='+')