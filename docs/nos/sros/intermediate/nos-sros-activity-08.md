---
tags:
  - SR OS
  - pySROS
  - Python
  - MD-CLI
  - Event handler
---

# Automatic update of interface descriptions using the event handler
|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Automatic update of interface descriptions using the event handler                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **Activity ID**             | 08                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **Short Description**       | Use the SR OS Event handler to automatically update interface descriptions when LLDP information changes.                                                                                                                                                                                                                                                                                                                                                  |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/){:target="_blank"}, [Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html){:target="_blank"}, [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html){:target="_blank"}, [Python programming language](https://www.python.org){:target="_blank"}, [MicroPython](https://micropython.org/), [SR OS YANG explorer](https://yang.labctl.net/yang/SROS/25.3.R1/t){:target="_blank"}, [Log Events Search Tool](https://documentation.nokia.com/sr/25-3/log-events-search/events.html){:target="_blank"}                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Topology Nodes**          | :material-router: PE2 and minor changes to :material-router: spine12                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              |[MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html){:target="_blank"}<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/system-management.html){:target="_blank"}<br/>[pySROS user documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html){:target="_blank"}<br/>[pySROS GitHub](https://github.com/nokia/pysros){:target="_blank"} (check the examples directory)|

## Objective

Through various tasks, this activity explores the event-handling features available in SR OS. The aim is to add some level of self-sufficiency to our model-driven router `PE2` that makes it automatically load information learned through the Link Layer Discovery Protocol (LLDP) into the corresponding port's description.

To achieve this objective, we will explore the SR OS Event Handling System (EHS) through the following tasks:

1. Create a Python script that polls LLDP state and adds it to the respective port `description` attribute in the configuration
2. Set up event handling configuration to trigger whenever an LLDP session is established or updated to call your Python script
3. Extend your Python application to send a log event whenever a change in LLDP peering information is observed

:material-router: PE2 will be configured in this activity and minor changes will be done to one or more of its directly connected neighbors. The example solution uses :material-router:spine12.

## Technology explanation

In this activity, in addition to using the SR OS model-driven CLI and event handling system, you will be working with the Python programming language from the development environment of your choosing.

A basic level of Python proficiency is assumed for this activity.

The key technologies this activity might include are summarized and briefly described here:

### LLDP

LLDP is a vendor-agnostic link layer protocol used by network devices to advertise information about their identity to their directly connected neighbors. One of its most common uses is being able to identify which nodes are connected to a given node for troubleshooting purposes by using commands similar to `show system lldp neighbors`.

### Model-driven SR OS and YANG

As the term "model-driven" suggests, a model-driven Network Operating System (NOS) such as SR OS has one or more data models at its core.  These data models compile together to provide the schema for the system.  These data models are written using a language called YANG. The data models used in this activity are for SR OS and are available [online](https://github.com/nokia/7x50_YangModels) and in the [YANG path explorer](https://yang.labctl.net/yang/SROS/25.3.R1/t){:target="_blank"}.

These YANG models are used to provide consistency between the MD-CLI and programmatic interfaces like NETCONF and gRPC. They describe the structure and data-types of everything in SR OS.
As we will see in this activity, the YANG model can be used as a source of information for you to learn where you might expect to find data or to know where certain configuration changes have to go.

### MD-CLI
Based on the YANG model, the MD-CLI can be used to display configuration and state information in different paths. This information can be retrieved using the [`info` command](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/display-information.html#ai89jylu4e){:target="_blank"}, which outputs the information in the same structure as it is saved in the underlying YANG modeled datastore.

The `pwc` command can be used to display the path associated with a given context in various encodings. For pySROS we use the `json-instance-path` format.

The `tree` command can be used to display the underlying YANG schema of the device.

The `/state` branch stores read-only information about the current state of the system, while modifiable configurations are stored in the `/configure` branch.

In the MD-CLI, the session is either in operational or [configuration mode](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/edit-configuration.html){:target="_blank"}, which is indicated in the command prompt.
/// details | Command prompt in operational mode
```
[/]
A:admin@g23-pe2#
```
///
/// details | Command prompt in exclusive configuration mode
```
(ex)[/]
A:admin@g23-pe2#
```
///

The `/state` branch is accessible in either mode while the `/configure` branch can only be accessed in configuration mode. Changes made in configuration mode are written to a candidate datastore rather than being directly applied to the running datastore. A `commit` operation validates and merges changes from a candidate datastore into the system's active configuration, stored in the running datastore.

### SR OS Event Handling System

The Event Handling System (EHS) has been a part of SR OS for many years. The capability to trigger pySROS applications to handle events has been added and that greatly increases the logic that can go into these scripts. For the second task outlined above we will look at using this functionality. Conceptually, an event generated by the system can be tied into an execution of a pySROS application and that application has complete access to the parameters associated with the event.

As we will see for the later part of the activity, the [documentation](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/event-account-logs.html#ai9exj5x1x){:target="_blank"} on the EHS highlights the configuration that is required for it to be functional. Generally, once the relevant event is identified, a trigger has to be created that refers to a filter and a handler. If the event passes through the filter's conditions the handler can be used to assign it to a script.

### MD-CLI pyexec command

The SR OS MD-CLI `pyexec` command allows operators to run a Python 3 application on the SR OS node by providing a filename or the name of a python-script configured in the MD-CLI as input. This may be useful when testing your application.

Example uses: ```pyexec cf3:/myscript.py``` or ```pyexec my-script-name```

The [SR OS system management guide](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exgst4k){:target="_blank"} provides more information on its use.

### Developing Python scripts

Python applications can be written in the form of a file or a combination of several files and are generally structured as reusable modules or packages. For use within model-driven SR OS, the possibilities narrow slightly as scripts exist as a single file and the modules that can be imported are tuned for and determined by the system. Scripts using pySROS can be executed either locally on the box or remotely from a Python-capable machine in which case pySROS also handles the connection to the remote model-driven SR OS node. The behavior between both environments is designed to be similar. This allows development efforts to take place on a system like your personal laptop or a shared scripting server, rather than needing to be done on the node directly. In this Hackathon, the VM you are given access to can be used as a development environment.

For the first task we will begin by implementing the logic remotely before deploying and integrating it into node `PE2`.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Building the logic to update port descriptions with LLDP information

In the coming subtasks, we will go over how to create a Python application that is ready to be run using the MicroPython interpreter inside model-driven SR OS.

#### Prepare your Python virtual environment

If you are able to, we recommend completing this activity using your local machine as a development environment. This task helps you prepare for that. Should you be unable to or if you want to move on quickly, your group's hackathon VM comes pre-installed with the necessary libraries for this activity. By switching to that platform for development you can skip the remainder of this task.

Several tools exist that make programming in Python a smooth experience. Among those are `pip`, `venv` and `uv`. In the example walkthrough we use `uv` on WSL for the preparations. Begin by creating a directory that will hold any files related to this activity and creating a virtual environment there. Install the pySROS library into that virtual environment.

/// details | Preparing your local environment
/// tab | Commands
```bash
sudo apt install python3-pip #if needed
pip install uv #if needed
# create a new session to load the uv command
mkdir usecase
cd usecase
uv venv env
source env/bin/activate
```
///
/// tab | Outputs
```bash
wsl-ubuntu: sudo apt install python3-pip
[sudo] password for user:
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
The following packages were automatically installed and are no longer required:
  bridge-utils dctrl-tools dkms dns-root-data dnsmasq-base libpython2-stdlib linux-headers-5.15.0-94
  linux-headers-5.15.0-94-generic linux-headers-generic python-pkg-resources python-setuptools python2 python2-minimal
  ubuntu-fan wireguard-dkms wireguard-tools
Use 'sudo apt autoremove' to remove them.
The following packages will be REMOVED:
  python-pip
The following NEW packages will be installed:
  python3-pip
0 upgraded, 1 newly installed, 1 to remove and 232 not upgraded.
Need to get 1306 kB of archives.
After this operation, 2153 kB of additional disk space will be used.
Do you want to continue? [Y/n] Y
Get:1 http://archive.ubuntu.com/ubuntu jammy-updates/universe amd64 python3-pip all 22.0.2+dfsg-1ubuntu0.5 [1306 kB]
Fetched 1306 kB in 0s (3666 kB/s)
(Reading database ... 115091 files and directories currently installed.)
Removing python-pip (20.3.4+dfsg-4) ...
Selecting previously unselected package python3-pip.
(Reading database ... 114590 files and directories currently installed.)
Preparing to unpack .../python3-pip_22.0.2+dfsg-1ubuntu0.5_all.deb ...
Unpacking python3-pip (22.0.2+dfsg-1ubuntu0.5) ...
Setting up python3-pip (22.0.2+dfsg-1ubuntu0.5) ...
Processing triggers for man-db (2.10.2-1) ...
wsl-ubuntu: pip install uv
Defaulting to user installation because normal site-packages is not writable
Collecting uv
  Downloading uv-0.7.2-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (17.4 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 17.4/17.4 MB 8.0 MB/s eta 0:00:00
Installing collected packages: uv
Successfully installed uv-0.7.2
#
# Create a new session here to reload the newly installed command uv
#
wsl-ubuntu: mkdir usecase
wsl-ubuntu: cd usecase/
wsl-ubuntu: uv venv env
Using CPython 3.10.12 interpreter at: /usr/bin/python3
Creating virtual environment at: env
Activate with: source env/bin/activate
wsl-ubuntu: source env/bin/activate
(env) wsl-ubuntu:
```
///
///

The prompt changes and shows the name of the virtual environment at the start of the prompt. The virtual environment can be exited using the `deactivate` command. We need to install the `pySROS` library in this virtual environment to be able to to interact with model-driven SR OS remotely. Install it using `uv pip`.

/// details | Installing pySROS
/// tab | Command
```bash
uv pip install pysros
```
///
/// tab | Outputs
```bash
(env) wsl-ubuntu: uv pip install pysros
Using Python 3.10.12 environment at: env
Resolved 9 packages in 788ms
      Built ncclient==0.6.19
Prepared 9 packages in 1.75s
Installed 9 packages in 5.10s
 + bcrypt==4.3.0
 + cffi==1.17.1
 + cryptography==44.0.3
 + lxml==5.3.2
 + ncclient==0.6.19
 + paramiko==3.5.1
 + pycparser==2.22
 + pynacl==1.5.0
 + pysros==25.3.2
```
///
///

#### Using the interactive Python interpreter to interact with `PE2`

Open an [interactive](https://docs.python.org/3/tutorial/appendix.html#tut-interac) Python interpreter session using the `python` command and import the [`connect`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.connect) method from the pySROS library. Use it to open a connection to SR OS node `PE2`. Under normal circumstances, the port exposed by SR OS for NETCONF is 830, however the Hackathon setup maps ports differently.

For `PE2` the NETCONF port is mapped to the your group's hackathon VM's port 50422. This means that when connecting to your assigned hackathon VM on aforementioned port, we will reach `PE2`'s NETCONF port. Since pySROS uses NETCONF for connecting to the node when running remotely, this port would be the one to use when developing outside your group's hackathon VM. If you are using the hackathon VM itself you can use the default port and the `clab-srexperts-pe2` hostname.

Once the connection object has been created, try to `get` the system's `oper-name` attribute from the running datastore to confirm we connected to the correct node.

/// details | Solution - connecting and executing a basic `get`
/// tab | Start the Python interpreter shell
```bash title="In your development environment of choice or your group's Hackathon VM."
python
```
///
/// tab | Connect and get something using pySROS
```python
from pysros.management import connect
connection = connect(host="23.srexperts.net", username="admin", hostkey_verify=False, password=#PROVIDED#, port=50422)
connection.running.get('/configure/system/name')
```
///
/// tab | Expected outcome
```bash {.no-copy}
(env) wsl-ubuntu: python
Python 3.10.12 (main, Jan 17 2025, 14:35:34) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from pysros.management import connect
>>> connection = connect(host="23.srexperts.net", username="admin", hostkey_verify=False, password=#PROVIDED#, port=50422)
>>> connection.running.get('/state/system/oper-name')
Leaf('g23-pe2')
```
///

/// admonition | Host key verification
    type: warning
As you can see from the example output or as you might have noticed, the `hostkey_verify` keyword parameter for the `connect` call is set to `False`. This makes us vulnerable to man-in-the-middle attacks. The alternative to disabling the verification is explicitly connecting to each node on the desired port to save the associated key, however for lab environments that are cleaned up and recreated regularly this is not efficient. In addition, the danger of this vulnerability is lessened greatly in such lab environments. In any live network environment `hostkey_verify` should be set to `True`.
///
///

///tip | Pretty Output
You can use the [`printTree` function](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.pprint.TreePrinter){:target="_blank"} to print data retrieved in a more readable format

/// tab | Code
```python
from pysros.pprint import printTree
data=connection.running.get('/state/port[port-id="1/1/c4/1"]/statistics')
printTree(data)
```
///
/// tab | Execution
```python
>>> from pysros.pprint import printTree
>>> data=connection.running.get('/state/port[port-id="1/1/c4/1"]/statistics')
>>> printTree(data)
+-- counter-discontinuity-time: 2025-04-30T07:58:48.5Z
+-- in-discards: 0
+-- in-errors: 0
+-- in-octets: 366447557
+-- in-packets: 2959028
+-- in-unknown-protocol-discards: 0
+-- in-broadcast-packets: 0
+-- in-multicast-packets: 24944
+-- in-unicast-packets: 2934084
+-- out-discards: 0
+-- out-errors: 0
+-- out-octets: 1043282539
+-- out-packets: 8537578
+-- out-broadcast-packets: 0
+-- out-multicast-packets: 24955
+-- out-unicast-packets: 8512623
`-- egress-queue:
    `-- queue:
        +-- 1:
        |   `-- queue-id: 1
        +-- 2:
        |   `-- queue-id: 2
        +-- 3:
        |   `-- queue-id: 3
        +-- 4:
        |   `-- queue-id: 4
        +-- 5:
        |   `-- queue-id: 5
        +-- 6:
        |   `-- queue-id: 6
        +-- 7:
        |   `-- queue-id: 7
        `-- 8:
            `-- queue-id: 8
```
///
///

#### Get LLDP information using your interactive interpreter

Continue with the interactive session from the previous task. Now that you have seen how to retrieve information from the system, think back to the problem we are trying to solve. The Hackathon nodes are pre-configured with LLDP, yet there is no documentation or check on which LLDP peer is expected to be visible on which node or which port. For the Hackathon topology where we control everything this isn't a big deal but for labs that are used and managed by several teams or production environments this is important.

To start, we will examine what data is available on `PE2` to identify which LLDP peers are available as well as what information we have about them. Use the online SR OS YANG explorer (the online version of the YANG model), the MD-CLI or anything else you're thinking of to find out where information about LLDP peers is stored in the system.

/// details | Solution - Which context contains LLDP neighbor information?
This information is stored under each port ([YANG model](https://yang.labctl.net/yang/SROS/25.3.R1/t/!b!nokia/!p!_all!/%2Fstate:state%2Fport[port-id=*]%2Fethernet%2Flldp){:target="_blank"}).
That means we can use the MD-CLI on node `PE2` and navigate to, for instance, `state port 1/1/c1/1 ethernet lldp` to retrieve LLDP neighbor information for this port using the `info` command.

```
[/]
A:admin@g23-pe2# state port 1/1/c1/1 ethernet lldp

[/state port 1/1/c1/1 ethernet lldp]
A:admin@g23-pe2# info
    dest-mac nearest-bridge {
        remote-system 5615 remote-index 1 {
            age 62489
            chassis-id "0C:00:E8:80:70:00"
            chassis-id-subtype mac-address
            remote-port-id "1/1/c2/1"
            remote-port-id-subtype interface-name
            port-description "1/1/c2/1, 100-Gig Ethernet, "first link to PE2""
            system-enabled-capabilities [bridge router]
            system-supported-capabilities [bridge router]
            system-description "TiMOS-B-25.3.R1 both/x86_64 Nokia 7750 SR Copyright (c) 2000-2025 Nokia.\nAll rights reserved. All use subject to applicable license agreements.\nBuilt on Wed Mar 12 21:50:19 UTC 2025 by builder in /builds/253B/R1/panos/main/sros\n"
            system-name "g23-p1"
        }
      ...
    }
```

The corresponding show command, `show system lldp neighbor`, aggregates and presents this information for the entire system in an easily readable table.
///

To complete this sub-task, implement logic in Python that retrieves `remote-port-id` and `system-name` attributes from all `nearest-bridge` LLDP neighbors in the system. Compare your solution with the expected result before you proceed with the next step.

///tip
[Documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.get){:target="_blank"} on pySROS' `get` and `selection filters` may help you with this.
///

/// details | Expected result
    type: note
/// tab | Expected result
```bash
>>> printTree(lldp_state)
+-- 1/1/c1/1:
|   +-- port-id: 1/1/c1/1
|   `-- ethernet:
|       `-- lldp:
|           `-- dest-mac:
|               `-- nearest-bridge:
|                   +-- mac-type: nearest-bridge
|                   `-- remote-system:
|                       `-- (48883486, 6):
|                           +-- remote-port-id: 1/1/c2/1
|                           `-- system-name: g15-p1
+-- 1/1/c2/1:
|   +-- port-id: 1/1/c2/1
|   `-- ethernet:
|       `-- lldp:
|           `-- dest-mac:
|               `-- nearest-bridge:
|                   +-- mac-type: nearest-bridge
|                   `-- remote-system:
|                       `-- (48883346, 5):
|                           +-- remote-port-id: 1/1/c2/1
|                           `-- system-name: g15-p2
+-- 1/1/c3/1:
|   +-- port-id: 1/1/c3/1
|   `-- ethernet:
|       `-- lldp:
|           `-- dest-mac:
|               `-- nearest-bridge:
|                   +-- mac-type: nearest-bridge
|                   `-- remote-system:
|                       `-- (48883649, 7):
|                           +-- remote-port-id: ethernet-1/32
|                           `-- system-name: g15-spine11
`-- 1/1/c4/1:
    +-- port-id: 1/1/c4/1
    `-- ethernet:
        `-- lldp:
            `-- dest-mac:
                `-- nearest-bridge:
                    +-- mac-type: nearest-bridge
                    `-- remote-system:
                        `-- (48883656, 8):
                            +-- remote-port-id: ethernet-1/32
                            `-- system-name: g15-spine12
```
///
/// tab | Solution
```python
from pysros.pprint import printTree
lldp_state=connection.running.get('/state/port',filter={"ethernet": {"lldp": {"dest-mac": { "remote-system": { "system-name": { }, "remote-port-id": { } } } } } } )
printTree(lldp_state)
```
///

///

#### Aggregate your code into a Python script

Exit the interactive interpreter session and create a file in your current working directory that contains the code you have developed in the previous steps. This script should perform the same actions as you have now done through the interactive interpreter when it is executed.

The example solution uses a file called `lldp_description.py`. Make sure your script can generate the same output as what you had in the previous step.

/// details | Expected outcome
/// tab | Expected execution
```bash
(env) wsl-Ubuntu: $ python lldp_description.py
+-- 1/1/c1/1:
|   +-- port-id: 1/1/c1/1
|   `-- ethernet:
|       `-- lldp:
|           `-- dest-mac:
|               `-- nearest-bridge:
|                   +-- mac-type: nearest-bridge
|                   `-- remote-system:
|                       `-- (27625165, 2):
|                           +-- remote-time-mark: 27625165
|                           +-- remote-index: 2
|                           +-- remote-port-id: 1/1/c2/1
|                           `-- system-name: p1
+-- 1/1/c2/1:
|   +-- port-id: 1/1/c2/1
|   `-- ethernet:
|       `-- lldp:
|           `-- dest-mac:
|               `-- nearest-bridge:
|                   +-- mac-type: nearest-bridge
|                   `-- remote-system:
|                       `-- (27627665, 1):
|                           +-- remote-time-mark: 27627665
|                           +-- remote-index: 1
|                           +-- remote-port-id: 1/1/c2/1
|                           `-- system-name: p2
+-- 1/1/c3/1:
|   +-- port-id: 1/1/c3/1
|   `-- ethernet:
|       `-- lldp:
|           `-- dest-mac:
|               `-- nearest-bridge:
|                   +-- mac-type: nearest-bridge
|                   `-- remote-system:
|                       `-- (18365, 3):
|                           +-- remote-time-mark: 18365
|                           +-- remote-index: 3
|                           +-- remote-port-id: ethernet-1/32
|                           `-- system-name: g23-spine11
`-- 1/1/c4/1:
    +-- port-id: 1/1/c4/1
    `-- ethernet:
        `-- lldp:
            `-- dest-mac:
                `-- nearest-bridge:
                    +-- mac-type: nearest-bridge
                    `-- remote-system:
                        `-- (18385, 4):
                            +-- remote-time-mark: 18385
                            +-- remote-index: 4
                            +-- remote-port-id: ethernet-1/32
                            `-- system-name: g23-spine12
```
///
/// tab | File `lldp_description.py`
```python
from pysros.management import connect
from pysros.pprint import printTree

def main():
    connection = connect(
        host="23.srexperts.net",
        username="admin",
        hostkey_verify=False,
        port=50422,
        password=#PROVIDED#
    )

    data = connection.running.get('/state/port', filter = {
            "ethernet": {
                "lldp": {
                    "dest-mac": {
                        "remote-system": {
                            "system-name": { },
                            "remote-port-id": { }
                        }
                    }
                }
            }
        }
    )
    printTree(data)


if __name__ == "__main__":
    main()
```
///
///

From here on, we will develop changes directly in your script file and test them by executing the file using the interpreter as this is a more convenient approach when developing complex and nested code.

#### Reflect the LLDP information into the corresponding port's description

Start building on your existing script. Remove the elements that generate output and replace them with code that iterates through the datastructure obtained in the previous steps to achieve a mapping between `port-id` and a tuple of `system-id` and `remote-port-id`. One by one, while going through the list of `port-id`s, overwrite the currently configured port description to instead be equal to

`"connected to port {remote-port-id} of {system-id}"`

As before, the MD-CLI with `pwc` or the online YANG model can help you determine the target path for your configuration changes. Similarly, the [documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.set){:target="_blank"} on the `set` function can help you here. Consider it an optimization to not commit for every individual updated `description` but to only do it once at the end.

!!! tip "Private candidate"
    One of the four configuration modes available in model-driven SR OS is [`private`](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/edit-configuration.html#ai89jylu08). A handy feature of this mode is that once you enter it using `edit-config private`, whenever someone or something else makes any changes your view of the running datastore won't automatically be updated. You are instead presented with a `!` at the start of your prompt, indicating there have been changes since your session began or was last updated.

    At that point, you can use `compare baseline running` to view these changes and `update /configure` allows you to pull the changes into your session. The example solution uses this approach to see changes made to the running datastore easily, without having to look up individual paths.

/// details | Expected result
/// tab | Resulting changes on the node
```
!(pr)[/]
A:admin@g23-pe2# compare baseline running
    configure {
        port 1/1/c1/1 {
-           description "first link to P1"
+           description "connected to port 1/1/c2/1 of g23-p1"
        }
        port 1/1/c2/1 {
-           description "link to P2"
+           description "connected to port 1/1/c2/1 of g23-p2"
        }
        port 1/1/c3/1 {
-           description "link to spine11"
+           description "connected to port ethernet-1/32 of g23-spine11"
        }
        port 1/1/c4/1 {
-           description "link to spine12"
+           description "connected to port ethernet-1/32 of g23-spine12"
        }
    }
```
///
/// tab | Corresponding Python code
```python
from pysros.management import connect

def main():
    connection = connect(
        host="23.srexperts.net",
        username="admin",
        hostkey_verify=False,
        port=50422,
        password=#PROVIDED#
    )

    data = connection.running.get('/state/port', filter = {
            "ethernet": {
                "lldp": {
                    "dest-mac": {
                        "remote-system": {
                            "system-name": { },
                            "remote-port-id": { }
                        }
                    }
                }
            }
        }
    )

    result = {}
    for key, value in data.items():
        relevant_context = value["ethernet"]["lldp"]["dest-mac"]["nearest-bridge"]["remote-system"]
        latest_entry = max(sorted(relevant_context.keys(), key=lambda x: x[0], reverse=True))
        result[key] = (relevant_context[latest_entry]["system-name"], relevant_context[latest_entry]["remote-port-id"])

    port_path = "/nokia-conf:configure/port[port-id=\"PORT_ID\"]"
    for key, value in result.items():
        connection.candidate.set(
            port_path.replace("PORT_ID", key),
            { "description": "connected to port %s of %s" % (value[1], value[0])},
            commit=False
        )
    connection.candidate.commit()


if __name__ == "__main__":
    main()
```
///
///

Roll back one or more of the changed port configurations before proceeding to the next step, to ensure we still have an observable result in the next task. You can use the following copy-pastable snippet on `PE2` to quickly go back to the original configuration:

```
exit all
quit-config
edit-config global
/configure port 1/1/c1/1 description "first link to P1"
/configure port 1/1/c2/1 description "first link to P2"
/configure port 1/1/c3/1 description "first link spine11"
/configure port 1/1/c4/1 description "first link spine12"
commit
quit-config
```

#### Copy the script to the target SROS node `PE2`

Having built up the code, we can now copy it onto our model-driven SR OS `PE2` node. Copy your `lldp_description.py` file over to the router using `scp`, copy and paste the file contents to a file on the local flash card using `file edit` or use another method and make sure your file is available on the router before proceeding.

If you are developing on your own platform, the port mapped to `PE2`'s port 22 is `50022`. If you are working on your group's hackathon VM you can go directly to `clab-srexperts-pe2`.

??? note "[vrnetlab](https://github.com/srl-labs/vrnetlab/tree/master/nokia/sros) SR OS tftpboot"
    If you use SR OS in containerlab, a file location is created and is reachable from within SR OS as a TFTP location, `tftp://172.31.255.29/`. In the Hackathon topology and environment, for node `PE2`, that location is `/home/nokia/clab-srexperts/pe2/tftpboot/`. The result of this is that any file you put in that folder will be accessible from within SR OS using TFTP. This could be used as an alternative to `scp` or manually copying over the file contents for containerlab environments.

/// details | Running your script with `pyexec`
```
[/]
A:admin@g23-pe2# edit-config private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(pr)[/]
A:admin@g23-pe2# pyexec cf3:/lldp_description.py

!(pr)[/]
A:admin@g23-pe2# compare baseline running
    configure {
        port 1/1/c1/1 {
-           description "first link to P1"
+           description "connected to port 1/1/c2/1 of g23-p1"
        }
        port 1/1/c2/1 {
-           description "link to P2"
+           description "connected to port 1/1/c2/1 of g23-p2"
        }
        port 1/1/c3/1 {
-           description "link to spine11"
+           description "connected to port ethernet-1/32 of g23-spine11"
        }
        port 1/1/c4/1 {
-           description "link to spine12"
+           description "connected to port ethernet-1/32 of g23-spine12"
        }
    }
```
///

This is looking like the behavior we set out to to achieve. A Python interpreter runs on the node and adapts the configuration. The only part that is missing is that the Python process was not triggered automatically.

Once again revert the changes made by your Python script so the script can be run with an observable result.

??? Info "Did you update the `connect()` call parameters?"
    As you may have noticed, when executed on-box, a call to connect will always connect to the local router and only the local router, it requires no credentials. Thus, any parameters that were left in the call are unused.


### Use the event handling system to trigger your script

For this step, look into the documentation for the [`Event Handling System (EHS)` ](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/event-account-logs.html#ai9exj5x1x){:target="_blank"} and consider the configuration required:

- Select the event to handle
- Create a trigger for that particular event
- Create a handler and a filter for that trigger to point to
- Point the handler to your script

In the next steps, we will look at how to configure each of these.

#### Searching through events

Looking at the [Log Events Search Tool](https://documentation.nokia.com/sr/25-3/log-events-search/events.html){:target="_blank"}, search for the event that corresponds to an LLDP neighborship being established or modified.

/// details | Solution
The events we will work with in the example solution are `tmnxLldpRemEntryPeerAdded` and `tmnxLldpRemEntryPeerUpdated`.
///

In the next sections we will build towards a complete EHS configuration, you may not be able to commit your changes before reaching the final step where the script is configured. That is expected, as it prevents your functionality from going into the system before it is ready to be used. The configuration changes required are dependant on each other so there may even be validation errors that prevent a `commit` before the complete configuration is prepared.

#### Event-trigger configuration

Using the EHS documentation from before, look into the configuration required to make an `event-trigger` that fires when the events you found in the previous step are logged to the system. Create an `event-trigger` of your own for the events you identified and link a filter and a handler to each one. Add your configuration changes to the `candidate` datastore and proceed to the next section.

#### Log filter configuration

In the `event-trigger` configuration added in the previous section a `filter` was specified. Add the `log filter` that is referenced to your candidate configuration. In the example solution, we don't filter out any events and simply allow every event through.

#### Event-handler configuration

Complete the log configuration with the `event-handler` referenced by the `event-trigger` object. These handler objects are used to tie together the triggering event to a set of actions to perform. In this case, that action will be the Python script we developed in the previous task. The `event-handler` should refer to a `script-policy` that will end up calling your Python script.

#### Script and script-policy

With the `log` configuration and the code ready, the `script` object to be referred to has to be created. The script was executed from SR OS already so we know the file is usable. Use some of the [SR OS Python documentation](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exgst4g){:target="_blank"} to configure your script as a precompiled Python application in the `candidate` datastore.

Finally, create the policy referenced by the event-handler from the previous step. To do this, add configuration to `/configure system script-control` that references the created `python-script` object. Once complete, `commit` your changes into the running datastore to make sure they are usable in the next section.

/// details | Solution - Script and EHS configuration
Commands required to make the necessary configuration updates:
```
edit-config private
    configure {
        log {
            event-handling {
                handler "lldp-description" {
                    admin-state enable
                    entry 10 {
                        script-policy {
                            name "lldp-description"
                        }
                    }
                }
            }
            event-trigger {
                lldp event tmnxLldpRemEntryPeerAdded {
                    admin-state enable
                    entry 10 {
                        filter "lldp-description"
                        handler "lldp-description"
                    }
                }
                lldp event tmnxLldpRemEntryPeerUpdated {
                    admin-state enable
                    entry 10 {
                        filter "lldp-description"
                        handler "lldp-description"
                    }
                }
            }
            filter "lldp-description" {
                default-action forward
            }
        }
        python {
            python-script "lldp-description" {
                admin-state enable
                urls ["cf3:/lldp_description.py"]
                version python3
            }
        }
        system {
            script-control {
                script-policy "lldp-description" owner "TiMOS CLI" {
                    admin-state enable
                    results "/null"
                    python-script {
                        name "lldp-description"
                    }
                }
            }
        }
    }
commit
quit-config
```
///

Commit your changes and make sure some (or all) of the port changes have been reverted so that your solution has some changes to make. The snippet from before is included for your convenience:

```
exit all
quit-config
edit-config global
/configure port 1/1/c1/1 description "first link to P1"
/configure port 1/1/c2/1 description "first link to P2"
/configure port 1/1/c3/1 description "first link spine11"
/configure port 1/1/c4/1 description "first link spine12"
commit
quit-config
```

#### Test your implementation

With everything in place, try bringing down and restoring an LLDP session to trigger your automation or changing a remote peer system name. As before, you may use a `private` configuration session to monitor for changes. Configuration groups have been used in the Hackathon topology, amongst other things for the LLDP configuration. This makes it so that a single change to that `group` configuration will affect every LLDP session. Alternatively, you can override the group configuration for a specific port by adding a single overriding configuration statement to a port.

/// Details | Bring down and recover LLDP neighborships
/// tab | For a single port
```
edit-config private
/configure port 1/1/c1/1 ethernet lldp dest-mac nearest-bridge receive false transmit false
commit
/configure port 1/1/c1/1 ethernet lldp dest-mac nearest-bridge receive true transmit true
commit
quit-config
```
///
/// tab | For a single port - example
```
(pr)[/]
A:admin@g23-pe2# # Bring down the LLDP session on port 1/1/c1/1

(pr)[/]
A:admin@g23-pe2# /configure port 1/1/c1/1 ethernet lldp dest-mac nearest-bridge receive false transmit false

*(pr)[/]
A:admin@g23-pe2# commit

(pr)[/]
A:admin@g23-pe2# # and restore it

(pr)[/]
A:admin@g23-pe2# /configure port 1/1/c1/1 ethernet lldp dest-mac nearest-bridge receive true transmit true

*(pr)[/]
A:admin@g23-pe2# commit
```
///
/// tab | For all ports
```
edit-config private
delete /configure apply-groups "lldp"
commit
/configure apply-groups "lldp"
commit
quit-config
```
///
/// tab | For all ports (example)
```
(pr)[/]
A:admin@g23-pe2# # Bring down the LLDP session on all ports by removing all LLDP configuration

(pr)[/]
A:admin@g23-pe2# delete /configure apply-groups "lldp"

*(pr)[/]
A:admin@g23-pe2# commit

(pr)[/]
A:admin@g23-pe2# # and restore the configuration to bring the sessions back

(pr)[/]
A:admin@g23-pe2# /configure apply-groups "lldp"

*(pr)[/]
A:admin@g23-pe2# commit

(pr)[/]
A:admin@g23-pe2#
```
///
///

Does your solution behave as expected? Before proceeding, make sure the `apply-group` or / and LLDP configuration is in the same state as it was originally in order not to interfere with any other activities.

Testing your script on `PE2` is well and good, however the real use case only becomes apparent once you make changes on neighboring nodes and let your automation pick up on the events.

Log in to `clab-srexperts-spine12` using SSH with the credentials provided to you and use the following snippet to update the system name:

```bash
enter candidate
system name host-name g23-dc1-spine12
commit stay
```

??? note "Expected outcome"
    ```bash
    --{ running }--[  ]--
    A:g23-spine12# enter candidate

    --{ candidate shared default }--[  ]--
    A:g23-spine12# system name host-name g23-dc1-spine12

    --{ * candidate shared default }--[  ]--
    A:g23-spine12# commit stay
    All changes have been committed. Starting new transaction.

    --{ + candidate shared default }--[  ]--
    A:g23-spine12#

    --{ + candidate shared default }--[  ]--
    A:g23-dc1-spine12#
    ```

Does the port description on port `1/1/c4/1` on node `PE2` get updated with this new information?

///details | Not working as expected?
    type: tip
If the port description is not getting updated as you expected, here are some tips on how to debug:

- Inspect system logs (`show log log-id 99`). Check if the LLDP peer added events are logged. Are there any EHS related errors spotted?
- Check operational status of the event-handler via `/show log event-handling handler ...`
- Check operational status of the python script via `/show python python-script ...`
- Check operational status of the script-policy via `/show system script-control script-policy ...`
///

### Adding logging to your script

Now that the port descriptions are being aligned whenever an LLDP peer appears, script extensions come into view. Because pySROS has the option to [read and write to and from files](https://documentation.nokia.com/sr/25-3/pysros/uio.html){:target="_blank"} on the filesystem and [custom log events](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/event-account-logs.html#custom_generic_log_events){:target="_blank"} can be raised as [modeled actions](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Connection.action){:target="_blank"}, we can extend the script functionality to write the data retrieved from the system to a file.

This gives us the option to compare the new state with the old state and to raise a log event should there be any changes. To test the functionality you can use the same steps as before to trigger your event-handler.

If you make any changes to your Python script, use `/perform python python-script reload script "lldp-description"` to load the changes into the Python object kept in memory. Once implemented, your implementation should be able to do the following:

```
233 2025/05/07 15:31:14.397 UTC MINOR: LOGGER #2022 Base lldp-nbr-change
"Changed 1/1/c4/1 from ['g23-spine12', 'ethernet-1/32'] to ('g23-dc01-spine12', 'ethernet-1/32')"
```

/// details | Solution - logging changes in learned LLDP neighbor information
```python
from pysros.management import connect
import json

def main():
    connection = connect(
        host="23.srexperts.net",
        username="admin",
        hostkey_verify=False,
        port=50422,
        password=#PROVIDED#
    )

    try:
        with open("cf3:/lldp-description-state.txt", "r+") as f:
            previous_result = json.loads(f.read())
    except:
        previous_result = {}

    data = connection.running.get('/state/port', filter = {
            "ethernet": {
                "lldp": {
                    "dest-mac": {
                        "remote-system": {
                            "system-name": { },
                            "remote-port-id": { }
                        }
                    }
                }
            }
        }
    )

    result = {}
    for key, value in data.items():
        relevant_context = value["ethernet"]["lldp"]["dest-mac"]["nearest-bridge"]["remote-system"]
        latest_entry = max(sorted(relevant_context.keys(), key=lambda x: x[0], reverse=True))
        result[key] = (str(relevant_context[latest_entry]["system-name"]), str(relevant_context[latest_entry]["remote-port-id"]))

    # Looking only at changes to LLDP neighbors (no new ports)
    for port in previous_result:
        if list(result[port]) != list(previous_result[port]):
            connection.action("/nokia-oper-perform:perform/log/custom-event",
            {
                "event-number": 3,
                "subject": "lldp-nbr-change",
                "message-string": "Changed %s from %s to %s" % (port, previous_result[port], result[port]),
            })

    with open("cf3:/lldp-description-state.txt", "w+") as f:
        f.write(json.dumps(result))

    port_path = "/nokia-conf:configure/port[port-id=\"PORT_ID\"]"
    for key, value in result.items():
        connection.candidate.set(
            port_path.replace("PORT_ID", key),
            { "description": "connected to port %s of %s" % (value[1], value[0])},
            commit=False
        )
    connection.candidate.commit()

if __name__ == "__main__":
    main()

```
///

### Using LLDP to communicate?

Briefly take inventory of what you have built so far:

- Looking at LLDP information received from neighbors
- Changing local `port description` configuration based on received LLDP information
- Tracking changes in the LLDP information received per port

With these elements and knowing that `port-description` is among the information exchanged via LLDP there should be a possibility to communicate generic information between nodes. If you want to go further, you could investigate this and see if you can get it to work (there is no example solution provided for this).

## Summary and review

Congratulations!  If you made it this far you have completed this activity and achieved the following:

- You have used a remote system with pySROS to connect to a model-driven SR OS device
- You have written or modified one or more applications using the Python 3 programming language
- You have used the model-driven CLI for changing configuration in SR OS
- You have made the behavior of SR OS dynamic using the event handling system

This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity, or try a similar activity on SR Linux: ([Event-handling on SR Linux](../../srlinux/intermediate/nos-srl-activity-12.md){:target="_blank"}).

In this activity we briefly covered some of the aspects of creating EHS automation.  The script required some iterations before it behaved as expected.  We are able to test code outside of the EHS environment which helped us develop quickly and efficiently. We only used the event as a trigger and didn't rely on any other inputs provided by it, and our script didn't generate any output. [Another activity](../intermediate/nos-sros-activity-62.md) explores this area further.