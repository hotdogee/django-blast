from __future__ import absolute_import
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache
from uuid import uuid4
from os import path, makedirs, chmod
from .tasks import run_clustal_task
from datetime import datetime, timedelta
from pytz import timezone
from os.path import basename
import json
import traceback
import stat as Perm
from clustal.models import ClustalQueryRecord
import os

def create(request, iframe=False):
    #return HttpResponse("BLAST Page: create.")
    if request.method == 'GET':
        return render(request, 'clustal/main.html', {
            'title': 'Clustal Query',
            'iframe': iframe
        })
    elif request.method == 'POST':
        # setup file paths
        task_id = uuid4().hex
        task_dir = path.join(settings.MEDIA_ROOT, 'clustal', 'task', task_id)
        # file_prefix only for task...
        file_prefix = path.join(settings.MEDIA_ROOT, 'clustal', 'task', task_id, task_id)
        if not path.exists(task_dir):
            makedirs(task_dir)
        chmod(task_dir, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can open files in the directory
        # change directory to task directory
        os.chdir(task_dir)

        query_filename = ''
        if 'query-file' in request.FILES:
            query_filename = request.FILES['query-file'].name
            with open(query_filename, 'wb') as query_f:
                for chunk in request.FILES['query-file'].chunks():
                    query_f.write(chunk)
        elif 'query-sequence' in request.POST and request.POST['query-sequence']:
            query_filename = task_id + 'in'
            with open(query_filename, 'wb') as query_f:
                query_f.write(request.POST['query-sequence'])
        else:
            return render(request, 'clustal/invalid_query.html', {'title': 'Invalid Query',})

        chmod(query_filename, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can access the file

        # check if program is in list for security
        if request.POST['program'] in ['clustalw','clustalo']:

            option_params = []
            args_list = []

            if request.POST['program'] == 'clustalw':
                option_params.append("-type="+request.POST['sequenceType'])

                #parameters setting for full option or fast option
                if request.POST['pairwise'] == "full":
                    option_params.append('-ALIGN')
                    if request.POST['sequenceType'] == "dna":
                        if request.POST['PWDNAMATRIX'] != "":
                            option_params.append('-PWDNAMATRIX='+request.POST['PWDNAMATRIX'])
                        if request.POST['dna-PWGAPOPEN'] != "":
                            option_params.append('-PWGAPOPEN='+request.POST['dna-PWGAPOPEN'])
                        if request.POST['dna-PWGAPEXT'] != "":
                            option_params.append('-PWGAPEXT='+request.POST['dna-PWGAPEXT'])
                    elif request.POST['sequenceType'] == "protein":
                        if request.POST['PWMATRIX'] != "":
                            option_params.append('-PWMATRIX='+request.POST['PWMATRIX'])
                        if request.POST['protein-PWGAPOPEN'] != "":
                            option_params.append('-PWGAPOPEN='+request.POST['protein-PWGAPOPEN'])
                        if request.POST['protein-PWGAPOPEN'] != "":
                            option_params.append('-PWGAPEXT='+request.POST['protein-PWGAPEXT'])
                elif request.POST['pairwise'] == "fast":
                    option_params.append('-QUICKTREE')
                    if request.POST['KTUPLE'] != "":
                        option_params.append('-KTUPLE='+request.POST['KTUPLE'])
                    if request.POST['WINDOW'] != "":
                        option_params.append('-WINDOW='+request.POST['WINDOW'])
                    if request.POST['PAIRGAP'] != "":
                        option_params.append('-PAIRGAP='+request.POST['PAIRGAP'])
                    if request.POST['TOPDIAGS'] != "":
                        option_params.append('-TOPDIAGS='+request.POST['TOPDIAGS'])
                    if request.POST['SCORE'] != "":
                        option_params.append('-SCORE='+request.POST['SCORE'])

                #prarmeters setting for mutliple alignment
                if request.POST['sequenceType'] == "dna":
                    if request.POST['DNAMATRIX'] != "":
                        option_params.append('-DNAMATRIX='+request.POST['DNAMATRIX'])
                    if request.POST['dna-GAPOPEN'] != "":
                        option_params.append('-GAPOPEN='+request.POST['dna-GAPOPEN'])
                    if request.POST['dna-GAPEXT'] != "":
                        option_params.append('-GAPEXT='+request.POST['dna-GAPEXT'])
                    if request.POST['dna-GAPDIST'] != "":
                        option_params.append('-GAPDIST='+request.POST['dna-GAPDIST'])
                    if request.POST['dna-ITERATION'] != "":
                        option_params.append('-ITERATION='+request.POST['dna-ITERATION'])
                    if request.POST['dna-NUMITER'] != "":
                        option_params.append('-NUMITER='+request.POST['dna-NUMITER'])
                    if request.POST['dna-CLUSTERING'] != "":
                        option_params.append('-CLUSTERING='+request.POST['dna-CLUSTERING'])
                elif request.POST['sequenceType'] == "protein":
                    if request.POST['MATRIX'] != "":
                        option_params.append('-MATRIX='+request.POST['MATRIX'])
                    if request.POST['protein-GAPOPEN'] != "":
                        option_params.append('-GAPOPEN='+request.POST['protein-GAPOPEN'])
                    if request.POST['protein-GAPEXT'] != "":
                        option_params.append('-GAPEXT='+request.POST['protein-GAPEXT'])
                    if request.POST['protein-GAPDIST'] != "":
                        option_params.append('-GAPDIST='+request.POST['protein-GAPDIST'])
                    if request.POST['protein-ITERATION'] != "":
                        option_params.append('-ITERATION='+request.POST['protein-ITERATION'])
                    if request.POST['protein-NUMITER'] != "":
                        option_params.append('-NUMITER='+request.POST['protein-NUMITER'])
                    if request.POST['protein-CLUSTERING'] != "":
                        option_params.append('-CLUSTERING='+request.POST['protein-CLUSTERING'])

                #parameters setting of  Output
                option_params.append('-OUTPUT='+request.POST['OUTPUT'])
                option_params.append('-OUTORDER='+request.POST['OUTORDER'])

                args_list.append(['clustalw2', '-TREE', '-infile='+query_filename, '-OUTFILE='+task_id+'.aln'] + option_params)
            else:
                #clustalo
                if request.POST['dealing_input'] == "yes":
                    option_params.append("--dealign")
                if request.POST['clustering_guide_tree'] != "no":
                    option_params.append("--full")
                if request.POST['clustering_guide_iter'] != "no":
                    option_params.append("--full-iter")

                if request.POST['combined_iter'] != "":
                    option_params.append("--iterations="+request.POST['combined_iter'])
                if request.POST['max_gt_iter'] != "":
                    option_params.append("--max-guidetree-iterations="+request.POST['max_gt_iter'])
                if request.POST['max_hmm_iter'] != "":
                    option_params.append("--max-hmm-iterations="+request.POST['max_hmm_iter'])
                if request.POST['omega_output'] != "":
                    option_params.append("--outfmt="+request.POST['omega_output'])
                if request.POST['omega_order'] != "":
                    option_params.append("--output-order="+request.POST['omega_order'])

                args_list.append(['clustalo', '--infile='+query_filename,'--guidetree-out='+task_id+'.ph','--outfile='+task_id+'.aln'] + option_params)

            record = ClustalQueryRecord()
            record.task_id = task_id
            if request.user.is_authenticated():
                record.user = request.user
            record.save()

            # generate status.json for frontend statu checking
            with open(query_filename, 'r') as f: # count number of query sequence by counting '>'
                qstr = f.read()
                seq_count = qstr.count('>')
                if (seq_count == 0):
                    seq_count = 1
                with open('status.json', 'wb') as f:
                    json.dump({'status': 'pending', 'seq_count': seq_count, 'cmd': " ".join(args_list[0]), 'query_filename': query_filename}, f)


            #args_list.append(['clustalw2', '-infile='+query_filename,'-OUTFILE='+task_id+'.aln'] + option_params)
            run_clustal_task.delay(task_id, args_list, file_prefix)

            return redirect('clustal:retrieve', task_id)
        else:
            raise Http404

def retrieve(request, task_id='1'):
    #return HttpResponse("BLAST Page: retrieve = %s." % (task_id))
    try:
        r = ClustalQueryRecord.objects.get(task_id=task_id)
        # if result is generated and not expired
        if r.result_date and (r.result_date.replace(tzinfo=None) >= (datetime.utcnow()+ timedelta(days=-7))):
            file_prefix = path.join(settings.MEDIA_URL, 'clustal', 'task', task_id, task_id)


            os.chdir(path.join(settings.MEDIA_ROOT, 'clustal', 'task', task_id))
            with open('status.json', 'r') as f:
                statusdata = json.load(f)

            out = []
            report = ["<br>"]

            with open(path.join(settings.MEDIA_ROOT, 'clustal', 'task', task_id, task_id+".aln"), 'r') as content_file:
                for line in content_file:
                    line = line.rstrip('\n')
                    report.append(line+"<br>")

            out.append(''.join(report).replace(' ','&nbsp;'))

            dnd_filename = path.join(settings.MEDIA_ROOT, 'clustal', 'task', task_id, os.path.splitext(statusdata['query_filename'])[0]+'.dnd')
            if path.isfile(dnd_filename):
                return_dnd = path.join(settings.MEDIA_URL, 'clustal', 'task', task_id, os.path.splitext(statusdata['query_filename'])[0]+'.dnd')
            else:
                return_dnd = None

            ph_filename = path.join(settings.MEDIA_ROOT, 'clustal', 'task', task_id, task_id+'.ph')
            if path.isfile(ph_filename):
                return_ph = file_prefix + '.ph'
            else:
                return_ph = None

            if r.result_status in set(['SUCCESS']):
                return render(
                    request,
                    'clustal/result.html', {
                        'title': 'CLUSTAL Result',
                        'aln': file_prefix+'.aln',
                        'ph': return_ph,
                        'dnd': return_dnd,
                        'status': path.join(settings.MEDIA_URL, 'clustal', 'task', task_id, 'status.json'),
                        'colorful': True if("=clu" in statusdata['cmd']) else False,
                        'report': out,
                        'task_id': task_id,
                    })
            else: # if .csv file size is 0, no hits found
                return render(request, 'clustal/results_not_existed.html',
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
            if r.result_date and (r.result_date.replace(tzinfo=None) < (datetime.utcnow()+ timedelta(days=-7))):
                isExpired = True
            return render(request, 'clustal/results_not_existed.html', {
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
        status_file_path = path.join(settings.MEDIA_ROOT, 'clustal', 'task', task_id, 'status.json')
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
                    asn_path = path.join(settings.MEDIA_ROOT, 'hmmer', 'task', task_id, (task_id+'.out'))
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
from .serializers import UserClustalQueryRecordSerializer
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
        records = ClustalQueryRecord.objects.filter(user__id=user_id)
        serializer = UserClustalQueryRecordSerializer(records, many=True)
        return JSONResponse(serializer.data)



