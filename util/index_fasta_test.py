from sys import platform
from subprocess import Popen, PIPE
import os

PROJECT_ROOT = r'D:\Django\django-blast'
path_full = r'D:\Django\django-blast\media\blastdb\AGLA_new_ids3.faa'
molecule_type = 'prot'
title = 'AGLA_new_ids.faa'
tax_id = '217634'


# parse fasta
sequence_set = []
seq_count = 0
with open(path_full, 'rb') as f:
    offset = 0
    id = ''
    header = ''
    length = 0
    seq_start_pos = 0
    seq_end_pos = 0
    for line in f:
        stripped = line.strip()
        if len(stripped) > 0:
            if stripped[0] == '>': # header
                if length > 0: # not first sequence, add previous sequence to db
                    #self.sequence_set.create(id=id, header=header, length=length, seq_start_pos=seq_start_pos, seq_end_pos=offset)
                    print 'id=%s, header=%s, length=%d, seq_start_pos=%d, seq_end_pos=%d\n' % (id, header, length, seq_start_pos, offset)
                    sequence_set.append((id, header, length, seq_start_pos, offset))
                    seq_count += 1
                seq_start_pos = offset + line.find('>') # white chars before '>'
                header = stripped[1:] # exclue '>'
                id = header.split(None, 1)[0]
                length = 0
            else: # sequence
                length += len(stripped)
        offset += len(line)
    if length > 0: # add last sequence
        #self.sequence_set.create(id=id, header=header, length=length, seq_start_pos=seq_start_pos, seq_end_pos=offset)
        print 'id=%s, header=%s, length=%d, seq_start_pos=%d, seq_end_pos=%d\n' % (id, header, length, seq_start_pos, offset)
        sequence_set.append((id, header, length, seq_start_pos, offset))
        seq_count += 1

# get sequence
with open(path_full, 'rb') as f:
    for seq in sequence_set:
        f.seek(seq[3])
        lines = f.read(seq[4] - seq[3])
        print lines