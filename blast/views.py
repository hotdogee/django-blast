# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from uuid import uuid4
from os import path
from django.conf import settings
from sys import platform
import subprocess
import json
import csv

blast_out_ext = {}
blast_out_ext['.0'] = '0'
blast_out_ext['.1'] = '1'
blast_out_ext['.3'] = '3'
blast_out_ext['.xml'] = '5'
blast_out_ext['.tsv'] = '6 qseqid sseqid evalue qlen slen length nident mismatch positive gapopen gaps qstart qend sstart send bitscore qcovs'
blast_out_ext['.csv'] = '10 qseqid sseqid evalue qlen slen length nident mismatch positive gapopen gaps qstart qend sstart send bitscore qcovs'
col_types = [str, str, float, int, int, int, int, int, int, int, int, int, int, int, int, float, int]

def create(request):
    #return HttpResponse("BLAST Page: create.")
    if request.method == 'GET':
        return render(
            request,
            'blast/main.html',
        )
    elif request.method == 'POST':
        # setup file paths
        file_prefix = path.join(settings.MEDIA_ROOT, uuid4().hex)
        query_filename = file_prefix + '.in'
        asn_filename = file_prefix + '.asn'
        bin_name = 'bin_linux'
        if platform == 'win32':
            #query_filename = query_filename.replace('/','\\')
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
            result = subprocess.check_output(args)
            # convert to multiple formats
            blast_formatter_path = path.join(settings.PROJECT_ROOT, 'blast', bin_name, 'blast_formatter')
            for ext, outfmt in blast_out_ext.items():
                args = [blast_formatter_path, '-archive', asn_filename, '-outfmt', outfmt, '-out', file_prefix + ext]
                subprocess.check_output(args)
            # parse csv
            result = []
            with open(file_prefix + '.csv', 'r') as f:
                cr = csv.reader(f)
                for row in cr:
                    result.append(tuple(convert(value) for convert, value in zip(col_types, row)))
        # return result
        #return HttpResponse(result)
        return render(
            request,
            'blast/results.html',
            RequestContext(request,
            {
                'results': json.dumps(result),
            })
        )

def retrieve(request, task_id='1'):
    #return HttpResponse("BLAST Page: retrieve = %s." % (task_id))
    return render(
        request,
        'blast/results.html',
        RequestContext(request,
        {
            'results': '[["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold1", 0.0, 1920, 10144477, 1920, 1920, 0, 1920, 0, 0, 1, 1920, 1, 1920, 3546.0, 100], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold23", 1e-25, 1920, 6368063, 128, 108, 18, 108, 2, 2, 1345, 1471, 6209895, 6209769, 124.0, 7], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold77", 3e-21, 1920, 1510826, 92, 81, 11, 81, 0, 0, 1341, 1432, 28092, 28183, 110.0, 5], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold266", 4e-20, 1920, 886450, 90, 79, 11, 79, 0, 0, 1353, 1442, 438805, 438716, 106.0, 5], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold61", 1e-16, 1920, 1954611, 70, 64, 5, 64, 1, 1, 1355, 1424, 488306, 488238, 95.3, 4], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold22", 1e-10, 1920, 5701487, 104, 83, 19, 83, 2, 2, 1340, 1442, 896312, 896210, 75.0, 5], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold16", 2e-09, 1920, 4306126, 53, 48, 5, 48, 0, 0, 1378, 1430, 1773730, 1773782, 71.3, 3], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold514", 6e-09, 1920, 134318, 59, 52, 6, 52, 1, 1, 1341, 1399, 19297, 19354, 69.4, 3], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold11", 4e-06, 1920, 8115852, 35, 34, 1, 34, 0, 0, 1342, 1376, 6190570, 6190536, 60.2, 2], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold39", 5e-05, 1920, 5665586, 43, 39, 3, 39, 1, 1, 465, 506, 5052910, 5052952, 56.5, 2], ["Contig1", "gnl|Ceratitis_capitata|cercap_Scaffold53", 0.0006, 1920, 1436579, 28, 28, 0, 28, 0, 0, 1304, 1331, 1372856, 1372883, 52.8, 1], ["Contig2", "gnl|Anoplophora_glabripennis|anogla_Scaffold1", 0.0, 1729, 5510682, 1225, 1225, 0, 1225, 0, 0, 505, 1729, 135519, 134295, 2263.0, 100], ["Contig2", "gnl|Anoplophora_glabripennis|anogla_Scaffold1", 0.0, 1729, 5510682, 479, 479, 0, 479, 0, 0, 29, 507, 140638, 140160, 885.0, 100], ["Contig2", "gnl|Anoplophora_glabripennis|anogla_Scaffold1", 1e-05, 1729, 5510682, 31, 31, 0, 31, 0, 0, 1, 31, 147296, 147266, 58.4, 100]]',
        })
    )