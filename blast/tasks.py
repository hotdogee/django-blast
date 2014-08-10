from __future__ import absolute_import
from celery import shared_task
from subprocess import Popen, PIPE
from datetime import datetime
from .models import BlastQueryRecord, Sequence, BlastDb, JbrowseSetting
from os import path, stat
from pytz import utc
from itertools import groupby
import csv

@shared_task() # ignore_result=True
def run_blast_task(task_id, args_list, file_prefix, blast_info):
    import django
    django.setup()
    
    # update dequeue time
    record = BlastQueryRecord.objects.get(task_id__exact=task_id)
    record.dequeue_date = datetime.utcnow().replace(tzinfo=utc)
    record.save()

    # run
    for args in args_list:
        Popen(args, stdin=PIPE, stdout=PIPE).wait()

    # update result state
    result_status = ''
    if not path.isfile(file_prefix + '.asn'):
        result_status = 'NO_ASN'
    elif stat(file_prefix + '.asn')[6] == 0:
        result_status = 'ASN_EMPTY'
    elif not path.isfile(file_prefix + '.csv'):
        result_status = 'NO_CSV'
    elif stat(file_prefix + '.csv')[6] == 0:
        result_status = 'CSV_EMPTY'
    else:
        # generate gff3 files
        overlap_cutoff = 5
        blast_program = path.basename(args_list[0][0])
        csv_path = file_prefix + '.csv'
        basedir = path.dirname(csv_path)
        content_groups = []
        type_func = {'str': str, 'float': float, 'int': int}
        gff_col_names = 'seqid source type start end score strand phase attributes'.split()
        with open(csv_path, 'r') as f:
            #csv_list = [row for row in csv.reader(f)]
            hsp_list = [dict(zip(blast_info['col_names'], [type_func[convert](value) for convert, value in zip(blast_info['col_types'], row)])) for row in csv.reader(f)]
            sseqid_db = dict(Sequence.objects.select_related('blast_db__title').filter(id__in=[hsp['sseqid'] for hsp in hsp_list]).values_list('id', 'blast_db__title'))
            db_organism = dict(BlastDb.objects.select_related('organism__short_name').filter(title__in=set(sseqid_db.values())).values_list('title', 'organism__short_name'))
            db_url = dict(JbrowseSetting.objects.select_related('blast_db__title').filter(blast_db__title__in=set(sseqid_db.values())).values_list('blast_db__title', 'url'))
            for db_name, db_hsp_list in groupby([hsp for hsp in hsp_list if sseqid_db[hsp['sseqid']] in db_url], lambda hsp: sseqid_db[hsp['sseqid']]):
                with open(path.join(basedir, db_organism[db_name] + '.gff'), 'wb') as fgff:
                    fgff.write('##gff-version 3\n')
                    match_id = 1
                    match_part_id = 1
                    for hsp_list in [sorted(hsps, key=lambda h: (h['sstart'], h['send']) if h['sstrand'] == 'plus' else (h['send'], h['sstart'])) for _, hsps in groupby(db_hsp_list, lambda x: x['qseqid'] + x['sseqid'] + x['sstrand'])]:
                        gff_item = {'seqid': hsp_list[0]['sseqid'].split('_')[-1] if hsp_list[0]['sseqid'][:3] == 'gnl' else hsp_list[0]['sseqid'].split('|')[1],
                                    'source': blast_program}
                        # cut if overlap length > overlap_cutoff
                        spos, qpos, matches, matches_list = 0, 0, [], []
                        for hsp in hsp_list:
                            if (hsp['sstrand'] == 'plus' and (spos - hsp['sstart'] > overlap_cutoff or qpos - hsp['qstart'] > overlap_cutoff)) or (hsp['sstrand'] == 'minus' and (spos - hsp['send'] > overlap_cutoff or qpos - hsp['qlen'] + hsp['qend'] > overlap_cutoff)):
                                matches_list.append(matches)
                                matches = []
                            matches.append(hsp)
                            spos, qpos = (hsp['send'], hsp['qend']) if hsp['sstrand'] == 'plus' else (hsp['sstart'], hsp['qlen'] - hsp['qstart'])
                        matches_list.append(matches)
                        for matches in matches_list:
                            gff_item['type'] = 'match'
                            gff_item['start'] = str(matches[0]['sstart'] if matches[0]['sstrand'] == 'plus' else matches[0]['send'])
                            gff_item['end'] = str(matches[-1]['send'] if matches[0]['sstrand'] == 'plus' else matches[-1]['sstart'])
                            gff_item['score'] = '.'
                            gff_item['strand'] = '+' if matches[0]['sstrand'] == 'plus' else '-'
                            gff_item['phase'] = '0' # for type CDS, this is not the frame
                            gff_item['attributes'] = 'ID=match%05d;Name=%s;Target=%s %d %d' % (match_id, matches[0]['qseqid'], matches[0]['qseqid'], matches[0]['qstart'] if matches[0]['sstrand'] == 'plus' else matches[-1]['qstart'], matches[-1]['qend'] if matches[0]['sstrand'] == 'plus' else matches[0]['qend'])
                            if len(matches) == 1:
                                gff_item['score'] = str(matches[0]['evalue'])
                                fgff.write('\t'.join([gff_item[c] for c in gff_col_names]) + '\n')
                            else:
                                fgff.write('\t'.join([gff_item[c] for c in gff_col_names]) + '\n')
                                gff_item['type'] = 'match_part'
                                for match_part in matches:
                                    gff_item['start'] = str(match_part['sstart'] if match_part['sstrand'] == 'plus' else match_part['send'])
                                    gff_item['end'] = str(match_part['send'] if match_part['sstrand'] == 'plus' else match_part['sstart'])
                                    gff_item['score'] = str(match_part['evalue'])
                                    gff_item['attributes'] = 'ID=match_part%05d;Parent=match%05d;Target=%s %d %d' % (match_part_id, match_id, match_part['qseqid'], match_part['qstart'], match_part['qend'])
                                    fgff.write('\t'.join([gff_item[c] for c in gff_col_names]) + '\n')
                                    match_part_id += 1
                            match_id += 1
        result_status = 'SUCCESS'
    record.result_status = result_status
    record.result_date = datetime.utcnow().replace(tzinfo=utc)
    record.save()
