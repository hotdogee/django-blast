from django.db import models
from django.contrib.auth.models import User
from blast.models import Organism
from filebrowser.fields import FileBrowseField


# Create your models here.

#class User_account(models.Model):

        
class MigrateUserRecord(models.Model):
    username = models.CharField(max_length=300)
    password = models.CharField(max_length=70)
    submission_date = models.DateTimeField(auto_now_add=True)
    organism = models.ForeignKey(Organism, default=0)
    user = models.ForeignKey(User, null=True, blank=True)
