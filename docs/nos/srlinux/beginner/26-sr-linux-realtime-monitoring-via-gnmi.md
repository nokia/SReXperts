---
tags:
  - gNMIc
  - SRLinux
  - YANG
  - CLI
---

# Realtime monitoring via gNMI


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Realtime monitoring via gNMI                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Activity ID**           | 26                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **Short Description**       | Explore SR Linux and gNMI using get and subscribe operations.                                                                                                                                                                                                                                                                                                                                                   |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [gNMIc](https://gnmic.openconfig.net/)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: Leaf21, :material-router: Spine21                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [SR Linux documentation portal](https://documentation.nokia.com/srlinux/26-3/index.html)<br/>[Learn SR Linux](https://learn.srlinux.dev/)<br/> [YANG Browser](https://yangbrowser.nokia.com/srlinux/26.3.1?from=0&pathfmt=gnmi)<br/> |

You are a network engineer operating a modern SR Linux-based data center fabric. You have been assigned to remotely support the field team during a maintenance task to replace a degraded cable between a leaf and a spine. During this activity, you will use gNMI to observe changes in BGP neighbors while the physical work is being executed, continuously monitoring the connectivity between the leaf and spine as the cable replacement takes place.

To perform this task, you will use the `gnmic` tool.

/// details | gNMIc user guide
    type: tip

You can refer to the [gNMIc](https://gnmic.openconfig.net/) documentation to learn how to use the `gnmic` command.

See the command syntax below:

/// tab | Syntax
```
gnmic [command]
```
///

To help you get started without digging into the documentation too deeply, let's identify some flags to be used on the activity.

/// tab | Commands & Flags
```
Available Commands (filtered):
  capabilities query targets gnmi capabilities
  get          run gnmi get on targets
  help         Help about any command
  set          run gnmi set on targets
  subscribe    subscribe to gnmi updates on targets
  version      show gnmic version

Flags (filtered):
  -a, --address strings                     comma separated gnmi targets addresses
  -e, --encoding string                     one of ["json" "bytes" "proto" "ascii" "json_ietf"]. Case insensitive (default "json")
      --insecure                            insecure connection
  -p, --password string                     password
      --path                                YANG path
  -u, --username string                     username

```
///


/// note
We will be working with SR Linux release 26.3.1. In this version, the default JSON encoding is not available, so a valid encoding must be explicitly specified in every command we run.
///



///

/// note | gNMIc tool

It is recomended that this activity is performed on the hackathon instance since the tool is preinstalled.

Information on how to install gNMIc can be found on the [installation page](https://gnmic.openconfig.net/install/). 

Note: Windows users should use WSL on Windows and install the linux version of the tool.

///

## Main objectives of the activity

The main objectives of this hands-on activity are to learn how to use gNMIc while working in a maintenance window performing a simple network cable replacement.  You will:

1. Learn how to use the gNMIc command to connect to a router
2. Learn how to get information from a YANG modelled path in the router
3. Learn how to subscribe to a YANG modelled path so any updates are automatically observed



## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

**It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.**

!!! warning

    During this activity, please use the data center that is not connected to EDA, specifically **Leafs 21 to 23** and **Spines 21 to 22**.  This ensures a safe and isolated environment for the exercises.

-{{image(url='/images/26-sr-linux-realtime-monitoring-via-gnmi/srx.clab_srl_non_managed.svg')}}-


Your task is to replace the cable between :material-router: leaf21 and :material-router: spine21, check the connection marked in red bellow.
-{{image(url='/images/26-sr-linux-realtime-monitoring-via-gnmi/leaf21-spine21-cable.jpg', id="leaf21-spine21-cable")}}-

### Task 1: Validate the gRPC configuration

In this task you will confirm the configuration on the router has gRPC and gNMI enabled and you will familiarize yourself with the interface configuration.

We will be using :material-router: leaf21 for this.

To ensure you can connect using the `gnmic` tool from the hackathon instance to :material-router: leaf21, you should first verify that :material-router: leaf21 is properly configured for gNMI access.

Specifically, confirm the following:

1. The gRPC server is enabled on :material-router: leaf21
2. You know which port the gRPC server is using (commonly 57400, but it may differ depending on configuration)
3. The gNMI service is enabled under the gRPC server


/// tab | Login to :material-router: leaf21 

``` bash
ssh clab-srexperts-leaf21
```

///
/// tab | :material-router: leaf21 gRPC verification

``` bash
info from running system grpc-server insecure-mgmt
```

///

/// tab | Expected output

``` bash
A:admin@g2-leaf21# info from running system grpc-server insecure-mgmt
    admin-state enable
    rate-limit 65000
    network-instance mgmt
    port 57400
    trace-options [
        request
        response
        common
    ]
    services [
        gnmi
        gnoi
        gnsi
        gribi
        p4rt
    ]
    unix-socket {
        admin-state enable
    }

```

///

From the output, you should be able to confirm that all prerequisites on the router are correctly configured.

You may have noticed, that TLS configuration has not been specified.  This means that you can use gRPC and gNMI over an insecure connection.  This is ideal for this hackathon, however, in an operational environment you should always secure your gRPC connection.


Once you have validated these prerequisites, you will be able to establish a successful gNMI session from the hackathon instance to :material-router: leaf21 using `gnmic`.

### Task 2: Test the gNMI connection


You may use :material-router: leaf21 or :material-router: spine21 (or both) for the gNMI connection. 

To test the connection, perform a gNMI get to retrieve the device hostname from the path 

This will allow you to verify connectivity and confirm that you can successfully retrieve operational data from each device.

/// tab | :material-router: leaf21 `gnmic`

``` bash
gnmic -a clab-srexperts-leaf21:57400 -u admin -p $EVENT_PASSWORD --encoding ASCII --insecure get --path "/system/name/host-name"
```

///
/// tab | :material-router: leaf21 expected output

``` bash
[
  {
    "source": "clab-srexperts-leaf21:57400",
    "timestamp": 1775476432978124505,
    "time": "2026-04-06T11:53:52.978124505Z",
    "updates": [
      {
        "Path": "system/name/host-name",
        "values": {
          "system/name/host-name": "g1-leaf21"
        }
      }
    ]
  }
]
```
///
/// tab | :material-router: spine21 `gnmic`

``` bash
gnmic -a clab-srexperts-spine21:57400 -u admin -p $EVENT_PASSWORD --encoding ASCII --insecure get --path "/system/name/host-name"
```

///
/// tab | :material-router: spine21 expected output

``` bash
[
  {
    "source": "clab-srexperts-spine21:57400",
    "timestamp": 1775476432978124505,
    "time": "2026-04-06T11:53:52.978124505Z",
    "updates": [
      {
        "Path": "system/name/host-name",
        "values": {
          "system/name/host-name": "g1-spine21"
        }
      }
    ]
  }
]
```
///

Once you confirm you can make the gNMI connection you can continue to the next task.

### Task 3: Subscribe to live telemetry streaming

You are now going to complete the planned works activity, but you need to see what is going on with the network as you progress. To do this you are going to enable streaming telemetry using the gNMI service running over the gRPC protocol.

You will monitor the BGP neighbor session status to monitor when BGP connectivity is working again between the leaf and spine devices.  If you need assistance to identify the YANG modelled paths for BGP neighbors, or you would just like to browse the YANG modelled paths that can be streamed take a look in the expandable box below.

/// details | gNMI path YANG browser
    type: tip

To know the gNMI path for the **protocol bgp neighbor session status** it is better to explore the YANG Browser of the equipment we are working on. You can find the detailed information on the [YANG Browser](https://yangbrowser.nokia.com/srlinux/26.3.1).

Since we are looking for gNMI paths and the idea is to get state information, you should ensure the options marked on the image bellow are selected.

-{{image(url='/images/26-sr-linux-realtime-monitoring-via-gnmi/yangbrowser_gnmi_state.jpg')}}-

Use the search bar to find the path to the BGP neighbor's session state.  Record this path somewhere for use in a moment.

-{{image(url='/images/26-sr-linux-realtime-monitoring-via-gnmi/yangbrowser_bgp_neighbor.jpg')}}-


An alternative option to retrieve the gNMI path (xpath) is to use the SR Linux CLI `pwc xpath` command. For example:

/// tab | SR Linux CLI `pwc xpath`
``` bash hl_lines="2 5 8 9"
--{ running }--[  ]--
A:root@g51-leaf21# enter state

--{ state }--[  ]--
A:root@g51-leaf21# network-instance default protocols bgp neighbor fe80::1817:3ff:feff:1%ethernet-1/31.0

--{ state }--[ network-instance default protocols bgp neighbor fe80::1817:3ff:feff:1%ethernet-1/31.0 ]--
A:root@g51-leaf21# pwc xpath
/network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::1817:3ff:feff:1%ethernet-1/31.0]
```
///

///

This time, since we want to monitor in real time, we will use the `subscribe` instead of the `get` operation that was used earlier to test the gNMI connection and we will target :material-router: spine21

/// tab | gNMIc subscribe

``` bash
gnmic -a clab-srexperts-spine21:57400 -u admin -p $EVENT_PASSWORD --encoding ascii --insecure subscribe --path "/network-instance[name=*]/protocols/bgp/neighbor[peer-address=*]/session-state"
```

///
/// tab | expected output

``` bash

nokia@hack1:~$ gnmic -a clab-srexperts-spine21:57400 -u admin -p $EVENT_PASSWORD --encoding ascii --insecure subscribe --path "/network-instance[name=*]/protocols/bgp/neighbor[peer-address=*]/session-state"
{
  "source": "clab-srexperts-spine21:57400",
  "subscription-name": "default-1775831179",
  "timestamp": 1775831179922986261,
  "time": "2026-04-10T14:26:19.922986261Z",
  "updates": [
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::1817:14ff:feff:1f%ethernet-1/2.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "established"
      }
    }
  ]
}
{
  "source": "clab-srexperts-spine21:57400",
  "subscription-name": "default-1775831179",
  "timestamp": 1775831179924148310,
  "time": "2026-04-10T14:26:19.92414831Z",
  "updates": [
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::182d:13ff:feff:1f%ethernet-1/1.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "established"
      }
    }
  ]
}
{
  "source": "clab-srexperts-spine21:57400",
  "subscription-name": "default-1775831179",
  "timestamp": 1775831179924270245,
  "time": "2026-04-10T14:26:19.924270245Z",
  "updates": [
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::188d:15ff:feff:1f%ethernet-1/3.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "established"
      }
    },
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::1e0b:19ff:fe00:0%ethernet-1/31.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "established"
      }
    },
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::1e7b:1cff:fe00:0%ethernet-1/32.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "established"
      }
    }
  ]
}
{
  "sync-response": true
}


```
///

You can see, in real-time, the output of the status of all BGP peering configured on :material-router: spine21.

You can check that the gNMI subscription is active by logging into :material-router: spine21 in another window and executing the following command:



/// tab | SSH to :material-router: spine21 

``` bash
ssh admin@clab-srexperts-spine21
```
///

/// tab | Check :material-router: spine21 subscription

``` bash
info from state system grpc-server insecure-mgmt
```
///
/// tab | Output: :material-router: spine21 subscription

``` bash
--{ running }--[  ]--
A:admin@g2-spine21# info from state system grpc-server insecure-mgmt
(truncated)
    client 941 {
        type gnmi
        user admin
        user-agent "gNMIc/0.45.0 grpc-go/1.78.0"
        remote-host 10.128.2.1
        remote-port 57670
        start-time "2026-04-15T14:12:43.785Z (a minute ago)"
        gnmi {
            paths 1 {
                path "/network-instance[name=*]/protocols/bgp/neighbor[peer-address=*]/session-state/..."
                mode TARGET_DEFINED
            }
        }
    }

```

///

Leave the telemetry stream running in your first window and use `gnmic` to disable the link between :material-router: leaf21 and :material-router: spine21.  
Refer to the [diagram earlier in this activity](#leaf21-spine21-cable) to check the ports on both nodes.  


/// details | Solution: Disable the link between :material-router: leaf21 and :material-router: spine21.
    type: solution

Disable both sides of the link:  

- :material-router: leaf21 port `ethernet-1/31`  
- :material-router: spine21 port `ethernet-1/1`  

Use these `gnmic` commands to disable the ports.
``` bash
### leaf21 - set status disable
gnmic -a clab-srexperts-leaf21:57400 -u admin -p $EVENT_PASSWORD --insecure -e json_ietf set \
--update-path '/interface[name=ethernet-1/31]/admin-state' --update-value disable
### spine21 - set status disable
gnmic -a clab-srexperts-spine21:57400 -u admin -p $EVENT_PASSWORD --insecure -e json_ietf set \
--update-path '/interface[name=ethernet-1/1]/admin-state' --update-value disable

```
///


Observe the changes in the streaming telemetry output in your other window.  

/// details | Output: Example streaming telemetry output
    type: info
/// tab | Example streaming telemetry output
``` bash
{
  "source": "clab-srexperts-spine21:57400",
  "subscription-name": "default-1775831179",
  "timestamp": 1775831313432146723,
  "time": "2026-04-10T14:28:33.432146723Z",
  "updates": [
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::182d:13ff:feff:1f%ethernet-1/1.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "idle"
      }
    }
  ]
}
{
  "source": "clab-srexperts-spine21:57400",
  "subscription-name": "default-1775831179",
  "timestamp": 1775831313432607189,
  "time": "2026-04-10T14:28:33.432607189Z",
  "deletes": [
    "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::182d:13ff:feff:1f%ethernet-1/1.0]/session-state"
  ]
}
```
///
///

You can see that the BGP neighbor has transitioned to **idle** and was then **removed**.

Now, use `gnmic` to re-enable the port on the leaf and observe the changes in the real-time telemetry stream.


/// details | Solution: Enable the link between :material-router: leaf21 and :material-router: spine21.
    type: solution

Use these `gnmic` commands to disable the ports.

``` bash
### leaf21 - set status disable
gnmic -a clab-srexperts-leaf21:57400 -u admin -p $EVENT_PASSWORD --insecure -e json_ietf set \
--update-path '/interface[name=ethernet-1/31]/admin-state' --update-value enable
### spine21 - set status disable
gnmic -a clab-srexperts-spine21:57400 -u admin -p $EVENT_PASSWORD --insecure -e json_ietf set \
--update-path '/interface[name=ethernet-1/1]/admin-state' --update-value enable

```
///


/// details | Output: Example streaming telemetry output
    type: info
/// tab | Realtime monitor window

``` bash
{
  "source": "clab-srexperts-spine21:57400",
  "subscription-name": "default-1776088932",
  "timestamp": 1776089048392299045,
  "time": "2026-04-13T14:04:08.392299045Z",
  "updates": [
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::182d:13ff:feff:1f%ethernet-1/1.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "opensent"
      }
    }
  ]
}
{
  "source": "clab-srexperts-spine21:57400",
  "subscription-name": "default-1776088932",
  "timestamp": 1776089048394957326,
  "time": "2026-04-13T14:04:08.394957326Z",
  "updates": [
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::182d:13ff:feff:1f%ethernet-1/1.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "openconfirm"
      }
    }
  ]
}
{
  "source": "clab-srexperts-spine21:57400",
  "subscription-name": "default-1776088932",
  "timestamp": 1776089048406717558,
  "time": "2026-04-13T14:04:08.406717558Z",
  "updates": [
    {
      "Path": "network-instance[name=default]/protocols/bgp/neighbor[peer-address=fe80::182d:13ff:feff:1f%ethernet-1/1.0]/session-state",
      "values": {
        "network-instance/protocols/bgp/neighbor/session-state": "established"
      }
    }
  ]
}
```
///
///

This output shows a successful BGP session re-establishment sequence on :material-router: spine21 after the interface change.
You can observe the real-time state transitions delivered via the gNMI Subscribe stream:

- **opensent**: BGP session is actively trying to establish and has sent an OPEN message

- **openconfirm**: OPEN exchange completed, waiting for final confirmation

- **established**: BGP session is fully up and operational


This confirms that:

- The physical link is back up
- The BGP adjacency has successfully recovered
- The gNMI subscription is correctly streaming state changes in real time


## Conclusion

Congratulations!  You have successfully completed your planned works activity simulating a cable swap on the network.  By completing this activity, you have successfully:

- Learned how to use the gNMIc tool.
- Learned how to navigate the Nokia YANG browser to search for valid gNMI paths.
- Used the gRPC protocol and the gNMI service to get data from an SR Linux router using the open source `gnmic` utility.
- Used the gRPC protocol and the gNMI service to to subscribe to a real-time telemetry monitoring stream from an SR Linux router to observe BGP peering state changes.
