# gNMI with Nokia SR Linux: Getting started with configuration management and streaming telemetry using gNMI protocol

| Item              | Details                                                                   |
| ----------------- | ------------------------------------------------------------------------- |
| Short Description | Use gNMI for configuration management and streaming telemetry on SR Linux |
| Skill Level       | Beginner                                                                  |
| Tools Used        | SR Linux, gNMIc                                                           |

## Introduction

Get started with gNMI on Nokia SR Linux in just five simple steps! This exercise will teach you how to leverage gNMI to perform configuration management and streaming telemetry tasks on Nokia SR Linux Network OS. After learning the concepts, you may treat yourself to some short chanllenges we prepared for you in the [Tasks section](#tasks).

**gNMI** (gRPC Network Management Interface) is a gRPC-based network management protocol [defined by the Openconfig group](https://github.com/openconfig/reference/blob/master/rpc/gnmi/gnmi-specification.md) that is used for configuration management and streaming telemetry. gRPC uses Google protocol buffers (protobuf) to describe the Remote Procedure Calls (RPC) and encoded data on the wire.

gNMI supports the following RPCs:

* Capabilities - Discover the capabilities (YANG modules and supported encodings) of the network device
* Get - Retrieve configuration and state data in a one-off fashion.
* Set - Perform configuration management.
* Subscribe - stream configuration and state data.

**gNMIc** is an [open-source tool](https://gnmic.openconfig.net/) which is part of the openconfig group contributed by Nokia. gNMIc provides full support for Capabilities, Get, Set and Subscribe RPCs with collector capabilities.

**Nokia SR Linux** supports the full set of gNMI RPCs and allows operators to leverage both configuration and streaming telemetry capabilities enabled by gNMI interface.

> Using the provided lab topology, the exercise below assume you are working with the `leaf11` node.

## Step 1: Configuring Nokia SR Linux

gNMI has already been enabled on `leaf11` and other SR Linux nodes of the lab, since we use it for other exercises and activies, but you can verify how the configuration is done to understand what it takes to configure SR Linux to support gNMI.

gNMI is one of the gRPC services that a user configures on SR Linux. The output below shows the configuration of the `mgmt` gRPC service on SR Linux device `leaf11` where you can see that `gnmi` is a member of the `services` list.

```
--{ running }--[  ]--
A:leaf11# info system grpc-server mgmt
    system {
        grpc-server mgmt {
            admin-state enable
            rate-limit 65000
            tls-profile clab-profile
            network-instance mgmt
            trace-options [
                request
                response
                common
            ]
            services [
                gnmi
                gnoi
                gribi
                p4rt
            ]
            unix-socket {
                admin-state enable
            }
        }
    }
```

You can verify the state of the `mgmt` gRPC server by querying the state datastore of SR Linux:

```
A:leaf11# info from state system grpc-server mgmt
    system {
        grpc-server mgmt {
            admin-state enable
            timeout 7200
            rate-limit 65000
            session-limit 20
            metadata-authentication true
            tls-profile clab-profile
            default-tls-profile false
            network-instance mgmt
            port 57400
            oper-state up
            trace-options [
```

The `oper-state up` leaf verifies that our gRPC server running fine and we should be able to use gNMI service.

> SR Linux defaults to port 57400 for the gRPC server.

## Step 2: Installing gNMIc

There are several gNMI clients that one can use to interface with gNMI-enabled devices, we will use gNMIc CLI tool in this exercise as it is the most feature rich tool for this task.

gNMIc is already installed on the server where we run the lab topology, so you don't have to install it. But even if you would have to, it is as easy as running a single [install script](https://gnmic.openconfig.net/install/).

## Step 3: Capabilities

A client MAY discover the capabilities of the target using the Capabilities RPC. The `CapabilityRequest` message is sent by the client to interrogate the target. The target MUST reply with a `CapabilityResponse` message that includes its gNMI service version, the versioned data models it supports, and the supported data encodings.

Using `gnmic` CLI tool perform the following command to query the capabilities:

```bash
gnmic -a clab-srexperts-leaf11:57400 -u admin -p SReXperts2024 --skip-verify capabilities
```

> Note, the port 57400 that we specified to highlight the default port number used by SR Linux. The port can be omitted as well, since gNMIc uses port 57400 whenever the port is not set explicitly.

Since SR Linux's `mgmt` gRPC server uses TLS encryption we added the `--skip-verify` flag to make our life a little bit easier and not providing a CA certificate for TLS verification.

*Expected Output*

```
gNMI version: 0.10.0
supported models:
  - urn:nokia.com:srlinux:aaa:aaa:srl_nokia-aaa, Nokia, 2024-03-31
  - urn:nokia.com:srlinux:aaa:aaa-password:srl_nokia-aaa-password, Nokia, 2024-03-31
  - urn:nokia.com:srlinux:aaa:aaa-types:srl_nokia-aaa-types, Nokia, 2023-03-31
  - urn:nokia.com:srlinux:acl:acl:srl_nokia-acl, Nokia, 2024-03-31
  - urn:nokia.com:srlinux:acl:acl-policers:srl_nokia-acl-policers, Nokia, 2024-03-31
  - urn:nokia.com:srlinux:acl:acl-qos:srl_nokia-acl-qos, Nokia, 2024-03-31
  - urn:nokia.com:srlinux:fib:aft:srl_nokia-aft, Nokia, 2024-03-31
  - urn:nokia.com:srlinux:static-route:aggregate-routes:srl_nokia-aggregate-routes, Nokia, 2024-03-31
  - urn:nokia.com:srlinux:app:app-mgmt:srl_nokia-app-mgmt, Nokia, 2022-03-31
  - urn:nokia.com:srlinux:bfd:bfd:srl_nokia-bfd, Nokia, 2024-03-31

    ~~~ output omitted ~~

  - urn:nokia.com:srlinux:vxlan:tools-vxlan-tunnel:srl_nokia-tools-vxlan-tunnel, Nokia, 2021-03-31
supported encodings:
  - JSON_IETF
  - PROTO
  - ASCII
  - 52
  - 42
  - 43
  - 45
  - 44
  - 46
  - 47
  - 48
  - 49
  - 50
  - 53
```

The output lists the gNMI version (0.10.0), the list of YANG models supported by this release of SR Linux and a list of encodings that the device supports.

## Step 4: Get

gNMI can be used to retrieve configuration and state information from the SR Linux nodes. zInformation is retrieved using the GET RPC that consists of the `GetRequest` and `GetResponse` messages.

To indicate what part of the device's datastore we want to get we use the `path` field in the `GetRequest` message. The path is a string that represents the gNMI path that points to a particular point in the YANG data model of the device.

> SR Linux offers its users a powerful YANG browser - <https://yang.srlinux.dev> - to assist with finding the correct path to the data you are interested in.

`GetRequest` message contains the [`DataType`](https://gnxi.srlinux.dev/gnmi/gnmi#GetRequest.DataType) field that can be used to select what data type the client is interested in. The `DataType` can be either:

* ALL (both state and config)
* CONFIG
* STATE
* OPERATIONAL

### a. Getting configuration data

Let's try and get the configuration data for an interface `ethernet-1/1` from the SR Linux node `leaf11`.

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify get --path "/interface[name=ethernet-1/1]" -e json_ietf --type CONFIG
```

Note, how we set the required data encoding (`json-ietf`) and provided the `CONFIG` data type to the command.

*Expected Output:*

```json
[
  {
    "source": "clab-srexperts-leaf11",
    "timestamp": 1715880503384439447,
    "time": "2024-05-16T20:28:23.384439447+03:00",
    "updates": [
      {
        "Path": "srl_nokia-interfaces:interface[name=ethernet-1/1]",
        "values": {
          "srl_nokia-interfaces:interface": {
            "admin-state": "enable",
            "description": "leaf11-client11",
            "srl_nokia-interfaces-vlans:vlan-tagging": true,
            "subinterface": [
              {
                "index": 1,
                "srl_nokia-interfaces-vlans:vlan": {
                  "encap": {
                    "single-tagged": {
                      "vlan-id": 1
                    }
                  }
                },
                "type": "srl_nokia-interfaces:bridged"
              },
              {
                "index": 101,
                "srl_nokia-interfaces-vlans:vlan": {
                  "encap": {
                    "single-tagged": {
                      "vlan-id": 101
                    }
                  }
                },
                "type": "srl_nokia-interfaces:bridged"
              }
            ]
          }
        }
      }
    ]
  }
]

```

### b. Getting state data

We can see how the output changes when we request the state data for the same interface:

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify get --path "/interface[name=ethernet-1/1]" -e json_ietf --type STATE
```

*Expected output:*

```json
[
  {
    "source": "clab-srexperts-leaf11",
    "timestamp": 1715880565056961222,
    "time": "2024-05-16T20:29:25.056961222+03:00",
    "updates": [
      {
        "Path": "srl_nokia-interfaces:interface[name=ethernet-1/1]",
        "values": {
          "srl_nokia-interfaces:interface": {
            "admin-state": "enable",
            "description": "leaf11-client11",
            "ethernet": {
              "dac-link-training": false,
              "flow-control": {
                "receive": false
              },
              "hold-time": {
                "down": 0,
                "up": 0
              },
              "hw-mac-address": "1A:10:0D:FF:00:01",
              "lacp-port-priority": 32768,
              "port-speed": "25G",
              "srl_nokia-interfaces-l2cp:l2cp-transparency": {
                "dot1x": {
                  "oper-rule": "drop-tagged-and-untagged",
                  "tunnel": false
                },
                "lacp": {
                  "oper-rule": "trap-to-cpu-untagged",
                  "tunnel": false
                },
-- snipped --
```

Now, we get way more output from the device. The reason for this, is that we are getting all state values of the interface as well as all its configured subinterfaces. A peculiar detail is that the configuration values are also visible, this is because SR Linux state datastore contains both configuration and state data.

## Step 5: Set

The configuration management part of gNMI is carried out by the Set RPC. With Set RPC users can update, replace, or delete configuration data on the target device.

gNMIc supports Set RPC and provides multiple ways of passing the data to the CLI tool in order to perform updates, replaces or deletes. In the following exercises we will explore various options of providing data to the Set command.

### a. Update operation with in-line value

The most simple way to update a single value on the device is by providing the new value using the `update-value` flag. For example, if we were to set the description of the subinterface 101 of the interface `ethernet-1/1` to "setting from gnmic at srexperts2024" we would use the following command:

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify set --update-path "/interface[name=ethernet-1/1]/subinterface[index=101]/description" --update-value "setting from gnmic at srexperts2024"
```

As you can see, we leverage two flags `--update-path` to point to the leaf we want to update and `--update-value` to provide the value we want to be set for that leaf.

*Expected output:*

```json
{
  "source": "clab-srexperts-leaf11",
  "timestamp": 1715911843938194701,
  "time": "2024-05-17T05:10:43.938194701+03:00",
  "results": [
    {
      "operation": "UPDATE",
      "path": "interface[name=ethernet-1/1]/subinterface[index=101]/description"
    }
  ]
}
```

The returned data is nothing more than a confirmation, that the data has been set and no errors occurred.

### b. Set RPC with file-based input

The downside of the inlined values for Set operations is that they are not suitable when you have to privide a non-scalar value, like a json blob. For example, when you want to create a new subinterface, you would need to provide more data than just a string like we did for the description.

To assist with more complex inputs, gNMIc supports the file-based input. You can provide a file with the data you want to set and gNMIc will read the file and use the data to perform the Set operation.

To demonstrate this, lets create a new subinterface `99` under the `ethernet-1/1` interface where all the parameters are defined in a file:

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify -e JSON_IETF set --update-path "/interface[name=ethernet-1/1]/subinterface[index=99]" --update-file subif.json

```

The last argument in the command refers to a `subif.json` file. Clearly this is the file that contains the data about the subinterface we want to create. But how to figure out what content can we put in the file?

This is, again, sourced from the YANG model of the device that defines all configuration and state data. You can use the YANG browser to identify what elements are nested one under another, or leverage the SR Linux CLI to get the data in json format.

For example, using the Tree Browser of our YANG Browser you open up an interface/subinterface tree - <https://yang.srlinux.dev/v24.3.2/tree?path=%2Finterface%5Bname%3D*%5D%2Fsubinterface%5Bindex%3D*%5D%2Findex> - and see what data comprises a subinterface and its nested elements.

Alternatively, you may connect to the `leaf11` and inspect one of the existing interface configurations to understand what can go into the subinterface config. To do that, ssh into the node, and enter into the context of any existing interface, for example:

```
--{ running }--[  ]--
A:leaf11# interface ethernet-1/1 subinterface 1
```

Now we can output the configuration of this subinterface and transform it to the json format, since this is what we want to use with the gNMIc later on:

```
--{ running }--[ interface ethernet-1/1 subinterface 1 ]--
A:leaf11# info | as json
{
  "index": 1,
  "type": "bridged",
  "vlan": {
    "encap": {
      "single-tagged": {
        "vlan-id": 1
      }
    }
  }
}
```

Using one of the above methods we can construct our `subif.json` files that we will use in the gnmic commmand:

```json
{
  "index": 99,
  "type": "bridged",
  "description": "setting from gnmic at srexperts2024",
  "vlan": {
    "encap": {
      "single-tagged": {
        "vlan-id": 99
      }
    }
  }
}
```

*Expected Output*

```json
{
  "source": "clab-srexperts-leaf11",
  "timestamp": 1715923235275894092,
  "time": "2024-05-17T08:20:35.275894092+03:00",
  "results": [
    {
      "operation": "UPDATE",
      "path": "interface[name=ethernet-1/1]/subinterface[index=99]"
    }
  ]
}
```

### c. Replace operation

Another useful operation under the Set RPC is the Replace operation. The Replace operation is used to replace the configuration data pointed by the path with the new value. Most commonly, Replace operation is used with containers and list, where an original container or list is replaced with the new one.

To demonstrate this, we can entirely replace the original subinterface 99 with the new configuration data, for example making it a routed subinterface without a vlan. To do that, we need to prepare another file with the new configuration data:

```json
{
  "index": 99,
  "type": "routed",
  "description": "replaced from gnmic at srexperts2024"
}
```

Note, how for the replace operation we changed the flag names to `replace-path` and `replace-file` accordingly.

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify set --replace-path "/interface[name=ethernet-1/1]/subinterface[index=99]" --replace-file routedsubif.json
```

*Expected Output*

```json
{
  "source": "clab-srexperts-leaf11",
  "timestamp": 1715927443923681216,
  "time": "2024-05-17T09:30:43.923681216+03:00",
  "results": [
    {
      "operation": "REPLACE",
      "path": "interface[name=ethernet-1/1]/subinterface[index=99]"
    }
  ]
}
```

### d. Delete operation

Finally, gNMI Set can delete configuration elements as well. Let's delete the subinterface `99` we created earlier.

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify set --delete "/interface[name=ethernet-1/1]/subinterface[index=99]"
```

*Expected Output*

```json
{
  "source": "clab-srexperts-leaf11",
  "timestamp": 1715926799833059405,
  "time": "2024-05-17T09:19:59.833059405+03:00",
  "results": [
    {
      "operation": "DELETE",
      "path": "interface[name=ethernet-1/1]/subinterface[index=99]"
    }
  ]
}
```

## Step 5: Streaming Telemetry with gNMI

gNMI is now de-facto the Streaming Telemetry interface when it comes to non-flow-related data, such as configuration and state. The performance of the protobuf encoding and the HTTP/2-based gRPC transport with streaming made it a perfect choice for streaming telemetry data.

Streaming Telemetry is carried out by the Subscribe RPC of the gNMI interface. The Subscribe RPC consists of the `SubscribeRequest` and `SubscribeResponse` messages. The `SubscribeRequest` message contains the `subscription` field that is used to define the subscription parameters.

Most notably, subscriptions can be made in a few different modes with distinct characteristics. We will cover two of them in this exercise:

### ONCE Mode

ONCE mode on the surface behaves exactly the same as Get operation, it returns the data for the element referenced by a path. The notable difference is in the background, where Subscribe ONCE uses streaming to deliver the data, this means that the data is streamed to the client as soon as the first bits become available, which contrasts with Get operation that waits for the whole data to be collected before sending it back to the client.

This makes ONCE mode useful to retrieve big chunks of data without waiting for the server to aggregate it first.

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify sub --path "/interface[name=ethernet-1/1]/subinterface[index=1]" --mode once
```

*Expected Output*

```json
{
  "source": "clab-srexperts-leaf11",
  "subscription-name": "default-1715924368",
  "timestamp": 1715924368499528038,
  "time": "2024-05-17T08:39:28.499528038+03:00",
  "updates": [
    {
      "Path": "interface[name=ethernet-1/1]/subinterface[index=1]/type",
      "values": {
        "interface/subinterface/type": "bridged"
      }
    },
    {
      "Path": "interface[name=ethernet-1/1]/subinterface[index=1]/admin-state",
      "values": {
        "interface/subinterface/admin-state": "enable"
      }
    },
    {
      "Path": "interface[name=ethernet-1/1]/subinterface[index=1]/l2-mtu",
      "values": {
        "interface/subinterface/l2-mtu": "9232"
      }
    },
    ..
    ...
    ....
    ~~~ output omitted ~~~
    
```

### Sample Mode

Sample mode is used to stream data at a fixed interval. In other words, sampled. The client specifies the interval at which the data should be streamed. The server then sends the data at the specified interval.

The main application for Sample mode is to stream data that changes frequently, for example, interface statistics counters or environmental parameters.

In the example below we would subscribe to the CPU utilization of the control plane module, asking it to provide the data every second.

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify sub --path "/platform/control[slot=*]/cpu[index=all]/total" --stream-mode sample --sample-interval 1s
```

*Expected output*

The output will keep streaming every sec as per the configured interval

```json
{
  "source": "clab-srexperts-leaf11",
  "subscription-name": "default-1715924240",
  "timestamp": 1715924241361100415,
  "time": "2024-05-17T08:37:21.361100415+03:00",
  "updates": [
    {
      "Path": "platform/control[slot=A]/cpu[index=all]/total/instant",
      "values": {
        "platform/control/cpu/total/instant": "31"
      }
    },
    {
      "Path": "platform/control[slot=A]/cpu[index=all]/total/average-1",
      "values": {
        "platform/control/cpu/total/average-1": "29"
      }
    },
    {
      "Path": "platform/control[slot=A]/cpu[index=all]/total/average-5",
      "values": {
        "platform/control/cpu/total/average-5": "29"
      }
    },
    {
      "Path": "platform/control[slot=A]/cpu[index=all]/total/average-15",
      "values": {
        "platform/control/cpu/total/average-15": "29"
      }
    }
  ]
}
```

### On change mode

The last subscription mode we cover today is the ONCHANGE mode that is used to stream data only when it changes. This is the most efficient way to stream telemetry data that changes infrequently, as it allows the client to receive the data almost instantly when the value changes, without sending lots of duplicated data as it happens with Sample mode.

Most commonly, on change subscriptions are made to the data that represents the operational state of some elements - interfaces, OSPF peers, number of BGP routes, etc.

Like in the example above, where we subscribe with on change mode to the operational state of all the interfaces on our leaf.

```bash
gnmic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify subscribe --stream-mode on_change --path /interface/oper-state
```

Expected output:

```json
{
  "source": "clab-srexperts-leaf11",
  "subscription-name": "default-1716088033",
  "timestamp": 1716088033376949261,
  "time": "2024-05-19T06:07:13.376949261+03:00",
  "updates": [
    {
      "Path": "interface[name=ethernet-1/2]/oper-state",
      "values": {
        "interface/oper-state": "up"
      }
    },
    {
      "Path": "interface[name=ethernet-1/3]/oper-state",
      "values": {
        "interface/oper-state": "down"
      }
    },
-- snipp --
```

## Tasks

Now that you are familiar with the gNMI concepts, treat yourself to some short challenges to test your knowledge.

### Configure the interface with a subinterface

Create a new interface, with a subinterface, and add it to the default network instance.

### Monitor BGP Neighbor status

Choose the appropriate subscription method to monitor the status of any BGP neighbor
