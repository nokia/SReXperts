import argparse

from pygnmi.client import gNMIclient
from tabulate import tabulate

parser = argparse.ArgumentParser(
    prog="get_interfaces.py",
    description="Displays a list of interfaces configured under a mac-vrf",
)
parser.add_argument("host")
parser.add_argument("username")
parser.add_argument("password")
parser.add_argument("mac_vrf")

args = parser.parse_args()

with gNMIclient(
    target=(args.host, 57400), username=args.username, password=args.password
) as gc:
    print(
        "Retrieving interfaces for mac-vrf '{}' on node '{}'".format(
            args.mac_vrf, args.host
        )
    )
    interfaces = gc.get(
        path=["/network-instance[name={}]/interface".format(args.mac_vrf)]
    )["notification"][0]["update"][0]["val"]["interface"]
    irb_name = None
    ifs = []
    for intf in interfaces:
        if intf["name"].startswith("irb"):
            irb_name = intf["name"]
        else:
            ifs.append([intf["name"], intf["oper-state"]])

    print("\nInterfaces configured under MAC-VRF '{}':\n".format(args.mac_vrf))
    print(tabulate(ifs, headers=["Name", "Status"]))
    if irb_name is not None:
        print(
            "*Note: this MAC-VRF is routed through IRB interface '{}'".format(irb_name)
        )
    print("\n")
