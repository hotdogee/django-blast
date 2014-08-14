#!/usr/bin/env python
from os import path

TSV_FILENAME = 'make_new_id_list.tsv'

# read tsv
with open(TSV_FILENAME, 'rb') as f:
    for row in f:
        (display_name, short_name, db_type, fasta_filepath, version) = [t.strip() for t in row.split('\t')]
        display_name = display_name.lower().capitalize().replace(' ', '_')
        (head, tail) = path.split(fasta_filepath)
        (root, ext) = path.splitext(tail)
        print '\t'.join([display_name, short_name, db_type, root + '_new_ids' + ext])