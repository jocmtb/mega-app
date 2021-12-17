FROM nginxinc/nginx-unprivileged:1-alpine
# copy configuration for nginx
COPY ./mega-proxy/default.conf /etc/nginx/conf.d/default.conf
# switch tmp to root for create files
USER root
# install openssl
RUN apk update && apk add openssl
#RUN mkdir /etc/nginx/certificate
#RUN cd /etc/nginx/certificate
#RUN touch nginx-certificate.crt
#RUN touch nginx.key
#RUN chmod 755 /etc/nginx/certificate/
#RUN chmod 755 /etc/nginx/certificate/nginx-certificate.crt
#RUN chmod 755 /etc/nginx/certificate/nginx.key
#RUN openssl req -new -newkey rsa:4096 -x509 -sha256 -days 365 -nodes -out nginx-certificate.crt -keyout nginx.key
# create directory
RUN mkdir -p /vol/static
# copy all static files
COPY mega-proxy/mega.corp.codetel.com.do.cer /etc/nginx/certificate/mega.corp.codetel.com.do.cer
COPY mega-proxy/mega.corp.codetel.com.do.key /etc/nginx/certificate/mega.corp.codetel.com.do.key
COPY mega-proxy/static /vol/static
# give permissions to directory
RUN chmod 755 /vol/static
# switch to default user
USER nginx
