from os import path
from django.conf import settings

def get_gff(in_task_id, in_dbname):
    file_prefix = path.join(settings.MEDIA_ROOT, in_task_id, in_dbname)

    gff_content = []
    try:
        with open(file_prefix+'.gff', 'r') as fp:
            for line in fp:
                gff_content.append(line)
        return ''.join(gff_content)

    except:
        return "##gff-version 3\n"