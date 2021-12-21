import re

def parse_mpls_interface(f):
  cmd_mpls_interfaces = []
  for line in f.splitlines():
    search_intf = re.search('Yes.*No',line)
    if search_intf and len(line.split())==5:
      INTERFACE_ID = line.split()[0]
      cmd_mpls_interfaces.append(f'show runn interface {INTERFACE_ID}\n')
  return cmd_mpls_interfaces

def parse_mpls_qos(f):
    cmd_qos_interfaces = []
    for line in f.splitlines():
        search_sp = re.search('service-policy',line)
        if search_sp and len(line.split())==3:
            SP_NAME = line.split()[2]
            qos_cmd = f'show runn policy-map {SP_NAME}'
            if qos_cmd not in cmd_qos_interfaces:
                cmd_qos_interfaces.append(qos_cmd)
    return cmd_qos_interfaces

def parse_mpls_qos_interface(f):
    cmd_qos_interfaces = []
    SP_IN = ''
    SP_OUT = ''
    INT_DESC = ''
    for line in f.splitlines():
        search_intf = re.search('^interface',line)
        if search_intf and len(line.split())==2:
            INTF_NAME = line.split()[1]
            SP_IN = ''
            SP_OUT = ''
            INT_DESC = ''
        search_desc = re.search('description (.+)',line)
        if search_desc:
            INT_DESC = search_desc.group(1)
        search_spin = re.search('service-policy input',line)
        if search_spin and len(line.split())==3:
            SP_IN = line.split()[2]
        search_spout = re.search('service-policy output',line)
        if search_spout and len(line.split())==3:
            SP_OUT = line.split()[2]
        search_end = re.search('^!$',line)
        if search_end and len(line.split())==1:
            cmd_qos_interfaces.append({
                            'interface':INTF_NAME
                            ,'sp_out':SP_OUT
                            ,'sp_in':SP_IN
                            ,'description':INT_DESC
                            })
    return cmd_qos_interfaces

def parse_policy_map(f):
    dict_pm = {'':''}
    READ = False
    for line in f.splitlines():
        search_pm = re.search('^policy-map',line)
        if search_pm and len(line.split())==2:
            PM_NAME = line.split()[1]
            READ = True
            dict_pm[PM_NAME]=''
        if READ:
            dict_pm[PM_NAME]+=line+'\n'
        search_end = re.search('end-policy-map',line)
        if search_end and len(line.split())==1:
            READ = False
    return dict_pm
