---
tags:
  - SR OS
  - pySROS
  - Python
  - MD-CLI
  - alias
  - pyexec
  - show commands
  - MicroPython
---

# Overriding built-in `show` commands with aliases


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Overriding built-in `show` commands with aliases                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Activity ID**             | 06                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Short Description**       | In some situations the output of `show` commands may not immediately display the desired information. Possible causes for this include the omission of the `no-more` parameter combined with the sheer amount of output, using too generic a command for the desired outcome or the target information not being at the start of the command output. Whatever the reason may be, in model-driven SR OS there is no reason to suffer this inconvenience as we can change these behaviors at will.                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/), [Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/MD-CLI_User_Guide_25.3.R1.pdf), [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html), [Python programming language](https://www.python.org) and [MicroPython](https://micropython.org/), [SR OS YANG explorer](https://yang.labctl.net/yang/SROS/25.3.R1/t)                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Topology Nodes**          | :material-router: PE1                                                                                                                                                                                                                                                                                                                                                                            |
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/MD-CLI_User_Guide_25.3.R1.pdf)<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/System_Management_Guide_25.3.R1.pdf)<br/>[pySROS user documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)<br/>[pySROS GitHub](https://github.com/nokia/pysros) (check the examples directory)<br/>[MicroPython](https://docs.micropython.org/en/latest/) |


In some situations the output of `show` commands may not immediately display the wanted information. Possible causes for this include the omission of the `no-more` parameter combined with the sheer amount of output, using too generic a command for the desired outcome or the target information not being at the start of the command output. Whatever the reason may be, in model-driven SR OS there is no reason to suffer this inconvenience as we can change these behaviors at will. In this activity you will zero in on the output of the command that displays a brief overview of BGP neighborship information:

`show router bgp summary`

When using this command the desired output is usually the table at the end, and it requires skipping through some output before that result is visible.

## Objective

1. Create a Python development environment and connect to the target model-driven SR OS router
2. Browse the model-driven SR OS state and YANG model to find where BGP information can be found.
3. Create a solution using pySROS that retrieves this information and displays it in an SR OS style table.
4. Override the existing `show router bgp summary` command with your version using an alias.

Only :material-router: PE1 will be configured in this activity and there is no need to roll back those changes at the end of the exercise.

## Technology explanation

To tackle this activity you will need to use the Python programming language pre-installed on all SR OS routers, installed locally on your workstation or installed on your group's Linux server instance.

A basic level of Python proficiency is assumed for this activity.

The key technologies this activity might utilize include:

### MicroPython

Otherwise known as uPython, MicroPython is a lean and efficient implementation of the Python 3 programming language that includes a small subset of the Python standard libraries and is optimized to run on microcontrollers and in constrained environments. Modern releases of model-driven SR OS provide a Python environment using the MicroPython interpreter, based on Python 3.4.


### MD-CLI pyexec command

The SR OS MD-CLI `pyexec` command allows operators to run a Python 3 application on the SR OS node by providing a filename as input or the name of a python-script configured in the MD-CLI.

Example uses: ```pyexec cf3:/myscript.py``` or ```pyexec my-script-name```

The [SR OS system management guide](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exgst4k) provides more information on it's use.


### MD-CLI alias command

SR OS MD-CLI command aliases provide a way for an operator to customize the user-experience of an SR OS node by renaming commands, creating shortcut aliases to existing commands or integrating custom developed commands directly into the MD-CLI with context sensitive help, auto-completion and the other user interface features operators love about SR OS.

The [MD-CLI command reference guide](https://documentation.nokia.com/sr/25-3/7750-sr/books/md-cli-command-reference/environment_0.html#d67300) and the [SR OS system management guide](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exj5x8z) provide more information.


### Developing Python scripts
Python applications can be written in the form of a file or a combination of several files and are generally structured as reusable modules or packages. For use within model-driven SR OS, the possibilities narrow slightly as scripts exist as a single file and the modules that can be imported are tuned for and determined by the system. The pySROS library can be used from a remote system and pointed at a model-driven SR OS node and it can also be used from within model-driven SR OS.

The behavior for both environments is designed to be similar. This allows development efforts to take place on a system like your personal laptop or a shared scripting server, rather than needing to be done on the node directly.


### Model-driven SR OS and the MD-CLI
As the term "model-driven" suggests, a model-driven Network Operating System (NOS) such as SR OS has one or more data models at its core. These data models compile together to provide the schema for the system. These data models are written using a language called YANG and, in the case of SR OS, are available [online](https://github.com/nokia/7x50_YangModels/blob/master/).

In this activity, you will have to use the MD-CLI, the online SR OS YANG explorer (the online version of the YANG model) or some level of pre-existing knowledge to retrieve information related to BGP neighbors in SR OS. The most convenient option is likely the MD-CLI itself because it is interactive and offers several tools that aid users when creating automated solutions for SR OS. Some of the tools it offers are:

- `pwc` shows in a number of formats what path you are currently in
- `tree` can show you what values would be valid further down the tree, in case you are looking for a certain attribute
- `compare`, when given the optional parameters `summary` and `netconf-rpc`, gives back a NETCONF `edit-config` RPC that can be reused by a NETCONF client.

The [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html) contains more information on how it can help operators.

Configuration changes in model-driven SR OS are first done to the candidate datastore and must then be entered into the running datastore using a `commit` operation. Needed to create the alias, you will be able to enter a candidate session using `edit-config private`. After atomically merging your changes using `commit` you can return to the operational mode using `quit-config`. More information on this topic is available in [the documentation](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/edit-configuration.html#unique_813655187).

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Create a Python development environment

If you are able to, we recommend completing this activity using your local machine as a development environment. This task helps you prepare for that. Should you be unable to, or if you want to move on quickly, the Hackathon VM you have been assigned comes pre-installed with the necessary libraries for this activity. If you decide to use the Hackathon VM or the SR OS machine for development you can skip the remainder of this task.

!!! warning
    As there is no way to enter into an interactive Read-Eval-Print-Loop (REPL) within SR OS, if you go that route, some of the example solutions may not be applicable and would require the use of script files and `pyexec` instead.

#### Virtual environment

It is good practice when programming in Python to work in a virtual environment.  A virtual environment can be created in a number of ways, provided are two options (pick one).

/// details | Create a virtual environment using uv

Create the virtual environment using the `uv` command.

/// tab | cmd
``` bash
uv venv
```

///
/// tab | expected output
``` bash
Using CPython 3.11.11
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
```
///

It is important to make sure that you are using this newly created virtual environment.  To do this use the Linux `source` command.

``` bash
source .venv/bin/activate
```

You can now install pySROS.

///

/// details | Create a virtual environment using venv

A virtual environment can be created using the builtin `venv` Python module.  Create the virtual environment using the following command.

/// tab | cmd
``` bash
python -m venv .venv
```
///

It is important to make sure that you are using this newly created virtual environment.  To do this use the Linux `source` command.

``` bash
source .venv/bin/activate
```

You can now install pySROS.

///

#### Install pySROS

When developing using pySROS you can develop on your personal device, on your group's Linux server or directly on the node. The choice is yours.

*If you are developing on your group's Linux server or on the SR OS devices directly, pySROS is already pre-installed so you can skip this task.*

If you are developing locally, pySROS should be installed/upgraded if it is not already present on your device. There are three methods that I will describe here: using the `uv` Python package and project manager, using the `pip` Python package manager and installing from the source code.

/// details | Installing pySROS using uv

If you have the `uv` Python package and project manager installed then follow these instructions.  If you do not have the `uv` Python package and project manager installed then please try to install using pip (it is more commonly used).

Ensure you are working in your virtual environment (created with `uv venv`) by using the `source` Linux command.

``` bash
source .venv/bin/activate
```

Next install the pySROS package from PyPI into your virtual environment.

/// tab | cmd
``` bash
uv pip install --upgrade pysros
```

///
/// tab | expected output
``` bash
Resolved 9 packages in 793ms
      Built ncclient==0.6.19
Prepared 9 packages in 2.96s
Installed 9 packages in 17ms
 + bcrypt==4.3.0
 + cffi==1.17.1
 + cryptography==44.0.2
 + lxml==5.3.1
 + ncclient==0.6.19
 + paramiko==3.5.1
 + pycparser==2.22
 + pynacl==1.5.0
 + pysros==25.3.1
```
///


pySROS is now installed inside your virtual environment.

///

/// details | Installing pySROS using pip

Ensure you are working in your virtual environment by using the `source` Linux command.

``` bash
source .venv/bin/activate
```

Now ensure that you have the `pip` package manager installed by running the command.

/// tab | cmd
``` bash
python -m ensurepip
```
///
/// tab | possible outcome on Debian/Ubuntu
``` bash
ensurepip is disabled in Debian/Ubuntu for the system python.

Python modules for the system python are usually handled by dpkg and apt-get.

    apt-get install python-<module name>

Install the python-pip package to use pip itself.  Using pip together
with the system python might have unexpected results for any system installed
module, so use it on your own risk, or make sure to only use it in virtual
environments.
```
///

If you receive the message shown in the "possible outcome on Debian/Ubuntu" tab then run the following command to install `pip`.

``` bash
sudo apt-get install -y python-pip
```

Next install the pySROS package from PyPI into your virtual environment.

/// tab | cmd
``` bash
pip install --upgrade pysros
```
///
/// tab | expected output
``` bash
Collecting pysros
  Using cached pysros-25.3.1-py3-none-any.whl (85 kB)
Collecting ncclient~=0.6.12
  Using cached ncclient-0.6.19.tar.gz (112 kB)
  Preparing metadata (setup.py) ... done
Collecting lxml~=5.3.0
  Using cached lxml-5.3.2-cp311-cp311-manylinux_2_28_x86_64.whl (5.0 MB)
Collecting paramiko>=1.15.0
  Using cached paramiko-3.5.1-py3-none-any.whl (227 kB)
Collecting bcrypt>=3.2
  Using cached bcrypt-4.3.0-cp39-abi3-manylinux_2_34_x86_64.whl (284 kB)
Collecting cryptography>=3.3
  Using cached cryptography-44.0.2-cp39-abi3-manylinux_2_34_x86_64.whl (4.2 MB)
Collecting pynacl>=1.5
  Using cached PyNaCl-1.5.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl (856 kB)
Collecting cffi>=1.12
  Using cached cffi-1.17.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (467 kB)
Collecting pycparser
  Using cached pycparser-2.22-py3-none-any.whl (117 kB)
Installing collected packages: pycparser, lxml, bcrypt, cffi, pynacl, cryptography, paramiko, ncclient, pysros
  DEPRECATION: ncclient is being installed using the legacy 'setup.py install' method, because it does not have a 'pyproject.toml' and the 'wheel' package is not installed. pip 23.1 will enforce this behavior change. A possible replacement is to enable the '--use-pep517' option. Discussion can be found at https://github.com/pypa/pip/issues/8559
  Running setup.py install for ncclient ... done
Successfully installed bcrypt-4.3.0 cffi-1.17.1 cryptography-44.0.2 lxml-5.3.2 ncclient-0.6.19 paramiko-3.5.1 pycparser-2.22 pynacl-1.5.0 pysros-25.3.1
```
///

///

/// details | Installing pySROS from the source code

These instructions assume you have the `git` source code management tool installed.

Use `git` to clone the source code repository from GitHub (where the pySROS source code is published).

/// tab | cmd
``` bash
git clone https://github.com/nokia/pysros
```
///
/// tab | expected output
``` bash
Cloning into 'pysros'...
remote: Enumerating objects: 1000, done.
remote: Counting objects: 100% (121/121), done.
remote: Compressing objects: 100% (83/83), done.
remote: Total 1000 (delta 62), reused 76 (delta 36), pack-reused 879 (from 1)
Receiving objects: 100% (1000/1000), 1.04 MiB | 5.75 MiB/s, done.
Resolving deltas: 100% (729/729), done.
```
///

Now ensure that you have the `pip` package manager installed by running the command.

/// tab | cmd
``` bash
python -m ensurepip
```
///
/// tab | possible outcome on Debian/Ubuntu
``` bash
ensurepip is disabled in Debian/Ubuntu for the system python.

Python modules for the system python are usually handled by dpkg and apt-get.

    apt-get install python-<module name>

Install the python-pip package to use pip itself.  Using pip together
with the system python might have unexpected results for any system installed
module, so use it on your own risk, or make sure to only use it in virtual
environments.
```
///

If you receive the message shown in the "possible outcome on Debian/Ubuntu" tab then run the following command to install `pip`.

``` bash
sudo apt-get install -y python-pip
```

Next install the pySROS package from the source code you downloaded.

/// tab | cmd
``` bash
cd pysros
pip install .
```
///
/// tab | expected output
``` bash
Processing /home/nokia/jgctest/pysros
Collecting ncclient~=0.6.12
  Using cached ncclient-0.6.19.tar.gz (112 kB)
Collecting lxml~=5.3.0
  Downloading lxml-5.3.1-cp310-cp310-manylinux_2_28_x86_64.whl (5.2 MB)
     |████████████████████████████████| 5.2 MB 19.2 MB/s
Collecting paramiko>=1.15.0
  Downloading paramiko-3.5.1-py3-none-any.whl (227 kB)
     |████████████████████████████████| 227 kB 89.9 MB/s
Collecting pynacl>=1.5
  Using cached PyNaCl-1.5.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl (856 kB)
Collecting cryptography>=3.3
  Downloading cryptography-44.0.2-cp39-abi3-manylinux_2_28_x86_64.whl (4.2 MB)
     |████████████████████████████████| 4.2 MB 60.4 MB/s
Collecting bcrypt>=3.2
  Downloading bcrypt-4.3.0-cp39-abi3-manylinux_2_28_x86_64.whl (284 kB)
     |████████████████████████████████| 284 kB 61.7 MB/s
Collecting cffi>=1.12
  Downloading cffi-1.17.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (446 kB)
     |████████████████████████████████| 446 kB 86.2 MB/s
Collecting pycparser
  Using cached pycparser-2.22-py3-none-any.whl (117 kB)
Using legacy 'setup.py install' for pysros, since package 'wheel' is not installed.
Using legacy 'setup.py install' for ncclient, since package 'wheel' is not installed.
Installing collected packages: pycparser, cffi, pynacl, cryptography, bcrypt, paramiko, lxml, ncclient, pysros
    Running setup.py install for ncclient ... done
    Running setup.py install for pysros ... done
Successfully installed bcrypt-4.3.0 cffi-1.17.1 cryptography-44.0.2 lxml-5.3.1 ncclient-0.6.19 paramiko-3.5.1 pycparser-2.22 pynacl-1.5.0 pysros-25.3.1
```
///

///


### From Output to Opportunity

To begin, we need to find out what it is we are actually trying to solve. With an objective in mind, we will try to find an approach to complete that objective in this task. The target is overriding the `show router bgp summary` command in such a way that the information at the start of the command is hidden and the convenient table is shown as output immediately.

#### The existing situation

Run the command on `PE1` by logging in to the node using SSH either from the provided Hackathon VM to the `clab-srexperts-pe1` hostname or from your own machine to your assigned Hackathon instance's hostname, `PE1`'s port 22 is exposed as port 50021. Use the credentials provided to you.

/// tab | Expected output of `show router bgp summary`
```hl_lines="2 62"
[/]
A:admin@g23-pe1# show router bgp summary
===============================================================================
 BGP Router ID:10.46.23.21      AS:65000       Local AS:65000
===============================================================================
BGP Admin State         : Up          BGP Oper State              : Up
Total Peer Groups       : 6           Total Peers                 : 8
Total VPN Peer Groups   : 0           Total VPN Peers             : 0
Current Internal Groups : 5           Max Internal Groups         : 5
Total BGP Paths         : 283         Total Path Memory           : 107892

Total IPv4 Remote Rts   : 102         Total IPv4 Rem. Active Rts  : 24
Total IPv6 Remote Rts   : 108         Total IPv6 Rem. Active Rts  : 18
Total IPv4 Backup Rts   : 0           Total IPv6 Backup Rts       : 0
Total LblIpv4 Rem Rts   : 0           Total LblIpv4 Rem. Act Rts  : 0
Total LblIpv6 Rem Rts   : 0           Total LblIpv6 Rem. Act Rts  : 0
Total LblIpv4 Bkp Rts   : 0           Total LblIpv6 Bkp Rts       : 0
Total Suppressed Rts     : 0           Total Hist. Rts             : 0
Total Decay Rts         : 0

Total VPN-IPv4 Rem. Rts : 22          Total VPN-IPv4 Rem. Act. Rts: 7
Total VPN-IPv6 Rem. Rts : 22          Total VPN-IPv6 Rem. Act. Rts: 7
Total VPN-IPv4 Bkup Rts : 0           Total VPN-IPv6 Bkup Rts     : 0
Total VPN Local Rts     : 16          Total VPN Supp. Rts         : 0
Total VPN Hist. Rts     : 0           Total VPN Decay Rts         : 0

Total MVPN-IPv4 Rem Rts : 0           Total MVPN-IPv4 Rem Act Rts : 0
Total MVPN-IPv6 Rem Rts : 0           Total MVPN-IPv6 Rem Act Rts : 0
Total MDT-SAFI Rem Rts  : 0           Total MDT-SAFI Rem Act Rts  : 0
Total McIPv4 Remote Rts : 0           Total McIPv4 Rem. Active Rts: 0
Total McIPv6 Remote Rts : 0           Total McIPv6 Rem. Active Rts: 0
Total McVpnIPv4 Rem Rts : 0           Total McVpnIPv4 Rem Act Rts : 0
Total McVpnIPv6 Rem Rts : 0           Total McVpnIPv6 Rem Act Rts : 0

Total EVPN Rem Rts      : 145         Total EVPN Rem Act Rts      : 4
Total L2-VPN Rem. Rts   : 0           Total L2VPN Rem. Act. Rts   : 0
Total MSPW Rem Rts      : 0           Total MSPW Rem Act Rts      : 0
Total RouteTgt Rem Rts  : 0           Total RouteTgt Rem Act Rts  : 0
Total FlowIpv4 Rem Rts  : 0           Total FlowIpv4 Rem Act Rts  : 0
Total FlowIpv6 Rem Rts  : 0           Total FlowIpv6 Rem Act Rts  : 0
Total FlowVpnv4 Rem Rts : 0           Total FlowVpnv4 Rem Act Rts : 0
Total FlowVpnv6 Rem Rts : 0           Total FlowVpnv6 Rem Act Rts : 0
Total Link State Rem Rts: 0           Total Link State Rem Act Rts: 0
Total SrPlcyIpv4 Rem Rts: 0           Total SrPlcyIpv4 Rem Act Rts: 0
Total SrPlcyIpv6 Rem Rts: 0           Total SrPlcyIpv6 Rem Act Rts: 0

===============================================================================
BGP Summary
===============================================================================
Legend : D - Dynamic Neighbor
===============================================================================
Neighbor
Description
                   AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                      PktSent OutQ
-------------------------------------------------------------------------------
10.64.51.2
                64699    5621    0 01d22h48m 0/0/0 (IPv4)
                         5621    0
10.64.54.0
                64599    5611    0 01d22h44m 0/0/0 (IPv4)
--(more)--(74%)--(lines 1-59/85)--
```
///
/// tab | Expected output of `show router bgp summary | no-more`
```hl_lines="2"
[/]
A:admin@g23-pe1# show router bgp summary | no-more
===============================================================================
 BGP Router ID:10.46.23.21      AS:65000       Local AS:65000
===============================================================================
BGP Admin State         : Up          BGP Oper State              : Up
Total Peer Groups       : 6           Total Peers                 : 8
Total VPN Peer Groups   : 0           Total VPN Peers             : 0
Current Internal Groups : 5           Max Internal Groups         : 5
Total BGP Paths         : 282         Total Path Memory           : 107504

Total IPv4 Remote Rts   : 102         Total IPv4 Rem. Active Rts  : 24
Total IPv6 Remote Rts   : 108         Total IPv6 Rem. Active Rts  : 18
Total IPv4 Backup Rts   : 0           Total IPv6 Backup Rts       : 0
Total LblIpv4 Rem Rts   : 0           Total LblIpv4 Rem. Act Rts  : 0
Total LblIpv6 Rem Rts   : 0           Total LblIpv6 Rem. Act Rts  : 0
Total LblIpv4 Bkp Rts   : 0           Total LblIpv6 Bkp Rts       : 0
Total Suppressed Rts     : 0           Total Hist. Rts             : 0
Total Decay Rts         : 0

Total VPN-IPv4 Rem. Rts : 22          Total VPN-IPv4 Rem. Act. Rts: 7
Total VPN-IPv6 Rem. Rts : 22          Total VPN-IPv6 Rem. Act. Rts: 7
Total VPN-IPv4 Bkup Rts : 0           Total VPN-IPv6 Bkup Rts     : 0
Total VPN Local Rts     : 16          Total VPN Supp. Rts         : 0
Total VPN Hist. Rts     : 0           Total VPN Decay Rts         : 0

Total MVPN-IPv4 Rem Rts : 0           Total MVPN-IPv4 Rem Act Rts : 0
Total MVPN-IPv6 Rem Rts : 0           Total MVPN-IPv6 Rem Act Rts : 0
Total MDT-SAFI Rem Rts  : 0           Total MDT-SAFI Rem Act Rts  : 0
Total McIPv4 Remote Rts : 0           Total McIPv4 Rem. Active Rts: 0
Total McIPv6 Remote Rts : 0           Total McIPv6 Rem. Active Rts: 0
Total McVpnIPv4 Rem Rts : 0           Total McVpnIPv4 Rem Act Rts : 0
Total McVpnIPv6 Rem Rts : 0           Total McVpnIPv6 Rem Act Rts : 0

Total EVPN Rem Rts      : 144         Total EVPN Rem Act Rts      : 4
Total L2-VPN Rem. Rts   : 0           Total L2VPN Rem. Act. Rts   : 0
Total MSPW Rem Rts      : 0           Total MSPW Rem Act Rts      : 0
Total RouteTgt Rem Rts  : 0           Total RouteTgt Rem Act Rts  : 0
Total FlowIpv4 Rem Rts  : 0           Total FlowIpv4 Rem Act Rts  : 0
Total FlowIpv6 Rem Rts  : 0           Total FlowIpv6 Rem Act Rts  : 0
Total FlowVpnv4 Rem Rts : 0           Total FlowVpnv4 Rem Act Rts : 0
Total FlowVpnv6 Rem Rts : 0           Total FlowVpnv6 Rem Act Rts : 0
Total Link State Rem Rts: 0           Total Link State Rem Act Rts: 0
Total SrPlcyIpv4 Rem Rts: 0           Total SrPlcyIpv4 Rem Act Rts: 0
Total SrPlcyIpv6 Rem Rts: 0           Total SrPlcyIpv6 Rem Act Rts: 0

===============================================================================
BGP Summary
===============================================================================
Legend : D - Dynamic Neighbor
===============================================================================
Neighbor
Description
                   AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                      PktSent OutQ
-------------------------------------------------------------------------------
10.64.51.2
                64699    5623    0 01d22h49m 0/0/0 (IPv4)
                         5623    0
10.64.54.0
                64599    5614    0 01d22h46m 0/0/0 (IPv4)
                         50616
fd00:fc00:0:51::2
                64699    5624    0 01d22h49m 3/0/0 (IPv6)
                         5623    0
fd00:fde8::23:11
                65000    5757    0 01d22h52m 50/21/5 (IPv4)
                         5651    0           50/16/4 (IPv6)
                                             10/5/3 (VpnIPv4)
                                             10/5/3 (VpnIPv6)
                                             24/2/8 (Evpn)
fd00:fde8::23:12
                65000    5758    0 01d22h52m 50/1/5 (IPv4)
                         5654    0           50/0/4 (IPv6)
                                             12/2/3 (VpnIPv4)
                                             12/2/3 (VpnIPv6)
                                             36/0/8 (Evpn)
fd00:fde8::23:13
                65000    6217    0 01d22h49m 84/2/8 (Evpn)
                         5626    0
fd00:fde8:0:54::
                64599    5617    0 01d22h46m 3/0/0 (IPv6)
                         5616    0
fe80::18b2:10ff:feff:31-"leaf21"(D)
           4200002001    5627    0 01d22h49m 2/2/12 (IPv4)
                         5646    0           2/2/8 (IPv6)
-------------------------------------------------------------------------------
```
///

To be able to reproduce the output shown in the table above we require at least the following information:

- For every BGP neighbor in the "Base" router instance:
    - their AS
    - statistics, including the amount of packets received and sent
    - how long it has been since the peering was established or went down
    - the amount of routes per family received, activated and sent
    - whether the peering is up or down

#### Finding the raw data

One place you might look is the [SR OS YANG explorer](https://yang.labctl.net/yang/SROS/25.3.R1/t) as it allows you to search the YANG model with a convenient web GUI. Another possible location is the MD-CLI. Last but not least, Nokia publishes the YANG models [online](https://github.com/nokia/7x50_YangModels/tree/master/latest_sros_25.3) any time a new version released. Use any of these resources to identify a path that you will be able to use to find each of the data points above for a given BGP neighbor, recognizing that those paths will be reusable when applied to a different BGP neighbor. Remember that `pwc` can provide you with reusable information.

/// details | Solution: finding the context
/// tab | Using the MD-CLI Path Finder
Using the web GUI we can click through the YANG model or we can use the search box in the top right. We can look for attributes including the word `family` under the `/state/router/bgp/neighbor` path and find the `negotiated-family` attribute as well as many others, shown [here](https://yang.labctl.net/yang/SROS/25.3.R1/t/!b!nokia/!k!s/!p!_all!/%2Fstate:state%2Frouter[router-name=*]%2Fbgp%2Fneighbor[ip-address=*]%2Fstatistics%2Fnegotiated-family)
///
/// tab | Using the YANG model repo
By accessing the repo and drilling down into the `nokia-submodule` folder, we find that one of the files named [`nokia-state-router-bgp.yang`](https://github.com/nokia/7x50_YangModels/blob/master/latest_sros_25.3/nokia-submodule/nokia-state-router-bgp.yang). Look at line [641](https://github.com/nokia/7x50_YangModels/blob/master/latest_sros_25.3/nokia-submodule/nokia-state-router-bgp.yang#L641) to see where the list of neighbors begins and what information is included per neighbor.
///
/// tab | Using the MD-CLI
With the MD-CLI we can navigate down to the `/state router bgp` context as that would be where this information is included. Knowing the information we are looking for, use `info full-context` with piped `match` commands to find what is needed.

As an example, consider the negotiated families associated with neighbor `10.64.54.0`. We could navigate down into the associated context or work it into the `match` expression.
/// tab | Navigating down
```
[/state router "Base" bgp neighbor "10.64.54.0" statistics]
A:admin@g23-pe1# info
    peer-port 179
    local-port 51585
    session-state "Established"
    last-state "Active"
    last-event "recvOpen"
    last-error "Unrecognized Error"
    negotiated-family ["IPv4"]
    ... (truncated)
```
///

/// tab | piped `match` statements
```hl_lines="3"
[/state router "Base" bgp]
A:admin@g23-pe1# info full-context | match neighbor | match 10.64.54.0 | match family
    /state router "Base" bgp neighbor "10.64.54.0" statistics negotiated-family ["IPv4"]
    /state router "Base" bgp neighbor "10.64.54.0" statistics remote-family family ["IPv4"]
    ... (truncated)
```
///

///
With the appropriate CLI path identified, you can navigate to it using the MD-CLI and use `pwc json-instance-path` to get a path you will be able to use in your Python code.
```hl_lines="4"
[/state router "Base" bgp neighbor "10.64.54.0" statistics]
A:admin@g23-pe1# pwc json-instance-path
Present Working Context:
/nokia-state:state/router[router-name="Base"]/bgp/neighbor[ip-address="10.64.54.0"]/statistics
```
///

Taking the command output from the previous subtask as a starting point and zeroing in on the case of BGP neighbor `fd00:fde8::23:13`, we would need to find that:

- there have been 5758 packets received
- we have sent 5654 packets
- the peering has been up for 1 day, 22 hours and 52 minutes
- the peering includes only the EVPN address family; 84 routes have been received of which 2 are installed and 8 are advertised
- its peer-as is 65000

These are the values shown for that neighbor in the table.

??? note "Solution: identifying individual attributes"
    ```hl_lines="3 7 11 15 19 23 27 49"
    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# info full-context statistics received messages
        /state router "Base" bgp neighbor "fd00:fde8::23:13" statistics received messages 5758

    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# info full-context statistics sent messages
        /state router "Base" bgp neighbor "fd00:fde8::23:13" statistics sent messages 5654

    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# info full-context statistics last-established-time
        /state router "Base" bgp neighbor "fd00:fde8::23:13" statistics last-established-time 2025-05-13T09:00:17...

    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# info full-context statistics negotiated-family
        /state router "Base" bgp neighbor "fd00:fde8::23:13" statistics negotiated-family ["EVPN"]

    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# info full-context statistics family-prefix evpn received
        /state router "Base" bgp neighbor "fd00:fde8::23:13" statistics family-prefix evpn received 84

    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# info full-context statistics family-prefix evpn active
        /state router "Base" bgp neighbor "fd00:fde8::23:13" statistics family-prefix evpn active 2

    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# info full-context statistics family-prefix evpn sent
        /state router "Base" bgp neighbor "fd00:fde8::23:13" statistics family-prefix evpn sent 8

    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# info full-context statistics peer-as

    [/state router "Base" bgp neighbor "fd00:fde8::23:13"]
    A:admin@g23-pe1# exit all

    [/]
    A:admin@g23-pe1# edit-config private
    INFO: CLI #2070: Entering private configuration mode
    INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

    (pr)[/]
    A:admin@g23-pe1# info /configure router bgp neighbor fd00:fde8::23:13 peer-as

    (pr)[/]
    A:admin@g23-pe1# info /configure router bgp neighbor fd00:fde8::23:13 group
        group "iBGP-DC"

    (pr)[/]
    A:admin@g23-pe1# info /configure router bgp group iBGP-DC peer-as
        peer-as 65000
    ```
    !!! tip Empty peer-as
        This last one may have thrown you for a loop. The peer-as attribute in the statistics context applies only to dynamic-peers which this is neighbor is not. To find out the actual `peer-as` value we can instead look for the value set in the configuration. Note that this could be further obfuscated by a possible `type internal` configuration or the like that would make explicit configuration of the `peer-as` unnecessary.



### Applying your learning with Python

Most of the information needed to build the table is now at your fingertips via the MD-CLI. Let's now look at how to gather it from the router using Python and pySROS. The example solutions will use the Python interpreter in the Hackathon instance opened in [Interactive Mode](https://docs.python.org/3/tutorial/appendix.html#tut-interac), also known as REPL or the interactive interpreter shell.

#### Connecting to model-driven SR OS from pySROS

To begin, make sure you have a working programmatic way of connecting to a model-driven SR OS machine. Use the pySROS [`connect`](https://documentation.nokia.com/html/3HE19211AAAFTQZZA01/pysros.html#pysros.management.connect) method by importing it from `pysros.management` and use the appropriate parameters to connect to `PE1` from your development environment. To complete this subtask, use the pySROS [`get`](https://documentation.nokia.com/sr/25-3/pysros/pysros.html#pysros.management.Datastore.get) method on the `running` datastore along with what you have learned to look up the configured system name to make sure you are on the router you expected to be on.

/// details | Expected result
```bash hl_lines="7"
$ python
Python 3.12.3 (main, Feb  4 2025, 14:48:35) [GCC 13.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from pysros.management import connect
>>> connection = connect(host="clab-srexperts-pe1", hostkey_verify=False, username="admin")
>>> connection.running.get('/configure/system/name')
Leaf('g23-pe1')
>>>
```
///

#### Gathering information from the paths you identified

Next, use the `get` method to get the paths that you identified you would be needing later on. As a general rule of thumb, consider that remotely executed pySROS scripts prefer few `get` calls with [filters](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros-management-datastore-get-example-content-node-filters) applied while on-box execution prefers more precise and frequent `get` calls.

Develop a solution that retrieves the paths required for building the table identified in the previous task for every BGP neighbor in the `Base` routing instance.

!!! note
    One of the BGP neighbors of `PE1` in the topology _is_ a dynamic neighbor so it does have a `peer-as` attribute under `statistics`. Is your solution able to capture that neighbor's information in addition to the information of the statically configured neighbors?

??? note "Solution: gathering information"
    ```python
    >>> neighbor_information = connection.running.get('/state/router[router-name="Base"]/bgp/neighbor')
    >>> result_info = {}
    >>> for neighbor,neighbor_data in neighbor_information.items():
    ...    info = {
    ...        "recvMsg": neighbor_data["statistics"]["received"]["messages"],
    ...        "sentMsg": neighbor_data["statistics"]["sent"]["messages"],
    ...        "lastEstabTime": neighbor_data["statistics"]["last-established-time"],
    ...    }
    ...    prefix_dict = {}
    ...    if "negotiated-family" in neighbor_data["statistics"]:
    ...        for address_family in neighbor_data["statistics"]["negotiated-family"]:
    ...            prefix_data = neighbor_data["statistics"]["family-prefix"][address_family.lower()]
    ...            prefix_dict[address_family] = (
    ...                prefix_data["received"], prefix_data["active"], prefix_data["sent"]
    ...            )
    ...        info["addrFamInfo"] = prefix_dict
    ...    else:
    ...        info["addrFamInfo"] = neighbor_data["statistics"]["session-state"]
    ...    if neighbor_data["statistics"]["dynamically-configured"]:
    ...        info["peerAS"] = neighbor_data["statistics"]["peer-as"]
    ...        info["dynConfig"] = True
    ...    else:
    ...        group_associated_with_neighbor = connection.running.get('/configure/router[router-name="Base"]/bgp/neighbor[ip-address=%s]/group' % neighbor)
    ...        peer_as_from_bgp_group = connection.running.get('/nokia-conf:configure/router[router-name="Base"]/bgp/group[group-name="%s"]/peer-as' % group_associated_with_neighbor)
    ...        info["peerAS"] = peer_as_from_bgp_group
    ...        info["dynConfig"] = False
    ...    result_info[neighbor] = info
    ...
    >>> result_info
    {'10.64.51.2': {'recvMsg': Leaf(7260), 'sentMsg': Leaf(7260), 'lastEstabTime': Leaf('2025-05-13T09:00:19.7Z'), 'addrFamInfo': {'IPv4': (Leaf(0), Leaf(0), Leaf(0))}, 'peerAS': Leaf(64599), 'dynConfig': False}, '10.64.54.0': {'recvMsg': Leaf(7251), 'sentMsg': Leaf(7253), 'lastEstabTime': Leaf('2025-05-13T09:04:00.9Z'), 'addrFamInfo': {'IPv4': (Leaf(0), Leaf(0), Leaf(0))}, 'peerAS': Leaf(64599), 'dynConfig': False}, 'fd00:fc00:0:51::2': {'recvMsg': Leaf(7262), 'sentMsg': Leaf(7260), 'lastEstabTime': Leaf('2025-05-13T09:00:14.9Z'), 'addrFamInfo': {'IPv6': (Leaf(3), Leaf(0), Leaf(0))}, 'peerAS': Leaf(64599), 'dynConfig': False}, 'fd00:fde8::23:11': {'recvMsg': Leaf(1499), 'sentMsg': Leaf(1238), 'lastEstabTime': Leaf('2025-05-15T11:23:59.4Z'), 'addrFamInfo': {'EVPN': (Leaf(24), Leaf(2), Leaf(8)), 'IPv4': (Leaf(50), Leaf(21), Leaf(5)), 'IPv6': (Leaf(50), Leaf(16), Leaf(4)), 'VPN-IPv4': (Leaf(22), Leaf(14), Leaf(6)), 'VPN-IPv6': (Leaf(10), Leaf(5), Leaf(3))}, 'peerAS': Leaf(65000), 'dynConfig': False}, 'fd00:fde8::23:12': {'recvMsg': Leaf(1490), 'sentMsg': Leaf(1238), 'lastEstabTime': Leaf('2025-05-15T11:23:59.4Z'), 'addrFamInfo': {'EVPN': (Leaf(36), Leaf(0), Leaf(8)), 'IPv4': (Leaf(50), Leaf(1), Leaf(5)), 'IPv6': (Leaf(50), Leaf(0), Leaf(4)), 'VPN-IPv4': (Leaf(24), Leaf(2), Leaf(6)), 'VPN-IPv6': (Leaf(12), Leaf(2), Leaf(3))}, 'peerAS': Leaf(65000), 'dynConfig': False}, 'fd00:fde8::23:13': {'recvMsg': Leaf(8086), 'sentMsg': Leaf(7271), 'lastEstabTime': Leaf('2025-05-13T09:00:17.8Z'), 'addrFamInfo': {'EVPN': (Leaf(84), Leaf(2), Leaf(8))}, 'peerAS': Leaf(65000), 'dynConfig': False}, 'fd00:fde8:0:54::': {'recvMsg': Leaf(7254), 'sentMsg': Leaf(7253), 'lastEstabTime': Leaf('2025-05-13T09:04:00.9Z'), 'addrFamInfo': {'IPv6': (Leaf(3), Leaf(0), Leaf(0))}, 'peerAS': Leaf(64599), 'dynConfig': False}, 'fe80::18b2:10ff:feff:31%leaf21': {'recvMsg': Leaf(7264), 'sentMsg': Leaf(7311), 'lastEstabTime': Leaf('2025-05-13T09:00:13.9Z'), 'addrFamInfo': {'IPv4': (Leaf(2), Leaf(2), Leaf(12)), 'IPv6': (Leaf(2), Leaf(2), Leaf(8))}, 'peerAS': Leaf(4200002001), 'dynConfig': True}}
    ```

    !!! note "Pretty Printing"
        pySROS has the [printTree](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.pprint.printTree) utility that can help you display data retrieved from the system datastores and dictionaries in general in a more convenient form:
        ```python
        >>> from pysros.pprint import printTree
        >>> printTree(result_info)
        +-- 10.64.51.2:
        |   +-- recvMsg: 7260
        |   +-- sentMsg: 7260
        |   +-- lastEstabTime: 2025-05-13T09:00:19.7Z
        |   +-- addrFamInfo:
        |   |   `-- IPv4: (Leaf(0), Leaf(0), Leaf(0))
        |   +-- peerAS: 64599
        |   `-- dynConfig: False
        +-- 10.64.54.0:
        |   +-- recvMsg: 7251
        |   +-- sentMsg: 7253
        |   +-- lastEstabTime: 2025-05-13T09:04:00.9Z
        |   +-- addrFamInfo:
        |   |   `-- IPv4: (Leaf(0), Leaf(0), Leaf(0))
        |   +-- peerAS: 64599
        |   `-- dynConfig: False
        +-- fd00:fc00:0:51::2:
        |   +-- recvMsg: 7262
        |   +-- sentMsg: 7260
        |   +-- lastEstabTime: 2025-05-13T09:00:14.9Z
        ... (truncated)
        ```

#### Displaying the information in an SR OS-style table

Clearly, the output from the previous subtask isn't very appealing or usable. Look through the pySROS documentation for the available [methods](https://documentation.nokia.com/sr/25-3/pysros/pysros.html#module-pysros.pprint) for displaying data or implement your own. Use it to display the information gathered in the previous task in a format inspired by the table shown in the standard `show router bgp summary` command.

!!! tip
    Since the system only stores the time of the BGP session being established or going down, you'll have to calculate the amount of time that has passed since then yourself. Fortunately, `datetime` is available in the on-box interpreter as well. The implementation available does not include `strptime` which might be otherwise used, so for on-box execution another approach is required.

/// details | Solution: Printing a table
/// tab | Expected outcome
```python
>>> printTable(table,rows)
===============================================================================
BGP Summary
===============================================================================
Legend : D - Dynamic Neighbor
===============================================================================
Neighbor
Description
                   AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                      PktSent OutQ
-------------------------------------------------------------------------------
10.64.51.2
                64599    7260    0 02d12h34m 0/0/0 (IPv4)
                         7260    0
10.64.54.0
                64599    7251    0 02d12h30m 0/0/0 (IPv4)
                         7253    0
fd00:fc00:0:51::2
                64599    7262    0 02d12h34m 3/0/0 (IPv6)
                         7260    0
fd00:fde8::23:11
                65000    1499    0 00d10h10m 24/2/8 (EVPN)
                         1238    0           50/21/5 (IPv4)
                                             50/16/4 (IPv6)
                                             22/14/6 (VPN-IPv4)
                                             10/5/3 (VPN-IPv6)
fd00:fde8::23:12
                65000    1490    0 00d10h10m 36/0/8 (EVPN)
                         1238    0           50/1/5 (IPv4)
                                             50/0/4 (IPv6)
                                             24/2/6 (VPN-IPv4)
                                             12/2/3 (VPN-IPv6)
fd00:fde8::23:13
                65000    8086    0 02d12h34m 84/2/8 (EVPN)
                         7271    0
fd00:fde8:0:54::
                64599    7254    0 02d12h30m 3/0/0 (IPv6)
                         7253    0
fe80::18b2:10ff:feff:31-"leaf21"(D)
           4200002001    7264    0 02d12h34m 2/2/12 (IPv4)
                         7311    0           2/2/8 (IPv6)
-------------------------------------------------------------------------------
```
///
/// tab | Implementation
/// tab | Creating the columns
Column widths are created to align with the pySROS Table object and how it splits rows.
```python
>>> from pysros.pprint import Padding
>>> width = 79 # standard width
>>> cols = [
...     (79, "Neighbor"),
...     (50, "Description"),
...     Padding(79), #wrap to a new line
...     Padding(8),
...     (12, "          AS"),
...     (7, "PktRcvd"),
...     (4, "InQ"),
...     (9, "Up/Down"),
...     (39, "State|Rcv/Act/Sent (Addr Family)"),
...     Padding(21),
...     (7, "PktSent"),
...     (5, "OutQ"),
... ]
>>>
```
///
/// tab | Populating table rows
```python
>>> import re
>>> from datetime import datetime, timezone
>>> from pysros.pprint import Table
>>> def format_neighbor(neighbor, dyn_config):
...     if "%" in neighbor:
...         ip_addr, intf = neighbor.split("%")
...         return ip_addr + "-\"" + intf + "\"" + ("(D)" if dyn_config else "")
...     return neighbor + ("(D)" if dyn_config else "")
...
...
>>> def calculate_format_timestamp(last_estab_time):
...     match = re.match("^(\\d+)-(\\d+)-(\\d+)T(\\d+):(\\d+):(\\d+).\\dZ$", last_estab_time)
...     year,month,day,hour,minute,second = match.groups()
...     establish_time = datetime(int(year),int(month),int(day),int(hour),int(minute),int(second), tzinfo = timezone.utc)
...     time_since_last_established = datetime.now(timezone.utc) - establish_time
...     hours = time_since_last_established.seconds // 3600
...     minutes = (time_since_last_established.seconds % 3600) // 60
...     return "%02dd%02dh%02dm" % (time_since_last_established.days,hours,minutes)
...
...
>>> def addr_fam_tuple(fam_tuples):
...    if not isinstance(fam_tuples, dict):
...        # in this case, the state is "Connect" and the peer may not be up
...        return (" "+str(fam_tuples),)
...    result = []
...    for family, pfx_info in fam_tuples.items():
...        result.append(" %s/%s/%s (%s)" % (pfx_info[0], pfx_info[1], pfx_info[2], family))
...    return result
...
...
>>> rows = []
>>> for nbr, info in result_info.items():
...    fam_tuples = addr_fam_tuple(info["addrFamInfo"])
...    output = format_neighbor(nbr, info["dynConfig"]) + "\n"
...    # output += description # not present
...    output += "%21s" % info["peerAS"]
...    output += "%8s"%info["recvMsg"]
...    output += "    0 "
...    output += calculate_format_timestamp(str(info["lastEstabTime"]))
...    output += fam_tuples[0]
...    output += "\n"
...    output += "%29s"%info["sentMsg"]
...    output += "    0 "
...    if len(fam_tuples) > 1:
...        output += "%9s%s" % ("",fam_tuples[1])
...    for fam_tuple in fam_tuples[2:]:
...        output += "\n%44s%s" % ("",fam_tuple)
...    rows.append(output)
...
>>>
```
///
/// tab | Writing a printTable function
```python
>>> table = Table("BGP Summary", columns=cols, width=width)
>>> def printTable(table, rows):
...    table.printHeader("BGP Summary")
...    print("Legend : D - Dynamic Neighbor")
...    table.printDoubleLine()
...    table.printColumnHeaders()
...    for row in rows:
...        print(row)
...    table.printSingleLine()
...
>>> printTable(table, rows)
===============================================================================
BGP Summary
===============================================================================
Legend : D - Dynamic Neighbor
===============================================================================
Neighbor
Description
                   AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                      PktSent OutQ
-------------------------------------------------------------------------------
10.64.51.2
                64599    7260    0 02d12h34m 0/0/0 (IPv4)
                         7260    0
10.64.54.0
                64599    7251    0 02d12h30m 0/0/0 (IPv4)
                         7253    0
fd00:fc00:0:51::2
                64599    7262    0 02d12h34m 3/0/0 (IPv6)
                         7260    0
fd00:fde8::23:11
                65000    1499    0 00d10h10m 24/2/8 (EVPN)
                         1238    0           50/21/5 (IPv4)
                                             50/16/4 (IPv6)
                                             22/14/6 (VPN-IPv4)
                                             10/5/3 (VPN-IPv6)
fd00:fde8::23:12
                65000    1490    0 00d10h10m 36/0/8 (EVPN)
                         1238    0           50/1/5 (IPv4)
                                             50/0/4 (IPv6)
                                             24/2/6 (VPN-IPv4)
                                             12/2/3 (VPN-IPv6)
fd00:fde8::23:13
                65000    8086    0 02d12h34m 84/2/8 (EVPN)
                         7271    0
fd00:fde8:0:54::
                64599    7254    0 02d12h30m 3/0/0 (IPv6)
                         7253    0
fe80::18b2:10ff:feff:31-"leaf21"(D)
           4200002001    7264    0 02d12h34m 2/2/12 (IPv4)
                         7311    0           2/2/8 (IPv6)
-------------------------------------------------------------------------------

```
///
///
///

#### Converting to a Python script

If not already done, aggregate the solutions to the preceding subtasks into a single Python file that has the same output as the various individual elements executed sequentially.

/// details | Solution: a single file
```python
import re
from datetime import datetime, timezone
from pysros.management import connect
from pysros.pprint import Table, Padding


def get_information(connection):
    neighbor_information = connection.running.get(
        '/state/router[router-name="Base"]/bgp/neighbor'
    )
    result_info = {}
    for neighbor, neighbor_data in neighbor_information.items():
        info = {
            "recvMsg": neighbor_data["statistics"]["received"]["messages"],
            "sentMsg": neighbor_data["statistics"]["sent"]["messages"],
            "lastEstabTime": neighbor_data["statistics"]["last-established-time"],
        }
        prefix_dict = {}
        if "negotiated-family" in neighbor_data["statistics"]:
            for address_family in neighbor_data["statistics"]["negotiated-family"]:
                prefix_data = neighbor_data["statistics"]["family-prefix"][
                    address_family.lower()
                ]
                prefix_dict[address_family] = (
                    prefix_data["received"],
                    prefix_data["active"],
                    prefix_data["sent"],
                )
            info["addrFamInfo"] = prefix_dict
        else:
            info["addrFamInfo"] = neighbor_data["statistics"]["session-state"]
        if neighbor_data["statistics"]["dynamically-configured"]:
            info["peerAS"] = neighbor_data["statistics"]["peer-as"]
            info["dynConfig"] = True
        else:
            group_associated_with_neighbor = connection.running.get(
                '/configure/router[router-name="Base"]/bgp/neighbor[ip-address=%s]/group'
                % neighbor
            )
            peer_as_from_bgp_group = connection.running.get(
                '/nokia-conf:configure/router[router-name="Base"]/bgp/group[group-name="%s"]/peer-as'
                % group_associated_with_neighbor
            )
            info["peerAS"] = peer_as_from_bgp_group
            info["dynConfig"] = False
        result_info[neighbor] = info
    return result_info


def format_neighbor(neighbor, dyn_config):
    if "%" in neighbor:
        ip_addr, intf = neighbor.split("%")
        return ip_addr + '-"' + intf + '"' + ("(D)" if dyn_config else "")
    return neighbor + ("(D)" if dyn_config else "")


def calculate_format_timestamp(last_estab_time):
    match = re.match(
        "^(\\d+)-(\\d+)-(\\d+)T(\\d+):(\\d+):(\\d+).\\dZ$", last_estab_time
    )
    year, month, day, hour, minute, second = match.groups()
    establish_time = datetime(
        int(year),
        int(month),
        int(day),
        int(hour),
        int(minute),
        int(second),
        tzinfo=timezone.utc,
    )
    time_since_last_established = datetime.now(timezone.utc) - establish_time
    hours = time_since_last_established.seconds // 3600
    minutes = (time_since_last_established.seconds % 3600) // 60
    return "%02dd%02dh%02dm" % (time_since_last_established.days, hours, minutes)


def addr_fam_tuple(fam_tuples):
    if not isinstance(fam_tuples, dict):
        # in this case, the state is "Connect" and the peer may not be up
        return (" " + str(fam_tuples),)
    result = []
    for family, pfx_info in fam_tuples.items():
        result.append(
            " %s/%s/%s (%s)" % (pfx_info[0], pfx_info[1], pfx_info[2], family)
        )
    return result


def printTable(table, rows):
    table.printHeader("BGP Summary")
    print("Legend : D - Dynamic Neighbor")
    table.printDoubleLine()
    table.printColumnHeaders()
    for row in rows:
        print(row)
    table.printSingleLine()


def main():
    connection = connect(
        host="clab-srexperts-pe1", hostkey_verify=False, username="admin"
    )
    result_info = get_information(connection)
    width = 79  # standard width
    cols = [
        (79, "Neighbor"),
        (50, "Description"),
        Padding(79), #wrap to a new line
        Padding(8),
        (12, "          AS"),
        (7, "PktRcvd"),
        (4, "InQ"),
        (9, "Up/Down"),
        (39, "State|Rcv/Act/Sent (Addr Family)"),
        Padding(21),
        (7, "PktSent"),
        (5, "OutQ"),
    ]
    rows = []
    for nbr, info in result_info.items():
        fam_tuples = addr_fam_tuple(info["addrFamInfo"])
        output = format_neighbor(nbr, info["dynConfig"]) + "\n"
        # output += description # not present
        output += "%21s" % info["peerAS"]
        output += "%8s" % info["recvMsg"]
        output += "    0 "
        output += calculate_format_timestamp(str(info["lastEstabTime"]))
        output += fam_tuples[0]
        output += "\n"
        output += "%29s" % info["sentMsg"]
        output += "    0 "
        if len(fam_tuples) > 1:
            output += "%9s%s" % ("", fam_tuples[1])
        for fam_tuple in fam_tuples[2:]:
            output += "\n%44s%s" % ("", fam_tuple)
        rows.append(output)

    table = Table("BGP Summary", columns=cols, width=width)
    printTable(table, rows)


if __name__ == "__main__":
    main()
```
///

Copy that file to `PE1` using SCP or another method to prepare for the next task.

```bash
$ scp bgp_summary.py admin@clab-srexperts-pe1:/cf3:/bgp_summary.py
Warning: Permanently added 'clab-srexperts-pe1' (ECDSA) to the list of known hosts.

bgp_summary.py                                                                                                                      100% 4735     2.8MB/s   00:00
```

### Override the existing show command with a command-alias

Note down the path where your Python script is on `PE1`. We will use `cf3:/bgp_summary.py`. In this final task, we will modify the SR OS configuration to override the existing command for `show router bgp summary` with our own implementation. To do this, we will have to create a `python-script` object and a `command-alias` that makes use of it.

Before changing any configuration, make sure your script works as expected when used via `pyexec`. Any issues introduced or discovered later would require additional steps as the `python-script` object exists in memory and will not be updated automatically when the underlying file is changed. Should you need to reload the file into memory you can use `/perform python python-script reload script <name>`. To see what version of the script lives in memory you can use `/show python python-script <name> source-in-use`.

!!! note "pyexec result"
    ```
    [/]
    A:admin@g23-pe1# pyexec bgp_summary.py
    ===============================================================================
    BGP Summary
    ===============================================================================
    Legend : D - Dynamic Neighbor
    ===============================================================================
    Neighbor
    Description
                    AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                        PktSent OutQ
    -------------------------------------------------------------------------------
    10.64.51.2
                    64599    6241    0 02d03h58m 0/0/0 (IPv4)
                            6241    0
    10.64.54.0
                    64599    6231    0 02d03h54m 0/0/0 (IPv4)
                            6233    0
    fd00:fde8:0:54::
                    64599    6234    0 02d03h54m 3/0/0 (IPv6)
                            6233    0
    fd00:fde8::23:13
                    65000    6969    0 02d03h58m 84/2/8 (EVPN)
                            6252    0
    fd00:fc00:0:51::2
                    64599    6242    0 02d03h58m 3/0/0 (IPv6)
                            6241    0
    fd00:fde8::23:12
                    65000     468    0 00d01h34m 50/0/4 (IPv6)
                            218    0           24/2/6 (VPN-IPv4)
                                                50/1/5 (IPv4)
                                                36/0/8 (EVPN)
                                                12/2/3 (VPN-IPv6)
    fd00:fde8::23:11
                    65000     471    0 00d01h34m 50/16/4 (IPv6)
                            218    0           22/14/6 (VPN-IPv4)
                                                50/21/5 (IPv4)
                                                24/2/8 (EVPN)
                                                10/5/3 (VPN-IPv6)
    fe80::18b2:10ff:feff:31-"leaf21"(D)
            4200002001    6244    0 02d03h58m 2/2/12 (IPv4)
                            6291    0           2/2/8 (IPv6)
    -------------------------------------------------------------------------------
    ```
    ??? question "Did you change the parameters in your `connect` call?"
        As you may have noticed, when executed on-box, a call to `connect` will always connect to the local router and only the local router, it requires no credentials. Thus, any parameters that were left in the call are unused.

Create a command alias called `summary` that calls your Python application (configured as a `python-script`). Use a private candidate session and the documentation for [Python objects](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exgst4g) and [aliases](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/navigate.html#concept_hkg_hb3_bqb) to find out what configuration is required.
/// details | Solution: creating an alias
/// tab | Python script
```
[/]
A:admin@g23-pe1# edit-config private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(pr)[/]
A:admin@g23-pe1# configure python python-script bgp_summary

*(pr)[/configure python python-script "bgp_summary"]
A:admin@g23-pe1# version python3

*(pr)[/configure python python-script "bgp_summary"]
A:admin@g23-pe1# admin-state enable

*(pr)[/configure python python-script "bgp_summary"]
A:admin@g23-pe1# urls cf3:/bgp_summary.py
```
///
/// tab | command-alias
```
*(pr)[/configure python python-script "bgp_summary"]
A:admin@g23-pe1# /configure system management-interface cli md-cli environment command-alias alias summary

*(pr)[/configure system management-interface cli md-cli environment command-alias alias "summary"]
A:admin@g23-pe1# mount-point "/show router bgp"

*(pr)[/configure system management-interface cli md-cli environment command-alias alias "summary"]
A:admin@g23-pe1# python-script bgp_summary

*(pr)[/configure system management-interface cli md-cli environment command-alias alias "summary"]
A:admin@g23-pe1# admin-state enable

*(pr)[/configure system management-interface cli md-cli environment command-alias alias "summary"]
A:admin@g23-pe1# commit
```
///
///

Finally, log out and back in and reap the rewards of your efforts in this activity. When you execute the command `show router bgp summary` the output will be the concise table you created yourself rather than the standard system output.

## Summary and review

Congratulations!  If you have got this far you have completed this activity and achieved the following:

- You have learned how to install pySROS and Python virtual environments
- You have written one or more applications using the Python 3 programming language
- You have an understanding of model-driven management
- You have worked with YANG modeled data
- You have bent the behavior of SR OS show commands to your will
- You have executed Python applications on the SR OS model-driven CLI (MD-CLI)
- You have created aliases on the SR OS model-driven CLI (MD-CLI) in order to integrate your own commands into the fabric of SR OS

This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity or have a look at some other `show` commands you might want to alter. You may also be interested in the robust and hardened implementation of this solution that exists as an [example in the pySROS repository](https://github.com/nokia/pysros/blob/main/examples/show_router_bgp_asn.py).