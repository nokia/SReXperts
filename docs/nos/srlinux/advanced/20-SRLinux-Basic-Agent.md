---
tags:
  - NDK
  - python
  - srlinux
  - srlinux agent
---

# NDK Agent to manage static-routes based on next-hop reachability checks


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           |  NDK Agent to manage static-routes based on next-hop reachability checks                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Activity ID**           | 20                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Short Description**       | Nokia SRLinux NDK (NetOps Development Kit) allows users to deploy non-native apps (aka agents). </p><br> These custom apps or agents run alongside native apps on SR Linux Network OS.</p><br>                                                                                                                                                                                     |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [NDK](https://learn.srlinux.dev/ndk/), [Python](https://www.python.org/)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: leaf11, :material-router: leaf13, :material-router: client02, :material-router: client11, :material-router: client13,:material-router: pe2                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **References**              | [SRLinux overview](https://documentation.nokia.com/srlinux/25-3/html/product/Overview.html)<br/>[NetOps Development Kit (NDK)](https://learn.srlinux.dev/ndk/)<br/> [NetOps Development Kit API Reference ](https://documentation.nokia.com/srlinux/25-3/title/ndk_api.html#undefined)<br/>[Apps Catalog](https://learn.srlinux.dev/ndk/apps/)<br/>[NDK Developers Guide](https://learn.srlinux.dev/ndk/guide/architecture/)<br/>[SR Linux applications](https://documentation.nokia.com/srlinux/25-3/books/config-basics/sr-linux-applications.html#sr-linux-applications)   | 


In this activity you will learn about the SRLinux NDK architecture and how to deploy non-native apps (aka custom agents).  
You will learn the file and folder structures and how to on-board a basic agent including the YANG data model.  
Finally, you will test the agent operation, inspect the code to fix some issues, validate the proper operation and add a new feature.

The objectives of this exercise are:

1. Explore the SRLinux NDK architecture and how to deploy non-native apps.
2. Inspect the agents file and folder structures and the on-board process.
3. Validate the agent execution, inspect the code, the logs and validate the proper operation.
4. Add code for a new feature

Let's first describe the use case.

### NDK Agent use case - static route with next-hop reachability validation
Imagine that you have a data center with an SR Linux IP fabric and several servers hosting two services (Green and Blue) each with it's own VLAN as represented in the picture below. Each service has multiple PODs distributed across the servers but exposing a single Anycast Virtual IP (VIP) per service. There is no BGP, BFD or other dynamic protocol supported, as such, static routes are used: the Anycast IP is the destination and the sub-interface VLAN IP is the next-hop.  

-{{ diagram(url='tiago-amado/srx/main/activity20_srx.clab.drawio', title='Fig. 1 - SR Linux basic agent - Use case setup', page=0) }}-

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>

As long as there is a POD active for a service in a server, the VIP and the VLAN interface will remain active. The leaves will have a static-route per service with the Anycast IP as destination and the local connected servers VLAN IP as next-hop. If a server or the physical interfaces fails, the leaf detects the failure and the route becomes inactive and is no longer advertised. However, if all the PODs are moved to another server or if there's a logical failure of one service, the leaves cannot detect it and an outage occurs.  
One potential solution would be to enhance the static-routes with the capability to validate the next-hop reachability, which is supported today in SROS ([cpe-check feature](https://infocenter.nokia.com/public/7750SR217R1A/index.jsp?topic=%2Fcom.nokia.Layer_3_Services_Guide_21.7.R1%2Fcpe_connectivit-d259e250.html)) but not in SR Linux.  

Your objective is to solve this problem using the NDK on SR Linux.


## Technology explanation

### NetOps Development Kit (NDK)

Nokia SR Linux provides a software development kit called **NetOps Development Kit** or **NDK** for short, that enables its users to create their own custom apps (also referred to as "agents"). These custom apps or agents run alongside native apps on SR Linux Network OS and can can deeply integrate with the rest of the SR Linux system.

<figure markdown>
  ![arch](https://gitlab.com/rdodin/pics/-/wikis/uploads/6beed5e008a32cffaeca2f6f811137b2/image.png){.img-shadow width="640" }
  <figcaption>Fig. 2 - Custom applications run natively on SR Linux NOS</figcaption>
</figure>


Applications developed with SR Linux NDK have a set of unique characteristics which set them aside from the traditional off-box automation solutions:

1. **Native integration with SR Linux system, management and telemetry**
2. **Programming language-neutral** - NDK is based on gRPC, it is possible to use any programming language that supports protobuf, such as [Python](https://learn.srlinux.dev/ndk/guide/dev/py/) and [Go](https://learn.srlinux.dev/ndk/guide/dev/go/)
3. **Deep integration with system components**


 > **Note:** Browse the [Apps Catalog](https://learn.srlinux.dev/ndk/apps/) with a growing list of NDK apps that Nokia or 3rd parties published.  


### NDK Architecture

The SRLinux NDK Architecture is illustrated in the Fig. 3. below. This shows how NDK gRPC service enables custom applications to interact with other SR Linux applications via Impart Database (IDB).  
Custom NDK applications app-1 and app-2 interact with other SR Linux subsystems via gRPC-based NDK service that offers access to IDB. SR Linux native apps, like BGP, LLDP, and others also interface with IDB to read and write configuration and state data.  


-{{image(url='../../../images/20_SRL_Agent_NDK_applications.png')}}-

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>


In addition to the traditional tasks of reading and writing configuration, NDK-based applications gain low-level access to the SR Linux system. For example, these apps can install FIB routes or listen to LLDP events.  

 > **Note:** Developers are welcomed to dig into the [NDK Developers Guide](https://learn.srlinux.dev/ndk/guide/architecture/) to learn all about NDK architecture and how to develop apps with this kit.  

#### SR Linux App logs

There are two concepts to keep in mind regarding logs and outputs that are generated by SR Linux apps:

 - **Standard Output/Error Redirection**: All apps (native or custom) `stdout/stderr` output is redirected by default to a file (with same name as the app) under `/var/log/srlinux/stdout`. This is useful for debugging or displaying exceptional error conditions - such as an application crash or unhandled exception.
 - **Operational Logging**: During normal operation, apps can produce structured log messages that describe their activity, status updates, and internal events. It's up to the app developer to decide how to implement this logic and to where send the logs to. SR Linux native apps are designed to send this logs to the system `syslog` daemon, allowing users to configure syslog rules to control how and where logs are forwarded, such as to external collectors or additional local files. In addition to user-defined rules, SR Linux includes built-in (hard-coded) syslog rules that forward a copy of all native apps logs to files under `/var/log/srlinux/debug/` for centralized access and troubleshooting.
   

## Access specific node/lab details

For this activity we will use a subset of the main topology, with a pair of leaves (`leaf11` and `leaf13`), a pair of clients (`client11` and `client13`) configured with the Anycast IP, and a third client (`client02`) to test connectivity as illustrated in Fig. 4. below:

-{{ diagram(url='tiago-amado/srx/main/activity20_srx.clab.drawio', title='Fig. 4 - SR Linux basic agent test setup', page=1) }}-

Keep in mind the following:

- An Anycast IP address is already configured at `client11` and `client13`.
- The new agent is deployed at `leaf11` and `leaf13` to allow the configuration of static routes to the anycast IP@ and allow next-hop validation.
- A complete agent solution is deployed in `leaf13`, while `leaf11` agent has missing parts that will be your challenge to complete along this activity. 
- Probe client is deployed at `client02` (to test connectivity to the `client11` and `client13` probe responder).

Let's now start with the activities! 

## Tasks

In this section we'll provide several tasks that will allow you to learn about SR Linux native agents and the process to onboard a new agent using NDK. The agent will allow to create new static-routes with the next-hop validation capabilities. 
We'll need to troubleshoot the onboard process, inspect the logs, configure the static-routes, validate the full operation and add new features to the agent. 

### Inspect the native apps/agents

First let's briefly inspect the native apps.  
Login to leaf11 `sr_cli` and verify which applications are running. Then move to linux `bash` and verify the contents of the `/opt/srlinux/appmgr/` folder.  

///note
 The `sr_cli` is SR Linux CLI and the linux `bash` is the underlying Linux shell that is running on SR Linux nodes. You can move between both using the keywords `sr_cli` or `bash`. 
///

  /// tab | View system apps from the SR Linux CLI
  ``` bash
  /show system application
  ```
  ///
  /// tab | Output

  ``` bash
  --{ + running }--[  ]--
  A:g15-leaf11# show system application
    +---------------------+---------+--------------------+-----------------------------------------------------------+--------------------------+
    |        Name         |   PID   |       State        |                          Version                          |       Last Change        |
    +=====================+=========+====================+===========================================================+==========================+
    | aaa_mgr             | 2095    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.585Z |
    | acl_mgr             | 2119    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.586Z |
    | app_mgr             | 1887    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:34.368Z |
    | arp_nd_mgr          | 2154    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.586Z |
    | bfd_mgr             | 2198    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.586Z |
    | bgp_mgr             | 6899    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:57.184Z |
    | chassis_mgr         | 2224    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.591Z |
    | dev_mgr             | 1951    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-04-13T11:27:07.152Z |
    | dhcp_client_mgr     | 2261    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.591Z |
    | dhcp_relay_mgr      |         | waiting-for-config |                                                           |                          |
    | dhcp_server_mgr     |         | waiting-for-config |                                                           |                          |
    | dnsmasq-mgmt        | 2789787 | running            | 2.89                                                      | 2025-04-14T16:34:09.562Z |
    | ethcfm_mgr          |         | waiting-for-config |                                                           |                          |
    | event_mgr           | 3331555 | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-04-17T12:36:51.996Z |
    | evpn_mgr            | 2302    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.591Z |
    | fhs_mgr             |         | waiting-for-config |                                                           |                          |
    | fib_mgr             | 2336    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.592Z |
    | grpc_server         | 3379    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:38.456Z |
    | idb_server          | 2058    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:31.274Z |
    | igmp_mgr            |         | waiting-for-config |                                                           |                          |
    | isis_mgr            |         | waiting-for-config |                                                           |                          |
    | json_rpc            | 7036    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:57.507Z |
    | l2_mac_learn_mgr    | 2366    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.592Z |
    | l2_mac_mgr          | 2445    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.592Z |
    | l2_proxy_arp_nd_mgr |         | waiting-for-config |                                                           |                          |
    | l2_static_mac_mgr   |         | waiting-for-config |                                                           |                          |
    | label_mgr           |         | waiting-for-config |                                                           |                          |
    | lag_mgr             | 2488    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.592Z |
    | ldp_mgr             |         | waiting-for-config |                                                           |                          |
    | license_mgr         | 2535    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.593Z |
    | linux_mgr           | 2567    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.593Z |
    | lldp_mgr            | 6946    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:57.337Z |
    | log_mgr             | 2614    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.593Z |
    | macsec_mgr          |         | waiting-for-config |                                                           |                          |
    | mcid_mgr            | 2656    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.593Z |
    | mfib_mgr            | 2707    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.593Z |
    | mgmt_server         | 2784688 | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-04-14T16:16:50.938Z |
    | mirror_mgr          |         | waiting-for-config |                                                           |                          |
    | mpls_mgr            |         | waiting-for-config |                                                           |                          |
    | net_inst_mgr        | 2806    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.594Z |
    | netconf_mgr         | 2673304 | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-04-14T10:58:23.092Z |
    | oam_mgr             |         | waiting-for-config |                                                           |                          |
    | oc_mgmt_server      | 2672247 | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-04-14T10:58:12.666Z |
    | ospf_mgr            |         | waiting-for-config |                                                           |                          |
    | pcc_mgr             |         | waiting-for-config |                                                           |                          |
    | pim_mgr             |         | waiting-for-config |                                                           |                          |
    | plcy_mgr            | 3275    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:38.147Z |
    | qos_mgr             | 3289    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:38.157Z |
    | radius_mgr          | 2859    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.594Z |
    | sdk_mgr             | 2874    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:33.594Z |
    | segrt_mgr           |         | waiting-for-config |                                                           |                          |
    | sflow_sample_mgr    | 2907    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:34.383Z |
    | snmp_server-mgmt    | 2785392 | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-04-14T16:16:58.385Z |
    | sshd-mgmt           | 2785340 | running            | OpenSSH_9.2p1 Debian-2+deb12u3, OpenSSL 3.0.15 3 Sep 2024 | 2025-04-14T16:16:58.372Z |
    | sshd-mgmt-netconf   | 2785352 | running            | OpenSSH_9.2p1 Debian-2+deb12u3, OpenSSL 3.0.15 3 Sep 2024 | 2025-04-14T16:16:58.379Z |
    | static_route_mgr    | 2087713 | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-04-11T15:44:54.691Z |
    | supported            | 1405    | running            |                                                           | 2025-03-31T15:58:30.377Z |
    | te_mgr              |         | waiting-for-config |                                                           |                          |
    | twamp_mgr           |         | waiting-for-config |                                                           |                          |
    | vrrp_mgr            |         | waiting-for-config |                                                           |                          |
    | vxlan_mgr           | 3323    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:38.170Z |
    | xdp_lc_1            | 2946    | running            | v24.10.3-201-g9d0e2b9371                                  | 2025-03-31T15:58:34.421Z |
    +---------------------+---------+--------------------+-----------------------------------------------------------+--------------------------+

  --{ + running }--[  ]--
  A:g15-leaf11#
  ```
  ///

  /// tab | View the native apps folder from bash
  ``` bash
  cd /opt/srlinux/appmgr/ && ls -al
  ```
  ///
  /// tab | Output - Native apps folder listing
  ``` bash
  admin@g15-leaf11:/etc/opt/srlinux$ cd /opt/srlinux/appmgr/
  admin@g15-leaf11:/opt/srlinux/appmgr$ ls -al
  total 296
  drwxr-xr-x 4 root root 4096 Feb 19 23:18 .
  drwxr-xr-x 1 root root 4096 Feb 19 23:18 ..
  drwxr-xr-x 2 root root 4096 Feb 19 23:18 aaa_mgr
  -rw-r--r-- 1 root root 2452 Feb 19 22:24 cgroup_profile.json
  drwxr-xr-x 2 root root 4096 Feb 19 23:18 logmgr
  -rw-rw-rw- 1 root root 3865 Feb 19 02:49 oc_yang_config.conf
  -rw-rw-rw- 1 root root  623 Feb 19 02:49 sr_aaa_mgr_config.yml
  -rw-rw-rw- 1 root root 1853 Feb 19 02:49 sr_acl_mgr_config.yml
  -rw-rw-rw- 1 root root  702 Feb 19 02:49 sr_app_mgr_config.yml
  -rw-rw-rw- 1 root root  712 Feb 19 02:49 sr_arp_nd_mgr_config.yml
  -rw-rw-rw- 1 root root  756 Feb 19 02:49 sr_bfd_mgr_config.yml
  -rw-rw-rw- 1 root root  643 Feb 19 02:49 sr_bgp_mgr_config.yml
  -rw-rw-rw- 1 root root 2292 Feb 19 02:49 sr_chassis_mgr_config.yml
  -rw-rw-rw- 1 root root  537 Feb 19 02:49 sr_device_mgr_config.yml
  -rw-rw-rw- 1 root root  307 Feb 19 02:49 sr_dhcp_client_mgr_config.yml
  -rw-rw-rw- 1 root root  676 Feb 19 02:49 sr_dhcp_relay_mgr_config.yml
  -rw-rw-rw- 1 root root  585 Feb 19 02:49 sr_dhcp_server_mgr_config.yml
  -rw-rw-rw- 1 root root  651 Feb 19 02:49 sr_ethcfm_mgr_config.yml
  -rw-rw-rw- 1 root root  632 Feb 19 02:49 sr_event_mgr_config.yml
  -rw-rw-rw- 1 root root  781 Feb 19 02:49 sr_evpn_mgr_config.yml
  -rw-rw-rw- 1 root root  526 Feb 19 02:49 sr_fhs_mgr_config.yml
  -rw-rw-rw- 1 root root  631 Feb 19 02:49 sr_fib_mgr_config.yml
  -rw-rw-rw- 1 root root  433 Feb 19 02:49 sr_gretunnel_mgr_config.yml
  -rw-rw-rw- 1 root root  728 Feb 19 02:49 sr_grpc_server_config.yml
  -rw-rw-rw- 1 root root  387 Feb 19 02:49 sr_idb_server_config.yml
  -rw-rw-rw- 1 root root  887 Feb 19 02:49 sr_igmp_mgr_config.yml
  -rw-rw-rw- 1 root root  839 Feb 19 02:49 sr_isis_mgr_config.yml
  -rw-rw-rw- 1 root root  824 Feb 19 02:49 sr_json_rpc_config.yml
  -rw-rw-rw- 1 root root  847 Feb 19 02:49 sr_l2_mac_learn_mgr_config.yml
  -rw-rw-rw- 1 root root 1592 Feb 19 02:49 sr_l2_mac_mgr_config.yml
  -rw-rw-rw- 1 root root  654 Feb 19 02:49 sr_l2_proxy_arp_nd_mgr_config.yml
  -rw-rw-rw- 1 root root  510 Feb 19 02:49 sr_l2_static_mac_mgr_config.yml
  -rw-rw-rw- 1 root root  517 Feb 19 02:49 sr_label_mgr_config.yml
  -rw-rw-rw- 1 root root  506 Feb 19 02:49 sr_lag_mgr_config.yml
  -rw-rw-rw- 1 root root  534 Feb 19 02:49 sr_ldp_mgr_config.yml
  -rw-rw-rw- 1 root root  541 Feb 19 02:49 sr_license_mgr_config.yml
  -rw-rw-rw- 1 root root 3464 Feb 19 02:49 sr_linux_mgr_config.yml
  -rw-rw-rw- 1 root root  598 Feb 19 02:49 sr_lldp_mgr_config.yml
  -rw-rw-rw- 1 root root  431 Feb 19 02:49 sr_log_mgr_config.yml
  -rw-rw-rw- 1 root root  565 Feb 19 02:49 sr_macsec_mgr_config.yml
  -rw-rw-rw- 1 root root  975 Feb 19 02:49 sr_mcid_mgr_config.yml
  -rw-rw-rw- 1 root root 1057 Feb 19 02:49 sr_mfib_mgr_config.yml
  -rw-rw-rw- 1 root root  945 Feb 19 02:49 sr_mgmt_server_config.yml
  -rw-rw-rw- 1 root root  639 Feb 19 02:49 sr_mirror_mgr_config.yml
  -rw-rw-rw- 1 root root  497 Feb 19 02:49 sr_mpls_mgr_config.yml
  -rw-rw-rw- 1 root root  620 Feb 19 02:49 sr_mplsoam_mgr_config.yml
  -rw-rw-rw- 1 root root  992 Feb 19 02:49 sr_net_inst_mgr_config.yml
  -rw-rw-rw- 1 root root  723 Feb 19 02:49 sr_netconf_mgr_config.yml
  -rw-rw-rw- 1 root root  532 Feb 19 02:49 sr_oam_mgr_config.yml
  -rw-rw-rw- 1 root root  635 Feb 19 02:49 sr_oc_mgmt_server_config.yml
  -rw-rw-rw- 1 root root  539 Feb 19 02:49 sr_ospf_mgr_config.yml
  -rw-rw-rw- 1 root root  494 Feb 19 02:49 sr_pcc_mgr_config.yml
  -rw-rw-rw- 1 root root  990 Feb 19 02:49 sr_pim_mgr_config.yml
  -rw-rw-rw- 1 root root  380 Feb 19 02:49 sr_pinger_config.yml
  -rw-rw-rw- 1 root root  902 Feb 19 02:49 sr_plcy_mgr_config.yml
  -rw-rw-rw- 1 root root  653 Feb 19 02:49 sr_pw_mgr_config.yml
  -rw-rw-rw- 1 root root  830 Feb 19 02:49 sr_qos_mgr_config.yml
  -rw-rw-rw- 1 root root  198 Feb 19 02:49 sr_radius_mgr_config.yml
  -rw-rw-rw- 1 root root  326 Feb 19 02:49 sr_sdk_mgr_config.yml
  -rw-rw-rw- 1 root root  456 Feb 19 02:49 sr_segrt_mgr_config.yml
  -rw-rw-rw- 1 root root  361 Feb 19 02:49 sr_sflow_sample_mgr_config.yml
  -rw-rw-rw- 1 root root  603 Feb 19 02:49 sr_static_route_mgr_config.yml
  -rw-rw-rw- 1 root root  375 Feb 19 02:49 sr_supportd_config.yml
  -rw-rw-rw- 1 root root  954 Feb 19 02:49 sr_te_mgr_config.yml
  -rw-rw-rw- 1 root root  817 Feb 19 02:49 sr_tepolicy_mgr_config.yml
  -rw-rw-rw- 1 root root 1219 Feb 19 02:49 sr_time_mgr_config.yml
  -rw-rw-rw- 1 root root  838 Feb 19 02:49 sr_timing_stack_config.yml
  -rw-rw-rw- 1 root root  751 Feb 19 02:49 sr_twamp_mgr_config.yml
  -rw-rw-rw- 1 root root  974 Feb 19 02:49 sr_vrrp_mgr_config.yml
  -rw-rw-rw- 1 root root  930 Feb 19 02:49 sr_vxlan_mgr_config.yml
  -rw-rw-rw- 1 root root  405 Feb 19 02:49 sr_xdp_cpm_config.yml
  -rw-rw-rw- 1 root root  542 Feb 19 02:49 sr_xdp_lc_config.yml
  -rw-r--r-- 1 root root 1411 Feb 19 22:24 upgradability.json
  admin@g15-leaf11:/opt/srlinux/appmgr$
  ```
  ///

  The previous outputs shows the native apps and their definition files.


### Inspect the custom agent

Keep the ssh session to `leaf11` open and create a new one to `leaf13`.   
Verify that a custom app `srl_basic_agent` is running. Compare the output against the one from `leaf11`.
Then move to linux bash and verify the contents of the `/etc/opt/srlinux/appmgr/` folder.


/// tab | View custom app from the SR Linux CLI
```
/show system application srl_basic_agent
```
///
/// tab | Output
``` bash
--{ running }--[  ]--
A:g15-leaf13# show system application srl_basic_agent
+-----------------+---------+---------+---------+--------------------------+
|      Name       |   PID   |  State  | Version |       Last Change        |
+=================+=========+=========+=========+==========================+
| srl_basic_agent | 2717566 | running | v1.0    | 2025-04-22T12:13:53.720Z |
+-----------------+---------+---------+---------+--------------------------+

--{ running }--[  ]--
A:g15-leaf13#
```
///

/// tab | List contents of custom app folder in bash  
``` bash
cd /etc/opt/srlinux/appmgr/ && ls -al -R
```
///
/// tab | Output
``` bash
admin@g15-leaf13:/etc/opt/srlinux/appmgr$ ls -al -R
.:
total 24
drwxrwxrwx+  3 srlinux srlinux  4096 Apr 23 17:35 .
drwxrwxrwx+ 14 srlinux srlinux  4096 Apr 22 12:04 ..
drwxrwxrwx   3 admin   ntwkuser 4096 Apr 22 12:04 srl_basic_agent
-rw-rw-r--+  1 admin   ntwkuser  887 Apr 22 11:53 srl_basic_agent.yml

./srl_basic_agent:
total 48
drwxrwxrwx  3 admin   ntwkuser  4096 Apr 22 12:04 .
drwxrwxrwx+ 3 srlinux srlinux   4096 Apr 23 17:35 ..
-rwxrwxrwx  1 admin   ntwkuser 21718 Apr 22 12:04 srl_basic_agent.py
-rwxrwxrwx  1 admin   ntwkuser   786 Apr 22 11:59 srl_basic_agent.sh
-rwxrwxrwx  1 admin   ntwkuser    24 Apr 22 12:02 srl_basic_agent_version.sh
drwxrwxrwx  2 admin   ntwkuser  4096 Apr 22 12:01 yang

./srl_basic_agent/yang:
total 12
drwxrwxrwx 2 admin ntwkuser 4096 Apr 22 12:01 .
drwxrwxrwx 3 admin ntwkuser 4096 Apr 22 12:04 ..
-rwxrwxrwx 1 admin ntwkuser 2467 Apr 22 12:01 srl_basic_agent.yang
admin@g15-leaf13:/etc/opt/srlinux/appmgr$
```
///

The previous outputs shows the custom app/agent and its configuration files.  
Is the `srl_basic_agent` agent running on both leafs?

/// details | Solution
    type: success
The agent is running at `leaf13` but not at `leaf11`. This is intended, because we introduce some issues that you need to solve in the following tasks!
///


### Onboard agent troubleshoot

At boot up, the SR Linux App Manager (`app_mgr`) looks for third-party apps `.yml` files in the `/etc/opt/srlinux/appmgr/` directory and loads them automatically.    
The onboarding of an NDK agent onto the SR Linux consists in copying [the agent and its files](https://learn.srlinux.dev/ndk/guide/agent/) over to the SR Linux filesystem and placing them in the directories.
The agent installation procedure can be carried out in different ways: [manual, automated or with `deb` packages](https://learn.srlinux.dev/ndk/guide/agent-install-and-ops/). 

The following agent files have been onboarded to both `leaf11` and `leaf13` for you already (using the CLAB bind feature):  

| Component         | Filesystem location                                                  |
| ---------------   | ----------------------------------------                             |
| Definition file   | `/etc/opt/srlinux/appmgr/srl_basic_agent.yml`                        |
| Executable file   | `/etc/opt/srlinux/appmgr/srl_basic_agent/srl_basic_agent.sh`         |  <!-- This file is usually placed at  `/usr/local/bin/`, but to keep it simple let's use the same dir for all files -->  
| YANG modules      | `/etc/opt/srlinux/appmgr/srl_basic_agent/yang/srl_basic_agent.yang`  |  <!-- This file is usually placed at  `/opt/$agentName/yang` --> 
| Agent version     | `/etc/opt/srlinux/appmgr/srl_basic_agent/srl_basic_agent_version.sh` |  <!-- This file is usually placed at  `/opt/$agentName/` --> 
| Agent Python code | `/etc/opt/srlinux/appmgr/srl_basic_agent/srl_basic_agent.py`         |  <!-- This file is usually placed at  `/opt/$agentName/` --> 

///warning
The agent version differs between leaf13 and leaf11.  
A complete working agent solution for this activity is deployed in `leaf13`, while `leaf11` agent has missing parts that will be your challenge to complete along this activity. 
///

///note
The agent files are located in your group's hackaton VM instance at `activities/nos/srlinux/20-SRLinux-basic-agent`. The `leaf11_agent` folder is binded to to the leaf11 `/etc/opt/srlinux/appmgr/`, so you can edit the files directly on the Hackaton VM host using Visual Studio code or any other editor.  

///

From the previous task we saw that the agent is running on `leaf13` but not on `leaf11`.  
  
Your task is to figure out why the agent is not running in `leaf11` and fix the issue.  

/// admonition | Stop and take time to think here
    type: question

- What is the first kind of file that system looks for to discover and load apps?
- Is it possible to check details about the app status, in addition to what is displayed by `show system application`? For example, how can you confirm that the parameters defined in `.yml` file were loaded as expected.
- What logs can be checked to help investigate the reason about why an app is not entering `running` state?

///

/// details | Hint 1
    type: tip
 - Check out [Agent Components](https://learn.srlinux.dev/ndk/guide/agent/){:target="_blank"} to know what key fields need to be filled in the definition `.yml` file.
 - You may also check examples of other custom apps in the [Apps Catalog](https://learn.srlinux.dev/ndk/apps/){:target="_blank"}
///

///details | Hint 2
    type: tip
You need to inspect agent `.yang` file, to know what needs to be filled in `yang-modules:` section of the definition `.yml` file.  


After modifying the app `.yml` file, how to signal the system to rediscover and process app `.yml` changes? This documentation piece can help you [Agent Installation & Operations - Loading the agent](https://learn.srlinux.dev/ndk/guide/agent-install-and-ops/#loading-the-agent){:target="_blank"}  


///

///details | Hint 3
    type: tip
Search for a path in the `state` datastore that represent detailed status about loaded apps.
///

///warning
During your attempts to load the app, if you introduce errors in the `.yml` file that conflicts with native SR Linux apps, the system might get into an unexpected state where you observe symptoms such as:  

 - missing information on `running` or `state` datastore
 - lose ssh access to the leaf

To recover, perform a restart of the `mgmt_server` native app with `tools system app-management application mgmt_server restart`. 
Take this into account for the remainder tasks of the activity.
///

/// details | Solution
    type: success

The `/etc/opt/srlinux/appmgr/srl_basic_agent.yml` is empty at leaf11 and that's why the app is not loading.

So you need to update your VM file at:  
`activities/nos/srlinux/20-SRLinux-basic-agent/leaf11_agent/srl_basic_agent.yml`.

You may also update leaf11's directly, e.g., with vi:  
`/etc/opt/srlinux/appmgr/srl_basic_agent.yml`  

  > **Note:** You can copy/paste code directly to `vi`, howhever, to keep your indentation you need to enable paste mode (Esc + `:set paste`) then move to insertation mode and paste your code. 

Once you fix the file you need to reload the app_mgr and verify that the `srl_basic_agent` is running. You may inspect the app status, version and state info with the following commands:

/// tab | reload app_mgr
``` bash
sr_cli
/tools system app-management application app_mgr reload
/show system application srl_basic_agent
```
///
/// tab | output - app summary status
``` bash
--{ running }--[  ]--
A:g15-leaf11# show system application srl_basic_agent
  +-----------------+---------+---------+---------+--------------------------+
  |      Name       |   PID   |  State  | Version |       Last Change        |
  +=================+=========+=========+=========+==========================+
  | srl_basic_agent | 2177265 | running | v0.5    | 2025-04-24T10:48:49.851Z |
  +-----------------+---------+---------+---------+--------------------------+
--{ running }--[  ]--
A:g15-leaf11#
```
///
/// tab | Output - info state (detailed status)
``` bash
--{ running }--[  ]--
A:g15-leaf11# info from state system app-management application srl_basic_agent
    system {
        app-management {
            application srl_basic_agent {
                pid 120406
                state running
                last-change "2025-04-27T17:19:33.203Z (37 minutes ago)"
                last-start-type cold
                author "Nokia SReXperts"
                failure-threshold 3
                failure-window 300
                failure-action wait=10
                path /etc/opt/srlinux/appmgr/srl_basic_agent/
                launch-command "sudo /etc/opt/srlinux/appmgr/srl_basic_agent/srl_basic_agent.sh"
                search-command "/bin/bash /etc/opt/srlinux/appmgr/srl_basic_agent/srl_basic_agent.sh"
                version v0.5
                oom-score-adj 0
                supported-restart-types [
                    cold
                ]
                restricted-operations [
                    quit
                ]
                statistics {
                    restart-count 52
                }
                yang {
                    modules [
                        srl_basic_agent
                    ]
                    source-directories [
                        /opt/srl_basic_agent/yang
                        /opt/srlinux/models/iana
                        /opt/srlinux/models/ietf
                        /opt/srlinux/models/srl_nokia/models
                    ]
                }
            }
        }
    }

--{ running }--[  ]--
A:g15-leaf11#
```
///


///



### Inspect the Agent logs

Open 2 new tabs to the `leaf11` bash and inspect the 2 agent logs files created under `/var/log/srlinux/stdout`:  

- srl_basic_agent.log - file created by the app_mgr to save `stdout/stderr` output of the app. You should see no errors.
- srl_basic_agent_python.log - custom log file created by `srl_basic_agent.py`. You should see keepalives

/// tab | View agent logs
``` bash
tail -f /var/log/srlinux/stdout/srl_basic_agent.log 
tail -f /var/log/srlinux/stdout/srl_basic_agent_python.log 
```
///

### Configure the new static routes  

Now that the agent is running on both leafs, its time to put it into action! The objective is to ensure reachability between the probe client and the probe responders' Anycast IP address. To accomplish this, you will use the custom agent to configure the static routes. <p>

The next-hop IP address reachability shall be periodically tested, such that when the next-hop becomes unreachable, respective static-route is automatically deactivated by the agent until reachability is restored.

**Your next task is to configure the new static routes in `leaf11` and `leaf13` under `ipvrf201` as shown in the diagram below:**


-{{ diagram(url='tiago-amado/srx/main/activity20_srx.clab.drawio', title='Fig. 4 - SR Linux basic agent logic setup', page=2) }}-

/// admonition
    type: question

The agent should expose a new configuration knob in `candidate` datastore that allows to manage the static routes. Can you find it out? 
///

/// details | Tip
    type: tip

You should see that under any ip-vrf instance there's a new option available: `static-routes-ndk`

/// tab | New agent Static-route
``` bash
--{ +! candidate shared default }--[ network-instance ipvrf201 ]--
A:g15-leaf11# static-routes
                   admin-state        
                   static-routes      
                   static-routes-ndk  




Local commands:
  static-routes
  static-routes-ndk
                    SReXperts - New static agent.


--{ +! candidate shared default }--[ network-instance ipvrf201 ]--
```
///
///


/// details | Solution
    type: success

/// tab | Leaf11
``` bash
exit all
enter candidate
network-instance ipvrf201
static-routes-ndk route 192.168.31.1/32 admin-state enable next-hop 192.168.30.11 cpe-check admin-state enable
commit now
```
///

/// tab | Leaf13
``` bash
exit all
enter candidate
network-instance ipvrf201
static-routes-ndk route 192.168.31.1/32 admin-state enable next-hop 192.168.30.13 cpe-check admin-state enable
commit now
```
///
///



### Verify the agent normal operation

Now that you have configured both `leaf11` and `leaf13`, you can verify the agent operation.  
The agent is supposed to consume configuration and populate state under the YANG path `/network-instance <name> static-routes-ndk`.

/// tab | Agent validation
``` bash
info from state / network-instance ipvrf201 static-routes-ndk
/show network-instance ipvrf201 route-table ipv4-unicast prefix 192.168.31.1/32
ping network-instance ipvrf201 192.168.31.1 -c 2
traceroute 192.168.31.1 network-instance ipvrf201
```
///
/// tab | Output leaf13 - info from state
``` bash
--{ + running }--[  ]--
A:g15-leaf13# info from state / network-instance ipvrf201 static-routes-ndk
    network-instance ipvrf201 {
        static-routes-ndk {
            route 192.168.31.1/32 {
                admin-state enable
                next-hop 192.168.30.13
                cpe-check {
                    admin-state enable
                    is-alive true
                    probe-statistics {
                        successful 17998
                        failed 0
                    }
                }
            }
        }
    }
```
///
/// tab | Output leaf11 - info from state
``` bash
--{ + running }--[ network-instance ipvrf201 static-routes-ndk ]--
A:g15-leaf11# info from state / network-instance ipvrf201 static-routes-ndk

```
///
/// tab | Output - route-table
``` bash
--{ + running }--[  ]--
A:g15-leaf11# show network-instance ipvrf201 route-table ipv4-unicast prefix 192.168.31.1/32
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance ipvrf201
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
|          Prefix           |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    | Next-hop (Type) |    Next-hop     | Backup Next-hop |   Backup Next-hop    |
|                           |       |            |                      |          | Network  |         |            |                 |    Interface    |     (Type)      |      Interface       |
|                           |       |            |                      |          | Instance |         |            |                 |                 |                 |                      |
+===========================+=======+============+======================+==========+==========+=========+============+=================+=================+=================+======================+
| 192.168.31.1/32           | 0     | bgp-evpn   | bgp_evpn_mgr         | False    | ipvrf201 | 0       | 170        | 10.46.15.35/32  |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | (indirect/vxlan |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | )               |                 |                 |                      |
| 192.168.31.1/32           | 10    | ndk1       | srl_basic_agent      | True     | ipvrf201 | 10      | 10         | 192.168.30.0/24 | irb0.101        |                 |                      |
|                           |       |            |                      |          |          |         |            | (indirect/local |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | )               |                 |                 |                      |
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--{ + running }--[  ]--
A:g15-leaf11#
```
///

/// tab | Output ping
``` bash
--{ + running }--[  ]--
A:g15-leaf11# ping network-instance ipvrf201 192.168.31.1 -c 2
Using network instance ipvrf201
PING 192.168.31.1 (192.168.31.1) 56(84) bytes of data.
64 bytes from 192.168.31.1: icmp_seq=1 ttl=64 time=1.84 ms
64 bytes from 192.168.31.1: icmp_seq=2 ttl=64 time=2.21 ms

--- 192.168.31.1 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 1.842/2.027/2.212/0.185 ms

--{ + running }--[  ]--
A:g15-leaf11#
```
///
/// tab | Output traceroute
``` bash
--{ + running }--[  ]--
A:g15-leaf11# traceroute 192.168.31.1 network-instance ipvrf201
Using network instance ipvrf201
traceroute to 192.168.31.1 (192.168.31.1), 30 hops max, 60 byte packets
 1  192.168.31.1 (192.168.31.1)  1.615 ms  1.563 ms  1.551 ms

--{ + running }--[  ]--
A:g15-leaf11#
```
///


Note from the output that there are 2 routes to `192.168.31.1`, the static-route installed by the agent identified as `ndk1`, and the route received from the other leaf through `bgp-evpn`. Only the local route is active, being the `bgp-evpn` in standby. <p>
Note that there is also no `state` populated in `leaf11`. This is one of the missing parts that you will be challenged to complete in a later task.<p>  

### Verify the agent operation under failure

To properly test the end-to-end the agent operation including failure scenarios, a probe client and probe responders will be used according to the table below:


| Component         | Filesystem location           | Nodes                      |
| ---------------   | ----------------------------  | -------------              | 
| probe client      | `/probe.sh`                   | `client02`                 |
| probe responder   | `/probe-responder.sh`         | `client11` and `client13`  |


The `probe-responder`is already installed and running at `client11` and `client13`.
On `client02` start the probe requests and verify that you're getting answers from both `client11` and `client13` (rate of 2 requests per second). 


/// tab | Start probe client
``` bash
/probe.sh 192.168.31.1 
```
///

/// tab | Output
``` bash
/probe.sh 192.168.31.1 
Probing 192.168.31.1:9999 using TCP...
Tue Apr 29 16:58:01 UTC 2025 - Response from client13
Tue Apr 29 16:58:01 UTC 2025 - Response from client11
Tue Apr 29 16:58:02 UTC 2025 - Response from client13
Tue Apr 29 16:58:02 UTC 2025 - Response from client13
Tue Apr 29 16:58:03 UTC 2025 - Response from client11
Tue Apr 29 16:58:03 UTC 2025 - Response from client11
Tue Apr 29 16:58:04 UTC 2025 - Response from client11
^C

```
///

Recall that the destination is an anycast address and sessions are load balanced across available targets.
If you don't get the expected result, have a look to the troobleshoot tips below, otherwise skip it and proceed the exercise.

/// details | Troubleshoot the probe operation
    type: tip

If you face any issues with the probes follow these steps:

1. Ensure the probe client and responders files exists at the hosts as listed in the table above.
2. Verify the file execution permissions and the script code.
3. verify that the responder is running on both `client11` and `client13` with: `ps -ef | grep probe`
   - If the probes are not running start them with: `setsid /probe-responder.sh`
4. Verify ip connectivity, arp, mac and routing tables.


/// tab | verify probe responder
``` bash
ps -ef | grep probe
```
///

/// tab | Start probe responder
``` bash
setsid /probe-responder.sh
```
///

/// tab | Code probe client
``` bash
#!/bin/bash
#usage: ./probe.sh <target-ip> [interval in seconds]

# Activity #20 SR Linux basic agent - Probe client

TARGET="$1"
PORT="9999"
INTERVAL="${2:-0.5}"  # Default interval between probes (in seconds)
TIMEOUT=1
echo "Probing $TARGET:$PORT using TCP..."

while true; do
    RESPONSE=$(echo "ping" | socat -T "$TIMEOUT" - TCP:"$TARGET":$PORT,connect-timeout="$TIMEOUT")

    if [ -n "$RESPONSE" ]; then
        echo "$(date) - Response from $RESPONSE"
        sleep "$INTERVAL"
    else
        echo "$(date) - No response or refused connection"
        sleep $INTERVAL
    fi
    
done
```
///

/// tab | Code probe responder
``` bash
#!/bin/bash
# start the probe responder: setsid /probe-responder.sh

# Activity #20 SR Linux basic agent - Probe server

#redirect stderr and stdout to a log file
exec >/tmp/"$0".log 2>&1

PORT=9999
HOSTNAME=$(hostname)

echo "Responder listening on TCP port $PORT..."
socat TCP-LISTEN:$PORT,reuseaddr,fork SYSTEM:"echo $HOSTNAME"
```
///

///



Now lets introduce a failure to view the agent in action.  

1. Open a session to `client11` and `client13` to verify the routing tables before and after the failure.
2. Keep an open session for `client02`  with the probe client running.
3. Log in to `client11` and shutdown the interface `eth1.101` with the commands below. 


/// tab | Client11 ifdown
``` bash
## show the interface status
ip -br addr show dev eth1.101
# disable the interface
sudo ifdown eth1.101 

```
///


/// tab | Client11 ifup
``` bash
# enable the interface
sudo ifup eth1.101
## show the interface status
ip -br addr show dev eth1.101
```
///


/// tab | Output Client02
``` bash
Tue Apr 29 19:03:53 UTC 2025 - Response from client13
Tue Apr 29 19:03:53 UTC 2025 - Response from client13
Tue Apr 29 19:03:54 UTC 2025 - Response from client11
Tue Apr 29 19:03:54 UTC 2025 - Response from client11
Tue Apr 29 19:03:55 UTC 2025 - Response from client13
2025/04/29 19:03:56 socat[15650] E connecting to AF=2 192.168.31.1:9999: Operation timed out
Tue Apr 29 19:03:56 UTC 2025 - No response or refused connection
Tue Apr 29 19:03:57 UTC 2025 - Response from client13
Tue Apr 29 19:03:57 UTC 2025 - Response from client13
Tue Apr 29 19:03:58 UTC 2025 - Response from client13
Tue Apr 29 19:03:58 UTC 2025 - Response from client13
```
///

/// tab | Output leaf11
``` bash
--{ + running }--[  ]--
A:g15-leaf11# show network-instance ipvrf201 route-table ipv4-unicast prefix 192.168.31.1/32
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance ipvrf201
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
|          Prefix           |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    | Next-hop (Type) |    Next-hop     | Backup Next-hop |   Backup Next-hop    |
|                           |       |            |                      |          | Network  |         |            |                 |    Interface    |     (Type)      |      Interface       |
|                           |       |            |                      |          | Instance |         |            |                 |                 |                 |                      |
+===========================+=======+============+======================+==========+==========+=========+============+=================+=================+=================+======================+
| 192.168.31.1/32           | 0     | bgp-evpn   | bgp_evpn_mgr         | False    | ipvrf201 | 0       | 170        | 10.46.15.35/32  |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | (indirect/vxlan |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | )               |                 |                 |                      |
| 192.168.31.1/32           | 10    | ndk1       | srl_basic_agent      | True     | ipvrf201 | 10      | 10         | 192.168.30.0/24 | irb0.101        |                 |                      |
|                           |       |            |                      |          |          |         |            | (indirect/local |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | )               |                 |                 |                      |
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--{ + running }--[  ]--
A:g15-leaf11# show network-instance ipvrf201 route-table ipv4-unicast prefix 192.168.31.1/32
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance ipvrf201
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
|          Prefix           |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    | Next-hop (Type) |    Next-hop     | Backup Next-hop |   Backup Next-hop    |
|                           |       |            |                      |          | Network  |         |            |                 |    Interface    |     (Type)      |      Interface       |
|                           |       |            |                      |          | Instance |         |            |                 |                 |                 |                      |
+===========================+=======+============+======================+==========+==========+=========+============+=================+=================+=================+======================+
| 192.168.31.1/32           | 0     | bgp-evpn   | bgp_evpn_mgr         | True     | ipvrf201 | 0       | 170        | 10.46.15.35/32  |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | (indirect/vxlan |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | )               |                 |                 |                      |
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--{ + running }--[  ]--
A:g15-leaf11#
Current mode: + running               
```
///

/// tab | Output leaf13
``` bash
--{ + running }--[  ]--
A:g15-leaf13# show network-instance ipvrf201 route-table ipv4-unicast prefix 192.168.31.1/32
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance ipvrf201
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
|          Prefix           |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    | Next-hop (Type) |    Next-hop     | Backup Next-hop |   Backup Next-hop    |
|                           |       |            |                      |          | Network  |         |            |                 |    Interface    |     (Type)      |      Interface       |
|                           |       |            |                      |          | Instance |         |            |                 |                 |                 |                      |
+===========================+=======+============+======================+==========+==========+=========+============+=================+=================+=================+======================+
| 192.168.31.1/32           | 0     | bgp-evpn   | bgp_evpn_mgr         | False    | ipvrf201 | 0       | 170        | 10.46.15.33/32  |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | (indirect/vxlan |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | )               |                 |                 |                      |
| 192.168.31.1/32           | 10    | ndk1       | srl_basic_agent      | True     | ipvrf201 | 10      | 10         | 192.168.30.0/24 | irb0.101        |                 |                      |
|                           |       |            |                      |          |          |         |            | (indirect/local |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | )               |                 |                 |                      |
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--{ + running }--[  ]--
A:g15-leaf13#

--{ + running }--[  ]--
A:g15-leaf13# show network-instance ipvrf201 route-table ipv4-unicast prefix 192.168.31.1/32
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
IPv4 unicast route table of network instance ipvrf201
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
|          Prefix           |  ID   | Route Type |     Route Owner      |  Active  |  Origin  | Metric  |    Pref    | Next-hop (Type) |    Next-hop     | Backup Next-hop |   Backup Next-hop    |
|                           |       |            |                      |          | Network  |         |            |                 |    Interface    |     (Type)      |      Interface       |
|                           |       |            |                      |          | Instance |         |            |                 |                 |                 |                      |
+===========================+=======+============+======================+==========+==========+=========+============+=================+=================+=================+======================+
| 192.168.31.1/32           | 10    | ndk1       | srl_basic_agent      | True     | ipvrf201 | 10      | 10         | 192.168.30.0/24 | irb0.101        |                 |                      |
|                           |       |            |                      |          |          |         |            | (indirect/local |                 |                 |                      |
|                           |       |            |                      |          |          |         |            | )               |                 |                 |                      |
+---------------------------+-------+------------+----------------------+----------+----------+---------+------------+-----------------+-----------------+-----------------+----------------------+
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--{ + running }--[  ]--
A:g15-leaf13#
```
///

/// tab | Output PE2
``` bash
[/]
A:admin@g15-pe2# show router "300" route-table 192.168.31.1

===============================================================================
Route Table (Service: 300)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric   
-------------------------------------------------------------------------------
192.168.31.1/32                               Remote  EVPN-IFL  00h04m48s  170
       10.46.15.33 (tunneled:VXLAN:201)                             0
192.168.31.1/32                               Remote  EVPN-IFL  00h04m48s  170
       10.46.15.35 (tunneled:VXLAN:201)                             0
-------------------------------------------------------------------------------
No. of Routes: 2
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================

[/]
A:admin@g15-pe2# show router "300" route-table 192.168.31.1

===============================================================================
Route Table (Service: 300)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric   
-------------------------------------------------------------------------------
192.168.31.1/32                               Remote  EVPN-IFL  00h58m22s  170
       10.46.15.35 (tunneled:VXLAN:201)                             0
-------------------------------------------------------------------------------
No. of Routes: 1
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================

[/]
A:admin@g15-pe2# 
```
///

Note that convergence is very fast and immediately after the failure all the probes requests are responded by `leaf13` only.
The leaf11 removes its local static-route and installs the `bgp-evpn` route received from `leaf13`.
`leaf13` has only its own local route and PE2 has only one `bgp-evpn` from `leaf13`.


///warning
**Don't forget to bring up the interface again!**
///


### Make leaf11 agent populate the state datastore
As you have observed in the "Verify the agent normal operation" task, the agent in `leaf11` is not populating the `state` datastore.  
Can you find out why and fix the issue?


/// details | Hint 1
Analyze the `srl_basic_agent.py` code in leaf11. Is there any method or function responsible to update the `state` datastore?
///
/// details | Hint 2
The function `update_state_datastore` needs to be completed.
///
/// details | Hint 3
- Check the [NDK documentation](https://ndk.srlinux.dev/doc/sdk?version=v0.4.0){:target="_blank"} to find what is the appropriate gRPC call to update the `state` datastore
- Check the [Python NDK bindings](https://github.com/nokia/srlinux-ndk-py/tree/v0.4.0){:target="_blank"} to find the respective Python function for the gRPC call.
- Check examples from similar code in this agent, or from the [Apps Catalog](https://learn.srlinux.dev/ndk/apps/){:target="_blank"}
///
/// note
You need to restart the agent for the python code changes to take effect. What command you can use for this?  
Check the [Agent Install and Operations](https://learn.srlinux.dev/ndk/guide/agent-install-and-ops/). 
///

Once you complete this task the `state` will be populated as shown below:

/// tab | Output static-routes-ndk info from state
```
--{ + running }--[ network-instance ipvrf201 static-routes-ndk ]--
A:g15-leaf11# info from state
    route 192.168.31.1/32 {
        admin-state enable
        next-hop 192.168.30.11
        cpe-check {
            admin-state enable
            is-alive true
        }
    }
```
///

/// details | Solution
    type: success
```py
def update_state_datastore(js_path, js_data):

    # create gRPC client stub for the Telemetry Service
    telemetry_stub = telemetry_service_pb2_grpc.SdkMgrTelemetryServiceStub(channel)

    # Build an telemetry update service request
    telemetry_update_request = telemetry_service_pb2.TelemetryUpdateRequest()

    # Add the YANG Path and Attribute/Value pair to the request
    telemetry_info = telemetry_update_request.state.add()
    telemetry_info.key.js_path = js_path
    telemetry_info.data.json_content = js_data

    # Log the request
    logging.info(f"Telemetry_Update_Request ::\{telemetry_update_request}")

    # Call the telemetry RPC
    telemetry_response = telemetry_stub.TelemetryAddOrUpdate(
        request=telemetry_update_request,
        metadata=metadata)

    return telemetry_response
```
///

### Add a feature to store basic statistics about next-hop-check probes

We would like really to challenge you for your final task.  
Modify leaf11's agent so that users are able to track (via the `state` datastore) the total number of successful and failed next-hop-check icmp probes (per static-route).  
Here's an example of what's expected:

/// tab | Output Probe-stats
```bash hl_lines="10-11"
--{ + candidate shared default }--[ network-instance ipvrf201 static-routes-ndk route
192.168.31.1/32 ]--
A:g15-leaf11# info from state
    admin-state enable
    next-hop 192.168.30.11
    cpe-check {
        admin-state enable
        is-alive false
        probe-statistics {
            successful 73
            failed 539
        }
    }

```

/// details | Tip
    type: tip

You first need to edit the `srl_basic_agent.yang` to include a new container `probe-statistics` under the container `cpe-check` including leaves `uint64` for each counter.

Then you need to edit the `srl_basic_agent.py` and: 

1. add new variables for the counters;
2. update the `update_telemetry` method;
3. update the `update_aliveness` method to update the counters and telemetry.


Finally, reload the `app_mgr` and verify that the `srl_basic_agent` is running:

///



/// details | Solution
    type: success

The outputs bellow shown the required code highlighted in blue.


/// tab | Code srl_basic_agent.yang
``` py hl_lines="58-68" linenums="1"
module srl_basic_agent {
  yang-version 1.1;
  namespace "urn:srl_sdk/srl_basic_agent";
  prefix srl_basic_agent;

  import srl_nokia-common {
      prefix srl_nokia-comm;
  }
  import srl_nokia-network-instance {
        prefix srl_nokia-netinst;
  }

  revision 2024-07-31 {
  description
    "SRLinux 24.7.1";
}

  grouping static-routes-ndk-top {
      container static-routes-ndk {
          presence "configure alternative static routes";

          description
              "SReXperts - ndk static-routes agent.";
          list route {
              max-elements 16384;
              key "prefix";
              leaf prefix {
                  must "not(../../../srl_nokia-netinst:type = 'srl_nokia-netinst:host')" {
                      error-message "Static route configuration not valid in network instance of type host";
                  }
                  type srl_nokia-comm:ip-prefix;
              }
              leaf admin-state {
                  type srl_nokia-comm:admin-state;
                  default "enable";
                  description
                      "Administratively enable or disable the static route.";
              }
              leaf next-hop {
                  type srl_nokia-comm:ip-address-with-zone;
                  description
                      "The next-hop IPv4 or IPv6 address

                      If the IPv6 address is a link-local address then the zoned format must be used";
              }
              container cpe-check {
                  leaf admin-state {
                  type srl_nokia-comm:admin-state;
                  default "enable";
                  description
                      "Probe the next-hop periodically using ICMP echo request.";
                  }

                  leaf is-alive {
                      type boolean;
                      config false;
                  }
                  container probe-statistics {
                    config false;
                    leaf successful {
                        type uint64;
                        config false;
                    }
                    leaf failed {
                        type uint64;
                        config false;
                    }
                  }
              }
          }
      }
  }

  augment "/srl_nokia-netinst:network-instance" {
      uses static-routes-ndk-top;
  }
}


```
///


/// tab | Code srl_basic_agent.py
``` py hl_lines="9-10 36-39 44-47" linenums="1"
#(...)
class StaticRoute():
    def __init__(self, data, route, network_instance):
        self.mutex = threading.Lock()
        self.admin_enabled = None
        self.cpe_check_enabled = None
        self.cpe_check_thread = None
        self.cpe_check_is_alive = None
        self.cpe_check_stat_successes = 0
        self.cpe_check_stat_failures = 0
        self.next_hop = None
        self.network_instance = network_instance
        self.route = route
        self.installed = False
        self.deleted = False
        self.update_config(data)
        self.evaluate()
    #(...)
    def update_telemetry(self):
        js_path = f'.network_instance{{.name=="{self.network_instance}"}}.static_routes_ndk.route{{.prefix=="{self.route}"}}'

        js_data = {
            "admin_state": 'ADMIN_STATE_enable' if self.admin_enabled else 'ADMIN_STATE_disable',
            "next_hop": self.next_hop,
            "cpe_check": {
                "admin_state": 'ADMIN_STATE_enable' if self.cpe_check_enabled else 'ADMIN_STATE_disable',
            }
        }

        if self.deleted:
            delete_state_datastore(js_path)
            return

        if self.cpe_check_thread:
            js_data['cpe_check']['is-alive'] =  self.cpe_check_is_alive
            js_data['cpe_check']['probe-statistics'] = {
                "successful": self.cpe_check_stat_successes,
                "failed": self.cpe_check_stat_failures
            }

        update_state_datastore(js_path=js_path, js_data=json.dumps(js_data))
    #(...)
    def update_aliveness(self, alive):
        if alive:
            self.cpe_check_stat_successes += 1
        else:
            self.cpe_check_stat_failures += 1

        #if alive status changed, evaluate route and update telemetry
        if alive != self.cpe_check_is_alive:
            self.cpe_check_is_alive = alive
            self.evaluate()

        self.update_telemetry()
    #(...)
```
///

/// tab | reload app_mgr
``` bash
sr_cli
/tools system app-management application app_mgr reload
/show system application srl_basic_agent
```
///
/// tab | output
``` bash
--{ running }--[  ]--
A:g15-leaf11# show system application srl_basic_agent
  +-----------------+---------+---------+---------+--------------------------+
  |      Name       |   PID   |  State  | Version |       Last Change        |
  +=================+=========+=========+=========+==========================+
  | srl_basic_agent | 2177265 | running | v1.0    | 2025-04-24T10:48:49.851Z |
  +-----------------+---------+---------+---------+--------------------------+
--{ running }--[  ]--
A:g15-leaf11#
```
///

///


And this concludes the activities we've prepared for you.   
These activities demonstrated how SR Linux agents work, how you can use NDK to create your own agents and the flexibility you have with SR Linux custom agents.  


## Summary and review

Congratulations! If you have got this far you have completed this activity and achieved the following:

- Explored the NDK architecture.  
- Understood the native and custom agents/apps file and folder structure and how to onboard new agents.  
- Verified agent operations, their logs and their state info.  
- Configured the new `SR_CLI static-route` provided by the agent, and tested it under normal and network failure situations.  
- Updated the custom agent YANG and Python scripts to include telemetry stats.  


You may explore the references for more information about developing Python or Go SR Linux agents. 

We hope you find this information useful and that you liked the activity.  
Now we invite you to try another amazing Hackathon activity.



