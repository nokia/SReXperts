---
tags:
  - template
  - markdown
  - styleguide
---

# Vendor neutral configuration management using Openconfig and gNMI


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Vendor neutral configuration management using Openconfig and gNMI                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Activity ID**           | 42                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Short Description**       | Perform a set of small configuration changes using vendor neutral OpenConfig YANG models over gNMI.  You will create a new loopback interface an advertise it's IP address over BGP.                                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [gNMIc](https://gnmic.openconfig.net/), [SR Linux](https://www.nokia.com/ip-networks/service-router-linux-NOS/)                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: spine11                                                                                                , :material-router: pe3                                                                                                                                                                                                                                                                                                                            |
| **References**              | [gRPC](https://grpc.io/)<br/>[gNxI](https://gnxi.srlinux.dev/)<br/>[Openconfig](https://www.openconfig.net/) |


Openconfig is a community based vendor neutral way for configuring and retrieving state from Network Operating Systems (NOS). Openconfig YANG models are managed by [OpenConfig](https://www.openconfig.net/).<br>

Openconfig yang models are published in [GitHub](https://github.com/openconfig/public).

Nokia SR Linux and SR OS both support Openconfig.

Due to the vendor neutral nature of the OpenConfig YANG models, they cannot cover every feature from every router vendor.  Therefore, a mix of vendor specific (also called native) and OpenConfig models are used to complete the configuration.

In this activity, we will explore OpenConfig (often referred to as "OC") YANG configuration and state using CLI and gNMI. We will then configure BGP on a SR Linux device using OC models.

## Objective

Your objective in this activity is to create a new loopback interface on a SR Linux device in order to attract traffic to that IP address. You will need to create the interface, provide it an IP address, and attach a route-policy that will advertise this prefix with a specific BGP community.

In this activity, we will:<br>

1. Enable OpenConfig on SR Linux
2. Read the routers configuration using OC
3. Read the routers state information using OC
4. Configure an interface using OC on the SR Linux CLI
4. Use gNMI to read configuration and state information using OC
5. Configure BGP using gNMI and OC to advertise the prefix with the correct attributes

## Technology explanation

### Openconfig

OpenConfig is a vendor neutral approach for configuring and retrieving state from a Network Operating System. OpenConfig models can be used via CLI, NETCONF or gRPC.

### gNMI

gRPC based Network Management Interface (gNMI) is a set of Remote Procedure Calls (RPC) that use the gRPC protocol to configure a network element, get state information and stream telemetry information. To implement gNMI, a client and server are required that understands gNMI RPCs. We will use [gNMIc](https://gnmic.openconfig.net/) as the client and the server will be the SR Linux router.

## Tasks

### Enable Openconfig in SR Linux

Login to `spine11` and change to candidate mode using `enter candidate`.

Run the following command to enable openconfig. After making the changes, run `commit now` to apply the changes.

/// tab | command
``` bash
set / system management openconfig admin-state enable
```
///
/// tab | verify after commit

``` bash
info flat from running /system management openconfig
```
///
/// tab | expected response

``` bash
set / system management openconfig admin-state enable
```
///

### Read the configuration using OpenConfig YANG models

Now that we have enabled OpenConfig, let's read the existing configuration on the device using the OpenConfig YANG models.

Because SR Linux does a built in translation between native and OC models, any configuration pushed using OC can be viewed in native mode and any configuration pushed via native can be viewed in OC mode provided the corresponding OC models are supported.

Here's quick reference table to assist you with switching between SR Linux (SRL) and OpenConfig (OC) modes in the SR Linux CLI.

|Model | From Mode | To Mode | Command |
|-----|-----------|---------|---------|
|SRL|running|candidate|`enter candidate`|
|SRL|candidate|running|`enter running`|
|SRL|candidate|state|`enter state`|
|SRL|running|state|`enter state`|
|SRL to OC|SRL running|OC running|`enter oc`|
|SRL to OC|SRL running|OC candidate|`enter oc candidate`|
|SRL to OC|SRL running|OC state|`enter oc state`|
|OC to SRL|OC running|SRL running|`enter srl`|
|OC to SRL|OC running|SRL candidate|`enter srl candidate`|
|OC to SRL|OC running|SRL state|`enter srl state`|

In summary, if you want to switch between the same mode on SRL and OC, use `enter srl` or `enter oc`.

If you want to switch to a different mode, then use the mode name (`running`/`candidate`/`state`) with the above command.

The current mode is displayed on the first line of the CLI prompt.

For example:

```bash hl_lines="1"
--{ + oc state }--[  ]--
A:g15-spine11#
```

Login to `spine11`, switch to OC running mode and display the interface configuration in OC mode.

To switch to OC mode:

```bash
enter oc
```

To display interface configuration:

/// tab | command
``` bash
info flat interfaces interface ethernet-1/31
```
///
/// tab | expected response

``` bash
set / interfaces interface ethernet-1/31 config name ethernet-1/31
set / interfaces interface ethernet-1/31 config type ethernetCsmacd
set / interfaces interface ethernet-1/31 config description spine11-pe3
set / interfaces interface ethernet-1/31 config enabled true
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 config index 0
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv6 addresses address fd00:fde8:0:1:15:23:31:1 config ip fd00:fde8:0:1:15:23:31:1
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv6 addresses address fd00:fde8:0:1:15:23:31:1 config prefix-length 127
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv6 config enabled true
```
///

The above interface was configured using SR Linux native models, but the configuration can be viewed in OC format.

### Read state information using OpenConfig

Now let's look at the OC state information of this interface.

To enter OC state mode:

```bash
enter oc state
```

To display interface state information:

/// tab | command
``` bash
info flat interfaces interface ethernet-1/31 state counters
```
///
/// tab | expected response

``` bash
/ interfaces interface ethernet-1/31 state counters in-octets 28194796
/ interfaces interface ethernet-1/31 state counters in-pkts 180118
/ interfaces interface ethernet-1/31 state counters in-unicast-pkts 145378
/ interfaces interface ethernet-1/31 state counters in-broadcast-pkts 0
/ interfaces interface ethernet-1/31 state counters in-multicast-pkts 34737
/ interfaces interface ethernet-1/31 state counters in-errors 3
/ interfaces interface ethernet-1/31 state counters in-discards 0
/ interfaces interface ethernet-1/31 state counters out-octets 254612533
/ interfaces interface ethernet-1/31 state counters out-pkts 2123668
/ interfaces interface ethernet-1/31 state counters out-unicast-pkts 2091309
/ interfaces interface ethernet-1/31 state counters out-broadcast-pkts 0
/ interfaces interface ethernet-1/31 state counters out-multicast-pkts 32359
/ interfaces interface ethernet-1/31 state counters out-discards 0
/ interfaces interface ethernet-1/31 state counters out-errors 0
/ interfaces interface ethernet-1/31 state counters in-fcs-errors 0
/ interfaces interface ethernet-1/31 state counters carrier-transitions 0
```
///

We can see the OC state information for an interface configured using SR Linux native model.

### Configure an interface using the OpenConfig (OC) CLI mode

Next, let's configure an interface IP address using OC CLI.

We will configure an IPv4 address on `ethernet-1/31` connected to `PE3`. An IPv6 address is already configured on this interface using the SR Linux native model. With this task, we also prove that a mix of native and OC models are possible under the same object.

To switch to OC candidate mode, use:

```bash
enter oc candidate
```

Run the below configuration:

/// tab | command
``` bash
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv4 addresses address 10.10.10.0 config ip 10.10.10.0
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv4 addresses address 10.10.10.0 config prefix-length 31
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv4 config enabled true
```
///
/// tab | verify after commit

``` bash
info flat from running interfaces interface ethernet-1/31
```
///
/// tab | expected response
``` bash  hl_lines="6"
set / interfaces interface ethernet-1/31 config name ethernet-1/31
set / interfaces interface ethernet-1/31 config type ethernetCsmacd
set / interfaces interface ethernet-1/31 config description spine11-pe3
set / interfaces interface ethernet-1/31 config enabled true
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 config index 0
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv4 addresses address 10.10.10.0 config ip 10.10.10.0
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv4 addresses address 10.10.10.0 config prefix-length 31
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv4 config enabled true
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv6 addresses address fd00:fde8:0:1:15:23:31:1 config ip fd00:fde8:0:1:15:23:31:1
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv6 addresses address fd00:fde8:0:1:15:23:31:1 config prefix-length 127
set / interfaces interface ethernet-1/31 subinterfaces subinterface 0 ipv6 config enabled true
```
///

Now that we pushed the above interface config in OC, let's view it SR Linux model.

To switch to SRL running mode:

```bash
enter srl running
```

/// tab | command
``` bash
info flat from running interface ethernet-1/31
```
///
/// tab | expected response

``` bash
set / interface ethernet-1/31 description spine11-pe3
set / interface ethernet-1/31 admin-state enable
set / interface ethernet-1/31 subinterface 0 ipv4 admin-state enable
set / interface ethernet-1/31 subinterface 0 ipv4 address 10.10.10.0/31
set / interface ethernet-1/31 subinterface 0 ipv6 admin-state enable
set / interface ethernet-1/31 subinterface 0 ipv6 address fd00:fde8:0:1:15:23:31:1/127
```
///

### Use gNMI to read configuration and state using OpenConfig

Next, we will use gNMI to retrieve config and state in OC format.

gNMI client is installed on your host VM. Verify it using:

/// tab | command
``` bash
gnmic version
```
///
/// tab | expected output
``` bash
version : 0.40.0
 commit : 3f13e44d
   date : 2025-01-27T22:03:58Z
 gitURL : https://github.com/openconfig/gnmic
   docs : https://gnmic.openconfig.net
```
///

Run the gNMI `Capabilities` RPC to verify the operational status of gNMI itself on the device.

From your host VM:

/// tab | command
``` bash
gnmic -a clab-srexperts-spine11:57400 -u admin -p $EVENT_PASSWORD --insecure cap
```
///
/// tab | expected output
``` bash
gNMI version: 0.10.0
supported models:
  - urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring:ietf-netconf-monitoring, IETF NETCONF (Network Configuration) Working Group, 2010-10-04
  - urn:ietf:params:xml:ns:yang:ietf-yang-library:ietf-yang-library, IETF NETCONF (Network Configuration) Working Group, 2019-01-04
  - urn:nokia.com:srlinux:aaa:aaa:srl_nokia-aaa, Nokia, 2024-10-31
  - urn:nokia.com:srlinux:aaa:aaa-password:srl_nokia-aaa-password, Nokia, 2024-03-31
  - urn:nokia.com:srlinux:aaa:aaa-types:srl_nokia-aaa-types, Nokia, 2023-03-31
  ---snip----
  - http://openconfig.net/yang/system:openconfig-system, OpenConfig working group, 2023-12-20
  - http://openconfig.net/yang/system-controlplane:openconfig-system-controlplane, OpenConfig working group, 2023-03-03
  - http://openconfig.net/yang/system-grpc:openconfig-system-grpc, OpenConfig working group, 2022-04-19
  - http://openconfig.net/yang/system-utilization:openconfig-system-utilization, OpenConfig working group, 2023-02-13
  - http://openconfig.net/yang/vlan:openconfig-vlan, OpenConfig working group, 2023-02-07
supported encodings:
  - JSON_IETF
  - PROTO
  - ASCII
  --snip--
```
///

In the output above, you will see the list of openconfig models are the supported by the device.

Now that we confirmed that gNMI is operational on `spine11`, let's get the interface configuration in OC format.

/// tab | command
``` bash
gnmic -a clab-srexperts-spine11:57400 -u admin -p $EVENT_PASSWORD --insecure get --path "openconfig:/interfaces/interface[name=ethernet-1/31]" -e json_ietf --type config
```
///
/// tab | expected output
``` bash
[
  {
    "source": "clab-srexperts-spine11:57400",
    "timestamp": 1746484347756010950,
    "time": "2025-05-06T01:32:27.75601095+03:00",
    "updates": [
      {
        "Path": "openconfig:interfaces/interface[name=ethernet-1/31]",
        "values": {
          "interfaces/interface": {
            "config": {
              "description": "spine11-pe3",
              "enabled": true,
              "name": "ethernet-1/31",
              "type": "iana-if-type:ethernetCsmacd"
            },
            "subinterfaces": {
              "subinterface": [
                {
                  "config": {
                    "index": 0
                  },
                  "index": 0,
                  "openconfig-if-ip:ipv4": {
                    "addresses": {
                      "address": [
                        {
                          "config": {
                            "ip": "10.10.10.0",
                            "prefix-length": 31
                          },
                          "ip": "10.10.10.0"
                        }
                      ]
                    },
                    "config": {
                      "enabled": true
                    }
                  },
                  "openconfig-if-ip:ipv6": {
                    "addresses": {
                      "address": [
                        {
                          "config": {
                            "ip": "fd00:fde8:0:1:15:23:31:1",
                            "prefix-length": 127
                          },
                          "ip": "fd00:fde8:0:1:15:23:31:1"
                        }
                      ]
                    },
                    "config": {
                      "enabled": true
                    }
                  }
                }
              ]
            }
          }
        }
      }
    ]
  }
```
///

Next, let's get the OC state information of this interface using gNMI. To do this, we will remove the `type` option from the previous command. The command will then default to getting the state information. To reduce the output, we will get only the counters from this interface.

The gNMI path for this object can be obtained from CLI using the `pwc xpath` command.


```bash
--{ + oc state }--[ interfaces interface ethernet-1/31 state ]--
A:g15-spine11# pwc xpath
/interfaces/interface[name=ethernet-1/31]/state
```

/// tab | cmd
``` bash
gnmic -a clab-srexperts-spine11:57400 -u admin -p $EVENT_PASSWORD --insecure get --path "openconfig:/interfaces/interface[name=ethernet-1/31]/state" -e json_ietf
```
///
/// tab | expected output
``` bash
[
  {
    "source": "clab-srexperts-spine11:57400",
    "timestamp": 1746484446619698764,
    "time": "2025-05-06T01:34:06.619698764+03:00",
    "updates": [
      {
        "Path": "openconfig:interfaces/interface[name=ethernet-1/31]/state",
        "values": {
          "interfaces/interface/state": {
            "admin-status": "UP",
            "counters": {
              "carrier-transitions": "0",
              "in-broadcast-pkts": "0",
              "in-discards": "0",
              "in-errors": "3",
              "in-fcs-errors": "0",
              "in-multicast-pkts": "34838",
              "in-octets": "28252060",
              "in-pkts": "180498",
              "in-unicast-pkts": "145657",
              "out-broadcast-pkts": "5",
              "out-discards": "0",
              "out-errors": "0",
              "out-multicast-pkts": "32451",
              "out-octets": "256009833",
              "out-pkts": "2135307",
              "out-unicast-pkts": "2102851"
            },
            "description": "spine11-pe3",
            "enabled": true,
            "ifindex": 999422,
            "last-change": "1745511341684000000",
            "loopback-mode": "NONE",
            "management": false,
            "mtu": 9232,
            "name": "ethernet-1/31",
            "openconfig-platform-port:hardware-port": "Ethernet-1/31-Port",
            "openconfig-platform-transceiver:transceiver": "Ethernet-1/31-transceiver",
            "oper-status": "UP",
            "type": "iana-if-type:ethernetCsmacd"
          }
        }
      }
    ]
  }
]
```
///

### Configure BGP using gNMI and the OpenConfig YANG models

We will now configure a BGP neighbor to `pe3 ` using OC.

To prepare for this, we need the OpenConfig BGP payload in JSON format.

The below payload creates a BGP group called `oc-bgp` and adds an IPv4 neighbor.

/// tip | How to generate JSON payload
The easiest way to generate the payload is to do the configuration in the SR Linux CLI and display it in OC with JSON format. For example: after configuring BGP in SR Linux, change to `oc running mode` and then run `info network-instances network-instance default protocols protocol BGP name BGP bgp neighbors neighbor 10.10.10.1 | as json`
///

Copy the below payload to a file called `oc-bgp.json` on your host VM.

/// details | OC BGP payload
    type: code
```json
{
  "network-instances": {
    "network-instance": [
      {
        "name": "default",
        "protocols": {
          "protocol": [
            {
              "identifier": "BGP",
              "name": "BGP",
              "bgp": {
                "peer-groups": {
                  "peer-group": [
                    {
                      "peer-group-name": "oc-bgp",
                      "config": {
                        "peer-group-name": "oc-bgp",
                        "peer-as": 65000
                      },
                      "afi-safis": {
                        "afi-safi": [
                          {
                            "afi-safi-name": "IPV4_UNICAST",
                            "config": {
                              "afi-safi-name": "IPV4_UNICAST",
                              "enabled": true
                            }
                          }
                        ]
                      }
                    }
                  ]
                },
				"neighbors": {
                  "neighbor": [
                    {
                      "neighbor-address": "10.10.10.1",
                      "config": {
                        "peer-group": "oc-bgp",
                        "neighbor-address": "10.10.10.1"
                      }
                    }
                  ]
                }
              }
            }
          ]
        }
      }
    ]
  }
}
```
///

Using gNMIc, use the `set` RPC to push the OpenConfig configuration to `spine11`.

/// tab | cmd

``` bash
gnmic -a clab-srexperts-spine11:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path openconfig:/ --update-file oc-bgp.json --encoding=JSON_IETF
```
///
/// tab | expected output
``` bash
{
  "source": "clab-srexperts-spine11:57400",
  "timestamp": 1746560230200785690,
  "time": "2025-05-06T22:37:10.20078569+03:00",
  "results": [
    {
      "operation": "UPDATE",
      "path": "openconfig:"
    }
  ]
}
```
///

Verify the configuration in SR Linux CLI.

/// tab | cmd

``` bash
enter srl running
info flat network-instance default protocols bgp neighbor 10.10.10.1
```
///
/// tab | expected output
``` bash
set / network-instance default protocols bgp neighbor 10.10.10.1 peer-group oc-bgp
```
///

To finish the configuration, login to the neighboring `pe3` device and configure interface and BGP facing `spine11`.

/// tab | cmd
``` bash
edit-config private
/configure router "Base" interface "spine11" ipv4 primary address 10.10.10.1
/configure router "Base" interface "spine11" ipv4 primary prefix-length 31
/configure router "Base" bgp group "oc-bgp" peer-as 4200001000
/configure router "Base" bgp group "oc-bgp" family ipv4 true
/configure router "Base" bgp neighbor "10.10.10.0" group "oc-bgp"
commit
```
///
/// tab | verify after commit
``` bash
admin show configuration full-context | match 10.10.10
```
///
/// tab | expected out
``` bash
/configure router "Base" interface "spine11" ipv4 primary address 10.10.10.1
/configure router "Base" bgp neighbor "10.10.10.0" group "oc-bgp"
```
///

Now, on SR Linux verify BGP neighbor session is UP.

/// tab | cmd
``` bash
show network-instance default protocols bgp neighbor 10.10.10.1 | as json
```
///
/// tab | expected out
``` bash hl_lines="12"
{
  "neighbor summary": [
    {
      "network-instance": "default",
      "state": [
        {
          "Net-Inst": "default",
          "Peer": "10.10.10.1",
          "Group": "oc-bgp",
          "Flags": "S",
          "Peer-AS": 65000,
          "State": "established",
          "Uptime": "0d:0h:14m:10s",
          "AFI/SAFI": "ipv4-unicast",
          "[Rx/Active/Tx]": "[0/0/15]"
        }
      ],
      "config": [
        {
          "network-instance": "default",
          "configured-peers": 1,
          "configured-up-peers": 1,
          "disabled-peers": 0,
          "dynamic-peers": 5
        }
      ]
    }
  ]
}
```
///



### Create a loopback interface and advertise it in BGP using route policy

Now it's time to put all these pieces together and achieve the objectives of this activity.

Create a loopback interface on `spine11` with IP `10.0.5.5/32` and advertise to the BGP neighbor we configured earlier. Attach a route policy that will add a community `2025:9` to this route advertisement.

All this should be done using gNMI and OC models.

Here are the configuration steps to help you:

1. Create loopback interface with IP `10.0.5.5/32`
2. Create a routing policy prefix-list for this IP
3. Create a routing policy community-set for `2025:9`
4. Create a routing policy to match the prefix-list and action to add the community
5. Attach the routing policy to the BGP neighbor `10.10.10.1`
6. Add the loopback interface to `default` network-instance

To get the OC payload, configure the required objects in SR Linux CLI. Then change to `oc running` mode and view the configuration in JSON format.

After the configuration is pushed, verify that the loopback IP is advertised to the neighbor with the community value on `spine11`.

/// tab | cmd
``` bash
show network-instance default protocols bgp routes ipv4 prefix 10.0.5.5/32 detail
```
///
/// tab | expected output
``` bash hl_lines="22"
----------------------------------------------------------------------------------------------------------
Show report for the BGP routes to network "10.0.5.5/32" network-instance  "default"
----------------------------------------------------------------------------------------------------------
Network: 10.0.5.5/32
Received Paths: 1
  Path 1: <Best,Valid,Used,>
    Route source    : neighbor 0.0.0.0
    Route Preference: MED is -, No LocalPref
    BGP next-hop    : 0.0.0.0
    Path            :  i
    Communities     : None
    RR Attributes   : No Originator-ID, Cluster-List is [ - ]
    Aggregation     : Not an aggregate route
    Unknown Attr    : None
    Invalid Reason  : None
    Tie Break Reason: none

Path 1 was advertised to: 
[ 10.10.10.1 ]
Route Preference: MED is -, No LocalPref
Path            :  i [4200001000]
Communities     : 2025:9
RR Attributes   : No Originator-ID, Cluster-List is [ - ]
Aggregation     : Not an aggregate route
Unknown Attr    : None
----------------------------------------------------------------------------------------------------------
```
///

/// details | Solution - OC payload for loopback interface and route policy
    type: code
```json
{
  "interfaces": {
    "interface": [
      {
        "name": "lo1",
        "config": {
          "name": "lo1",
          "type": "softwareLoopback"
        },
        "subinterfaces": {
          "subinterface": [
            {
              "index": 0,
              "config": {
                "index": 0
              },
              "ipv4": {
                "addresses": {
                  "address": [
                    {
                      "ip": "10.0.5.5",
                      "config": {
                        "ip": "10.0.5.5",
                        "prefix-length": 32
                      }
                    }
                  ]
                },
                "config": {
                  "enabled": true
                }
              }
            }
          ]
        }
      }
    ]
  },
  "routing-policy": {
    "defined-sets": {
      "prefix-sets": {
        "prefix-set": [
          {
            "name": "loopback",
            "config": {
              "name": "loopback"
            },
            "prefixes": {
              "prefix": [
                {
                  "ip-prefix": "10.0.5.5/32",
                  "masklength-range": "32..32",
                  "config": {
                    "ip-prefix": "10.0.5.5/32",
                    "masklength-range": "32..32"
                  }
                }
              ]
            }
          }
        ]
      },
      "bgp-defined-sets": {
        "community-sets": {
          "community-set": [
            {
              "community-set-name": "oc-comm",
              "config": {
                "community-set-name": "oc-comm",
                "community-member": [
                  "2025:9"
                ]
              }
            }
          ]
        }
      }
    },
    "policy-definitions": {
      "policy-definition": [
        {
          "name": "oc-export",
          "config": {
            "name": "oc-export"
          },
          "statements": {
            "statement": [
              {
                "name": "lb1",
                "config": {
                  "name": "lb1"
                },
                "conditions": {
                  "match-prefix-set": {
                    "config": {
                      "prefix-set": "loopback"
                    }
                  }
                },
                "actions": {
                  "config": {
                    "policy-result": "ACCEPT_ROUTE"
                  },
                  "bgp-actions": {
                    "set-community": {
                      "config": {
                        "options": "ADD"
                      },
                      "reference": {
                        "config": {
                          "community-set-ref": "oc-comm"
                        }
                      }
                    }
                  }
                }
              }
            ]
          }
        }
      ]
    }
  },
    "network-instances": {
    "network-instance": [
      {
        "name": "default",
        "protocols": {
          "protocol": [
            {
              "identifier": "BGP",
              "name": "BGP",
              "bgp": {
                "neighbors": {
                  "neighbor": [
                    {
                      "neighbor-address": "10.10.10.1",
                      "apply-policy": {
                        "config": {
                          "export-policy": [
                            "oc-export"
                          ]
                        }
                      }
                    }
                  ]
                }
              }
            }
          ]
        },
		"interfaces": {
          "interface": [
            {
              "id": "lo1.0",
              "config": {
                "id": "lo1.0"
              }
            }
          ]
        }
      }
    ]
  }
}
```
///

## Summary

Congratulations! By this point you should have successfully completed the activity and have configured your router using the OpenConfig YANG models. With the work you have put in, you should now have an understanding of the following topics:

- Using gRPC to perform activities on a remote router
- Using the SR Linux CLI to navigate and change configuration and state in using OpenConfig YANG models
- Using gNMIc to configure the SR Linux device over gNMI using OpenConfig YANG models

Good job in completing all the tasks in this activity!
