import argparse

from pygnmi.client import gNMIclient

parser = argparse.ArgumentParser(prog='get_hostname.py', description='Gets the host name for an SRLinux router')
parser.add_argument('host')
parser.add_argument('username')
parser.add_argument('password')

args = parser.parse_args()
with gNMIclient(target=(args.host, 57400), username=args.username, password=args.password) as gc:
    print("Retrieving hostname for node '{}'".format(args.host))
    hostname = gc.get(path=["/system/name/host-name"])['notification'][0]['update'][0]['val']
    print("Hostname of node {} is '{}'".format(args.host, hostname))