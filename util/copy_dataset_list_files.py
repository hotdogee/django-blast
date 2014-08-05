#!/usr/bin/env python
from os import path
import shutil

TSV_FILENAME = 'dataset_list.tsv'
FROM_PATH = r'E:\NAL-Home\NAL\Blast\db'
TO_PATH = r'D:\Django\django-blast\media\blastdb'

# read tsv
with open(TSV_FILENAME, 'r') as f:
    for row in f:
        tokens = row.strip().split('\t')
        filename = tokens[3]
        # if file exists
        if path.isfile(path.join(FROM_PATH, filename)):
            shutil.copy2(path.join(FROM_PATH, filename), TO_PATH)
        else:
            print '%s not found' % filename
