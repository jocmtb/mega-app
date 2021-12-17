# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-05-21 21:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Mcast_flows',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src_mcast', models.CharField(max_length=200)),
                ('mcast_grp', models.CharField(max_length=200)),
                ('in_intf', models.CharField(max_length=200)),
                ('rpf_neighbor', models.CharField(max_length=200)),
                ('flow_status', models.CharField(max_length=200)),
                ('out_intf', models.CharField(max_length=200)),
                ('data_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]
