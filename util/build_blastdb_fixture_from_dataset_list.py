#!/usr/bin/env python
import json

TSV_FILENAME = 'dataset_list.tsv'
BLASTDB_URL_ROOT = '/media/blastdb/'
DUMP_FILENAME = 'blastdb.json'

fixture_list = []
# read tsv
with open(TSV_FILENAME, 'rb') as f:
    for row in f:
        (display_name, short_name, db_type, fasta_filename) = row.strip().split('\t')
        fixture_item = {
            'model': 'blast.blastdb',
            'fields': {
                'description': fasta_filename,
                'title': fasta_filename,
                'organism': [short_name],
                'fasta_file': BLASTDB_URL_ROOT + fasta_filename,
                'is_shown': True,
                'type': [db_type]
            }
        }
        fixture_list.append(fixture_item)
# dump json
with open(DUMP_FILENAME, 'wb') as f:
    json.dump(fixture_list, f, sort_keys=True, indent=2, separators=(',', ': '))