import csv
import json
import logging
import time
from datetime import datetime, timedelta, timezone
from itertools import groupby
from os import path, stat
from subprocess import DEVNULL, PIPE, Popen

from celery import shared_task
from celery.signals import after_task_publish, task_failure, task_success
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.cache import cache

from .gff3 import hsp_dict_list as build_hsp_dict_list, write_gff3
from .models import BlastDb, BlastQueryRecord, JbrowseSetting, Sequence
from .utils import program_name

logger = get_task_logger(__name__)

LOCK_EXPIRE = 30
LOCK_ID = 'task_list_cache_lock'
CACHE_ID = 'task_list_cache'
acquire_lock = lambda: cache.add(LOCK_ID, 'true', LOCK_EXPIRE)
release_lock = lambda: cache.delete(LOCK_ID)

RUN_BLAST_TASK = 'blast.tasks.run_blast_task'


def utcnow():
    return datetime.now(timezone.utc)


def lookup_subject_databases(sseqids, db_titles=None):
    '''Map each subject sequence id to the title of the BLAST database it came from.

    The same id may exist in more than one database (#19), so only the
    databases searched by this task are considered. If an id is still
    ambiguous, the first database title in sorted order wins.
    '''
    sequences = Sequence.objects.filter(id__in=set(sseqids))
    if db_titles:
        sequences = sequences.filter(blast_db__title__in=set(db_titles))
    sseqid_db = {}
    for sseqid, title in sequences.order_by('-blast_db__title').values_list('id', 'blast_db__title'):
        if sseqid in sseqid_db:
            logger.warning('Sequence id %s exists in several searched databases (%s, %s); set a sequence ID prefix on the databases to disambiguate', sseqid, title, sseqid_db[sseqid])
        sseqid_db[sseqid] = title
    return sseqid_db


@shared_task() # ignore_result=True
def run_blast_task(task_id, args_list, file_prefix, blast_info):
    logger.info("blast_task_id: %s" % (task_id,))

    # update dequeue time
    record = BlastQueryRecord.objects.get(task_id__exact=task_id)
    record.dequeue_date = utcnow()
    record.save()

    # update status from 'pending' to 'running' for frontend
    with open(path.join(path.dirname(file_prefix), 'status.json'), 'r') as f:
        statusdata = json.load(f)
        statusdata['status'] = 'running'

    with open(path.join(path.dirname(file_prefix), 'status.json'), 'w') as f:
        json.dump(statusdata, f)

    # run
    for args in args_list:
        p = Popen(args, stdin=DEVNULL, stdout=PIPE, stderr=PIPE)
        output, error = p.communicate()
        if p.returncode != 0:
            logger.warning('%s exited with code %d: %s', program_name(args[0]), p.returncode, error.decode('utf-8', 'replace').strip())

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
        with open(report_path, 'r', encoding='utf-8', errors='replace') as f:
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
        with open(csv_path, 'r', newline='', encoding='utf-8', errors='replace') as f:
            hsp_list = [[type_func[convert](value) for convert, value in zip(blast_info['col_types'], row)] for row in csv.reader(f)]
        # generate gff3 files
        try:
            blast_program = program_name(args_list[0][0])
            basedir = path.dirname(csv_path)
            hsp_dict_list = build_hsp_dict_list(hsp_list, blast_info['col_names'])
            # build lookup tables from db
            sseqid_db = lookup_subject_databases([hsp['sseqid'] for hsp in hsp_dict_list], blast_info.get('db_titles'))
            db_titles = set(sseqid_db.values())
            db_organism = dict(BlastDb.objects.filter(title__in=db_titles).values_list('title', 'organism__short_name'))
            db_url = dict(JbrowseSetting.objects.filter(blast_db__title__in=db_titles).values_list('blast_db__title', 'url'))
            with open(path.join(basedir, 'info.json'), 'w') as f:
                json.dump({'sseqid_db': sseqid_db, 'db_organism': db_organism, 'db_url': db_url, 'line_num_list': line_num_list}, f)
            with open(json_path, 'w') as f:
                json.dump([[sseqid_db.get(hsp_dict_list[i]['sseqid'], '')] + hsp for i, hsp in enumerate(hsp_list)], f)
            # group hsps by database, need to sort before doing groupby
            sorted_hsp_dict_list = sorted([hsp for hsp in hsp_dict_list if sseqid_db.get(hsp['sseqid']) in db_url], key=lambda a: sseqid_db[a['sseqid']])
            for db_name, db_hsp_dict_list in groupby(sorted_hsp_dict_list, key=lambda a: sseqid_db[a['sseqid']]):
                with open(path.join(basedir, db_name + '.gff'), 'w') as fgff:
                    write_gff3(fgff, db_hsp_dict_list, blast_program)
            result_status = 'SUCCESS'
        except Exception:
            logger.exception('Generating results of %s failed', task_id)
            result_status = 'NO_GFF'
    record.result_status = result_status
    record.result_date = utcnow()
    record.save()

    # generate status.json for frontend status checking
    with open(path.join(path.dirname(file_prefix), 'status.json'), 'w') as f:
        json.dump({'status': 'done'}, f)

    return task_id # passed to 'result' argument of task_success_handler

@shared_task()
def remove_files():
    '''Scheduled daily by celery beat (CELERY_BEAT_SCHEDULE).

    Only logs the expired result directories unless BLAST_REMOVE_EXPIRED_FILES is set.
    '''
    from shutil import rmtree
    expire = utcnow() - timedelta(days=settings.BLAST_RESULT_RETENTION_DAYS)
    for expired_task in BlastQueryRecord.objects.filter(result_date__lt=expire):
        task_path = path.join(settings.MEDIA_ROOT, 'blast', 'task', expired_task.task_id)
        if path.exists(task_path):
            if settings.BLAST_REMOVE_EXPIRED_FILES:
                rmtree(task_path, ignore_errors=True)
                logger.info('removed directory %s' % (task_path))
            else:
                logger.info('expired directory %s (set BLAST_REMOVE_EXPIRED_FILES to remove it)' % (task_path))

@after_task_publish.connect(sender=RUN_BLAST_TASK)
def task_sent_handler(sender=None, headers=None, body=None, **kwds):
    if settings.USE_CACHE:
        task_id = (headers or {}).get('id')
        args = body[0] if body else None
        while not acquire_lock():
            time.sleep(0.1)
        try:
            tlist = cache.get(CACHE_ID, [])
            if args:
                bid = args[0] # blast_task_id
                tlist.append( (task_id,bid) )
                logger.info('[task_sent] task sent: %s. queue length: %s' % (bid, len(tlist)) )
                cache.set(CACHE_ID, tlist)
            else:
                logger.info('[task_sent] no args. rabbit task_id: %s' % (task_id) )
        finally:
            release_lock()

@task_success.connect(sender=run_blast_task)
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

@task_failure.connect(sender=run_blast_task)
def task_failure_handler(sender=None, task_id=None, exception=None,
                         args=None, kwargs=None, traceback=None, einfo=None, **kwds):
    if settings.USE_CACHE:
        logger.info('[task_failure] task failed. rabbit task_id: %s' % (task_id) )
        task_success_handler(sender, task_id)
