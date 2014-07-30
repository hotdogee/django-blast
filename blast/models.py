from django.db import models

class BlastQueryRecord(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.task_id

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('blast:retrieve', args=[str(self.task_id)])

class Organism(models.Model):
    display_name = models.CharField(max_length=200, unique=True) # shown to user
    short_name = models.CharField(max_length=20, unique=True) # used in code or filenames
    description = models.TextField(blank=True) # optional
    tax_id = models.PositiveIntegerField('NCBI Taxonomy ID', null=True, blank=True) # ncbi tax id

    def __unicode__(self):
        return self.display_name

class BlastDb(models.Model):
    organism = models.ForeignKey(Organism) # 
    type = models.ForeignKey(BlastDbType) # 
    description = models.TextField(blank=True) # shown in blast db selection ui
    title = models.CharField(max_length=200, unique=True) # makeblastdb -title
    fasta_file = models.PositiveIntegerField(null=True, blank=True) # upload file
    is_shown = models.BooleanField() # to temporarily remove from blast db selection ui
    #sequence_count = models.PositiveIntegerField(null=True, blank=True) # number of sequences in this fasta

    def __unicode__(self):
        return self.fasta_file

class BlastDbType(models.Model):
    molecule_type = models.CharField(max_length=4, default='nucl', choices=(
        ('nucl', 'Nucleotide'),
        ('prot', 'Protein'))) # makeblastdb -dbtype
    dataset_type = models.CharField(max_length=50) # 

    def __unicode__(self):
        return u'%s - %s' % (self.get_molecule_type_display(), self.dataset_type)

    class Meta:
        unique_together = ('molecule_type', 'dataset_type')

class Sequence(models.Model):
    key = models.AutoField(primary_key=True)
    blast_db = models.ForeignKey(BlastDb) # 
    id = models.CharField(max_length=100) # 
    header = models.CharField(max_length=400) # 
    length = models.PositiveIntegerField() # 
    sequence = models.TextField() # 

    def __unicode__(self):
        return self.id

    class Meta:
        unique_together = ('blast_db', 'id')

class JbrowseInfo(models.Model):
    blast_db = models.ForeignKey(BlastDb) # 
    url = models.URLField('Jbrowse URL', unique=True)

    def __unicode__(self):
        return self.url