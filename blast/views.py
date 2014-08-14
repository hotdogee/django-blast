from __future__ import absolute_import
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.template import RequestContext
from django.conf import settings
from uuid import uuid4
from os import path, makedirs, chmod, stat
from django.conf import settings
from sys import platform
from .models import BlastQueryRecord, BlastDb, Sequence, JbrowseSetting
from .tasks import run_blast_task
from datetime import datetime, timedelta
from pytz import timezone
import subprocess
import json
import csv
import traceback
import stat as Perm
from copy import deepcopy
from itertools import groupby

blast_customized_options = {'blastn':['max_target_seqs', 'evalue', 'word_size', 'reward', 'penalty', 'gapopen', 'gapextend', 'strand', 'low_complexity', 'soft_masking'],
                            'tblastn':['max_target_seqs', 'evalue', 'word_size', 'matrix', 'threshold', 'gapopen', 'gapextend', 'low_complexity', 'soft_masking'],
                            'tblastx':['max_target_seqs', 'evalue', 'word_size', 'matrix', 'threshold', 'strand'],
                            'blastp':['max_target_seqs', 'evalue', 'word_size', 'matrix', 'threshold', 'gapopen', 'gapextend'],
                            'blastx':['max_target_seqs', 'evalue', 'word_size', 'matrix', 'threshold', 'strand', 'gapopen', 'gapextend']}
#blast_col_name = 'qseqid sseqid evalue qlen slen length nident mismatch positive gapopen gaps qstart qend sstart send bitscore qcovs qframe sframe'
blast_col_name = 'qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore nident qcovs qlen slen qframe sframe'
blast_col_names_display = 'Query sequence ID,Subject sequence ID,Percentage of identical matches,Alignment length,Number of mismatches,Number of gap openings,Start of alignment in query,End of alignment in query,Start of alignment in subject,End of alignment in subject,Expect value,Bit score,Number of identical matches,Query coverage per subject,Query sequence length,Subject sequence length,Query frame,Subject frame'.split(',')
blast_info = {
    'col_types': ['str', 'str', 'float', 'int', 'int', 'int', 'int', 'int', 'int', 'int', 'float', 'float', 'int', 'int', 'int', 'int', 'int', 'int'],
    'col_names': blast_col_name.split(),
    'ext': {
        '.0': '0',
        '.html': '0',
        '.1': '1',
        '.3': '3',
        '.xml': '5',
        '.tsv': '6 ' + blast_col_name,
        '.csv': '10 ' + blast_col_name,
    },
}

def create(request):
    #return HttpResponse("BLAST Page: create.")
    if request.method == 'GET':
        # build dataset_list = [['Genome Assembly', 'Nucleotide', 'Agla_Btl03082013.genome_new_ids.fa', 'Anoplophora glabripennis'],]
        blastdb_list = [[db.type.dataset_type, db.type.get_molecule_type_display(), db.title, db.organism.display_name, db.description] for db in BlastDb.objects.select_related('organism').select_related('sequencetype').filter(is_shown=True) if db.db_ready()]
        blastdb_type_counts = dict([(k.lower().replace(' ', '_'), len(list(g))) for k, g in groupby(sorted(blastdb_list, key=lambda x: x[0]), key=lambda x: x[0])])
        return render(request, 'blast/main.html', {
            'title': 'BLAST Query', 
            'blastdb_list': json.dumps(blastdb_list), 
            'blastdb_type_counts': blastdb_type_counts,
        })
    elif request.method == 'POST':
        # setup file paths
        task_id = uuid4().hex # TODO: Create from hash of input to check for duplicate inputs
        file_prefix = path.join(settings.MEDIA_ROOT, task_id, task_id)
        query_filename = file_prefix + '.in'
        asn_filename = file_prefix + '.asn'
        if not path.exists(path.dirname(query_filename)):
            makedirs(path.dirname(query_filename))
        chmod(path.dirname(query_filename), Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can open files in the directory
        bin_name = 'bin_linux'
        if platform == 'win32':
            bin_name = 'bin_win'

        # write query to file
        if 'query-file' in request.FILES:
            with open(query_filename, 'wb') as query_f:
                for chunk in request.FILES['query-file'].chunks():
                    query_f.write(chunk)
        elif 'query-sequence' in request.POST and request.POST['query-sequence']:
            with open(query_filename, 'wb') as query_f:
                query_f.write(request.POST['query-sequence'])
        else:
            return render(request, 'blast/invalid_query.html', {'title': 'Invalid Query',})

        chmod(query_filename, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can access the file

        # build blast command
        db_list = ' '.join([db.fasta_file.path_full for db in BlastDb.objects.filter(title__in=set(request.POST.getlist('db-name'))) if db.db_ready()])
        if not db_list:
            return render(request, 'blast/invalid_query.html', {'title': 'Invalid Query',})
        
        # check if program is in list for security
        if request.POST['program'] in ['blastn', 'tblastn', 'tblastx', 'blastp', 'blastx']:

            # generate customized_options
            input_opt = []
            max_target_seqs = request.POST['max_target_seqs']
            for blast_option in blast_customized_options[request.POST['program']]:
                if blast_option == 'low_complexity':
                    if request.POST['program'] == 'blastn':
                        input_opt.append('-dust')
                    else:
                        input_opt.append('-seg')
                else:
                    input_opt.append('-'+blast_option)
                input_opt.append(request.POST[blast_option])

            
            program_path = path.join(settings.PROJECT_ROOT, 'blast', bin_name, request.POST['program'])
            args_list = [[program_path, '-query', query_filename, '-db', db_list, '-outfmt', '11', '-out', asn_filename, '-num_threads', '6']]
            args_list[0].extend(input_opt)

            # convert to multiple formats
            blast_formatter_path = path.join(settings.PROJECT_ROOT, 'blast', bin_name, 'blast_formatter')
            for ext, outfmt in blast_info['ext'].items():
                args = [blast_formatter_path, '-archive', asn_filename, '-outfmt', outfmt, '-out', file_prefix + ext]
                if ext == '.html':
                    args.append('-html')
                if int(outfmt.split()[0]) > 4:
                    args.append('-max_target_seqs')
                    args.append(max_target_seqs)
                else:
                    args.append('-num_descriptions')
                    args.append(max_target_seqs)
                    args.append('-num_alignments')
                    args.append(max_target_seqs)
                args_list.append(args)

            record = BlastQueryRecord()
            record.task_id = task_id
            record.save()

            run_blast_task.delay(task_id, args_list, file_prefix, blast_info)
            # debug
            #run_blast_task.delay(task_id, args_list, file_prefix, blast_info).get()
            return redirect('blast:retrieve', task_id)
        else:
            raise Http404

def retrieve(request, task_id='1'):
    #return HttpResponse("BLAST Page: retrieve = %s." % (task_id))
    try:
        r = BlastQueryRecord.objects.get(task_id=task_id)
        # if result is generated and not expired
        if r.result_date and (r.result_date.replace(tzinfo=None) >= (datetime.utcnow()+ timedelta(days=-7))):
            if r.result_status in set(['SUCCESS', 'NO_GFF']):
                file_prefix = path.join(settings.MEDIA_ROOT, task_id, task_id)
                results_info = ''
                with open(path.join(settings.MEDIA_ROOT, task_id, 'info.json'), 'rb') as f:
                    results_info = f.read()
                results_data = ''
                with open(file_prefix + '.json', 'rb') as f:
                    results_data = f.read()
                results_detail = ''
                with open(file_prefix + '.0', 'rb') as f:
                    results_detail = f.read()
                results_col_names = blast_info['col_names']
                results_col_names_display = blast_col_names_display
                if r.result_status == 'SUCCESS':
                    results_col_names = ['jbrowse'] + results_col_names
                    results_col_names_display = ['View result in genome browser'] + results_col_names_display
                return render(
                    request,
                    'blast/results.html', {
                        'title': 'BLAST Result',
                        'results_col_names': json.dumps(results_col_names),
                        'results_col_names_display': json.dumps(results_col_names_display),
                        'results_data': results_data,
                        'results_detail': results_detail,
                        'results_info': results_info,
                        'task_id': task_id,
                    })
            else: # if .csv file size is 0, no hits found
                return render(request, 'blast/results_not_existed.html', 
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
            return render(request, 'blast/results_not_existed.html', {
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
        
def read_gff3(request, task_id, dbname):
    output = '##gff-version 3\n'
    try:
        if request.method == 'GET':
            with open(path.join(settings.MEDIA_ROOT, task_id, dbname) + '.gff', 'rb') as f:
                output = f.read()
    finally:
        return HttpResponse(output)
