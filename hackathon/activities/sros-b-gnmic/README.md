# gNMIc with Nokia SR OS: Getting started with configuration management and monitoring using gNMI protocol

## Introduction

Master gNMIc on Nokia SR OS in just five simple steps! This activity will guide you from setup, configuration management and stream telemetry data empowering you to efficiently manage your network devices.

**gNMI:** gNMI (gRPC Network Management Interface) is a protocol for network management and operations which is based out of gRPC framework uses HTTP/2 as its transport. gRPC uses protocol buffers as its data encoding enabling efficient configurations management and streaming live data. With gNMI, users can perform operations like `get`, `set`, and `subscribe` to state and configuration data on network devices.

**gNMIc:** gNMIc is an open-source tool that was written by Nokia and donated to OpenConfig. gNMIc provides full support for `get`/`set`/`capabilities` and `subscribe`. 

More details: [gNMIc](https://gNMIc.openconfig.net/) 

**Nokia SR OS:** Nokia SR OS gRPC server supports gNMI enabling operators to perform `get`/`set`/`capabilities` and `subscribe` operations.

## Getting Started

The hackathon lab topology provides a full operational network for you to use.  We will perform this lab on the `P1` node which is running Nokia SR OS.

### Step-1: Configuration of Nokia SR OS

In this lab, These configurations are already done, However you should verify that they are correct:

1. Enable gNMI

```
[gl:/configure system grpc]
A:admin@p1# info
    admin-state enable
    allow-unsecure-connection
    gNMI {
        admin-state enable
        auto-config-save true
    }
``` 

*Note: `allow-unsecure-connection` disabled TLS and should only be used in laboratory environments.*

2. Add `grpc` to the user's permissions

```
[gl:/configure system security user-params local-user user "admin"]
A:admin@p1# info
    access {
        console true
        ftp true
        netconf true
        grpc true
    }
```

3. Confirm the state using other CLI commands

```
A:admin@p1# show system grpc

===============================================================================
gRPC Server
===============================================================================
Administrative State      : Enabled
Operational State         : Up

Supported services          Version      Admin State
-------------------------------------------------------------------------------
gNMI                        0.8.0        Enabled
gNOI CertificateManagement  0.1.0        Disabled
gNOI File                   0.1.0        Enabled
gNOI System                 1.0.0        Disabled
mdCli                       24.3.0       Disabled
RibApi                      1.1.0        Enabled
===============================================================================
```
```
A:admin@p1# show system security user

===============================================================================
Users
===============================================================================
User ID      New User Permissions                 Password Login   Failed Local
             Pwd console ftp li snmp netconf grpc Expires  Attempt Logins Conf
-------------------------------------------------------------------------------
admin        n   y       y   n  n    y       y    never    651     427    y
-------------------------------------------------------------------------------
Number of users : 1
===============================================================================
``` 

### Step-2: Using the `capabilities` operation

During the capabilities check, the client discovers the capabilities of the gRPC server (Nokia SR OS here) through a capability discovery.

The `capabilities` RPC consists of `CapabiltyRequest` and `CapabilityResponse` messages. During this message exchange, the gRPC server informs the client about following attributes:

1. Supported gNMI version
2. Supported models
3. Supported encodings

*Run the following command:*
```
gnmic -a clab-srexperts-p1 -u admin -p SReXperts2024  --port 57400 --insecure capabilities
```

*Expected Output:*

```
gNMI version: 0.8.0
supported models:
  - nokia-conf, Nokia, 24.3.R2-1 
  - nokia-state, Nokia, 24.3.R2-1
  - nokia-li-state, Nokia, 24.3.R2-1
supported encodings:
  - JSON
  - BYTES
  - PROTO
  - JSON_IETF
```

### Step-3: Using the `get` operation

gNMIc can be used to pull information from the SR OS device.  Configuration and state information can be obtained.  Information is obtained using the `get` RPC which consists of `GetRequest` and `GetResponse` messages.

1. gNMIc `get` for port configurations

*Run the following command:*

```
gnmic -a clab-srexperts-p1 -u admin -p SReXperts2024  --port 57400 --insecure get --path "/configure/port[port-id="1/1/c1"]"
```
*Expected Output:*

```
[
  {
    "source": "clab-srexperts-p1",
    "timestamp": 1715844168161434396,
    "time": "2024-05-16T10:22:48.161434396+03:00",
    "updates": [
      {
        "Path": "configure/port[port-id=1/1/c1]",
        "values": {
          "configure/port": {
            "admin-state": "enable",
            "connector": {
              "breakout": "c1-100g"
            },
            "port-id": "1/1/c1"
          }
        }
      }
    ]
  }
]
```

2. gNMIc `get` for port state infomation

*Run the following command:*

```
gnmic -a clab-srexperts-p1 -u admin -p SReXperts2024  --port 57400 --insecure get --path "/state/port[port-id="1/1/c1"]"
```

*Expected output:*

```
[
  {
    "source": "clab-srexperts-p1",
    "timestamp": 1715844425237981874,
    "time": "2024-05-16T10:27:05.237981874+03:00",
    "updates": [
      {
        "Path": "state/port[port-id=1/1/c1]",
        "values": {
          "state/port": {
            "down-reason": "",
            "dwdm": {
              "laser-tunability": "not-tunable"
            },
            "far-end-port-id": "",
            "fp-number": 1,
            "hardware-mac-address": "00:00:00:00:00:00",
            "if-index": 1610899520,
            "interface-group-handler-index": 0,
            "licensed": true,
            "mac-chip-number": 1,
            "number-of-channels": 0,
            "oper-state": "up",
            "oper-state-last-changed": "2024-05-14T13:51:42.6Z",
```

### Step-4: Using the `set` operation

The `set` operation can only be performed with configuration data and is placed (on SR OS) into a private candidate configuration datastore

1. `set` operation with in-line values

Values can be set or updated using the keyword `update-value` with the `set` operation.

*Run the following command:*

```
gnmic -a clab-srexperts-p1 -u admin -p SReXperts2024  --port 57400 --insecure set --update-path "/configure/port[port-id="1/1/c10"]/description" --update-value "setting from gNMIc at srexperts2024"
```

*Expected output:*

```
{
  "source": "clab-srexperts-p1",
  "timestamp": 1715845540880131722,
  "time": "2024-05-16T10:45:40.880131722+03:00",
  "results": [
    {
      "operation": "UPDATE",
      "path": "configure/port[port-id=1/1/c10]/description"
    }
  ]
}
```

Alternatively, the `set` operation can be perfomed by supplying configuration from a file.

2. `set` operation from a file

*Run the following command:*

```
gnmic -a clab-srexperts-p1 -u admin -p SReXperts2024  --port 57400 --insecure set --update-path "/configure/port[port-id="1/1/c10"]/" --update-file port.json
```

Below is the provided JSON file named as port.json,  We can easily retrive this as a sample format from the node using the command `info json` under the respective context.

```
{
    "admin-state": "enable",
    "description": "setting using gNMIc on srexperts",
    "connector": {
        "breakout": "c10-10g"
    }
}
```

*Expected Output*

```
{
  "source": "clab-srexperts-p1",
  "timestamp": 1715846089622984552,
  "time": "2024-05-16T10:54:49.622984552+03:00",
  "results": [
    {
      "operation": "UPDATE",
      "path": "configure/port[port-id=1/1/c10]"
    }
  ]
}
```

### Step 5: Your task for this activity

Configure an OSPF neighborship between the `P1` and `P2` nodes using gNMIc.

*Hint: Consider these gNMIc commands*

Example command for the `P1` node:

```
gnmic -a clab-srexperts-p1 -u admin -p SReXperts2024  --port 57400 --insecure set --update-path "/configure/router[router-name="Base"]/ospf[ospf-instance="0"]" --update-file p1_ospf.json
```

Example command for the `P2` node:

```
gnmic -a clab-srexperts-p2 -u admin -p SReXperts2024  --port 57400 --insecure set --update-path "/configure/router[router-name="Base"]/ospf[ospf-instance="0"]" --update-file p2_ospf.json
```

An example configuration file for the `P1` node (in JSON) can be found [here](./example_solution/p1_ospf.json).  Take a look if you get stuck.

Once you are complete, verify the OSPF neighbor is available:

```
A:admin@p1# show router ospf neighbor

===============================================================================
Rtr Base OSPFv2 Instance 0 Neighbors
===============================================================================
Interface-Name                   Rtr Id          State      Pri  RetxQ   TTL
   Area-Id
-------------------------------------------------------------------------------
p2_1                             10.46.1.12      Full       1    0       40
   0.0.0.0
-------------------------------------------------------------------------------
No. of Neighbors: 1
===============================================================================
```

### Step-6: Using the `subscribe` operation

The `subscribe` RPC is a part of streaming telemetry support in gNMI. The gRPC client initiates a subscription by sending a `subscribe` RPC that contains a `SubscribeRequest` message to the gRPC server (The SR OS node).

Subscriptions have multiples modes.  You will use `once` and `sample` modes in this lab.

1. `once` mode collects the data once

*Run the following command:*

```
gnmic -a clab-srexperts-p1 -u admin -p SReXperts2024  --port 57400 --insecure sub --path "/state/system/cpu[sample-period="1"]" --mode once
```

2. `sample` mode collects the data at regular intervals

*Run the following command:*

```
gnmic -a clab-srexperts-p1 -u admin -p SReXperts2024  --port 57400 --insecure sub --path "/state/port[port-id="1/1/c1"]/statistics" --stream-mode sample --sample-interval 1s
```

## Conclusion

During this activity you have got hands-on with gNMI using the gRPC protocol and the gNMIc tool.  Nokia SR OS has provided you configuration and state data and has shown how powerful streaming (publish and subscribe) telemetry can be.

