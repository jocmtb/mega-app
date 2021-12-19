from .models import Collections, Traffic_interfaces, ARP_data, IGMP_data
from helpers.class2_device import BaseDevice, DeviceIOS, DeviceNXOS, DeviceIOSXR
from .scripts_all import parse, Compare_flows, parse_interface, parse_arp, parse_igmp, parse_mcast
from .scripts_all import parse_xr, Create_Excel_Table_xr
from django.utils import timezone
from django.conf import settings
from time import sleep
import sys
import uuid

def wait_and_print(user):
    new_uuid = str(uuid.uuid4())
    new_collection = Collections(
    user = user,
    uuid = new_uuid,
    type = 'example',
    status = 'collecting',
    datetime = timezone.now(),
    )
    new_collection.save()
    sleep(60)
    return {'status':'completed', 'user':user, 'uuid':new_uuid}

def return_result(task):
    collection = Collections.objects.get(uuid=task.result['uuid'])
    collection.status = task.result['status']
    collection.err_msg = task.result['err_msg']
    collection.save()
    print (task.result, file=sys.stderr)

def traffic_task_queue(username, host_ip):
    new_uuid = str(uuid.uuid4())
    new_collection = Collections(
    user = username,
    uuid = new_uuid,
    type = 'nxos_traffic',
    status = 'collecting',
    err_msg = 'na',
    datetime = timezone.now(),
    )
    new_collection.save()
    router = DeviceNXOS(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
    stdout = router.ssh_connect(['show interface'])
    if isinstance(stdout, tuple):
        return {'status':'Failed', 'user':username, 'uuid':new_uuid, 'err_msg':f'{stdout[0]}: {stdout[1]}'}
    interfaces = parse_interface(stdout)
    for interfaz in interfaces.keys():
        device_now = Traffic_interfaces(
                                    host_id = host_ip,
                                    interface_id = interfaz,
                                    input_rate = interfaces[interfaz]['input_rate'],
                                    output_rate = interfaces[interfaz]['output_rate'],
                                    data_date = timezone.now()
                                    )
        device_now.save()
    return {'status':'completed', 'user':username, 'uuid':new_uuid, 'err_msg':"Ok"}

def arp_task_queue(username, host_ip):
    new_uuid = str(uuid.uuid4())
    new_collection = Collections(
    user = username,
    uuid = new_uuid,
    type = 'nxos_arp',
    status = 'collecting',
    err_msg = 'na',
    datetime = timezone.now(),
    )
    new_collection.save()
    router = DeviceNXOS(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
    stdout = router.ssh_connect(['show interface description | i Vlan',
                                'show mac address-table ',
                                'show ip arp' ] )
    if isinstance(stdout,tuple):
        return {'status':'Failed', 'user':username, 'uuid':new_uuid, 'err_msg':f'{stdout[0]}: {stdout[1]}'}
    dict_ARP,lista_MAC = parse_arp(stdout)
    for arp in lista_MAC:
        device_now = ARP_data(
                                host_id=host_ip,
                                arp_ip=arp['mac_ip'],
                                arp_mac=arp['mac_add'],
                                arp_intf=arp['mac_intf'],
                                arp_vlan=arp['mac_vlan'],
                                vlan_name=arp['vlan_name'],
                                datetime=timezone.now()
                                )
        device_now.save()
    return {'status':'completed', 'user':username, 'uuid':new_uuid, 'err_msg':"Ok"}

def igmp_task_queue(username, host_ip):
    new_uuid = str(uuid.uuid4())
    new_collection = Collections(
    user = username,
    uuid = new_uuid,
    type = 'nxos_igmp',
    status = 'collecting',
    err_msg = 'na',
    datetime = timezone.now(),
    )
    new_collection.save()
    router = DeviceNXOS(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
    stdout = router.ssh_connect(['show ip igmp groups'] )
    if isinstance(stdout, tuple):
        return {'status':'Failed', 'user':username, 'uuid':new_uuid, 'err_msg':f'{stdout[0]}: {stdout[1]}'}
    lista_IGMP = parse_igmp(stdout)
    for arp in lista_IGMP:
        device_now = IGMP_data(
                                host_id=host_ip,
                                mcast_grp=arp['mcast_grp'],
                                mcast_src=arp['mcast_src'],
                                reporter_ip=arp['reporter_ip'],
                                intf=arp['intf'],
                                version=arp['version'],
                                datetime=timezone.now()
                                )
        device_now.save()
    return {'status':'completed', 'user':username, 'uuid':new_uuid, 'err_msg':"Ok"}
