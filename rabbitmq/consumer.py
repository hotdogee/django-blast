#!/usr/bin/env python

import pika
import time
import urllib2
import os
import sys
import logging
import threading
import datetime
import sqlite3
import json
import subprocess

dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=(dir + '/consumer.log'), format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

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

class MyThread(threading.Thread):

    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID

    def run(self):
        logging.info('[Thread id %s] Consumer is started.', str(self.threadID))        
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='blast_query', durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, queue='blast_query')
        channel.start_consuming()   # the thread will keep consuming and not terminated

def callback(ch, method, properties, body):

    """
    example message:
        task_id=3ee04cec89b54d33ba557335b7b7134darg=["/usr/local/i5k/blast/bin_linux/blastn", "-query", "/usr/local/i5k/media/3ee04cec89b54d33ba557335b7b7134d/3ee04cec89b54d33ba557335b7b7134d.in", "-db", "Agla_Btl03082013.genome_new_ids.fa Ccap01172013-genome_new_ids.fa", "-outfmt", "11", "-out", "/usr/local/i5k/media/3ee04cec89b54d33ba557335b7b7134d/3ee04cec89b54d33ba557335b7b7134d.asn", "-num_threads", "6"]fmt=/usr/local/i5k/blast/bin_linux/blast_formatter
    """

    task_id = body[(body.find("task_id=")+8):(body.find("arg="))]
    task_arg = body[(body.find("arg=")+4):(body.find("fmt="))]
    blast_formatter_path = body[(body.find("fmt=")+4):]

    # update dequeue time
    con = sqlite3.connect('../db.sqlite3')
    with con:
        cur = con.cursor()
        cur.execute('UPDATE blast_blastqueryrecord SET dequeue_date =? WHERE task_id=?', (datetime.datetime.utcnow(), task_id))
        con.commit()
    
    logging.info('task_id [%s] is received.', task_id)
    #print task_id
    #print task_arg
    #print blast_formatter_path
    
    args = json.loads(task_arg)
    # run blast process
    subprocess.Popen(args).wait()
    
    # convert to multiple formats
    asn_filename = args[-3] # ex. /usr/local/i5k/media/3ee04cec89b54d33ba557335b7b7134d/3ee04cec89b54d33ba557335b7b7134d.asn
    file_prefix = args[-3].replace('.asn', '')
    for ext, outfmt in blast_out_ext.items():
        args = [blast_formatter_path, '-archive', asn_filename, '-outfmt', outfmt, '-out', file_prefix + ext]
        if ext == '.html':
            args.append('-html')
        subprocess.Popen(args).wait()
  
    # update job finish time
    con = sqlite3.connect('../db.sqlite3')
    with con:
        cur = con.cursor()
        cur.execute('UPDATE blast_blastqueryrecord SET result_date =? WHERE task_id=?', (datetime.datetime.utcnow(), task_id))
    
    logging.info('task_id [%s] is done.', task_id)
    ch.basic_ack(delivery_tag = method.delivery_tag)

thread_num = 3
thread_list = []
if len(sys.argv)==3 and sys.argv[1]=='-threads':
    thread_num = int(sys.argv[2])

print ' [*] Multithreaded consumer is started. Kill this process to exit'

# Create new threads
for i in range(thread_num):
    thread = MyThread(i)
    thread_list.append(thread)

# Start new Threads
for i in range(thread_num):
    thread_list[i].start()

#print "Exiting Main Thread"
