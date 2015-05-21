from django.db import models
from django.contrib.postgres.fields import HStoreField
from filebrowser.fields import FileBrowseField
from file_types.gff3 import Gff3, fasta_file_to_dict
import os
import six
import numbers
from collections import MutableSet, OrderedDict

class OrderedSet(MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

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
        file_id = str(self.id)
        if self.type == 'gff3':
            #try:
                # remove existing items
                self.item_set.all().delete()
                # parse file
                gff = Gff3(str(self.name.path_full))
                #seq_count = 0

                # assign every line to an Item
                item_list = []
                for line_index, line_data in enumerate(gff.lines):
                    attributes = {}
                    for k, v in line_data.items():
                        if v:
                            if isinstance(v, six.string_types):
                                attributes[k] = v
                            elif isinstance(v, numbers.Number):
                                attributes[k] = str(v)
                    item_list.append(Item(file=self, index=line_index, text=line_data['line_raw'], attributes=attributes))

                # write database
                if len(item_list) > 0:
                    Item.objects.bulk_create(item_list)
                
                # get the saved Items back in a list
                item_list = Item.objects.filter(file=self).order_by('index')
                item_list = [item for item in item_list] # cache

                # build ItemRelationships
                item_relationship_list = []
                parent_lines = [line_data for line_data in gff.lines if line_data['line_type'] == 'feature' and line_data['children']]
                for parent_line in parent_lines:
                    parent_item = item_list[parent_line['line_index']]
                    for child_line in parent_line['children']:
                        child_item = item_list[child_line['line_index']]
                        item_relationship_list.append(ItemRelationship(source=parent_item, type='child', target=child_item))
                        item_relationship_list.append(ItemRelationship(source=child_item, type='parent', target=parent_item))

                # write database
                if len(item_relationship_list) > 0:
                    ItemRelationship.objects.bulk_create(item_relationship_list)

                # assign Accessions through dfs tranversal
                accession_list = []
                def dfs(root_lines, path=OrderedDict()):
                    for root_line_index, root_line in enumerate(root_lines):
                        # don't visit the same node twice in a path (don't allow loops)
                        if root_line['line_index'] not in path:
                            path[root_line['line_index']] = str(root_line_index + 1)
                            accession_list.append(Accession(accession='{}/{}'.format(file_id, '/'.join(path.viewvalues())), item=item_list[root_line['line_index']]))
                            if root_line['children']:
                                dfs(root_line['children'], path=path)
                            path.popitem()

                # get a list of root nodes
                root_lines = [line_data for line_data in gff.lines if line_data['line_type'] == 'feature' and not line_data['parents']]
                dfs(root_lines)

                # write database
                if len(accession_list) > 0:
                    Accession.objects.bulk_create(accession_list)

                return 0, '', '%d items added.' % len(item_list)
            #except Exception as e:
                #return 1, str(e), ''
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
                accession_list = []
                for index, id in enumerate(fasta):
                    item = Item(file=self, index=index, text='{}\n{}'.format(fasta[id]['header'], fasta[id]['seq']), attributes={'header': fasta[id]['header'], 'id': fasta[id]['id'], 'seq': fasta[id]['seq']})
                    item_list.append(item)
                    accession_list.append(Accession(accession='{}/{}'.format(file_id, str(index+1)), item=item))

                # write database
                if len(item_list) > 0:
                    Item.objects.bulk_create(item_list)
                if len(item_relationship_list) > 0:
                    ItemRelationship.objects.bulk_create(item_relationship_list)
                if len(accession_list) > 0:
                    Accession.objects.bulk_create(accession_list)

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
    #key = models.AutoField(primary_key=True) # auto
    file = models.ForeignKey(File)
    index = models.PositiveIntegerField(null=True, blank=True) # unique index within a file
    text = models.TextField(blank=True)
    attributes = HStoreField(blank=True)
    related = models.ManyToManyField('self', through='ItemRelationship', through_fields=('source', 'target'), symmetrical=False, related_name='itemrelationship_set')
    
    def __unicode__(self):
        return str(self.text)

class ItemRelationship(models.Model):
    '''source.type = target
    '''
    source = models.ForeignKey(Item, related_name='relationships_to')
    type = models.CharField(max_length=50, help_text='Relationship Type')
    target = models.ForeignKey(Item, related_name='relationships_from')

class Accession(models.Model):
    '''Accessions are assigned to Items.
    '''
    accession = models.TextField(primary_key=True)
    item = models.ForeignKey(Item)
    
    def __unicode__(self):
        return str(self.accession)