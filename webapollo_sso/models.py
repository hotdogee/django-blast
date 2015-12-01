from django.db import models
from django.contrib.auth.models import User

class PermsRequest(models.Model):
    action = models.CharField(max_length=100)
    oid = models.IntegerField()
    user_apply = models.ForeignKey(User, related_name='user_apply')
    apply_date = models.DateTimeField(auto_now_add=True)
    apply_desc = models.CharField(max_length=120, blank=True)
    reply_desc = models.CharField(max_length=120, blank=True)
    user_reply = models.ForeignKey(User, related_name='user_reply', blank=True, null=True)
    end_date = models.DateTimeField(auto_now=True, blank=True)
    status = models.CharField(max_length=20)

    def __unicode__(self):
        return self.action

class UserMapping(models.Model):
    apollo_user_id = models.IntegerField(unique=True)
    apollo_user_name = models.CharField(max_length=100)
    apollo_user_pwd = models.CharField(max_length=50)
    django_user = models.OneToOneField(User,unique=True, blank=True, null=True)
    last_date = models.DateTimeField(auto_now=True, blank=True)

    def __unicode__(self):
        return unicode(self.apollo_user_id) or u''