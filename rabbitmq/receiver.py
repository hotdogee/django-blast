import pika 
import sys
import logging

logging.basicConfig()

def assign(task_id, task_arg, fmt_path):
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='blast_query', durable=True)
    message = "task_id=" + task_id + "arg=" + task_arg + "fmt=" + fmt_path
    channel.basic_publish(exchange='',
                      routing_key='blast_query',
                      body=message,
                      properties=pika.BasicProperties(
                          delivery_mode = 2))
    connection.close()


