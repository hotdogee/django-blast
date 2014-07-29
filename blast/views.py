# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.template import RequestContext
from uuid import uuid4
from os import path, makedirs, chmod
from django.conf import settings
from sys import platform
from blast.models import BlastQueryRecord
from rabbitmq import receiver
from datetime import datetime, timedelta
from pytz import timezone
import subprocess
import json
import csv
import traceback
import stat


blast_out_col_types = [str, str, float, int, int, int, int, int, int, int, int, int, int, int, int, float, int, int, int]
blast_out_col_name_str = 'qseqid sseqid evalue qlen slen length nident mismatch positive gapopen gaps qstart qend sstart send bitscore qcovs qframe sframe'
blast_out_col_names = blast_out_col_name_str.split()
#blast_out_ext = {}
#blast_out_ext['.0'] = '0'
#blast_out_ext['.html'] = '0'
#blast_out_ext['.1'] = '1'
#blast_out_ext['.3'] = '3'
#blast_out_ext['.xml'] = '5'
#blast_out_ext['.tsv'] = '6 ' + blast_out_col_name_str
#blast_out_ext['.csv'] = '10 ' + blast_out_col_name_str

def create(request):
    #return HttpResponse("BLAST Page: create.")
    if request.method == 'GET':
        return render(
            request,
            'blast/main.html',
        )
    elif request.method == 'POST':
        # setup file paths
        task_id = uuid4().hex # TODO: Create from hash of input to check for duplicate inputs
        file_prefix = path.join(settings.MEDIA_ROOT, task_id, task_id)
        query_filename = file_prefix + '.in'
        asn_filename = file_prefix + '.asn'
        if not path.exists(path.dirname(query_filename)):
            makedirs(path.dirname(query_filename))
        chmod(path.dirname(query_filename), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # ensure the standalone dequeuing process can open files in the directory
        bin_name = 'bin_linux'
        if platform == 'win32':
            bin_name = 'bin_win'
        # write query to file
        if 'query-file' in request.FILES:
            with open(query_filename, 'wb+') as query_f:
                for chunk in request.FILES['query-file'].chunks():
                    query_f.write(chunk)
        elif 'query-sequence' in request.POST and request.POST['query-sequence']:
            with open(query_filename, 'wb+') as query_f:
                query_f.write(request.POST['query-sequence'])
        chmod(query_filename, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO) # ensure the standalone dequeuing process can access the file
        # build blast command
        db_list = ' '.join(request.POST.getlist('db-name'))
        # check if program is in list for security
        if request.POST['program'] in ['blastn', 'tblastn', 'tblastx', 'blastp', 'blastx']:
            program_path = path.join(settings.PROJECT_ROOT, 'blast', bin_name, request.POST['program'])
            #args = [program_path, '-query', query_filename, '-db', db_list, '-html']
            args = [program_path, '-query', query_filename, '-db', db_list, '-outfmt', '11', '-out', asn_filename, '-num_threads', '6']
            # run blast process
            #subprocess.Popen(args).wait()
            # convert to multiple formats
            blast_formatter_path = path.join(settings.PROJECT_ROOT, 'blast', bin_name, 'blast_formatter')

            r = BlastQueryRecord()
            r.task_id = task_id
            r.save()

            task_arg = json.dumps(args)
            receiver.assign(task_id, task_arg, blast_formatter_path)

            #for ext, outfmt in blast_out_ext.items():
            #    args = [blast_formatter_path, '-archive', asn_filename, '-outfmt', outfmt, '-out', file_prefix + ext]
            #    if ext == '.html':
            #        args.append('-html')
            #    subprocess.Popen(args).wait()
            return redirect('blast:retrieve', task_id)
        else:
            raise Http404

def retrieve(request, task_id='1'):
    #return HttpResponse("BLAST Page: retrieve = %s." % (task_id))
    try:
        r = BlastQueryRecord.objects.get(task_id=task_id)

        # if result is generated and not expired
        if r.result_date and (r.result_date.replace(tzinfo=None) >= (datetime.utcnow()+ timedelta(days=-7))):
            # parse csv
            file_prefix = path.join(settings.MEDIA_ROOT, task_id, task_id)
            results_data = []
            with open(file_prefix + '.csv', 'r') as f:
                cr = csv.reader(f)
                for row in cr:
                    results_data.append(tuple(convert(value) for convert, value in zip(blast_out_col_types, row)))
            # detail results
            results_detail = ''
            with open(file_prefix + '.html', 'r') as f:
                results_detail = f.read()
            return render(
                request,
                'blast/results.html',
                RequestContext(request,
                {
                    'results_col_names': json.dumps(blast_out_col_names),
                    'results_data': json.dumps(results_data),
                    'results_detail': results_detail,
                    'task_id': task_id,
                })
            )
        else:
            enqueue_date = r.enqueue_date.astimezone(timezone('US/Eastern')).strftime('%d %b %Y %X %Z')
            if r.dequeue_date:
                dequeue_date = r.dequeue_date.astimezone(timezone('US/Eastern')).strftime('%d %b %Y %X %Z')
            else:
                dequeue_date = None
            # result is exipired
            isExpired = False
            if r.result_date and (r.result_date.replace(tzinfo=None) < (datetime.utcnow()+ timedelta(days=-7))):
                isExpired = True
            return render(request, 'blast/results_not_existed.html', {
                'task_id': task_id,
                'isExpired': isExpired,
                'enqueue_date': enqueue_date,
                'dequeue_date': dequeue_date,
            })
    except:
        return HttpResponse(traceback.format_exc())
        #raise Http404
