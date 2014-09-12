#!/usr/bin/env python
import json

TSV_FILENAME = 'i5k_blastdb_list.tsv'
BLASTDB_URL_ROOT = '/blast/db/'
DUMP_FILENAME = 'jbrowsesetting-stage.json'
#DUMP_FILENAME = 'jbrowsesetting.json'

fixture_list = []
# read tsv
with open(TSV_FILENAME, 'rb') as f:
    for row in f:
        (display_name, short_name, db_type, fasta_filename) = row.strip().split('\t')
        if db_type == 'Genome Assembly':
            fixture_item = {
                'model': 'blast.jbrowsesetting',
                'fields': {
                    'url': 'https://apollo.nal.usda.gov/%s/jbrowse/' % short_name,
                    #'url': 'http://gmod-dev.nal.usda.gov:8080/%s/jbrowse/' % short_name,
                    'blast_db': [BLASTDB_URL_ROOT + fasta_filename],
                }
            }
            fixture_list.append(fixture_item)
# dump json
with open(DUMP_FILENAME, 'wb') as f:
    json.dump(fixture_list, f, sort_keys=True, indent=2, separators=(',', ': '))