#!/usr/bin/env python3
from sys import argv
xml_file = argv[1]

#parsing xml
import xml.etree.ElementTree as etree
tree = etree.parse('xml_file')
all_nodes_xml = tree.findall('.//node')


legit = ['R', 'NXOS']
routing = input('Would you like to enable routing? Press O for OSPF, I for ISIS or N for none.')
mpls = input('Do you need to enable MPLS? Press R for RSVP, L for LDP or N for none.')
output = input('Would you like to save configuration to separate file or you would rather have it printed? Press F for saving, P for printing.')
if output == 'F':
	file_name = input('Enter file name: ')
rsvp_bw = 10000
node_attributes = {}
result_config = {}


#here we just compose a dictionary which contains a list of every node's connected interfaces and corresponding network ids
for node in all_nodes_xml:
	for i in legit:
		if i in node.attrib['name'].upper():
			node_name = node.attrib['name']
			node_attributes[node_name] = {}
			interfaces = node.findall('interface')
			for interface in interfaces:
				int_id = 'interface_id_' + interface.attrib['id']
				node_attributes[node_name][int_id] = [ interface.attrib['name'].split()[-1], interface.attrib['network_id']]
		
#making a set of all existing network ids
net_set = set([ i[1] for node in node_attributes for i in node_attributes[node].values() ]) 

#a little cludge which purpose is to prevent loopback and routing config generation duplication
checkloopback = {}
checkrouting = {}
checkmpls = {}
for i in node_attributes.keys():
	checkloopback[i], checkrouting[i], checkmpls[i] = [False for i in range(3)]
	

#walking over the net_set and node_attributes, making note of nodes which has the same network id we're going through in net_set right now
for net in net_set:
	remember = {} 
	node_names_digit_octet = [] #sorted list of hostname digits, like ['4', '8'] for R4 and R8
	node_names_digit = {} #contains hotname and corresponding digit, like  {'R4': '4', 'R8': '8'}

	for node in node_attributes:
		for value in node_attributes[node].values():
			if value[1] == net:
				remember[node] = []
				if not node in result_config:
					result_config[node] = []				
				remember[node].append(value[0])
	
	#collecting digits from nodes hostnames and sorting them
	for node in remember:
		node_names_digit_octet.append(int(''.join([symbol for symbol in node if symbol.isdigit()])))
		node_names_digit[node] = ''.join([symbol for symbol in node if symbol.isdigit()])
		
	node_names_digit_octet.sort()
	node_names_digit_octet = [str(i) for i in node_names_digit_octet]

	#creating lists from collected digits. one-digit names and two-digit names require different handling	
	two_digit_name = False
	for i in node_names_digit_octet:
		if len(i) > 1:
			two_digit_name = True
			break
		else:
			continue
	
	if not two_digit_name:
		octet = '0', ''.join([str(i) for i in node_names_digit_octet]) 
	else:
		octet = node_names_digit_octet[0], node_names_digit_octet[1]
		
	#config generation	
	for node in remember.keys():
		
		#mpls
		if mpls == 'L' and not checkmpls[node]:
			result_config[node].append('mpls ip\n!\nmpls ldp router-id Loopback0 force\n!')
		if mpls == 'R' and not checkmpls[node]:
			result_config[node].append('mpls traffic-eng tunnels\n!')	
	
		#loopback config
		if not checkloopback[node]:
			result_config[node].append('interface Loopback0\n ip address {}.{}.{}.{} 255.255.255.255'.format(*[node_names_digit[node] for i in range(4)]))
			checkloopback[node] = True
			if routing == 'I':
				result_config[node].append(' ip router isis 1')
			elif routing == 'O':
				result_config[node].append(' ip ospf 1 area 0')
			result_config[node].append('!')			
	
		#routing process configuration
		if routing == 'I' and not checkrouting[node]:
			result_config[node].append('router isis 1\n net 10.0000.0000.00{:02}.00\n metric-style wide'.format(int(node_names_digit[node])))
			if mpls == 'R':
				result_config[node].append(' mpls traffic-eng router-id Loopback0\n mpls traffic-eng level-1')
			result_config[node].append('!')
			checkrouting[node] = True
		elif routing == 'O' and not checkrouting[node]:
			result_config[node].append('router ospf 1\n router-id {}.{}.{}.{}'.format(*[node_names_digit[node] for i in range(4)]))			
			checkrouting[node] = True		
			if mpls == 'R':
				result_config[node].append(' mpls traffic-eng area 0\n mpls traffic-eng router-id Loopback0')					
			result_config[node].append('!')
		
		#interface configuration		
		result_config[node].append('interface {}\n ip address 10.{}.{}.{} 255.255.255.0\n no shutdown'.format(remember[node][0], octet[0], octet[1], node_names_digit[node]))			
		if routing == 'I':
			result_config[node].append(' ip router isis 1')
		elif routing == 'O':
			result_config[node].append(' ip ospf 1 area 0')
		if mpls == 'L':
			result_config[node].append(' mpls ip')
			checkmpls[node] = True
		elif mpls == 'R':
			result_config[node].append(' mpls traffic-eng tunnels\n ip rsvp bandwidth {}'.format(rsvp_bw))
			checkmpls[node] = True
		result_config[node].append('!')

#printing & writing		
if output == 'P':
	for node in node_attributes:
		print('\nhostname {}\n!'.format(node))
		for value in result_config[node]:
			print(value)
elif output == 'F':
	with open(file_name, 'w') as f:
		for node in node_attributes:
			f.write('\nhostname {}\n!'.format(node))
			for value in result_config[node]:	
				f.write(value + '\n')
		
