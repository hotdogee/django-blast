from sys import platform
from subprocess import Popen, PIPE
import os

PROJECT_ROOT = r'D:\Django\django-blast'
path_full = r'D:\Django\django-blast\media\blastdb\AGLA_new_ids.faa'
molecule_type = 'prot'
title = 'AGLA_new_ids.faa'
tax_id = '217634'

bin_name = 'bin_linux'
if platform == 'win32':
    bin_name = 'bin_win'
makeblastdb_path = os.path.join(PROJECT_ROOT, 'blast', bin_name, 'makeblastdb')
args = [makeblastdb_path, '-in', path_full, '-dbtype', molecule_type, '-hash_index']
if title:
    args += ['-title', title]
if tax_id:
    args += ['-taxid', tax_id]
p = Popen(args, stdout=PIPE, stderr=PIPE)
output, error = p.communicate()
print 'output = %s\n' % output
print 'error = %s\n' % error
print 'returncode = %s\n' % p.returncode

''' Fail example
output =

Building a new DB, current time: 08/06/2014 15:17:34
New DB name:   D:\Django\django-blast\media\blastdb\AGLA_new_ids.f
New DB title:  AGLA_new_ids.faa
Sequence type: Protein
Keep Linkouts: T
Keep MBits: T
Maximum file size: 1000000000B


error = BLAST options error: File D:\Django\django-blast\media\blastdb\AGLA_new_
ids.f does not exist


returncode = 1
'''
''' Success example
output =

Building a new DB, current time: 08/06/2014 15:18:37
New DB name:   D:\Django\django-blast\media\blastdb\AGLA_new_ids.faa
New DB title:  AGLA_new_ids.faa
Sequence type: Protein
Keep Linkouts: T
Keep MBits: T
Maximum file size: 1000000000B
Adding sequences from FASTA; added 22035 sequences in 1.6441 seconds.


error =

returncode = 0
'''