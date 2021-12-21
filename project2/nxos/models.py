# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.db import models
from django.utils import timezone

# Create your models here.
class Devices(models.Model):
    hostname = models.CharField(max_length=200)
    ip_address = models.CharField(max_length=200)
    platform = models.CharField(max_length=200)
    version = models.CharField(max_length=200)
    def __str__(self):
        return self.hostname

class Collections(models.Model):
    user = models.CharField(max_length=200)
    uuid = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    status = models.CharField(max_length=200)
    err_msg = models.CharField(max_length=200, default="na")
    datetime = models.DateTimeField('date published')
    def __str__(self):
        return '{0} <> {1}'.format(self.uuid, self.type)

class Mcast_flows(models.Model):
    host_id = models.CharField(max_length=200)
    src_mcast = models.CharField(max_length=200)
    mcast_grp = models.CharField(max_length=200)
    in_intf = models.CharField(max_length=200)
    rpf_neighbor = models.CharField(max_length=200)
    flow_status = models.CharField(max_length=200)
    out_intf = models.CharField(max_length=200)
    data_date = models.DateTimeField('date published')
    def __str__(self):
        return self.mcast_grp

class Script_logs(models.Model):
    host_id = models.CharField(max_length=200)
    script_type = models.CharField(max_length=200)
    file_location = models.CharField(max_length=200)
    data_date = models.DateTimeField('date published')
    def __str__(self):
        return Devices.objects.get(ip_address=self.host_id).hostname+'<>'+self.data_date.strftime('%d %B %Y, %I:%M %p')

class Traffic_interfaces(models.Model):
    host_id = models.CharField(max_length=200)
    interface_id = models.CharField(max_length=200)
    input_rate = models.BigIntegerField()
    output_rate = models.BigIntegerField()
    data_date = models.DateTimeField('date published')
    def __str__(self):
        return self.host_id+'_'+str(self.data_date)

class ARP_data(models.Model):
    host_id = models.CharField(max_length=200)
    arp_mac = models.CharField(max_length=200)
    arp_ip = models.CharField(max_length=200)
    arp_intf = models.CharField(max_length=200)
    arp_vlan = models.CharField(max_length=200)
    vlan_name = models.CharField(max_length=200)
    datetime = models.DateTimeField('date published')
    def __str__(self):
        return '{0} on {1}'.format(self.arp_mac, self.arp_intf)

class IGMP_data(models.Model):
    host_id = models.CharField(max_length=200)
    mcast_grp = models.CharField(max_length=200)
    mcast_src = models.CharField(max_length=200)
    version = models.CharField(max_length=200)
    reporter_ip = models.CharField(max_length=200)
    intf = models.CharField(max_length=200)
    datetime = models.DateTimeField('date published')
    def __str__(self):
        return '({0} , {1}) is joined by {2}'.format(self.mcast_grp, self.mcast_src, self.reporter_ip)
