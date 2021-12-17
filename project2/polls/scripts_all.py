import re
import sys
import xlsxwriter

def parse(f):
  jose=[]
  jose3={}
  OUT_INTF=''
  for line in f.splitlines():
    search=re.search('.*\((.+), (.+)\), uptime.*',line)
    if search:
      #print 'match#1'
      MCAST_SRC=search.group(1)
      MCAST_GRP=search.group(2)
      OUT_INTF=''
      jose2=[]
    search2=re.search('Incoming interface: (.+), RPF nbr: (.+)',line)
    if search2:
      #print 'match#2'
      IN_INTF=search2.group(1)
      if ',' in search2.group(2):
        RPF_NBR=search2.group(2).split(',')[0]
      else:
        RPF_NBR=search2.group(2)
    stat_flow=re.search('Stats: (.+) Flow',line)
    if stat_flow:
      #print 'match#2'
      STAT_FLOW=stat_flow.group(1)
    search3=re.search('Outgoing interface list: \(count: (.+)\)',line)
    if search3 and len(line.split())==5:
      #print 'match#3'
      OUT_INTF=search3.group(1)
      OUT_INTF_COUNT=int(OUT_INTF)
      count_cc1=0
      if count_cc1==OUT_INTF_COUNT:
        jose2.append('none')
        jose.append({'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':IN_INTF
                    ,'rpf_nbr':RPF_NBR
					,'out_intf_count':OUT_INTF
					,'out_intfs':','.join(jose2)
					,'stat_flow':STAT_FLOW})
        jose3[(MCAST_SRC,MCAST_GRP)]={'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':IN_INTF
					,'out_intf_count':OUT_INTF
					,'out_intfs':jose2
					,'stat_flow':STAT_FLOW}
    search31=re.search('Outgoing interface list: \(count: (.+)\) \(bri',line)
    if search31 and len(line.split())==7:
      #print 'match#3'
      OUT_INTF=search31.group(1)
      OUT_INTF_COUNT=int(OUT_INTF)
      count_cc1=0
      if count_cc1==OUT_INTF_COUNT:
        jose2.append('none')
        jose.append({'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':IN_INTF
                    ,'rpf_nbr':RPF_NBR
					,'out_intf_count':OUT_INTF
					,'out_intfs':','.join(jose2)
					,'stat_flow':STAT_FLOW})
        jose3[(MCAST_SRC,MCAST_GRP)]={'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':IN_INTF
					,'out_intf_count':OUT_INTF
					,'out_intfs':jose2
					,'stat_flow':STAT_FLOW}
    out_intfs=re.search('.*\s+(.+), uptime:',line)
    if out_intfs and OUT_INTF!='':
      #print 'match#2'
      count_cc1+=1
      OUT_INTFS=out_intfs.group(1)
      jose2.append(OUT_INTFS)
      if count_cc1==OUT_INTF_COUNT:
        jose.append({'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':IN_INTF
                    ,'rpf_nbr':RPF_NBR
					,'out_intf_count':OUT_INTF
					,'out_intfs':','.join(jose2)
					,'stat_flow':STAT_FLOW})
        jose3[(MCAST_SRC,MCAST_GRP)]={'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':IN_INTF
					,'out_intf_count':OUT_INTF
					,'out_intfs':jose2
					,'stat_flow':STAT_FLOW}
  print 'Numero Total de Prefijos: ' + str(len(jose))
  return jose,jose3

def Compare_flows(dict_MCAST_GRP,dict_MCAST_GRP2):
    joc=[]
    for x in dict_MCAST_GRP.keys():
      if x not in dict_MCAST_GRP2.keys():
        print "Missing Mcast route : " + str(x)
        joc.append({'mcast_grp':str(x)
                    ,'diff_type':'Missing Mcast route'
					,'input_intf':str(dict_MCAST_GRP[x]['in_intf'])
					,'description':'mcast route exist in first file now it is gone'})
      elif dict_MCAST_GRP[x]['in_intf'] != dict_MCAST_GRP2[x]['in_intf']:
        print "INPUT Intf Mcast route : " + str(x) + " Missmatched " + str(dict_MCAST_GRP[x]['in_intf']) + "/" + str(dict_MCAST_GRP2[x]['in_intf'])
        joc.append({'mcast_grp':str(x)
                    ,'diff_type':'INPUT Intf Mcast route'
					,'input_intf':str(dict_MCAST_GRP[x]['in_intf'])
					,'description':"Missmatched " + str(dict_MCAST_GRP[x]['in_intf']) + "/" + str(dict_MCAST_GRP2[x]['in_intf'])})
      else:
        for y in dict_MCAST_GRP[x]['out_intfs']:
          if y not in dict_MCAST_GRP2[x]['out_intfs'] and y is not 'none':
            print "OUTPUT Intf Mcast route : " + str(x) +" Missing "+ str(y)
            joc.append({'mcast_grp':str(x)
                    ,'diff_type':'OUTPUT Intf Mcast route'
					,'input_intf':str(dict_MCAST_GRP[x]['in_intf'])
					,'description':'Missing '+ str(y)})
      if x in dict_MCAST_GRP2.keys():
        if dict_MCAST_GRP[x]['stat_flow'] != dict_MCAST_GRP2[x]['stat_flow']:
          print "Status Flow Change : " + str(x) + " It went from " + str(dict_MCAST_GRP[x]['stat_flow']) + " to " + str(dict_MCAST_GRP2[x]['stat_flow'])
          joc.append({'mcast_grp':str(x)
                    ,'diff_type':'Status Flow Change'
					,'input_intf':str(dict_MCAST_GRP[x]['in_intf'])
					,'description':"It went from " + str(dict_MCAST_GRP[x]['stat_flow']) + " to " + str(dict_MCAST_GRP2[x]['stat_flow'])})
    for x in dict_MCAST_GRP2.keys():
      if x not in dict_MCAST_GRP.keys():
        print "New Mcast route : " + str(x)
        joc.append({'mcast_grp':str(x)
                    ,'diff_type':'New Multicast route'
					,'input_intf':str(dict_MCAST_GRP2[x]['in_intf'])
					,'description':'new mcast route found with input intf '+ str(dict_MCAST_GRP2[x]['in_intf']) })
      else:
        for y in dict_MCAST_GRP2[x]['out_intfs']:
          if y not in dict_MCAST_GRP[x]['out_intfs'] and y is not 'none':
            print "New OUTPUT Intferface in OIL : " + str(x) +" New "+ str(y)
            joc.append({'mcast_grp':str(x)
                    ,'diff_type':'New OUTPUT Intferface in OIL'
					,'input_intf':str(dict_MCAST_GRP2[x]['in_intf'])
					,'description':'New Intf '+ str(y)})
    return joc

def parse_interface(f):
  dict_interfaces={}
  INTERFACE_ID=''
  for line in f.splitlines():
    search=re.search('^(port-channel[0-9]+) is up',line)
    if search:
      INTERFACE_ID=search.group(1)
    search2=re.search('30 seconds input rate (.+) bits/sec',line)
    if search2:
      INPUT_RATE=search2.group(1)
    search3=re.search('30 seconds output rate (.+) bits/sec',line)
    if search3:
      OUTPUT_RATE=search3.group(1)
      if INTERFACE_ID not in dict_interfaces.keys() and 'channel' in INTERFACE_ID:
          dict_interfaces[INTERFACE_ID]={'input_rate':INPUT_RATE,'output_rate':OUTPUT_RATE}
  return dict_interfaces

if __name__=='__main__':
    if len(sys.argv)==3:
      docfile1=sys.argv[1]
      docfile2=sys.argv[2]
    else:
      print 'python isis_tdp.py <file-before> <file-after>'
    exit()
