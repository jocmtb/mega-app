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
    search_new=re.search('^(TenGigE[0-9]+/[0-9]+/[0-9]+/[0-9]+) is up, line protocol is up',line)
    if search_new:
      INTERFACE_ID=search_new.group(1)
    search=re.search('^(Bundle-Ether[0-9]+) is up, line protocol is up',line)
    if search:
      INTERFACE_ID=search.group(1)
    search2=re.search('input rate (.+) bits/sec,',line)
    if search2:
      INPUT_RATE=search2.group(1)
    search3=re.search('output rate (.+) bits/sec,',line)
    if search3:
      OUTPUT_RATE=search3.group(1)
      if INTERFACE_ID not in dict_interfaces.keys() and ('Bundle-Ether' in INTERFACE_ID or 'TenGigE' in INTERFACE_ID):
          dict_interfaces[INTERFACE_ID]={'input_rate':INPUT_RATE,'output_rate':OUTPUT_RATE}
  return dict_interfaces

def parse_arp(f):
  lista_vrf={}
  lista_macs=[]
  lista_descripcion={}
  for line in f.splitlines():
    search_descrip=re.search('up\s+up',line)
    if search_descrip:
      descripcion_final='_'.join(line.split()[3:])
      interface_id=line.split()[0]
      if 'Te' in interface_id: interface_id=interface_id.replace('Te','TenGigE')
      if 'BE' in interface_id: interface_id=interface_id.replace('BE','Bundle-Ether')
      lista_descripcion[interface_id]=descripcion_final
    search_vrf=re.search('Up\s+Up',line)
    if search_vrf and len(line.split())==5:
      interface_id=line.split()[0]
      vrf_id=line.split()[4]
      lista_vrf[interface_id]=vrf_id
    search_arp=re.search('Dynamic\s+ARPA',line)
    if (search_arp ) and len(line.split())==6:
      MAC_add=line.split()[2]
      MAC_intf=line.split()[5]
      MAC_ip=line.split()[0]
      if MAC_intf in lista_descripcion.keys():
         lista_macs.append({'mac_add':MAC_add,'mac_intf':MAC_intf,'mac_ip':MAC_ip,'mac_vrf':lista_vrf[MAC_intf],'descrip_name':lista_descripcion[MAC_intf]})
      else:
         lista_macs.append({'mac_add':MAC_add,'mac_intf':MAC_intf,'mac_ip':MAC_ip,'mac_vrf':lista_vrf[MAC_intf],'descrip_name':'None'})
  print '# Total de MACs aprendidas: ' + str(len(lista_macs))
  return lista_macs

def parse_igmp(f):
  dict_igmp=[]
  MCAST_GRP=''
  for line in f.readlines():
    search_vrf_id=re.search('show igmp vrf (.+) group',line)
    if search_vrf_id:
      VRF_ID=search_vrf_id.group(1)
    search_mcast_grp=re.search('^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',line)
    if search_mcast_grp and len(line.split())==1:
      MCAST_GRP=search_mcast_grp.group(1)
    search_v2=re.search('^([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',line)
    if search_v2 and len(line.split())==5:
      MCAST_GRP=search_v2.group(1)
      REPORTER_IP=search_v2.group(2)
      dict_igmp.append( {'mcast_grp':MCAST_GRP,'reporter_ip':REPORTER_IP
                        ,'vrf_id':VRF_ID,'mcast_src':'*','intf':line.split()[1]} )
    search_v3=re.search('^  ([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*\s+([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)',line)
    if search_v3 and len(line.split())==6:
      MCAST_SRC=search_v3.group(1)
      REPORTER_IP=search_v3.group(2)
      dict_igmp.append({'mcast_grp':MCAST_GRP,'reporter_ip':REPORTER_IP
                        ,'vrf_id':'v3','mcast_src':MCAST_SRC,'intf':line.split()[2]})
  return dict_igmp


def parse_mcast(buffer):
   lista=[]
   output_data = buffer.splitlines()
   lista2=['\n']
   for x in output_data:
      if len(x.split())==3 and 'VRF name' in x and x.split()[0]!='WORD':
         lista.append(x.split()[0])
   lista2 = [ 'show mrib vrf ' + x + ' route\n' for x in lista]
   lista2.insert(0,'\n')
   print lista2
   return lista2

def parse_mcast_igmp(buffer):
   lista=[]
   output_data = buffer.splitlines()
   lista2=['\n']
   for x in output_data:
      if len(x.split())==3 and 'VRF name' in x and x.split()[0]!='WORD':
         lista.append(x.split()[0])
   lista2 = [ 'show igmp vrf ' + x + ' group\n' for x in lista]
   lista2.insert(0,'\n')
   print lista2
   return lista2

def parse_xr(f):
  jose=[]
  jose3={}
  dict_vrf={}
  OUT_INTF=''
  MCAST_SRC=''
  MCAST_GRP=''
  INTF_IN='NA'
  RPF_NBR='NA'
  jose_out=[]
  VRF_ID='none'
  for line in f.readlines():
    search_vrf=re.search('show mrib vrf (.+) ro',line)
    if search_vrf:
      if VRF_ID!='none':
        dict_vrf[VRF_ID].append({'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':INTF_IN
                    ,'rpf_nbr':RPF_NBR
					,'out_intfs':','.join(jose_out)})
      VRF_ID=search_vrf.group(1)
      dict_vrf[VRF_ID]=[]
      MCAST_GRP=''
    search=re.search('^\((.+),(.+)\) RPF nbr: (.+) Flags',line)
    if search:
      if MCAST_GRP!='':
        dict_vrf[VRF_ID].append({'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':INTF_IN
                    ,'rpf_nbr':RPF_NBR
					,'out_intfs':','.join(jose_out)})
        jose3[(MCAST_SRC,MCAST_GRP)]={'mcast_grp':(MCAST_SRC,MCAST_GRP)
                    ,'in_intf':INTF_IN
					,'out_intf_count':OUT_INTF
					,'out_intfs':jose_out}
      #print 'match#1'
      MCAST_SRC=search.group(1)
      MCAST_GRP=search.group(2)
      RPF_NBR=search.group(3)
      OUT_INTF='OFF'
      OUT_INTF='OFF'
      jose_out=[]
      jose_in=[]
      INTF_IN='NA'
    search2=re.search('Incoming Interface List',line)
    if search2:
      #print 'match#2'
      IN_INTF='ON'
    search3=re.search('Outgoing Interface List',line)
    if search3 and len(line.split())==3:
      #print 'match#3'
      IN_INTF='OFF'
      OUT_INTF='ON'
    inout_intfs=re.search('.*\s+(.+) Flags:.*Up:',line)
    if inout_intfs and OUT_INTF!='':
      #print 'match#2'
      OUT_INTFS=line.split()[0]
      if IN_INTF=='ON':
        INTF_IN=OUT_INTFS
      elif OUT_INTF=='ON':
        jose_out.append(OUT_INTFS)

  print 'Numero Total de Prefijos: ' + str(len(dict_vrf.keys()))
  return dict_vrf,jose3

def Create_Excel_Table_xr(ip1,date1,data):

        filename='./xr/session_logs/'+ip1+'_'+date1+'_xr_mcast.xlsx'
        filename2=ip1+'_'+date1+'_xr_mcast.xlsx'
        filename=str(filename)
        # Create an new Excel file and add a worksheet.
        workbook = xlsxwriter.Workbook(filename)
        for x in data.keys():
          worksheet = workbook.add_worksheet(x)
          # Widen the first column to make the text clearer.
          worksheet.set_column(0, 0, 30)
          worksheet.set_column(1, 1, 20)
          worksheet.set_column(2, 2, 20)
          worksheet.set_column(3, 3, 20)
          worksheet.set_column(4, 4, 26)
          worksheet.set_column(5, 5, 26)
          worksheet.set_column(6, 6, 26)
          worksheet.set_column(7, 7, 18)

          #add border to cells
          border_format=workbook.add_format({
                            'border':1,
                            'align':'left',
                            'font_size':10
                           })
          worksheet.conditional_format( 'A1:N1000' , { 'type' : 'no_blanks' , 'format' : border_format} )
          # Add a bold format to use to highlight cells.
          bold = workbook.add_format({'bold': True,'bg_color':'#095381','color':'#ffffff','font_size':12})

        # Write some simple text. Text with formatting.
          worksheet.write('A1', 'Mcast Group',bold)
          worksheet.write('B1', 'Mcast Scource',bold)
          worksheet.write('C1', 'Mcast Group',bold)
          worksheet.write('D1', 'Input Interfaces', bold)
          worksheet.write('E1', 'RPF Neighbor', bold)
          worksheet.write('F1', 'Output Interfaces', bold)

          #Create excel file, put data in excel
          ordenar_left = workbook.add_format({'align':'left','font_size':10})
          custom_1 = workbook.add_format({'align':'left','font_size':10,'bg_color':'#66ff66'})
          custom_2 = workbook.add_format({'align':'left','font_size':10,'bg_color':'#ff9999'})
          i=1
          for datax in data[x]:
                # Write some numbers, with row/column notation.
                worksheet.write(i, 0, str(datax['mcast_grp']), ordenar_left)
                worksheet.write(i, 1, datax['mcast_grp'][0], ordenar_left)
                worksheet.write(i, 2, datax['mcast_grp'][1], ordenar_left)
                worksheet.write(i, 3, datax['in_intf'], ordenar_left)
                worksheet.write(i, 4, datax['rpf_nbr'], ordenar_left)
                worksheet.write(i, 5, datax['out_intfs'], ordenar_left)
                i+=1
          i=1
          print"Excel Done"
        workbook.close()
        return filename2
        #os.system('start excel.exe doc2.xlsx')


if __name__=='__main__':
    if len(sys.argv)==3:
      docfile1=sys.argv[1]
      docfile2=sys.argv[2]
    else:
      print 'python isis_tdp.py <file-before> <file-after>'
    exit()
