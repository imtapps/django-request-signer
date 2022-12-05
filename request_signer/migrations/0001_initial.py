# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='AuthorizedClient',
            fields=[
                ('client_id', models.CharField(max_length=20, serialize=False, primary_key=True)),
                ('private_key', models.CharField(default='', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={},
            bases=(models.Model, ),
        ),
    ]
