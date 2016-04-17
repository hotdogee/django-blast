from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DrupalUserMapping(models.Model):
    django_user = models.OneToOneField(User,unique=True, blank=True, null=True)
    drupal_user_pwd = models.CharField(max_length=50)
    last_date = models.DateTimeField(auto_now=True, blank=True)

    def __unicode__(self):
        return unicode(self.django_user) or u''
