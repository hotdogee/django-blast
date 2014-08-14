#!/usr/bin/env python
from os import path

#TSV_FILENAME = 'make_new_id_list.tsv'
TSV_FILENAME = 'make_new_id_list_diacit.tsv'
#TARGET_DIR = '/app/local/i5k/media/blastdb'
TARGET_DIR = '/app/local/i5k/media/blastdb'

# read tsv
with open(TSV_FILENAME, 'rb') as f:
    for row in f:
        (display_name, short_name, db_type, fasta_filepath, version) = [t.strip() for t in row.split('\t')]
        display_name = display_name.lower().capitalize().replace(' ', '_')
        with open(fasta_filepath, 'rb') as f_in:
            (head, tail) = path.split(fasta_filepath)
            (root, ext) = path.splitext(tail)
            #with open(path.join(TARGET_DIR, root + '_new_ids' + ext), 'wb') as f_out_target:
            #with open(path.join(head, root + '_new_ids' + ext), 'wb') as f_out:
            with open(root + '_new_ids' + ext, 'wb') as f_out:
                for line in f_in:
                    if line[0] == '>' and line[:4] != '>gnl':
                        seqid = line[1:]
                        tokens = seqid.split('|', 1)
                        if len(tokens) == 2:
                            seqid = tokens[1].replace('|', ' ')
                        if db_type == 'Genome Assembly':
                            line = '>gnl|' + display_name + '|' + short_name + '_' + seqid
                        else:
                            line = '>gnl|' + display_name + '_' + db_type.lower() + '_' + version + '|' + seqid
                    #f_out_target.write(line)
                    f_out.write(line)