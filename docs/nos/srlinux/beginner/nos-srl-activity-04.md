---
tags:
  - SR OS
  - SR Linux
  - gRIBI
---

# On demand traffic steering for firewall or packet inspection using gRIBI


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | On demand traffic steering for firewall or packet inspection using gRIBI |
| **Activity ID**           | 4 |
| **Short Description**       | Re-direct traffic to another temporary destination like firewall or packet inspector </p> Example usecases include: a temporary firewall and SDN controlled path injection </p>  |
| **Difficulty**              | Beginner |
| **Tools used**              | [gRIBIc](https://gribic.kmrd.dev/) |
| **Topology Nodes**          | :material-router: peering1, :material-router: peering2 |
| **References**              | [gRPC website](https://grpc.io/)<br/>[Openconfig gRIBI Specification](https://github.com/openconfig/gribi)<br/>[SR Linux documentation](https://documentation.nokia.com/srlinux/)<br/>[gNxI protobuf reference](https://gnxi.srlinux.dev/)<br/>[gRIBIc client](https://gribic.kmrd.dev/)<br/> |


A temporary firewall application is installed behind `peering1` and traffic for a specific prefix on `peering2` should be temporarily re-routed to this application. After some time, the re-routing should be removed. Your task is to program a route dynamically using APIs on `peering2` for a prefix and later remove it.

## Objective

We will create a loopback on `peering1` and assume the loopback IP as the IP of the firewall. Our task is to route traffic from `peering2` to the loopback IP on `peering1` using an on-demand injected route with a specific next hop.

```
        peering2----------------------------------peering1
  (LB: 22.10.22.10/32)                      (LB: 31.10.31.11/32)
    (NH: 10.64.51.1)                          (NH: 10.64.51.2)
```

In this activity, we will:

1. Create loopback interfaces on both `peering1` and `peering2` nodes.
2. On `peering1` node, we will create a static route to reach the `peering2` loopback.
3. Dynamically inject a route using API on `peering2` to reach `peering1` loopback.
4. Ping between the 2 loopbacks.
5. Dynamically remove the injected route

## Technology explanation

### gRPC
gRPC is an open source Remote Procedure Call (RPC) framework. To use a gRPC service, a gRPC client and a gRPC server are required. The client sends a gRPC request to the server who will then process the request and respond back to the client.

```
gRPC (client) --------(Request)-----------> gRPC (server)
gRPC (client) <-------(Response)----------- gRPC (server)
```

Protocol buffers (protobuf) encoding is used as the interface description language for the Request and Response messages and HTTP/2 is used as the transport protocol for the messaging. This means TLS can be applied to provide encryption.

Examples of gRPC servers include SR OS and SR Linux.

Examples of gRPC clients include gNMIc, gNOIc and gNSIc.

### gRIBI
gRIBI (gRPC RIB Injection) is a gRPC service for inserting routes into the RIB of a router. The inserted route has a protocol priority and behaves just like any other static or dynamically (IGP/BGP) learned route. Route injection using gRIBI is used to steer traffic to certain paths by a SDN controller or to re-direct traffic to a temporary destination like firewall.

gRIBI uses the OpenConfig AFT (Abstract Forwarding Table) model as an abstracted view of the device RIB. This allows the injected route entries to be consumed by gNMI `Get` and `Subscribe` RPCs. For our activity, the relevant AFTs are `nh` (for next hop), `nhg` (for next hop group) and `ipv4` (for destination prefix).

gRIBI has the following RPCs:

1. `Get` - information on existing installed gRIBI routes
2. `Modify` - install a route to the RIB and/or FIB
3. `Flush` - remove all installed gRIBI routes on the router

When using the `modify` RPC, the gRIBI client takes the route configuration in a `yaml` payload.

This gRIBI payload includes the following parameters:

1. `default-network-instance` - for our use case, this should be set to `default`.

2. `params` - defines options like client redundancy, route persistence and enable/disable FIB update. For our activity, this should be set to:

    ```yaml
    params:
      redundancy: single-primary
      persistence: preserve
      ack-type: rib-fib
    ```

3. `operations` - defines the IPv4 prefix, next hop group and next hop of the route. For our activity, we will use the `add` operation to program each one of those components. An example of this for next-hop is:

    ```yaml
      - op: add
        election-id: 1:0
        nh:
          index: 1
          ip-address: 172.16.1.1
    ```

    Similarly a Next hop group `nhg` can be defined tying the next-hop to the nhg using the next-hop index value.

    ```yaml
      - op: add
        election-id: 1:0
        nhg:
          id: 1
          next-hop:
            - index: 1
    ```

    Finally, the IPv4 prefix can defined and attached to the `nhg` index.

    ```yaml
      - op: add
        election-id: 1:0
        ipv4:
          prefix: 192.168.10.200/32
          nhg: 1
    ```


## Preparing the routers

**You should read these tasks from top-to-bottom before beginning the activity**.  

We will create loopbacks on `peering1` and `peering2`. On `peering1`, we will create a static route to reach `peering2` loopback.

### Configure loopback on `peering1` (an SR OS router)

Run `edit-config private` to enter the candidate mode and then `commit` after changes are completed.

/// tab | cmd

``` bash
/configure router "Base" interface "grib-loopback" loopback
/configure router "Base" interface "grib-loopback" ipv4 primary address 31.10.31.11
/configure router "Base" interface "grib-loopback" ipv4 primary prefix-length 32
```
///
/// tab | verify after commit

``` bash
admin show configuration full-context | match grib
```

///
/// tab | expected output after commit

``` bash
/configure router "Base" interface "grib-loopback" loopback
/configure router "Base" interface "grib-loopback" ipv4 primary address 31.10.31.11
/configure router "Base" interface "grib-loopback" ipv4 primary prefix-length 32
```
///

### Configure loopback on `peering2` (An SR Linux router)
Create a loopback interface on `peering2` and add it to `default` network-instance.

/// tab | cmd

``` bash
set / network-instance default interface lo1.0
set / interface lo1 subinterface 0 ipv4 admin-state enable
set / interface lo1 subinterface 0 ipv4 address 22.10.22.10/32
```

///
/// tab | verify after commit

``` bash
info flat from running | grep lo1
```

///
/// tab | expected output

``` bash
A:g15-peering2# info flat from running | grep lo1
set / network-instance default interface lo1.0
set / interface lo1 subinterface 0 ipv4 admin-state enable
set / interface lo1 subinterface 0 ipv4 address 22.10.22.10/32
```
///

### Configure static route on `peering1`
Create a static route on `peering1` to reach the loopback on `peering2`.

/// tab | cmd

``` bash
/configure router "Base" static-routes route 22.10.22.10/32 route-type unicast next-hop "10.64.51.2" admin-state enable
```

///
/// tab | verify after commit

``` bash
admin show configuration full-context | match static
```

///
/// tab | expected output

``` bash
A:admin@g15-peering1# admin show configuration full-context | match static
    /configure router "Base" static-routes route 22.10.22.10/32 route-type unicast next-hop "10.64.51.2" admin-state enable
```
///

### Configure gRIBI on `peering2`
An insecure gRPC server with gRIBI is already created on `peering2`. Verify the config of the insecure grpc server.

/// tab | cmd

``` bash
info flat system grpc-server insecure-mgmt
```

///
/// tab | expected output

``` bash
--{ candidate private private-admin }--[  ]--
A:g15-leaf11# info flat system grpc-server insecure-mgmt
set / system grpc-server insecure-mgmt admin-state enable
set / system grpc-server insecure-mgmt rate-limit 65000
set / system grpc-server insecure-mgmt network-instance mgmt
set / system grpc-server insecure-mgmt port 57400
set / system grpc-server insecure-mgmt trace-options [ request response common ]
set / system grpc-server insecure-mgmt services [ gnmi gnoi gribi p4rt ]
set / system grpc-server insecure-mgmt unix-socket admin-state enable
```
///

Based on the config, insecure gRPC server is listening on port 57400.

There are 4 gRPC services enabled in this config including gRIBI.

### Configure user for gRIBI client

Create a user `grclient1` that will be used by gRIBIc client to inject routes.

Remember to run `enter candidate private` to change to the candidate mode and `commit now` to save your changes.

/// tab | cmd

``` bash
set / system aaa authorization role gribi-clients services [ gribi ]
set / system aaa authentication user grclient1 password grclient1 role [ gribi-clients ]
```

///
/// tab | verify after commit

``` bash
info flat from running system aaa | grep client
```

///
/// tab | expected output

``` bash
A:g15-leaf11# info flat from running system aaa | grep client
set / system aaa authentication user grclient1 password $y$j9T$bcd1d72367d5f71e$FgwfvyKXBZwkPv7hrI45hqgQF3i20buJoaTmBjLLK9.
set / system aaa authentication user grclient1 role [ gribi-clients ]
set / system aaa authorization role gribi-clients services [ gribi ]
```
///

### Client Verification

We will be using gRIBIc as the client for injecting routes to `peering2`.

Verify that this client are installed on your host.

/// tab | gribic

``` bash
gribic version
```

///
/// tab | expected output

``` bash
❯ gribic version
version : 0.0.14
 commit : 26a317b
   date : 2023-11-14T23:24:49Z
 gitURL : https://github.com/karimra/gribic
   docs : https://gribic.kmrd.dev
```
///

if gRIBIc client is not installed or needs to be updated, refer to [gRIBIc page](https://gribic.kmrd.dev/) for more details.

Now that we confirmed that gRIBI is enabled on `peering2`, user is created and client is installed, let's do a quick test to verify gRIBI is operational on `peering2`.

We will use the `gRIBI Get` RPC to get the current installed gRIBI routes.

/// tab | cmd

``` bash
gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 get --ns default --aft ipv4
```

///
/// tab | expected output

``` bash
❯ gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 get --ns default --aft ipv4
INFO[0000] target clab-srexperts-peering2:57400: final get response:  
INFO[0000] got 1 results                                
INFO[0000] "clab-srexperts-peering2:57400":  
```
///

As expected, there are no gRIBI routes that are currently installed.

## Tasks

### Inject route on `peering2`

To reach `peering1` loopback IP, there should be a route on `peering2` with a next hop. This is typically advertised in a routing protocol like OSPF, ISIS, BGP or manually created as a static route.

Your task is to inject this route using an API call using gRPC gRIBI service.

After a successful ping is verified, remove the injected route using API call.

Prepare the gRIBI payload to inject the route for the loopback IP on `peering1`.

Before injecting the route, check if there are any existing routes to this destination.

/// tab | verify after commit

``` bash
show network-instance default route-table ipv4-unicast prefix 31.10.31.11/32
```

///
/// tab | expected output is empty

``` bash

```
///

Using gRIBIc, inject a route into `peering2` RIB to reach `peering1` loopback 31.10.31.11/32

Use `gRIBI Modify` RPC to inject this route to `peering2`. Replace `file.yml` with your payload file.

/// tab | cmd
``` bash
gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 modify --input-file file.yml
```
///
/// tab | expected output
``` bash
INFO[0000] trying to find variable file "file_vars.yml" 
INFO[0000] sending request=params:{redundancy:SINGLE_PRIMARY persistence:PRESERVE ack_type:RIB_AND_FIB_ACK} to "clab-srexperts-peering2:57400" 
INFO[0000] sending request=election_id:{high:1} to "clab-srexperts-peering2:57400" 
INFO[0000] clab-srexperts-peering2:57400
response: session_params_result: {} 
INFO[0000] clab-srexperts-peering2:57400
response: election_id: {
  high: 1
} 
INFO[0000] target clab-srexperts-peering2:57400 modify request:
****snip***
```
///

### Verify `peering2` route table
Verify `peering2` route table for the presence of gRIBI route.

/// tab | cmd
``` bash
show network-instance default route-table ipv4-unicast prefix 31.10.31.11/32 | as json
```
///
/// tab | expected output

``` bash hl_lines="10"
A:g15-peering2# show network-instance default route-table ipv4-unicast prefix 31.10.31.10/32 | as json
{
  "instance": [
    {
      "Name": "default",
      "ip route": [
        {
          "Prefix": "31.10.31.11/32",
          "ID": 1,
          "Route Type": "gribi",
          "Route Owner": "grpc_server",
          "Active": "True",
          "Origin Network Instance": "default",
          "Metric": 1,
          "Pref": 6,
          "Next-hop (Type)": "10.64.51.1 (direct)",
          "Next-hop Interface": "ethernet-1/2.0 ",
          "Backup Next-hop (Type)": "",
          "Backup Next-hop Interface": ""
        }
      ]
    }
  ]
}
```
///

### Test connectivity between the loopback addresses
Now that we created a route to reach the loopbacks on either nodes, we should be able to ping between the loopbacks.

Try ping on `peering2` towards `peering1` loopback 31.10.31.11/32

/// tab | cmd

``` bash
ping -c 3 31.10.31.11 network-instance default -I 22.10.22.10
```
///
/// tab | expected output

``` bash
A:g15-peering2# ping -c 3 31.10.31.11 network-instance default -I 22.10.22.10
Using network instance default
PING 31.10.31.11 (31.10.31.11) from 22.10.22.10 : 56(84) bytes of data.
64 bytes from 31.10.31.11: icmp_seq=1 ttl=64 time=3.67 ms
64 bytes from 31.10.31.11: icmp_seq=2 ttl=64 time=3.01 ms
64 bytes from 31.10.31.11: icmp_seq=3 ttl=64 time=4.06 ms

--- 31.10.31.11 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 3.006/3.580/4.063/0.436 ms
```
///

### Remove all gRIBI routes

When the firewall application use is complete, the gRIBI routes can be moved using `gRIBI Flush` RPC.

/// tab | cmd

``` bash
gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 flush --ns default --override
```
///
/// tab | expected output

``` bash
❯ gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 flush --ns default --override
INFO[0000] got 1 results                                
INFO[0000] "clab-srexperts-peering2:57400": timestamp: 1745865482482562426
result: OK 
```
///

## Solution

### gRIBI payload

For help, refer to the solution below.

/// details | gRIBI payload
    type: code
```yaml
default-network-instance: default

params:
  redundancy: single-primary
  persistence: preserve
  ack-type: rib-fib

operations:
  - op: add
    election-id: 1:0
    nh:
      index: 1
      ip-address: 10.64.51.1

  - op: add
    election-id: 1:0
    nhg:
      id: 1
      next-hop:
        - index: 1

  - op: add
    election-id: 1:0
    ipv4:
      prefix: 31.10.31.11/32
      nhg: 1
```
///

### Injecting the route

/// details | Injecting the route
/// tab | cmd
``` bash
gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 modify --input-file gribi-input.yml
```
///
/// tab | expected output

``` bash
❯ gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 modify --input-file gribi-input.yml
INFO[0000] trying to find variable file "gribi-input_vars.yml" 
INFO[0000] sending request=params:{redundancy:SINGLE_PRIMARY persistence:PRESERVE ack_type:RIB_AND_FIB_ACK} to "clab-srexperts-peering2:57400" 
INFO[0000] sending request=election_id:{high:1} to "clab-srexperts-peering2:57400" 
INFO[0000] clab-srexperts-peering2:57400
response: session_params_result: {} 
INFO[0000] clab-srexperts-peering2:57400
response: election_id: {
  high: 1
} 
INFO[0000] target clab-srexperts-peering2:57400 modify request:
operation: {
  id: 1
  network_instance: "default"
  op: ADD
  next_hop: {
    index: 1
    next_hop: {
      ip_address: {
        value: "10.64.51.1"
      }
    }
  }
  election_id: {
    high: 1
  }
} 
INFO[0010] target clab-srexperts-peering2:57400 modify request:
operation: {
  id: 2
  network_instance: "default"
  op: ADD
  next_hop_group: {
    id: 1
    next_hop_group: {
      next_hop: {
        index: 1
      }
    }
  }
  election_id: {
    high: 1
  }
} 
INFO[0010] clab-srexperts-peering2:57400
response: result: {
  id: 1
  status: FIB_PROGRAMMED
  timestamp: 1745865166674709126
} 
INFO[0010] clab-srexperts-peering2:57400
response: result: {
  id: 2
  status: FIB_PROGRAMMED
  timestamp: 1745865166684152065
} 
INFO[0010] target clab-srexperts-peering2:57400 modify request:
operation: {
  id: 3
  network_instance: "default"
  op: ADD
  ipv4: {
    prefix: "31.10.31.11/32"
    ipv4_entry: {
      next_hop_group: {
        value: 1
      }
    }
  }
  election_id: {
    high: 1
  }
} 
INFO[0010] target clab-srexperts-peering2:57400 modify stream done 
INFO[0010] clab-srexperts-peering2:57400
response: result: {
  id: 3
  status: FIB_PROGRAMMED
  timestamp: 1745865166688125845
} 
```
///
///

### Verifying using gRIBI

/// details | Verifying using gRIBI
We can also verify the gRIBI routes using `gRIBI Get` RPC.

To see the next-hop definition:

/// tab | cmd

``` bash
gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 get --ns default --aft nh
```
///
/// tab | expected output

``` bash
❯ gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 get --ns default --aft nh
INFO[0000] target clab-srexperts-peering2:57400: final get response: entry:{network_instance:"default" next_hop:{index:1 next_hop:{ip_address:{value:"10.64.51.1"}}} rib_status:PROGRAMMED fib_status:PROGRAMMED} 
INFO[0000] got 1 results                                
INFO[0000] "clab-srexperts-peering2:57400":
entry: {
  network_instance: "default"
  next_hop: {
    index: 1
    next_hop: {
      ip_address: {
        value: "10.64.51.1"
      }
    }
  }
  rib_status: PROGRAMMED
  fib_status: PROGRAMMED
}
```
///


To see the next-hop group definition:

/// tab | cmd

``` bash
gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 get --ns default --aft nhg
```
///
/// tab | expected output

``` bash
❯ gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 get --ns default --aft nhg
INFO[0000] target clab-srexperts-peering2:57400: final get response: entry:{network_instance:"default" next_hop_group:{id:1 next_hop_group:{next_hop:{index:1}}} rib_status:PROGRAMMED fib_status:PROGRAMMED} 
INFO[0000] got 1 results                                
INFO[0000] "clab-srexperts-peering2:57400":
entry: {
  network_instance: "default"
  next_hop_group: {
    id: 1
    next_hop_group: {
      next_hop: {
        index: 1
      }
    }
  }
  rib_status: PROGRAMMED
  fib_status: PROGRAMMED
} 
```
///

To see the destination prefix definition:

/// tab | cmd

``` bash
gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 get --ns default --aft ipv4
```
///
/// tab | expected output

``` bash
❯ gribic -a clab-srexperts-peering2:57400 --insecure -u grclient1 -p grclient1 get --ns default --aft ipv4
INFO[0000] target clab-srexperts-peering2:57400: final get response: entry:{network_instance:"default" ipv4:{prefix:"31.10.31.11/32" ipv4_entry:{next_hop_group:{value:1}}} rib_status:PROGRAMMED fib_status:PROGRAMMED} 
INFO[0000] got 1 results                                
INFO[0000] "clab-srexperts-peering2:57400":
entry: {
  network_instance: "default"
  ipv4: {
    prefix: "31.10.31.11/32"
    ipv4_entry: {
      next_hop_group: {
        value: 1
      }
    }
  }
  rib_status: PROGRAMMED
  fib_status: PROGRAMMED
}
```
///
///

## Additional Task

### Install default route
Let's apply this learning to install a default route on `peering2` using gRIBI.

Create the payload `yaml` file and use the RPCs above to inject the route.

### Solution

/// details | Solution - gRIBI payload
    type: code
```yaml
default-network-instance: default

params:
  redundancy: single-primary
  persistence: preserve
  ack-type: rib-fib

operations:
  - op: add
    election-id: 1:0
    nh:
      index: 1
      ip-address: 10.64.51.1

  - op: add
    election-id: 1:0
    nhg:
      id: 1
      next-hop:
        - index: 1

  - op: add
    election-id: 1:0
    ipv4:
      prefix: 0.0.0.0/0
      nhg: 1
```
///

## Summary

Congratulations! By this point you should have successfully completed the activity and redirected your traffic using the gRIBI gRPC service.  With the work you have put in, you should now have an understanding of the following topics:

- Using gRPC to perform activities on a remote router
- Simple configuration tasks on SR OS
- Simple configuration tasks on SR Linux
- Using the gRIBI service to manipulate the routing and forwarding table

Good job in completing all the tasks in this activity! 

