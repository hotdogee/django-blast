from __future__ import absolute_import

from celery import shared_task
import time
import json
import subprocess
import datetime
from blast.models import BlastQueryRecord
from os import path, stat
import pytz

blast_out_col_name_str = 'qseqid sseqid evalue qlen slen length nident mismatch positive gapopen gaps qstart qend sstart send bitscore qcovs qframe sframe'
blast_out_col_names = blast_out_col_name_str.split()
blast_out_ext = {}
blast_out_ext['.0'] = '0' 
blast_out_ext['.html'] = '0' 
blast_out_ext['.1'] = '1' 
blast_out_ext['.3'] = '3' 
blast_out_ext['.xml'] = '5' 
blast_out_ext['.tsv'] = '6 ' + blast_out_col_name_str
blast_out_ext['.csv'] = '10 ' + blast_out_col_name_str

@shared_task
def run(msg):
    """
    example msg:
    task_id=3ee04cec89b54d33ba557335b7b7134darg=["/usr/local/i5k/blast/bin_linux/blastn", "-query", "/usr/local/i5k/media/3ee04cec89b54d33ba557335b7b7134d/3ee04cec89b54d33ba557335b7b7134d.in", "-db", "Agla_Btl03082013.genome_new_ids.fa Ccap01172013-genome_new_ids.fa", "-outfmt", "11", "-out", "/usr/local/i5k/media/3ee04cec89b54d33ba557335b7b7134d/3ee04cec89b54d33ba557335b7b7134d.asn", "-num_threads", "6"]fmt=/usr/local/i5k/blast/bin_linux/blast_formatter
    """

    task_id = msg[(msg.find("task_id=")+8):(msg.find("arg="))]
    task_arg = msg[(msg.find("arg=")+4):(msg.find("fmt="))]
    blast_formatter_path = msg[(msg.find("fmt=")+4):]
    
    # update dequeue time
    BlastQueryRecord.objects.filter(task_id=task_id).update(dequeue_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc))

    args = json.loads(task_arg)
    
    # run blast process
    subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE).wait()
    
    # convert to multiple formats
    asn_filename = args[-3] # ex. /usr/local/i5k/media/3ee04cec89b54d33ba557335b7b7134d/3ee04cec89b54d33ba557335b7b7134d.asn
    file_prefix = args[-3].replace('.asn', '') 
    for ext, outfmt in blast_out_ext.items():
        args = [blast_formatter_path, '-archive', asn_filename, '-outfmt', outfmt, '-out', file_prefix + ext]
        if ext == '.html':
            args.append('-html')
        subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE).wait()

    result_status = ''
    # check running status
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
    BlastQueryRecord.objects.filter(task_id=task_id).update(result_status=result_status)

    # update job finish time
    BlastQueryRecord.objects.filter(task_id=task_id).update(result_date=datetime.datetime.utcnow().replace(tzinfo=pytz.utc))
