import psycopg2
import random, string
from django.db import models
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, pre_save, post_save, m2m_changed
from django.dispatch import receiver

class Species(models.Model):
    name = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=200, unique=True)
    host = models.CharField(max_length=100)
    db_name = models.CharField(max_length=100)
    db_acct = models.CharField(max_length=100)
    db_pwd = models.CharField(max_length=50, blank=True)
    url =  models.URLField(unique=True)

    # properties
    def db_exists(self):
        try:
            conn = psycopg2.connect('dbname=' + self.db_name + ' user=' + self.db_acct + ' host=' + self.host)
            cur = conn.cursor()
            cur.close()
            conn.close()
            return True
        except:
            return False    
    db_exists.boolean = True
    db_exists.short_description = 'Postgres DB exists'

    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        content_type = ContentType.objects.get_for_model(Species)
        for perm in ['read', 'write', 'publish', 'admin', 'owner']:
            Permission.objects.update_or_create(codename = self.name + '_' + perm,
                                               name = self.name + '_' + perm,
                                               content_type = content_type)
        # todo: deploy_instance()
        super(Species, self).save(*args, **kwargs)

class SpeciesPassword(models.Model):
    user = models.ForeignKey(User)
    species = models.ForeignKey(Species)
    pwd = models.CharField(max_length=64)
    
    class Meta:
        unique_together = ('user', 'species', 'pwd',)

    def __unicode__(self):
        return self.user.username + ' - ' + self.species.name

class Registration(models.Model):
    user = models.ForeignKey(User)
    species = models.ForeignKey(Species)
    submission_time = models.DateTimeField(auto_now_add=True)
    decision_time = models.DateTimeField(null=True, blank=True)
    submission_comment = models.TextField(blank=True, max_length=200)
    decision_comment = models.TextField(blank=True, max_length=200)
    REG_STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Removed', 'Removed'),
        ('Added', 'Added'),
    )
    status = models.CharField(max_length=10, choices=REG_STATUS, default='Pending')

    class Meta:
        unique_together = ('user', 'species', 'submission_time',)

    def __unicode__(self):
        return self.user.username + ' for ' + self.species.name + ': ' + self.status

@receiver(post_delete, sender=Species, weak=False)
def species_post_delete(sender, instance, **kwargs):
    Permission.objects.filter(codename__startswith=instance.name).delete()
    # todo: clear all SSO user permission in postgres DB
    # todo: undeploy_instance()

def delete_species_permission(username, species_id):
    try:
        species = Species.objects.get(id=species_id)
        conn = psycopg2.connect('dbname=' + species.db_name + ' user=' + species.db_acct + ' host=' + species.host)
        cur = conn.cursor()
    
        cur.execute('SELECT user_id FROM users WHERE username=%s', (username,))
        rows = cur.fetchall()
        if rows:
            user_id = int(rows[0][0])
            cur.execute('DELETE FROM permissions WHERE user_id=%s', (user_id,))
            conn.commit()

        cur.close()
        conn.close()
    except:
        print 'Exception in delete_species_permission'
        raise Exception('Exception in delete_species_permission')

@receiver(post_save, sender=User)
def user_post_save(instance, **kwargs):
    # clear all permissions won't trigger m2m_changed event. so trying to clear postgres db manually.
    # but failed because the perms I get are old...
    _user = User.objects.get(pk=instance.id)  
    #perms = Permission.objects.filter(content_type=ContentType.objects.get_for_model(Species), user=_user)
    '''
    if perms:
        print 'Todo: nothing'
    else:
        print 'Todo: remove records from postgres db'
    '''

@receiver(m2m_changed, sender=User.user_permissions.through)
def user_m2m_changed(instance, action, pk_set, **kwargs):
    #print 'm2m_change', action
    #print pk_set
    if action == 'post_add':    
        # first, delete all permissions in WebApollo postgres DB,
        # then add new permissions back
        species = Species.objects.all()
        for s in species:
            delete_species_permission(instance.username, s.id)
            
        content_type = ContentType.objects.get_for_model(Species)
        perm_values = {'read': 1, 'write': 2, 'publish': 4, 'admin': 8, 'owner': 0}
        species_perms = {}
        for _pk in pk_set:
            perm = Permission.objects.get(id=_pk)
            if perm.content_type == content_type:
                # insert new permissions into WebApollo DB
                #print perm.name, perm.codename, perm.content_type
                species_name = perm.name.split('_', 2)[0]
                perm_name = perm.name.split('_', 2)[1]
                species_id = Species.objects.get(name=species_name).id
                if species_id not in species_perms:
                    species_perms[species_id] = perm_values[perm_name]
                else:
                    species_perms[species_id] = species_perms[species_id] + perm_values[perm_name]
        for k,v in species_perms.items():
            insert_species_permission(instance.username, k, v)

def insert_species_permission(username, species_id, perm_value): 
    try:
        species = Species.objects.get(id=species_id)
        conn = psycopg2.connect('dbname=' + species.db_name + ' user=' + species.db_acct + ' host=' + species.host)
        cur = conn.cursor()
        
        cur.execute('SELECT user_id FROM users WHERE username = %s', (username,))
        rows = cur.fetchall()
        if not rows: 
            pwd = ''.join(random.SystemRandom().choice(string.uppercase + string.digits) for _ in xrange(16))
            cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, pwd,))
            spe_pwd = SpeciesPassword()
            spe_pwd.user = User.objects.get(username=username)
            spe_pwd.species = species
            spe_pwd.pwd = pwd
            spe_pwd.save()
        cur.execute('SELECT user_id FROM users WHERE username=%s', (username,))
        rows = cur.fetchall()
        user_id = int(rows[0][0])

        cur.execute('SELECT track_id FROM tracks')
        rows = cur.fetchall()
        if rows:
            for row in rows:
                track_id = int(row[0])
                cur.execute('INSERT INTO permissions (track_id, user_id, permission) VALUES (%s, %s, %s)', (track_id, user_id, perm_value,))

        conn.commit()
        cur.close()
        conn.close()
    except:
        print 'Exception in insert_species_permission'
        raise Exception('Exception in insert_species_permission')

@receiver(post_delete, sender=User, weak=False)
def user_post_delete(sender, instance, **kwargs):
    species = Species.objects.all()
    for s in species:
        delete_species_permission(instance.username, s.id)
