from __future__ import absolute_import
from celery import shared_task
from subprocess import Popen, PIPE
from datetime import datetime
from blast.models import BlastQueryRecord
from os import path, stat
from pytz import utc

@shared_task(ignore_result=True)
def run_blast_task(task_id, args_list):
    import django
    django.setup()
    
    # update dequeue time
    BlastQueryRecord.objects.get(task_id__exact=task_id).update(dequeue_date=datetime.utcnow().replace(tzinfo=utc))

    # run
    for args in args_list:
        Popen(args, stdin=PIPE, stdout=PIPE).wait()

    # get result state
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
        result_status = 'SUCCESS'
    BlastQueryRecord.objects.get(task_id__exact=task_id).update(result_status=result_status)

    # update job finish time
    BlastQueryRecord.objects.get(task_id__exact=task_id).update(result_date=datetime.utcnow().replace(tzinfo=utc))
