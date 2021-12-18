from time import sleep
import sys
from .models import Collections
from django.utils import timezone
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
    return {'status':'OK', 'user':user, 'uuid':new_uuid}

def return_result(task):
    collection = Collections.objects.get(uuid=task.result['uuid'])
    collection.status = 'completed'
    collection.save()
    print (task.result, file=sys.stderr)
