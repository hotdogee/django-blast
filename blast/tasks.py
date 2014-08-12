from __future__ import absolute_import
from celery import shared_task
from subprocess import Popen, PIPE
from datetime import datetime
from .models import BlastQueryRecord, Sequence, BlastDb, JbrowseSetting
from os import path, stat
from pytz import utc
from itertools import groupby
import csv
import json

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
        # parse .0, and save index in line_num_list
        report_path = file_prefix + '.0'
        line_num_list = []
        with open(report_path, 'rb') as f:
            target_str = ' Score ='
            line_num = 0
            for line in f:
                if line[:len(target_str)] == target_str:
                    line_num_list.append(line_num)
                line_num += 1
        # read csv and convert to appropreate types
        csv_path = file_prefix + '.csv'
        json_path = file_prefix + '.json'
        type_func = {'str': str, 'float': float, 'int': int}
        hsp_list = []
        with open(csv_path, 'rb') as f:
            hsp_list = [[type_func[convert](value) for convert, value in zip(blast_info['col_types'], row)] for row in csv.reader(f)]
        # generate gff3 files
        try:
            overlap_cutoff = 5
            blast_program = path.basename(args_list[0][0])
            basedir = path.dirname(csv_path)
            gff_col_names = 'seqid source type start end score strand phase attributes'.split()
            # build hsp_dict_list with extra strand info, always let qend > qstart, if not swap both query and subject cords, than set strand
            cid = dict([(v, i) for i, v in enumerate(blast_info['col_names'])])
            hsp_dict_col_names = 'qseqid sseqid evalue qlen qstart qend sstart send sstrand'.split()
            hsp_dict_list = [dict(zip(hsp_dict_col_names, [row[cid['qseqid']], row[cid['sseqid']], row[cid['evalue']], row[cid['qlen']], row[cid['qend']], row[cid['qstart']], row[cid['send']], row[cid['sstart']], '-' if row[cid['sstart']] - row[cid['send']] < 0 else '+'] if row[cid['qend']] - row[cid['qstart']] < 0 else [row[cid['qseqid']], row[cid['sseqid']], row[cid['evalue']], row[cid['qlen']], row[cid['qstart']], row[cid['qend']], row[cid['sstart']], row[cid['send']], '-' if row[cid['send']] - row[cid['sstart']] < 0 else '+'])) for row in hsp_list]
            # build lookup tables from db
            sseqid_db = dict(Sequence.objects.select_related('blastdb').filter(id__in=set([hsp['sseqid'] for hsp in hsp_dict_list])).values_list('id', 'blast_db__title'))
            db_organism = dict(BlastDb.objects.select_related('organism').filter(title__in=set(sseqid_db.values())).values_list('title', 'organism__short_name'))
            db_url = dict(JbrowseSetting.objects.select_related('blastdb').filter(blast_db__title__in=set(sseqid_db.values())).values_list('blast_db__title', 'url'))
            with open(path.join(basedir, 'info.json'), 'wb') as f:
                json.dump({'sseqid_db': sseqid_db, 'db_organism': db_organism, 'db_url': db_url, 'line_num_list': line_num_list}, f)
            # group hsps by database, need to sort before doing groupby
            sorted_hsp_dict_list = sorted([hsp for hsp in hsp_dict_list if sseqid_db[hsp['sseqid']] in db_url], key=lambda a: sseqid_db[a['sseqid']])
            db_count = 0
            for db_name, db_hsp_dict_list in groupby(sorted_hsp_dict_list, key=lambda a: sseqid_db[a['sseqid']]):
                with open(path.join(basedir, db_name + '.gff'), 'wb') as fgff:
                    fgff.write('##gff-version 3\n')
                    db_count += 1
                    match_id = 1
                    match_part_id = 1
                    # sort before groupby
                    sorted_db_hsp_dict_list = sorted(db_hsp_dict_list, key=lambda x: x['qseqid'] + x['sseqid'] + x['sstrand'])
                    # group hsps with the same key = qseqid + sseqid + sstrand, sort groups asc on sstart or send according to sstrand
                    for key_db_hsp_dict_list in [sorted(hsps, key=lambda h: (h['sstart'], h['send']) if h['sstrand'] == '+' else (h['send'], h['sstart'])) for _, hsps in groupby(sorted_db_hsp_dict_list, key=lambda x: x['qseqid'] + x['sseqid'] + x['sstrand'])]:
                        # seqid parsing currently customized for i5k
                        seqid = key_db_hsp_dict_list[0]['sseqid'] if len(key_db_hsp_dict_list[0]['sseqid'].split('|')) < 2 else key_db_hsp_dict_list[0]['sseqid'].split('|')[1]
                        gff_item = {'seqid': key_db_hsp_dict_list[0]['sseqid'].split('|')[-1].split('_', 1)[-1] if key_db_hsp_dict_list[0]['sseqid'][:3] == 'gnl' else seqid,
                                    'source': blast_program}
                        # cut if overlap length > overlap_cutoff
                        spos, qpos, matches, matches_list = 0, 0, [], []
                        for hsp in key_db_hsp_dict_list:
                            if (hsp['sstrand'] == '+' and (spos - hsp['sstart'] > overlap_cutoff or qpos - hsp['qstart'] > overlap_cutoff)) or (hsp['sstrand'] == '-' and (spos - hsp['send'] > overlap_cutoff or qpos - hsp['qlen'] + hsp['qend'] > overlap_cutoff)):
                                matches_list.append(matches)
                                matches = []
                            matches.append(hsp)
                            spos, qpos = (hsp['send'], hsp['qend']) if hsp['sstrand'] == '+' else (hsp['sstart'], hsp['qlen'] - hsp['qstart'])
                        matches_list.append(matches)
                        for matches in matches_list:
                            gff_item['type'] = 'match'
                            gff_item['start'] = str(matches[0]['sstart'] if matches[0]['sstrand'] == '+' else matches[0]['send'])
                            gff_item['end'] = str(matches[-1]['send'] if matches[0]['sstrand'] == '+' else matches[-1]['sstart'])
                            gff_item['score'] = '.'
                            gff_item['strand'] = matches[0]['sstrand']
                            gff_item['phase'] = '0' # for type CDS, this is not the frame
                            gff_item['attributes'] = 'ID=match%05d;Name=%s;Target=%s %d %d' % (match_id, matches[0]['qseqid'], matches[0]['qseqid'], matches[0]['qstart'] if matches[0]['sstrand'] == '+' else matches[-1]['qstart'], matches[-1]['qend'] if matches[0]['sstrand'] == '+' else matches[0]['qend'])
                            if len(matches) == 1:
                                gff_item['score'] = str(matches[0]['evalue'])
                            fgff.write('\t'.join([gff_item[c] for c in gff_col_names]) + '\n')
                            gff_item['type'] = 'match_part'
                            for match_part in matches:
                                gff_item['start'] = str(match_part['sstart'] if match_part['sstrand'] == '+' else match_part['send'])
                                gff_item['end'] = str(match_part['send'] if match_part['sstrand'] == '+' else match_part['sstart'])
                                gff_item['score'] = str(match_part['evalue'])
                                gff_item['attributes'] = 'ID=match_part%05d;Parent=match%05d;Target=%s %d %d' % (match_part_id, match_id, match_part['qseqid'], match_part['qstart'], match_part['qend'])
                                fgff.write('\t'.join([gff_item[c] for c in gff_col_names]) + '\n')
                                match_part_id += 1
                            match_id += 1
            with open(json_path, 'wb') as f:
                json.dump([[db_organism[sseqid_db[hsp_dict_list[i]['sseqid']]] if sseqid_db[hsp_dict_list[i]['sseqid']] in db_url else ''] + hsp for i, hsp in enumerate(hsp_list)], f)
            result_status = 'SUCCESS'
        except Exception, e:
            print Exception, e
            with open(json_path, 'wb') as f:
                json.dump([hsp + [''] for i, hsp in enumerate(hsp_list)], f)
            result_status = 'NO_GFF'
    record.result_status = result_status
    record.result_date = datetime.utcnow().replace(tzinfo=utc)
    record.save()

    # generate status.json for frontend statu checking
    statusdir = path.dirname(file_prefix + '.in')
    with open(path.join(statusdir, 'status.json'), 'wb') as f:
        json.dump({'status': 'done'}, f)
