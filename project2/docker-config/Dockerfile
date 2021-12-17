# import the last base image from respository
FROM ubuntu:latest
# expose the port 8000 for noa services connectivity
EXPOSE 8000
# change to root directory
WORKDIR /root/
# change of variable to avoid configuration questions
ENV DEBIAN_FRONTEND=noninteractive
# update to the lastest code
RUN apt update
# install dependencys
RUN apt install python3-pip python3-dev libpq-dev curl gunicorn iputils-ping vim nano tzdata -y
# install requirements for noa
COPY ./requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt --default-timeout=100
# create directories for noa service discovery
RUN mkdir /root/static && mkdir /var/log/mega && mkdir /root/project2 && cd /root/project2
# run GUNICORN - DJANGO - CELERY
CMD /root/project2/docker-config/services-wrapper.sh
