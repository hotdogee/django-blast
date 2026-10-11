import logging
import os.path
from subprocess import DEVNULL, STDOUT, Popen

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from app.fields import MediaPathField
from .utils import blast_bin

logger = logging.getLogger(__name__)

# Written next to the FASTA file by BlastDb.makeblastdb() (#8)
MAKEBLASTDB_LOG_SUFFIX = '.makeblastdb.log'


class BlastQueryRecord(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)
    result_status = models.CharField(max_length=32, default='WAITING') # ex. WAITING, SUCCESS, NO_ASN, ASN_EMPTY, NO_CSV, CSV_EMPTY
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    is_shown = models.BooleanField(default=True)

    def __str__(self):
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

    def __str__(self):
        return self.display_name

class SequenceTypeManager(models.Manager):
    def get_by_natural_key(self, dataset_type):
        return self.get(dataset_type=dataset_type)

class SequenceType(models.Model):
    objects = SequenceTypeManager()
    molecule_type = models.CharField(max_length=4, default='nucl', choices=(
        ('nucl', 'Nucleotide'),
        ('prot', 'Peptide'))) # makeblastdb -dbtype
    dataset_type = models.CharField(max_length=50, unique=True) #

    def natural_key(self):
        return (self.dataset_type,)

    def __str__(self):
        return '%s - %s' % (self.get_molecule_type_display(), self.dataset_type)

    class Meta:
        verbose_name = 'sequence type'

class BlastDbManager(models.Manager):
    def get_by_natural_key(self, fasta_file):
        return self.get(title=fasta_file)

class BlastDb(models.Model):
    objects = BlastDbManager()
    organism = models.ForeignKey(Organism, on_delete=models.CASCADE) #
    type = models.ForeignKey(SequenceType, on_delete=models.CASCADE) #
    fasta_file = MediaPathField('FASTA file path', max_length=100, directory='blast/db/', extensions='FASTA')
    title = models.CharField(max_length=200, unique=True, help_text='This is passed into makeblast -title') # makeblastdb -title
    description = models.TextField(blank=True) # shown in blast db selection ui
    is_shown = models.BooleanField(default=None, help_text='Display this database in the BLAST submit form') # to temporarily remove from blast db selection ui

    # properties
    def fasta_file_exists(self):
        return os.path.isfile(self.fasta_file.path_full)
    fasta_file_exists.boolean = True
    fasta_file_exists.short_description = 'fasta file exists'

    def _blast_db_index_file(self):
        '''The alias (.nal/.pal, multi-volume databases) or index (.nin/.pin) file, or None.

        BLAST+ 2.10+ writes version 5 databases, which don't have all the files
        that BLAST+ 2.2.29 created, so only check the files every version has.
        '''
        base = self.fasta_file.path_full + '.' + self.type.molecule_type[0]
        if os.path.isfile(base + 'al'):
            return base + 'al'
        if all(os.path.isfile(base + ext) for ext in ('hr', 'in', 'sq')):
            return base + 'in'
        return None

    def blast_db_files_exists(self):
        return self._blast_db_index_file() is not None
    blast_db_files_exists.boolean = True
    blast_db_files_exists.short_description = 'blast db files exists'

    def sequence_set_exists(self):
        return self.sequence_set.count() > 0
    sequence_set_exists.boolean = True
    sequence_set_exists.short_description = 'sequence table populated'

    def db_ready(self):
        return self.fasta_file_exists() and self.blast_db_files_exists() and self.sequence_set_exists()

    def makeblastdb_log_path(self):
        return self.fasta_file.path_full + MAKEBLASTDB_LOG_SUFFIX

    def makeblastdb_log(self):
        '''Output of the last makeblastdb run, '' if there is none.'''
        try:
            with open(self.makeblastdb_log_path(), encoding='utf-8', errors='replace') as f:
                return f.read()
        except OSError:
            return ''

    def makeblastdb(self):
        '''Run makeblastdb. Returns (returncode, error, output).

        The command line and its output are saved to <fasta file>.makeblastdb.log (#8).
        '''
        fasta_path = self.fasta_file.path_full
        if not os.path.isfile(fasta_path):
            return 1, 'FASTA file not found', ''
        args = [blast_bin('makeblastdb'), '-in', fasta_path, '-dbtype', self.type.molecule_type, '-hash_index'] # , '-parse_seqids' TODO: make option
        if self.title:
            args += ['-title', self.title]
        if self.organism.tax_id:
            args += ['-taxid', str(self.organism.tax_id)]
        log_path = self.makeblastdb_log_path()
        try:
            open(log_path, 'wb').close()
            # makeblastdb writes to the same file: append so both end up in order
            log = open(log_path, 'ab')
        except OSError as e:
            return 1, 'Could not write the makeblastdb log %s: %s' % (log_path, e), ''
        with log:
            log.write(('# %s\n# %s\n' % (timezone.now().isoformat(), ' '.join(args))).encode('utf-8'))
            log.flush()
            try:
                p = Popen(args, stdin=DEVNULL, stdout=log, stderr=STDOUT)
            except OSError as e:
                log.write(('Could not run makeblastdb: %s\n' % e).encode('utf-8'))
                return 1, 'Could not run makeblastdb (%s): %s' % (args[0], e), ''
            returncode = p.wait()
            log.write(('# exit code %d\n' % returncode).encode('utf-8'))
        output = self.makeblastdb_log()
        if returncode == 0:
            logger.info('makeblastdb succeeded for %s, log: %s', self.title, log_path)
            return 0, '', output
        logger.error('makeblastdb failed for %s (exit code %d), log: %s\n%s', self.title, returncode, log_path, output)
        tail = ' '.join(line for line in output.splitlines()[-5:] if not line.startswith('#'))
        return returncode, 'makeblastdb exited with code %d: %s (full log: %s)' % (returncode, tail.strip(), log_path), output

    def index_fasta(self):
        if not os.path.isfile(self.fasta_file.path_full):
            return 1, 'FASTA file not found', ''
        try:
            # remove existing sequences
            self.sequence_set.all().delete()
            # parse fasta
            sequence_list = []
            with open(self.fasta_file.path_full, 'rb') as f:
                offset = 0
                id = ''
                length = 0
                seq_start_pos = 0
                for line in f:
                    stripped = line.strip()
                    if len(stripped) > 0:
                        if stripped[:1] == b'>': # header
                            if length > 0: # not first sequence, add previous sequence to db
                                sequence_list.append(Sequence(blast_db=self, id=id, length=length, seq_start_pos=seq_start_pos, seq_end_pos=offset))
                            seq_start_pos = offset + line.find(b'>') # white chars before '>'
                            id = stripped.split(None, 1)[0][1:].decode('utf-8', 'replace')
                            length = 0
                        else: # sequence
                            length += len(stripped)
                    offset += len(line)
                if length > 0: # add last sequence
                    sequence_list.append(Sequence(blast_db=self, id=id, length=length, seq_start_pos=seq_start_pos, seq_end_pos=offset))
            if len(sequence_list) > 0:
                Sequence.objects.bulk_create(sequence_list, batch_size=5000)
            return 0, '', '%d sequences added.' % len(sequence_list)
        except Exception as e:
            return 1, str(e), ''

    def natural_key(self):
        return (str(self.title),)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'BLAST database'


class Sequence(models.Model):
    '''
    Contents of this table should be generated programmatically
    >gi|45478711|ref|NC_005816.1| Yersinia pestis biovar Microtus ... pPCP1, complete sequence
    SELECT [key], blast_db_id, id, length, seq_start_pos, seq_end_pos, modified_date FROM blast_sequence

    The same id can exist in several BLAST databases (#19); it is only unique
    together with blast_db.
    '''
    key = models.AutoField(primary_key=True)
    blast_db = models.ForeignKey(BlastDb, verbose_name='BLAST DB', on_delete=models.CASCADE) #
    id = models.CharField(max_length=200, db_index=True) # gi|45478711|ref|NC_005816.1|
    length = models.PositiveIntegerField() #
    seq_start_pos = models.BigIntegerField() # used for file.seek(offset), marks start of '>'
    seq_end_pos = models.BigIntegerField() # used to calculate file.read(size)
    modified_date = models.DateTimeField(auto_now_add=True)

    def _read_record(self):
        if not os.path.isfile(self.blast_db.fasta_file.path_full):
            return None
        with open(self.blast_db.fasta_file.path_full, 'rb') as f:
            f.seek(self.seq_start_pos)
            record = f.read(self.seq_end_pos - self.seq_start_pos)
        return record.decode('utf-8', 'replace').replace('\r\n', '\n')

    def fasta_seq(self):
        seq = self._read_record()
        if seq is None:
            return 'FASTA file not found.'
        if not seq.endswith('\n'):
            seq += '\n'
        return seq

    def get_sequence(self):
        seq = self._read_record()
        if seq is None:
            return 'FASTA file not found.'
        return seq.split('\n', 1)[1] if '\n' in seq else ''

    def get_header(self):
        seq = self._read_record()
        if seq is None:
            return 'FASTA file not found.'
        return seq.split('\n', 1)[0]

    def __str__(self):
        return self.id

    class Meta:
        unique_together = ('blast_db', 'id')

class JbrowseSetting(models.Model):
    'Used to link databases to Jbrowse'
    blast_db = models.OneToOneField(BlastDb, verbose_name='reference', help_text='The BLAST database used as the reference in Jbrowse', on_delete=models.CASCADE) #
    url = models.URLField('Jbrowse URL', unique=True, help_text='The URL to Jbrowse using this reference')

    def __str__(self):
        return self.url
