---
tags:
  - SR OS
  - pySROS
  - Python
  - MD-CLI
  - alias
  - pyexec
  - configuration
  - EHS
---

# Automatically update prefix-lists when BGP peer configuration changes


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Automatically update prefix-lists when BGP peer configuration changes                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Activity ID**             | 21                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Short Description**       | With model-driven SR OS and pySROS we can extend the CLI. One area where that can come in handy updating configuration elements that depend on other configuration elements being updated and kept in line to function properly.                                                                                                                                                                                                                                                                                                                                                        |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/), [Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html), [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html), [Python programming language](https://www.python.org)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: PE1                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html)<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/system-management.html)<br/>[pySROS user documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)<br/>[pySROS GitHub](https://github.com/nokia/pysros) (check the examples directory)<br/>[Event handling system](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/event-account-logs.html#ai9exj5x1x)|


Ever lost time troubleshooting a BGP session that wasn't coming up while everything seemed to be configured correctly, only to find a CPM filter entry that wasn't updated to allow the peering? Similar situations can arise with other protocols like BFD or NTP and in general this is not something we want to worry about. Fortunately, with model-driven SR OS and its on-board Python interpreter we can build a solution for this issue. In this activity, we will explore how that solution might look and different ways it could be applied.

## Objective

The following tasks will help you build a complete solution and introduce you to the challenges you have to solve along the way.

1. Build a pySROS script that runs remotely and analyzes the target SR OS node's configuration and creates prefix-lists
2. Adapt the resulting pySROS script into an MD-CLI alias that can be executed as a command within the SR OS MD-CLI
3. Make the SR OS configuration reactive using event-handlers so that the prefix-lists are brought up to date whenever the node configuration is changed

## Technology explanation

To reach our goal of getting more comfortable with automating model-driven SR OS, in this case by automating away some complexity, we can't forego understanding the fundamentals and keeping track of how everything fits together. In this section we highlight the elements of the system that will be useful when going through the tasks in this activity.

### SR OS Event Handling System

The Event Handling System or EHS has been a part of SR OS for many years. The capability to trigger pySROS applications to handle events has been added and that greatly increases the logic that can go into these handlers. For **Objective 3** we will look at using this functionality.

Conceptually, an event generated by the system can be tied into an execution of a pySROS application. The pySROS application uses that event as input and has the standard pySROS on-box functionality available.

As we will see in the later part of the activity, and as [documented](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/event-account-logs.html#ai9exj5x1x), the EHS requires some configuration to be functional. This will be part of **Objective 3**.

### MD-CLI pyexec command

The SR OS MD-CLI `pyexec` command allows operators to run a Python 3 application on the SR OS node by providing a filename as input or the name of a python-script configured in the MD-CLI.

Example uses: ```pyexec cf3:/myscript.py``` or ```pyexec my-script-name```

The [SR OS system management guide](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exgst4k) provides more information on its use.

### MD-CLI alias

SR OS MD-CLI command aliases provide a way for an operator to customize the user-experience of an SR OS node by renaming commands, creating shortcut aliases to existing commands or integrating custom developed commands directly into the MD-CLI with context sensitive help, auto-completion and the other user interface features operators love about SR OS. These aliases can be made permanent via configuration.

The [MD-CLI command reference guide](https://documentation.nokia.com/sr/25-3/7750-sr/books/md-cli-command-reference/environment_0.html#d67300) and the [SR OS system management guide](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exj5x8z) contain more information.

### Developing Python scripts

Python applications can be written in the form of a file or a combination of several files and are generally structured as reusable modules or packages. For use within model-driven SR OS, the possibilities narrow slightly as scripts exist as a single file and the modules that can be imported are determined by the system. Python scripts using pySROS can be executed either locally on the box or remotely from a Python-capable machine in which case pySROS also handles the connection to the remote model-driven SR OS node. The behavior for local and remote execution is designed to be similar. This allows development efforts to take place on a system like your personal laptop or a shared scripting server, rather than needing to be done on the node directly. In this Hackathon, the VM you are given access to can be used as a development environment.

For **Objective 1**, we will follow the approach of implementing and testing the solution before integrating it into node `PE1`.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Prepare your Python virtual environment

If you are able to, we recommend completing this activity using your local machine as a development environment. This task helps you prepare for that. Should you be unable or want to move on quickly, your group's hackathon VM comes pre-installed with the necessary libraries for this activity. By switching to your group's hackathon VM for development you can skip the remainder of this task.

Several tools exist that make programming in Python a smooth experience. Among those are `pip`, `venv` and `uv`. In the example walkthrough we use `uv` on WSL for the preparations. Begin by creating a directory that will hold any files related to this activity and creating a virtual environment there. Install the pySROS library into that virtual environment.

/// details | Preparing your local environment
/// tab | Commands
```bash
sudo apt install python3-pip #if needed
pip install uv #if needed
mkdir usecase
cd usecase
uv venv env
source env/bin/activate
```
///
/// tab | Outputs
```
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

The prompt changes and shows the name of the virtualenv at the start of the prompt. The virtual environment can be exited using the `deactivate` command. From within this virtual environment, we need to install the `pySROS` library to interact with model-driven SR OS remotely. Install it using `pip`.

/// details | Installing pySROS
/// tab | Command
```
uv pip install pysros
```
///
/// tab | Outputs
```
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

### Using the interactive Python interpreter to interact with `PE1`

Interactive Mode, also known as REPL or the interactive interpreter shell.

Open an [interactive](https://docs.python.org/3/tutorial/appendix.html#tut-interac) Python interpreter session using the `python` command in your chosen development environment and import the `connect` method from the pySROS library. Use it to open a connection to SR OS node `PE1`.

If you are working on your group's hackathon VM you can use the default NETCONF port value which is 830 and the target hostname `clab-srexperts-pe1`.

If you are using your own platform outside the hackathon environment you can make use of the port forwarding set up as part of the containerlab topology. For `PE1` the NETCONF port is mapped to your group's hackathon VM's port 50421. This means that when connecting to your assigned hackathon VM on the aforementioned port, we will reach `PE1`'s NETCONF port. This is information we need, since pySROS uses NETCONF for connecting to the node when running remotely.

Once the connection object has been created, try to `get` the system's `oper-name` attribute from the running datastore to confirm we reached the correct node.

/// details | Connecting and executing a basic get
```bash
(env) wsl-ubuntu: python
Python 3.10.12 (main, Jan 17 2025, 14:35:34) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from pysros.management import connect
>>> connection = connect(host="21.srexperts.net", username="admin", hostkey_verify=False, password=#PROVIDED#, port=50421)
>>> connection.running.get('/state/system/oper-name')
Leaf('g21-pe1')
```
///

/// admonition | Host key verification
    type: warning
As you can see from the example output or as you might have noticed, the `hostkey_verify` keyword parameter for the `connect` call is set to `False`. This makes us vulnerable to man-in-the-middle attacks. The alternative to disabling the verification is explicitly connecting to each node on the desired port and saving the associated key, however for lab environments that are cleaned up and recreated regularly this is not efficient. In addition, the danger of this vulnerability is lessened greatly in such lab environments. In any live network environment `hostkey_verify` should be set to `True`.
///

### Build logic within the interactive interpreter

Continue with the interactive session from the previous task. Now that you have seen how to retrieve information from the system, think back to the problem we are trying to solve.

When we add a BGP neighbor to the configuration, that particular peer may not come up due to the implementation of an ACL that wasn't yet updated to include the new neighbor's IP address. Clearly something that can be easily solved, but figuring out the root cause may take some time that could be better spent elsewhere.

In the next steps we will build automation that prevents this problem. The configuration contexts in which BGP neighbors can be established can be considered either in the `Base` routing instance or in a VPRN service. As such, consider the following paths as the ones to look for neighbors in:

- `/nokia-conf:configure/router[router-name="Base"]/bgp`
- `/nokia-conf:configure/service/vprn[service-name="*"]/bgp`

Use your pySROS session to collect the relevant configuration information from the `running` datastore.

You may find the use of

??? tip "Optimizing pySROS calls"
    Since, for the `Base` routing instance, we know the router-name in which we are looking you could use the [`get_list_keys` function](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.get_list_keys).

    For VPRN services the same is not true, as the service name could be anything and a regular [`get`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.get) call is required. This can be optimized using [selection node filters](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros-management-datastore-get-example-selection-node-filters) to retrieve less data in total.

/// details | Finding the bgp neighbor configuration with pySROS
```
>>> connection.running.get_list_keys('/nokia-conf:configure/router[router-name="Base"]/bgp/neighbor')
['10.64.51.2', '10.64.54.0', 'fd00:fc00:0:51::2', 'fd00:fde8::23:11', 'fd00:fde8::23:12', 'fd00:fde8::23:13', 'fd00:fde8:0:54::']
>>> connection.running.get('/nokia-conf:configure/service/vprn', filter= {"bgp": { "neighbor": { "ip-address": {}} } })
{'dci': Container({'service-name': Leaf('dci'), 'bgp': Container({'neighbor': {'12.3.3.3': Container({'ip-address': Leaf('12.3.3.3')})}})})}
```
///

### Create prefix-list configuration
Prefix lists to be used in SR OS are configured in the `configure filter match-list` context. Find the correct translation of this path for use in your Python interpreter such that the interpreter is able to create `ip-prefix-list` and `ipv6-prefix-list` objects. Use that path and an appropriate dictionary to create 2 match-lists (one for ipv4, another for ipv6) that include all BGP neighbors you found in the previous step.

One possible method for determining the expected structure and hierarchy of data that needs to be put in a [`set`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.set) call is by configuring the desired state on SR OS and using `get`. The output retrieved from the system will contain the configuration converted into the correct Python object, allowing you to go from there by building on top of known good information.

/// details | Create match lists
```python
>>> import ipaddress
>>> ipv4_peers, ipv6_peers = set(), set()
>>> peers = connection.running.get_list_keys('/nokia-conf:configure/router[router-name="Base"]/bgp/neighbor')
>>> svc_peers = connection.running.get('/nokia-conf:configure/service/vprn', filter= {"bgp": { "neighbor": { "ip-address": {}} } })
>>> for k,v in svc_peers.items():
...  if "neighbor" not in v["bgp"].keys():
...    continue
...  for address in v["bgp"]["neighbor"].keys():
...    peers.append(address)
...
>>> for peer in peers:
...  if ipaddress.ip_address(peer).version == 4:
...    ipv4_peers.add(peer)
...  else:
...    ipv6_peers.add(peer)
...
>>> ipv4_peers
{'10.64.51.2', '10.64.54.0'}
>>> ipv6_peers
{'fd00:fde8::23:12', 'fd00:fde8:0:54::', 'fd00:fde8::23:13', 'fd00:fde8::23:11', 'fd00:fc00:0:51::2'}
>>> path = '/nokia-conf:configure/filter/match-list/ip-prefix-list[prefix-list-name="pysros-match-list"]'
>>> payload = { "prefix": { "%s/32"%peer: {"ip-prefix": f"%s/32"%peer} for peer in ipv4_peers } }
>>> connection.candidate.set(path, payload, commit=False)
>>> path = '/nokia-conf:configure/filter/match-list/ipv6-prefix-list[prefix-list-name="pysros-match-list"]'
>>> payload = { "prefix": { "%s/128"%peer: {"ipv6-prefix": "%s/128"%peer} for peer in ipv6_peers } }
>>> connection.candidate.set(path, payload, commit=True)
```
///

To complete this step, exit your interactive Python shell once you confirm that the configuration exists in the target SR OS node, `PE1`. You can do this using your pySROS connection or simply by logging in to the node.

!!! tip "Private candidate"
    One of the four configuration modes available in model-driven SR OS is [`private`](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/edit-configuration.html#ai89jylu08). A handy feature of this mode is that once you enter it using `edit-config private`, whenever someone or something else makes any changes your view of the running datastore won't automatically be updated. You are instead presented with a `!` at the start of your prompt, indicating there have been changes since your session began or was last updated.

    At that point, you can use `compare baseline running` to view these changes and `update /configure` allows you to pull the changes into your session. The example solution uses this approach to see changes made to the running datastore easily, without having to look up individual paths.

#### Apply your prefix-list configuration

By default, the creation you have now created is not used anywhere. In this optional subtask we will use the created match-list to populate an entry in the `cpm-filter` on `PE1`. We will use entries that are set to `accept` with a `default-action accept` so as not to impact the topology routing or lock ourselves out of the system.

```
*(pr)[/]
A:admin@pe1# compare /
    configure {
        system {
            security {
+               cpm-filter {
+                   default-action accept
+                   ipv6-filter {
+                       admin-state enable
+                       entry 10 {
+                           match {
+                               router-instance "Base"
+                               src-ip {
+                                   ipv6-prefix-list "pysros_match_list"
+                               }
+                           }
+                           action {
+                               accept
+                           }
+                       }
+                   }
+               }
            }
        }
    }
```

If you're using this approach you can check the effect and correctness of your prefix list using the following commands:

- `/show system security cpm-filter ipv6-filter entry 10`
- `/show router bgp summary`

The BGP sessions remain active and the `default-action accept` acts as a safety net, however if you remove the entries from your created match list you'll notice the counter on the entry stops incrementing.

### Wrap it into a script

Create a new file in your current working directory and add the Python code you have written in the previous steps. This Python script should achieve the same end result as what you had at the end of the previous step. In the example solution, we use `match_lists.py`. Delete some `match-list` configuration or add a BGP peer to the `dci` service and run your script as `python match_lists.py` from within your Python virtual environment. Confirm that the results are in line with your expectation.

/// details | Expected outcome
/// tab | Expected execution
```bash
python match_lists.py
```
///
/// tab | Expected result (using private candidate)
```
!(pr)[/]
A:admin@g21-pe1# compare baseline running
    configure {
        filter {
            match-list {
+               ip-prefix-list "pysros_match_list" {
+                   prefix 10.64.51.2/32 { }
+                   prefix 10.64.54.0/32 { }
+               }
+               ipv6-prefix-list "pysros_match_list" {
+                   prefix fd00:fc00:0:51::2/128 { }
+                   prefix fd00:fde8::23:11/128 { }
+                   prefix fd00:fde8::23:12/128 { }
+                   prefix fd00:fde8::23:13/128 { }
+                   prefix fd00:fde8:0:54::/128 { }
+               }
            }
        }
    }
```
///
/// tab | File `match_lists.py` content
```python
from pysros.management import connect
import ipaddress

def main():
    connection = connect(
        host="21.srexperts.net",
        username="admin",
        hostkey_verify=False,
        port=50421,
        password=#PROVIDED#
    )
    ipv4_peers,ipv6_peers = set(),set()
    peers = connection.running.get_list_keys('/nokia-conf:configure/router[router-name="Base"]/bgp/neighbor')
    svc_peers = connection.running.get('/nokia-conf:configure/service/vprn', filter= {"bgp": { "neighbor": { "ip-address": {}} } })
    for k,v in svc_peers.items():
      if "neighbor" not in v["bgp"].keys():
        continue
      for address in v["bgp"]["neighbor"].keys():
            peers.append(address)
    for peer in peers:
        if ipaddress.ip_address(peer).version == 4:
            ipv4_peers.add(peer)
        else:
            ipv6_peers.add(peer)
    if ipv4_peers:
        path = '/nokia-conf:configure/filter/match-list/ip-prefix-list[prefix-list-name="pysros_match_list"]'
        payload = { "prefix": { "%s/32"%peer: {"ip-prefix": "%s/32"%peer} for peer in ipv4_peers } }
        connection.candidate.set(path, payload, commit=False)
    if ipv6_peers:
        path = '/nokia-conf:configure/filter/match-list/ipv6-prefix-list[prefix-list-name="pysros_match_list"]'
        payload = { "prefix": { "%s/128"%peer: {"ipv6-prefix": "%s/128"%peer} for peer in ipv6_peers } }
        connection.candidate.set(path, payload, commit=True)

if __name__ == "__main__":
    main()
```
///
///

### Copy the script to the target SROS node `PE1`

Having built up the code, we can now copy it onto our model-driven SR OS `PE1` node. Copy your `match_lists.py` file over to the router using `scp` or another method and make sure your file is available on the router before proceeding. If you are developing on your own platform, the port mapped to `PE1`'s port 22 is `50021`. If you are working on your group's hackathon VM you can go directly to `clab-srexperts-pe1`.

??? note "SR OS tftpboot"
    In the hackathon environment the `/home/nokia/clab-srexperts/pe1/tftpboot/` directory on the hackathon VM instance is reachable from within SR OS as the TFTP location, `tftp://172.31.255.29/`.  The result of this is that any file you put in that folder will be accessible from within SR OS using TFTP. This could be used as an alternative to `scp` or manually copying over the file contents.

Once your file is prepared and reachable, run it with `pyexec` on `PE1` to make sure it still works as expected.

/// details | Running your script with `pyexec`
```
[/]
A:admin@g21-pe1# edit-config private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(pr)[/]
A:admin@g21-pe1# pyexec cf3:/match_lists.py

!(pr)[/]
A:admin@g21-pe1# compare baseline running
    configure {
+       filter {
+           match-list {
+               ip-prefix-list "pysros_match_list" {
+                   prefix 10.64.51.2/32 { }
+                   prefix 10.64.54.0/32 { }
+               }
+               ipv6-prefix-list "pysros_match_list" {
+                   prefix fd00:fc00:0:51::2/128 { }
+                   prefix fd00:fde8::23:11/128 { }
+                   prefix fd00:fde8::23:12/128 { }
+                   prefix fd00:fde8::23:13/128 { }
+                   prefix fd00:fde8:0:54::/128 { }
+               }
+           }
+       }
    }
```
///

### Create the alias

A next step, now that we are able to use our code from within SR OS, is to make it into an `alias`. With that completed, a simple short-hand command can be used to align configuration to any BGP peers added to the configuration. That saves us from having to remember filenames and URLs and gives fellow operators the ability to use your code as if it were a command built in to the model-driven CLI.

Use the [documentation](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/navigate.html#concept_hkg_hb3_bqb) for command aliases to create an alias called `align-prefix-lists` that is mounted under the `tools` context and calls a `python-script` object that calls your script file. You'll also have to create this `python-script` object. Test and make sure that the alias works the same as the `pyexec` approach by removing some prefixes from the previously created prefix-lists or by creating new BGP peer entries.

/// details | Solution - creating an alias
```
*[pr:/configure]
A:admin@g21-pe1# compare /
    configure {
+       python {
+           python-script "align-prefix-lists" {
+               admin-state enable
+               urls ["cf3:/match_lists.py"]
+               version python3
+           }
+       }
        system {
            management-interface {
+               cli {
+                   md-cli {
+                       environment {
+                           command-alias {
+                               alias "align-prefix-lists" {
+                                   admin-state enable
+                                   python-script "align-prefix-lists"
+                                   mount-point "/tools" { }
+                               }
+                           }
+                       }
+                   }
+               }
            }
        }
    }
*[pr:/configure]
A:admin@g21-pe1# commit

[pr:/configure]
A:admin@g21-pe1# logout
INFO: CLI #2074: Exiting private configuration mode

... <log back in>

[/]
A:admin@g21-pe1# /tools

 align-prefix-lists  dump  perform
```
///

### Make it automated

Having the `align-prefix-lists` command at your fingertips is quite handy, but we can skip this step entirely! Look into the documentation for the [`event handling system (EHS)` ](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/event-account-logs.html#ai9exj5x1x) and implement an `event-handler` that is triggered by successful commit events and calls your script. This task is split up into several subtasks as several elements have to be added to the configuration.

!!! warning "Event-handlers triggering event-handlers"
    Keep in mind that your code may not be reusable for the EHS application in its current state. If your script is triggered by a commit event and it triggers another commit event you may create a loop. Something should prevent commits triggered for your reactive configuration from triggering additional executions of the application.

#### Find the correct event and create an `event-trigger`

To handle any events, we must try to narrow down the exact event to handle. In this case, the straightforward option is to trigger an execution any time anything is committed to the system configuration.

Look for the correct event using the MD-CLI or by browsing through the [Log Events Search Tool](https://documentation.nokia.com/sr/25-3/log-events-search/events.html).

Configure an `event-trigger` to be raised for the `commit` event that references a filter and a handler but don't commit your changes yet, the filter and handler configuration will be configured in the coming subtasks.

#### Create a log `filter`

The event-trigger refers to two additional elements that need to be present in the configuration before we can start using it. In this section we will create the required filter. For this activity, and given that the commit event doesn't have much we can filter on, we pass all events. Do note that this filter could be configured to filter on severity and content of the log events which may be useful for more complex scenarios.

#### Create an `event-handler`

Next, create the second element referenced and required by the event-trigger, an `event-handler`. This object will trigger a script-policy and passes the event as an input.

#### Create a `script-policy`

The last element required to make our solution autonomous is a `script-policy`. In the previous step, when creating the alias, we already created and used a `python-script` object. The same object will be used now, the only configuration that needs to be added is the bridge between the `event-handler` and the `python-script`.

Create the `script-policy` and review your changes, make sure anything that needs to be set to `admin-state enable` has been set. Note that because we do not expect any output from the script currently, we use `/null` for the results location. This is the SR OS equivalent of the well-known `/dev/null` in Linux.

??? tip "Troubleshooting and testing"
    If you were able to commit the configuration without any complaints yet you don't see your `match-list` configuration update after you `commit`, there may be something wrong.

    Good places to look include:

    - `log 99`, using `/show log log-id 99`. There should be entries corresponding to your commits and the subsequent event-trigger
    - the `event-handler`, as it doesn't boast much in the way of configuration but all information is linked to it. Use `/show log event-handling information` to see if you can find an issue.
    - the `script-policy`, as we had already verified in the previous task that the `python-script` works by way of the alias. Use `/show system script-control script-policy "match_lists"` to identify issues.

??? note "Solution - required configuration changes"
    ```
    *[pr:/configure]
    A:admin@g21-pe1# compare /
        configure {
            log {
                event-handling {
                    handler "match_lists" {
                        admin-state enable
                        entry 10 {
                            script-policy {
                                name "match_lists"
                            }
                        }
                    }
                }
                event-trigger {
                    system event mdCommitSucceeded {
                        admin-state enable
                        description "event-trigger for activity #21"
                        entry 10 {
                            filter "10"
                            handler "match_lists"
                        }
                    }
                }
                filter "10" {
                    default-action forward
                }
            }
            system {
                script-control {
                    script-policy "match_lists" owner "TiMOS CLI" {
                        admin-state enable
                        results "/null"
                        python-script {
                            name "align-prefix-lists"
                        }
                    }
                }
            }
        }
    ```

#### Test the functionality

Commit your changes and make sure the different elements are operationally up. Add BGP peer `192.168.0.1` to the service `dci` configuration. Was your match-list configuration updated?

/// details | Testing your implementation
```
[/]
A:admin@g21-pe1# edit-config private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(pr)[/]
A:admin@g21-pe1# configure service vprn dci bgp group neighbor

*(pr)[/configure service vprn "dci" bgp group "neighbor"]
A:admin@g21-pe1# /configure service vprn dci bgp neighbor 192.168.0.1 group "neighbor"

*(pr)[/configure service vprn "dci" bgp group "neighbor"]
A:admin@g21-pe1# commit

!(pr)[/configure service vprn "dci" bgp group "neighbor"]
A:admin@g21-pe1# compare baseline running /
    configure {
        filter {
            match-list {
                ip-prefix-list "pysros_match_list" {
+                   prefix 192.168.0.1/32 { }
                }
            }
        }
    }
```
///

Remove the previously added BGP peer from your configuration and commit the changes. Does your configuration look as you had expected?

/// details | The removed BGP peer is still in my prefix list configuration
Not to worry! That is the expected situation if you have followed the example solution. By default, any changes made via any of the model-driven interfaces use the `merge` operation. If the removed BGP neighbor's IP address is still present after the neighbor was removed, change your implementation to use the `replace` operation instead. Use `perform python python-script reload script "align-prefix-lists"` to load any changes and try again.
///

## Summary and review

Congratulations!  If you have got this far you have completed this activity and achieved the following:

- You have used a remote system with pySROS to connect to model-driven SR OS
- You have written or modified one or more applications using the Python 3 programming language
- You have used the model-driven CLI for changing configuration in SR OS
- You have created an alias in model-driven SR OS that exposes your code as if it were a native command
- You have made the behavior of SR OS dynamic using the event handling system

This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity, or try to expand upon this one if you have some more ideas.
