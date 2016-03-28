from __future__ import absolute_import
from celery import shared_task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
from subprocess import Popen, PIPE, call
from datetime import datetime, timedelta
from os import path, chdir, getcwd, devnull
from pytz import utc
from celery.utils.log import get_task_logger
from celery.signals import task_sent, task_success, task_failure
from django.core.cache import cache
from django.conf import settings
import json
import time
from clustal.models import ClustalQueryRecord

logger = get_task_logger(__name__)

if settings.USE_CACHE:
    LOCK_EXPIRE = 30
    LOCK_ID = 'task_list_cache_lock'
    CACHE_ID = 'task_list_cache'
    acquire_lock = lambda: cache.add(LOCK_ID, 'true', LOCK_EXPIRE)
    release_lock = lambda: cache.delete(LOCK_ID)

@shared_task() # ignore_result=True
def run_clustal_task(task_id, args_list, file_prefix):
    import django
    django.setup()

    logger.info("clustal_task_id: %s" % (task_id,))

    chdir(path.dirname(file_prefix))

    # update dequeue time
    record = ClustalQueryRecord.objects.get(task_id__exact=task_id)
    record.dequeue_date = datetime.utcnow().replace(tzinfo=utc)
    record.save()

    
    # update status from 'pending' to 'running' for frontend
    with open('status.json', 'r') as f:
        statusdata = json.load(f)
        statusdata['status'] = 'running'

    with open('status.json', 'w') as f:
        json.dump(statusdata, f)

    # run
    FNULL = open(devnull, 'w')
    for args in args_list:
        p = Popen(args, stdout=FNULL, stderr=PIPE)
        p.wait()

    # generate status.json for frontend status checking
    if not path.isfile(file_prefix + '.aln'):
        result_status = "FAILURE"
    else:
        result_status = 'SUCCESS'

    record.result_status = result_status
    record.result_date = datetime.utcnow().replace(tzinfo=utc)
    record.save()

    with open('status.json', 'r') as f:
        statusdata = json.load(f)
        statusdata['status'] = 'done'
    with open('status.json', 'wb') as f:
        json.dump(statusdata, f)

    return task_id # passed to 'result' argument of task_success_handler

@periodic_task(run_every=(crontab(hour='0', minute='10'))) # Execute daily at midnight
def remove_files():
    from shutil import rmtree
    logger.info('removing expired files (under test, not working actually)')
    for expired_task in ClustalQueryRecord.objects.filter(result_date__lt=(datetime.utcnow().replace(tzinfo=utc) + timedelta(days=-7))):
        task_path = path.join(settings.MEDIA_ROOT, 'clustal', 'task', expired_task.task_id)
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
                bid = args[0] # clustal_task_id
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
            clustal_task_id = result
            tlist = cache.get(CACHE_ID, [])
            if tlist and clustal_task_id:
                for tuple in tlist:
                    if clustal_task_id in tuple:
                        tlist.remove(tuple)
                        logger.info('[task_success] task removed from queue: %s' % (clustal_task_id) )
                        break
                logger.info('[task_success] task done: %s. queue length: %s' % (clustal_task_id, len(tlist)) )
                cache.set(CACHE_ID, tlist)
            else:
                logger.info('[task_success] no queue list or clustal task id.')
        finally:
            release_lock()

@task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None,
                         args=None, kwargs=None, traceback=None, einfo=None, **kwds):
    if settings.USE_CACHE:
        logger.info('[task_failure] task failed. rabbit task_id: %s' % (task_id) )
        task_success_handler(sender, task_id)
