---
tags:
  - SR Linux
  - Troubleshooting
  - CLI
---

# SR Linux troubleshooting


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | SR Linux fundamentals through a troubleshooting scenario                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Activity ID**           | 20                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Short Description**       | Troubleshoot operational issues using SR Linux workflows to resolve a routing issue, and validate end-to-end network behavior while applying best operational practices.                                                                                                                                                                                                                                                                                                                                                     |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **Tools used**              | [Configuration management](https://documentation.nokia.com/srlinux/25-10/books/config-basics/configuration-management.html#configuration-checkpoints)<br/>[SR Linux interactive traffic monitoring tool](https://documentation.nokia.com/srlinux/25-10/books/troubleshooting-toolkit/interactive-traffic-monitor-tool-troubleshooting-toolkit.html)<br/>                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: leaf21, :material-router: leaf22, :material-router: leaf23, :material-router: spine21, :material-router: spine22, :material-router: pe1, :material-router: pe4                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **References**              | [Nokia SR Linux](https://documentation.nokia.com/srlinux/26-3/index.html)<br/> [Learn SR Linux](https://learn.srlinux.dev/)<br/> |


You are a Network Engineer starting your shift in a modern data center running SR Linux. During the handover, you are informed that traffic from the data center to the DNS server at IP address 1.1.1.1 has stopped working.

Your task is to investigate the issue, identify the root cause, and restore connectivity. While troubleshooting, you should validate the current network state, analyze routing behavior, and apply SR Linux best practices to implement a robust and efficient solution.

## Main objectives of the activity

The main objectives of this activity are to investigate and restore connectivity in a SR Linux data center fabric while strengthening operational troubleshooting skills:

1. Diagnose and resolve the network issue preventing access to the DNS server (1.1.1.1)
2. Validate the network state
3. Apply SR Linux best practices for safe configuration changes, including checkpoints and rollback mechanisms



## Technology explanation

All tools and configurations in this activity are executed on Leaf and Spine devices, specifically Nokia 7220 [IXR](https://www.nokia.com/data-center-networks/data-center-fabric/7220-interconnect-router/) platforms. These devices run the Nokia SR Linux operating system, which is the focus of this activity.

This activity assumes the following knowledge:

- Navigating the SR Linux CLI interface
- Applying configurations using the model-driven approach
- Customizing your environment with CLI aliases
- Managing configuration safety through checkpoints and rollback

If you feel confident, let’s get started. If not, we recommend completing the **Introduction to the SR Linux YANG CLI** hackathon activity first. By the end, you will have a solid foundation for operating Nokia SR Linux nodes, which is essential for successfully completing this activity.


## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

**It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.**

### Configuration checkpoint
/// admonition | Warning
    type: warning
**This step is extremely important and will be crucial to the success of the activity**.
///

Run the configuration checkpoint command on the **leaf** and **spine** devices before executing any other command.

This will create a checkpoint that you'll use in the final step of this activity to perform a configuration rollback.

After creating the checkpoint, run the info from state command to view the list of available checkpoints. You should see your newly created checkpoint listed with ID 0, indicating that it is the most recent one.


/// details | Solution: Checkpoint saving
    type: solution 

/// tab | Before running Checkpoint

``` bash
A:admin@g2-spine21# info from state system configuration checkpoint * | as table
+-----+-------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------+-------------------------------------------------+------------------+
| Id  |                                                 Name                                                  |                                                Comment                                                |                     Created                     |     Username     |
+=====+=======================================================================================================+=======================================================================================================+=================================================+==================+
|   0 | clab-initial                                                                                          | set by containerlab                                                                                   | 2026-02-23T10:47:54.296Z (28 days ago)          | srlinux          |
+-----+-------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------+-------------------------------------------------+------------------+

```

///

/// tab | Running Checkpoint

``` bash
A:admin@g2-spine21# save checkpoint name before_srl_tshoot_activity_20 comment "this is a checkpoint before starting activity 20"
/system:
    Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'before_srl_tshoot_activity_20' and comment 'this is a checkpoint before starting activity 20'

```
///

/// tab | After running Checkpoint

``` bash
A:admin@g2-spine21# info from state system configuration checkpoint * | as table
+-----+-------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------+-------------------------------------------------+------------------+
| Id  |                                                 Name                                                  |                                                Comment                                                |                     Created                     |     Username     |
+=====+=======================================================================================================+=======================================================================================================+=================================================+==================+
|   0 | before_srl_tshoot_activity_20                                                                         | this is a checkpoint before starting activity 20                                                      | 2026-03-24T09:44:38.520Z (7 seconds ago)        | srlinux          |
|   1 | clab-initial                                                                                          | set by containerlab                                                                                   | 2026-02-23T10:47:54.296Z (28 days ago)          | srlinux          |
+-----+-------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------------------------------+-------------------------------------------------+------------------+

```

///
///

### Check the current network state

During this activity, the default network-instance will be used to reach the DNS server (`1.1.1.1`). This IP-VRF is used by the leaf and spine nodes to communicate within the underlay network and to forward external traffic.

/// admonition
    type: tip
You may want to obtain the following outputs:

1. Which interfaces are operating within the default network instance
2. Which BGP neighbors are established within the fabric
3. The routing table for the default network instance
4. The routes exchanged and exported across the data-center
///

Reviewing this information will give you clear visibility into the current network state and help you identify why, and where, connectivity to the DNS server (1.1.1.1) may be failing.

/// details | Solution: Checking the current state (use only if you get stuck)
    type: solution 

Note: The IP addresses of the BGP neighbors in your environment may differ from those shown in the solution.

/// tab | Interfaces 

``` bash

A:admin@g2-leaf21# show network-instance default interfaces | as table
+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+----------------------------+
|        Net instance        |         Interface          |            Type            |         Oper state         |          GBP Tags          |      Oper down reason      |           Ip mtu           |
+============================+============================+============================+============================+============================+============================+============================+
| default                    | ethernet-1/31.0            | routed                     | up                         |                            |                            | 9198                       |
| default                    | ethernet-1/32.0            | routed                     | up                         |                            |                            | 9198                       |
| default                    | irb0.1                     |                            | up                         |                            |                            | 9000                       |
| default                    | system0.0                  |                            | up                         |                            |                            |                            |

(truncated)

A:admin@g2-spine21# show network-instance default interfaces | as table
+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+
|           Net instance            |             Interface             |               Type                |            Oper state             |             GBP Tags              |         Oper down reason          |              Ip mtu               |
+===================================+===================================+===================================+===================================+===================================+===================================+===================================+
| default                           | ethernet-1/1.0                    | routed                            | up                                |                                   |                                   | 9198                              |
| default                           | ethernet-1/2.0                    | routed                            | up                                |                                   |                                   | 9198                              |
| default                           | ethernet-1/3.0                    | routed                            | up                                |                                   |                                   | 9198                              |
| default                           | ethernet-1/31.0                   | routed                            | up                                |                                   |                                   | 9198                              |
| default                           | ethernet-1/32.0                   | routed                            | up                                |                                   |                                   | 9198                              |
| default                           | system0.0                         |                                   | up                                |                                   |                                   |                                   |
+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+-----------------------------------+
(truncated)

```
///

/// tab | BGP Neighbors

``` bash
A:admin@g2-leaf21# show network-instance default protocols bgp neighbor
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP neighbor summary for network-instance "default"
Flags: S static, D dynamic, L discovered by LLDP, B BFD enabled, - disabled, * slow
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+----------------------+--------------------------------+----------------------+--------+------------+------------------+------------------+----------------+--------------------------------+
|       Net-Inst       |              Peer              |        Group         | Flags  |  Peer-AS   |      State       |      Uptime      |    AFI/SAFI    |         [Rx/Active/Tx]         |
+======================+================================+======================+========+============+==================+==================+================+================================+
| default              | fd00:fde8::2:13                | iBGP-DC              | S      | 65000      | established      | 7d:23h:35m:21s   | evpn           | [62/62/23]                     |
| default              | fe80::1856:25ff:feff:1%etherne | spine                | D      | 4200002000 | established      | 7d:23h:35m:29s   | ipv4-unicast   | [14/14/2]                      |
|                      | t-1/32.0                       |                      |        |            |                  |                  | ipv6-unicast   | [13/13/2]                      |
| default              | fe80::1882:24ff:feff:1%etherne | spine                | D      | 4200002000 | established      | 7d:23h:34m:54s   | ipv4-unicast   | [14/14/2]                      |
|                      | t-1/31.0                       |                      |        |            |                  |                  | ipv6-unicast   | [13/13/2]                      |
+----------------------+--------------------------------+----------------------+--------+------------+------------------+------------------+----------------+--------------------------------+
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Summary:
1 configured neighbors, 1 configured sessions are established, 0 disabled peers
2 dynamic peers


A:admin@g2-spine21# show network-instance default protocols bgp neighbor
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
BGP neighbor summary for network-instance "default"
Flags: S static, D dynamic, L discovered by LLDP, B BFD enabled, - disabled, * slow
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+---------------------------+---------------------------------------+---------------------------+---------+--------------+----------------------+----------------------+-------------------+---------------------------------------+
|         Net-Inst          |                 Peer                  |           Group           |  Flags  |   Peer-AS    |        State         |        Uptime        |     AFI/SAFI      |            [Rx/Active/Tx]             |
+===========================+=======================================+===========================+=========+==============+======================+======================+===================+=======================================+
| default                   | fe80::183a:12ff:feff:1f%ethernet-     | leaf                      | D       | 4200002001   | established          | 28d:23h:22m:51s      | ipv4-unicast      | [2/2/14]                              |
|                           | 1/1.0                                 |                           |         |              |                      |                      | ipv6-unicast      | [2/2/12]                              |
| default                   | fe80::1879:14ff:feff:1f%ethernet-     | leaf                      | D       | 4200002003   | established          | 28d:23h:22m:48s      | ipv4-unicast      | [2/2/15]                              |
|                           | 1/3.0                                 |                           |         |              |                      |                      | ipv6-unicast      | [2/2/13]                              |
| default                   | fe80::18e1:13ff:feff:1f%ethernet-     | leaf                      | D       | 4200002002   | established          | 28d:23h:22m:52s      | ipv4-unicast      | [2/2/15]                              |
|                           | 1/2.0                                 |                           |         |              |                      |                      | ipv6-unicast      | [2/2/13]                              |
| default                   | fe80::1e35:18ff:fe00:0%ethernet-      | pe                        | D       | 65000        | established          | 28d:23h:22m:52s      | ipv4-unicast      | [12/11/5]                             |
|                           | 1/31.0                                |                           |         |              |                      |                      | ipv6-unicast      | [8/7/7]                               |
| default                   | fe80::1ec3:1bff:fe00:0%ethernet-      | pe                        | D       | 65000        | established          | 28d:23h:22m:46s      | ipv4-unicast      | [12/11/16]                            |
|                           | 1/32.0                                |                           |         |              |                      |                      | ipv6-unicast      | [8/7/14]                              |
+---------------------------+---------------------------------------+---------------------------+---------+--------------+----------------------+----------------------+-------------------+---------------------------------------+
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Summary:
0 configured neighbors, 0 configured sessions are established, 0 disabled peers
5 dynamic peers

```
///

/// tab | IPv4 Routing Table 

``` bash
A:admin@g2-spine21# show network-instance default ipv4 route
============================================================================================================================================================================================================================================================================
IPv4-unicast route table for default network-instance
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Flags: > (best), * (unviable), ! (failed)
     : L (leaked route from another network-instance)
     : B (backup NHG active and displayed)
     : S (statistics supported)
     : D (dynamic LB), R (resilient LB)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Prefix               Route Type   Metric   Pref    Flags    Next-Hop(s)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
10.46.0.0/16         bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.46.2.43/32        bgp          0        170     >        fe80::180c:13ff:feff:1f(ethernet-1/1.0)
10.46.2.44/32        bgp          0        170     >        fe80::188a:14ff:feff:1f(ethernet-1/2.0)
10.46.2.45/32        bgp          0        170     >        fe80::1815:15ff:feff:1f(ethernet-1/3.0)
10.64.11.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.12.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.13.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.13.128/25      bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.21.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.22.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.23.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.24.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.30.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
10.64.40.0/24        bgp          0        170     >        fe80::180c:13ff:feff:1f(ethernet-1/1.0)
                                                            fe80::188a:14ff:feff:1f(ethernet-1/2.0)
                                                            fe80::1815:15ff:feff:1f(ethernet-1/3.0)
10.64.51.0/24        bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)

```
///

/// tab | BGP Route Advertisement

``` bash

A:admin@g2-leaf21# show network-instance default protocols bgp neighbor fe80::1882:24ff:feff:1%ethernet-1/31.0 advertised-routes ipv4
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Peer        : fe80::1882:24ff:feff:1%ethernet-1/31.0, remote AS: 4200002000, local AS: 4200002001
Type        : dynamic
Description : None
Group       : spine
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Origin codes: i=IGP, e=EGP, ?=incomplete
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|               Network                           Path-id                 Next Hop               MED                                 LocPref                               AsPath             Origin      |
+=========================================================================================================================================================================================================+
| 10.46.2.43/32                          0                            fe80::180c:13ff:f           -                                                                   [4200002001]               i        |
|                                                                     eff:1f                                                                                                                              |
| 10.64.40.0/24                          0                            fe80::180c:13ff:f           -                                                                   [4200002001]               i        |
|                                                                     eff:1f                                                                                                                              |
+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
2 advertised BGP routes
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

A:admin@g2-spine21# show network-instance default protocols bgp neighbor fe80::183a:12ff:feff:1f%ethernet-1/1.0 advertised-routes ipv4
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Peer        : fe80::183a:12ff:feff:1f%ethernet-1/1.0, remote AS: 4200002001, local AS: 4200002000
Type        : dynamic
Description : None
Group       : leaf
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Origin codes: i=IGP, e=EGP, ?=incomplete
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                    Network                                   Path-id                       Next Hop                   MED                                           LocPref                                         AsPath                 Origin        |
+==========================================================================================================================================================================================================================================================+
| 10.46.0.0/16                                    0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.46.2.41/32                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000]                      i          |
| 10.46.2.44/32                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000,                      i          |
|                                                                                                                                                                                                             4200002002]                                  |
| 10.46.2.45/32                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000,                      i          |
|                                                                                                                                                                                                             4200002003]                                  |
| 10.64.11.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.64.12.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.64.13.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.64.13.128/25                                 0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.64.21.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.64.22.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.64.23.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.64.24.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
| 10.64.30.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000,               i          |
|                                                                                                                                                                                                             4200001000,                                  |
|                                                                                                                                                                                                             4200001002]                                  |
| 10.64.51.0/24                                   0                                   fe80::18b2:23ff:feff:1             -                                                                                    [4200002000, 65000]               i          |
+----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
14 advertised BGP routes
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```
///
///


From the outputs, you should be able to validate the network topology of your data-center. Specifically that:

- Each spine is connected to the three leaf devices on ports `ethernet-1/1`, `ethernet-1/2`, and `ethernet-1/3`.
- Each spine is also connected to the PE routers on ports `ethernet-1/31` and `ethernet-1/32`.
- Each leaf is configured with a unique BGP autonomous system number (ASN), while all spines share a single ASN and all PE routers share a single ASN. This configuration follows best practices in a CLOS data-center network.

This connectivity and ASN configuration should be confirmed by your BGP neighbors output.  Is it?

### Alias to improve CLI usability (optional)

**Note: These CLI aliases are optional and intended only to simplify command execution if the user prefers a more convenient workflow.**

In multi-vendor environments, network operators often deal with different CLI syntax between platforms. Even within Nokia operating systems like SR OS and SR Linux, due to syntax changes, similar operations can use different commands.

For example:  
    - In SR OS, you enter configuration mode with: ```configure```  
    - In SR Linux, the equivalent command is: ```enter candidate```  

To make your workflow and troubleshooting task more efficient and consistent, you may want to define the following CLI aliases:

1. Create an alias `configure` that enters the candidate configuration mode
2. Create an alias (with a short name) to display BGP neighbors in the default network-instance
3. Create an alias (with a short name) to display advertised BGP routes for a specific neighbor
4. Create an alias to inspect configuration in a given context
5. Create an alias to show the default routing table


/// details | Alias
    type: example 

/// tab | configure

``` bash
environment alias "configure" "enter candidate"
```
///
/// tab | show bgp neighbors

``` bash
environment alias "show my neighbors" "show network-instance default protocols bgp neighbor"
```
///
/// tab | show bgp adve

``` bash
environment alias "show bgp {neighbor} advertisements" "show network-instance default protocols bgp neighbor {neighbor} advertised-routes ipv4"
```
///
/// tab | admin display-config

``` bash
environment alias "admin display-config {context}" "info from running {context}"
```
///
/// tab | show default routing table

``` bash
environment alias "show default route-table" "show network-instance default ipv4 route"
```
///

///


Use the command ```environment show``` to verify the aliases you just created.
Test each alias to make sure it works as expected.

If you would like, you can explore CLI aliasing further and create any additional customized commands that improve your workflow.

/// details | Output: Verification
    type: example 


``` bash
A:admin@g2-spine21# environment show
[alias]
"show default route-table" = "show network-instance default ipv4 route"
configure = "enter candidate"
"show my neighbors" = "show network-instance default protocols bgp neighbor"
"show bgp {neighbor} advertisements" = "show network-instance default protocols bgp neighbor {neighbor} advertised-routes ipv4"
"admin display-config {context}" = "info from running {context}"
..........
(truncated)
```
///

Lastly save the environment alias for future sessions. For that run the command 

/// details | Output: CLI Alias Save
    type: example 

/// tab | save environment

``` bash

A:admin@g2-spine21# environment save home
Saved configuration to /home/admin/.srlinuxrc

```
///
///

/// admonition 
    type: warning 
Alternatively, if you want the aliases to persist in the configuration, you can define them by entering candidate mode and running: ```system cli environment alias "alias-name" "actual sr-linux command"```. Then commit the changes to make them permanent.
///

### Investigate your network issue
Now that you understand the current network state, you should be able to determine why traffic from the data center is not reaching the DNS server at 1.1.1.1.

The next step is to think about how to restore connectivity. There are multiple possible solutions, so choose the one that best fits what you observe in the network.


/// admonition
    type: tip
Consider that the DNS server is not reachable via ICMP. To properly validate that your network is forwarding traffic in the correct direction, it is recommended to configure a loopback interface on :material-router: pe1 or :material-router: pe4 using the IP address 1.1.1.1. This allows you to test and confirm that your solution is working as expected, ensuring that your leaf and spine switches are forwarding DNS requests to the PE layer of your DC.
///

/// details | Recomendation: Loopback configuration
    type: solution 
/// tab | Loopback configuration (repeat in both :material-router: pe1 and :material-router: pe4)

``` bash
A:admin@g2-pe1# edit-config global
INFO: CLI #2054: Entering global configuration mode
INFO: CLI #2075: Other global configuration sessions are active

2026-03-25T15:13:51.89+00:00
(gl)[/]
A:admin@g2-pe1# /configure router "Base" interface "loopback_test" admin-state enable loopback ipv4 primary address 1.1.1.1 prefix-length 32

2026-03-25T15:14:34.45+00:00
*(gl)[/]
A:admin@g2-pe1# compare
    configure {
        router "Base" {
+           interface "loopback_test" {
+               admin-state enable
+               loopback
+               ipv4 {
+                   primary {
+                       address 1.1.1.1
+                       prefix-length 32
+                   }
+               }
+           }
        }
    }

2026-03-25T15:14:36.89+00:00
*(gl)[/]
A:admin@g2-pe1# commit

2026-03-25T15:14:39.38+00:00
(gl)[/]
A:admin@g2-pe1#

```
///

///

Even after configuring it, you will see, just as reported at the beginning of your shift, that there is still no connectivity.

/// details | Output: Try to ping 1.1.1.1
    type: example 
``` bash
A:admin@g2-leaf21# ping network-instance default 1.1.1.1 -c 5
Using network instance default
PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.

--- 1.1.1.1 ping statistics ---
5 packets transmitted, 0 received, 100% packet loss, time 4130ms

```
///

The `ping` is not working. Now ask yourself: **what is preventing connectivity to the destination?**

Think about what needs to be in place for end-to-end reachability and compare it with the current network state.

### One possible solution to resolve your network issue
**Note: This is just one possible solution; review it only if you are stuck.**

/// details | Some steps to guide you
    type: solution 

1. Configure a default route (0.0.0.0/0) on spine-21, using the system IPs of :material-router: pe1 and :material-router: pe4 as next hops
2. Ensure the route is installed and properly advertised to the leaf switches via BGP
3. Verify that the ping to the destination is now successful

///

/// details | If needed, the commands for this solution are shown below.
    type: solution 

Retrieve :material-router: pe1 and :material-router: pe4 system IP addresses.

``` bash

A:admin@g2-pe1# show router interface "system"

===============================================================================
Interface Table (Router: Base)
===============================================================================
Interface-Name                   Adm       Opr(v4/v6)  Mode    Port/SapId
   IP-Address                                                  PfxState
-------------------------------------------------------------------------------
system                           Up        Up/Up       Network system
   10.46.2.21/32                                               n/a
   fd00:fde8::2:21/128                                         PREFERRED
-------------------------------------------------------------------------------
Interfaces : 1
===============================================================================

A:admin@g2-pe4# show router interface "system"

===============================================================================
Interface Table (Router: Base)
===============================================================================
Interface-Name                   Adm       Opr(v4/v6)  Mode    Port/SapId
   IP-Address                                                  PfxState
-------------------------------------------------------------------------------
system                           Up        Up/Up       Network system
   10.46.2.24/32                                               n/a
   fd00:fde8::2:24/128                                         PREFERRED
-------------------------------------------------------------------------------
Interfaces : 1
===============================================================================

```
Ensure you can reach :material-router: pe1 and :material-router: pe4 system IP addresses.

``` bash
A:admin@g2-spine21# show default route-table
============================================================================================================================================================================================================================================================================
IPv4-unicast route table for default network-instance
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Flags: > (best), * (unviable), ! (failed)
     : L (leaked route from another network-instance)
     : B (backup NHG active and displayed)
     : S (statistics supported)
     : D (dynamic LB), R (resilient LB)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Prefix               Route Type   Metric   Pref    Flags    Next-Hop(s)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
10.46.0.0/16         bgp          0        170     >        fe80::1ea0:19ff:fe00:0(ethernet-1/31.0)
                                                            fe80::1e19:1cff:fe00:0(ethernet-1/32.0)
(truncated)

A:admin@g2-spine21# ping network-instance default 10.46.2.21 -c 5
Using network instance default
PING 10.46.2.21 (10.46.2.21) 56(84) bytes of data.
64 bytes from 10.46.2.21: icmp_seq=1 ttl=64 time=16.4 ms
64 bytes from 10.46.2.21: icmp_seq=2 ttl=64 time=4.21 ms
64 bytes from 10.46.2.21: icmp_seq=3 ttl=64 time=4.90 ms
64 bytes from 10.46.2.21: icmp_seq=4 ttl=64 time=8.20 ms
64 bytes from 10.46.2.21: icmp_seq=5 ttl=64 time=4.98 ms

--- 10.46.2.21 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4005ms
rtt min/avg/max/mdev = 4.210/7.734/16.385/4.541 ms


A:admin@g2-spine21# ping network-instance default 10.46.2.24 -c 5
Using network instance default
PING 10.46.2.24 (10.46.2.24) 56(84) bytes of data.
64 bytes from 10.46.2.24: icmp_seq=1 ttl=64 time=6.48 ms
64 bytes from 10.46.2.24: icmp_seq=2 ttl=64 time=3.91 ms
64 bytes from 10.46.2.24: icmp_seq=3 ttl=64 time=5.93 ms
64 bytes from 10.46.2.24: icmp_seq=4 ttl=64 time=4.01 ms
64 bytes from 10.46.2.24: icmp_seq=5 ttl=64 time=4.37 ms

--- 10.46.2.24 ping statistics ---
5 packets transmitted, 5 received, 0% packet loss, time 4006ms
rtt min/avg/max/mdev = 3.905/4.937/6.482/1.059 ms

```

Configure the default route under networ-instance default with next-hop in the :material-router: pe1 and :material-router: pe4 system IP's.

``` bash
set / network-instance default next-hop-groups group towards_pe_system admin-state enable
set / network-instance default next-hop-groups group towards_pe_system nexthop 1 ip-address 10.46.2.21
set / network-instance default next-hop-groups group towards_pe_system nexthop 1 resolve true
set / network-instance default next-hop-groups group towards_pe_system nexthop 2 ip-address 10.46.2.24
set / network-instance default next-hop-groups group towards_pe_system nexthop 2 resolve true
set / network-instance default static-routes route 0.0.0.0/0 next-hop-group towards_pe_system

```

Verify that the default route is correctly installed in the routing table.

``` bash
A:admin@g2-spine21# show default route-table
============================================================================================================================================================================================================================================================================
IPv4-unicast route table for default network-instance
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Flags: > (best), * (unviable), ! (failed)
     : L (leaked route from another network-instance)
     : B (backup NHG active and displayed)
     : S (statistics supported)
     : D (dynamic LB), R (resilient LB)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Prefix               Route Type   Metric   Pref    Flags    Next-Hop(s)
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
0.0.0.0/0            static       1        5       >        10.46.2.21(route:bgp)
                                                            10.46.2.24(route:bgp)
(truncated)

```

Now export the default route to the leaf switches to ensure it is available across all the leaf-spine topology.

``` bash
set / routing-policy prefix-set export_my_route prefix 0.0.0.0/0 mask-length-range 0..0
set / routing-policy policy modified_local statement loopback match protocol local
set / routing-policy policy modified_local statement loopback action policy-result accept
set / routing-policy policy modified_local statement export_static_route match prefix prefix-set export_my_route
set / routing-policy policy modified_local statement export_static_route action policy-result accept
set / network-instance default protocols bgp group leaf export-policy [ modified_local ]
```

Confirm that the default route has been successfully exported to the leafs and is installed in their routing tables.

``` bash
A:admin@g2-spine21# show bgp fe80::183a:12ff:feff:1f%ethernet-1/1.0 advertisements
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Peer        : fe80::183a:12ff:feff:1f%ethernet-1/1.0, remote AS: 4200002001, local AS: 4200002000
Type        : dynamic
Description : None
Group       : leaf
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Origin codes: i=IGP, e=EGP, ?=incomplete
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
|                      Network                                        Path-id                           Next Hop                       MED                                                 LocPref                                               AsPath                    Origin         |
+=========================================================================================================================================================================================================================================================================================+
| 0.0.0.0/0                                            0                                        fe80::18b2:23ff:feff:1                  -                                                                                               [4200002000]                          ?           |

(truncated)

A:admin@g2-leaf21# show network-instance default route-table ipv4-unicast prefix 0.0.0.0/0
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance default
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+---------------------------------------------+-------+------------+----------------------+----------+----------+---------+------------+---------------------------+---------------------------+---------------------------+---------------------------+
|                   Prefix                    |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    |      Next-hop (Type)      |    Next-hop Interface     |  Backup Next-hop (Type)   | Backup Next-hop Interface |
|                                             |       |            |                      |          | Network  |         |            |                           |                           |                           |                           |
|                                             |       |            |                      |          | Instance |         |            |                           |                           |                           |                           |
+=============================================+=======+============+======================+==========+==========+=========+============+===========================+===========================+===========================+===========================+
| 0.0.0.0/0                                   | 0     | bgp        | bgp_mgr              | True     | default  | 0       | 170        | fe80::18b2:23ff:feff:1    | ethernet-1/31.0           |                           |                           |
|                                             |       |            |                      |          |          |         |            | (direct)                  |                           |                           |                           |
+---------------------------------------------+-------+------------+----------------------+----------+----------+---------+------------+---------------------------+---------------------------+---------------------------+---------------------------+
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

Finally test your ping against your DNS server, in this case what will reply is the loopback you've applied in the :material-router: pe1 or :material-router: pe4.

``` bash
A:admin@g2-leaf21# ping network-instance default 1.1.1.1 -c 10
Using network instance default
PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
64 bytes from 1.1.1.1: icmp_seq=1 ttl=63 time=4.22 ms
64 bytes from 1.1.1.1: icmp_seq=2 ttl=63 time=3.19 ms
64 bytes from 1.1.1.1: icmp_seq=3 ttl=63 time=4.10 ms
64 bytes from 1.1.1.1: icmp_seq=4 ttl=63 time=4.11 ms
64 bytes from 1.1.1.1: icmp_seq=5 ttl=63 time=3.70 ms
64 bytes from 1.1.1.1: icmp_seq=6 ttl=63 time=2.96 ms
64 bytes from 1.1.1.1: icmp_seq=7 ttl=63 time=3.37 ms
64 bytes from 1.1.1.1: icmp_seq=8 ttl=63 time=4.13 ms
64 bytes from 1.1.1.1: icmp_seq=9 ttl=63 time=2.29 ms
64 bytes from 1.1.1.1: icmp_seq=10 ttl=63 time=4.91 ms

--- 1.1.1.1 ping statistics ---
10 packets transmitted, 10 received, 0% packet loss, time 9011ms
rtt min/avg/max/mdev = 2.288/3.698/4.910/0.717 ms
``` 

You can repeat the ping test using the native IXR monitoring tool on the spine to capture packets, ensuring that traffic is being sent from the leaf towards the spine.

``` bash
A:admin@g2-spine21# tools system traffic-monitor destination-address 1.1.1.1 | grep ICMP
Capturing on 'monit'
 ** (tshark:87529) 11:28:26.289839 [Main MESSAGE] -- Capture started.
 ** (tshark:87529) 11:28:26.289922 [Main MESSAGE] -- File: "/tmp/wireshark_monitKNXTM3.pcapng"
1       0.000000000     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=1/256, ttl=64
2       1.003182326     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=2/512, ttl=64
3       2.002023579     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=3/768, ttl=64
4       3.006963413     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=4/1024, ttl=64
5       4.004017286     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=5/1280, ttl=64
6       5.005970165     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=6/1536, ttl=64
7       6.007035653     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=7/1792, ttl=64
8       7.007984937     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=8/2048, ttl=64
9       8.011271971     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=9/2304, ttl=64
10      9.010733067     ethernet-1/1.0  1a:3a:12:ff:00:1f       1a:b2:23:ff:00:01       10.46.2.43      1.1.1.1 ICMP    146     Echo (ping) request  id=0xa2e5, seq=10/2560, ttl=64
```

///

**🎉🚀⚡Congratulations, excellent work! You have successfully identified and resolved the issue, restoring connectivity to the DNS server 🛠️🧠✨**


### Configuration rollback

To complete the activity, you should rollback to the initial configuration.

If you have configured the ```loopback_test``` it’s a good idea to remove it once you’re done using it.

/// details | Warning: Loopback removal
    type: warning 

/// tab | Remove loopback

``` bash
A:admin@g2-pe1# edit-config global

2026-03-25T15:28:50.56+00:00
(gl)[/]
A:admin@g2-pe1# configure router "Base"

2026-03-25T15:28:57.27+00:00
(gl)[/configure router "Base"]
A:admin@g2-pe1# delete interface "loopback_test"

2026-03-25T15:29:01.81+00:00
*(gl)[/configure router "Base"]
A:admin@g2-pe1# compare
-   interface "loopback_test" {
-       admin-state enable
-       loopback
-       ipv4 {
-           primary {
-               address 1.1.1.1
-               prefix-length 32
-           }
-       }
-   }

2026-03-25T15:29:04.47+00:00
*(gl)[/configure router "Base"]
A:admin@g2-pe1# commit

2026-03-25T15:29:07.22+00:00
(gl)[/configure router "Base"]
A:admin@g2-pe1#

```
///
///


For the leaf/spine devices, you have two options:

1. Manually remove the changes which would be more complex and prone to error.

2. Rollback from the checkpoint which is the recommended and easier method. Don't forget to commit the new rolled-back configuration.

After executing the rollback command and committing the changes, verify that the configuration added during this activity in no longer present.

/// details | Solution: Rollback the configuration
    type: solution 

/// tab | rollback

``` bash
A:admin@g2-spine21# tools system configuration checkpoint 0 revert
/system/configuration/checkpoint[id=0]:
    Reverting to checkpoint 0 (name 'before_srl_tshoot_activity_20' comment 'this is a checkpoint before starting activity 20')

/:
    Successfully reverted configuration



--{ + running }--[  ]--
A:admin@g2-spine21#
```
///
///

## Conclusion

Congratulations!  If you have got this far, you have completed your troubleshooting activities, identified the network issue and resolved it.  You can now relax,  have that cup of coffee and hope that tomorrows shift handover is a little less eventful.

By completing this activity, you have successfully:

- Identified and resolved the connectivity issue affecting traffic from the data-center to the DNS server (`1.1.1.1`)
- Validated the network state and confirmed end-to-end reachability
- Analyzed and corrected routing behavior impacting external traffic forwarding
- Applied safe configuration practices using checkpoints and rollback mechanisms
- If you configured loopbacks on the PE routers as an additional step, you also validated that connectivity is successfully restored, with ICMP ping traffic now reaching the expected destination (`1.1.1.1`).
- You have also improved operational efficiency through the use of CLI aliases and workflow best practices, while reinforcing practical troubleshooting skills in a real-world CLOS data-center scenario.

This exercise provides a solid foundation for operating modern SR Linux environments with confidence.


