# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse
from django.template import RequestContext
from uuid import uuid4
from os import path
from django.conf import settings
from sys import platform
import subprocess
import json
import csv

blast_out_col_types = [str, str, float, int, int, int, int, int, int, int, int, int, int, int, int, float, int, int, int]
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

def create(request):
    #return HttpResponse("BLAST Page: create.")
    if request.method == 'GET':
        return render(
            request,
            'blast/main.html',
        )
    elif request.method == 'POST':
        # setup file paths
        task_id = uuid4().hex
        file_prefix = path.join(settings.MEDIA_ROOT, task_id)
        query_filename = file_prefix + '.in'
        asn_filename = file_prefix + '.asn'
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
        # build blast command
        db_list = ' '.join(request.POST.getlist('db-name'))
        # check if program is in list for security
        if request.POST['program'] in ['blastn', 'tblastn', 'tblastx', 'blastp', 'blastx']:
            program_path = path.join(settings.PROJECT_ROOT, 'blast', bin_name, request.POST['program'])
            #args = [program_path, '-query', query_filename, '-db', db_list, '-html']
            args = [program_path, '-query', query_filename, '-db', db_list, '-outfmt', '11', '-out', asn_filename, '-num_threads', '6']
            # run blast process
            subprocess.Popen(args).wait()
            # convert to multiple formats
            blast_formatter_path = path.join(settings.PROJECT_ROOT, 'blast', bin_name, 'blast_formatter')
            for ext, outfmt in blast_out_ext.items():
                args = [blast_formatter_path, '-archive', asn_filename, '-outfmt', outfmt, '-out', file_prefix + ext]
                if ext == '.html':
                    args.append('-html')
                subprocess.Popen(args).wait()
            return redirect('blast:retrieve', task_id)
        else:
            raise Http404

def retrieve(request, task_id='1'):
    #return HttpResponse("BLAST Page: retrieve = %s." % (task_id))
    try:
        # parse csv
        file_prefix = path.join(settings.MEDIA_ROOT, task_id)
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
            })
        )
    except:
        raise Http404