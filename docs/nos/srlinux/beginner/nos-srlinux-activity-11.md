---
tags:
  - SR Linux
  - ACL
  - traffic
  - monitoring
  - troubleshooting
  - checkpoint
---

# Troubleshooting Access Control Lists (ACLs) using traffic monitoring tools, and configuration checkpoints


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Troubleshooting Access Control Lists (ACLs) using traffic monitoring tools, and configuration checkpoints                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **Activity ID**           | 11                                                                                                                                                                                                                                                                                                                                                                                                                           |
| **Short Description**       | This activity provides hands-on experience with SR Linux tools for troubleshooting issues in network environments, with a primary focus on, but not limited to, data center fabric scenarios.    It will focus on troubleshooting Access Control Lists (ACLs).                                                                                                                                                                                                                                                                                                         |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                        |
| **Tools used**              | [Configuration Management](https://documentation.nokia.com/srlinux/24-10/books/config-basics/configuration-management.html#configuration-checkpoints)<br/>[ACLs](https://documentation.nokia.com/srlinux/24-10/books/acl-policy-based-routing/access-control-lists.html)<br/> [SRLinux Interactive Traffic Monitoring Tool](https://documentation.nokia.com/srlinux/24-10/books/troubleshooting-toolkit/interactive-traffic-monitor-tool-troubleshooting-toolkit.html)<br/>                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Topology Nodes**          | :material-router: Leaf11, :material-router: Leaf12, :material-router: Leaf13, :material-router: Spine11,  :material-router: Spine12                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [Learn SR Linux](https://learn.srlinux.dev/) |


Troubleshooting is an essential daily responsibility for network engineers. As network complexity continues to increase, this task becomes more challenging. Consequently, network engineers depend on a variety of tools to assist in their troubleshooting efforts. This activity explores the application of several SR Linux tools designed to support network engineers in such scenarios.

## Objective

During this activity, participants will be guided through the application of a set of SR Linux tools within a use case scenario. Upon completion, users will be able to understand and effectively utilize the following:

1. Configuration Checkpoints and rollback
2. Access Control Lists (ACLs) in SR Linux
3. SR Linux Interactive Traffic Monitoring Tool

## Technology
All tools and configurations in this activity are executed on Leaf and Spine devices, specifically [Nokia 7220 IXR](https://documentation.nokia.com/ixr/7220-IXR/index.html) platforms. These devices run the [Nokia SR Linux operating system](https://documentation.nokia.com/srlinux/index.html), which is the focus of this activity.

### Configuration Checkpoints
Before making configuration changes, network engineers commonly back up the current device configuration. Nokia SR Linux facilitates this process through built-in tools that allow users to create configuration checkpoints. When a checkpoint is generated, it is saved as a JSON file in the `/etc/opt/srlinux/checkpoint` directory, containing the complete configuration of the device.

Checkpoints are named using the format `checkpoint-<#>.json`, where `<#>` is a sequential number, 0 representing the most recent checkpoint. At any time, users can roll back the device configuration to a previously saved checkpoint, ensuring a reliable and efficient method for configuration recovery.

The list of saved checkpoint configurations can be obtained with the command `show system configuration checkpoint`.

### Access Control List (ACL)
An Access Control List (ACL) is a set of rules used within a network environment to evaluate packets individually, determining whether to allow or deny access. Each ACL entry includes a match condition and an associated action, which can be one of the following: accept, drop, log, or a rate-limit policer.

Nokia SR Linux supports both IPv4/IPv6 and MAC ACLs. IP ACLs can be configured as interface, CPM, capture, or system types for both IPv4 and IPv6 traffic. MAC ACLs are supported on interface and CPM types.

In this activity, participants will work specifically with IPv4 Interface ACLs.

### Interactive Traffic Monitoring Tool
SR Linux includes a built-in traffic monitoring tool that enables users to capture traffic based on defined match criteria. This is achieved through the use of a packet capture ACL, which can be applied to all subinterfaces of a specific IXR device.

Captured traffic can be viewed directly in the CLI, either in a simplified format or a more detailed output using the verbose option. Additionally, the capture data can be exported to a file for later analysis using third-party tools such as [wireshark](https://www.wireshark.org/), or `tshark`, which is available directly in SR Linux through bash.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

**It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.**

### SSH leaf and spine
Select one of the spines in the topology (e.g., spine11) and establish an SSH connection to it.

Then, repeat the process for a leaf device (e.g., leaf11), also connecting via SSH.

Keep both SSH sessions open throughout the duration of this task.

/// tab | ssh

``` bash
ssh admin@clab-srexperts-spine11
```

///
/// tab | expected output

``` bash
................................................................
:                  Welcome to Nokia SR Linux!                  :
:              Open Network OS for the NetOps era.             :
:                                                              :
:    This is a freely distributed official container image.    :
:                      Use it - Share it                       :
:                                                              :
: Get started: https://learn.srlinux.dev                       :
: Container:   https://go.srlinux.dev/container-image          :
: Docs:        https://doc.srlinux.dev/24-10                   :
: Rel. notes:  https://doc.srlinux.dev/rn24-10-3               :
: YANG:        https://yang.srlinux.dev/v24.10.3               :
: Discord:     https://go.srlinux.dev/discord                  :
: Contact:     https://go.srlinux.dev/contact-sales            :
................................................................

Last login: Wed Apr  9 13:17:53 2025 from 10.128.15.1
Using configuration file(s): ['/home/admin/.srlinuxrc']
Welcome to the srlinux CLI.
Type 'help' (and press <ENTER>) if you need any help using this.

--{ + running }--[  ]--
A:g15-spine11#

```
///

### Configuration checkpoint
**This step is extremely important and will be crucial to the success of the activity**.

Run the configuration checkpoint command on *both* the leaf and spine devices using Nokia SR Linux.

This will create a checkpoint that you'll use in the final step of this activity to perform a configuration rollback.

After creating the checkpoint, run the `show` command to view the list of available checkpoints. You should see your newly created checkpoint listed with ID 0, indicating that it is the most recent one.
/// details | Saving a checkpoint
/// tab | configuration checkpoint

``` bash
save checkpoint
show system configuration checkpoint
```

///
/// tab | expected output

``` bash
/system:
    Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'checkpoint-2025-03-26T14:38:09.022Z' and comment ''


--{ + running }--[  ]--
A:g15-spine11# show system configuration checkpoint
+-----+---------------------------------------+-----------------------+------------------+-------------------------------+
| Id  |    Name                               |      Comment          |     Username     |   Created                     |
+=====+=======================================+=======================+==================+===============================+
|   0 | checkpoint-2025-03-26T14:38:09.022Z   |                       | srlinux          | 2025-03-26T14:38:09.033Z      |
|   1 | clab-initial                          | set by containerlab   | srlinux          | 2025-03-21T14:32:28.703Z      |
+-----+---------------------------------------+-----------------------+------------------+-------------------------------+
```
///
///

### Verify node system IP
Inspect the IP address configured under the system interface.

You can verify this either by reviewing the device configuration or by using the appropriate show command.

Make sure to perform this step on both the selected leaf and spine devices.
/// details | Get the IP address using the show command

/// tab | system0 interface

``` bash
show interface system0
```

///
/// tab | expected output

``` bash
A:g15-spine11# show interface system0
=====================================================================================================================================================================================================
system0 is up, speed None, type None
  system0.0 is up
    Network-instances:
      * Name: default (default)
    Encapsulation   : null
    Type            : None
    IPv4 addr    : 10.46.15.31/32 (static, preferred)
    IPv6 addr    : fd00:fde8::15:31/128 (static, preferred)
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
=====================================================================================================================================================================================================

--{ + running }--[  ]--
A:g15-spine11#


```
///
///

/// details | Get the IP address by checking the running config

/// tab | system0 interface

``` bash
info from running interface system0
```

///
/// tab | expected output

``` bash
--{ + running }--[  ]--
A:g15-spine11# info from running interface system0
    interface system0 {
        subinterface 0 {
            ipv4 {
                admin-state enable
                address 10.46.15.31/32 {
                }
            }
            ipv6 {
                admin-state enable
                address fd00:fde8::15:31/128 {
                }
            }
        }
    }

--{ + running }--[  ]--
A:g15-spine11#


```
///
///

### Ping and traffic monitoring tool
With both SSH sessions active:

1. On the spine, start the traffic monitoring tool to capture incoming packets.

2. On the leaf, run a ping to the spine's system interface IP address that you previously verified. To specify the number of echo requests, for example 8 ICMP packets, use the -c flag with the ping command.

In this example, 8 ICMP packets were sent using the -c flag with the ping command.
You can choose a different value or omit the flag entirely to allow the ping to run without a packet limit.

After completing steps 1) and 2), the ICMP packets sent from the leaf should be visible and captured in the spine's CLI through the traffic monitoring tool.

/// details | Traffic monitor on spine
/// tab | Command

``` bash
tools system traffic-monitor destination-address 10.46.15.31
```

///
/// tab | expected output

``` bash
A:g15-spine11# tools system traffic-monitor destination-address 10.46.15.31
Capturing on 'monit'
 ** (tshark:547969) 14:36:01.553687 [Main MESSAGE] -- Capture started.
 ** (tshark:547969) 14:36:01.553817 [Main MESSAGE] -- File: "/tmp/wireshark_monitIVNC42.pcapng"
1       0.000000000     ethernet-1/1.0  1a:1a:0d:ff:00:31       1a:67:1d:ff:00:01       10.46.15.33     10.46.15.31     ICMP    146     Echo (ping) request  id=0x1a37, seq=1/256, ttl=64
2       1.000977231     ethernet-1/1.0  1a:1a:0d:ff:00:31       1a:67:1d:ff:00:01       10.46.15.33     10.46.15.31     ICMP    146     Echo (ping) request  id=0x1a37, seq=2/512, ttl=64
3       2.002000169     ethernet-1/1.0  1a:1a:0d:ff:00:31       1a:67:1d:ff:00:01       10.46.15.33     10.46.15.31     ICMP    146     Echo (ping) request  id=0x1a37, seq=3/768, ttl=64
4       3.003047325     ethernet-1/1.0  1a:1a:0d:ff:00:31       1a:67:1d:ff:00:01       10.46.15.33     10.46.15.31     ICMP    146     Echo (ping) request  id=0x1a37, seq=4/1024, ttl=64
5       4.004991392     ethernet-1/1.0  1a:1a:0d:ff:00:31       1a:67:1d:ff:00:01       10.46.15.33     10.46.15.31     ICMP    146     Echo (ping) request  id=0x1a37, seq=5/1280, ttl=64
6       5.005978041     ethernet-1/1.0  1a:1a:0d:ff:00:31       1a:67:1d:ff:00:01       10.46.15.33     10.46.15.31     ICMP    146     Echo (ping) request  id=0x1a37, seq=6/1536, ttl=64
7       6.006988736     ethernet-1/1.0  1a:1a:0d:ff:00:31       1a:67:1d:ff:00:01       10.46.15.33     10.46.15.31     ICMP    146     Echo (ping) request  id=0x1a37, seq=7/1792, ttl=64
8       7.009201611     ethernet-1/1.0  1a:1a:0d:ff:00:31       1a:67:1d:ff:00:01       10.46.15.33     10.46.15.31     ICMP    146     Echo (ping) request  id=0x1a37, seq=8/2048, ttl=64
^CStopping the capture and clearing the capture filter configuration
Command execution aborted : 'tools system traffic-monitor destination-address 10.46.15.31'

```
///
///

/// details | Ping from leaf to spine
/// tab | Command

``` bash
ping network-instance default 10.46.15.31 -c 8
```
///


/// tab | expected output

``` bash
A:g15-leaf11# ping network-instance default 10.46.15.31 -c 8
Using network instance default
PING 10.46.15.31 (10.46.15.31) 56(84) bytes of data.
64 bytes from 10.46.15.31: icmp_seq=1 ttl=64 time=3.99 ms
64 bytes from 10.46.15.31: icmp_seq=2 ttl=64 time=3.93 ms
64 bytes from 10.46.15.31: icmp_seq=3 ttl=64 time=4.05 ms
64 bytes from 10.46.15.31: icmp_seq=4 ttl=64 time=4.29 ms
64 bytes from 10.46.15.31: icmp_seq=5 ttl=64 time=4.83 ms
64 bytes from 10.46.15.31: icmp_seq=6 ttl=64 time=4.23 ms
64 bytes from 10.46.15.31: icmp_seq=7 ttl=64 time=3.84 ms
64 bytes from 10.46.15.31: icmp_seq=8 ttl=64 time=4.00 ms

--- 10.46.15.31 ping statistics ---
8 packets transmitted, 8 received, 0% packet loss, time 7009ms
rtt min/avg/max/mdev = 3.844/4.146/4.830/0.293 ms
```
///
///

### ACL configuration
On the spine device, configure an Access Control List (ACL) to capture the ICMP packets that were generated in the previous step.

To do this:

1. Create the ACL and enable statistics tracking (set statistics-per-entry to true to monitor matched packets).

2. Add an entry with matching criteria for ICMP traffic, define the match conditions (e.g. protocol type = ICMP) and specify the desired action. 

3. Apply the ACL to the appropriate interface (this should be the same interface that the ICMP packets were observed on during the packet capture in the previous task).


/// details | Solution (check if you get stuck)
```
type: success
A:g15-spine11# enter candidate
A:g15-spine11# diff
      acl {
+         acl-filter ping_leaf type ipv4 {
+             description "ACL to capture ICMP request from leaf"
+             statistics-per-entry true
+             entry 10 {
+                 match {
+                     ipv4 {
+                         protocol icmp
+                         destination-ip {
+                             prefix 10.46.15.31/32
+                         }
+                         icmp {
+                             type echo
+                         }
+                         source-ip {
+                             prefix 10.46.15.33/32
+                         }
+                     }
+                 }
+                 action {
+                     accept {
+                     }
+                 }
+             }
+         }
+         interface ethernet-1/1.0 {
+             input {
+                 acl-filter ping_leaf type ipv4 {
+                 }
+             }
+         }
      }

```
///

### Check ACL statistics
Repeat the ping command on the leaf, just as you did before.

Then, on the spine, check the ACL statistics.

You should observe that the number of matched packets corresponds exactly to the number of ICMP packets sent from the leaf.
If you run the ping multiple times, the statistics will show a cumulative count of all matching packets since the ACL was applied.

/// details | Check ACL statistics
/// tab | Command

``` bash
show acl ipv4-filter ping_leaf entry 10
```

///

/// tab | expected output

``` bash
A:g15-spine11# show acl ipv4-filter ping_leaf entry 10
======================================================================================================================================================================================================================================================================================
Filter        : ping_leaf
SubIf-Specific: disabled
Entry-stats   : yes
Entries       : 1
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Entry 10
  Match               : protocol=icmp, 10.46.15.33/32(*)->10.46.15.31/32(*)
  Action              : accept
  Match Packets       : 8
  Last Match          : 4 seconds ago
  TCAM Entries        : 1 for one subinterface and direction
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```
///
///

### Modify ACL to drop the packet
On the spine, modify the existing ACL configuration to drop ICMP packets instead of allowing them.

To do this:

1. Enter the candidate configuration mode.

2. Locate the ACL entry that matches ICMP traffic.

3. Change the action from accept to drop.

4. Commit the changes to apply the new configuration.

This will drop ICMP packets from reaching their destination, effectively blocking the pings sent from the leaf.

/// details | Solution (check if you get stuck)
```
A:g15-spine11# enter candidate
A:g15-spine11# diff
      acl {
          acl-filter ping_leaf type ipv4 {
              entry 10 {
                  action {
-                     accept {
+                     drop {
                      }
                  }
              }
          }
      }

```
///

### Clear and check ACL statistics
1. On the spine, clear the ACL statistics on the spine to reset the packet counters.

2. On the leaf, repeat the same ping command you used earlier to send ICMP packets to the spine.

You should observe:

- The exact number of ICMP packets sent by the leaf, now marked with the action drop.

- No ping replies received on the leaf, since the spine is now dropping the ICMP traffic.

/// details | clear and show acl statistics
/// tab | Command
``` bash
tools acl acl-filter ping_leaf type ipv4 statistics clear
show acl ipv4-filter ping_leaf entry 10
```
///
/// tab | expected output

``` bash
A:g15-spine11# show acl ipv4-filter ping_leaf entry 10
======================================================================================================================================================================================================================================================================================
Filter        : ping_leaf
SubIf-Specific: disabled
Entry-stats   : yes
Entries       : 1
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Entry 10
  Match               : protocol=icmp, 10.46.15.33/32(*)->10.46.15.31/32(*)
  Action              : drop
  Match Packets       : 8
  Last Match          : 14 seconds ago
  TCAM Entries        : 1 for one subinterface and direction
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```
///
///

### Configuration rollback
To complete the activity, you should rollback to the initial configuration.

You have two options:

- Manually remove the changes which would be more complex and prone to error.

- Rollback from the checkpoint which is the recommended and easier method.  Don't forget to commit the new rolled-back configuration.

After executing the rollback command and committing the changes, verify that the ACL configuration you applied on the spine is no longer present.

/// details | Rollback the configuration
/// tab | rollback

``` bash
tools system configuration checkpoint 0 revert
commit now
```

///
///

