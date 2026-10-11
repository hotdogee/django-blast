import io

from django.test import SimpleTestCase

from blast.gff3 import gff_seqid, hsp_dict_list, write_gff3

COLS = 'qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore nident qcovs qlen slen qframe sframe'.split()


def hit(qseqid, sseqid, qstart, qend, sstart, send, evalue=1e-30, bitscore=120.0, pident=98.5, qlen=1000):
    return [qseqid, sseqid, pident, abs(qend - qstart) + 1, 0, 0, qstart, qend, sstart, send, evalue, bitscore, 0, 100, qlen, 50000, 1, 1]


def gff(rows, program='blastn'):
    out = io.StringIO()
    write_gff3(out, hsp_dict_list(rows, COLS), program)
    lines = out.getvalue().splitlines()
    assert lines[0] == '##gff-version 3'
    return [line.split('\t') for line in lines[1:]]


def attributes(columns):
    return dict(item.split('=', 1) for item in columns[8].split(';'))


class SeqidTest(SimpleTestCase):
    def test_i5k_seqid_parsing(self):
        self.assertEqual(gff_seqid('Scaffold1'), 'Scaffold1')
        self.assertEqual(gff_seqid('gi|5524211|gb|AAD44166.1|'), 'gi|5524211|gb|AAD44166.1|')
        self.assertEqual(gff_seqid('gnl|Ceratitis_capitata|cercap_Scaffold1'), 'Scaffold1')
        self.assertEqual(gff_seqid('lcl|Scaffold9|extra'), 'Scaffold9')


class Gff3Test(SimpleTestCase):
    def test_contiguous_hsps_are_one_match(self):
        rows = [hit('q1', 'Scaffold1', 1, 100, 1001, 1100), hit('q1', 'Scaffold1', 101, 200, 1201, 1300)]
        features = gff(rows)
        self.assertEqual([f[2] for f in features], ['match', 'match_part', 'match_part'])
        match = features[0]
        self.assertEqual(match[:5], ['Scaffold1', 'blastn', 'match', '1001', '1300'])
        self.assertEqual(match[5], '.')  # several HSPs, no single e-value
        self.assertEqual(match[6], '+')
        self.assertEqual(attributes(match)['Target'], 'q1 1 200 +')
        part = attributes(features[1])
        self.assertEqual(part['Parent'], attributes(match)['ID'])
        self.assertEqual(part['Bitscore'], '120')

    def test_overlapping_hsps_are_split(self):
        # the second HSP starts 50 bases before the first one ends: two matches
        rows = [hit('q1', 'Scaffold1', 1, 100, 1001, 1100), hit('q1', 'Scaffold1', 51, 150, 1051, 1150)]
        features = gff(rows)
        self.assertEqual([f[2] for f in features], ['match', 'match_part', 'match', 'match_part'])
        self.assertEqual(features[0][5], '1e-30')

    def test_minus_strand(self):
        rows = [hit('q1', 'gnl|Org|org_Scaffold2', 1, 100, 5100, 5001)]
        match = gff(rows)[0]
        self.assertEqual(match[0], 'Scaffold2')
        self.assertEqual(match[3:5], ['5001', '5100'])
        self.assertEqual(match[6], '-')

    def test_groups_by_query_and_subject(self):
        rows = [hit('q1', 'Scaffold1', 1, 100, 1, 100), hit('q2', 'Scaffold1', 1, 100, 1, 100), hit('q1', 'Scaffold2', 1, 100, 1, 100)]
        features = gff(rows)
        self.assertEqual(sum(1 for f in features if f[2] == 'match'), 3)

    def test_seqid_prefix_is_removed(self):
        out = io.StringIO()
        write_gff3(out, hsp_dict_list([hit('q1', 'Mdes_genome|Scaffold7', 1, 100, 1, 100)], COLS), 'blastn', 'Mdes_genome|')
        self.assertEqual(out.getvalue().splitlines()[1].split('\t')[0], 'Scaffold7')
        self.assertEqual(gff_seqid('genome_Scaffold1', 'genome_'), 'Scaffold1')

    def test_hit_statistics_are_exported(self):
        # #12: bit score, e-value and percent identity of every HSP
        features = gff([hit('q1', 'Scaffold1', 1, 100, 1001, 1100, evalue=3.5e-42, bitscore=187.3, pident=97.25)])
        part = attributes(features[1])
        self.assertEqual((part['Bitscore'], part['evalue'], part['pident']), ('187.3', '3.5e-42', '97.25'))
        self.assertEqual(features[1][5], '3.5e-42')
