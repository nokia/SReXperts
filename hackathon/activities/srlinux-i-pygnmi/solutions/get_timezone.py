import argparse

from pygnmi.client import gNMIclient

parser = argparse.ArgumentParser(prog='get_timezone.py', description='Gets the timezone for an SR Linux router')
parser.add_argument('host')
parser.add_argument('username')
parser.add_argument('password')

args = parser.parse_args()
with gNMIclient(target=(args.host, 57400), username=args.username, password=args.password) as gc:
    print("Retrieving timezone for node '{}'".format(args.host))
    timezone = gc.get(path=["/system/clock/timezone"])['notification'][0]['update'][0]['val']
    print("Configured timezone on host {} is '{}'".format(args.host, timezone))