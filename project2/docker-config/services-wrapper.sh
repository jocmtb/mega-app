#!/bin/bash


# run script wait_for_db.py
python3 /root/ProjectNOA/docker-config/wait_for_db.py

# run django webserver development environment only
if [ "$DEVELOPMENT" == "True" ]
then
  echo "Running development environment"
  # python3 /root/ProjectNOA/manage.py createsuperuser --username admin --email noa@claro.com.do
  echo "
import os
for appFolder in os.listdir('project2'):
  if os.path.isdir(os.path.join('project2', appFolder)):
    if 'migrations' in os.listdir(os.path.join('project2', appFolder)):
      for migrationFile in os.listdir(os.path.join('project2', appFolder, 'migrations')):
        if '00' in migrationFile:
          os.remove(os.path.join('project2', appFolder, 'migrations', migrationFile))" | python3 /root/project2/manage.py shell
  python3 /root/project2/manage.py makemigrations
  python3 /root/project2/manage.py migrate --database=default
  python3 /root/project2/manage.py migrate --database=events
  echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'mega@megacable.com', 'mega123')" | python3 /root/project2/manage.py shell
  python3 /root/project2/manage.py runserver 0.0.0.0:8000
else
  echo "Running production environment"
fi
