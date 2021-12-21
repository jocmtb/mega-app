
import paramiko as pm
import time
import re
import socket
import sys
'''
Class to instance network objects
'''
TACACS_USER='provciscojosec'
TACACS_PASSWORD='y^2R[!MzSc'

class BaseDevice():
        def __init__(self,ip_address,comando='',user=TACACS_USER,password=TACACS_PASSWORD):
                self.ip_address=ip_address
                self.hostname='unknown'
                self.portssh=22
                self.comand=comando+'\nexit\n'
                self.user=user
                self.buffer=''
                self.version='unknown'
                self.platform='unknown'
                self.serial='unknown'
                self.uptime='0 days'
                self.paging='terminal length 0\n'
                self.paging2='terminal width 510\n'
                self.password=password
        def ssh_connect(self,comandos=[],):
                if isinstance(comandos,list):
                        comandos.append(self.comand)
                        comandosn=[x+'\n' for x in comandos]
                else:
                        return 'method expects a list variable'
                try:
                        client = pm.SSHClient()
                        client.load_system_host_keys()
                        client.set_missing_host_key_policy(pm.AutoAddPolicy())
                        client.connect(self.ip_address, username=self.user, password=self.password)
                        channel = client.invoke_shell()
                        time.sleep(1)
                        channel.settimeout(20)
                        stdin = channel.makefile('wb')
                        stdout = channel.makefile('rb')
                        stdin.write(self.paging)
                        stdin.write(self.paging2)
                        for cmd in comandosn:
                                stdin.write(cmd)
                        output_data = stdout.read()
                        self.buffer += output_data.decode("utf-8")
                        stdout.close(); stdin.close(); client.close()
                        return output_data.decode("utf-8")
                except Exception as e:
                        return type(e).__name__, str(e)
        def send_command(self,func1,comandos=[]):
                if isinstance(comandos,list):
                        #comandos.append(self.comand)
                        comandosn=[x+'\n' for x in comandos]
                else:
                        return 'method expects a list variable'
                try:
                        client = pm.SSHClient()
                        client.load_system_host_keys()
                        client.set_missing_host_key_policy(pm.AutoAddPolicy())
                        client.connect(self.ip_address, username=self.user, password=self.password)
                        channel = client.invoke_shell()
                        time.sleep(1)
                        channel.settimeout(30)
                        stdin = channel.makefile('wb')
                        stdout = channel.makefile('rb')
                        stdin.write(self.paging)
                        stdin.write(self.paging2)
                        for cmd in comandosn:
                                stdin.write(cmd)
                        stdin.write('### Connection terminated\n')
                        while True:
                                x = channel.recv(1024)
                                self.buffer += x.decode("utf-8")
                                #print x
                                if '### Connection terminated' in self.buffer:
                                     break
                        lista2 = func1(self.buffer)
                        #print(lista2, file=sys.stderr)
                        for cmd in lista2:
                                stdin.write(cmd)
                        stdin.write('exit\n')
                        output_data = stdout.read()
                        self.buffer += output_data.decode("utf-8")
                        stdout.close(); stdin.close(); client.close()
                        return self.buffer
                except Exception as e:
                        return type(e).__name__, str(e)
        def validate_ip(self):
                ipv=self.ip_address.split('.')
                if len(ipv) != 4:
                        return False
                for i,x in enumerate(ipv):
                        if i==0 and int(x) > 0 and int(x) < 256:
                                continue
                        elif i>0 and int(x) >= 0 and int(x) < 256:
                                continue
                        else:
                                return False
                return True
        def clear_buffer(self):
                self.buffer=''
        def ssh_active(self):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.ip_address,self.portssh))
                if result == 0:
                        print (self.ip_address+" : Port " + str(self.portssh)+ " is open")
                else:
                        print ("Port " + str(self.portssh)+ " is not open")
                        print ('  >> port CLOSED, connect_ex returned: '+str(result))
        def get_hostname(self,texto=''):
                if isinstance(texto, str) and texto!='':
                        lista=texto.splitlines()
                elif texto=='' and self.buffer!='':
                        lista=self.buffer.splitlines()
                elif texto=='' and self.buffer=='':
                        return 'Buffer is empty.'
                else:
                        return 'method expects a string variable'
                for line in lista:
                        hostname = re.search('^(.+)#.*', line)
                        if hostname:
                                host1=hostname.group(1)
                                if ':'in host1:
                                        host2=host1.split(':')
                                        self.hostname=host2[1]
                                        return host2[1]
                                elif '@'in host1:
                                        host2=host1.split('@')
                                        self.hostname=host2[1]
                                        return host2[1]
        def __repr__(self):
                return 'device: {0}'.format(self.ip_address)
        def parse_bgpsum(self):
                array1=[]
                for line in self.buffer.splitlines():
                        bgpsum = re.search('^[0-9]+.[0-9]+.[0-9]+.[0-9]+\s+.*', line)
                        if (bgpsum and len(line.split())==10):
                                array1.append(line.split())
                return array1
        def parse_shipintbri(self):
                array1=[]
                for line in self.buffer.splitlines():
                        shipintbri = re.search('^(.+)\s+(.+)\s+([USD].+)\s+([USDP].+)\s+(.+)$', line)
                        if (shipintbri and len(line.split())==5):
                                array1.append(line.split())
                return array1
        def parse_shisisnei(self):
                array1=[]
                for line in self.buffer.splitlines():
                        shisisnei = re.search('^(.+)\s+(.+)\s+(.+)\s+(.+)\s+(.+)\s+(.+)\s+(.+)$', line)
                        if (shisisnei and len(line.split())==7):
                                array1.append(line.split())
                return array1
        def parse_shmplsnei(self):
                array1=[]
                for line in self.buffer.splitlines():
                        shmplsnei = re.search('^Peer LDP Identifier: (.+)$', line)
                        if shmplsnei:
                                ldpnei=shmplsnei.group(1)
                        tcpcon = re.search('^  TCP connection: (.+)$', line)
                        if (tcpcon):
                                array1.append([ldpnei,tcpcon.group(1)])
                        shmplsnei2 = re.search('^\s+([GTPBS].+)$', line)
                        if (shmplsnei2 and len(line.split())==1):
                                array1.append([ldpnei,shmplsnei2.group(1)])
                return array1
        def parse_shplatform(self):
                array1=[]
                for line in self.buffer.splitlines():
                        shplatform = re.search('^(0/.+)\s+(.+)\s+.*$', line)
                        if (shplatform and len(line.split())>=4):
                                bana=line.split()
                                array1.append([bana[0],bana[1],' '.join(bana[2:-1]),bana[-1]])
                return array1
        def parse_shinvchassis(self):
                array1=[]
                for line in self.buffer.splitlines():
                        shchassis = re.search('^PID: (.+), VID: (.+), SN: (.+)$', line)
                        if (shchassis and len(line.split())==6):
                                bana=line.split()
                                array1.append([bana[1],bana[3],bana[5]])
                                self.serial=bana[5]
                                self.platform=bana[1]
                return array1
        def get_version(self):
                for line in self.buffer.splitlines():
                        gversion = re.search('^Cisco IOS.*$', line)
                        if (gversion):
                                self.version=line
                        guptime = re.search('^(.+)\s+uptime\s+is\s+(.+)$', line)
                        if (guptime):
                                self.uptime=guptime.group(2)

class DeviceLinux(BaseDevice):
        portssh=22
        def __init__(self,ip_address,comando='',user='root',password='t3l3f0n1c4!'):
                self.ip_address=ip_address
                self.portssh=22
                self.buffer=''
                self.hostname='None'
                self.comand=comando+'\nexit\n'
                self.user=user
                self.paging='date\n'
                self.password=password
        def get_hostname(self,texto=''):
                if isinstance(texto,str) and texto!='':
                        lista=texto.splitlines()
                elif texto=='' and self.buffer!='':
                        lista=self.buffer.splitlines()
                elif texto=='' and self.buffer=='':
                        return 'Buffer is empty.'
                else:
                        return 'method expects a string variable'
                for line in lista:
                        hostname = re.search('^(.+)\s+(.+)#.*', line)
                        if hostname:
                                host1=hostname.group(1)
                                if '@'in host1:
                                        host2=host1.split('@')
                                        self.hostname=host2[1]
                                        return host2[1]
        def __repr__(self):
                return 'device: {0}'.format(self.ip_address)

class DeviceJunos(BaseDevice):
        portssh=22
        def __init__(self,ip_address,comando='',user='usertftp',password='TFTPL0g!N'):
                self.ip_address=ip_address
                self.portssh=22
                self.buffer=''
                self.hostname='None'
                self.comand=comando+'\nexit\n'
                self.user=user
                self.paging='set cli screen-length 0\n'
                self.password=password
        def get_hostname(self,texto=''):
                if isinstance(texto,str) and texto!='':
                        lista=texto.splitlines()
                elif texto=='' and self.buffer!='':
                        lista=self.buffer.splitlines()
                elif texto=='' and self.buffer=='':
                        return 'Buffer is empty.'
                else:
                        return 'method expects a string variable'
                for line in lista:
                        hostname = re.search('^(.+)>.*', line)
                        if hostname:
                                host1=hostname.group(1)
                                if '@'in host1:
                                        host2=host1.split('@')
                                        self.hostname=host2[1]
                                        return host2[1]
        def __repr__(self):
                return 'device: {0}'.format(self.ip_address)

class DeviceIOS(BaseDevice):
        portssh=22
        def __init__(self,ip_address,comando='',user='jcostav',password='Lima2018$'):
                self.ip_address=ip_address
                self.portssh=22
                self.buffer=''
                self.hostname='None'
                self.comand=comando+'\nexit\n'
                self.user=user
                self.paging='terminal length 0\n'
                self.paging2='enable\n'
                self.password=password
        def get_hostname(self,texto=''):
                if isinstance(texto,str) and texto!='':
                        lista=texto.splitlines()
                elif texto=='' and self.buffer!='':
                        lista=self.buffer.splitlines()
                elif texto=='' and self.buffer=='':
                        return 'Buffer is empty.'
                else:
                        return 'method expects a string variable'
                for line in lista:
                        hostname = re.search('^(.+)#.*show', line)
                        if hostname and '##' not in line:
                                self.hostname=hostname.group(1)
                                return hostname.group(1)
        def parse_shinvchassis(self):
                array1=[]
                for line in self.buffer.splitlines():
                        shchassis = re.search('^PID: (.+), VID: (.+), SN: (.+)$', line)
                        if (shchassis and len(line.split())>6):
                                bana=line.split()
                                if len(line.split())==8:
                                   array1.append([bana[1],bana[4],bana[7]])
                                   self.serial=bana[7]
                                   self.platform=bana[1]
                                   break
                                if len(line.split())==7:
                                   array1.append([bana[1],bana[4],bana[6]])
                                   self.serial=bana[6]
                                   self.platform=bana[1]
                                   break
        def get_version(self):
                for line in self.buffer.splitlines():
                        gversion = re.search('^Cisco IOS XE.*Version.*$', line)
                        if (gversion):
                                self.version=line
                        guptime = re.search('^(.+)\s+uptime\s+is\s+(.+)$', line)
                        if (guptime):
                                self.uptime=guptime.group(2)
        def __repr__(self):
                return 'device: {0}'.format(self.ip_address)

class DeviceIOSXR(BaseDevice):
        portssh=22
        def __init__(self,ip_address,comando='',user='jcostav',password='Lima2018$'):
                self.ip_address=ip_address
                self.portssh=22
                self.buffer=''
                self.hostname='None'
                self.comand=comando+'\nexit\n'
                self.user=user
                self.paging='terminal length 0\n'
                self.paging2='terminal width 512\n'
                self.password=password
        def parse_shinvchassis(self):
                array1=[]
                for line in self.buffer.splitlines():
                        shchassis1 = re.search('^NAME: (.+), DESCR: (.+)$', line)
                        if (shchassis1 and len(line.split())>4):
                            DESCRIP=shchassis1.group(2)
                        shchassis = re.search('^PID: (.+), VID: (.+), SN: (.+)$', line)
                        if (shchassis and len(line.split())>6):
                                bana=line.split()
                                if len(line.split())==8:
                                   array1.append([bana[1],bana[4],bana[7]])
                                   self.serial=bana[7]
                                   self.platform=bana[1]
                                   if 'Chassis' in DESCRIP:
                                       break
                                if len(line.split())==7:
                                   array1.append([bana[1],bana[4],bana[6]])
                                   self.serial=bana[6]
                                   self.platform=bana[1]
                                   if 'Chassis' in DESCRIP:
                                       break

        def get_version(self):
                for line in self.buffer.splitlines():
                        gversion = re.search('^Cisco IOS XR.*Version.*$', line)
                        if (gversion):
                                self.version=line
                        guptime = re.search('^(.+)\s+uptime\s+is\s+(.+)$', line)
                        if (guptime):
                                self.uptime=guptime.group(2)
        def __repr__(self):
                return 'device: {0}'.format(self.ip_address)

class DeviceNXOS(BaseDevice):
        portssh=22
        def __init__(self,ip_address,comando='',user='jcostav',password='Lima2018$'):
                self.ip_address=ip_address
                self.portssh=22
                self.buffer=''
                self.hostname='None'
                self.version='unkown'
                self.platform='unkown'
                self.uptime='unkown'
                self.comand=comando+'\nexit\n'
                self.user=user
                self.paging='terminal length 0\n'
                self.paging2='enable\n'
                self.password=password
        def get_hostname(self,texto=''):
                if isinstance(texto,str) and texto!='':
                        lista=texto.splitlines()
                elif texto=='' and self.buffer!='':
                        lista=self.buffer.splitlines()
                elif texto=='' and self.buffer=='':
                        return 'Buffer is empty.'
                else:
                        return 'method expects a string variable'
                for line in lista:
                        hostname = re.search('^(.+)#.*show', line)
                        if hostname:
                                self.hostname=hostname.group(1)
                                return hostname.group(1)
        def parse_shinvchassis(self):
                array1=[]
                for line in self.buffer.splitlines():
                        shchassis = re.search('^PID: (.+)\s+,\s+VID: (.+)\s+,\s+SN: (.+)$', line)
                        if (shchassis and len(line.split())>6):
                                bana=line.split()
                                array1.append([bana[1],bana[4],bana[7]])
                                self.serial=bana[7]
                                self.platform=bana[1]
                                return self.platform
        def get_version(self):
                for line in self.buffer.splitlines():
                        gversion = re.search('^  NXOS: (.+)$', line)
                        if (gversion):
                                self.version='NX-OS Software '+gversion.group(1)
                        n7kversion = re.search('^  system: (.+)$', line)
                        if (n7kversion):
                                self.version='NX-OS Software '+n7kversion.group(1)
                        guptime = re.search('^Kernel\s+uptime\s+is\s+(.+)$', line)
                        if (guptime):
                                self.uptime=guptime.group(1)
                                return self.version,self.uptime
        def __repr__(self):
                return 'device: {0}'.format(self.ip_address)

if __name__=='__main__':
        time1=time.time()
        router1=BaseDevice('200.37.0.239','date','root','t3l3f0n1c4!')
        logs1=router1.ssh_connect()
        print (logs1)
        time2=time.time()-time1
        print ('Elapsed Time: ',time2)
