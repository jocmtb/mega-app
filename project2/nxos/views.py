# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from .models import Devices, Mcast_flows, Script_logs, Traffic_interfaces, ARP_data, IGMP_data, Collections
from django.http import HttpResponse,JsonResponse
from .forms import NameForm, IPForm, LoginForm, CompareForm, TrafficForm, IP_XR_Form, d3Form, d3Form2
from .tests import json_data
from django.template import RequestContext
from django.http import HttpResponseRedirect
from helpers.class2_device import BaseDevice, DeviceIOS, DeviceNXOS, DeviceIOSXR
from .scripts_all import parse, Compare_flows, parse_interface, parse_arp, parse_igmp, parse_mcast
from .scripts_all import parse_xr, Create_Excel_Table_xr
from datetime import datetime as dt
import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django import forms
from django.utils import timezone
import uuid
import json
from django.conf import settings
import os
import re
from mysite.settings import BASE_DIR
from django_q.tasks import async_task
from .tasks import wait_and_print, return_result, traffic_task_queue


def example_q(request):
    async_task(wait_and_print, request.user.username, hook=return_result)
    #return JsonResponse({'status':'OK','code':200})
    return HttpResponseRedirect('/nxos/list-collections/')

def get_collections(request):
    data = [ {
                'id':x.id,
                'type':x.type,
                'status':x.status,
                'uuid':x.uuid,
                'user':x.user,
                'datetime':x.datetime,
    } for x in Collections.objects.all()]
    return JsonResponse({ 'data': data })

def list_collections(request):
    return render(request, 'nxos/list_collections.html')

@login_required(login_url='/nxos/login/')
def index(request):
    #return HttpResponse("Hello, world. You're at the nxos index.")
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    #context = {'latest_question_list': latest_question_list}
    return render(request, 'nxos/index.html')

def index3(request):
    return render(request, 'nxos/index3.html')

def index_nxos(request):
    return render(request, 'nxos/dashboard_nxos.html')

def index_xr(request):
    return render(request, 'nxos/dashboard_xr.html')

def login_user(request):
    if request.method=='POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username= form.cleaned_data.get('your_email', 'default1')
            password= form.cleaned_data.get('your_password', 'default1')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('/nxos/nx/')
            else:
                return HttpResponse('User does not exist')
    else:
        form = LoginForm()
        return render(request, 'nxos/login.html', {'form': form} )

def logout_user(request):
    logout(request)
    return HttpResponse('User is now logout')

def parse_cdp(nodes,links,host,f):
    if host not in nodes.keys():
        num = len(nodes.keys())
        nodes[host] = {'id':num, 'name':host, 'image':'nexus'}
    else:
        num = nodes[host]['id']
    i = len(nodes.keys())
    for line in f.splitlines():
        search_device = re.search('^Device ID:(.+)$',line)
        if search_device:
            device = search_device.group(1).split('.')[0]
            if device not in nodes.keys():
                if 'ASR' in device:
                    nodes[device]={'id':i, 'name':device, 'image':'router'}
                elif 'NEXUS' in device or 'N9K' in device:
                    nodes[device]={'id':i, 'name':device, 'image':'nexus'}
                elif 'CAT6K' in device:
                    nodes[device]={'id':i, 'name':device, 'image':'switch'}
                elif 'CAT4K' in device:
                    nodes[device]={'id':i, 'name':device, 'image':'switch1'}
                elif 'CBR8' in device:
                    nodes[device]={'id':i, 'name':device, 'image':'cmts'}
                elif 'SEP' in device:
                    nodes[device]={'id':i, 'name':device, 'image':'phone'}
                elif 'NCS' in device:
                    nodes[device]={'id':i, 'name':device, 'image':'ncs'}
                else:
                    nodes[device]={'id':i, 'name':device, 'image':'switch2'}
                enlace = {'source':num,'target':i,'color':'orange','type':'solid'}
                if enlace not in links:
                    links.append(enlace)
                i+=1
            else:
                enlace = {'source':num,'target':nodes[device]['id'],'color':'orange','type':'solid'}
                if enlace not in links:
                    links.append(enlace)

    print ('Numero Total de Nodes: ' + str(len(nodes)) )
    return nodes,links

@login_required(login_url='/nxos/login/')
def d3_graph(request):
    if request.method=='POST':
        form = d3Form(request.POST)
        if form.is_valid():
            site = form.cleaned_data.get('sites')
            device_list = [ x.ip_address for x in Devices.objects.filter(hostname__icontains=site)]
            print (device_list)
            nodes = {}
            links=[] ; nodes2=[]
            for ip in device_list:
                router = DeviceNXOS(ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
                stdout = router.ssh_connect(['show cdp neighbor detail'])
                router.get_hostname()
                if isinstance(stdout,tuple):
                    return HttpResponse('{0} > {1}'.format(stdout[0],stdout[1]) )
                nodes,links = parse_cdp(nodes, links, router.hostname, stdout)
            for x in nodes:
                nodes2.append(nodes[x])
            data = json.dumps( { 'nodes':nodes2, 'links':links } )
            context = { 'form': form, 'data': data }
            return render(request, 'nxos/d3_graph.html', context)
    else:
        form = d3Form()
        data = json.dumps( json_data )
        context = { 'form': form, 'data': data }
        return render(request, 'nxos/d3_graph.html', context)

@login_required(login_url='/nxos/login/')
def d3_graph2(request):
    if request.method=='GET':
        form = d3Form2()
        data = json.dumps( json_data )
        context = { 'form': form, 'data': data }
        return render(request, 'nxos/d3_graph1.html', context)

@login_required(login_url='/nxos/login/')
def dashboard(request):
    if request.method=='POST':
        form = TrafficForm(request.POST)
        if form.is_valid():
            device_list = Devices.objects.all()
            host_ip= form.cleaned_data.get('devices')
            context = { 'form': form, 'hostname': host_ip.ip_address, 'device_list': device_list, 'host1': host_ip.hostname }
            return render(request, 'nxos/dashboard.html', context)
    else:
        form = TrafficForm()
        device_list = Devices.objects.all()
        context = { 'form': form, 'hostname': '10.0.166.249', 'device_list': device_list, 'host1': 'TVD-SW-N9K-VIDEO1-QRO' }
        return render(request, 'nxos/dashboard.html', context)

@login_required(login_url='/nxos/login/')
def dashboard2(request,hostname):
    if request.method=='POST':
        '''form = TrafficForm(request.POST)
        if form.is_valid():
            device_list = Devices.objects.all()
            host_ip= form.cleaned_data.get('devices')
            context = { 'form': form, 'hostname': host_ip.ip_address, 'device_list': device_list, 'host1': host_ip.hostname }
            return render(request, 'nxos/dashboard.html', context)'''
    else:
        form = TrafficForm()
        device_list = Devices.objects.all()
        host_fetch=Devices.objects.get(ip_address=hostname)
        if host_fetch:
            host_name=host_fetch.hostname
            context = { 'form': form, 'hostname': hostname, 'device_list': device_list, 'host1': host_name }
            return render(request, 'nxos/dashboard.html', context)
        else:
            HttpResponse('No host in database with that IP-Address')


@login_required(login_url='/nxos/login/')
def script_type(request, option_id):
    #tipo = get_object_or_404(Question, pk=option_id)
    return render(request, 'nxos/detail.html', {'tiposc': option_id})

def thanks(request, name):
    return render(request, 'nxos/thanks.html', {'user_id': name})
'''
def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)
'''
@login_required(login_url='/nxos/login/')
def about(request):
    return render(request, 'nxos/about.html', {'user_id': 'jocmtb'})
    #return HttpResponse("This page is created by %s." % 'jocmtb')

@login_required(login_url='/nxos/login/')
def traffic_interface(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            host_ip = form.cleaned_data.get('alternativas').ip_address
            async_task(traffic_task_queue, request.user.username, host_ip, hook=return_result)
            return HttpResponseRedirect('/nxos/list-collections/')
            #return render(request, 'nxos/thanks.html', {'user_id': host_ip} )
    else:
        form = IPForm()
        return render(request, 'nxos/launch_script.html', {'form': form, 'type_var': 'traffic'} )

@login_required(login_url='/nxos/login/')
def arp_info(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            host_ip= form.cleaned_data.get('alternativas').ip_address
            router=DeviceNXOS(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            stdout=router.ssh_connect(['show interface description | i Vlan',
                                        'show mac address-table ',
                                        'show ip arp' ] )
            if isinstance(stdout,tuple):
                return HttpResponse('{0} > {1}'.format(stdout[0],stdout[1]) )
            dict_ARP,lista_MAC=parse_arp(stdout)
            for arp in lista_MAC:
                device_now = ARP_data(host_id=host_ip,
                                            arp_ip=arp['mac_ip'],
                                             arp_mac=arp['mac_add'],
                                             arp_intf=arp['mac_intf'],
                                             arp_vlan=arp['mac_vlan'],
                                             vlan_name=arp['vlan_name'],
                                             datetime=timezone.now() )
                device_now.save()
            return render(request, 'nxos/thanks.html', {'user_id': host_ip} )
    else:
        form = IPForm()
        return render(request, 'nxos/launch_script.html', {'form': form, 'type_var': 'arp_data'} )


@login_required(login_url='/nxos/login/')
def join_igmp(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            host_ip= form.cleaned_data.get('alternativas').ip_address
            router=DeviceNXOS(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            stdout=router.ssh_connect(['show ip igmp groups'] )
            if isinstance(stdout,tuple):
                return HttpResponse('{0} > {1}'.format(stdout[0],stdout[1]) )
            lista_IGMP=parse_igmp(stdout)
            for arp in lista_IGMP:
                device_now = IGMP_data(host_id=host_ip,
                                            mcast_grp=arp['mcast_grp'],
                                             mcast_src=arp['mcast_src'],
                                             reporter_ip=arp['reporter_ip'],
                                             intf=arp['intf'],
                                             version=arp['version'],
                                             datetime=timezone.now() )
                device_now.save()
            return render(request, 'nxos/thanks.html', {'user_id': host_ip} )
    else:
        form = IPForm()
        return render(request, 'nxos/launch_script.html', {'form': form, 'type_var': 'join_igmp'} )


@login_required(login_url='/nxos/login/')
def get_name(request):
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
            router=DeviceNXOS(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            stdout=router.ssh_connect(['show version','show inventory'])
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
            return render(request, 'nxos/thanks.html', {'user_id': host_ip} )
            #return HttpResponse("Thanks for submitting your Form %s." % name1)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    return render(request, 'nxos/launch_script.html', {'form': form, 'type_var': 'addon'} )

@login_required(login_url='/nxos/login/')
def delete_device(request):
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
            return render(request, 'nxos/thanks.html', {'user_id': host_ip} )
            #return HttpResponse("Thanks for submitting your Form %s." % name1)
    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    return render(request, 'nxos/launch_script.html', {'form': form, 'type_var': 'delete'} )

@login_required(login_url='/nxos/login/')
def show_logs(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            ip1= form.cleaned_data.get('alternativas').ip_address
            router=BaseDevice(ip1, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            output_data=router.ssh_connect(['show ip mroute detail'])
            if type(output_data)==tuple:
                return HttpResponse('Hit Exception: {0} {1}'.format(output_data[0],output_data[1] ) )
            lista_MCAST_GRP,dict_MCAST_GRP=parse(output_data)
            file_name='mcastflow_'+str(uuid.uuid4())
            file_path = os.path.join(BASE_DIR, "nxos/session_logs", file_name)
            with open(file_path,'w') as file:
                file.write(output_data)
            date_now=timezone.now()
            entrada= Script_logs(host_id=ip1,script_type='mcastflow'
                                ,file_location=file_name
                                 ,data_date=date_now)
            entrada.save()
            for x in lista_MCAST_GRP:
                entrada= Mcast_flows(src_mcast=x['mcast_grp'][0],mcast_grp=x['mcast_grp'][1]
                                 ,host_id=ip1
                                ,in_intf=x['in_intf']
                                 ,rpf_neighbor=x['rpf_nbr']
                                 ,flow_status=x['stat_flow']
                                 ,out_intf=x['out_intfs']
                                 ,data_date=date_now)
                entrada.save()
            return render(request, 'nxos/show_logs.html', {'form': form, 'log_file_contents': output_data, 'type_form': 'mcast_flows'} )
    else:
        form = IPForm()
    return render(request, 'nxos/show_logs.html', {'form': form, 'type_form': 'mcast_flows'} )

@login_required(login_url='/nxos/login/')
def session_logs(request):
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
        file_name = request.GET.get('file_name', '')
        file_path = os.path.join(BASE_DIR, "nxos/session_logs", file_name)
        with open(file_path,'r') as file:
            file_data=file.read()
    return render(request, 'nxos/show_logs.html', {'form': form, 'type_form': 'session_logs', 'log_file_contents': file_data} )

@login_required(login_url='/nxos/login/')
def backup(request):
    if request.method == 'POST':
        form = IPForm(request.POST)
        if form.is_valid():
            ip1= form.cleaned_data.get('alternativas').ip_address
            router=BaseDevice(ip1, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
            output_data=router.ssh_connect(settings.LISTA_CMD)
            if type(output_data)==tuple:
                return HttpResponse('Hit Exception: {0} {1}'.format(output_data[0],output_data[1] ) )
            date_now=timezone.now()
            file_name = 'backup_'+str(uuid.uuid4())
            file_path = os.path.join(BASE_DIR, "nxos/session_logs", file_name)
            with open(file_path,'w') as file:
                file.write(output_data)
            entrada= Script_logs(host_id=ip1,script_type='backup'
                                ,file_location=file_name
                                 ,data_date=date_now)
            entrada.save()
            return render(request, 'nxos/show_logs.html', {'form': form, 'log_file_contents': output_data, 'type_form': 'backup'} )
    else:
        form = IPForm()
    return render(request, 'nxos/show_logs.html', {'form': form, 'type_form': 'backup'} )

@login_required(login_url='/nxos/login/')
def compare_mcast(request):
    if request.method == 'POST':
        form = CompareForm(request.POST)
        if form.is_valid():
            flow1= form.cleaned_data.get('alternativas1')
            flow2= form.cleaned_data.get('alternativas2')
            file_path1=file_path = os.path.join(BASE_DIR, "nxos/session_logs", flow1.file_location)
            with open(file_path1,'r') as file:
                lista_MCAST_GRP,dict_MCAST_GRP=parse(file.read())
            file_path2=file_path = os.path.join(BASE_DIR, "nxos/session_logs", flow2.file_location)
            with open(file_path2,'r') as file:
                lista_MCAST_GRP2,dict_MCAST_GRP2=parse(file.read())
            joc=Compare_flows(dict_MCAST_GRP,dict_MCAST_GRP2)
            data_tabla = json.dumps( {"data": joc} )
            return render(request, 'nxos/compare_mcast.html', { 'form': form, 'log_file_contents': 'mcast_flows'
                                                            , 'lista_diffs': data_tabla } )
    else:
        form = CompareForm()
    return render(request, 'nxos/compare_mcast.html', {'form': form, 'type_form': 'compare_flows'} )

### APi ###
# All Api method return JSON responses
### APi ###
def api_traffic_table(request,hostname):
    data_list = []
    devs = Traffic_interfaces.objects.filter(host_id=hostname).all()
    if devs.count() != 0:
        for x in devs:
            data_list.append( { 'interface_id':x.interface_id,
                       'input_rate':x.input_rate,
                       'output_rate':x.output_rate,
                       'datetime':x.data_date} )
    return JsonResponse( {'data':data_list} )

def api_traffic(request,hostname):
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

def api_host_stats(request,stat_id):
    joc=[]
    joc2=[]
    joc3=[]
    if stat_id=='statsnxos1':
      host_list = Devices.objects.all()
      for x in host_list:
         joc.append(x.version)
         if x.version not in joc2:
           joc2.append(x.version)
      for x in joc2:
         joc3.append([x,joc.count(x)])
    if stat_id=='statsnxos2':
      host_list = Devices.objects.all()
      for x in host_list:
         joc.append(x.platform)
         if x.platform not in joc2:
           joc2.append(x.platform)
      for x in joc2:
         joc3.append([x,joc.count(x)])
    if stat_id=='statsnxos3':
      joc3=[['DATOS',0],['VIDEO',0],['HUB',0]]
      host_list = Devices.objects.all()
      for x in host_list:
         if 'VIDEO' in x.hostname:
           joc3[1][1]+=1
         if 'DATOS' in x.hostname:
           joc3[0][1]+=1
         if 'HUB' in x.hostname:
           joc3[2][1]+=1
    return JsonResponse({'data':joc3})

def hostnames(request):
    data = {'data':[]}
    query_results = Devices.objects.all();
    for x in query_results:
        data['data'].append({'hostname':x.hostname,'IP_Address':x.ip_address,'platform':x.platform,'version':x.version})
    return JsonResponse(data)

def ajax_mcast_flows(request):
    data = {'data':[]}
    query_results = Mcast_flows.objects.all();
    for x in query_results:
        data['data'].append({'mcast_src':x.src_mcast,'mcast_grp':x.mcast_grp
                            ,'in_intf':x.in_intf,'out_intf':x.out_intf
                            ,'flow_stat':x.flow_status,'rpf_nei':x.rpf_neighbor
                            ,'datetime':x.data_date,'host':x.host_id})
    return JsonResponse(data)

def script_logs(request):
    data = {'data':[]}
    query_results = Script_logs.objects.all();
    if query_results.count() != 0:
        for x in query_results:
            data['data'].append({'sc_type':x.script_type,'file_name':x.file_location
                            ,'datetime':x.data_date,'host':x.host_id})
    return JsonResponse(data)

def script_logs_by_host(request,hostname):
    data = {'data':[]}
    query_results = Script_logs.objects.filter(host_id=hostname).all();
    if query_results.count() != 0:
        for x in query_results:
            data['data'].append({'sc_type':x.script_type,'file_name':x.file_location
                            ,'datetime':x.data_date,'host':x.host_id})
    return JsonResponse(data)

def api_arp(request,hostname):
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

def api_join_igmp(request,hostname):
    data_list = []
    devs = IGMP_data.objects.filter(host_id=hostname).all()
    if devs.count() != 0:
        for x in devs:
            data_list.append( {  'host_id':x.host_id,
                        'mcast_grp':x.mcast_grp,
                       'mcast_src':x.mcast_src,
                       'reporter_ip':x.reporter_ip,
                       'version':x.version,
                       'intf':x.intf,
                       'datetime':x.datetime} )
    return JsonResponse( {'data':data_list} )

###TEST defs###
def download(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404
