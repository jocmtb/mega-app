import re

def parse_mpls_interface(f):
  cmd_mpls_interfaces = []
  for line in f.splitlines():
    search_intf = re.search('Yes.*No',line)
    if search_intf and len(line.split())==5:
      INTERFACE_ID = line.split()[0]
      cmd_mpls_interfaces.append(f'show runn interface {INTERFACE_ID}\n')
  return cmd_mpls_interfaces
