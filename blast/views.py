from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.http import HttpResponse
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from uuid import uuid4
from os import path, makedirs, chmod
from zoneinfo import ZoneInfo
from .models import BlastQueryRecord, BlastDb
from .tasks import run_blast_task
from .utils import BLAST_PROGRAMS, blast_bin, escape_json_for_script, json_for_script
from datetime import timedelta
import json
import stat as Perm
from itertools import groupby

blast_customized_options = {'blastn':['max_target_seqs', 'evalue', 'word_size', 'reward', 'penalty', 'gapopen', 'gapextend', 'strand', 'low_complexity', 'soft_masking'],
                            'tblastn':['max_target_seqs', 'evalue', 'word_size', 'matrix', 'threshold', 'gapopen', 'gapextend', 'low_complexity', 'soft_masking'],
                            'tblastx':['max_target_seqs', 'evalue', 'word_size', 'matrix', 'threshold', 'strand', 'low_complexity', 'soft_masking'],
                            'blastp':['max_target_seqs', 'evalue', 'word_size', 'matrix', 'threshold', 'gapopen', 'gapextend', 'low_complexity', 'soft_masking'],
                            'blastx':['max_target_seqs', 'evalue', 'word_size', 'matrix', 'threshold', 'strand', 'gapopen', 'gapextend', 'low_complexity', 'soft_masking']}
# server side validation of the option values posted by the form
blast_option_types = {
    'max_target_seqs': int, 'evalue': float, 'word_size': int, 'reward': int, 'penalty': int,
    'gapopen': int, 'gapextend': int, 'threshold': float,
    'strand': ('both', 'plus', 'minus'),
    'matrix': ('BLOSUM45', 'BLOSUM50', 'BLOSUM62', 'BLOSUM80', 'BLOSUM90', 'PAM30', 'PAM70', 'PAM250'),
    'low_complexity': ('yes', 'no'),
    'soft_masking': ('true', 'false'),
}
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


def clean_blast_option(name, value):
    '''Return the option value as a string for the command line, or None if invalid.'''
    allowed = blast_option_types.get(name)
    if allowed is None or value is None:
        return None
    value = value.strip()
    if isinstance(allowed, tuple):
        return value if value in allowed else None
    try:
        allowed(value)
    except ValueError:
        return None
    return value


def invalid_query(request, message=None):
    return render(request, 'blast/invalid_query.html', {'title': 'Invalid Query', 'message': message}, status=400)


def create(request, iframe=False):
    if request.method == 'GET':
        # build dataset_list = [['Genome Assembly', 'Nucleotide', 'Agla_Btl03082013.genome_new_ids.fa', 'Anoplophora glabripennis'],]
        blastdb_list = sorted([[db.type.dataset_type, db.type.get_molecule_type_display(), db.title, db.organism.display_name, db.description] for db in BlastDb.objects.select_related('organism').select_related('type').filter(is_shown=True) if db.db_ready()], key=lambda x: (x[3], x[1], x[0], x[2]))
        blastdb_type_counts = dict([(k.lower().replace(' ', '_'), len(list(g))) for k, g in groupby(sorted(blastdb_list, key=lambda x: x[0]), key=lambda x: x[0])])
        return render(request, 'blast/main.html', {
            'title': 'BLAST Query',
            'blastdb_list': json_for_script(blastdb_list),
            'blastdb_type_counts': blastdb_type_counts,
            'iframe': iframe
        })
    elif request.method == 'POST':
        # check if program is in list for security
        program = request.POST.get('program')
        if program not in BLAST_PROGRAMS:
            raise Http404

        # build blast command
        dbs = [db for db in BlastDb.objects.select_related('type').filter(title__in=set(request.POST.getlist('db-name'))) if db.db_ready()]
        db_list = ' '.join([db.fasta_file.path_full for db in dbs])
        if not db_list:
            return invalid_query(request)

        # generate customized_options
        input_opt = []
        max_target_seqs = clean_blast_option('max_target_seqs', request.POST.get('max_target_seqs'))
        for blast_option in blast_customized_options[program]:
            value = clean_blast_option(blast_option, request.POST.get(blast_option))
            if value is None:
                return invalid_query(request, 'Invalid value for the BLAST option "%s".' % blast_option)
            if blast_option == 'low_complexity':
                if program == 'blastn':
                    input_opt.append('-dust')
                else:
                    input_opt.append('-seg')
            else:
                input_opt.append('-'+blast_option)
            input_opt.append(value)

        # read the query
        if 'query-file' in request.FILES:
            query_chunks = request.FILES['query-file'].chunks()
        elif request.POST.get('query-sequence'):
            query_chunks = [request.POST['query-sequence'].encode('utf-8')]
        else:
            return invalid_query(request)

        # setup file paths
        task_id = uuid4().hex # TODO: Create from hash of input to check for duplicate inputs
        file_prefix = path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id, task_id)
        query_filename = file_prefix + '.in'
        asn_filename = file_prefix + '.asn'
        if not path.exists(path.dirname(query_filename)):
            makedirs(path.dirname(query_filename))
        chmod(path.dirname(query_filename), Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can open files in the directory

        # write query to file, counting the number of query sequences by counting '>'
        seq_count = 0
        with open(query_filename, 'wb') as query_f:
            for chunk in query_chunks:
                query_f.write(chunk)
                seq_count += chunk.count(b'>')

        chmod(query_filename, Perm.S_IRWXU | Perm.S_IRWXG | Perm.S_IRWXO) # ensure the standalone dequeuing process can access the file

        program_path = blast_bin(program)
        args_list = [[program_path, '-query', query_filename, '-db', db_list, '-outfmt', '11', '-out', asn_filename, '-num_threads', str(settings.BLAST_NUM_THREADS)]]
        args_list[0].extend(input_opt)

        # convert to multiple formats
        blast_formatter_path = blast_bin('blast_formatter')
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
        if request.user.is_authenticated:
            record.user = request.user
        record.save()

        # generate status.json for frontend statu checking
        if (seq_count == 0):
            seq_count = 1
        with open(path.join(path.dirname(file_prefix), 'status.json'), 'w') as f:
            json.dump({'status': 'pending', 'seq_count': seq_count}, f)

        # the titles of the searched databases disambiguate subject ids (#19)
        task_blast_info = dict(blast_info, db_titles=[db.title for db in dbs])
        run_blast_task.delay(task_id, args_list, file_prefix, task_blast_info)

        return redirect('blast:retrieve', task_id)
    else:
        return HttpResponse(status=405)

def retrieve(request, task_id='1'):
    r = get_object_or_404(BlastQueryRecord, task_id=task_id)
    expire_date = timezone.now() - timedelta(days=settings.BLAST_RESULT_RETENTION_DAYS)
    # if result is generated and not expired
    if r.result_date and (r.result_date >= expire_date):
        if r.result_status in set(['SUCCESS', 'NO_GFF']):
            file_prefix = path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id, task_id)
            results_info = ''
            with open(path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id, 'info.json'), 'r') as f:
                results_info = f.read()
            results_data = ''
            with open(file_prefix + '.json', 'r') as f:
                results_data = f.read()
            results_detail = ''
            with open(file_prefix + '.0', 'r', encoding='utf-8', errors='replace') as f:
                results_detail = f.read()
            results_col_names = blast_info['col_names']
            results_col_names_display = blast_col_names_display
            results_col_names = ['blastdb'] + results_col_names
            results_col_names_display = ['BLAST Database Title'] + results_col_names_display
            return render(
                request,
                'blast/results.html', {
                    'title': 'BLAST Result',
                    'results_col_names': json_for_script(results_col_names),
                    'results_col_names_display': json_for_script(results_col_names_display),
                    'results_detail': json_for_script(results_detail),
                    'results_data': escape_json_for_script(results_data),
                    'results_info': escape_json_for_script(results_info),
                    'task_id': task_id,
                    # result files, including the GFF3 files JBrowse loads
                    'media_url': json_for_script(settings.MEDIA_URL),
                })
        else: # if .csv file size is 0, no hits found
            return render(request, 'blast/results_not_existed.html',
            {
                'title': 'No Hits Found',
                'isNoHits': True,
                'isExpired': False,
            })
    else:
        eastern = ZoneInfo('US/Eastern')
        enqueue_date = r.enqueue_date.astimezone(eastern).strftime('%d %b %Y %X %Z')
        if r.dequeue_date:
            dequeue_date = r.dequeue_date.astimezone(eastern).strftime('%d %b %Y %X %Z')
        else:
            dequeue_date = None
        # result is exipired
        isExpired = False
        if r.result_date and (r.result_date < expire_date):
            isExpired = True
        return render(request, 'blast/results_not_existed.html', {
            'title': 'Query Submitted',
            'task_id': task_id,
            'isExpired': isExpired,
            'enqueue_date': enqueue_date,
            'dequeue_date': dequeue_date,
            'isNoHits': False,
        })

def read_gff3(request, task_id, dbname):
    output = '##gff-version 3\n'
    try:
        if request.method == 'GET':
            with open(path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id, dbname) + '.gff', 'r') as f:
                output = f.read()
    finally:
        return HttpResponse(output)

def status(request, task_id):
    if request.method == 'GET':
        status_file_path = path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id, 'status.json')
        status = {'status': 'unknown'}
        if path.isfile(status_file_path):
            with open(status_file_path, 'r') as f:
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
                    asn_path = path.join(settings.MEDIA_ROOT, 'blast', 'task', task_id, (task_id+'.asn'))
                    if path.isfile(asn_path):
                        with open(asn_path, 'r', errors='replace') as asn_f:
                            astr = asn_f.read()
                            processed_seq_count = astr.count('title \"')
                            statusdata['processed'] = processed_seq_count
                    else:
                        statusdata['processed'] = 0
                return HttpResponse(json.dumps(statusdata), content_type='application/json')
        return HttpResponse(json.dumps(status), content_type='application/json')
    else:
        return HttpResponse('Invalid Post')


# to-do: integrate with existing router of restframework
from rest_framework.renderers import JSONRenderer
from .serializers import UserBlastQueryRecordSerializer
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
    Return tasks performed by the user. Only the user and staff may list them.
    """
    if request.method == 'GET':
        if not request.user.is_authenticated or (request.user.id != int(user_id) and not request.user.is_staff):
            return JSONResponse({'detail': 'You do not have permission to perform this action.'}, status=403)
        records = BlastQueryRecord.objects.filter(user__id=user_id, is_shown=True)
        serializer = UserBlastQueryRecordSerializer(records, many=True)
        return JSONResponse(serializer.data)
