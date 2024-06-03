# Leveraging Python with PyGNMI to obtain structure data from a node

| Item              | Details                                                            |
| ----------------- | ------------------------------------------------------------------ |
| Short Description | Using pyGNMI to perform configuration management tasks on SR Linux |
| Skill Level       | Intermediate                                                       |
| Tools Used        | SR Linux, pyGNMI                                                   |

Network operators are increasingly focussing on leveraging automation to monitor, manage, and configure network elements. As interactions with routers are increasingly done by machines instead of humans, the [GNMI](https://documentation.nokia.com/srlinux/24-3/books/system-mgmt/gnmi.html) programmable interface has become a more attractive alternative to CLIs to let automation agents interact with them.

The motivation for this is obvious: by returning operational data in a well-structured format like [JSON](https://www.json.org/json-en.html), screen scraping - taking into account things like terminal width - has become a thing of the past.

## Objective

In this lab, you will use the [PyGNMI](https://pypi.org/project/pygnmi/) library for Python, which allows the user to automate data retrieval and configuration tasks using Python code. The scope of this lab is limited to data retrieval.

## Accessing a lab node

We will be executing Python scripts from the cloud instance (where you're logging in to) to any of the leafs: I'll be using `clab-srexperts-leaf21` for the examples. While it's not necessary to log into the nodes itself, it might be useful to explore the running configuration and the state trees. You can log in by using the DNS name of the container.

```
ssh admin@clab-srexperts-leaf21
```

## Documentation resources

Below are some resources you might find interesting:

- [pyGNMI](https://github.com/akarneliuk/pygnmi): a python package to work with gNMI targets
- [gNMIc](https://gnmic.openconfig.net/): a command-line utility for interacting with the GNMI interface
- [SR Linux YANG browser](https://yang.srlinux.dev/v24.3.2): use this to look for gNMI paths
- [Nokia GNMI Documentation](https://documentation.nokia.com/srlinux/24-3/books/system-mgmt/gnmi.html)

## Setting up a Python virtual environment

To get you up and running, I've provided some initial steps to get started. Ensure that your python environment is active before you run your commands!

```
❯ mkdir ~/pygnmi
❯ cd ~/pygnmi
❯ python3 -m venv venv
❯ ls
venv
❯ source venv/bin/activate
❯ python --version
Python 3.10.12
❯ python -m pip install pygnmi
Collecting pygnmi
  Using cached pygnmi-0.8.14.tar.gz (32 kB)
...
❯ python <your-python-file.py> arg1 arg2
```

## Exercise 0

This first exercise is an example: the script `get_timezone.py` located at the bottom of this document, shows an example on how to retrieve the current timezone of the SR Linux router. Below is an example execution

```bash
❯ python get_timezone.py --help
usage: get_timezone.py [-h] host

Gets the timezone for an SR Linux router

positional arguments:
  host
  username
  password

optional arguments:
  -h, --help  show this help message and exit
  
❯ python get_timezone.py clab-srexperts-leaf21 <username> <password>
Retrieving timezone for node 'clab-srexperts-leaf21'
Configured timezone on host clab-srexperts-leaf21 is 'UTC'
```

## Exercise 1

With the example from exercise 0, you are now ready to start messing around yourself. Note that while the exercises below are pre-made and become increasingly more difficult, there is no obligation for you to stick to the script!

> Exercise 1: retrieve the hostname of any SR Linux box in the network.

### Example execution

```bash
❯ python get_hostname.py --help
usage: get_hostname.py [-h] host

Gets the host name for an SR Linux router

positional arguments:
  host
  username
  password

optional arguments:
  -h, --help  show this help message and exit

❯ python get_hostname.py clab-srexperts-leaf21 <username> <password>
Retrieving hostname for node 'clab-srexperts-leaf21'
Hostname of node clab-srexperts-leaf21 is 'leaf21'
```

## Exercise 2

That was easy enough! Now for something more difficult: if you connect to leaf21, you'll notice there are a couple MAC-VRF network-instances. MAC-VRFs are layer-2 services that connect downlink ports to eachother, and optionally route it towards an IP-VRF (via an irb interface).

> Exercise 2: create a script that - given the name of a specific MAC-VRF - displays a list of interfaces connected to it.

*Note: IRB interfaces are used to connect a MAC-VRF to an IP-VRF. Make sure that the interfaces returned by this script do not include the IRB interface. Instead, a message should be displayed informing the user that this MAC-VRF is a routed layer 2 service*

### Example execution

```bash
❯ python get_interfaces.py --help
usage: get_interfaces.py [-h] host mac_vrf

Displays a list of interfaces configured under a mac-vrf

positional arguments:
  host
  mac_vrf
  username
  password

optional arguments:
  -h, --help  show this help message and exit

❯ python get_interfaces.py clab-srexperts-leaf21 macvrf102 <username> <password>
Retrieving interfaces for mac-vrf 'macvrf102' on node 'clab-srexperts-leaf21'

Interfaces configured under MAC-VRF 'macvrf102':

Name              Status
----------------  --------
ethernet-1/1.102  up
*Note: this MAC-VRF is routed through IRB interface 'irb0.102'
```

## Exercise 3

Now for the final exercise: extend the script from exercise 2 to also include information that is not found in the MAC-VRF directly: this will require one or more additional calls, per interface:

> Exercise 3: extend the script from exercise 2 with the following functionality:<br/>
>
> 1) Print the EVI of the network-instance, and the VNI of the tunnel-interface that is used to set up VXLAN transport tunnels for the MAC-VRF. It is expected that these numbers are the same.
> 2) If there is an IRB interface, display the name of the IP-VRF which is connected to this MAC-VRF, along with the IP address configured on the IRB interface. Remember that a MAC-VRF is connected to an IP-VRF by specifying the same IRB subinterface in both the MAC-VRF and the IP-VRF
> 3) For each interface, also display the associated VLAN

### Example execution

```bash
❯ python get_interfaces_improved.py --help
usage: get_interfaces.py [-h] host mac_vrf

Displays a list of interfaces configured under a mac-vrf

positional arguments:
  host
  mac_vrf
  username
  password

optional arguments:
  -h, --help  show this help message and exit

❯ python get_interfaces_improved.py clab-srexperts-leaf21 macvrf102 <username> <password>
General information about MAC-VRF 'macvrf102'
- EVI: 102
- VNI: 102

This interface is connected to IP-VRF 'ipvrf202' with IP '192.168.41.1/24'

Interfaces configured under MAC-VRF 'macvrf102':

Interface       Sub-interface    VLAN  Status
------------  ---------------  ------  --------
ethernet-1/1              102     102  up
```

## What's next

Feel free to think of your own automation ideas, or take a crack at pushing config with PyGNMI instead! And of course, don't forget to try out the other labs part of this hackathon.

## Annex A

`get_timezone.py`

```python
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
```
