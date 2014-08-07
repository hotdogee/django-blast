from django.db import models
from filebrowser.fields import FileBrowseField
from django.core.urlresolvers import reverse
import os.path
from django.conf import settings

class BlastQueryRecord(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)
    result_status = models.CharField(max_length=32, default='WAITING') # ex. WAITING, SUCCESS, NO_ASN, ASN_EMPTY, NO_CSV, CSV_EMPTY

    def __unicode__(self):
        return self.task_id

    def get_absolute_url(self):
        return reverse('blast:retrieve', args=[str(self.task_id)])

    class Meta:
        verbose_name = 'BLAST result'

class OrganismManager(models.Manager):
    def get_by_natural_key(self, short_name):
        return self.get(short_name=short_name)

class Organism(models.Model):
    objects = OrganismManager()
    display_name = models.CharField(max_length=200, unique=True, help_text='Scientific or common name') # shown to user
    short_name = models.CharField(max_length=20, unique=True, help_text='This is used for file names and variable names in code') # used in code or filenames
    description = models.TextField(blank=True) # optional
    tax_id = models.PositiveIntegerField('NCBI Taxonomy ID', null=True, blank=True, help_text='This is passed into makeblast') # ncbi tax id
    
    def natural_key(self):
        return (self.short_name,)

    def __unicode__(self):
        return self.display_name

class BlastDbTypeManager(models.Manager):
    def get_by_natural_key(self, dataset_type):
        return self.get(dataset_type=dataset_type)

class BlastDbType(models.Model):
    objects = BlastDbTypeManager()
    molecule_type = models.CharField(max_length=4, default='nucl', choices=(
        ('nucl', 'Nucleotide'),
        ('prot', 'Protein'))) # makeblastdb -dbtype
    dataset_type = models.CharField(max_length=50, unique=True) # 
    
    def natural_key(self):
        return (self.dataset_type,)

    def __unicode__(self):
        return u'%s - %s' % (self.get_molecule_type_display(), self.dataset_type)

    class Meta:
        verbose_name = 'BLAST database type'

class BlastDbManager(models.Manager):
    def get_by_natural_key(self, fasta_file):
        return self.get(fasta_file=fasta_file)

class BlastDb(models.Model):
    objects = BlastDbManager()
    organism = models.ForeignKey(Organism) # 
    type = models.ForeignKey(BlastDbType) # 
    #fasta_file = models.FileField(upload_to='blastdb') # upload file
    fasta_file = FileBrowseField('FASTA file', max_length=100, directory='blastdb/', extensions='FASTA', format='FASTA')
    title = models.CharField(max_length=200, unique=True, help_text='This is passed into makeblast -title') # makeblastdb -title
    description = models.TextField(blank=True) # shown in blast db selection ui
    is_shown = models.BooleanField(default=None, help_text='Display this database in the BLAST submit form') # to temporarily remove from blast db selection ui
    #sequence_count = models.PositiveIntegerField(null=True, blank=True) # number of sequences in this fasta
    
    # properties
    def fasta_file_exists(self):
        return os.path.isfile(self.fasta_file.path_full)
    fasta_file_exists.boolean = True
    fasta_file_exists.short_description = 'fasta file exists'
    
    def blast_db_files_exists(self):
        return all([os.path.isfile(self.fasta_file.path_full + '.' + self.type.molecule_type[0] + ext) for ext in  ['hd', 'hi', 'hr', 'in', 'og', 'sd', 'si', 'sq']])
    blast_db_files_exists.boolean = True
    blast_db_files_exists.short_description = 'blast db files exists'

    def makeblastdb(self):
        if not os.path.isfile(self.fasta_file.path_full):
            return 1, 'FASTA file not found', ''
        from sys import platform
        from subprocess import Popen, PIPE
        bin_name = 'bin_linux'
        if platform == 'win32':
            bin_name = 'bin_win'
        makeblastdb_path = os.path.join(settings.PROJECT_ROOT, 'blast', bin_name, 'makeblastdb')
        args = [makeblastdb_path, '-in', self.fasta_file.path_full, '-dbtype', self.type.molecule_type, '-hash_index']
        if self.title:
            args += ['-title', self.title]
        if self.organism.tax_id:
            args += ['-taxid', str(self.organism.tax_id)]
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        return p.returncode, error, output

    def index_fasta(self):
        if not os.path.isfile(self.fasta_file.path_full):
            return 1, 'FASTA file not found', ''
        try:
            # remove existing sequences
            self.sequence_set.all().delete()
            # parse fasta
            #seq_count = 0
            sequence_list = []
            with open(self.fasta_file.path_full, 'rb') as f:
                offset = 0
                id = ''
                #header = ''
                length = 0
                seq_start_pos = 0
                seq_end_pos = 0
                for line in f:
                    stripped = line.strip()
                    if len(stripped) > 0:
                        if stripped[0] == '>': # header
                            if length > 0: # not first sequence, add previous sequence to db
                                sequence_list.append(Sequence(blast_db=self, id=id, length=length, seq_start_pos=seq_start_pos, seq_end_pos=offset))
                                #seq_count += 1
                            seq_start_pos = offset + line.find('>') # white chars before '>'
                            #header = stripped[1:] # exclue '>'
                            id = stripped.split(None, 1)[0][1:]
                            length = 0
                        else: # sequence
                            length += len(stripped)
                    offset += len(line)
                if length > 0: # add last sequence
                    sequence_list.append(Sequence(blast_db=self, id=id, length=length, seq_start_pos=seq_start_pos, seq_end_pos=offset))
                    #seq_count += 1
            if len(sequence_list) > 0:
                Sequence.objects.bulk_create(sequence_list)
            return 0, '', '%d sequences added.' % len(sequence_list)
        except Exception as e:
            return 1, str(e), ''

    def natural_key(self):
        return (str(self.fasta_file),)

    def __unicode__(self):
        return str(self.fasta_file)

    class Meta:
        verbose_name = 'BLAST database'

class Sequence(models.Model):
    '''
    Contents of this table should be generated programmatically
    >gi|45478711|ref|NC_005816.1| Yersinia pestis biovar Microtus ... pPCP1, complete sequence
    SELECT [key], blast_db_id, id, length, seq_start_pos, seq_end_pos, modified_date FROM blast_sequence
    '''
    key = models.AutoField(primary_key=True)
    blast_db = models.ForeignKey(BlastDb, verbose_name='BLAST DB') # 
    id = models.CharField(max_length=100) # gi|45478711|ref|NC_005816.1|
    length = models.PositiveIntegerField() # 
    seq_start_pos = models.BigIntegerField() # used for file.seek(offset), marks start of '>'
    seq_end_pos = models.BigIntegerField() # used to calculate file.read(size)
    modified_date = models.DateTimeField(auto_now_add=True)

    def get_entry(self):
        if not os.path.isfile(self.blast_db.fasta_file.path_full):
            return 'FASTA file not found.'
        with open(self.blast_db.fasta_file.path_full, 'rb') as f:
            f.seek(seq_start_pos)
            return f.read(seq_end_pos - seq_start_pos)

    def get_sequence(self):
        if not os.path.isfile(self.blast_db.fasta_file.path_full):
            return 'FASTA file not found.'
        with open(self.blast_db.fasta_file.path_full, 'rb') as f:
            f.seek(seq_start_pos)
            return f.read(seq_end_pos - seq_start_pos).split('\n', 1)[1]

    def get_header(self):
        if not os.path.isfile(self.blast_db.fasta_file.path_full):
            return 'FASTA file not found.'
        with open(self.blast_db.fasta_file.path_full, 'rb') as f:
            f.seek(seq_start_pos)
            return f.read(seq_end_pos - seq_start_pos).split('\n', 1)[0]

    def __unicode__(self):
        return self.id

    class Meta:
        unique_together = ('blast_db', 'id')

class JbrowseSetting(models.Model):
    'Used to link databases to Jbrowse'
    blast_db = models.ForeignKey(BlastDb, verbose_name='reference', unique=True, help_text='The BLAST database used as the reference in Jbrowse') # 
    url = models.URLField('Jbrowse URL', unique=True, help_text='The URL to Jbrowse using this reference')

    def __unicode__(self):
        return self.url
