from django.db import models
from django.contrib.auth.models import User

class ClustalQueryRecord(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True) # ex. 128c8661c25d45b8-9ca7809a09619db9
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)
    result_status = models.CharField(max_length=32, default='WAITING') # ex. WAITING, SUCCESS, NO_ASN, ASN_EMPTY, NO_CSV, CSV_EMPTY
    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        verbose_name = 'Clustal result'
# Create your models here.
