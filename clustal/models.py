from django.db import models
from django.contrib.auth.models import User

class ClustalQueryRecord(models.Model):
    task_id = models.CharField(max_length=32, primary_key=True)
    enqueue_date = models.DateTimeField(auto_now_add=True)
    dequeue_date = models.DateTimeField(null=True)
    result_date = models.DateTimeField(null=True)
    result_status = models.CharField(max_length=32, default='WAITING')
    user = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        verbose_name = 'Clustal result'
# Create your models here.
