---
tags:
  - SR OS
  - pySROS
  - TPSDA
  - BNG
  - Radius
  - configuration
---

# Dynamic configuration management with Radius


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Dynamic configuration management with Radius                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Activity ID**             | 63                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Short Description**       | Explore the SR OS feature introduced in 24.10.R1 that allows pySROS Python applications to be run based on subscriber management events.
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/), [Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html), [Python programming language](https://www.python.org), [Python 3 API for SR OS](https://documentation.nokia.com/sr/25-3/tpsda-python-3-api/index.html),[MicroPython](https://micropython.org/)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: PE4, :material-account-circle-outline: sub1, sub2 and sub3, :material-radius-outline: Radius|
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html)<br/>[Triple Play Service Delivery Architecture (TPSDA) with Enhanced Subscriber Management (ESM)](https://documentation.nokia.com/sr/25-3/7750-sr/books/tpsda/triple-play-enhanced-subscriber-management.html)<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/system-management.html)<br/>[pySROS user documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)<br/>[pySROS GitHub](https://github.com/nokia/pysros) (check the examples directory)<br/>[Radius Attributes](https://documentation.nokia.com/sr/25-3/7750-sr/titles/radius.html)<br/>[Dynamic Data Services](https://documentation.nokia.com/sr/25-3/7750-sr/books/tpsda/dynamic-data-services-triple-play.html) |


The BNG node `PE4` in the Hackathon topology makes use of the on-board Python utilities to streamline DHCP and Radius flows to and from the client network and Radius server, respectively. These Python scripts make it so that all subscribers in the topology can be authenticated and assigned an IP address despite some inconsistencies in the way clients present themselves and the way the Radius server expects them to be identified. Changes on the client or Radius side would have complicated the solution as neither side has visibility of the other, while the BNG has access to both flows.

With the advent of SR OS release 24.10.R1, model-driven SR OS now has the capability to trigger pySROS Python applications based on subscriber management events. This feature enables a Radius server to send Extended VSAs that will be interpreted by the router and used to decide when and which Python scripts should be run. In this activity we will explore this limited support feature.

Wasting no time, the Radius configuration has already been updated to make use of this feature by sending the necessary VSAs to add service configuration and perform a connectivity check using `ping`. In this activity you will add the functionality necessary to `PE4` to interpret and use those attributes.

## Objective

For each subscriber in the topology, the Radius server has been configured to add script parameters in responses to successful authentication attempts. In this activity, we will look at what the Radius server sends and we will make sure the BNG `PE4` implements the desired behavior. As you'll see, for one of the subscribers that involves sending a `ping` request while for others the behavior involves changing service configuration.

The aim of this activity is to show how powerful the Radius integration using pySROS can be in implementing complex business logic in an automated way, reducing human error and operating costs. To do this, we will go through the following list of tasks:

1. Check how subscriber sessions can be created and deleted at will
2. Look at the Radius attributes being sent down by the Radius server in Access-Accept
3. Explore the state and configuration required in SR OS for this feature to be usable
4. Modify the pre-created scripts to send a `ping` to confirm `sub1` is reachable
5. Modify the pre-created scripts for `sub2` and `sub3` to do the necessary service configuration

Only :material-router: PE4 will be configured in this activity. Some commands need to be executed on the other nodes listed above however they are of an ephemeral nature. When relevant, the configuration to be rolled back once the usecase is completed will be highlighted.

## Technology explanation

In this chapter, we will discuss the tools that will be used throughout the exercise.

### Python on SR OS and pySROS
Modern releases of model-driven SR OS provide a [Python environment](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html) using the [MicroPython](https://docs.micropython.org/en/latest/index.html) interpreter. The [pySROS library](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html) provides a way to programmatically interface with SR OS from a Python script and allows a developer to query and modify the various datastores. This script can be executed either locally on the box or remotely from a Python-capable machine in which case pySROS also handles the connection to the remote model-driven SR OS node

In this activity we use new functionality introduced in model-driven SR OS that allows certain events related to Enhanced Subscriber Management (ESM) to create and manage a [control channel](https://documentation.nokia.com/sr/25-3/7750-sr/books/tpsda/dynamic-data-services-triple-play.html#radius-triggered-pysros-script-execution) that controls pySROS script execution. A Radius Access-Accept or Change of Authorization (CoA) is used to trigger the script with varying parameters. These parameters and the script reference are specified in the message as Radius VSA (Vendor Specific Attributes).

### TPSDA

The Triple Play Service Delivery Architecture guide details amongst other things the implementation flow of subscriber management on the BNG, as well as the related Command Line Interface (CLI) syntax and command usage. The answers to most questions you might have around subscriber management can be found in this document. It talks about DHCP in all it's variants, PPPoE sessions, NAT, different manners of associating hosts with authentication and accounting policies or adding more information to them without making changes on the client side, security, redundancy, quality of service, how and where to use Python along with many more topics.

To understand the general flow of the subscribers in this activity and to understand which elements may be causing trouble, the following sequence happens when a subscriber comes online:

1. Client broadcasts a DHCP Discover message
2. BNG receives the DHCP Discover and sends a Radius Authentication Request to the Radius server.
3. Radius checks the data in the Access Request and sends back either Access-Accept or Access-Reject.
4. BNG receives the Access-Accept and creates a subscriber context, an Access-Reject would be indicative of a problem.
5. The remaining exchange of DHCP Request, Offer and Acknowledgment is performed so the client gets an IP address.
6. Now, the client is "online".

Among the additional topics not explicitly mentioned before are the [dynamic data services](https://documentation.nokia.com/sr/25-3/7750-sr/books/tpsda/dynamic-data-services-triple-play.html#dynamic-data-services-in-model-driven-config-mode). This functionality allows configuration to be added to a router based on a Radius-triggered pySROS script. We only consider the model-driven variety of the feature here, as the functionality is different for classic SR OS.

The general flow will involve sending `Alc-PySROS-Script-Policy` and `Alc-PySROS-Script-Params`, respectively extended Vendor Specific Attribute (VSA) `241.26.6527.98` and `241.26.6527.99`, down from the Radius server in either Access-Accept or CoA. These attributes contain string values. The first can contain the name of a `script-policy` on the target router and the second contains up to 1000 bytes of input to be passed into the pySROS application. These bytes are made available inside the application as if they were parameters passed in.

In addition, context is provided to the pySROS application by the system. This includes information about the subscriber ID, service, which SAP it is associated with and the device's MAC address. The system also provides the lifecycle state of the subscriber session to the application. With these inputs, we can use pySROS to create configuration or perform actions when a subscriber is created and clear the configuration if the subscriber is deleted.

### Model-driven SR OS and the MD-CLI

As the term "model-driven" suggests, a model-driven Network Operating System (NOS) such as SR OS has one or more data models at its core. These data models compile together to provide the schema for the system. These data models are written using a language called YANG and, in the case of SR OS, are available [online](https://github.com/nokia/7x50_YangModels).

#### Configuration management

One of the advantages of model-driven SR OS is that the system becomes transactional in nature. Changes have to be explicitly applied from a candidate configuration to the running configuration via a commit operation rather than being immediately applied. This reduces the chances for operational issues to occur as a result of partial configuration changes. SR OS will atomically apply configuration changes to the system, this means that either all changes stored in the candidate configuration datastore will be successfully applied upon a commit, or none of them will be applied and your device will remain operationally intact.

You will notice during this activity that configuration changes made will not be applied and the traditional configuration change indicator `*` only disappears upon issuing a `commit` command.

#### Configuration modes

Something that will come up as you move through the activity are the [operational and configuration mode](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/edit-configuration.html) of the MD-CLI. The status is indicated in the command prompt.

/// details | Command prompt in operational mode
```
[/]
A:admin@g15-pe1#
```
///
/// details | Command prompt in exclusive configuration mode
```
(ex)[/]
A:admin@g15-pe1#
```
///

The `/state` branch is accessible in either mode while configuration changes can only be made after switching to configuration mode. Whether that be for the `li`, `bof`, `configure` or `debug` contexts, an operator must first open a configuration session before being able to make any changes. The latter two are relevant to this activity. There are four candidate configuration modes; `read-only`, `private`, `global` and `exclusive`. They are documented in detail in the [MD-CLI User Guide](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/edit-configuration.html#unique_813655187).

If any changes have been made to the running configuration that aren't reflected in your configuration session this is made clear through a `!` character being prepended to the prompt.

#### Debugging
The `debug` context is another tree similar to the `configure` tree in model-driven SR OS. Any time you need to add debug statements you would open an exclusive configuration session for the `debug` tree and enter your changes followed by a `commit` statement to apply those changes. A pre-configured logging destination exists for you in the form of `log 21`. This log is set up to receive data from any active debug sources and to display it back to the CLI. To inspect the log you can use either `show log log-id 21` or use the command `tools perform log subscribe-to log-id 21` to subscribe to any events in your current terminal. This can be undone with `tools perform log unsubscribe-from log-id 21`.

In this activity, all Radius traffic resides in the `Base` routing instance while all DHCP traffic exchanged between `PE4` and subscribers resides in routing instance `bng-vprn` with service ID `401`. In order to visualize the Radius and DHCP packets being exchanged, these variables will have to be taken into account.

### The Hackathon BNG environment

As this activity revolves entirely the BNG, let's briefly look at what is currently in place on the BNG that is part of the Hackathon topology. Some details on the existing implementation are included in this section that may be useful later.

In the Hackathon topology three subscribers exist who are aggregated and connected to the `PE4` BNG. On that BNG they reach a [`capture-sap`](https://documentation.nokia.com/sr/25-3/7750-sr/books/tpsda/subscriber-management.html#managed-sap-and-capture-sap) in VPLS 400, `bng-vpls`. Any time a DHCP packet reaches this SAP this leads to an attempted authentication of the subscriber based on information in the DHCP packet against the Radius server at `10.64.13.0`, reachable and configured in the `Base` routing instance of the BNG. If that authentication is successful, a managed SAP is created in a `group-interface` under a `subscriber-interface` in VPRN 401, `bng-vprn`. This is where the subscriber is instantiated.

Due to inconsistencies between the client and Radius configuration only two of the subscribers were online initially. Configuration and Python scripts have been written to align both sides of the interaction so that three subscribers are active and working in the current state of the topology. These modifications had to be configured in the VPLS, the VPRN and also applied to the Radius server configuration in the BNG.

In addition, to improve usability, further modifications were included in the BNG to assign subscriber identifiers that includes some information learned from the client side as well as some information learned from the Radius server. In the client case DHCP Option 61 is used and Radius attribute 25, Class, is used on the other side. Both are combined to form a subscriber ID on the BNG currently.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

All supporting files can be found in the `activities/nos/sros/activity-63` directory of the repository.

### Confirm the initial situation

Access `PE4` using SSH by connecting from your group's hackathon VM to the hostname `clab-srexperts-pe4` or by connecting remotely to your group's hackathon VM on port 50024 as that is forwarded to `PE4` as well. Use the login credentials provided to you. Use `show service active-subscribers` on `PE4` to verify which subscribers are online. Initially, three subscribers should exist in the system.

Any issues with the pre-existing configuration or Python scripts would lead to two or less subscribers being available and this would form an issue for the activity, so make sure you **reach out for help if the expected three subscribers do not exist**. The subscribers are assigned subscriber identifiers by the system made up of a combination of their DHCP Circuit ID provided by the client and the Radius Class attribute provided by the Radius server.

/// details | Verify the initial state of subscribers in the system
/// tab | Command
```
show service active-subscribers
```
///
/// tab | Expected output
```
[/]
A:admin@g##-pe4# show service active-subscribers

===============================================================================
Active Subscribers
===============================================================================
-------------------------------------------------------------------------------
Subscriber 0ff1ce0100cafe
           (SUB_PROF1)
-------------------------------------------------------------------------------
NAT Policy    : NAT_POL1
Outside IP    : 10.67.200.1
Ports         : 1024-1055

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
(1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
-------------------------------------------------------------------------------
IP Address
              MAC Address        Session            Origin       Svc        Fwd
-------------------------------------------------------------------------------
10.24.1.112
              00:d0:f6:01:01:01  IPoE               DHCP         401        Y
-------------------------------------------------------------------------------

-------------------------------------------------------------------------------
Subscriber 0ff1ce0200beef
           (SUB_PROF1)
-------------------------------------------------------------------------------
NAT Policy    : NAT_POL1
Outside IP    : 10.67.200.0
Ports         : 1024-1055

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
(1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
-------------------------------------------------------------------------------
IP Address
              MAC Address        Session            Origin       Svc        Fwd
-------------------------------------------------------------------------------
10.24.1.113
              00:d0:f6:02:02:02  IPoE               DHCP         401        Y
-------------------------------------------------------------------------------

-------------------------------------------------------------------------------
Subscriber 0ff1ce0300babe
           (SUB_PROF1)
-------------------------------------------------------------------------------
NAT Policy    : NAT_POL1
Outside IP    : 10.67.200.2
Ports         : 1024-1055

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
(1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
-------------------------------------------------------------------------------
IP Address
              MAC Address        Session            Origin       Svc        Fwd
-------------------------------------------------------------------------------
10.24.1.114
              00:d0:f6:03:03:03  IPoE               DHCP         401        Y
-------------------------------------------------------------------------------

-------------------------------------------------------------------------------
Number of active subscribers : 3
===============================================================================
```
///
///

### Force a renewal of a subscriber

When doing any development, you will need to be able to verify the outcome of your changes. For the remainder of the exercise and before we get into further customization, make sure you can trigger DHCP and RADIUS interactions on-demand. You can remove sessions on BNG `PE4` forcibly, however this won't necessarily cause a renewal on the client side. For testing purposes, the easiest solution is simply triggering a renewal on the client side by flipping the relevant link down and up again.

To do this, log in to any of the emulated client devices, available as `clab-srexperts-sub1`, `clab-srexperts-sub2` and `clab-srexperts-sub3` from your group's hackathon VM or, when SSHing into them directly, you may use port `50061`, `50062` and `50063`. Use the login credentials provided to you. Once logged in, run `sudo ifdown eth1.100; sudo ifup eth1.100` to force a new DHCP transaction. For convenience, you may want to wrap this action in a loop. This could be done as follows:

```bash
while :; do sudo ifdown eth1.100; sudo ifup eth1.100; sleep 300; done
```

You could also start the `crond` process on the emulated subscribers using `sudo crond`. A cron job will then begin to run every 5 minutes to renew the lease on interface `eth1.100`. For debugging purposes on the subscriber side, when going this route, you may prefer to use `sudo crond -l 1 -L /var/log/crond.log`.

/// details | Subscriber renewal as seen from client `sub1`
/// tab | Command
```bash
bash# while :; do sudo ifdown eth1.100; sudo ifup eth1.100; sleep 15; done
```
///
/// tab | Expected output
```bash
bash# while :; do sudo ifdown eth1.100; sudo ifup eth1.100; sleep 300; done
udhcpc: started, v1.36.1
udhcpc: broadcasting discover
udhcpc: broadcasting select for 10.24.1.112, server 10.24.1.5
udhcpc: lease of 10.24.1.112 obtained from 10.24.1.5, lease time 604800
udhcpc: started, v1.36.1
udhcpc: broadcasting discover
udhcpc: broadcasting select for 10.24.1.112, server 10.24.1.5
udhcpc: lease of 10.24.1.112 obtained from 10.24.1.5, lease time 604800
udhcpc: started, v1.36.1
udhcpc: broadcasting discover
udhcpc: broadcasting select for 10.24.1.112, server 10.24.1.5
udhcpc: lease of 10.24.1.112 obtained from 10.24.1.5, lease time 604800
udhcpc: started, v1.36.1
udhcpc: broadcasting discover
udhcpc: broadcasting select for 10.24.1.112, server 10.24.1.5
udhcpc: lease of 10.24.1.112 obtained from 10.24.1.5, lease time 604800
... (truncated)
```
///
///

### Using debug statements, view the existing Radius traffic in the topology

Now that we are able to renew clients to test our setup at will, the next objective is being able to visualize Radius messages so that we can evaluate behavior where necessary. This can be done in several ways, however the BNG `PE4` being the central part of the solution taking part in both the Radius and DHCP flows makes it particularly well suited.

Being empty by default, to see anything coming through the debug logs we have to add debug configuration for anything to appear. Remember that log 21 was created specifically for us to capture and monitor debug statements.

/// details | Log 21 configuration
```
configure {
  log {
    log-id "21" {
      admin-state enable
      description "debug log"
      source {
          debug true
      }
      destination {
          cli {
          }
      }
    }
  }
}

```
///

Above, the different contexts and configuration modes have been highlighted. To add configuration to the debug context we will have to open an `exclusive` configuration session on it and add the required statements. Add configuration to the debug context to ensure that all Radius traffic related to authentication from the Radius server with IP address `10.64.13.0` in the Base router is marked as debug information.

/// details | Expected result
```
[ex:/debug]
A:admin@g23-pe4# info
    router "Base" {
        radius {
            servers {
                packet-types {
                    authentication true
                    accounting false
                    coa false
                }
                server-address 10.64.13.0 { }
            }
        }
    }
```
///

If additional information from the Radius server is required, the server's logs can be viewed using

`docker exec -it  clab-srexperts-radius tail -f /var/log/radius/radius.log`

As an example, consider that this file may include additional information from the Radius server about why it is declining certain requests. Before proceeding to the next section, find out for the three subscribers in our topology which values the Radius server is returning in the Radius Access Accept for attributes `Alc-PySROS-Script-Policy` and `Alc-PySROS-Script-Params`.

/// details | Gather information being sent down by Radius
/// tab | Trigger a renewal for each subscriber host
For sub1:

```bash
bash# sudo ifdown eth1.100; sudo ifup eth1.100
udhcpc: started, v1.36.1
udhcpc: broadcasting discover
udhcpc: broadcasting select for 10.24.1.112, server 10.24.1.5
udhcpc: lease of 10.24.1.112 obtained from 10.24.1.5, lease time 604800
```
For sub2:
```bash
bash# sudo ifdown eth1.100; sudo ifup eth1.100
udhcpc: started, v1.36.1
udhcpc: broadcasting discover
udhcpc: broadcasting select for 10.24.1.113, server 10.24.1.5
udhcpc: lease of 10.24.1.113 obtained from 10.24.1.5, lease time 604800
```

For sub3:
```bash
bash# sudo ifdown eth1.100; sudo ifup eth1.100
udhcpc: started, v1.36.1
udhcpc: broadcasting discover
udhcpc: broadcasting select for 10.24.1.114, server 10.24.1.5
udhcpc: lease of 10.24.1.114 obtained from 10.24.1.5, lease time 604800
```
///
/// tab | Captured Radius debug logs on BNG `PE4`
Using either `show log log-id 21` or `tools perform log subscribe-to log-id 21` with the debug setting set as indicated before.
```hl_lines="58-61 119-122 185-188"
[/]
A:admin@g23-pe4# /tools perform log subscribe-to log-id 21

16814 2025/05/03 19:57:25.191 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Access-Request(1) 10.64.13.0:1812 id 96 len 175 vrid 1 pol RadPolicy1
    USER NAME [1] 17 00:d0:f6:01:01:01
    PASSWORD [2] 16 hxnISblmudYVLaY1eisO/U
    NAS IP ADDRESS [4] 4 10.46.23.24
    VSA [26] 7 DSL(3561)
      AGENT CIRCUIT ID [1] 5 0x04 0f f1 ce 01
    NAS PORT TYPE [61] 4 Ethernet(15)
    NAS PORT ID [87] 12 1/1/c3/1:100
    VSA [26] 73 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:01:01:01
      TO-SERVER DHCP OPTIONS [102] 52
        Message type [53] 1 discover
        Max msg size [57] 2 0x02 40
        Param request list [55] 7 0x01 03 06 0c 0f 1c 2a
        Host name [12] 4 0x73 75 62 31
        Class id [60] 12 0x75 64 68 63 70 20 31 2e 33 36 2e 31
        Client id [61] 4 0x0f f1 ce 01
        Relay agent information [82]
          AGENT CIRCUIT ID [1] 5 ▒▒
        End [255]



16815 2025/05/03 19:57:25.195 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Receive
  Access-Accept(2) id 96 len 407 from 10.64.13.0:1812 vrid 1 pol RadPolicy1
    MESSAGE AUTHENTICATOR [80] 16 0x66aecd017608e482c80ef2870954bdde
    FRAMED IP ADDRESS [8] 4 10.24.1.112
    FRAMED IP NETMASK [9] 4 255.255.255.0
    VSA [26] 6 Nokia(6527)
      DEFAULT ROUTER [18] 4 10.24.1.5
    CLASS [25] 2 0xcafe
    VSA [26] 11 Nokia(6527)
      SUBSC PROF STR [12] 9 SUB_PROF1
    VSA [26] 6 Nokia(6527)
      MSAP SERVICE ID [31] 4 401
    VSA [26] 9 Nokia(6527)
      MSAP INTERFACE [33] 7 GrpInt1
    VSA [26] 11 Nokia(6527)
      SLA PROF STR [13] 9 SLA_PROF1
    VSA [26] 13 Nokia(6527)
      SLAAC IPV6 POOL [181] 11 POOL_IPV6ND
    VSA [26] 9 Nokia(6527)
      DELEGATED IPV6 POOL [131] 7 REGULAR
    VSA [26] 11 Nokia(6527)
      TO-CLIENT DHCP OPTIONS [103] 9
        Classless Static Route Option [121] 7 0x10 0a 40 0a 18 01 05
    VSA [26] 38 Nokia(6527)
      TO-CLIENT DHCP6 OPTIONS [192] 36
        DNS_NAME_SRVR [23] 32 0x20 01 0d b8 00 01 00 01 00 01 00 01 00 01 00 01 20 01 0d b8 00 01 00 01 00 01 00 01 00 01 00 02
    VSA [26] 19 Nokia(6527)
      ANCP STR [16] 17 00:d0:f6:01:01:01
    VSA [241.26] 5 Nokia(6527)
      PYSROS SCRIPT POLICY [98] 5 sub1-script-policy
    VSA [241.26] 139 Nokia(6527)
      PYSROS SCRIPT PARAMS [99] 139 {'PING':{'target':10.24.1.112,'source':'192.168.211.1','size':500}}



16820 2025/05/03 19:57:26.369 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Access-Request(1) 10.64.13.0:1812 id 100 len 175 vrid 1 pol RadPolicy1
    USER NAME [1] 17 00:d0:f6:02:02:02
    PASSWORD [2] 16 WFVynIYLaYfpJpvKUcdraU
    NAS IP ADDRESS [4] 4 10.46.23.24
    VSA [26] 7 DSL(3561)
      AGENT CIRCUIT ID [1] 5 0x04 0f f1 ce 02
    NAS PORT TYPE [61] 4 Ethernet(15)
    NAS PORT ID [87] 12 1/1/c3/1:100
    VSA [26] 73 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:02:02:02
      TO-SERVER DHCP OPTIONS [102] 52
        Message type [53] 1 discover
        Max msg size [57] 2 0x02 40
        Param request list [55] 7 0x01 03 06 0c 0f 1c 2a
        Host name [12] 4 0x73 75 62 32
        Class id [60] 12 0x75 64 68 63 70 20 31 2e 33 36 2e 31
        Client id [61] 4 0x0f f1 ce 02
        Relay agent information [82]
          AGENT CIRCUIT ID [1] 5 ▒▒
        End [255]



16821 2025/05/03 19:57:26.374 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Receive
  Access-Accept(2) id 100 len 247 from 10.64.13.0:1812 vrid 1 pol RadPolicy1
    MESSAGE AUTHENTICATOR [80] 16 0x3823a8c6492174e3dda4c4126e0fb26d
    FRAMED IP ADDRESS [8] 4 10.24.1.113
    FRAMED IP NETMASK [9] 4 255.255.255.0
    VSA [26] 6 Nokia(6527)
      DEFAULT ROUTER [18] 4 10.24.1.5
    CLASS [25] 2 0xbeef
    VSA [26] 11 Nokia(6527)
      SUBSC PROF STR [12] 9 SUB_PROF1
    VSA [26] 6 Nokia(6527)
      MSAP SERVICE ID [31] 4 401
    VSA [26] 9 Nokia(6527)
      MSAP INTERFACE [33] 7 GrpInt1
    VSA [26] 11 Nokia(6527)
      SLA PROF STR [13] 9 SLA_PROF1
    VSA [26] 13 Nokia(6527)
      SLAAC IPV6 POOL [181] 11 POOL_IPV6ND
    VSA [26] 9 Nokia(6527)
      DELEGATED IPV6 POOL [131] 7 REGULAR
    VSA [26] 11 Nokia(6527)
      TO-CLIENT DHCP OPTIONS [103] 9
        Classless Static Route Option [121] 7 0x10 0a 40 0a 18 01 05
    VSA [26] 38 Nokia(6527)
      TO-CLIENT DHCP6 OPTIONS [192] 36
        DNS_NAME_SRVR [23] 32 0x20 01 0d b8 00 01 00 01 00 01 00 01 00 01 00 01 20 01 0d b8 00 01 00 01 00 01 00 01 00 01 00 02
    VSA [26] 19 Nokia(6527)
      ANCP STR [16] 17 00:d0:f6:02:02:02
    VSA [241.26] 5 Nokia(6527)
      PYSROS SCRIPT POLICY [98] 5 sub2-3-script-policy
    VSA [241.26] 139 Nokia(6527)
      PYSROS SCRIPT PARAMS [99] 139 {'SVC':{'id':10011,'name':'dynsvc-epipe-1','SAP':{'id':'1/1/c6/1:3000','desc':'client-sub2-vlan3000'}}}


16822 2025/05/03 19:57:26.374 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Script
  Access-Accept(2) id 100 len 247 from 10.64.13.0:1812 policy python-policy status success


16826 2025/05/03 19:57:27.719 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Access-Request(1) 10.64.13.0:1812 id 104 len 196 vrid 1 pol RadPolicy1
    PASSWORD [2] 16 S3eNGhHJbRSW4eHzhZlt4k
    NAS IP ADDRESS [4] 4 10.46.23.24
    VSA [26] 10 DSL(3561)
      AGENT CIRCUIT ID [1] 8 0x04 0f f1 ce 03 02 ba be
    NAS PORT TYPE [61] 4 Ethernet(15)
    NAS PORT ID [87] 12 1/1/c3/1:100
    VSA [26] 94 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:03:03:03
      TO-SERVER DHCP OPTIONS [102] 73
        Message type [53] 1 discover
        Max msg size [57] 2 0x02 40
        Param request list [55] 7 0x01 03 06 0c 0f 1c 2a
        Host name [12] 4 0x73 75 62 33
        Class id [60] 12 0x75 64 68 63 70 20 31 2e 33 36 2e 31
        Client id [61] 4 0x0f f1 ce 03
        Client FQDN [81] 16 0x00 03 73 65 72 76 65 72 2e 6f 66 66 69 63 65 33
        Relay agent information [82]
          AGENT CIRCUIT ID [1] 8 ▒▒▒▒
        End [255]
    USER NAME [1] 14 server.office3



16827 2025/05/03 19:57:27.723 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Receive
  Access-Accept(2) id 104 len 247 from 10.64.13.0:1812 vrid 1 pol RadPolicy1
    MESSAGE AUTHENTICATOR [80] 16 0x65828f6967fcd9dba9922ccbbd244ce7
    FRAMED IP ADDRESS [8] 4 10.24.1.114
    FRAMED IP NETMASK [9] 4 255.255.255.0
    VSA [26] 6 Nokia(6527)
      DEFAULT ROUTER [18] 4 10.24.1.5
    CLASS [25] 2 0xbabe
    VSA [26] 11 Nokia(6527)
      SUBSC PROF STR [12] 9 SUB_PROF1
    VSA [26] 6 Nokia(6527)
      MSAP SERVICE ID [31] 4 401
    VSA [26] 9 Nokia(6527)
      MSAP INTERFACE [33] 7 GrpInt1
    VSA [26] 11 Nokia(6527)
      SLA PROF STR [13] 9 SLA_PROF1
    VSA [26] 13 Nokia(6527)
      SLAAC IPV6 POOL [181] 11 POOL_IPV6ND
    VSA [26] 9 Nokia(6527)
      DELEGATED IPV6 POOL [131] 7 REGULAR
    VSA [26] 11 Nokia(6527)
      TO-CLIENT DHCP OPTIONS [103] 9
        Classless Static Route Option [121] 7 0x10 0a 40 0a 18 01 05
    VSA [26] 38 Nokia(6527)
      TO-CLIENT DHCP6 OPTIONS [192] 36
        DNS_NAME_SRVR [23] 32 0x20 01 0d b8 00 01 00 01 00 01 00 01 00 01 00 01 20 01 0d b8 00 01 00 01 00 01 00 01 00 01 00 02
    VSA [26] 19 Nokia(6527)
      ANCP STR [16] 17 00:d0:f6:03:03:03
    VSA [241.26] 5 Nokia(6527)
      PYSROS SCRIPT POLICY [98] 5 sub2-3-script-policy
    VSA [241.26] 139 Nokia(6527)
      PYSROS SCRIPT PARAMS [99] 139 {'SVC':{'id':10011,'name':'dynsvc-epipe-1','SAP':{'id':'1/1/c6/1:3001','desc':'client-sub3-vlan3000'}}}
```
///
///

### Explore the configuration required in SR OS for this feature to be usable

As outlined in the [TPSDA guide](https://documentation.nokia.com/sr/25-3/7750-sr/books/tpsda/dynamic-data-services-triple-play.html#radius-triggered-pysros-script-execution), the Radius attributes received by the system are used as a reference to a `script-policy` on the one hand and as input for aforementioned script on the other. The `script-policy` in turn refers to a `python-script`. Based on the information from the last step, check the configuration in the system that would be called as a result of the ESM events that follow the receipt of this Access-Accept message.

/// details | Findings from the previous step
We found that for subscriber 1, in this setup, the `script-policy` being called is `sub1-script-policy` and the parameters supplied are `{'PING':{'target':10.24.1.112,'source':'192.168.211.1','size':500}}`. This indicates that the system will send a ping to the subscriber as an extra check.

For subscribers 2 and 3, we see that the situation is different. In both cases, their assigned `script-policy` is `sub2-3-script-policy`, and the input is a service configuration. This configuration is intended to let interfaces on these clients communicate with each other through an epipe service set up on `PE4`, whereby the service is assigned a SAP only when the subscriber has an active IPoE session.
///

To complete this task, look into the configuration for the script policies and check if they are functional. Use any combination of navigating through the configuration with `info`, `show` and `state` commands to find out which changes are required to make the `script-policy` objects and the related `python-script`s operational.

/// details | Changes required
/// tab | Explanation
The status we find in the configuration is that each script-policy has been administratively disabled. In addition, the results locations has been set to `/null` to ensure there can be no clogging up of the system with log files that aren't being looked at. For debugging and development purposes, we will write the output generated by our script-policy whenever it runs to a directory on `cf3:`.
///
/// tab | Commands
```
*[gl:/configure]
A:admin@g23-pe4# compare /
    configure {
        system {
            script-control {
                script-policy "sub1-script-policy" owner "TiMOS CLI" {
-                   admin-state disable
+                   admin-state enable
-                   results "/null"
+                   results "cf3:/sub1_results/"
                }
                script-policy "sub2-3-script-policy" owner "TiMOS CLI" {
-                   admin-state disable
+                   admin-state enable
-                   results "/null"
+                   results "cf3:/sub2_3_results/"
                }
            }
        }
    }

[gl:/configure]
A:admin@g23-pe4# /file make-directory sub1_results/

[gl:/configure]
A:admin@g23-pe4# /file make-directory sub2_3_results/

```
///
///

### Prepare a debugging script for the script-policy executions

You may find that it is time-consuming to look for the directories linked to each script-policy, followed by searching for available files in that directory before being able to look at the output of any script-policy.

Since any script executions triggered from Radius invoke a `script-policy`, that would be a hurdle to get over any time the policy is executed and any output of the script needs to be collected. For troubleshooting that is a mild inconvenience and so we are using a Python script that has been prepared as an alias in the `PE4` node.

Configuration for this alias you can find in both the `configure system management-interface cli md-cli environment` and `/configure python python-script script-policy-results` contexts.

There, you will see that the file is reached from SR OS using the TFTP location `tftp://172.31.255.29/script-policy-results.py`. This is a mounted file available in the Hackathon repository path `clab/configs/sros/script-policy-results.py`. You can call the command via its alias using `/show script-policy-results`.

### Complete `sub1-python-script.py` for the desired behavior

Having done all the preparation and research, we are now ready to use the inputs sent by the Radius server.

For subscriber `sub1` the input sent down by Radius requests a `ping` be sent to verify that the subscriber host is replying to ICMP.

Modify the file available on your group's hackathon VM under the path `/home/nokia/SReXperts/activities/nos/sros/activity-63/sub1-python-script.py`.

This file is mounted inside the SR OS container and comes pre-configured as a `python-script`.

When you make changes, load them into `SR OS` using `perform python python-script reload script sub1-python-script` on `PE4`.

If needed, you can display the version of the script in memory using `show python python-script sub1-python-script source-in-use`.

Find and decode the information sent by Radius using the [`pysros.esm`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.esm) module and send an [ICMP request](https://github.com/nokia/7x50_YangModels/blob/master/latest_sros_24.10/nokia-oper-global.yang#L9304) using the corresponding modeled [action](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Connection.action) from pySROS.

As an approach for your script, consider the following steps:

- Load the parameter information provided to the script
- Connect to the node using the pySROS `connect` method
- Send a `ping` operation using the loaded parameters
- Output the result of your `ping` operation

You can test the behavior of the script by renewing the session of `clab-srexperts-sub1`. The debug alias can show you any outputs generated by your script.

/// details | Example implementation for `sub1-python-script.py`
/// tab | Example output
```
[/]
A:admin@pe4# /show script-policy-results sub1-script-policy
>>> Showing output for script policy sub1-script-policy from cf3:/sub1_results/_20250517-222637-UTC.769933.out

+-- results:
|   +-- probe:
|   |   `-- 1:
|   |       +-- probe-index: 1
|   |       +-- round-trip-time: 3736
|   |       +-- response-packet:
|   |       |   +-- size: 508
|   |       |   +-- source-address: 10.24.1.112
|   |       |   +-- icmp-sequence-number: 1
|   |       |   `-- ttl: 64
|   |       `-- status: response-received
|   +-- summary:
|   |   `-- statistics:
|   |       +-- packets:
|   |       |   +-- sent: 1
|   |       |   +-- received: 1
|   |       |   `-- loss: 0.0
|   |       `-- round-trip-time:
|   |           +-- average: 3736
|   |           +-- maximum: 3736
|   |           +-- standard-deviation: 0
|   |           `-- minimum: 3736
|   `-- test-parameters:
|       +-- interval: 1
|       +-- timeout: 5
|       +-- size: 500
|       +-- router-instance: bng-vprn
|       +-- destination: 10.24.1.112
|       +-- do-not-fragment: False
|       +-- ttl: 64
|       +-- preference: 100
|       +-- tos: 0
|       +-- output-format: detail
|       +-- count: 1
|       +-- pattern: sequential
|       +-- srv6-policy: False
|       +-- candidate-path: False
|       +-- bypass-routing: False
|       +-- fc: nc
|       `-- source-address: 192.168.211.1
+-- operation-id: 25
+-- end-time: 2025-05-17T22:26:39.1Z
+-- start-time: 2025-05-17T22:26:37.7Z
`-- status: completed
```
///

/// tab | `sub1-python-script.py`
```python
from pysros.esm import get_event
from pysros.management import connect
from pysros.pprint import printTree
import json

def sub1_script_policy():
    event = get_event()
    if event.eventparameters["scriptAction"] == "create":
        # Freeradius configuration format difference
        params_dict = json.loads(event.eventparameters["scriptParams"]
            .replace("'", "__*")
            .replace('"', "'")
            .replace("__*", '"')
        )["PING"]
        ping_target = params_dict["target"]
        ping_source = params_dict["source"]
        ping_payload_size = params_dict["size"]

        connection = connect()
        ping_result  = connection.action(
            "/nokia-oper-global:global-operations/ping",
            {
                "destination": ping_target,
                "router-instance": "bng-vprn",
                "source-address": ping_source,
                "count": 1,
                "size": ping_payload_size
            }
        )
        printTree(ping_result)

if __name__ == "__main__":
    sub1_script_policy()
```
///
///

### Complete `sub2-3-python-script.py` for the desired behavior

Sending pings is only one of the possible applications of this feature. For the other subscribers, `sub2` and `sub3`, the input sent down by Radius contains inputs required for configuring a service that is expected by the customer in addition to the subscriber management service provided.

As before, we can accommodate this using Python.

Modify the file available on your group's hackathon VM under the path `/home/nokia/SReXperts/activities/nos/sros/activity-63/sub2-3-python-script.py`.

This file is mounted inside the SR OS container and comes pre-configured as a `python-script`.

When you make changes, load them into SR OS using `perform python python-script reload script sub2-3-python-script` on `PE4`.

If needed, you can display the version of the script in memory using `show python python-script sub2-3-python-script source-in-use`.

Find and decode the information sent by Radius using the [`pysros.esm`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.esm) module and build the necessary logic into your script to create, modify or delete the epipe service any time one of the subscribers is created or deleted in the system. Use the subscriber lifecycle state information provided by the system to decide which changes to the service configuration are required.

As an approach for your script, consider the following steps:

- Load the service parameter information provided to the script
- Determine what lifecycle state change triggered this execution
- Connect to the node using the pySROS `connect` method
- Make the appropriate changes to the configuration
- Generate some output so that the result can be verified.

!!! note "Shared service"
    As both `sub2` and `sub3` have a SAP assigned to them, consider that deleting the entire service whenever one of the subscribers is deleted may not be the correct approach.

You can test the behavior of the script by starting, stopping or renewing the sessions of `clab-srexperts-sub2` and `clab-srexperts-sub3`. Use the provided debug alias to look at the outputs generated by your script.

/// details | Example implementation for `sub2-3-python-script.py`
```python
from pysros.esm import get_event
from pysros.management import connect
import json

def sub2_3_script_policy():
    event = get_event()

    # Freeradius configuration format difference
    params_dict = json.loads(event.eventparameters["scriptParams"]
        .replace("'", "__*")
        .replace('"', "'")
        .replace("__*", '"')
    )["SVC"]

    cust_id = '1' if "customer" not in params_dict.keys() else params_dict["customer"]
    svc_id = params_dict["id"]
    svc_name = params_dict["name"]
    sap_id = params_dict["SAP"]["id"]
    sap_desc = params_dict["SAP"]["desc"]

    connection = connect()
    path = '/configure/service/epipe[service-name="%s"]' % svc_name
    payload = {
        'service-name': svc_name,
        'admin-state': 'enable',
        'service-id': svc_id,
        'customer': cust_id,
        'sap': {
            sap_id: {
                'sap-id': sap_id,
                'description': sap_desc
            }
        }
    }
    if event.eventparameters["scriptAction"] == "create":
        connection.candidate.set(path, payload)
        print("Successfully created service %s." % svc_name)
    elif event.eventparameters["scriptAction"] == "delete":
        # if we are the last SAP in the service: delete the service
        sap_list = connection.running.get_list_keys(path + "/sap")
        if len(sap_list) <= 1:
            # it is an epipe, so max 2 SAPs
            connection.candidate.delete(path)
            print("Successfully deleted service %s, we were the last SAP." % svc_name)
        else:
            connection.candidate.delete(path+"/sap[sap-id=%s]" %sap_id)
            print("Successfully deleted SAP %s in %s, we were not the last SAP." % (sap_id, svc_name))

if __name__ == "__main__":
    sub2_3_script_policy()
```
///

### Test your dynamic epipe service

The configuration of the subscribers expects that `sub2`'s second interface on VLAN 2000 has layer-2 connectivity to VLAN 3000 on the second interface of `sub-3` in subnet `192.168.190.0/24`. Confirm they can reach each other using `ping`.

```bash
bash# ping -c 1 192.168.190.3
PING 192.168.190.3 (192.168.190.3) 56(84) bytes of data.
64 bytes from 192.168.190.3: icmp_seq=1 ttl=64 time=1.36 ms
```

### Optional - sending custom log events

An optional yet useful addition to this usecase is to add logging that goes beyond the file under the `results` directory defined under the `script-policy`. You could do this with pySROS using the [`custom-event ` action](https://github.com/nokia/7x50_YangModels/blob/master/latest_sros_24.10/nokia-oper-perform.yang#L1439). You can explore adding this functionality to your scripts. There is [an activity](../beginner/9-custom-generic-log.md){:target="_blank"} that dives into the details of this feature and its possible uses.

### Rollback the configuration to reduce system impact

To ensure your Hackathon instance's performance isn't affected by the changes done in this usecase, ensure that the `script-policy` configuration results are pointed to `/null` as in the original situation, and stop any loops or `cron` tasks that may be renewing subscriber sessions for testing.

/// details | Suggestions to help with rolling back
/// tab | Commands on `PE4`
```
edit-config private
configure system script-control script-policy "sub1-script-policy" results "/null"
configure system script-control script-policy "sub2-3-script-policy" results "/null"
commit
exit all
quit-config
```
///
/// tab | Stopping `crond` on `sub` instances
```bash
bash# sudo kill -8 "$(pgrep crond.*)"

```
///
///

## Summary and review

Congratulations!  If you have got this far you have completed this activity and achieved the following:

- You have gone over the details of how an IPoE session is set up in SR OS, and probably set up a few manually
- You have written or modified one or more applications using the Python 3 programming language
- You have used the model-driven CLI for changing configuration and inspecting Radius traffic flows in model-driven SR OS
- You have made the behavior of SR OS dynamic and subject to inputs from Radius, in at least two different ways
- You have created and tested solutions using a combination of SR OS and Linux

This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity, or try to expand upon this one if you have some more ideas. If you'd like to replicate the alias available for troubleshooting and quickly browsing through script-policy outputs [try this activity](nos-sros-activity-62.md).
