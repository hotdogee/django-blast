# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webapollo', '0002_species_full_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Registraion',
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
            unique_together=set([('user', 'species')]),
        ),
    ]
