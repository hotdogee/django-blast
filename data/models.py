from django.db import models
from django.contrib.postgres.fields import HStoreField
from filebrowser.fields import FileBrowseField
from file_types.gff3 import Gff3, fasta_file_to_dict
import os
import six
import numbers
from collections import OrderedDict

class File(models.Model):
    '''A File is a self-contained List, Tree, or Graph of Items.
    '''
    #id = models.AutoField(primary_key=True) # auto
    type = models.CharField(max_length=50, help_text='Specifies which parser to use on this file') # gi|45478711|ref|NC_005816.1|
    name = FileBrowseField('File path', max_length=100, directory='data/')
    hash = models.TextField(blank=True)
    processed_hash = models.TextField(blank=True)
    processed_date = models.DateTimeField(auto_now_add=True)
    attributes = HStoreField(blank=True)
    related = models.ManyToManyField('self', through='FileRelationship', through_fields=('source', 'target'), symmetrical=False)
    
    def process_file(self):
        if not os.path.isfile(self.name.path_full):
            return 1, 'File not found', ''
        from sys import platform
        from subprocess import Popen, PIPE
        if self.type == 'gff3':
            try:
                # remove existing items
                self.item_set.all().delete()
                # parse file
                gff = Gff3(str(self.name.path_full))
                #seq_count = 0
                item_list = []
                item_relationship_list = []

                # assign every line to an Item
                for idx, ld in enumerate(gff.lines):
                    attributes = {}
                    for k, v in ld.items():
                        if v:
                            if isinstance(v, six.string_types):
                                attributes[k] = v
                            elif isinstance(v, numbers.Number):
                                attributes[k] = str(v)
                    item_list.append(Item(file=self, id=idx+1, text=ld['line_raw'], attributes=attributes))

                # assign Accessions with dfs tranversal
                def dfs(root_line, path=OrderedDict()):
                    pass
                # get a list of root nodes
                root_lines = [line_data for line_data in gff.lines if line_data['line_type'] == 'feature' and not line_data['parents']]
                for idx, root_line in enumerate(root_lines):
                    pass

                # build ItemRelationships

                if len(item_list) > 0:
                    Item.objects.bulk_create(item_list)
                if len(item_relationship_list) > 0:
                    ItemRelationship.objects.bulk_create(item_relationship_list)
                return 0, '', '%d items added.' % len(item_list)
            except Exception as e:
                return 1, str(e), ''
            #return p.returncode, error, output
            #return 1, 'Gff3 lines = {}'.format(len(gff.lines)), ''
        elif self.type == 'fasta':
            try:
                # remove existing items
                self.item_set.all().delete()
                # parse file
                fasta, count = fasta_file_to_dict(str(self.name.path_full))
                #seq_count = 0
                item_list = []
                item_relationship_list = []
                for idx, id in enumerate(fasta):
                    item_list.append(Item(file=self, id=idx+1, text='{}\n{}'.format(fasta[id]['header'], fasta[id]['seq']), attributes={'header': fasta[id]['header'], 'id': fasta[id]['id'], 'seq': fasta[id]['seq']}))
                if len(item_list) > 0:
                    Item.objects.bulk_create(item_list)
                if len(item_relationship_list) > 0:
                    ItemRelationship.objects.bulk_create(item_relationship_list)
                return 0, '', '%d items added.' % len(item_list)
            except Exception as e:
                return 1, str(e), ''
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
    accession = models.TextField(blank=True)
    file = models.ForeignKey(File)
    text = models.TextField(blank=True)
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

class Accession(models.Model):
    '''Accessions are assigned to Items.
    '''
    accession = models.TextField(blank=True)
    item = models.ForeignKey(Item)
    
    def __unicode__(self):
        return str(self.accession)