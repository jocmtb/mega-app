from .models import Collections, Traffic_interfaces
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
    collection.save()
    print (task.result, file=sys.stderr)

def traffic_task_queue(username, host_ip):
    new_uuid = str(uuid.uuid4())
    new_collection = Collections(
    user = username,
    uuid = new_uuid,
    type = 'nxos_traffic',
    status = 'collecting',
    datetime = timezone.now(),
    )
    new_collection.save()
    router = DeviceNXOS(host_ip, user=settings.TACACS_USER, password=settings.TACACS_PASSWORD)
    stdout = router.ssh_connect(['show interface'])
    if isinstance(stdout, tuple):
        return {'status':'Failed', 'user':username, 'uuid':new_uuid}
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
    return {'status':'completed', 'user':username, 'uuid':new_uuid}
