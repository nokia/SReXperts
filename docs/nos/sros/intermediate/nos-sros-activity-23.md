---
tags:
  - SR OS
  - pySROS
  - TPSDA
  - BNG
  - NAT
  - Radius
  - configuration
---

# Customizing DHCP and Radius flows with "alc"


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Customizing DHCP and Radius flows with "alc"                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Activity ID**             | 23                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Short Description**       | The BNG node `PE4` in the Hackathon topology makes use of the on-board Python utilities to streamline DHCP and Radius flows to and from the client network and Radius server, respectively. These Python scripts make it so that all subscribers in the topology can be authenticated and assigned an IP address despite some inconsistencies in the way clients present themselves and the way the Radius server expects them to be identified. Changes on the client or Radius side would have complicated the solution as neither side has visibility of the other, while the BNG has access to both flows. In this activity we will look further at the SR OS capabilities for inspecting and modifying Enhanced Subscriber Management (ESM) related traffic in-flight. |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/), [Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/get-started-md-cli-user.html), [Python programming language](https://www.python.org), [Python 3 API for SR OS](https://documentation.nokia.com/sr/25-3/tpsda-python-3-api/index.html)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: PE4, :material-account-circle-outline: sub1, sub2 and sub3, :material-radius-outline: Radius|
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html)<br/>[Triple Play Service Delivery Architecture (TPSDA) with Enhanced Subscriber Management (ESM)](https://documentation.nokia.com/sr/25-3/7750-sr/books/tpsda/triple-play-enhanced-subscriber-management.html)<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/system-management.html)<br/>[Radius Attributes](https://documentation.nokia.com/sr/25-3/7750-sr/titles/radius.html)<br/>[Python3 API for ESM](https://documentation.nokia.com/sr/25-3/tpsda-python-3-api/alc-sr-overview.html) |


The BNG node `PE4` in the Hackathon topology makes use of the on-board Python utilities to streamline DHCP and Radius flows to and from the client network and Radius server, respectively. These Python scripts make it so that all subscribers in the topology can be authenticated and assigned an IP address despite some inconsistencies in the way clients present themselves and the way the Radius server expects them to be identified. Changes on the client or Radius side would have complicated the solution as neither side has visibility of the other, while the BNG has access to both flows. In this activity we will look further at the SR OS capabilities for inspecting and modifying Enhanced Subscriber Management (ESM) related traffic in-flight.

The challenge to solve has to do with improvements on the logging and visualization of Radius Accounting traffic. This has lead them to request that subscriber identifier and DHCP options specified by the clients in the network be added to the Accounting traffic so they don't have to store and correlate data from the Authentication traffic with what is received via Accounting and what can be seen in the SR OS logs and traces.

## Objective

Fortunately, this is a request we can fulfill in SR OS using the same Python utilities that are already being used in the BNG today. Let's explore how we can go about implementing this through the following steps:

1. Find a way to inspect Radius Accounting traffic in the Hackathon topology so that we can see if our changes have any impact.
2. Using SR OS configuration statements, add the `subscriber-id` attribute to Radius Accounting Requests originated by the BNG `PE4`
3. Using `alc`, add DHCP Client Option information to Radius Accounting Requests.

Only :material-router: PE4 will be configured in this activity, there will be no need to rollback any configuration. There will be commands to be executed on the other nodes listed above however those changes are of an ephemeral nature.

## Technology explanation

In the following sections, we will briefly highlight each of the tools that will be used as well as mention what the references listed above may be used and needed for.

### TPSDA Guide

The Triple Play Service Delivery Architecture guide details amongst other things the implementation flow of subscriber management on the BNG, as well as the related Command Line Interface (CLI) syntax and command usage. The answers to most questions you might have around subscriber management can be found in this document. It talks about DHCP in all its variants, PPPoE sessions, NAT, different manners of associating hosts with authentication and accounting policies or adding more information to them without making changes on the client side, security, redundancy, quality of service, how and where to use Python along with many more topics.

To understand the general flow of the subscribers in this activity and to understand which elements may be having trouble, the following sequence happens when a subscriber comes online:

1. Client broadcasts a DHCP Discover message
2. BNG receives the DHCP Discover and sends a Radius Authentication Request to the Radius server.
3. Radius checks the data in the Access Request and sends back either Access-Accept or Access-Reject
4. BNG receives the Access-Accept and creates a subscriber context, an Access-Reject would be indicative of a problem.
5. The remaining exchange of DHCP Request, Offer and Acknowledgment is performed so the client gets an IP address.
6. Now, the client is "online".

### Python bindings for ESM

Although technically included in the previous section and since it plays a prominent role in this activity, the Python packages contained in SR OS that give access to various ESM objects including DHCPv4, DHCPv6 and Radius packets deserve an additional highlight. These packages are all available under the `alc` module that can be imported in Python scripts in SR OS. The general workflow for using the `alc` objects is as follows:

1. Create a `python-script` object in the configuration that points to your script file, via (T)FTP or locally on the router's flash card.
2. If the file was changed or not ready yet when the script was configured, make sure it is reloaded so the version in memory matches the file
3. Create a `python-policy` object that links ESM-related traffic like DHCP and Radius to the `python-script`. For each traffic and packet type, the direction is taken into account as an incoming DHCP Offer packet would be treated differently as an outgoing DHCP Offer packet.
4. Associate the `python-policy` with the appropriate service or subscriber-management objects in the configuration for it to take effect. While last year's activity required configuration on the level of a `capture-sap` and `group-interface`, the key association for this activity will be the Radius `server-policy`.

As this library is implemented specifically to be able to handle large amounts of packets in an efficient manner, there are no options to work with it interactively. As a result, debug tools are presented for them (and all other `python-script` objects) allowing some insight into what is happening. When combined with debug logs of Radius and DHCP traffic, in most cases a clear picture of what the library contributes can quickly be formed.

### Model-driven SR OS and the MD-CLI

As the term "model-driven" suggests, a model-driven Network Operating System (NOS) such as SR OS has one or more data models at its core. These data models compile together to provide the schema for the system. These data models are written using a language called YANG and, in the case of SR OS, are available [online](https://github.com/nokia/7x50_YangModels).

#### Configuration management

One of the advantages of model-driven SR OS is that the system becomes transactional in nature. Changes have to be explicitly applied from a candidate configuration to the running configuration via a `commit` operation rather than being immediately applied. This reduces the chances for operational issues to occur as a result of partial configuration changes. SR OS will atomically apply configuration changes to the system, this means that either all changes stored in the candidate configuration datastore will be successfully applied upon a `commit`, or none of them will be applied and your device will remain operationally intact.

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

The `/state` branch is accessible in either mode while configuration changes can only be made after switching to configuration mode. Whether that be for the `li`, `bof`, `configure` or `debug` contexts, an operator must first open a configuration session before being able to make any changes. The latter two are relevant to this activity.

There are four variants of configuration sessions; `read-only`, `private`, `global` and `exclusive`. The different options correspond to the level and type of candidate datastore that is created when the session is opened. More information on these modes is available in [the documentation](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/edit-configuration.html#unique_813655187).

#### Debugging
The `debug` context is another tree similar to the `configure` tree in model-driven SR OS. Any time you need to add debug statements you would open an exclusive configuration session for the `debug` tree and enter your changes followed by a `commit` statement to apply those changes. A pre-configured logging destination exists for you in the form of `log 21`. This log is set up to receive data from any active debug sources and to display it back to the CLI. To inspect the log you can use either `show log log-id 21` or use the command `tools perform log subscribe-to log-id 21` to subscribe to any events in your current terminal. This can be undone with `tools perform log unsubscribe-from log-id 21`.

To debug any Python scripts you may be adding during the activity or to see the scripts that are already present in action, you can use a oneliner that switches to classic CLI, adds the debug configuration and switches back immediately due to the leading `//`. The command given here would show any print statements or modifications made to packets done by the script, as well as any Python exceptions that are going uncaught and possibly leading to trouble.

`//debug python python-script <name> script-all-info`

Make sure you aren't in an exclusive configuration session on the `debug` context, as that would prevent the oneliner from working.

In this activity, all Radius traffic resides in the `Base` routing instance while all DHCP traffic exchanged between `PE4` and subscribers resides in routing instance `bng-vprn` with service ID `401`. In order to visualize the Radius and DHCP packets being exchanged, these variables will have to be taken into account.

### The Hackathon BNG environment

As this activity revolves entirely the BNG, let's briefly look at what is currently already in place on the BNG that is part of the Hackathon topology. Some details on the existing implementation are included in this section that may be useful later. In the Hackathon topology three subscribers exist who are aggregated and connected to the `PE4` BNG. On that BNG they reach a [`capture-sap`](https://documentation.nokia.com/sr/25-3/7750-sr/books/tpsda/subscriber-management.html#managed-sap-and-capture-sap) in VPLS 400, `bng-vpls`. Any time a DHCP packet reaches this SAP this leads to an attempted authentication of the subscriber based on information in the DHCP packet against the Radius server at `10.64.13.0`, reachable and configured in the `Base` routing instance of the BNG. If that authentication is successful, a managed SAP is created in a `group-interface` under a `subscriber-interface` in VPRN 401, `bng-vprn`. This is where the subscriber is instantiated.

Due to inconsistencies between the client and Radius configuration only two of the subscribers were online initially. Configuration and Python scripts have been written to align both sides of the interaction so that three subscribers are active and working in the current state of the topology. These modifications had to be configured in the VPLS, the VPRN and also applied to the Radius server configuration in the BNG.

In addition, to improve usability, further modifications were included in the BNG to assign subscriber identifiers that includes some information learned from the client side as well as some information learned from the Radius server. In the client case DHCP Option 61 is used and Radius attribute 25, Class, is used on the other side. Both are combined to form a subscriber ID on the BNG currently.

You are free to explore how this subscriber identifier customization is done, as well as how the third subscriber misalignment is resolved on the BNG. You may end up changing, replacing or building on top of some of the existing code that is already in place.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

All supporting files can be found in the `activities/nos/sros/activity-23` directory of the repository.

### Confirm the initial situation

Access `PE4` using SSH by connecting from your your group's hackathon VM to the hostname `clab-srexperts-pe4` or by connecting remotely to your group's hackathon VM on port 50024 as that is forwarded to `PE4` as well. Use the login credentials provided to you. Use `show service active-subscribers` on `PE4` to verify subscribers are online. Initially, three subscribers should exist in the system. Any issues with the pre-existing configuration or Python scripts would lead to two or less subscribers being available and this would form an issue for the activity, so make sure you **reach out for help if the expected three subscribers do not exist**. The subscribers are assigned subscriber identifiers by the system made up of a combination of their DHCP Circuit ID provided by the client and the Radius Class attribute provided by the Radius server.

/// details | Verify the initial state of subscribers in the system
/// tab | Command
```
show service active-subscribers
```
///
/// tab | Expected output
```
[/]
A:admin@g23-pe4# show service active-subscribers

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

When doing any development, we need to be able to verify the outcome of our changes. For the remainder of the exercise and before we get into further customization, lets make sure we can trigger DHCP and RADIUS interactions on-demand. We can remove sessions on BNG `PE4` forcibly, however this won't necessarily cause a renewal on the client side. For testing purposes, the easiest solution is simply triggering a renewal on the client side by flipping the relevant link down and up.

To do this, log in to any of the emulated client devices using SSH. They are available as `clab-srexperts-sub1`, `clab-srexperts-sub2` and `clab-srexperts-sub3` from your group's hackathon VM or, when SSHing into them from outside your group's hackathon VM, you may use port `50061`, `50062` and `50063` that are forwarded. Use the login credentials provided to you.

/// details | Logging in to a virtual subscriber
/// tab | From inside the Hackathon VM
```bash
ssh -l admin clab-srexperts-sub3
```
<div class="embed-result">
```{.text .no-select .no-copy}
Warning: Permanently added 'clab-srexperts-sub3' (ED25519) to the list of known hosts.

[*]─[sub3]─[~]
└──>
```
</div>
///
/// tab | From outside the Hackathon VM
```bash
ssh -l admin 23.srexperts.net -p 50063
```
<div class="embed-result">
```{.text .no-select .no-copy}
The authenticity of host '[23.srexperts.net]:50063 ([23.srexperts.net]:50063)' can't be established.
ED25519 key fingerprint is SHA256:OkKDNbCUoVhEP3Up6TSjpsB9skvBrpsvMobr025B4i8.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[23.srexperts.net]:50063' (ED25519) to the list of known hosts.
admin@23.srexperts.net's password: #PROVIDED#

[*]─[sub3]─[~]
└──>
```
</div>
///
///

Once logged in, run `sudo ifdown eth1.100; sudo ifup eth1.100` to force a new DHCP transaction. For convenience, you may want to wrap this action in a loop. This could be done as follows:

```bash
while :; do sudo ifdown eth1.100; sudo ifup eth1.100; sleep 15; done
```

You could also start the `crond` process on the emulated subscribers using `sudo crond`. A cron job will then begin to run every 5 minutes to renew the lease on interface `eth1.100`. For debugging purposes on the subscriber side, when going this route, you may prefer to use `sudo crond -l 1 -L /var/log/crond.log`.

/// details | Subscriber renewal as seen from client `sub1`
/// tab | Command
```bash
while :; do sudo ifdown eth1.100; sudo ifup eth1.100; sleep 15; done
```
///
/// tab | Expected output
```bash
bash# while :; do sudo ifdown eth1.100; sudo ifup eth1.100; sleep 15; done
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

Now that we are able to renew clients to test our setup at will, the next objective is being able to visualize Radius and DHCP logs so that we can evaluate behavior where necessary. This can be done in several ways, however the BNG `PE4` being the central part of the solution taking part in both the Radius and DHCP flows makes it particularly well suited.

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

Above, the different contexts and configuration modes have been highlighted. To add configuration to the debug context we will have to open an `exclusive` configuration session on it and add the required statements. Add configuration to the debug context to ensure that all Radius traffic from the Radius server with IP address `10.64.13.0` in the Base router is marked as debug information, as well as any DHCP traffic that passes through routing-instance `bng-vprn`.

/// details | Expected result
```
[ex:/debug]
A:admin@g23-pe4# info
    router "Base" {
        radius {
            servers {
                server-address 10.64.13.0 { }
            }
        }
    }
    router "bng-vprn" {
        dhcp {
            all-packets {
            }
        }
    }
```
///

If additional information from the Radius server is required, the server's logs can be viewed using

`docker exec -it  clab-srexperts-radius tail -f /var/log/radius/radius.log`

from your group's hackathon VM instance. As an example, consider that this file may include additional information from the Radius server about why it is declining certain requests.

### Add an attribute into Radius Accounting Requests using configuration

Attributes can be added or removed from Radius accounting updates using configuration, this is part of the `radius-accounting-policy` created in the `subscriber-mgmt` context. Use the previous task's debug configuration and what you have learned so far to confirm that every time there is a Radius Accounting-Request, it does not currently contain the subscriber's ID as an attribute.

As there is now a request to add this information to improve the ability to retrieve and correlate information from the different systems, we will do just that in this task. Use a `private` configuration candidate to include the `subscriber-id` attribute in Accounting Requests sent by `PE4`. Using the previous task's debug configuration and the other debugging tools in SR OS, verify your change had the expected result of adding a TLV to Accounting Requests. If needed, look into the Radius server logs for any additional information you may need.

///tip
To trigger an accounting request you can use one of the following methods:

 - Send any traffic from the subscriber to the BNG `loopbackPing` interface (`ping 192.168.211.1`), followed by forcing DHCP lease renewal of that subscriber.
 - Remove the subscriber session from the BNG (`/clear service id 401 ipoe session subscriber ...`)
///

/// details | Add `subscriber-id` to Radius accounting
/// tab | Commands
```
edit-config private
/configure subscriber-mgmt radius-accounting-policy "RadAcctPolicy1"
include-radius-attribute subscriber-id
commit
exit all
quit-config
```
///
/// tab | Expected Output (including debug)
```hl_lines="27 35"
[/]
A:admin@g23-pe4# edit-config private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(pr)[/]
A:admin@g23-pe4# /configure subscriber-mgmt radius-accounting-policy "RadAcctPolicy1"

(pr)[/configure subscriber-mgmt radius-accounting-policy "RadAcctPolicy1"]
A:admin@g23-pe4# include-radius-attribute subscriber-id

*(pr)[/configure subscriber-mgmt radius-accounting-policy "RadAcctPolicy1"]
A:admin@g23-pe4# commit

(pr)[/configure subscriber-mgmt radius-accounting-policy "RadAcctPolicy1"]
A:admin@g23-pe4# exit all

(pr)[/]
A:admin@g23-pe4# quit-config
INFO: CLI #2074: Exiting private configuration mode

[/]
A:admin@g23-pe4# tools perform log subscribe-to log-id 21
...
10387 2025/05/01 16:08:28.982 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Accounting-Request(4) 10.64.13.0:1813 id 22 len 187 vrid 1 pol RadPolicy1
    STATUS TYPE [40] 4 Start(1)
    NAS IP ADDRESS [4] 4 10.46.23.24
    CLASS [25] 2 0xcafe
    SESSION ID [44] 62 401@1/1/c3/1:100@session@00:d0:f6:01:01:01_2025/05/01 16:08:28
    MULTI SESSION ID [50] 57 0ff1ce0100cafe@1/1/c3/1:100@SLA_PROF1_2025/05/01 16:08:28
    EVENT TIMESTAMP [55] 4 1746115708
    VSA [26] 16 Nokia(6527)
      SUBSC ID STR [11] 14 0ff1ce0100cafe
...
```
///
///

### Add an attribute into Radius Accounting Requests using `alc`

Many reasons exist for wanting to add information to Radius Accounting Requests and those haven't always been considered as part of the built-in functionality in SR OS. In the previous task, adding a `subscriber-id` was possible via a configuration change. This is not the case here, where we need to include DHCPv4 options sent by the client towards the BNG in Radius Accounting messages for logging purposes.

In SR OS Radius authentication configuration, an option for adding the Radius VSA `Alc-ToServer-Dhcp-Options` to authentication packets is present. This same option does not exist for accounting configuration. By storing these options either when they are sent in Access Requests by the BNG or when they are received in DHCP messages from the client side, we will be able to retrieve them and add them to accounting requests as well.

To do this, we will use the cache associated with the `python-policy` to act as our storage, using a value that can uniquely identify each client to ensure there can be no mix-ups. In the example solution given below we will store options received in DHCP messages from the client side in the cache as a first step. Having achieved that, these cache entries are looked up and attached to accounting request messages any time they are sent by the system.

#### Caching DHCP Options

On your group's hackathon VM instance, under the location `/home/nokia/SReXperts/activities/nos/sros/activity-23/dhcp.py` you will find a file that was created previously that is currently ensuring that all three subscribers come up and that they receive human-readable subscriber IDs. We will modify this script to create additional cache entries for each client containing all DHCP options sent by the client, as we might see when enabling `dhcp-options` under the `radius-authentication-policy`. It's a good idea to use the existing code as a base, and expand upon it.

If you make any changes to the `dhcp.py` file, use `perform python python-script reload script "dhcp"` to load them into memory. You can always use a `show` command to view the script version currently loaded in memory by sending `/show python python-script "dhcp" source-in-use`. To inspect the Python cache, use the command `/tools dump python python-policy "python-policy" cache`.

Use the `alc` documentation for the `dhcpv4` object to get started and make sure your cache entries' lifetime is managed.

/// details | Curious what happens when `dhcp-options` is enabled for Radius authentication?
You can see the differences below:
```hl_lines="30-39"
Before:

21325 2025/05/01 17:12:41.376 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Access-Request(1) 10.64.13.0:1812 id 226 len 124 vrid 1 pol RadPolicy1
    USER NAME [1] 17 00:d0:f6:01:01:01
    PASSWORD [2] 16 vEeGfmYKBwLfmsPAQ/uLIE
    NAS IP ADDRESS [4] 4 10.46.23.24
    VSA [26] 10 DSL(3561)
      AGENT CIRCUIT ID [1] 8 0x04 0f f1 ce 01 02 ca fe
    NAS PORT TYPE [61] 4 Ethernet(15)
    NAS PORT ID [87] 12 1/1/c3/1:100
    VSA [26] 19 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:01:01:01

After:

21241 2025/05/01 17:12:14.067 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Access-Request(1) 10.64.13.0:1812 id 210 len 181 vrid 1 pol RadPolicy1
    USER NAME [1] 17 00:d0:f6:01:01:01
    PASSWORD [2] 16 30fvvWjMibFikJZk6Vaw7U
    NAS IP ADDRESS [4] 4 10.46.23.24
    VSA [26] 10 DSL(3561)
      AGENT CIRCUIT ID [1] 8 0x04 0f f1 ce 01 02 ca fe
    NAS PORT TYPE [61] 4 Ethernet(15)
    NAS PORT ID [87] 12 1/1/c3/1:100
    VSA [26] 76 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:01:01:01
      TO-SERVER DHCP OPTIONS [102] 55
        Message type [53] 1 discover
        Max msg size [57] 2 0x02 40
        Param request list [55] 7 0x01 03 06 0c 0f 1c 2a
        Host name [12] 4 0x73 75 62 31
        Class id [60] 12 0x75 64 68 63 70 20 31 2e 33 36 2e 31
        Client id [61] 4 0x0f f1 ce 01
        Relay agent information [82]
          AGENT CIRCUIT ID [1] 8 ▒▒▒▒
        End [255]
```
///

Confirm that your changes have the desired effect and watch out for any side-effects or edge cases that might impact subscribers. You can verify this by clearing the subscriber sessions and any and all cache entries from the BNG and triggering new sessions from the simulated subscribers as you've already seen. To clear the BNG from any remaining state, use
```
[/]
A:admin@g23-pe4# /clear python python-policy "python-policy" cache all

[/]
A:admin@g23-pe4# /clear service id 401 ipoe session all
```

All three subscribers should reappear in the system after this operation.

/// details | Modify DHCP script to cache options for Radius accounting
```python title="Modified version of script found under /home/nokia/SReXperts/activities/nos/sros/activity-23/dhcp.py"
from alc import dhcpv4
from alc import cache
from binascii import unhexlify

def dhcp4_discover():
  client_id = dhcpv4.get(61)[0]
  ue_mac = dhcpv4.chaddr[:6]
  with cache as cache_object:
    if cache_object.get(ue_mac):
        cache_object.set_lifetime(ue_mac, 600)
        if cache_object.get(ue_mac + b'\x81'):
            cache_object.set_lifetime(ue_mac + b'\x81', 600)
    else:
        if (client_fqdn := dhcpv4.get(81)):
          cache_object.set(ue_mac + b'\x81', client_fqdn[0][2:])
        cache_object.set(ue_mac, (bytes(chr(len(client_id)), 'utf-8') + client_id))
  with cache as cache_object:
    relayagent = [{1:[cache_object.get(ue_mac)]},]
  dhcpv4.set_relayagent(relayagent)
  store_options(ue_mac)


def dhcp4_request():
  ue_mac = dhcpv4.chaddr[:6]
  with cache as cache_object:
    cache_info = cache_object.get(ue_mac)

    dhcp_info_len = int(cache_info[0])
    dhcp_client_info = cache_info[1:1+dhcp_info_len]

    if (len(cache_info) > dhcp_info_len+1):
      class_len = int(cache_info[1+dhcp_info_len])
      class_info = cache_info[1+dhcp_info_len+1:1+dhcp_info_len+1+class_len]
    else:
      class_info = ""

    relayagent = [{1:[dhcp_client_info + "\x00" + class_info]},]
  dhcpv4.set_relayagent(relayagent)

def store_options(ue_mac):
  cache_entry = b''
  cache_key = ue_mac + "-toserv-options"
  for option in sorted(dhcpv4.getOptionList()):
    val = dhcpv4.get(option)[0]
    if len(val) > 0:
      cache_entry += unhexlify("%02x%02x" % (option, len(val))) + val
    else:
      cache_entry += unhexlify("%02x" % option) + val
  with cache as cache_object:
    cache_object.set(cache_key, cache_entry)
    cache_object.set_lifetime(cache_key, 14400)


if __name__ == "__main__":
  if ord(dhcpv4.get(53)[0]) == 1:
    # DISCOVER is attr 53 value 1
    dhcp4_discover()
  elif ord(dhcpv4.get(53)[0]) == 3:
    # REQUEST is attr 53 value 1
    dhcp4_request()
```
/// tab | Cache for UE MAC 00:d0:f6:01:01:01 - before
```
[/]
A:admin@g23-pe4# tools dump python python-policy "python-policy" cache

===============================================================================
Python policy cache "python-policy" entries
===============================================================================
Key       : (hex) 00 d0 f6 01 01 01
Value     : (hex) 04 0f f1 ce 01 02 ca fe
Time Left : 0d 00:09:58
DDP Key   : N/A
===============================================================================
```
///
/// tab | Cache for UE MAC 00:d0:f6:01:01:01 - after
```
[/]
A:admin@g23-pe4# tools dump python python-policy "python-policy" cache

===============================================================================
Python policy cache "python-policy" entries
===============================================================================
Key       : (hex) 00 d0 f6 01 01 01
Value     : (hex) 04 0f f1 ce 01 02 ca fe
Time Left : 0d 00:09:58
DDP Key   : N/A
-------------------------------------------------------------------------------
Key       : (hex) 00 d0 f6 01 01 01 2d 74 6f 73 65 72 76 2d 6f 70 74 69 6f 6e 73
Value     : (hex) 0c 04 73 75 62 31 35 01 01 37 07 01 03 06 0c 0f 1c 2a 39 02 02 40 3c 0c 75 64 68 63 70 20 31 2e 33 36 2e 31 3d 04 0f f1 ce 01 52 0a 01 08 04 0f f1 ce 01 02 ca fe ff
Time Left : 0d 00:09:57
DDP Key   : N/A
===============================================================================
```
///
///

If you're thinking of another attribute or value you would like to add here, try to add it and let us know!

#### Copying DHCP Options from cache to Radius Accounting Requests

The file `/home/nokia/SReXperts/activities/nos/sros/activity-23/radius-accounting-request.py` on your group's hackathon VM instance has been made available within your SR OS BNG `PE4`. Any modifications you make to the file in your group's hackathon VM will be visible to the router, this is the preferred method of development for this activity as it allows you to modify the file under the Linux filesystem while being able to test on the router. Additionally, you have access to two files created for you in advance that modify Access-Request and Access-Accept messages respectively. You can look at them online using the SR OS' `file show` or `/show python python-script <name> source-in-use` commands and from within your group's hackathon VM, as they are located in the `/home/nokia/SReXperts/clab/configs/sros/` folder.

For this step, you will have to modify the `python-policy` that is currently in use for your subscribers to apply the pre-provisioned Python script `radius-accounting-request` to Radius Accounting-Request packages headed towards the Radius server. The script doesn't do anything yet, that will be addressed later.

/// details | Add the radius-accounting-request `python-script` to the `python-policy`
/// tab | Commands
```
configure global
python {
    python-policy "python-policy" {
        radius accounting-request direction egress {
            script "radius-accounting-request"
        }
    }
}
compare /
commit
```
///
/// tab | Compare output
```
*[gl:/configure]
A:admin@g23-pe4# compare /
    configure {
        python {
            python-policy "python-policy" {
+               radius accounting-request direction egress {
+                   script "radius-accounting-request"
+               }
            }
        }
    }
```
///
///

Next up, you will modify the `radius-accounting-request.py` file so that it copies cached DHCP options into Radius Accounting Requests. Add your DHCP options to Radius Vendor-Specific Attribute (VSA) 26.6527.102, `Alc-ToServer-Dhcp-Options`. Check the [Radius reference guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/radius.html) for formatting details. Use the debugging and test methods shown above to verify your changes behave as expected.

///tip
The expected value to be set on VSA `26.6527.102` is a byte sequence of [TLVs](https://datatracker.ietf.org/doc/html/rfc6929#section-2.3), each one representing a DHCP option.
///

/// details | Side quest: where is the `python-policy` applied to the accounting traffic flow?
This configuration is done under the `server-policy`, the `radius-authentication-policy` and `radius-accounting-policy` in use by our subscribers rely on the same `radius-server-policy`.
///

When you make any changes to the `radius-accounting-request.py` file, use the `perform python python-script reload script radius-accounting-request` command on `PE4` to load them into memory.

You can always use a show command to view the script version currently loaded in memory by sending `/show python python-script "radius-accounting-request" source-in-use`.

To add this Python script output and it's results to the debug log, use `//debug python python-script radius-accounting-request script-all-info`.

To inspect the Python cache, use the command `/tools dump python python-policy "python-policy" cache`.

/// details | Add cached DHCP options to Radius accounting
/// tab | Example contents of radius-accounting-request.py
```python
from alc import radius
from alc import cache
import binascii

ALU = 6527

def radius_accounting_request():
  # get the MAC
  mac_hex = radius.attributes.getVSA(ALU,27)
  mac_hex = mac_hex.replace(b':', b'')
  ue_mac = binascii.unhexlify(mac_hex)
  with cache as cache_object:
    cache_info = cache_object.get(ue_mac + "-toserv-options")
    radius.attributes.setVSA(ALU, 102, cache_info)

if __name__ == "__main__":
  radius_accounting_request()
```
///
/// tab | Accounting Request - Before
```
  Accounting-Request(4) 10.64.13.0:1813 id 106 len 190 vrid 1 pol RadPolicy1
    STATUS TYPE [40] 4 Start(1)
    NAS IP ADDRESS [4] 4 10.46.23.24
    CLASS [25] 2 0xcafe
    SESSION ID [44] 62 401@1/1/c3/1:100@session@00:d0:f6:01:01:01_2025/05/02 11:52:51
    MULTI SESSION ID [50] 57 0ff1ce0100cafe@1/1/c3/1:100@SLA_PROF1_2025/05/02 11:52:51
    EVENT TIMESTAMP [55] 4 1746186771
    VSA [26] 19 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:01:01:01
```
///
/// tab | Accounting Request - After
```
223247 2025/05/02 11:46:01.523 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Accounting-Request(4) 10.64.13.0:1813 id 122 len 247 vrid 1 pol RadPolicy1
    STATUS TYPE [40] 4 Start(1)
    NAS IP ADDRESS [4] 4 10.46.23.24
    CLASS [25] 2 0xcafe
    SESSION ID [44] 62 401@1/1/c3/1:100@session@00:d0:f6:01:01:01_2025/05/02 11:46:01
    MULTI SESSION ID [50] 57 0ff1ce0100cafe@1/1/c3/1:100@SLA_PROF1_2025/05/02 11:46:01
    EVENT TIMESTAMP [55] 4 1746186361
    VSA [26] 76 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:01:01:01
      TO-SERVER DHCP OPTIONS [102] 55
        Host name [12] 4 0x73 75 62 31
        Message type [53] 1 discover
        Param request list [55] 7 0x01 03 06 0c 0f 1c 2a
        Max msg size [57] 2 0x02 40
        Class id [60] 12 0x75 64 68 63 70 20 31 2e 33 36 2e 31
        Client id [61] 4 0x0f f1 ce 01
        Relay agent information [82]
          AGENT CIRCUIT ID [1] 8 ▒▒▒▒
        End [255]
```
///
///

### Augment information provided in Accounting-Stop

One of the more common attributes in Accounting-Stop messages is option 49, also known as the Acct-Terminate-Cause. This attribute indicates how the session was terminated, and can
only be present in Accounting-Request records where the Acct-Status-Type is set to Stop (2). Visible under the SR OS command `/tools dump aaa radius-acct-terminate-cause`, there are many different reasons for an accounting session to be stopped. These different causes are mapped to the standardized 23 values, as shown in the table under the `TermCause` column.

For this last part of the activity, let's try to add information to the accounting messages that shows how often a given reason has been used for an Accounting Stop on this BNG. This would be usable in a monitoring solution that ingests Radius data. Further complexity could be added by adding that number for a specific subscriber or by looking at it only in a specific interval, the example solution does not implement this. As always, feel free to add your own ideas into the exercises and let us know, we would be excited to hear about them.

A specific `cache` entry can be created and maintained for each possible value acting as storage and every Accounting-Stop has this information added to it. Since there is no Radius attribute for this, we will commandeer the VSA `26.6527.16`, Alc-ANCP-Str, as it is not used elsewhere in this setup.

Since the `cache` is already enabled and the appropriate configuration for calling out to Python for each Accounting-Request is already present, the only changes that should be required will be in your Python code from the previous step.

/// details | Augmented Accounting-Stop
/// tab | Modified `radius-accounting-request.py`
```python
from alc import radius
from alc import cache
import binascii

ALU = 6527

CACHE_ENTRIES = [j.to_bytes(4, 'big') for j in range(1,24)]

def renew_cache_entries():
    with cache as cache_object:
      for entry in CACHE_ENTRIES:
        if not cache_object.get(entry):
          cache_object.set(entry, b'\x00')
        cache_object.set_lifetime(entry, 86400)

def radius_accounting_request():
  # get the MAC
  mac_hex = radius.attributes.getVSA(ALU,27)
  mac_hex = mac_hex.replace(b':', b'')
  ue_mac = binascii.unhexlify(mac_hex)
  with cache as cache_object:
    cache_info = cache_object.get(ue_mac + "-toserv-options")
    if cache_info is not None:
      radius.attributes.setVSA(ALU, 102, cache_info)

if __name__ == "__main__":
  radius_accounting_request()
  acctType = int(binascii.hexlify(radius.attributes.get(40)))
  renew_cache_entries()
  if acctType == 2:
    termCause = radius.attributes.get(49)
    with cache as cache_object:
      curCount = int(binascii.hexlify(cache_object.get(termCause)), 16)+1
      radius.attributes.setVSA(ALU, 16, bytes(str(curCount), 'ascii'))
      curCount_numBits = len(bin(curCount)[2:]) #'01...01'
      # formatted length should be 2 * (ceil of required # bits / 8) because unhexlify
      # takes an event length string so any time we go up over a multiple of 8, one hex char
      # will be added automatically and we have to pad a 0 to the front ourselves
      curCount = binascii.unhexlify("%0*x"%(int(-(curCount_numBits/8)//1 * -1)*2,curCount))
      cache_object.set(termCause, curCount)
```
///
/// tab | Output - before
```
240282 2025/05/02 13:12:47.102 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Accounting-Request(4) 10.64.13.0:1813 id 87 len 359 vrid 1 pol RadPolicy1
    STATUS TYPE [40] 4 Stop(2)
    NAS IP ADDRESS [4] 4 10.46.23.24
    CLASS [25] 2 0xcafe
    SESSION ID [44] 62 401@1/1/c3/1:100@session@00:d0:f6:01:01:01_2025/05/02 13:12:40
    SESSION TIME [46] 4 7
    TERMINATE CAUSE [49] 4 User Request(1)
    MULTI SESSION ID [50] 57 0ff1ce0100cafe@1/1/c3/1:100@SLA_PROF1_2025/05/02 13:12:40
    EVENT TIMESTAMP [55] 4 1746191567
    VSA [26] 176 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:01:01:01
      INPUT_INPROF_OCTETS_64 [19] 10 0x00010000000000000000
      INPUT_OUTPROF_OCTETS_64 [20] 10 0x00010000000000000000
      INPUT_INPROF_PACKETS_64 [23] 10 0x00010000000000000000
      INPUT_OUTPROF_PACKETS_64 [24] 10 0x00010000000000000000
      OUTPUT_INPROF_OCTETS_64 [21] 10 0x00010000000000000000
      OUTPUT_OUTPROF_OCTETS_64 [22] 10 0x00010000000000000000
      OUTPUT_INPROF_PACKETS_64 [25] 10 0x00010000000000000000
      OUTPUT_OUTPROF_PACKETS_64 [26] 10 0x00010000000000000000
      TO-SERVER DHCP OPTIONS [102] 55
        Host name [12] 4 0x73 75 62 31
        Message type [53] 1 discover
        Param request list [55] 7 0x01 03 06 0c 0f 1c 2a
        Max msg size [57] 2 0x02 40
        Class id [60] 12 0x75 64 68 63 70 20 31 2e 33 36 2e 31
        Client id [61] 4 0x0f f1 ce 01
        Relay agent information [82]
          AGENT CIRCUIT ID [1] 8 ▒▒▒▒
        End [255]
```
///
/// tab | Output - after
```
[/]
A:admin@g23-pe4# /tools dump python python-policy "python-policy" cache

===============================================================================
Python policy cache "python-policy" entries
===============================================================================
Key       : (hex) 00 00 00 01
Value     : (hex) 09
Time Left : 0d 23:59:58
DDP Key   : N/A
-------------------------------------------------------------------------------
Key       : (hex) 00 00 00 02
Value     : (hex) 00
Time Left : 0d 23:59:58
DDP Key   : N/A
-------------------------------------------------------------------------------
Key       : (hex) 00 00 00 03
Value     : (hex) 00
Time Left : 0d 23:59:58
DDP Key   : N/A
-------------------------------------------------------------------------------

...

240257 2025/05/02 13:12:40.432 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Accounting-Request(4) 10.64.13.0:1813 id 83 len 359 vrid 1 pol RadPolicy1
    STATUS TYPE [40] 4 Stop(2)
    NAS IP ADDRESS [4] 4 10.46.23.24
    CLASS [25] 2 0xcafe
    SESSION ID [44] 62 401@1/1/c3/1:100@session@00:d0:f6:01:01:01_2025/05/02 13:12:33
    SESSION TIME [46] 4 7
    TERMINATE CAUSE [49] 4 User Request(1)
    MULTI SESSION ID [50] 57 0ff1ce0100cafe@1/1/c3/1:100@SLA_PROF1_2025/05/02 13:12:33
    EVENT TIMESTAMP [55] 4 1746191560
    VSA [26] 176 Nokia(6527)
      CHADDR [27] 17 00:d0:f6:01:01:01
      INPUT_INPROF_OCTETS_64 [19] 10 0x00010000000000000000
      INPUT_OUTPROF_OCTETS_64 [20] 10 0x00010000000000000000
      INPUT_INPROF_PACKETS_64 [23] 10 0x00010000000000000000
      INPUT_OUTPROF_PACKETS_64 [24] 10 0x00010000000000000000
      OUTPUT_INPROF_OCTETS_64 [21] 10 0x00010000000000000000
      OUTPUT_OUTPROF_OCTETS_64 [22] 10 0x00010000000000000000
      OUTPUT_INPROF_PACKETS_64 [25] 10 0x00010000000000000000
      OUTPUT_OUTPROF_PACKETS_64 [26] 10 0x00010000000000000000
      ANCP STR [16] 1 9
      TO-SERVER DHCP OPTIONS [102] 55
        Host name [12] 4 0x73 75 62 31
        Message type [53] 1 discover
        Param request list [55] 7 0x01 03 06 0c 0f 1c 2a
        Max msg size [57] 2 0x02 40
        Class id [60] 12 0x75 64 68 63 70 20 31 2e 33 36 2e 31
        Client id [61] 4 0x0f f1 ce 01
        Relay agent information [82]
          AGENT CIRCUIT ID [1] 8 ▒▒▒▒
        End [255]
```
///
///

## Summary and review

Congratulations!  If you have got this far you have completed this activity and achieved the following:

- You have learned how an IPoE session is set up in an SR OS, and probably set up a few yourself
- You have written or modified one or more applications using the Python 3 programming language
- You have used the model-driven CLI for changing configuration and debugging Enhanced Subscriber Management (ESM) behavior
- You have added attributes that would otherwise not be present in Radius Accounting Messages using your own Python code
- You have adapted the provided Hackathon VM into a development environment to your liking
- You have created and tested solutions using a combination of SR OS and Linux

This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity, or try to expand upon this one if you have some more ideas.
