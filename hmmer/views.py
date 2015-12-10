from __future__ import absolute_import
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache
from uuid import uuid4
from os import path, makedirs, chmod
from .tasks import run_hmmer_task
from datetime import datetime, timedelta
from pytz import timezone
import json
import traceback
import stat as Perm
from itertools import groupby
from hmmer.models import HmmerQueryRecord, HmmerDB
import os
from subprocess import Popen, PIPE


def create(request):
    if request.method == 'GET':
        hmmerdb_list = sorted([['Protein', "Protein", db.title, db.organism.display_name, db.description] for db in
                               HmmerDB.objects.select_related('organism').filter(is_shown=True)],
                              key=lambda x: (x[3], x[1], x[0], x[2]))
        hmmerdb_type_counts = dict([(k.lower().replace(' ', '_'), len(list(g))) for k, g in
                                    groupby(sorted(hmmerdb_list, key=lambda x: x[0]), key=lambda x: x[0])])


        clustal_content = []
        if ("clustal_task_id" in request.GET):
            clustal_aln = path.join(settings.MEDIA_ROOT, 'clustal', 'task', request.GET['clustal_task_id'],
                                     request.GET['clustal_task_id'] + ".aln")

            with open(clustal_aln, 'r') as content_file:
                for line in content_file:
                    clustal_content.append(line)

        return render(request, 'hmmer/main.html', {
            'title': 'HMMER Query',
            'hmmerdb_list': json.dumps(hmmerdb_list),
            'hmmerdb_type_counts': hmmerdb_type_counts,
            'clustal_content': "".join(clustal_content),
        })
    elif request.method == 'POST' and request.POST['format_check'] == "True":
        tmp_dir = path.join(settings.MEDIA_ROOT, 'hmmer', 'tmp')
        if not path.exists(tmp_dir):
            makedirs(tmp_dir)
        chmod(tmp_dir, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO)
        os.chdir(tmp_dir)

        if 'query-file' in request.FILES:
            query_filename = request.FILES['query-file'].name
            with open(query_filename, 'wb') as query_f:
                for chunk in request.FILES['query-file'].chunks():
                    query_f.write(chunk)
        elif 'query-sequence' in request.POST and request.POST['query-sequence']:
            query_filename = uuid4().hex + 'in'
            with open(query_filename, 'wb') as query_f:
                query_f.write(request.POST['query-sequence'])
        else:
            return render(request, 'hmmer/invalid_query.html', {'title': 'Invalid Query', })

        p = Popen(["hmmbuild","--fast", '--amino', "out", query_filename], stdout=PIPE, stderr=PIPE)
        p.wait()
        result = p.communicate()[1]
        return HttpResponse(result)

    elif request.method == 'POST':
        # setup file paths

        task_id = uuid4().hex
        task_dir = path.join(settings.MEDIA_ROOT, 'hmmer', 'task', task_id)
        # file_prefix only for task...
        file_prefix = path.join(settings.MEDIA_ROOT, 'hmmer', 'task', task_id, task_id)
        if not path.exists(task_dir):
            makedirs(task_dir)
        chmod(task_dir,
              Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO)  # ensure the standalone dequeuing process can open files in the directory
        # change directory to task directory
        os.chdir(task_dir)

        if 'query-file' in request.FILES:
            query_filename = request.FILES['query-file'].name
            with open(query_filename, 'wb') as query_f:
                for chunk in request.FILES['query-file'].chunks():
                    query_f.write(chunk)
        elif 'query-sequence' in request.POST and request.POST['query-sequence']:
            query_filename = task_id + '.in'
            with open(query_filename, 'wb') as query_f:
                query_f.write(request.POST['query-sequence'])
        else:
            return render(request, 'hmmer/invalid_query.html', {'title': 'Invalid Query', })

        chmod(query_filename,
              Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO)  # ensure the standalone dequeuing process can access the file

        # build hmmer command
        db_list = ' '.join(
            [db.fasta_file.path_full for db in HmmerDB.objects.filter(title__in=set(request.POST.getlist('db-name')))])
        for db in db_list.split(' '):
            os.symlink(db, db[db.rindex('/') + 1:])

        if not db_list:
            return render(request, 'hmmer/invalid_query.html', {'title': 'Invalid Query', })

        # check if program is in list for security
        if request.POST['program'] in ['phmmer', 'hmmsearch']:
            option_params = []
            if (request.POST['cutoff'] == 'evalue'):
                option_params.extend(['--incE', request.POST['s_sequence'], '--incdomE', request.POST['s_hit']])
                option_params.extend(['-E', request.POST['r_sequence'], '--domE', request.POST['r_hit']])
            elif (request.POST['cutoff'] == 'bitscore'):
                option_params.extend(['--incT', request.POST['s_sequence'], '--incdomT', request.POST['s_hit']])
                option_params.extend(['-T', request.POST['r_sequence'], '--domT', request.POST['r_hit']])

            record = HmmerQueryRecord()
            record.task_id = task_id
            if request.user.is_authenticated():
                record.user = request.user
            record.save()

            # generate status.json for frontend statu checking
            with open(query_filename, 'r') as f:  # count number of query sequence by counting '>'
                qstr = f.read()
                seq_count = qstr.count('>')
                if (seq_count == 0):
                    seq_count = 1
                with open('status.json', 'wb') as f:
                    json.dump({'status': 'pending', 'seq_count': seq_count,
                               'db_list': [db[db.rindex('/') + 1:] for db in db_list.split(' ')], 'program':request.POST['program'], 'params':option_params, 'input':query_filename}, f)

            args_list = []
            if (request.POST['program'] == 'hmmsearch'):
                args_list.append(['hmmbuild', '--amino', '-o', 'hmm.sumary', query_filename + '.hmm', query_filename])
                for idx, db in enumerate(db_list.split()):
                    args_list.append(['hmmsearch', '-o', str(idx) + '.out'] + option_params + [query_filename + '.hmm',
                                                                                               os.path.basename(db)])
            else:
                for idx, db in enumerate(db_list.split()):
                    args_list.append(
                        ['phmmer', '-o', str(idx) + '.out'] + option_params + [query_filename, os.path.basename(db)])

            run_hmmer_task.delay(task_id, args_list, file_prefix)

            return redirect('hmmer:retrieve', task_id)
        else:
            raise Http404


def retrieve(request, task_id='1'):
    try:
        r = HmmerQueryRecord.objects.get(task_id=task_id)
        # if result is generated and not expired
        if r.result_date and (r.result_date.replace(tzinfo=None) >= (datetime.utcnow() + timedelta(days=-7))):
            file_prefix = path.join(settings.MEDIA_URL, 'hmmer', 'task', task_id, task_id + ".merge")

            os.chdir(path.join(settings.MEDIA_ROOT, 'hmmer', 'task', task_id))
            with open('status.json', 'r') as f:
                statusdata = json.load(f)
                db_list = statusdata['db_list']
                file_in = path.join(settings.MEDIA_URL, 'hmmer', 'task', task_id, statusdata['input'])

            out = []
            report = ["<br>"]

            with open(path.join(settings.MEDIA_ROOT, 'hmmer', 'task', task_id, task_id + ".merge"),
                      'r') as content_file:
                for line in content_file:
                    line = line.rstrip('\n')
                    if line == '[ok]':
                        out.append(''.join(report).replace(' ', '&nbsp;'))
                        report = ["<br>"]
                    else:
                        report.append(line + "<br>")

            if r.result_status in set(['SUCCESS', ]):
                return render(
                    request,
                    'hmmer/result.html', {
                        'title': 'HMMER Result',
                        'output': file_prefix,
                        'status': path.join(settings.MEDIA_URL, 'hmmer', 'task', task_id, 'status.json'),
                        'input': file_in,
                        'options': db_list,
                        'report': out,
                        'task_id': task_id,
                    })
            else:  # if .csv file size is 0, no hits found
                return render(request, 'hmmer/results_not_existed.html',
                              {
                                  'title': 'No Hits Found',
                                  'isNoHits': True,
                                  'isExpired': False,
                              })
        else:
            enqueue_date = r.enqueue_date.astimezone(timezone('US/Eastern')).strftime('%d %b %Y %X %Z')
            if r.dequeue_date:
                dequeue_date = r.dequeue_date.astimezone(timezone('US/Eastern')).strftime('%d %b %Y %X %Z')
            else:
                dequeue_date = None
            # result is exipired
            isExpired = False
            if r.result_date and (r.result_date.replace(tzinfo=None) < (datetime.utcnow() + timedelta(days=-7))):
                isExpired = True
            return render(request, 'hmmer/results_not_existed.html', {
                'title': 'Query Submitted',
                'task_id': task_id,
                'isExpired': isExpired,
                'enqueue_date': enqueue_date,
                'dequeue_date': dequeue_date,
                'isNoHits': False,
            })
    except:
        if settings.USE_PROD_SETTINGS:
            raise Http404
        else:
            return HttpResponse(traceback.format_exc())


def status(request, task_id):
    if request.method == 'GET':
        status_file_path = path.join(settings.MEDIA_ROOT, 'hmmer', 'task', task_id, 'status.json')
        status = {'status': 'unknown'}
        if path.isfile(status_file_path):
            with open(status_file_path, 'rb') as f:
                statusdata = json.load(f)
                if statusdata['status'] == 'pending' and settings.USE_CACHE:
                    tlist = cache.get('task_list_cache', [])
                    num_preceding = -1;
                    if tlist:
                        for index, tuple in enumerate(tlist):
                            if task_id in tuple:
                                num_preceding = index
                                break
                    statusdata['num_preceding'] = num_preceding
                elif statusdata['status'] == 'running':
                    asn_path = path.join(settings.MEDIA_ROOT, 'hmmer', 'task', task_id, (task_id + '.out'))
                    if path.isfile(asn_path):
                        with open(asn_path, 'r') as asn_f:
                            astr = asn_f.read()
                            processed_seq_count = astr.count('Scores for complete sequences')
                            statusdata['processed'] = processed_seq_count
                    else:
                        statusdata['processed'] = 0
                return HttpResponse(json.dumps(statusdata))
        return HttpResponse(json.dumps(status))
    else:
        return HttpResponse('Invalid Post')

# to-do: integrate with existing router of restframework
from rest_framework.renderers import JSONRenderer
from .serializers import UserHmmerQueryRecordSerializer


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def user_tasks(request, user_id):
    """
    Return tasks performed by the user.
    """
    if request.method == 'GET':
        records = HmmerQueryRecord.objects.filter(user__id=user_id)
        serializer = UserHmmerQueryRecordSerializer(records, many=True)
        print serializer.data
        return JSONResponse(serializer.data)
