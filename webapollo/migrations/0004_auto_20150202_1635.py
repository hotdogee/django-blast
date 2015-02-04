# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webapollo', '0003_auto_20150202_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submission_time', models.DateTimeField(auto_now_add=True)),
                ('decision_time', models.DateTimeField(null=True)),
                ('submission_comment', models.TextField(max_length=300, blank=True)),
                ('decision_comment', models.TextField(max_length=300, blank=True)),
                ('status', models.CharField(default=b'PENDING', max_length=32)),
                ('species', models.ForeignKey(to='webapollo.Species')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='registraion',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='registraion',
            name='species',
        ),
        migrations.RemoveField(
            model_name='registraion',
            name='user',
        ),
        migrations.DeleteModel(
            name='Registraion',
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together=set([('user', 'species')]),
        ),
    ]
