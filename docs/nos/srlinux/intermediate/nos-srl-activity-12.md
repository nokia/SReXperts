---
tags:
  - SR Linux
  - Python
  - Event handler
  - MicroPython
  - Programmability
---

# Automatic update of interface descriptions using the event handler
|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Automatic update of interface descriptions using the event handler                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **Activity ID**             | 12                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **Short Description**       | Use the SR Linux Event handler to automatically update interface descriptions when LLDP information changes and provision inter-switch links (ISLs).                                                                                                                                                                                   |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR Linux Event handler](https://documentation.nokia.com/srlinux/25-3/books/event-handler/event-handler-overview.html#undefined){:target="_blank"}, [MicroPython](https://micropython.org/){:target="_blank"}, [SR Linux CLI](https://documentation.nokia.com/srlinux/25-3/books/system-mgmt/cli-interface.html#cli-interface){:target="_blank"}                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: spine12                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [Event Handler Guide](https://documentation.nokia.com/srlinux/25-3/title/event-handler-guide.html#undefined){:target="_blank"}<br>[MicroPython docs](https://docs.micropython.org/en/latest/){:target="_blank"}<br>[SR Linux YANG browser](https://yang.srlinux.dev/v25.3.1){:target="_blank"}<br>[SR Linux CLI documentation](https://documentation.nokia.com/srlinux/25-3/books/system-mgmt/cli-interface.html#cli-interface){:target="_blank"}<br>|


## Objective

This activity will explore event-handler features to implement the following 2 use-cases:

- Auto-update interface descriptions based on LLDP information received from peers.
- Automatically provision ISLs (Inter-switch links) for underlay configuration based on the LLDP neighbor system name

## Technology explanation

In this activity, in addition to using the SR Linux CLI, you will be working with the Python programming language from the development environment of your choosing. A basic level of Python and Linux OS proficiency is assumed for this activity. The key technologies that this activity might include are summarized and briefly described in the next sections.

### LLDP

LLDP is a vendor-agnostic link layer protocol used by network devices to advertise information about their identity to their directly connected neighbors. One of its most common uses is being able to identify which nodes are connected to a given node for troubleshooting purposes by using commands similar to `show system lldp neighbor`.

### SR Linux Event handler
Event handler is a framework that enables SR Linux to react to specific system events, using programmable logic to define the actions taken in response to the events.<p>
The event handler framework allows you to write custom scripts that are invoked when specific events occur, such as when a port goes operationally down. The scripts can generate a list of actions for the SR Linux device to execute. The actions can include updating the SR Linux configuration, changing the operational state of a group of ports, executing a tools command, or running another script. Both the input passed to the script and the output generated by it are in `JSON` format.<p>
The core building blocks of an event-handler instance are:

- The **configuration**, which specifies specific system state data to monitor.
- The **script**, which is responsible for processing the system state data and defining actions.

SR Linux supports multiple independent event-handler instances

It's important to read [Event handler overview](https://documentation.nokia.com/srlinux/25-3/books/event-handler/event-handler-overview.html){:target="_blank"} to understand the fundamental architecture of event-handler before starting the tasks.<p>
<i id=script-loc></i>
/// note | Scripts location
The event handler can read scripts from the following locations:

 - ```/opt/srlinux/eventmgr/``` - Nokia-provided scripts that come pre-installed with SR Linux
 - ```/etc/opt/srlinux/eventmgr``` - user-provided scripts
/// tip
The ```/etc/opt/srlinux/eventmgr``` directory is directly accessible on your group's hackathon VM filesystem at <br/>```~/clab-srexperts/spine12/config/eventmgr```<br>
This allows you to edit scripts directly from the host using remote editing capabilities of Visual Studio Code or any other editor.
///
///

### YANG data models
SR Linux makes extensive use of structured YANG data models to provide network operators with a single set of data models to configure and manage commonly-used network protocols, services, and devices. Each application that SR Linux supports has a Nokia vendor-specific YANG model that defines the application's configuration and state.<p>

The Event Handler listens for system events by monitoring changes in configured YANG paths. It is the operator that decides and configures which YANG paths a particular event-handler instance will be monitoring. The [SR Linux YANG browser](https://yang.srlinux.dev/v25.3.1){:target="_blank"} is a great tool to explore all the YANG paths available in SR Linux. The SR Linux CLI can also be used to explore this.

### SR Linux CLI interface
The SR Linux CLI (`sr_cli` app) is an interface for configuring, monitoring, and maintaining the SR Linux system. In summary, the user is able to switch between the following modes:

- **Candidate** – Use this mode to modify a configuration. Modifications are not applied to the running system until a commit command is issued. When committed, the changes are copied to the running configuration and become active.
- **Running** – Use this mode to display the currently running or active configuration. Configurations cannot be edited in this mode. This is the default mode.
- **State** – Use this mode to display the configuration and operational states. The state mode displays more information than show mode.
- **Show** – Use this mode to display configured features and operational states. The show mode information is shown in a more human-centric format.

**State** is the most useful mode to discover and inspect the YANG paths to be monitored by the event-handler.<p>
While working on the activity tasks you might want to switch to the onboard **Linux bash shell** occasionally. Enter `bash` (from SR Linux CLI) to launch a Linux bash shell.

For more information about SR Linux CLI, check [SR Linux CLI documentation](https://documentation.nokia.com/srlinux/25-3/books/system-mgmt/cli-interface.html#cli-interface){:target="_blank"}

### MicroPython (also referred to as uPython)
Event Handler Scripts are written in MicroPython.<p>
MicroPython is a lean and efficient implementation of the Python 3 programming language that includes a small subset of the Python standard library and is optimized to run on microcontrollers and in constrained environments.<p>

If additional logic is needed that isn't feasible to do in the uPython script, you can invoke an external program (via the [run-script action](https://documentation.nokia.com/srlinux/25-3/books/event-handler/event-handler-scripts.html#actions){:target="_blank"}). This basically runs an arbitrary command in a Linux shell with optional arguments passed.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.<p>

To log in to `spine12` for the below activity, you can use SSH from your group's hackathon VM, as below:

```bash
ssh admin@clab-srexperts-spine12
```

If desired, you can also SSH directly to your assigned VM's port `50032` as that port is forwarded to `spine12` port `22` in the topology.

### Reflect LLDP neighbor on interface descriptions

Create an event-handler that monitors LLDP neighbors' ```system-name``` and ```port-id``` attributes and automatically uses this information to configure the matching interface descriptions. For simplicity, assume that only one neighbor can exist per interface. An example is shown below.

/// tab | Example LLDP neighbor

``` bash hl_lines="5 9"
A:g15-spine12# info from state / system lldp interface ethernet-1/2 neighbor *
    neighbor 1A:2D:0E:FF:00:00 {
        first-message "2025-03-31T15:58:54.654Z (a day ago)"
        last-update "2025-04-02T14:53:31.623Z (22 seconds ago)"
        system-name g15-leaf12
        system-description "SRLinux-v24.10.3-201-g9d0e2b9371 g15-leaf12 6.1.0-32-cloud-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.129-1 (2025-03-06)"
        chassis-id 1A:2D:0E:FF:00:00
        chassis-id-type MAC_ADDRESS
        port-id ethernet-1/50
        port-id-type INTERFACE_NAME
        port-description leaf12-spine12
        capability ROUTER {
            enabled true
        }
    }
```

///
/// tab | Expected Result
Based on the LLDP information, the description of interface `ethernet-1/2` description should automatically be updated.
``` bash
A:g15-spine12# info from running / interface ethernet-1/2 description
    description "g15-leaf12|ethernet-1/50"
```
///

/// admonition | Stop and take time to think here
    type: question
 - What YANG paths should you monitor? The state output above might give you an idea, but how you will specify them in the event-handler instance configuration?
 - What kind of actions does the event-handler script need to output?
///

///tip
Check the scripts inside the [`Nokia-provided`](#script-loc) folder to see if any could be useful for this task. <br>
If you find a useful script and want to modify it, copy it to the [`user-provided`](#script-loc) scripts folder and change its name, before making changes.<p>

You can enter a Linux `bash` shell to explore/copy files.<br>
Alternatively you can use the CLI `file` command. Use `file ?` to see the available options.
///


#### Configure the event-handler instance
Go into `candidate` mode and create an event-handler instance.<p>

/// details | Getting help on navigating in `candidate` mode
    type: tip

To get help on how to navigate and apply configurations in `candidate` CLI mode, check out the documentation on [configuration modes](https://documentation.nokia.com/srlinux/25-3/books/system-mgmt/cli-interface.html#configuration-modes-system-mgmt){:target="_blank"}
///

/// details | Getting help on configuring event-handler
    type: tip

 - Check [Event handler configuration documentation](https://documentation.nokia.com/srlinux/25-3/books/event-handler/event-handler-configuration.html#event-handler-config){:target="_blank"} for examples and understanding of the various options
 - Nokia-provided scripts typically include examples at the beginning of the file on how the event-handler should be configured.
///

///note
The uPython script doesn't need to be complete at this stage
///

Before advancing to the next step, confirm that your configuration changes have been applied.
/// details | Hint - Checking if the configuration has been applied
    type: tip

Check the event-handler path under `running` or `state` modes. For example `info from state / system event-handler instance <name>`
/// details | Expected output
```
--{ + candidate shared default }--[ system event-handler instance jmac ]--
A:g15-spine12# info from state
    admin-state enable
    upython-script auto-ifdesc.py
    oper-state down
    paths [
        "system lldp interface * neighbor * port-id"
        "system lldp interface * neighbor * system-name"
    ]
    options {
        object interfaces {
            values [
                ethernet-1/{1..200}
            ]
        }
    }
    last-execution {
        oper-down-reason script-unavailable
        oper-down-reason-detail ""
        start-time "2025-05-09T12:57:34.810Z (11 seconds ago)"
        end-time "2025-05-09T12:57:34.816Z (11 seconds ago)"
        upython-duration 4
(...truncated...)
```
///
///

#### Create the script
It's time to develop the MicroPython script logic. If you found a useful script in the [`Nokia-provided`](#script-loc) scripts folder, that's great - it will save you a lot of work! Equally, if you want to go it alone, that's great as well!

/// details | Getting help
    type: tip

- Check out the [event-handler scripts documentation](https://documentation.nokia.com/srlinux/25-3/books/event-handler/event-handler-scripts.html#scripts){:target="_blank"}
- Inspect Nokia-provided scripts examples
///

/// details | Reloading the script
    type: tip

After modifying the script content, make sure to reload the event-handler instance for the changes to take effect. <br/>Use `/tools system event-handler instance <name> reload` to do it.<br>
Note that each time an event-handler is reloaded or transits from admin-disabled to admin-enabled, the YANG paths are re-read and the associated script is executed at least once.
///

Test the event-handler and verify that it behaves as expected before proceeding to the next task.

/// details | debugging script errors
    type: tip

It is possible you may encounter errors while testing the script.
As the first step in troubleshooting, check the information provided by `info from state / system event-handler instance <name>`:

- ```last-execution``` displays information about the last execution regardless of the outcome while ```last-errored-execution``` contains only information about the last failed execution. Both contain script runtime ```input/output``` information.
-  ```stdout-stderr``` is useful to view output generated by ```print()``` functions.
-  ```last-errored-execution``` additionally includes ```oper-down-reason-detail```, which displays the direct reason for failure.
///

#### Mark stale information
Add a feature to flag interface description as stale when the associated LLDP neighbor session is terminated.

``` bash title="expected interface description after an LLDP neighbor expires"
A:g15-spine12# info from state / interface ethernet-1/1 description
    description "g15-pe2|1/1/c4/1 [STALE]"
```

/// admonition | Stop and take time to think here
    type: question

 - What information needs to be passed to the script by the event-handler instance, so that it is possible to achieve this task?
 - When an LLDP neighbor expires, what happens to the respective YANG path? Does this event trigger the event-handler instance? What state information is passed to the script?
 - What mechanism could be used to preserve information across event-handler instance executions?
///

/// tip
Look for features in [Event handler scripts documentation](https://documentation.nokia.com/srlinux/25-3/books/event-handler/event-handler-scripts.html#scripts){:target="_blank"} that can help you accomplish this task.
///

/// details | Hint
    type: tip
The ```persistent-data``` object can be used to persist data across script executions.<br>
```py title="example"
def event_handler_main(in_json_str):
    in_json = json.loads(in_json_str)
    persist = in_json.get('persistent-data', dict()) #fetch persistent-data passed by the event-handler instance into a dictionary
    #...do stuff...
    persist['newkey']='new data' #update persistent-data object information
    response = {'actions':actions, 'persistent-data':persist} #include the persistent-data in the response to the event-handler instance
    json_response = json.dumps(response)
    return json_response
#(...)
```
///

Test the event-handler before advancing to the next task
/// tip | Testing tips
- Disabling an interface causes immediate expiration of the learned LLDP neighbor information for that interface
- Disabling LLDP globally (`system lldp admin-state disable`) triggers the immediate expiration of all LLDP neighbors
///

#### Log changes
Add a feature so that a syslog message is generated whenever an interface description is updated as following a detected change.

``` bash title="expected syslog after an LLDP neighbor system-name changes from g15-leaf12 to g15-leaf12222"
auto-updating ethernet-1/2 description: "g15-leaf12|ethernet-1/50" -> "g15-leaf12222|ethernet-1/50"
```
``` bash title="expected syslog after an LLDP neighbor expires"
auto-updating ethernet-1/2 description: "g15-leaf12|ethernet-1/50" -> "g15-leaf12|ethernet-1/50 [STALE]"
```

/// tip | generating syslogs
The Linux program `logger` can be used to generate syslog messages.<br>
```bash title="example execution of logger program in Linux shell"
admin@g15-spine12:~$ logger -t sr_event_mgr -p local6.info 'this is my ($@log^) message'
```
Notice we spoof the tag (`-t`) to have same identifier as `sr_event_mgr` SR Linux app for convenience. This way, it will end up in the log `/var/log/srlinux/debug/sr_event_mgr.log`, which you can monitor:
```bash title="inspecting last 20 log messages from bash shell"
admin@g15-spine12:~$ tail -n 20 /var/log/srlinux/debug/sr_event_mgr.log
#...
2025-04-07T17:14:49.149172+00:00 g15-spine12 local6|INFO sr_event_mgr: this is my ($@log^) message
```
///

/// details | Hint
    type: tip

Use the `run-script` action to generate a log message
///

Test the event-handler. You may use one of the methods from the previous tasks or modify the `system-name` of one of the LLDP neighbors. Confirm that the interface description is updated and that a log entry is generated in `/var/log/srlinux/debug/sr_event_mgr.log`

This concludes the first use-case.

/// details | use-case 1 possible solution
    type: success

/// details | configuration
``` bash
--{ +!* candidate shared default }--[ system event-handler instance auto-ifdesc ]--
A:g15-spine12# info
    admin-state enable
    upython-script auto-ifdesc.py
    paths [
        "system lldp interface * neighbor * port-id"
        "system lldp interface * neighbor * system-name"
    ]
    options {
        object interfaces {
            values [
                ethernet-1/{1..200}
            ]
        }
    }
```
///

/// details | script
Modified version of Nokia-provided script ```lldp-interface-descriptions.py```
``` python
#!/usr/bin/env python3
#
# Example implementation of an event handler script to set interface descriptions according to information learnt over LLDP.
#
# Paths:
#   system lldp interface neighbor system-name - e.g. system lldp interface * neighbor * system-name
#   system lldp interface neighbor port-id - e.g. system lldp interface * neighbor * port-id
# Options:
#   interfaces: <array> - list of interfaces to enable auto-configuration of descriptions, e.g. [ ethernet-1/{10,11}, ethernet-2/5 ]
#   debug: <value>[default false] - optional debug prints - will be visible in 'last-stdout-stderr' leaf
#
# Example config:
#   system {
#        event-handler {
#            instance lldp {
#                admin-state enable
#                upython-script auto-ifdesc.py
#                paths [
#                    "system lldp interface * neighbor * port-id"
#                    "system lldp interface * neighbor * system-name"
#                ]
#                options {
#                    object interfaces {
#                        values [
#                            ethernet-1/12
#                            ethernet-1/{2..10}
#                            ethernet-1/{21..24}
#                            ethernet-1/{25,27..30}
#                        ]
#                    }
#                }
#            }
#        }
#    }

import sys
import json

_MAX_PATH_RANGE_EXPANSION = 4096

class PathRangeExpansionError(Exception):
    pass

def _expand_ranges(path):
    result = {}
    start = path.find('{') + 1
    end = path.find('}')
    if start < 1 or end < 0 or start == end:
        result[path] = None
        return result

    range_block = path[start:end]
    numbers = set()
    splits = range_block.split(',')
    # For each range
    for split in splits:
        pos = split.find('..')
        try:
            if pos >= 0:
                low = int(split[:pos])
                high = int(split[pos+2:])
                if high - low + 1 > _MAX_PATH_RANGE_EXPANSION:
                    raise PathRangeExpansionError(
                        f'Cannot expand path to more than {_MAX_PATH_RANGE_EXPANSION} paths')

                for i in range(low, high+1):
                    numbers.add(i)
            else:
                numbers.add(int(split))
        except (TypeError, ValueError) as e:
            raise PathRangeExpansionError(f"Invalid range expansion in '{path}': {type(e)}: {e}")

    if len(result) + len(numbers) > _MAX_PATH_RANGE_EXPANSION:
        raise PathRangeExpansionError(f'Cannot expand path to more than {_MAX_PATH_RANGE_EXPANSION} paths')

    sorted_list = sorted(numbers)
    if not sorted_list:
        raise PathRangeExpansionError(
            f"Invalid range expansion in '{path}': Must expand to at least one number")
    if sorted_list[0] < 0:
        raise PathRangeExpansionError(
            f"Invalid range expansion in '{path}': Negative numbers are not supported")

    for number in sorted_list:
        new_value = path[:start-1] + str(number) + path[end+1:]
        result[new_value] = None

    # found and expanded range
    return result

def process_options(options):
    parsed_interfaces = {}
    for interface_range in enabled_interfaces(options):
        interface_list = _expand_ranges(interface_range)
        parsed_interfaces.update(interface_list)
    return parsed_interfaces

def create_actions(parsed_interfaces, interfaces, cache):
    """cache save interfaces state from previous run
        {
        'ethernet-x/y':{
            'description':'node1|1/1/1'
            'stale':False
            }
        }
    """
    actions = []
    cached_interfaces_pending_check = list(cache.keys())

    #process active lldp neighbors
    for interface, lldp_info in interfaces.items():
        if interface in parsed_interfaces:
            description = f'{lldp_info.get("system-name", "unknown")}|{lldp_info.get("port-id","unknown")}'
            actions.append({
                'set-cfg-path':{'path':f'interface {interface} description',
                'value':description,
                'always-execute':False}
            })
            if interface in cache:
                old_description = cache[interface]['description']
                cached_interfaces_pending_check.remove(interface)
                if description != old_description:
                    logmessage = f"'activity-12: auto-updating {interface} description: {old_description} -> {description}'"
                    actions.append({
                        'run-script': {"cmdline": f"logger -t sr_event_mgr -p local6.info {logmessage}"}
                    })
                cache[interface]['stale'] = False
                cache[interface]['description'] = description
            else:
                cache[interface] = {
                    'stale': False,
                    'description': description
                }

    #process expired lldp neighbors
    while cached_interfaces_pending_check:
        interface = cached_interfaces_pending_check.pop()
        if cache[interface]['stale'] == False:
            old_description = cache[interface]['description']
            description = old_description + " [STALE]"
            logmessage = f"'activity-12: auto-updating {interface} description: {old_description} -> {description}'"
            actions.append({
                'set-cfg-path':{'path':f'interface {interface} description',
                'value':description,
                'always-execute':False}
            })
            actions.append({
                'run-script': {"cmdline": f"logger -t sr_event_mgr -p local6.info {logmessage}"}
            })
            cache[interface]['description'] = description
            cache[interface]['stale'] = True

    return actions

def enabled_interfaces(options):
    return options.get('interfaces', [])

def process_paths(paths):
    interfaces = {}
    for update in paths:
        path = update.get('path','')
        value = update.get('value','')
        interface_name = path.split(' ')[3]
        if interface_name not in interfaces:
            interfaces[interface_name] = {}
        if path.endswith('system-name'):
            interfaces[interface_name]['system-name'] = value
        elif path.endswith('port-id'):
            interfaces[interface_name]['port-id'] = value
    return interfaces

def event_handler_main(in_json_str):
    in_json = json.loads(in_json_str)
    paths = in_json['paths']
    options = in_json['options']
    cache = in_json.get('persistent-data', dict())
    parsed_interfaces = process_options(options)
    lldp_interfaces = process_paths(paths)
    if options.get('debug', '') == 'true':
        print(
            f'enabled interfaces = {enabled_interfaces(options)}\n\
parsed interfaces = {parsed_interfaces}\n'
        )
    actions = create_actions(parsed_interfaces, lldp_interfaces, cache)
    response = { 'actions':actions, 'persistent-data':cache }
    json_response = json.dumps(response)
    return json_response

#
# This code is only if you want to test it from bash - this isn't used when invoked from SRL
#
def main():
    example_in_json_str = """
{
    "paths": [
        {
            "path":"system lldp interface ethernet-1/2 neighbor 11:22:33:44:55:66 system-name",
            "value":"node1"
        },
        {
            "path":"system lldp interface ethernet-1/2 neighbor 11:22:33:44:55:66 port-id",
            "value":"1/1/1"
        }
    ],
    "persistent-data":{
        "ethernet-1/2":{
            "description":"node1|1/1/1",
            "stale":"true"
        }
    },
    "options": {"interfaces":["ethernet-1/{2..6}", "ethernet-1/{10,11,14..20}"],"debug":"true"}
}
"""
    json_response = event_handler_main(example_in_json_str)
    print(json_response)

if __name__ == "__main__":
    sys.exit(main())
```
///
///

### Auto-provision ISL spine-to-leaf interface
Create a new event-handler that automatically provisions a spine-to-leaf ISL(Inter-switch link) if the LLDP neighbor's `system-name` includes the string `leaf`. The script should first check if `subinterface 0` exists and, if not, configure the following:

- create `subinterface` with `index 0` (untagged, `ip-mtu`=9198, ipv6 enabled with `router-advertisements`)
- add the `subinterface` to `network-instance default`
- add the `subinterface` to bgp `dynamic-neighbors`(`peer-group`=bgpgroup-ebgp-srexperts-fabric ; `allowed-peer-as`=4200001000..4200001999) <p>
Example:
/// tab | LLDP neighbor
```bash hl_lines="8"
A:g15-spine12# info from state / system lldp interface ethernet-1/1 neighbor *
    system {
        lldp {
            interface ethernet-1/1 {
                neighbor 1A:41:0D:FF:00:00 {
                    first-message "2025-04-11T14:28:21.505Z (6 days ago)"
                    last-update "2025-04-17T15:10:37.614Z (3 seconds ago)"
                    system-name g15-leaf11
                    system-description "SRLinux-v24.10.3-201-g9d0e2b9371 g15-leaf11 6.1.0-32-cloud-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.129-1 (2025-03-06)"
                    chassis-id 1A:41:0D:FF:00:00
                    chassis-id-type MAC_ADDRESS
                    port-id ethernet-1/50
                    port-id-type INTERFACE_NAME
                    port-description leaf11-spine12
                    capability ROUTER {
                        enabled true
                    }
                }
            }
        }
    }
```
///
/// tab | expected auto-provisioned config
```
set / interface ethernet-1/1 subinterface 0 ip-mtu 9198
set / interface ethernet-1/1 subinterface 0 ipv6 admin-state enable
set / interface ethernet-1/1 subinterface 0 ipv6 router-advertisement router-role admin-state enable
set / network-instance default interface ethernet-1/1.0 interface-ref interface ethernet-1/1
set / network-instance default interface ethernet-1/1.0 interface-ref subinterface 0
set / network-instance default protocols bgp dynamic-neighbors interface ethernet-1/1.0 peer-group bgpgroup-ebgp-srexperts-fabric
set / network-instance default protocols bgp dynamic-neighbors interface ethernet-1/1.0 allowed-peer-as [ 4200001000..4200001999 ]
```
///

/// admonition | allowed-peer-as
    type: warning
The event-handler action `set-cfg-path` doesn't currently support setting values for `leaf-lists` such as the parameter `allowed-peer-as`. As an alternative you can use the `run-script` action to configure the `dynamic-neighbor interface` through an `sr_cli` shell command. An example usage of the command itself from Linux shell is shown here:
```bash
A:g15-spine12# bash
admin@g15-spine12:~$ sr_cli -ec -- 'network-instance default protocols bgp dynamic-neighbors interface ethernet-1/1.0 allowed-peer-as [ 4200001000..4200001999 ] peer-group bgpgroup-ebgp-srexperts-fabric'
```
///
/// details | Tip - Which paths should you subscribe to?
    type: tip
Include `interface * subinterface 0 oper-state` in the event-handler subscribed paths so that it is easy to check if subinterface 0 already exists from the script.
///
/// details | Tip - Don't hardcode values in Python
    type: tip
Use the event-handler options feature to define the `dynamic-neighbor interface` parameters `allowed-peer-as` and `peer-group`.
///

To test the event-handler you can use the following steps on `spine12` (using leaf interface `ethernet-1/1` as example):
/// tab | Step1 - disable interface
```bash title="disable"
enter candidate
set / interface ethernet-1/1 admin-state disable
commit stay
```
```bash title="verification"
info from state / interface ethernet-1/1 admin-state
info from state / system lldp interface ethernet-1/1 neighbor * system-name
info from state / network-instance default protocols bgp neighbor * session-state | as table
```
/// note | expectation
The LLDP neighbor and BGP session for `ethernet-1/1` disappears
///
///
/// tab | Step2 - delete subinterface
```bash title="delete"
enter candidate
delete / interface ethernet-1/1 subinterface 0
delete / network-instance default interface ethernet-1/1.0
delete / network-instance default protocols bgp dynamic-neighbors interface ethernet-1/1.0
commit stay
```
```bash title="verification"
info from running / interface ethernet-1/1 subinterface 0
info from running / network-instance default interface ethernet-1/1.0
info from running / network-instance default protocols bgp dynamic-neighbors interface ethernet-1/1.0
```
/// note | expectation
no output
///
///
/// tab | Step3 - enable interface
```bash title="enable"
enter candidate
set / interface ethernet-1/1 admin-state enable
commit stay
```
```bash title="verification"
info from running / interface ethernet-1/1 subinterface 0
info from running / network-instance default interface ethernet-1/1.0
info from running / network-instance default protocols bgp dynamic-neighbors interface ethernet-1/1.0
info from state / system lldp interface ethernet-1/1 neighbor * system-name
info from state / network-instance default protocols bgp neighbor * session-state | as table
```
/// note | expectation
- LLDP neighbor system-name is displayed
- An ISL is added to the configuration
- a BGP session establishes (this may take a few seconds)
///
///

/// details | use-case 2 possible solution
    type: success

/// details | configuration
``` bash
--{ +!* candidate shared default }--[ system event-handler instance auto-isl ]--
A:g15-spine12# info
    admin-state enable
    upython-script auto-isl.py
    paths [
        "system lldp interface * neighbor * system-name"
        "interface * subinterface 0 oper-state"
    ]
    options {
        object allowed-peer-as {
            values [
                4200001000..4200001999
            ]
        }
        object peer-group {
            value bgpgroup-ebgp-srexperts-fabric
        }
    }
```
///

/// details | script
``` python
#!/usr/bin/env python3
#
# Example implementation of an event handler to auto-provision spine-leaf ISLs. Assumes:
# IPv6 link-local addresses
# Untagged subinterface 0
# BGP IPv6 dynamic-neighbors
#
# Example config:
#   system {
#        event-handler {
#            instance auto-isl {
#                admin-state enable
#                upython-script auto-isl.py
#                paths [
#                    "interface * subinterface 0 oper-state"
#                    "system lldp interface * neighbor * system-name"
#                ]
#                options {
#                    object allowed-peer-as {
#                        values [
#                            4200001000..4200001999
#                        ]
#                    }
#                    object peer-group {
#                        value bgpgroup-ebgp-srexperts-fabric
#                   }
#                }
#            }
#        }
#    }

import sys
import json

def create_actions(interfaces, peergroup, as_list):
    actions = []

    for interface in interfaces:
        actions.append({
            'set-cfg-path':{'path':f'interface {interface} subinterface 0 ip-mtu',
            'value':9198,
            'always-execute':True}
        })
        actions.append({
            'set-cfg-path':{'path':f'interface {interface} subinterface 0 admin-state',
            'value':'enable',
            'always-execute':True}
        })
        actions.append({
            'set-cfg-path':{'path':f'interface {interface} subinterface 0 ipv6 admin-state',
            'value':'enable',
            'always-execute':True}
        })
        actions.append({
            'set-cfg-path':{'path':f'interface {interface} subinterface 0 ipv6 router-advertisement router-role admin-state',
            'value':'enable',
            'always-execute':True}
        })
        actions.append({
            'set-cfg-path':{'path':f'network-instance default interface {interface}.0 interface-ref interface',
            'value':interface,
            'always-execute':True}
        })
        actions.append({
            'set-cfg-path':{'path':f'network-instance default interface {interface}.0 interface-ref subinterface',
            'value':0,
            'always-execute':True}
        })
        actions.append({
            'run-script': {
                "cmdline": f"sr_cli -ec -- 'network-instance default protocols bgp dynamic-neighbors interface {interface}.0 allowed-peer-as [ {' '.join(as_list)} ] peer-group {peergroup}'"}
        })
        actions.append({
            'run-script': {
                "cmdline": f"logger -t sr_event_mgr -p local6.info auto-provisioned leaf ISL interface {interface}"}
        })
    return actions

def process_paths(paths):
    already_provisioned_interfaces = set()
    leaf_interfaces = set()
    for update in paths:
        path = update.get('path','')
        value = update.get('value','')

        #collect LLDP neighbor system-name
        if path.startswith('system'):
            splitted_path = path.split(' ')
            interface_name = splitted_path[3]
            if 'leaf' in value:
                leaf_interfaces.add(interface_name)

        #collect subinterfaces with index 0 already existing in config
        elif path.startswith('interface'):
            splitted_path = path.split(' ')
            interface_name = splitted_path[1]
            already_provisioned_interfaces.add(interface_name)

    #return leaf interfaces that are not yet configured.
    return (leaf_interfaces - already_provisioned_interfaces)

def event_handler_main(in_json_str):
    in_json = json.loads(in_json_str)
    paths = in_json['paths']
    options = in_json['options']

    allowed_peer_as_list = options['allowed-peer-as']
    peer_group = options['peer-group']
    interfaces_to_provision = process_paths(paths)
    actions = create_actions(interfaces_to_provision,peergroup=peer_group,as_list=allowed_peer_as_list)
    response = { 'actions':actions }
    json_response = json.dumps(response)
    return json_response

#
# This code is only if you want to test it from bash - this isn't used when invoked from SRL
#
def main():
    example_in_json_str = """
{
    "paths": [
        {
            "path":"system lldp interface ethernet-1/2 neighbor 11:22:33:44:55:66 system-name",
            "value":"leaf1"
        },
        {
            "path":"system lldp interface ethernet-1/3 neighbor 11:22:33:44:55:67 system-name",
            "value":"leaf2"
        },
        {
            "path":"interface ethernet-1/3 oper-state",
            "value":"down"
        }
    ],
    "options": {"allowed-peer-as":["1","2"], "peer-group":"leaf"}
}
"""
    json_response = event_handler_main(example_in_json_str)
    print(json_response)

if __name__ == "__main__":
    sys.exit(main())
```
///

///

## Summary and review

Congratulations!  If you have got this far you have completed this activity and achieved the following:

- You have written or modified one or more applications using the Python 3 programming language
- You have used the model-driven CLI for managing configuration and observe system state in SR Linux
- You have made the behavior of SR Linux dynamic using event handling
- You have worked with YANG modeled data

If you're hungry for more have a go at another activity, or try a similar activity on SR OS: ([Automatic update of interface descriptions using the event handler](../../sros/intermediate/nos-sros-activity-08.md){:target="_blank"}).
