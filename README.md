# EVE-NG-config-generator

This script creates a basic configuration for Cisco (IOS only right now) routers basing on EVE-NG topology map file (.unl file which you can export from every lab).

I use EVE-NG a lot and there's always a bunch of little things you need to configure on every node to get things started, like hostnames, interfaces addresses, routing protocols etc.
I always use similar naming and addressing scheme in every lab, so I thought it would be nice to automate this stuff a little.

This script will:
- configure hostnames;
- configure interfaces addresses (including loopback) and enable them;
- configure routing protocol (IS-IS/OSPF at the moment);
- configure MPLS (LDP/RSVP).

Configuration will be either printed or saved to the file.

This script assumes you use names like R1, R13 etc for your nodes and will generate ip addresses based on the digits presented in the name. For instance, nodes R1 and R2 connected to each other will have addresses 10.0.12.1/24 and 10.0.12.2/24 correspondingly.
Nodes that have two digits in their names, like R42 and R66, will be assigned 10.42.66.42/24 and 10.42.66.66/24.

That's an example of what this script will return for a topology like this one:

![alt text](https://raw.githubusercontent.com/grindelwaldus/EVE-NG-config-generator/master/topo_pic.jpg)

```
rootx@python_vm:~$ ./eve_config_gen.py test_topology.unl 
Would you like to enable routing? Press O for OSPF, I for ISIS or N for none.I
Do you need to enable MPLS? Press R for RSVP, L for LDP or N for none.R
Would you like to save configuration to separate file or you would rather have it printed? Press F for saving, P for printing.P

hostname R1
!
mpls traffic-eng tunnels
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
 ip router isis 1
!
router isis 1
 net 10.0000.0000.0001.00
 metric-style wide
 mpls traffic-eng router-id Loopback0
 mpls traffic-eng level-1
!
interface e0/0
 ip address 10.0.12.1 255.255.255.0
 no shutdown
 ip router isis 1
 mpls traffic-eng tunnels
 ip rsvp bandwidth 10000
!

hostname R2
!
mpls traffic-eng tunnels
!
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
 ip router isis 1
!
router isis 1
 net 10.0000.0000.0002.00
 metric-style wide
 mpls traffic-eng router-id Loopback0
 mpls traffic-eng level-1
!
interface e0/2
 ip address 10.0.23.2 255.255.255.0
 no shutdown
 ip router isis 1
 mpls traffic-eng tunnels
 ip rsvp bandwidth 10000
!
interface e0/3
 ip address 10.0.24.2 255.255.255.0
 no shutdown
 ip router isis 1
 mpls traffic-eng tunnels
 ip rsvp bandwidth 10000
!
interface e0/1
 ip address 10.0.12.2 255.255.255.0
 no shutdown
 ip router isis 1
 mpls traffic-eng tunnels
 ip rsvp bandwidth 10000
!

hostname R3
!
mpls traffic-eng tunnels
!
interface Loopback0
 ip address 3.3.3.3 255.255.255.255
 ip router isis 1
!
router isis 1
 net 10.0000.0000.0003.00
 metric-style wide
 mpls traffic-eng router-id Loopback0
 mpls traffic-eng level-1
!
interface e0/0
 ip address 10.0.23.3 255.255.255.0
 no shutdown
 ip router isis 1
 mpls traffic-eng tunnels
 ip rsvp bandwidth 10000
!

hostname R4
!
mpls traffic-eng tunnels
!
interface Loopback0
 ip address 4.4.4.4 255.255.255.255
 ip router isis 1
!
router isis 1
 net 10.0000.0000.0004.00
 metric-style wide
 mpls traffic-eng router-id Loopback0
 mpls traffic-eng level-1
!
interface e0/0
 ip address 10.0.24.4 255.255.255.0
 no shutdown
 ip router isis 1
 mpls traffic-eng tunnels
 ip rsvp bandwidth 10000
!
```
