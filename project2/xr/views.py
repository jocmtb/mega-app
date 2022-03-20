# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.template import RequestContext
from django.http import HttpResponseRedirect
from datetime import datetime as dt
import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.utils import timezone
from .forms import NameForm, IPForm, LoginForm, CompareForm, TrafficForm, IP_XR_Form, d3Form
from .models import Devices, Mcast_flows, Script_logs, Traffic_interfaces, ARP_data, IGMP_data
from .models import QoSInterfaces
from .scripts_all import parse_mcast, parse_xr, Create_Excel_Table_xr, parse_interface, parse_arp, parse_mcast_igmp
from .scripts_all import parse_igmp
from helpers.class2_device import BaseDevice
from helpers.parse_cmd import parse_mpls_interface, parse_mpls_qos, parse_mpls_qos_interface, parse_policy_map
import uuid
import json
from .helpers import json_data, parse_bgp
from django.conf import settings
import os
from mysite.settings import BASE_DIR


def index2(request):
    return render(request, 'xr/index2.html')


def index_xr(request):
    return render(request, 'xr/dashboard_xr.html')

@login_required(login_url='/nxos/login/')
def d3_graph(request):
    if request.method=='POST':
        form = d3Form(request.POST)
        if form.is_valid():
            site = form.cleaned_data.get('sites')
            device_list = [ x.ip_address for x in Devices.objects.filter(hostname__icontains=site+'_ctc')]
            #return JsonResponse({'data':device_list})
            nodes = {}
            links=[] ; nodes2=[]
            for ip in device_list:
                router = BaseDevice(ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
                stdout = router.ssh_connect(['show bgp ipv4 unic neighbor | i "^BGP neighbor|Descrip"', 'show bgp summary'])
                router.get_hostname()
                if isinstance(stdout,tuple):
                    return HttpResponse('{0} > {1}'.format(stdout[0],stdout[1]) )
                nodes,links = parse_bgp(nodes, links, router.hostname, stdout)
            for x in nodes:
                nodes2.append(nodes[x])
            data = json.dumps( { 'nodes':nodes2, 'links':links } )
            context = { 'form': form, 'data': data }
            return render(request, 'xr/d3_graph.html', context)
    else:
        form = d3Form()
        data = json.dumps( json_data )
        context = { 'form': form, 'data': data }
        return render(request, 'xr/d3_graph.html', context)

@login_required(login_url='/nxos/login/')
def add_device(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            host_ip= form.cleaned_data.get('your_ip')
            router=BaseDevice(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            stdout=router.ssh_connect(['show version brief','admin show inventory chassis'])
            router.get_hostname()
            router.get_version()
            router.parse_shinvchassis()
            device_now = Devices.objects.filter(ip_address=host_ip)
            if device_now.count() == 0:
                ts=time.time()
                st = dt.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                new_host = Devices(hostname=router.hostname, ip_address=host_ip
                         ,version=router.version, platform=router.platform )
                new_host.save()
            else:
                device_now = Devices.objects.get(ip_address=host_ip)
                device_now.hostname=router.hostname
                device_now.version=router.version
                device_now.platform=router.platform
                device_now.save()
            return render(request, 'xr/result_page.html', {'user_id': host_ip} )
            #return HttpResponse("Thanks for submitting your Form %s." % name1)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    return render(request, 'xr/launch_script.html', {'form': form, 'type_var': 'addon'} )

@login_required(login_url='/nxos/login/')
def delete_device_xr(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            host_ip= form.cleaned_data.get('your_ip')
            device_now = Devices.objects.filter(ip_address=host_ip)
            if device_now.count() == 0:
                return HttpResponse("Device with IP: %s does not Exist." % host_ip)
            else:
                device_now = Devices.objects.get(ip_address=host_ip)
                device_now.delete()
            return render(request, 'xr/result_page.html', {'user_id': host_ip} )
            #return HttpResponse("Thanks for submitting your Form %s." % name1)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    return render(request, 'xr/launch_script.html', {'form': form, 'type_var': 'delete'} )

@login_required(login_url='/nxos/login/')
def backup_xr(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            ip1= form.cleaned_data.get('alternativas').ip_address
            router=BaseDevice(ip1, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            output_data=router.ssh_connect(settings.LISTA_CMD_XR)
            if type(output_data)==tuple:
                return HttpResponse('Hit Exception: {0} {1}'.format(output_data[0],output_data[1] ) )
            date_now=timezone.now()
            file_name='backup_'+str(uuid.uuid4())
            file_path = os.path.join(BASE_DIR, "xr/session_logs", file_name)
            with open(file_path,'w') as file:
                file.write(output_data)
            entrada= Script_logs(host_id=ip1,script_type='backup'
                                ,file_location=file_name
                                 ,data_date=date_now)
            entrada.save()
            return render(request, 'xr/show_logs.html', {'form': form, 'log_file_contents': output_data, 'type_form': 'backup'} )
    else:
        form = IPForm()
    return render(request, 'xr/show_logs.html', {'form': form, 'type_form': 'backup'} )

@login_required(login_url='/nxos/login/')
def qos_xr(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            ip1 = form.cleaned_data.get('alternativas').ip_address
            router = BaseDevice(ip1, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            output_data = router.send_command(parse_mpls_interface, ['show mpls interfaces'])
            if type(output_data) == tuple:
                return HttpResponse('Hit Exception: {0} {1}'.format(output_data[0],output_data[1] ) )
            hostname = router.get_hostname()
            lista_qos = parse_mpls_qos(output_data)
            output_data2 = router.ssh_connect(lista_qos)
            if type(output_data2) == tuple:
                return HttpResponse('Hit Exception: {0} {1}'.format(output_data2[0],output_data2[1] ) )
            date_now = timezone.now()
            output_data +=  output_data2
            file_name ='qos_'+str(uuid.uuid4())
            file_path = os.path.join(BASE_DIR, "xr/session_logs", file_name)
            with open(file_path,'w') as file:
                file.write(output_data)
            entrada = Script_logs(
                                host_id = ip1
                                ,script_type = 'qos'
                                ,file_location = file_name
                                ,data_date = date_now
                                )
            entrada.save()
            dict_pm = parse_policy_map(output_data)
            list_interfaces = parse_mpls_qos_interface(output_data)
            data = {'interfaces':list_interfaces, 'policy-map':dict_pm}
            for x in list_interfaces:
                new_qos = QoSInterfaces(
                        hostname = hostname,
                        interface = x['interface'],
                        description = x['description'],
                        input_sp = x['sp_in'],
                        output_sp = x['sp_out'],
                        input_sp_config = dict_pm[x['sp_in']],
                        output_sp_config = dict_pm[x['sp_out']],
                        datetime = date_now
                        )
                new_qos.save()
            return render(request, 'xr/show_logs.html', {'form': form, 'log_file_contents': output_data, 'type_form': 'qos'} )
    else:
        form = IPForm()
    return render(request, 'xr/show_logs.html', {'form': form, 'type_form': 'qos'} )

def qos_pm(request, type, qos_id):
    qos_entry = QoSInterfaces.objects.get(id=qos_id)
    if type=='input':
        data =  {  'config':qos_entry.input_sp_config  }
    else:
        data =  {  'config':qos_entry.output_sp_config  }
    return JsonResponse({ 'data': data })

def get_qos(request):
    data = [ {
                'id':x.id,
                'hostname':x.hostname,
                'interface':x.interface,
                'description':x.description,
                'input_sp':x.input_sp,
                'output_sp':x.output_sp,
                'datetime':x.datetime.strftime('%d %B %Y, %I:%M %p'),
    } for x in QoSInterfaces.objects.all().order_by('-id')]
    return JsonResponse({ 'data': data })

def list_qos(request):
    return render(request, 'xr/list_qos.html')

@login_required(login_url='/nxos/login/')
def session_logs_xr(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            ip1= form.cleaned_data.get('alternativas').ip_address
            router=BaseDevice(ip1, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            output_data=router.ssh_connect(['show ip mroute detail'])
            if type(output_data)==tuple:
                return HttpResponse('Hit Exception: {0} {1}'.format(output_data[0],output_data[1] ) )
            date_now=timezone.now()
            return render(request, 'nxos/show_logs.html', {'form': form, 'log_file_contents': output_data, 'type_form': 'session_logs'} )
    else:
        form = IPForm()
        file_name=request.GET.get('file_name', '')
        file_path = os.path.join(BASE_DIR, "xr/session_logs", file_name)
        with open(file_path,'r') as file:
            file_data=file.read()
    return render(request, 'xr/show_logs.html', {'form': form, 'type_form': 'session_logs', 'log_file_contents': file_data} )

@login_required(login_url='/nxos/login/')
def xr_mcast(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            host_ip= form.cleaned_data.get('alternativas').ip_address
            x = dt.now()
            date1 = ("%s-%s-%s_%s-%s-%s" % (x.year, x.month, x.day,x.hour,x.minute,x.second) )
            router = BaseDevice(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            output_data = router.send_command(parse_mcast,['show mrib vrf ?'])
            docfile = os.path.join(BASE_DIR, "xr/session_logs", f'{host_ip}_mcast_{date1}')
            file_name = host_ip+'_mcast_'+date1
            with open(docfile,'w') as file:
                file.write(router.buffer)
            f1 = open (docfile,'r')
            lista_MCAST_GRP,dict_MCAST_GRP=parse_xr(f1)
            f1.close()
            date_now=timezone.now()
            entrada= Script_logs(host_id=host_ip,script_type='xr_mcastflow'
                                ,file_location=file_name
                                 ,data_date=date_now)
            entrada.save()
            for x in lista_MCAST_GRP.keys():
                for item in lista_MCAST_GRP[x]:
                    entrada= Mcast_flows(src_mcast=item['mcast_grp'][0],mcast_grp=item['mcast_grp'][1]
                                     ,host_id=host_ip
                                    ,in_intf=item['in_intf']
                                     ,rpf_neighbor=item['rpf_nbr']
                                     ,flow_status=x
                                     ,out_intf=item['out_intfs']
                                     ,data_date=date_now)
                    entrada.save()
            filename = Create_Excel_Table_xr(host_ip, date1, lista_MCAST_GRP)
            return render(request, 'xr/result_page.html', {'user_id': host_ip, 'file_name': filename} )
    else:
        form = IPForm()
        return render(request, 'xr/launch_script.html', {'form': form, 'type_var': 'xr_mcast'} )

@login_required(login_url='/nxos/login/')
def join_igmp_xr(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            host_ip= form.cleaned_data.get('alternativas').ip_address
            x = dt.now()
            date1 = ("%s-%s-%s_%s-%s-%s" % (x.year, x.month, x.day,x.hour,x.minute,x.second) )
            router=BaseDevice(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            output_data=router.send_command(parse_mcast_igmp,['show mrib vrf ?'])
            docfile = os.path.join(BASE_DIR, "xr/session_logs", f'{host_ip}_igmp_{date1}')
            file_name=host_ip+'_igmp_'+date1
            with open(docfile,'w') as file:
                file.write(router.buffer)
            f1 = open (docfile,'r')
            lista_IGMP=parse_igmp(f1)
            f1.close()
            date_now=timezone.now()
            entrada= Script_logs(host_id=host_ip,script_type='xr_join_igmp'
                                ,file_location=file_name
                                 ,data_date=date_now)
            entrada.save()
            for x in lista_IGMP:
                entrada = IGMP_data(host_id=host_ip,
                                    mcast_grp=x['mcast_grp'],
                                    mcast_src=x['mcast_src'],
                                    reporter_ip=x['reporter_ip'],
                                    intf=x['intf'],
                                    vrf_id=x['vrf_id'],
                                    datetime=timezone.now() )
                entrada.save()
            return render(request, 'xr/result_page.html', {'user_id': host_ip, 'join_igmp': 'join_igmp'} )
    else:
        form = IPForm()
        return render(request, 'xr/launch_script.html', {'form': form, 'type_var': 'join_igmp'} )

@login_required(login_url='/nxos/login/')
def traffic_interface_xr(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            host_ip= form.cleaned_data.get('alternativas').ip_address
            router=BaseDevice(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            stdout=router.ssh_connect(['show interfaces'])
            if isinstance(stdout,tuple):
                return HttpResponse('{0} > {1}'.format(stdout[0],stdout[1]) )
            interfaces=parse_interface(stdout)
            for interfaz in interfaces.keys():
                device_now = Traffic_interfaces(host_id=host_ip,
                                            interface_id=interfaz,
                                             input_rate=interfaces[interfaz]['input_rate'],
                                             output_rate=interfaces[interfaz]['output_rate'],
                                             data_date=timezone.now() )
                device_now.save()
            return render(request, 'xr/result_page.html', {'user_id': host_ip} )
    else:
        form = IPForm()
        return render(request, 'xr/launch_script.html', {'form': form, 'type_var': 'traffic'} )

@login_required(login_url='/nxos/login/')
def dashboard_xr(request):
    if request.method=='POST':
        form = TrafficForm(request.POST)
        if form.is_valid():
            device_list = Devices.objects.all()
            host_ip= form.cleaned_data.get('devices')
            context = { 'form': form, 'hostname': host_ip.ip_address, 'device_list': device_list, 'host1': host_ip.hostname }
            return render(request, 'xr/dashboard.html', context)
    else:
        form = TrafficForm()
        device_list = Devices.objects.all()
        context = { 'form': form, 'hostname': '189.196.41.47', 'device_list': device_list, 'host1': 'RAC_ASR9K10_Tol_CTC' }
        return render(request, 'xr/dashboard.html', context)

@login_required(login_url='/nxos/login/')
def arp_info_xr(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            host_ip= form.cleaned_data.get('alternativas').ip_address
            router=BaseDevice(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            stdout=router.ssh_connect(['show interfaces description', 'show ipv4 vrf all interface brief', 'show arp vrf all'  ] )
            if isinstance(stdout,tuple):
                return HttpResponse('{0} > {1}'.format(stdout[0],stdout[1]) )
            lista_MAC=parse_arp(stdout)
            for arp in lista_MAC:
                device_now = ARP_data(host_id=host_ip,
                                            arp_ip=arp['mac_ip'],
                                             arp_mac=arp['mac_add'],
                                             arp_intf=arp['mac_intf'],
                                             arp_vlan=arp['mac_vrf'],
                                             vlan_name=arp['descrip_name'],
                                             datetime=timezone.now() )
                device_now.save()
            return render(request, 'xr/result_page.html', {'user_id': host_ip} )
    else:
        form = IPForm()
        return render(request, 'xr/launch_script.html', {'form': form, 'type_var': 'arp_data'} )

###########
##API API API API FUNctions ####
############

def hostnames_xr(request):
    data = {'data':[]}
    query_results = Devices.objects.all();
    for x in query_results:
        data['data'].append({'hostname':x.hostname,'IP_Address':x.ip_address,'platform':x.platform,'version':x.version})
    return JsonResponse(data)

def api_host_stats_xr(request,stat_id):
    joc=[]
    joc2=[]
    joc3=[]
    if stat_id=='statsxr':
      host_list = Devices.objects.all()
      for x in host_list:
         joc.append(x.version)
         if x.version not in joc2:
           joc2.append(x.version)
      for x in joc2:
         joc3.append([x,joc.count(x)])
    return JsonResponse({'data':joc3})

def script_logs_xr(request):
    data = {'data':[]}
    query_results = Script_logs.objects.all();
    if query_results.count() != 0:
        for x in query_results:
            data['data'].append({
                        'sc_type':x.script_type
                        ,'file_name':x.file_location
                        ,'datetime':x.data_date.strftime('%d %B %Y, %I:%M %p')
                        ,'host':x.host_id
                            })
    return JsonResponse(data)

def api_traffic_table_xr(request,hostname):
    data_list = []
    devs = Traffic_interfaces.objects.filter(host_id=hostname).all()
    if devs.count() != 0:
        for x in devs:
            data_list.append( { 'interface_id':x.interface_id,
                       'input_rate':x.input_rate,
                       'output_rate':x.output_rate,
                       'datetime':x.data_date} )
    return JsonResponse( {'data':data_list} )

def api_traffic_xr(request,hostname):
    data_list = []
    devs = Traffic_interfaces.objects.filter(host_id=hostname).all()
    if devs.count() != 0:
        for x in devs:
            ts_seconds= (x.data_date - dt(1970,1,1)).total_seconds()
            tiempo= int(ts_seconds*1000)
            data_list.append( { 'interface_id':x.interface_id,
                       'input_rate':x.input_rate,
                       'output_rate':x.output_rate,
                       'datetime':tiempo} )
    return JsonResponse( {'data':data_list} )

def script_logs_by_host_xr(request,hostname):
    data = {'data':[]}
    query_results = Script_logs.objects.filter(host_id=hostname).all();
    if query_results.count() != 0:
        for x in query_results:
            data['data'].append({'sc_type':x.script_type,'file_name':x.file_location
                            ,'datetime':x.data_date,'host':x.host_id})
    return JsonResponse(data)

def api_arp_xr(request,hostname):
    data_list = []
    devs = ARP_data.objects.filter(host_id=hostname).all()
    if devs.count() != 0:
        for x in devs:
            data_list.append( {  'host_id':x.host_id,
                        'arp_ip':x.arp_ip,
                       'arp_mac':x.arp_mac,
                       'arp_vlan':x.arp_vlan,
                       'vlan_name':x.vlan_name,
                       'arp_intf':x.arp_intf,
                       'datetime':x.datetime} )
    return JsonResponse( {'data':data_list} )

def ajax_mcast_flows_xr(request):
    data = {'data':[]}
    query_results = Mcast_flows.objects.all();
    for x in query_results:
        data['data'].append({'mcast_src':x.src_mcast,'mcast_grp':x.mcast_grp
                            ,'in_intf':x.in_intf,'out_intf':x.out_intf
                            ,'flow_stat':x.flow_status,'rpf_nei':x.rpf_neighbor
                            ,'datetime':x.data_date,'host':x.host_id})
    return JsonResponse(data)

def api_join_igmp_xr(request,hostname):
    data_list = []
    devs = IGMP_data.objects.filter(host_id=hostname).all()
    if devs.count() != 0:
        for x in devs:
            data_list.append( {  'host_id':x.host_id,
                        'mcast_grp':x.mcast_grp,
                       'mcast_src':x.mcast_src,
                       'reporter_ip':x.reporter_ip,
                       'vrf_id':x.vrf_id,
                       'intf':x.intf,
                       'datetime':x.datetime} )
    return JsonResponse( {'data':data_list} )

###TEST defs###
def download_xr(request, filename):
    file_path = os.path.join(BASE_DIR, "xr/session_logs", filename)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
