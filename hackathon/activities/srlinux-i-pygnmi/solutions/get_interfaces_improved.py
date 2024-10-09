import argparse

from pygnmi.client import gNMIclient
from tabulate import tabulate

parser = argparse.ArgumentParser(prog='get_interfaces.py', description='Displays a list of interfaces configured under a mac-vrf')
parser.add_argument('host')
parser.add_argument('username')
parser.add_argument('password')
parser.add_argument('mac_vrf')

args = parser.parse_args()

def get_evi(gc):
    return gc.get(path=["/network-instance[name={}]/protocols/bgp-evpn/bgp-instance[id=1]/evi".format(args.mac_vrf)])['notification'][0]['update'][0]['val']

def get_vni(gc):
    vxlan_if = gc.get(path=["/network-instance[name={}]/vxlan-interface".format(args.mac_vrf)])['notification'][0]['update'][0]['val']['vxlan-interface'][0]
    (name, subintf) = vxlan_if['name'].split(".")
    return gc.get(path=["/tunnel-interface[name={}]/vxlan-interface[index={}]/ingress/vni".format(name, subintf)])['notification'][0]['update'][0]['val']

def get_connected_ipvrf(gc):
    interfaces = gc.get(path=["/network-instance[name={}]/interface".format(args.mac_vrf)])['notification'][0]['update'][0]['val']['interface']
    irb = None
    for intf in interfaces:
        if intf['name'].startswith('irb'):
            irb = intf
            break

    connected_ipvrf = None

    ipvrfs = gc.get(path=["/network-instance[name=*]/type"])['notification'][0]['update'][0]['val']['srl_nokia-network-instance:network-instance']
    for ipvrf in ipvrfs:
        if ipvrf['type'].endswith('ip-vrf'):
            ipvrf_interfaces = gc.get(path=["/network-instance[name={}]/interface".format(ipvrf['name'])])['notification'][0]['update'][0]['val']['interface']
            for ipvrf_interface in ipvrf_interfaces:
                if ipvrf_interface['name'] == irb['name']:
                    connected_ipvrf = ipvrf
                    break

    return connected_ipvrf

def get_irb_ip(gc):
    interfaces = gc.get(path=["/network-instance[name={}]/interface".format(args.mac_vrf)])['notification'][0]['update'][0]['val']['interface']
    irb = None
    for intf in interfaces:
        if intf['name'].startswith('irb'):
            irb = intf
            break

    (irb_name, irb_subint) = irb['name'].split(".")

    ip = gc.get(path=["/interface[name={}]/subinterface[index={}]/ipv4/address".format(irb_name, irb_subint)])['notification'][0]['update'][0]['val']['address'][0]
    return ip['ip-prefix']

def get_interfaces(gc):
    interfaces = gc.get(path=["/network-instance[name={}]/interface".format(args.mac_vrf)])['notification'][0]['update'][0]['val']['interface']
    ifs = []
    for intf in interfaces:
        if not intf['name'].startswith('irb'):
            (intf_name, intf_subint) = intf['name'].split(".")
            vlan = gc.get(path=["/interface[name={}]/subinterface[index={}]/vlan/encap/single-tagged".format(intf_name, intf_subint)])['notification'][0]['update'][0]['val']
            ifs.append([intf_name, intf_subint, vlan['vlan-id'], intf['oper-state']])
    return ifs

with gNMIclient(target=(args.host, 57400), username=args.username, password=args.password) as gc:
    print("General information about MAC-VRF '{}'".format(args.mac_vrf))
    print("- EVI: {}".format(get_evi(gc)))
    print("- VNI: {}\n".format(get_vni(gc)))

    print("This interface is connected to IP-VRF '{}' with IP '{}'\n".format(get_connected_ipvrf(gc)['name'], get_irb_ip(gc)))

    interfaces = get_interfaces(gc)
    print("Interfaces configured under MAC-VRF '{}':\n".format(args.mac_vrf))
    print(tabulate(interfaces, headers=["Interface", "Sub-interface", "VLAN", "Status"]))
    print()