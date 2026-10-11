import os
import shutil
import tempfile
import unittest

from django.db import connection
from django.test import TestCase, override_settings

from .models import Accession, File


@unittest.skipUnless(connection.vendor == 'postgresql', 'the data app stores attributes in PostgreSQL hstore fields')
class ProcessFileTest(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix='django-blast-media-')
        self.addCleanup(shutil.rmtree, self.media_root, True)
        override = override_settings(MEDIA_ROOT=self.media_root)
        override.enable()
        self.addCleanup(override.disable)
        os.makedirs(os.path.join(self.media_root, 'data'))

    def write(self, name, text):
        with open(os.path.join(self.media_root, 'data', name), 'w', newline='\n') as f:
            f.write(text)
        return 'data/' + name

    def test_fasta(self):
        f = File.objects.create(type='fasta', name=self.write('a.fa', '>s1 one\nACGT\n>s2\nGG\n'), attributes={})
        self.assertEqual(f.process_file(), (0, '', '2 items added.'))
        item = Accession.objects.get(accession='%d/1' % f.id).item
        self.assertEqual(item.attributes['id'], 's1')
        self.assertEqual(item.attributes['seq'], 'ACGT')

    def test_gff3(self):
        gff = ('##gff-version 3\n'
               'ctg1\t.\tgene\t1\t100\t.\t+\t.\tID=gene1\n'
               'ctg1\t.\tmRNA\t1\t100\t.\t+\t.\tID=mrna1;Parent=gene1\n')
        f = File.objects.create(type='gff3', name=self.write('a.gff3', gff), attributes={})
        self.assertEqual(f.process_file()[0], 0)
        self.assertEqual(sorted(Accession.objects.filter(item__file=f).values_list('accession', flat=True)),
                         ['%d/1' % f.id, '%d/1/1' % f.id])
        response = self.client.get('/data/api/accession/%d/1/1/' % f.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['item']['attributes']['type'], 'mRNA')

    def test_unsupported_type(self):
        f = File.objects.create(type='bam', name=self.write('a.bam', ''), attributes={})
        self.assertEqual(f.process_file(), (1, 'File type not supported', ''))
