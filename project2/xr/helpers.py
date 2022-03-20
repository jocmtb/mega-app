import re

json_data = {
'nodes': [{  'index':0, 'name': "PR-IPP-01",  'image': "ncs" ,'ip':'172.16.10.1'},
        {  'index':1, 'name': "PR-IPP-02",  'image': "ncs",'ip':'172.16.10.2' },
         {  'index':2, 'name': "ASR03",  'image': "taipan",'ip':'221.22.40.1' },
          {  'index':3, 'name': "ASR04",  'image': "switch" ,'ip':'201.34.10.1'},
           {  'index':4, 'name': "ASR05",  'image': "router",'ip':'189.164.20.1' }
      ],
'links': [
  { 'source': 0, 'target': 2, 'index':0, 'color':'orange', 'type':'solid' },
  { 'source': 0, 'target': 2, 'index':1, 'color':'#909497', 'type':'solid' },
  { 'source': 0, 'target': 3, 'index':2, 'color':'#34495E', 'type':'dashed' },
  { 'source': 0, 'target': 4, 'index':3, 'color':'#34495E', 'type':'dashed' },
  { 'source': 1, 'target': 2, 'index':4, 'color':'#34495E', 'type':'dashed2' },
  { 'source': 1, 'target': 3, 'index':5, 'color':'#34495E', 'type':'dashed2' },
  { 'source': 1, 'target': 4, 'index':6, 'color':'#34495E', 'type':'solid' }
]
}

def parse_bgp(nodes,links,host,f):
    devices_info = {}
    if host not in nodes.keys():
        current_node_id = len(nodes.keys())
        nodes[host] = {'index':current_node_id, 'name':host, 'image':'ncs' }
    else:
        current_node_id = nodes[host]['index']
    i = len(nodes.keys())
    for line in f.splitlines():
        search_device_ip = re.search('^BGP neighbor is (.+)',line)
        if search_device_ip:
            DEVICE_IP = search_device_ip.group(1).strip()
            devices_info[DEVICE_IP]='na'
        search_device_desc = re.search('^ Description: (.+)',line)
        if search_device_desc:
            DEVICE_DESC = search_device_desc.group(1).strip()
            devices_info[DEVICE_IP]=DEVICE_DESC
        search_device = re.search('^\d+\.\d+\.\d+\.\d+',line)
        if search_device and len(line.split()) == 10:
            device = line.split()[0]
            if device not in nodes.keys():
                nodes[device]={'index':i, 'name':devices_info[device][:16], 'image':'router', 'ip':device}
                enlace = {'source':current_node_id,'target':i,'color':'#34495E','type':'dashed'}
                if enlace not in links:
                    links.append(enlace)
                i+=1
            else:
                enlace = {'source':current_node_id,'target':nodes[device]['index'],'color':'#909497','type':'solid'}
                if enlace not in links:
                    links.append(enlace)

    print ('Numero Total de Nodes: ' + str(len(nodes)) )
    return nodes,links
