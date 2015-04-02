from __future__ import absolute_import
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from subprocess import Popen, PIPE
from datetime import datetime, timedelta
from .models import BlastQueryRecord, Sequence, BlastDb, JbrowseSetting
from os import path, stat
from pytz import utc
from itertools import groupby
from celery.utils.log import get_task_logger
from celery.signals import task_sent, task_success, task_failure
from django.core.cache import cache
from django.conf import settings
import csv
import json
import time

logger = get_task_logger(__name__)

if settings.USE_CACHE:
    LOCK_EXPIRE = 30
    LOCK_ID = 'task_list_cache_lock'
    CACHE_ID = 'task_list_cache'
    acquire_lock = lambda: cache.add(LOCK_ID, 'true', LOCK_EXPIRE)
    release_lock = lambda: cache.delete(LOCK_ID)

@shared_task() # ignore_result=True
def run_blast_task(task_id, args_list, file_prefix, blast_info):
    import django
    django.setup()
    
    logger.info("blast_task_id: %s" % (task_id,))

    # update dequeue time
    record = BlastQueryRecord.objects.get(task_id__exact=task_id)
    record.dequeue_date = datetime.utcnow().replace(tzinfo=utc)
    record.save()

    # update status from 'pending' to 'running' for frontend
    with open(path.join(path.dirname(file_prefix), 'status.json'), 'r') as f:
        statusdata = json.load(f)
        statusdata['status'] = 'running'

    with open(path.join(path.dirname(file_prefix), 'status.json'), 'w') as f:
        json.dump(statusdata, f)

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
            blast_program = path.basename(args_list[0][0])
            basedir = path.dirname(csv_path)
            gff_col_names = 'seqid source type start end score strand phase attributes'.split()
            # build hsp_dict_list with extra strand info, always let qend > qstart, if not swap both query and subject cords, than set strand
            cid = dict([(v, i) for i, v in enumerate(blast_info['col_names'])])
            hsp_dict_col_names = 'qseqid sseqid evalue bitscore qlen qstart qend sstart send qstrand sstrand'.split()
            hsp_dict_list = [dict(zip(hsp_dict_col_names, [row[cid['qseqid']], row[cid['sseqid']], row[cid['evalue']], row[cid['bitscore']], row[cid['qlen']], row[cid['qstart']], row[cid['qend']], row[cid['sstart']], row[cid['send']], '-' if row[cid['qend']] - row[cid['qstart']] < 0 else '+', '-' if row[cid['send']] - row[cid['sstart']] < 0 else '+'])) for row in hsp_list]
            # build lookup tables from db
            sseqid_db = dict(Sequence.objects.select_related('blastdb').filter(id__in=set([hsp['sseqid'] for hsp in hsp_dict_list])).values_list('id', 'blast_db__title'))
            db_organism = dict(BlastDb.objects.select_related('organism').filter(title__in=set(sseqid_db.values())).values_list('title', 'organism__short_name'))
            db_url = dict(JbrowseSetting.objects.select_related('blastdb').filter(blast_db__title__in=set(sseqid_db.values())).values_list('blast_db__title', 'url'))
            with open(path.join(basedir, 'info.json'), 'wb') as f:
                json.dump({'sseqid_db': sseqid_db, 'db_organism': db_organism, 'db_url': db_url, 'line_num_list': line_num_list}, f)
            with open(json_path, 'wb') as f:
                json.dump([[sseqid_db[hsp_dict_list[i]['sseqid']]] + hsp for i, hsp in enumerate(hsp_list)], f)
            overlap_cutoff = 5
            # group hsps by database, need to sort before doing groupby
            sorted_hsp_dict_list = sorted([hsp for hsp in hsp_dict_list if sseqid_db[hsp['sseqid']] in db_url], key=lambda a: sseqid_db[a['sseqid']])
            for db_name, db_hsp_dict_list in groupby(sorted_hsp_dict_list, key=lambda a: sseqid_db[a['sseqid']]):
                with open(path.join(basedir, db_name + '.gff'), 'wb') as fgff:
                    fgff.write('##gff-version 3\n')
                    match_id = 1
                    match_part_id = 1
                    # sort before groupby using key = qseqid + sseqid + qstrand + sstrand
                    sorted_db_hsp_dict_list = sorted(db_hsp_dict_list, key=lambda x: x['qseqid'] + x['sseqid'] + x['qstrand'] + x['sstrand'])
                    # group hsps with the same key = qseqid + sseqid + qstrand + sstrand, sort groups asc on sstart or send according to sstrand
                    for key_db_hsp_dict_list in [sorted(hsps, key=lambda h: (h['sstart'], h['send']) if h['sstrand'] == '+' else (h['send'], h['sstart'])) for _, hsps in groupby(sorted_db_hsp_dict_list, key=lambda x: x['qseqid'] + x['sseqid'] + x['qstrand'] + x['sstrand'])]:
                        # seqid parsing currently customized for i5k
                        original_seqid = key_db_hsp_dict_list[0]['sseqid']
                        original_seqid_tokens = original_seqid.split('|')
                        if len(original_seqid_tokens) < 2 or original_seqid[:3] == 'gi|':
                            seqid = original_seqid
                        elif original_seqid[:3] == 'gnl':
                            seqid = original_seqid_tokens[-1].split('_', 1)[-1]
                        else:
                            seqid = original_seqid_tokens[1]
                        gff_item = {'seqid': seqid, 'source': blast_program}
                        # cut if overlap length > overlap_cutoff
                        spos, qpos, matches, matches_list = 0, 0, [], []
                        for hsp in key_db_hsp_dict_list:
                            cut = False
                            if hsp['sstrand'] == '+':
                                if hsp['qstrand'] == '+':
                                    if (spos - hsp['sstart'] > overlap_cutoff or qpos - hsp['qstart'] > overlap_cutoff):
                                        cut = True
                                    spos, qpos = (hsp['send'], hsp['qend'])
                                else:
                                    if (spos - hsp['sstart'] > overlap_cutoff or qpos - (hsp['qlen'] - hsp['qstart']) > overlap_cutoff):
                                        cut = True
                                    spos, qpos = (hsp['send'], hsp['qlen'] - hsp['qend'])
                            else:
                                if hsp['qstrand'] == '+':
                                    if (spos - hsp['send'] > overlap_cutoff or qpos - (hsp['qlen'] - hsp['qend']) > overlap_cutoff):
                                        cut = True
                                    spos, qpos = (hsp['sstart'], hsp['qlen'] - hsp['qstart'])
                                else:
                                    if (spos - hsp['send'] > overlap_cutoff or qpos - hsp['qend'] > overlap_cutoff):
                                        cut = True
                                    spos, qpos = (hsp['sstart'], hsp['qstart'])
                            if cut:
                                matches_list.append(matches)
                                matches = []
                            matches.append(hsp)
                        matches_list.append(matches)
                        for matches in matches_list:
                            gff_item['type'] = 'match'
                            gff_item['start'] = str(matches[0]['sstart'] if matches[0]['sstrand'] == '+' else matches[0]['send'])
                            gff_item['end'] = str(matches[-1]['send'] if matches[0]['sstrand'] == '+' else matches[-1]['sstart'])
                            gff_item['score'] = '.'
                            gff_item['strand'] = matches[0]['sstrand']
                            gff_item['phase'] = '0' # for type CDS, this is not the frame
                            gff_item['attributes'] = 'ID=match%05d;Name=%s;Target=%s %d %d %s' % (match_id, matches[0]['qseqid'], matches[0]['qseqid'], min(matches[0]['qstart'], matches[0]['qend'], matches[-1]['qstart'], matches[-1]['qend']), max(matches[0]['qstart'], matches[0]['qend'], matches[-1]['qstart'], matches[-1]['qend']), matches[0]['qstrand'])
                            if len(matches) == 1:
                                gff_item['score'] = str(matches[0]['evalue'])
                            fgff.write('\t'.join([gff_item[c] for c in gff_col_names]) + '\n')
                            gff_item['type'] = 'match_part'
                            for match_part in matches:
                                gff_item['start'] = str(match_part['sstart'] if match_part['sstrand'] == '+' else match_part['send'])
                                gff_item['end'] = str(match_part['send'] if match_part['sstrand'] == '+' else match_part['sstart'])
                                gff_item['score'] = str(match_part['evalue'])
                                gff_item['attributes'] = 'ID=match_part%05d;Parent=match%05d;Target=%s %d %d %s;Bitscore=%g' % (match_part_id, match_id, match_part['qseqid'], min(match_part['qstart'], match_part['qend']), max(match_part['qstart'], match_part['qend']), match_part['qstrand'], match_part['bitscore'])
                                fgff.write('\t'.join([gff_item[c] for c in gff_col_names]) + '\n')
                                match_part_id += 1
                            match_id += 1
            result_status = 'SUCCESS'
        except Exception, e:
            # print Exception, e
            result_status = 'NO_GFF'
    record.result_status = result_status
    record.result_date = datetime.utcnow().replace(tzinfo=utc)
    record.save()

    # generate status.json for frontend status checking
    with open(path.join(path.dirname(file_prefix), 'status.json'), 'wb') as f:
        json.dump({'status': 'done'}, f)

    return task_id # passed to 'result' argument of task_success_handler

@periodic_task(run_every=(crontab(hour='0', minute='10'))) # Execute daily at midnight
def remove_files():
    from shutil import rmtree
    logger.info('removing expired files (under test, not working actually)')
    for expired_task in BlastQueryRecord.objects.filter(result_date__lt=(datetime.utcnow().replace(tzinfo=utc) + timedelta(days=-7))):
        task_path = path.join(settings.MEDIA_ROOT, 'blast', 'task', expired_task.task_id)
        if path.exists(task_path):
            #rmtree(task_path)
            logger.info('removed directory %s' % (task_path))

@task_sent.connect
def task_sent_handler(sender=None, task_id=None, task=None, args=None,
                      kwargs=None, **kwds):
    if settings.USE_CACHE:
        while not acquire_lock():
            time.sleep(0.1)
        try:
            tlist = cache.get(CACHE_ID, [])
            if args:
                bid = args[0] # blast_task_id
                tlist.append( (task_id,bid) )
                #logger.info('[task_sent] task sent: %s. queue length: %s' % (bid, len(tlist)) )
                print('[task_sent] task sent: %s. queue length: %s' % (bid, len(tlist)) )
                cache.set(CACHE_ID, tlist)
            else:
                logger.info('[task_sent] no args. rabbit task_id: %s' % (task_id) )
        finally:
            release_lock()

@task_success.connect
def task_success_handler(sender=None, result=None, **kwds):
    if settings.USE_CACHE:
        while not acquire_lock():
            time.sleep(0.1)
        try:
            blast_task_id = result
            tlist = cache.get(CACHE_ID, [])
            if tlist and blast_task_id:
                for tuple in tlist:
                    if blast_task_id in tuple:
                        tlist.remove(tuple)
                        logger.info('[task_success] task removed from queue: %s' % (blast_task_id) )
                        break
                logger.info('[task_success] task done: %s. queue length: %s' % (blast_task_id, len(tlist)) )
                cache.set(CACHE_ID, tlist)
            else:
                logger.info('[task_success] no queue list or blast task id.')
        finally:
            release_lock()

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None,
                         args=None, kwargs=None, traceback=None, einfo=None, **kwds):
    if settings.USE_CACHE:
        logger.info('[task_failure] task failed. rabbit task_id: %s' % (task_id) )
        task_success_handler(sender, task_id)
