"""Smoke test for a running instance (e.g. `docker compose up`) with the sample data.

    python docker/smoke_test.py [http://localhost:8000]

Submits a BLAST job through the web form, waits for the Celery worker to
finish it and checks the results page and the REST API. Standard library only.
"""
import http.cookiejar
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000').rstrip('/')
# AGLA000012-RA from the sample transcripts: blastx against the sample proteins
SAMPLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'example', 'blastdb', 'AGLA_sample_transcripts.fna')
HIT = 'gnl|Anoplophora_glabripennis_protein_v0.5.3|AGLA000012-PA'


def read_query(name):
    records, current = {}, None
    with open(SAMPLE) as f:
        for line in f:
            line = line.strip()
            if line.startswith('>'):
                current = line[1:].split()[0]
                records[current] = []
            elif current:
                records[current].append(line)
    return '>%s\n%s\n' % (name, ''.join(records[name]))


OPTIONS = {
    'program': 'blastx', 'max_target_seqs': '10', 'evalue': '1e-5', 'word_size': '3', 'matrix': 'BLOSUM62', 'threshold': '12',
    'strand': 'both', 'gapopen': '11', 'gapextend': '1', 'low_complexity': 'yes', 'soft_masking': 'false',
}

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def get(path):
    with opener.open(BASE + path, timeout=30) as response:
        return response.read().decode('utf-8', 'replace')


def main():
    page = get('/blast/')
    assert 'AGLA_new_ids.faa' in page, 'the sample databases are not listed on /blast/'
    token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page).group(1)
    data = dict(OPTIONS, **{'csrfmiddlewaretoken': token, 'query-sequence': read_query('AGLA000012-RA'), 'db-name': 'AGLA_new_ids.faa'})
    request = urllib.request.Request(BASE + '/blast/', data=urllib.parse.urlencode(data).encode(), headers={'Referer': BASE + '/blast/'})
    with opener.open(request, timeout=30) as response:
        location = response.geturl()
    task_id = re.search(r'/blast/([0-9a-f]{32})$', location).group(1)
    print('submitted task', task_id)
    for _ in range(120):
        status = json.loads(get('/blast/%s/status' % task_id))['status']
        if status == 'done':
            break
        time.sleep(2)
    else:
        raise SystemExit('the job did not finish, status: %s' % status)
    results = get('/blast/' + task_id)
    assert 'Query Coverage Graph' in results, 'no results page'
    assert 'AGLA000012-PA' in results, 'the expected hit is missing'
    task = json.loads(get('/blast/api/task/%s/' % task_id))
    assert task['result_status'] == 'SUCCESS', task
    fasta = get('/blast/api/seq/%s/?format=fasta&blast_db=AGLA_new_ids.faa' % urllib.parse.quote(HIT, safe=''))
    assert fasta.startswith('>' + HIT), fasta[:100]
    print('ok: results page, task API and sequence API work')


if __name__ == '__main__':
    main()
