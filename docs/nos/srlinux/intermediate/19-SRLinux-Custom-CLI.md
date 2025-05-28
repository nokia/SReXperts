---
tags:
  - python
  - srlinux
  - srlinux cli plugin
---

# Create your own traffic overview CLI command


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Create your own traffic overview CLI command using a SR Linux CLI plug-in.                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Activity ID**           | 19                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Short Description**       | Network engineers often need specific CLI commands to troubleshoot, monitor, or configure devices. Traditionally, the only way to get those commands is to submit a feature request to the vendor and wait. </p><br> But what if you could create and deploy your own CLI commands instantly?</p><br> Welcome to SR Linux CLI — a Python-based, open-source, and fully pluggable CLI engine. It allows you to extend the CLI with custom commands that behave just like native ones. No delays. No feature requests. Just the flexibility to build what you need, when you need it. </p><br>                                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [Python](https://www.python.org/)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: leaf11                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [SR Linux CLI plugin documentation](https://learn.srlinux.dev/cli/plugins/)<br/> [SR Linux uptime plugin](https://github.com/srl-labs/uptime-cli-plugin)<br/> [CLI plug-in guide](https://documentation.nokia.com/srlinux/25-3/title/cli_plugin.html)<br/> [SR Linux YANG browser](https://yang.srlinux.dev/)<br/> |


SR Linux CLI is an open-source, Python-based, and pluggable engine.
It allows users to implement custom CLI `global`, `show`, and `tools` commands that run alongside the native CLI commands. SR Linux provides a Python framework to develop those commands.  



In this activity, we will explore the native CLI commands, how the Python CLI plugin framework is implemented in SR Linux and develop custom CLI Plugins.


## Objective

Imagine you are managing a network with SR Linux nodes, and you receive a request to create several custom `global`, `show`, and `tools` commands for the operations and engineering teams. These new commands will also be used by automation tools to collect system information efficiently.  

Some examples are:

- `show traffic` - to display a table with the in/out traffic rate per active interface and the total per chassis.
- `show inventory` - to display all system FRUs (cards, PSUs, FANs, transceivers,...) including part numbers and serial numbers.
- `show interface-summary` - to display a summary with the count of interfaces per type (loopback, ethernet, mgmt, sub-interfaces), their operational or admin state (up or down), their speed (10G, 25G, 100G, 400G, ...), form factor (SFP, SFPplus, SFP28, QSFP28,...), connector type, etc.
- Enhance existing commands to change the format or information displayed.


In this activity we'll guide you through the `show traffic` custom CLI command deployment.

The objectives of this exercise are:  

   1. Familiarize with the SR Linux CLI engine filesystem and explore native CLI plugins  
   2. Create a modified `show version` plugin using an existing native plugin as reference with custom modifications  
   3. Create a new custom CLI `show traffic` command step-by-step  


With this activity you'll learn how flexible it is to modify or implement a new SRLinux custom CLI plugin.

## Technology explanation
<!-- Text from: https://github.com/srl-labs/learn-srlinux/blob/main/docs/cli/plugins/index.md -->

The pluggable architecture of SR Linux CLI allows you to create custom CLI commands using the same infrastructure as the native SR Linux commands.  

The Python-based CLI engine allows a user to create the custom CLI commands in the following categories:

- **show** commands  
    These are your much-loved show commands that print out the state of the system in a human-readable format, often in a table.  
- **global** commands  
    These are operational commands like `ping`, `traceroute`, `file`, `bash`, etc.  
- **tools** commands  
    These represent a run-to-completion task or an operation. Like a reboot or a request to load a configuration from a file.



-{{ diagram(url='srl-labs/uptime-cli-plugin/main/diagrams/cli.drawio', title='CLI engine and its plugin architecture', page=0) }}-

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>

> The configuration commands are not implemented as CLI plugins, they directly modify the candidate configuration datastore and are not subject to customization.

As shown in the diagram above, the CLI plugins infrastructure is used to support both SR Linux native and custom commands. Users can add their own command simply by putting a Python file in one of the directories used in the CLI plugin discovery process.

When SR Linux CLI is started, the available commands (native and user-defined) are loaded by the engine based on the plugin discovery process that scans the known directories for Python files implementing the `CliPlugin` interface.


## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  


For the activity tasks you will login to `leaf11`.  
You may use the `bash` CLI command to move to the Linux shell from the SR Linux CLI.

/// tab | login with SSH to `sr_cli`

```
ssh admin@clab-srexperts-leaf11
```

///


 There are 3 tasks sections below:  

   1. Explore the native CLI plugins  
   
   2. Create modified `show version` CLI  

   3. Create `show traffic` custom CLI  


**Let's now start the activity tasks!**  


### Explore the native CLI plugins

Before you start deploying your own custom CLI plugins you decide to inspect the existing native plugins to learn and use as examples.  

In this section you'll familiarize yourself with the SR Linux CLI engine filesystem and explore native CLI plugins.  

Customized CLI commands can be added to SR Linux using a Python plugin framework. The native `global`, `show` and `tools` SR Linux commands use this same framework, and their source code is available to any CLI user with admin access rights. 
The existing native CLI commands can be used to learn how to create additional CLI commands. 

1. Login to `leaf11` and move to the linux `bash` shell.


2. Go to the native CLI plugins directory, where the Python source code for the native global CLI commands is located, and list its contents. Using the documentation references, can you find the native plugins directory?

    /// details | Solution: Native global CLI plugins list

    /// tab | cmd

    ``` bash
    cd /opt/srlinux/python/virtual-env/lib/python3.11/dist-packages/srlinux/mgmt/cli/plugins/
    ls -al
    ```

    ///
    /// tab | Native global plugins

    ``` bash linenums="1"
    admin@g15-leaf11:~$ cd /opt/srlinux/python/virtual-env/lib/python3.11/dist-packages/srlinux/mgmt/cli/plugins/
    admin@g15-leaf11:/opt/srlinux/python/virtual-env/lib/python3.11/dist-packages/srlinux/mgmt/cli/plugins$ ls -al
    total 912
    drwxr-xr-x 1 root root  4096 Mar 31 15:58 .
    drwxr-xr-x 1 root root  4096 Mar 31 15:58 ..
    -rw-r--r-- 1 root root   267 Feb 19 22:24 __init__.py
    drwxr-xr-x 2 root root  4096 Apr  8 14:02 __pycache__
    -rw-r--r-- 1 root root  5392 Feb 19 22:24 acl_resequence.py
    -rw-r--r-- 1 root root 14700 Feb 19 22:24 admin_tech.py
    -rw-r--r-- 1 root root 27199 Feb 19 22:24 alias.py
    -rw-r--r-- 1 root root  6950 Feb 19 22:24 annotate.py
    -rw-r--r-- 1 root root  7392 Feb 19 22:24 autoboot.py
    -rw-r--r-- 1 root root  9946 Feb 19 22:24 back.py
    -rw-r--r-- 1 root root  2938 Feb 19 22:24 baseline.py
    -rw-r--r-- 1 root root  2113 Feb 19 22:24 bash.py
    -rw-r--r-- 1 root root  9940 Feb 19 22:24 bash_network_command_helper.py
    -rw-r--r-- 1 root root  7297 Feb 19 22:24 bash_output_modifiers.py
    -rw-r--r-- 1 root root  4069 Feb 19 22:24 bottom_toolbar.py
    -rw-r--r-- 1 root root   518 Feb 19 22:24 candidate_mode.py
    -rw-r--r-- 1 root root  5313 Feb 19 22:24 cgroup.py
    -rw-r--r-- 1 root root   726 Feb 19 22:24 clear.py
    -rw-r--r-- 1 root root 10186 Feb 19 22:24 cli_engine.py
    -rw-r--r-- 1 root root 16334 Feb 19 22:24 commit.py
    -rw-r--r-- 1 root root  1482 Feb 19 22:24 confirmation_prompt.py
    -rw-r--r-- 1 root root 18789 Feb 19 22:24 copy_.py
    -rw-r--r-- 1 root root  3722 Feb 19 22:24 date.py
    -rw-r--r-- 1 root root  2011 Feb 19 22:24 delete.py
    -rw-r--r-- 1 root root 14439 Feb 19 22:24 deploy_agent.py
    -rw-r--r-- 1 root root  9827 Feb 19 22:24 deploy_image.py
    -rw-r--r-- 1 root root 10308 Feb 19 22:24 diff.py
    -rw-r--r-- 1 root root 10105 Feb 19 22:24 diff_printer.py
    -rw-r--r-- 1 root root  4948 Feb 19 22:24 discard.py
    -rw-r--r-- 1 root root  4269 Feb 19 22:24 disconnect.py
    -rw-r--r-- 1 root root  1495 Feb 19 22:24 echo.py
    -rw-r--r-- 1 root root  6494 Feb 19 22:24 enter.py
    -rw-r--r-- 1 root root 13503 Feb 19 22:24 environment.py
    -rw-r--r-- 1 root root  3429 Feb 19 22:24 eql.py
    -rw-r--r-- 1 root root  1981 Feb 19 22:24 exit.py
    -rw-r--r-- 1 root root 17073 Feb 19 22:24 file_cmds.py
    -rw-r--r-- 1 root root  8866 Feb 19 22:24 file_path_completer.py
    -rw-r--r-- 1 root root 20490 Feb 19 22:24 filter.py
    -rw-r--r-- 1 root root  7100 Feb 19 22:24 flat_info_formatter.py
    -rw-r--r-- 1 root root  5311 Feb 19 22:24 from_subcommand.py
    -rw-r--r-- 1 root root  6690 Feb 19 22:24 help.py
    -rw-r--r-- 1 root root 11673 Feb 19 22:24 history.py
    -rw-r--r-- 1 root root 13321 Feb 19 22:24 info.py
    -rw-r--r-- 1 root root  7919 Feb 19 22:24 info_printer.py
    -rw-r--r-- 1 root root  2318 Feb 19 22:24 input_logger.py
    -rw-r--r-- 1 root root 14195 Feb 19 22:24 insert.py
    -rw-r--r-- 1 root root  6551 Feb 19 22:24 interface_name_completer.py
    -rw-r--r-- 1 root root  2566 Feb 19 22:24 key_completion_limit.py
    -rw-r--r-- 1 root root  5180 Feb 19 22:24 leafref_completer.py
    -rw-r--r-- 1 root root 11288 Feb 19 22:24 list.py
    -rw-r--r-- 1 root root 14532 Feb 19 22:24 load.py
    -rw-r--r-- 1 root root 12858 Feb 19 22:24 monitor.py
    -rw-r--r-- 1 root root  3792 Feb 19 22:24 more.py
    -rw-r--r-- 1 root root  2526 Feb 19 22:24 network_instance.py
    -rw-r--r-- 1 root root  3521 Feb 19 22:24 output_display_format.py
    -rw-r--r-- 1 root root  1103 Feb 19 22:24 output_format_modifier.py
    -rw-r--r-- 1 root root 13470 Feb 19 22:24 packet_trace.py
    -rw-r--r-- 1 root root  4817 Feb 19 22:24 pagination.py
    -rw-r--r-- 1 root root  2943 Feb 19 22:24 passwd.py
    -rw-r--r-- 1 root root  4900 Feb 19 22:24 ping.py
    -rw-r--r-- 1 root root  3836 Feb 19 22:24 prompt.py
    -rw-r--r-- 1 root root  2032 Feb 19 22:24 pwc.py
    -rw-r--r-- 1 root root  2280 Feb 19 22:24 question_mark.py
    -rw-r--r-- 1 root root   719 Feb 19 22:24 quit.py
    -rw-r--r-- 1 root root 10069 Feb 19 22:24 read_only_schema.py
    -rw-r--r-- 1 root root  3405 Feb 19 22:24 references.py
    -rw-r--r-- 1 root root 12677 Feb 19 22:24 replace.py
    drwxr-xr-x 1 root root  4096 Apr  8 14:02 reports
    -rw-r--r-- 1 root root  8558 Feb 19 22:24 rule_cli_schema_path_completer.py
    -rw-r--r-- 1 root root   549 Feb 19 22:24 running_mode.py
    -rw-r--r-- 1 root root  9324 Feb 19 22:24 save.py
    -rw-r--r-- 1 root root  2095 Feb 19 22:24 schema.py
    -rw-r--r-- 1 root root 27785 Feb 19 22:24 secure_boot.py
    -rw-r--r-- 1 root root  3873 Feb 19 22:24 session_idle_timeout.py
    -rw-r--r-- 1 root root  3804 Feb 19 22:24 set.py
    -rw-r--r-- 1 root root  6801 Feb 19 22:24 show.py
    -rw-r--r-- 1 root root  3374 Feb 19 22:24 slash.py
    -rw-r--r-- 1 root root  3619 Feb 19 22:24 source.py
    -rw-r--r-- 1 root root  2464 Feb 19 22:24 space_completion.py
    -rw-r--r-- 1 root root  3554 Feb 19 22:24 squiggly_brackets.py
    -rw-r--r-- 1 root root  2260 Feb 19 22:24 ssh.py
    -rw-r--r-- 1 root root   574 Feb 19 22:24 state_mode.py
    -rw-r--r-- 1 root root 15619 Feb 19 22:24 subcmd_navigation.py
    -rw-r--r-- 1 root root 17537 Feb 19 22:24 subinterface_name_completer.py
    -rw-r--r-- 1 root root 31679 Feb 19 22:24 subtree_navigation.py
    -rw-r--r-- 1 root root  9604 Feb 19 22:24 switch_mode.py
    -rw-r--r-- 1 root root  1890 Feb 19 22:24 systemd_manager.py
    drwxr-xr-x 2 root root  4096 Feb 19 23:18 test
    -rw-r--r-- 1 root root  1587 Feb 19 22:24 time_formatter.py
    -rw-r--r-- 1 root root  4117 Feb 19 22:24 tools.py
    -rw-r--r-- 1 root root  5538 Feb 19 22:24 tools_executor.py
    -rw-r--r-- 1 root root   937 Feb 19 22:24 tools_mode.py
    -rw-r--r-- 1 root root  4420 Feb 19 22:24 tools_schema.py
    -rw-r--r-- 1 root root  3874 Feb 19 22:24 traceroute.py
    -rw-r--r-- 1 root root 18364 Feb 19 22:24 traffic_monitor.py
    -rw-r--r-- 1 root root  7620 Feb 19 22:24 tree.py
    -rw-r--r-- 1 root root 21378 Feb 19 22:24 watch.py
    -rw-r--r-- 1 root root 11373 Feb 19 22:24 writable_schema.py
    -rw-r--r-- 1 root root  3539 Feb 19 22:24 yang_models.py
    admin@g15-leaf11:/opt/srlinux/python/virtual-env/lib/python3.11/dist-packages/srlinux/mgmt/cli/plugins$ 
    ```
    ///
    ///

3. Do you recognize any of the listed files from the plugins folder?


    /// details | Explanation version.py
    From the output file list you should recognize several of those commands, such as `clear`, `date`, `echo`, `info` or `ping`. These are some of the **global** CLI commands available in `sr_cli`.  
    ///



4. Do you recognize any `show` CLI command? Can you find where the `show` CLI commands are located?   

    /// details | Solution: Native `show` CLI plugins list
    The native `show` CLI commands Python source code files are located under `plugins/reports` directory. 
    /// tab | cmd

    ``` bash
    cd reports/
    ls -al
    ```

    ///
    /// tab | Native show CLI commands

    ``` bash linenums="1"
    admin@g15-leaf11:/opt/srlinux/python/virtual-env/lib/python3.11/dist-packages/srlinux/mgmt/cli/plugins$ cd reports/
    admin@g15-leaf11:/opt/srlinux/python/virtual-env/lib/python3.11/dist-packages/srlinux/mgmt/cli/plugins/reports$ ls -al
    total 2540
    drwxr-xr-x 1 root root  4096 Apr  8 14:02 .
    drwxr-xr-x 1 root root  4096 Mar 31 15:58 ..
    -rw-r--r-- 1 root root   267 Feb 19 22:24 __init__.py
    drwxr-xr-x 2 root root 16384 Apr  8 14:02 __pycache__
    -rw-r--r-- 1 root root 30981 Feb 19 22:24 acl_ipv4_filter_report.py
    -rw-r--r-- 1 root root 30903 Feb 19 22:24 acl_ipv6_filter_report.py
    -rw-r--r-- 1 root root 22527 Feb 19 22:24 acl_mac_filter_report.py
    -rw-r--r-- 1 root root  3330 Feb 19 22:24 acl_reports.py
    -rw-r--r-- 1 root root 14349 Feb 19 22:24 acl_summary_report.py
    -rw-r--r-- 1 root root  8379 Feb 19 22:24 arpnd_reports.py
    -rw-r--r-- 1 root root 27054 Feb 19 22:24 bgp_evpn_advertised_routes_report.py
    -rw-r--r-- 1 root root  7899 Feb 19 22:24 bgp_evpn_instance_report.py
    -rw-r--r-- 1 root root 29176 Feb 19 22:24 bgp_evpn_received_routes_report.py
    -rw-r--r-- 1 root root 51980 Feb 19 22:24 bgp_evpn_reports.py
    -rw-r--r-- 1 root root 89213 Feb 19 22:24 bgp_evpn_route_type_report.py
    -rw-r--r-- 1 root root 20324 Feb 19 22:24 bgp_ipv4_exact_route_detail_report.py
    -rw-r--r-- 1 root root 17562 Feb 19 22:24 bgp_ipv4_exact_route_report.py
    -rw-r--r-- 1 root root 20870 Feb 19 22:24 bgp_ipv4_labeled_unicast_exact_route_detail_report.py
    -rw-r--r-- 1 root root 17369 Feb 19 22:24 bgp_ipv4_labeled_unicast_exact_route_report.py
    -rw-r--r-- 1 root root 11645 Feb 19 22:24 bgp_ipv4_labeled_unicast_routes_summary_report.py
    -rw-r--r-- 1 root root 11575 Feb 19 22:24 bgp_ipv4_routes_summary_report.py
    -rw-r--r-- 1 root root 20336 Feb 19 22:24 bgp_ipv6_exact_route_detail_report.py
    -rw-r--r-- 1 root root 17299 Feb 19 22:24 bgp_ipv6_exact_route_report.py
    -rw-r--r-- 1 root root 20442 Feb 19 22:24 bgp_ipv6_labeled_unicast_exact_route_detail_report.py
    -rw-r--r-- 1 root root 17106 Feb 19 22:24 bgp_ipv6_labeled_unicast_exact_route_report.py
    -rw-r--r-- 1 root root 11223 Feb 19 22:24 bgp_ipv6_labeled_unicast_routes_summary_report.py
    -rw-r--r-- 1 root root 11169 Feb 19 22:24 bgp_ipv6_routes_summary_report.py
    -rw-r--r-- 1 root root 20843 Feb 19 22:24 bgp_l3vpn_ipv4_exact_route_detail_report.py
    -rw-r--r-- 1 root root 17773 Feb 19 22:24 bgp_l3vpn_ipv4_exact_route_report.py
    -rw-r--r-- 1 root root 11641 Feb 19 22:24 bgp_l3vpn_ipv4_routes_summary_report.py
    -rw-r--r-- 1 root root 20813 Feb 19 22:24 bgp_l3vpn_ipv6_exact_route_detail_report.py
    -rw-r--r-- 1 root root 17510 Feb 19 22:24 bgp_l3vpn_ipv6_exact_route_report.py
    -rw-r--r-- 1 root root 11641 Feb 19 22:24 bgp_l3vpn_ipv6_routes_summary_report.py
    -rw-r--r-- 1 root root 34051 Feb 19 22:24 bgp_neigh_advertised_routes_report.py
    -rw-r--r-- 1 root root 35283 Feb 19 22:24 bgp_neigh_received_routes_report.py
    -rw-r--r-- 1 root root 61888 Feb 19 22:24 bgp_neighbor_detail_report.py
    -rw-r--r-- 1 root root 15570 Feb 19 22:24 bgp_neighbor_summary_report.py
    -rw-r--r-- 1 root root 39579 Feb 19 22:24 bgp_reports_detail.py
    -rw-r--r-- 1 root root 41174 Feb 19 22:24 bgp_summary_report.py
    -rw-r--r-- 1 root root  5064 Feb 19 22:24 bgp_vpn_instance_report.py
    -rw-r--r-- 1 root root  7533 Feb 19 22:24 bridge_table_mac_duplication_report.py
    -rw-r--r-- 1 root root 23335 Feb 19 22:24 bridge_table_mac_table_report.py
    -rw-r--r-- 1 root root 22014 Feb 19 22:24 bridge_table_proxy_arp_report.py
    -rw-r--r-- 1 root root 22139 Feb 19 22:24 bridge_table_proxy_nd_report.py
    -rw-r--r-- 1 root root 10288 Feb 19 22:24 bridge_table_report.py
    -rw-r--r-- 1 root root 17095 Feb 19 22:24 control_component_report.py
    -rw-r--r-- 1 root root  1885 Feb 19 22:24 ethcfm_association_brief_report.py
    -rw-r--r-- 1 root root  3041 Feb 19 22:24 ethcfm_association_detail_report.py
    -rw-r--r-- 1 root root  3069 Feb 19 22:24 ethcfm_domain_association_detail_report.py
    -rw-r--r-- 1 root root  1621 Feb 19 22:24 ethcfm_domain_report.py
    -rw-r--r-- 1 root root  3109 Feb 19 22:24 ethcfm_mep_report.py
    -rw-r--r-- 1 root root  5506 Feb 19 22:24 ethcfm_report.py
    -rw-r--r-- 1 root root  2198 Feb 19 22:24 ethcfm_stacktable_report.py
    -rw-r--r-- 1 root root  5751 Feb 19 22:24 fabric_component_report.py
    -rw-r--r-- 1 root root  5201 Feb 19 22:24 fantray_component_report.py
    -rw-r--r-- 1 root root 10438 Feb 19 22:24 igmp_group_report.py
    -rw-r--r-- 1 root root  9323 Feb 19 22:24 igmp_interface_report.py
    -rw-r--r-- 1 root root  1762 Feb 19 22:24 igmp_reports.py
    -rw-r--r-- 1 root root  8800 Feb 19 22:24 igmp_snooping_evpn_proxy_membership_report.py
    -rw-r--r-- 1 root root 10443 Feb 19 22:24 igmp_snooping_group_report.py
    -rw-r--r-- 1 root root  7510 Feb 19 22:24 igmp_snooping_interface_report.py
    -rw-r--r-- 1 root root  8055 Feb 19 22:24 igmp_snooping_mrouter_report.py
    -rw-r--r-- 1 root root  8529 Feb 19 22:24 igmp_snooping_proxy_membership_report.py
    -rw-r--r-- 1 root root  2879 Feb 19 22:24 igmp_snooping_reports.py
    -rw-r--r-- 1 root root  7281 Feb 19 22:24 igmp_snooping_state_data.py
    -rw-r--r-- 1 root root 11361 Feb 19 22:24 igmp_snooping_statistics_report.py
    -rw-r--r-- 1 root root  6490 Feb 19 22:24 igmp_snooping_status_report.py
    -rw-r--r-- 1 root root  7237 Feb 19 22:24 igmp_snooping_vxlan_report.py
    -rw-r--r-- 1 root root  4750 Feb 19 22:24 igmp_state_data.py
    -rw-r--r-- 1 root root  9374 Feb 19 22:24 igmp_statistics_report.py
    -rw-r--r-- 1 root root  5373 Feb 19 22:24 igmp_status_report.py
    -rw-r--r-- 1 root root  2035 Feb 19 22:24 interface_brief_report.py
    -rw-r--r-- 1 root root 49821 Feb 19 22:24 interface_detail_report.py
    -rw-r--r-- 1 root root 18757 Feb 19 22:24 interface_queues.py
    -rw-r--r-- 1 root root  4251 Feb 19 22:24 interface_reports.py
    -rw-r--r-- 1 root root 14860 Feb 19 22:24 interface_summary_report.py
    -rw-r--r-- 1 root root 17378 Feb 19 22:24 isis_adjacency_report.py
    -rw-r--r-- 1 root root 44233 Feb 19 22:24 isis_database_report.py
    -rw-r--r-- 1 root root  6065 Feb 19 22:24 isis_hostname_report.py
    -rw-r--r-- 1 root root 26449 Feb 19 22:24 isis_interface_report.py
    -rw-r--r-- 1 root root  5333 Feb 19 22:24 isis_reports_detail.py
    -rw-r--r-- 1 root root 22255 Feb 19 22:24 isis_summary_report.py
    -rw-r--r-- 1 root root  3834 Feb 19 22:24 lag_brief_report.py
    -rw-r--r-- 1 root root 39285 Feb 19 22:24 lag_detail_report.py
    -rw-r--r-- 1 root root  5232 Feb 19 22:24 lag_lacp_state.py
    -rw-r--r-- 1 root root  4691 Feb 19 22:24 lag_lacp_stats.py
    -rw-r--r-- 1 root root  5428 Feb 19 22:24 lag_member_stats.py
    -rw-r--r-- 1 root root 19996 Feb 19 22:24 lag_queues.py
    -rw-r--r-- 1 root root  4480 Feb 19 22:24 lag_reports.py
    -rw-r--r-- 1 root root  5770 Feb 19 22:24 lag_summary_report.py
    -rw-r--r-- 1 root root 13792 Feb 19 22:24 ldp_address_report.py
    -rw-r--r-- 1 root root 25009 Feb 19 22:24 ldp_fec128_report.py
    -rw-r--r-- 1 root root 17290 Feb 19 22:24 ldp_fec_report.py
    -rw-r--r-- 1 root root  9343 Feb 19 22:24 ldp_info_requests.py
    -rw-r--r-- 1 root root 12758 Feb 19 22:24 ldp_interface_report.py
    -rw-r--r-- 1 root root  8267 Feb 19 22:24 ldp_neighbors_report.py
    -rw-r--r-- 1 root root  9391 Feb 19 22:24 ldp_nexthop_report.py
    -rw-r--r-- 1 root root  2860 Feb 19 22:24 ldp_reports.py
    -rw-r--r-- 1 root root 19344 Feb 19 22:24 ldp_session_report.py
    -rw-r--r-- 1 root root  8650 Feb 19 22:24 ldp_stats_report.py
    -rw-r--r-- 1 root root  7417 Feb 19 22:24 ldp_summary_report.py
    -rw-r--r-- 1 root root 17513 Feb 19 22:24 linecard_component_reports.py
    -rw-r--r-- 1 root root 10317 Feb 19 22:24 mld_group_report.py
    -rw-r--r-- 1 root root  9284 Feb 19 22:24 mld_interface_report.py
    -rw-r--r-- 1 root root  1744 Feb 19 22:24 mld_reports.py
    -rw-r--r-- 1 root root  8677 Feb 19 22:24 mld_snooping_evpn_proxy_membership_report.py
    -rw-r--r-- 1 root root 10313 Feb 19 22:24 mld_snooping_group_report.py
    -rw-r--r-- 1 root root  7472 Feb 19 22:24 mld_snooping_interface_report.py
    -rw-r--r-- 1 root root  7959 Feb 19 22:24 mld_snooping_mrouter_report.py
    -rw-r--r-- 1 root root  8489 Feb 19 22:24 mld_snooping_proxy_membership_report.py
    -rw-r--r-- 1 root root  2845 Feb 19 22:24 mld_snooping_reports.py
    -rw-r--r-- 1 root root  7249 Feb 19 22:24 mld_snooping_state_data.py
    -rw-r--r-- 1 root root 10951 Feb 19 22:24 mld_snooping_statistics_report.py
    -rw-r--r-- 1 root root  6406 Feb 19 22:24 mld_snooping_status_report.py
    -rw-r--r-- 1 root root  7203 Feb 19 22:24 mld_snooping_vxlan_report.py
    -rw-r--r-- 1 root root  4737 Feb 19 22:24 mld_state_data.py
    -rw-r--r-- 1 root root  9216 Feb 19 22:24 mld_statistics_report.py
    -rw-r--r-- 1 root root  5306 Feb 19 22:24 mld_status_report.py
    -rw-r--r-- 1 root root  8407 Feb 19 22:24 netinst_interfaces_report.py
    -rw-r--r-- 1 root root 13334 Feb 19 22:24 netinst_mfib_reports.py
    -rw-r--r-- 1 root root  1682 Feb 19 22:24 netinst_reports.py
    -rw-r--r-- 1 root root  2736 Feb 19 22:24 netinst_summary_report.py
    -rw-r--r-- 1 root root 33653 Feb 19 22:24 netinst_tunnel_reports.py
    -rw-r--r-- 1 root root  4310 Feb 19 22:24 netinst_vxlan_reports.py
    -rw-r--r-- 1 root root  4778 Feb 19 22:24 network_instance_interface_util.py
    -rw-r--r-- 1 root root 17948 Feb 19 22:24 next_hop_util.py
    -rw-r--r-- 1 root root 16132 Feb 19 22:24 ospf_area_report.py
    -rw-r--r-- 1 root root 28649 Feb 19 22:24 ospf_database_report.py
    -rw-r--r-- 1 root root 20812 Feb 19 22:24 ospf_interface_report.py
    -rw-r--r-- 1 root root 15481 Feb 19 22:24 ospf_neighbor_report.py
    -rw-r--r-- 1 root root  3008 Feb 19 22:24 ospf_reports_detail.py
    -rw-r--r-- 1 root root  8412 Feb 19 22:24 ospf_state_data.py
    -rw-r--r-- 1 root root 10544 Feb 19 22:24 ospf_statistics_report.py
    -rw-r--r-- 1 root root 13177 Feb 19 22:24 ospf_status_report.py
    -rw-r--r-- 1 root root 15127 Feb 19 22:24 pim_database_report.py
    -rw-r--r-- 1 root root 12636 Feb 19 22:24 pim_interface_report.py
    -rw-r--r-- 1 root root 11592 Feb 19 22:24 pim_neighbor_report.py
    -rw-r--r-- 1 root root  2097 Feb 19 22:24 pim_reports.py
    -rw-r--r-- 1 root root  5652 Feb 19 22:24 pim_state_data.py
    -rw-r--r-- 1 root root 20913 Feb 19 22:24 pim_statistics_report.py
    -rw-r--r-- 1 root root  8164 Feb 19 22:24 pim_status_report.py
    -rw-r--r-- 1 root root   838 Feb 19 22:24 platform_component_report.py
    -rw-r--r-- 1 root root  2989 Feb 19 22:24 platform_environment_report.py
    -rw-r--r-- 1 root root 12257 Feb 19 22:24 platform_reports.py
    -rw-r--r-- 1 root root 25344 Feb 19 22:24 platform_trust_report.py
    -rw-r--r-- 1 root root  6476 Feb 19 22:24 power_component_report.py
    -rw-r--r-- 1 root root  2968 Feb 19 22:24 redundancy_report.py
    -rw-r--r-- 1 root root  6092 Feb 19 22:24 resource_monitoring_report.py
    -rw-r--r-- 1 root root 23949 Feb 19 22:24 route_table_ip_routes_report.py
    -rw-r--r-- 1 root root 26549 Feb 19 22:24 route_table_ip_routes_summary.py
    -rw-r--r-- 1 root root  9947 Feb 19 22:24 route_table_mpls.py
    -rw-r--r-- 1 root root  4806 Feb 19 22:24 route_table_next_hop_report.py
    -rw-r--r-- 1 root root  6439 Feb 19 22:24 route_table_reports.py
    -rw-r--r-- 1 root root  2246 Feb 19 22:24 sath_reports.py
    -rw-r--r-- 1 root root 22558 Feb 19 22:24 sath_test_report.py
    -rw-r--r-- 1 root root  3108 Feb 19 22:24 sath_testslist_report.py
    -rw-r--r-- 1 root root 12441 Feb 19 22:24 static_mpls_entries_report.py
    -rw-r--r-- 1 root root   826 Feb 19 22:24 static_mpls_reports.py
    -rw-r--r-- 1 root root   569 Feb 19 22:24 system.py
    -rw-r--r-- 1 root root  4167 Feb 19 22:24 system_aaa_authentication_reports.py
    -rw-r--r-- 1 root root  3130 Feb 19 22:24 system_application_report.py
    -rw-r--r-- 1 root root  4583 Feb 19 22:24 system_lldp_reports.py
    -rw-r--r-- 1 root root  5954 Feb 19 22:24 system_logging.py
    -rw-r--r-- 1 root root 14056 Feb 19 22:24 system_network_instance_reports.py
    -rw-r--r-- 1 root root  5313 Feb 19 22:24 system_sflow_report.py
    -rw-r--r-- 1 root root 10596 Feb 19 22:24 tunnel_interface_detail_reports.py
    -rw-r--r-- 1 root root 24245 Feb 19 22:24 tunnel_interface_reports.py
    -rw-r--r-- 1 root root 12390 Feb 19 22:24 tunnel_vxlan_reports.py
    -rw-r--r-- 1 root root  6578 Feb 19 22:24 version.py
    admin@g15-leaf11:/opt/srlinux/python/virtual-env/lib/python3.11/dist-packages/srlinux/mgmt/cli/plugins/reports$ 
    ```
    ///

    You should be able to guess some commands from the file names, like `show bgp summary`, `show interface`, or `show system application`. All the SR linux show commands are implemented in this directory.  

    ///




5. Explore the `show version` file to see one of the simplest CLI show commands of the system. Can you find the file? 
In parallel, open a second terminal session side-by-side, and login to `leaf11` `sr-cli` shell, so that you can execute the CLI command and see the output while looking at the Python file:

    /// details | Solution: Native `show version` CLI plugins list
    The `show version` file is the version.py. 
    /// tab | Output - show version

    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# show version
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Hostname             : g15-leaf11
    Chassis Type         : 7220 IXR-D2L
    Part Number          : Sim Part No.
    Serial Number        : Sim Serial No.
    System HW MAC Address: 1A:41:0D:FF:00:00
    OS                   : SR Linux
    Software Version     : v24.10.3
    Build Number         : 201-g9d0e2b9371
    Architecture         : x86_64
    Last Booted          : 2025-03-31T15:58:31.303Z
    Total Memory         : 88503363 kB
    Free Memory          : 42164375 kB
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    --{ + running }--[  ]--
    A:g15-leaf11#
    ```
    ///
    /// tab | cmd

    ``` bash
    nl -ba version.py | more
    ```

    ///
    /// tab | version.py (full output - lines 1 to 156)

    ``` py linenums="1"
    import subprocess

    from srlinux.constants import OS_NAME
    from srlinux.data import TagValueFormatter, Border, Data
    from srlinux.location import build_path
    from srlinux.mgmt.cli import CliPlugin
    from srlinux.mgmt.server.server_error import ServerError
    from srlinux.schema import FixedSchemaRoot
    from srlinux.syntax import Syntax


    class Plugin(CliPlugin):

        '''
        Adds 'show version' command.

        Example output:

        Hostname          : DUT4
        Chassis Type      : 7250 IXR-10
        Part Number       : Sim Part No.
        Serial Number     : Sim Serial No.
        System MAC Address: 00:01:04:FF:00:00
        Software Version  : v0.0.0-12388-g1815c7e
        Architecture      : x86_64
        Last Booted       : 2019-09-12T17:34:42.865Z
        Total Memory      : 49292336 kB
        Free Memory       : 8780776 kB
        '''

        def load(self, cli, **_kwargs):
            cli.show_mode.add_command(
                Syntax('version', help='Show basic information of the system'), update_location=False, callback=self._print,
                schema=self._get_schema())

        def _print(self, state, output, arguments, **_kwargs):
            self._fetch_state(state)
            result = self._populate_data(state, arguments)
            self._set_formatters(result)
            output.print_data(result)

        def _get_schema(self):
            root = FixedSchemaRoot()
            root.add_child(
                'basic system info',
                fields=[
                    'Hostname',
                    'Chassis Type',
                    'Part Number',
                    'Serial Number',
                    'System HW MAC Address',
                    'OS',
                    'Software Version',
                    'Build Number',
                    'Beta',
                    'Architecture',
                    'Last Booted',
                    'Total Memory',
                    'Free Memory']
            )
            return root

        def _fetch_state(self, state):
            hostname_path = build_path('/system/name/host-name:')
            chassis_path = build_path('/platform/chassis')
            software_version_path = build_path('/system/app-management/application[name="idb_server"]')
            control_path = build_path('/platform/control[slot="*"]')

            try:
                self._hostname_data = state.server_data_store.get_data(hostname_path, recursive=True)
            except ServerError:
                self._hostname_data = None

            try:
                self._chassis_data = state.server_data_store.get_data(chassis_path, recursive=True)
            except ServerError:
                self._chassis_data = None

            try:
                self._software_version = state.server_data_store.get_data(software_version_path, recursive=True)
            except ServerError:
                self._software_version = None

            try:
                self._control_data = state.server_data_store.get_data(control_path, recursive=True)
            except ServerError:
                self._control_data = None

            self._beta = None # Ensures it won't be visible unless set
            try:
                cmd = ['sr_mgmt_server', '--version']
                info = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("UTF-8").strip()
                force_beta = info.find('FORCE_BETA') != -1
                if force_beta:
                    force_next_release = info.find('FORCE_NEXT_RELEASE') != -1
                    self._beta = 'B1' if force_next_release else 'B0'
            except subprocess.SubprocessError:
                pass

        def _populate_data(self, state, arguments):
            result = Data(arguments.schema)
            data = result.basic_system_info.create()

            data.hostname = '<Unknown>'
            if self._hostname_data:
                data.hostname = self._hostname_data.system.get().name.get().host_name or data.hostname

            data.chassis_type = '<Unknown>'
            data.part_number = '<Unknown>'
            data.serial_number = '<Unknown>'
            data.system_hw_mac_address = '<Unknown>'
            data.last_booted = '<Unknown>'
            if self._chassis_data:
                data.chassis_type = self._chassis_data.platform.get().chassis.get().type or data.chassis_type
                data.part_number = self._chassis_data.platform.get().chassis.get().part_number or data.part_number
                data.serial_number = self._chassis_data.platform.get().chassis.get().serial_number or data.serial_number
                data.system_hw_mac_address = self._chassis_data.platform.get().chassis.get().hw_mac_address \
                    or data.system_hw_mac_address
                data.last_booted = self._chassis_data.platform.get().chassis.get().last_booted or data.last_booted

            data.os = OS_NAME
            data.software_version = '<Unknown>'
            data.build_number = '<Unknown>'
            data.beta = self._beta
            if self._software_version:
                if self._software_version.system.get().app_management.get().application.exists('idb_server'):
                    sw_version = self._software_version.system.get().app_management.get().application.get('idb_server').version
                    if len(sw_version.strip()):
                        sw_version_strings = sw_version.split('-')
                        data.software_version = sw_version_strings[0]
                        if len(sw_version_strings) > 1:
                            data.build_number = '-'.join(sw_version_strings[1:])

            data.architecture = '<Unknown>'
            data.total_memory = '<Unknown>'
            data.free_memory = '<Unknown>'
            if self._control_data:
                for control_slot in ['A', 'B']:
                    if self._control_data.platform.get().control.exists(control_slot):
                        ctrl_data = self._control_data.platform.get().control.get(control_slot)
                        if state.system_features.chassis and not ctrl_data.role == 'active':
                            continue
                        if 'cpu' in ctrl_data.child_names:
                            if ctrl_data.cpu.exists('all'):
                                data.architecture = ctrl_data.cpu.get('all').architecture
                        if 'memory' in ctrl_data.child_names:
                            total_mem_value = ctrl_data.memory.get().physical
                            free_mem_value = ctrl_data.memory.get().free
                            if total_mem_value:
                                data.total_memory = (str(total_mem_value // 1024)) + ' kB'
                            if free_mem_value:
                                data.free_memory = (str(free_mem_value // 1024)) + ' kB'
            return result

        def _set_formatters(self, data):
            data.set_formatter('/basic system info', Border(TagValueFormatter(), Border.Above | Border.Below))
    ```
    ///
    ///



6. Examine the file `version.py`. Can you understand the code and the existing methods? Use the provided references, user guides or the explanation below if needed.



/// details | Detailed Explanation `version.py`
    type: success


1. Inspect the beginning of `version.py` (line 1 to 61). In a second terminal session, run the `show version` CLI command and compare the output with the schema object.


    /// tab | cmd
    ``` bash
    nl -ba version.py | more | sed -n '1,61p'
    ```
    ///

    /// tab | version.py (line 1 to 61)
    ```py title="version.py"  linenums="1"
    import subprocess

    from srlinux.constants import OS_NAME
    from srlinux.data import TagValueFormatter, Border, Data
    from srlinux.location import build_path
    from srlinux.mgmt.cli import CliPlugin
    from srlinux.mgmt.server.server_error import ServerError
    from srlinux.schema import FixedSchemaRoot
    from srlinux.syntax import Syntax


    class Plugin(CliPlugin):

        '''
        Adds 'show version' command.

        Example output:

        Hostname          : DUT4
        Chassis Type      : 7250 IXR-10
        Part Number       : Sim Part No.
        Serial Number     : Sim Serial No.
        System MAC Address: 00:01:04:FF:00:00
        Software Version  : v0.0.0-12388-g1815c7e
        Architecture      : x86_64
        Last Booted       : 2019-09-12T17:34:42.865Z
        Total Memory      : 49292336 kB
        Free Memory       : 8780776 kB
        '''

        def load(self, cli, **_kwargs):
            cli.show_mode.add_command(
                Syntax('version', help='Show basic information of the system'), update_location=False, callback=self._print,
                schema=self._get_schema())

        def _print(self, state, output, arguments, **_kwargs):
            self._fetch_state(state)
            result = self._populate_data(state, arguments)
            self._set_formatters(result)
            output.print_data(result)

        def _get_schema(self):
            root = FixedSchemaRoot()
            root.add_child(
                'basic system info',
                fields=[
                    'Hostname',
                    'Chassis Type',
                    'Part Number',
                    'Serial Number',
                    'System HW MAC Address',
                    'OS',
                    'Software Version',
                    'Build Number',
                    'Beta',
                    'Architecture',
                    'Last Booted',
                    'Total Memory',
                    'Free Memory']
            )
            return root
    ```
    ///


    /// tab | show version
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# show version
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Hostname             : g15-leaf11
    Chassis Type         : 7220 IXR-D2L
    Part Number          : Sim Part No.
    Serial Number        : Sim Serial No.
    System HW MAC Address: 1A:41:0D:FF:00:00
    OS                   : SR Linux
    Software Version     : v24.10.3
    Build Number         : 201-g9d0e2b9371
    Architecture         : x86_64
    Last Booted          : 2025-03-31T15:58:31.303Z
    Total Memory         : 88503363 kB
    Free Memory          : 42164375 kB
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    --{ + running }--[  ]--
    A:g15-leaf11#
    ```
    ///


    In the beginning of `version.py` you find:  

    -  the import statements  (line 1 to 9)

    -  the `Plugin(CliPlugin)` class  (line 12 to 29)

    -  the `load()` method that defines the CLI command syntax (line 31 to 34)

    -  the `_print` method that provides the output of the `show version` (line 36 to 40)

    -   the `_get_schema` method  that builds the schema(line 42 to 61)



    Few notes regarding the code:  

    *  the CLI command is appended to the CLI command tree using `cli.show_mode.add_command()` to append the CLI command under the `show` branch. (line 32)  

    *  the syntax definition is done directly in the `add_command()` method. This is the same as first creating a syntax object and then using it as a parameter.  (line 33)  

    *  there's a callback `method_print()` which is executed when the `show version` command is entered by a CLI user.  (line 33)  

    *  there is a schema object that is passed to the `add_command()` method using the `_get_schema()`. This is specific to show commands.  (line 34)  

    *  the `_get_schema()` method builds a schema consisting of one node called `basic system info` that has multiple fields (`hostname`,`chassis type`, etc). (line 42 to 61)  

    *  the schema object is a placeholder for the data to be displayed by the command.  


    When the callback function is executed it:  

    *  retrieves relevant data in the state datastore with `_fetch_state()`.  (line 37)  

    *  populates the retrieved data into the schema object with `_populate_data()`.  (line 38)  

    *  specifies how the retrieved data should be formatted on the screen with `_set_formatters()`.  (line 39)  

    *  instruct SR Linux to display the retrieved data by calling the `print_data()` method of the output object.  (line 40)   





2. Look at the code for the _fetch_state method:

    /// tab | cmd
    ``` bash
    nl -ba version.py | more | sed -n '63,98p'
    ```
    ///

    /// tab | version.py (line 63 to 98)
    ```py title="version.py"  linenums="63"
    def _fetch_state(self, state):
        hostname_path = build_path('/system/name/host-name:')
        chassis_path = build_path('/platform/chassis')
        software_version_path = build_path('/system/app-management/application[name="idb_server"]')
        control_path = build_path('/platform/control[slot="*"]')

        try:
            self._hostname_data = state.server_data_store.get_data(hostname_path, recursive=True)
        except ServerError:
            self._hostname_data = None

        try:
            self._chassis_data = state.server_data_store.get_data(chassis_path, recursive=True)
        except ServerError:
            self._chassis_data = None

        try:
            self._software_version = state.server_data_store.get_data(software_version_path, recursive=True)
        except ServerError:
            self._software_version = None

        try:
            self._control_data = state.server_data_store.get_data(control_path, recursive=True)
        except ServerError:
            self._control_data = None

        self._beta = None # Ensures it won't be visible unless set
        try:
            cmd = ['sr_mgmt_server', '--version']
            info = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("UTF-8").strip()
            force_beta = info.find('FORCE_BETA') != -1
            if force_beta:
                force_next_release = info.find('FORCE_NEXT_RELEASE') != -1
                self._beta = 'B1' if force_next_release else 'B0'
        except subprocess.SubprocessError:
            pass
    ```
    ///


    /// tab | show version
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# show version
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Hostname             : g15-leaf11
    Chassis Type         : 7220 IXR-D2L
    Part Number          : Sim Part No.
    Serial Number        : Sim Serial No.
    System HW MAC Address: 1A:41:0D:FF:00:00
    OS                   : SR Linux
    Software Version     : v24.10.3
    Build Number         : 201-g9d0e2b9371
    Architecture         : x86_64
    Last Booted          : 2025-03-31T15:58:31.303Z
    Total Memory         : 88503363 kB
    Free Memory          : 42164375 kB
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    --{ + running }--[  ]--
    A:g15-leaf11#
    ```
    ///


    Few notes regarding the code:  

    *  Lines 64 to 67 set 4 different xpaths into the state datastore 

    *  The following lines retrieve the values associated with the 4 xpaths and store them in local data objects (_hostname_data, _chassis_data, _software_version and _control_data)

    *  You can get the same information using the CLI `info from state` command. The xpath strings using the notation with `/` must be translated into the YANG model hierarchy. For example, `/system/name/host-name` is translated into the YANG elements `system name host-name`.  


3. Run the `info from state` commands in your CLI session. 


    /// tab | `info from state`
    ``` bash
    info from state system name host-name
    info from state platform chassis
    info from state system app-management application idb_server
    ```
    ///

    /// tab | hostname
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# info from state system name host-name
        system {
            name {
                host-name g15-leaf11
            }
        }

    --{ + running }--[  ]--
    A:g15-leaf11#
    ```
    ///

    /// tab | platform chassis
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# info from state platform chassis
        platform {
            chassis {
                type "7220 IXR-D2L"
                last-boot-type normal
                hw-mac-address 1A:41:0D:FF:00:00
                slots 1
                oper-state up
                last-booted "2025-03-31T15:58:31.303Z (10 days ago)"
                last-change "2025-03-31T15:58:31.303Z (10 days ago)"
                part-number "Sim Part No."
                removable false
                clei-code "Sim CLEI"
                serial-number "Sim Serial No."
                environment {
                    orientation horizontal
                }
                power {
                    total {
                    }
                }
                healthz {
                    status healthy
                }
            }
        }

    --{ + running }--[  ]--
    A:g15-leaf11#
    ```
    ///

    /// tab | application idb_server
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# info from state system app-management application idb_server
        system {
            app-management {
                application idb_server {
                    pid 2058
                    state running
                    last-change "2025-03-31T15:58:31.274Z (10 days ago)"
                    last-start-type cold
                    author Nokia
                    failure-threshold 3
                    failure-window 300
                    failure-action reboot
                    path /opt/srlinux/bin
                    launch-command ./sr_idb_server
                    search-command ./sr_idb_server
                    version v24.10.3-201-g9d0e2b9371
                    oom-score-adj 0
                    restricted-operations [
                        start
                        stop
                        restart
                        quit
                        kill
                        reload
                    ]
                    statistics {
                        restart-count 0
                    }
                    yang {
                    }
                }
            }
        }

    --{ + running }--[  ]--
    A:g15-leaf11#
    ```
    ///




4. The `_populate_data()` method parses the info returned from the state datastore to extract the relevant information and then assigns a value to each of the fields of the schema.  
The `_set_formatters()` method specifies how the schema should be displayed. It uses the formatter function `TagValueFormatter()` to display each field in the schema as a tag/value pair, one per row. It also specifies that there should be a border above and a border below.


    /// tab | cmd
    ``` bash
    nl -ba version.py | more | sed -n '100,153p'
    ```
    ///

    /// tab | _populate_data() (line 100 to 153)
    ```py title="_populate_data"  linenums="100"
    def _populate_data(self, state, arguments):
        result = Data(arguments.schema)
        data = result.basic_system_info.create()

        data.hostname = '<Unknown>'
        if self._hostname_data:
            data.hostname = self._hostname_data.system.get().name.get().host_name or data.hostname

        data.chassis_type = '<Unknown>'
        data.part_number = '<Unknown>'
        data.serial_number = '<Unknown>'
        data.system_hw_mac_address = '<Unknown>'
        data.last_booted = '<Unknown>'
        if self._chassis_data:
            data.chassis_type = self._chassis_data.platform.get().chassis.get().type or data.chassis_type
            data.part_number = self._chassis_data.platform.get().chassis.get().part_number or data.part_number
            data.serial_number = self._chassis_data.platform.get().chassis.get().serial_number or data.serial_number
            data.system_hw_mac_address = self._chassis_data.platform.get().chassis.get().hw_mac_address \
                or data.system_hw_mac_address
            data.last_booted = self._chassis_data.platform.get().chassis.get().last_booted or data.last_booted

        data.os = OS_NAME
        data.software_version = '<Unknown>'
        data.build_number = '<Unknown>'
        data.beta = self._beta
        if self._software_version:
            if self._software_version.system.get().app_management.get().application.exists('idb_server'):
                sw_version = self._software_version.system.get().app_management.get().application.get('idb_server').version
                if len(sw_version.strip()):
                    sw_version_strings = sw_version.split('-')
                    data.software_version = sw_version_strings[0]
                    if len(sw_version_strings) > 1:
                        data.build_number = '-'.join(sw_version_strings[1:])

        data.architecture = '<Unknown>'
        data.total_memory = '<Unknown>'
        data.free_memory = '<Unknown>'
        if self._control_data:
            for control_slot in ['A', 'B']:
                if self._control_data.platform.get().control.exists(control_slot):
                    ctrl_data = self._control_data.platform.get().control.get(control_slot)
                    if state.system_features.chassis and not ctrl_data.role == 'active':
                        continue
                    if 'cpu' in ctrl_data.child_names:
                        if ctrl_data.cpu.exists('all'):
                            data.architecture = ctrl_data.cpu.get('all').architecture
                    if 'memory' in ctrl_data.child_names:
                        total_mem_value = ctrl_data.memory.get().physical
                        free_mem_value = ctrl_data.memory.get().free
                        if total_mem_value:
                            data.total_memory = (str(total_mem_value // 1024)) + ' kB'
                        if free_mem_value:
                            data.free_memory = (str(free_mem_value // 1024)) + ' kB'
        return result
    ```
    ///


    /// tab | cmd
    ``` bash
    nl -ba version.py | more | sed -n '155,156p'
    ```
    ///

    /// tab | `_set_formatters()` (line 155 to 156)

    ```py title="_populate_data"  linenums="155"
    def _set_formatters(self, data):
        data.set_formatter('/basic system info', Border(TagValueFormatter(), Border.Above | Border.Below))
    ```
    ///


5. You may compare the output of the `show version` command with the differente fields of the schema.  
You can see that the different fields from the schema are displayed line by line. The system has automatically adjusted the width of the columns to the widest field and there is a border above and below all the fiels. Note that you can change the number of columns for your CLI session and SR linux automatically calculates how wide the borders need to be. 
When implementing a show command, the focus is on the schema definition rather that on the output formatting. Once the schema values are filled in, SR Linux can automatically format the output.



    > **Note 1:** It is possible to use the `as json` modifier for the show commands to display the output in JSON notation instead of displaying as text. If you compare with the python code, you can see that it's the schema definition that is being displayed. 

    > **Note 2:** The SR Linux containes several classes and utility functions. The formatters and format utilities allows to customize the outputs look-and-feel. E.g. you have the `show version | as table` that displays the output in a table format. You can achieve the same by using the `ColumnFormatter()` instead of the `TagValueFormatter()` in your code.



    /// tab | show version
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# show version
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Hostname             : g15-leaf11
    Chassis Type         : 7220 IXR-D2L
    Part Number          : Sim Part No.
    Serial Number        : Sim Serial No.
    System HW MAC Address: 1A:41:0D:FF:00:00
    OS                   : SR Linux
    Software Version     : v24.10.3
    Build Number         : 201-g9d0e2b9371
    Architecture         : x86_64
    Last Booted          : 2025-03-31T15:58:31.303Z
    Total Memory         : 88503363 kB
    Free Memory          : 42164375 kB
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    --{ + running }--[  ]--
    A:g15-leaf11#
    ```
    ///

    /// tab | show version | as json
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# show version | as json
    {
    "basic system info": {
        "Hostname": "g15-leaf11",
        "Chassis Type": "7220 IXR-D2L",
        "Part Number": "Sim Part No.",
        "Serial Number": "Sim Serial No.",
        "System HW MAC Address": "1A:41:0D:FF:00:00",
        "OS": "SR Linux",
        "Software Version": "v24.10.3",
        "Build Number": "201-g9d0e2b9371",
        "Architecture": "x86_64",
        "Last Booted": "2025-03-31T15:58:31.303Z",
        "Total Memory": "88503363 kB",
        "Free Memory": "44018316 kB"
    }
    }

    --{ + running }--[  ]--
    A:g15-leaf11#
    ```
    ///

    /// tab | show version | as table

    ```bash
    --{ + running }--[  ]--
    A:g15-leaf11# show version | as table
    +-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+
    |  Hostname   |   Chassis   | Part Number |   Serial    |  System HW  |     OS      |  Software   |    Build    |    Beta     | Architectur | Last Booted |    Total    | Free Memory |
    |             |    Type     |             |   Number    | MAC Address |             |   Version   |   Number    |             |      e      |             |   Memory    |             |
    +=============+=============+=============+=============+=============+=============+=============+=============+=============+=============+=============+=============+=============+
    | g15-leaf11  | 7220        | Sim Part    | Sim Serial  | 1A:41:0D:FF | SR Linux    | v24.10.3    | 201-        |             | x86_64      | 2025-03-    | 88503363 kB | 40952687 kB |
    |             | IXR-D2L     | No.         | No.         | :00:00      |             |             | g9d0e2b9371 |             |             | 31T15:58:31 |             |             |
    |             |             |             |             |             |             |             |             |             |             | .303Z       |             |             |
    +-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+-------------+

    --{ + running }--[  ]--
    ```
    ///

    /// tab | ColumnFormatter

    ```py title="Using ColumnFormatter instead of TagValueFormatter"  
    from srlinux.data import TagValueFormatter, Border, Data, ColumnFormatter
    def _set_formatters(self, data):
        data.set_formatter('/basic system info', Border(ColumnFormatter(), Border.Above | Border.Below))
    ```
    ///


    > **Tip:** When writing a show command plugin, it is recommended that you first focus on retrieving the data to be displayed (defining and filling in the schema values). You can then test if all values have been properly retrieved and assigned using the `as json` output modifier. Then you can consider the exact formatting of the output.



///



**Now let's proceed and create a plugin!!**


### Create modified `show version` custom CLI

You now understand the SR Linux plugin architecture and you have explored the native CLI plugins. So you decide to create a modified version of the `show version` plugin.  

In this section you'll create a new plugin using an existing native `show version` plugin as reference and apply custom modifications.  
Using an existing native command, duplicate and modify it to adapt to your purpose is a relatively easy way to create a new plugin.  

At the start of a CLI session, SR linux scans the following directories to check for new CLI plugins: 

*  `/home/<user>/cli/plugins`: a plugin in this directory is usable only for this user  

*  `/etc/opt/srlinux/cli/plugins`: a plugin in this directory is usable for all users  
  

In this exercise you'll use the `show version` command file to create a new custom CLI show command.

1. Copy the Python source file `show version` to the 2nd directory listed above and rename it to version_srx.py.

    /// tab | cp version.py to version_srx.py
    ``` bash
    cd /etc/opt/srlinux/cli/plugins
    cp /opt/srlinux/python/virtual-env/lib/python3.11/dist-packages/srlinux/mgmt/cli/plugins/reports/version.py version_srx.py
    ```
    ///

    ///warning
    Don't forget to check and adjust the folder permissions with `chmod` if needed. 
    ///

    /// note

    If you prefer to use VSCode, we suggest you to add the server home folder to you workspace (`~/` or `/home/nokia/`).  
    The `~/clab-srexperts/leaf11/config/cli/plugins` is bound to the `leaf11's` `/etc/opt/srlinux/cli/plugins` folder.  
    As such, you may edit the `~/clab-srexperts/leaf11/config/cli/plugins/version_srx.py` directly from VSCode.  

    ///

2. Edit the version_srx.py and change the `load()` method Syntax string and help text. 


    /// tab | version_srx.py syntax
    ``` py hl_lines="3"
    def load(self, cli, **_kwargs):
        cli.show_mode.add_command(
            Syntax('version_srexperts', help='SReXperts - Custom show version CLI Plugin'), update_location=False, callback=self._print,
            schema=self._get_schema())
    ```
    ///




3. You can now test the new CLI command. To load the new CLI command the CLI session must be restarted. You can logout/login or open a new `sr_cli` session.
Then you can use the new CLI command. 


    /// tab | version_srx.py cmd
    ``` bash
    show version_srexperts
    ```
    ///

    /// tab | version_srx.py syntax and help
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# show <TAB>
                        /                   interface           platform            tunnel-interface   
                        acl                 lag                 system              version            
                        arpnd               network-instance    tunnel              version_srexperts  



    --{ + running }--[  ]--
    A:g15-leaf11# show version<TAB>
                            version            
                            version_srexperts  



    --{ + running }--[  ]--
    A:g15-leaf11# show version_srexperts ?
    usage: version_srexperts

    SReXperts - Custom show version CLI Plugin

    *** Not all commands are listed, press '?' again to see all options ***

    ```
    ///

    /// tab | version_srx.py output
    ``` bash
    --{ + running }--[  ]--
    A:g15-leaf11# show version_srexperts


    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    Hostname             : g15-leaf11
    Chassis Type         : 7220 IXR-D2L
    Part Number          : Sim Part No.
    Serial Number        : Sim Serial No.
    System HW MAC Address: 1A:41:0D:FF:00:00
    OS                   : SR Linux
    Software Version     : v24.10.3
    Build Number         : 201-g9d0e2b9371
    Architecture         : x86_64
    Last Booted          : 2025-03-31T15:58:31.303Z
    Total Memory         : 88503363 kB
    Free Memory          : 43055351 kB
    --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    --{ + running }--[  ]--
    ```
    ///


    > **Tip:** You can use `show <TAB>` and the `show version_srexperts ?` to verify the syntax and options available.

What has changed in the output compared to the native plugin output? 

/// details | Answer
    type: success
The output of the new CLI command is the same as the `show version` as we didn't change anything. 
    
**Let's do it now!**  
///

#### Add extra fields to your command  

You task is to add an extra field to the output to display the current time as shown below.  



/// tab | version_srx.py current_time output
``` bash hl_lines="4"
--{ + running }--[  ]--
A:g15-leaf11# show version_srexperts
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Current Time         : 2025-04-11 17:25:53.626118
Hostname             : g15-leaf11
Chassis Type         : 7220 IXR-D2L
Part Number          : Sim Part No.
Serial Number        : Sim Serial No.
System HW MAC Address: 1A:41:0D:FF:00:00
OS                   : SR Linux
Software Version     : v24.10.3
Build Number         : 201-g9d0e2b9371
Architecture         : x86_64
Last Booted          : 2025-03-31T15:58:31.303Z
Total Memory         : 88503363 kB
Free Memory          : 43477910 kB
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--{ + running }--[  ]--
A:g15-leaf11#
```
///



/// details | Tip
    type: tip

There are multiple ways to achieve the solution, you can you use the python datetime module or retrieve this value from system information current-datetime state datastore.  
These are the steps using the python datetime module:  

1. Add an extra filed `Current time` to the schema.
2. Import the `datetime` module
3. Update the `_populate_data()` method.
4. Reload the plugin.

And these are the steps using system information current-datetime state datastore:  

1. Add an extra filed `Current time` to the schema.
2. Retrieve the current-datetime at `_fetch_state()` method 
3. Update the `_populate_data()` method.
4. Reload the plugin.


///


/// details | Solution: Add extra fields to your command
    type: success

These are the steps using the python datetime module:

  1. Edit the version_srx.py and add an extra filed `Current time` as shown below:
  2. Import the datetime module
  3. Update the `_populate_data()` method with the value of the new field to the current time.
  4. Reload the plugin

    /// tab | version_srx.py Current time
    ``` py hl_lines="7"
    --{ + running }--[  ]--
    def _get_schema(self):
        root = FixedSchemaRoot()
        root.add_child(
            'basic system info',
            fields=[
                'Current time',
                'Hostname',
                'Chassis Type',
                'Part Number',
                'Serial Number',
                'System HW MAC Address',
                'OS',
                'Software Version',
                'Build Number',
                'Beta',
                'Architecture',
                'Last Booted',
                'Total Memory',
                'Free Memory']
        )
        return root
    ```
    ///

    /// tab | `import datetime`
    ``` py
    from datetime import datetime
    ```
    ///

    /// tab | `_populate_data` `current_time` 
    ``` py hl_lines="5"
    def _populate_data(self, state, arguments):
        result = Data(arguments.schema)
        data = result.basic_system_info.create()

        data.current_time = str(datetime.now())

        data.hostname = '<Unknown>'
    ```
    ///

    > **Note:** Although the extra fields in the schema is defined as `Current Time`, its actual name in the schema structure becomes `current_time`. The name is converted to lower case and the space character is replaced by an underscore to avoid Python miss interpretations. The same occurs for the `'-' (dash)` character in the field name, it is replaced by the underscore.  



And these are the steps using system information current-datetime state datastore:

1. Add an extra filed `Current time` to the schema.
2. Retrieve the `current-datetime` at `_fetch_state()` method 
3. Update the `_populate_data()` method.
4. Reload the plugin.


    /// tab | `version_srx.py` Current time
    ``` py hl_lines="7"
    --{ + running }--[  ]--
    def _get_schema(self):
        root = FixedSchemaRoot()
        root.add_child(
            'basic system info',
            fields=[
                'Current time',
                'Hostname',
                'Chassis Type',
                'Part Number',
                'Serial Number',
                'System HW MAC Address',
                'OS',
                'Software Version',
                'Build Number',
                'Beta',
                'Architecture',
                'Last Booted',
                'Total Memory',
                'Free Memory']
        )
        return root
    ```
    ///

    /// tab | import datetime
    ``` py
    def _fetch_state(self, state):
        
        current_time_path = build_path('/system/information/current-datetime')
        try:
            self._current_time_data = state.server_data_store.get_data(current_time_path, recursive=False)
        except ServerError:
            self._current_time_data = None
    ```
    ///

    /// tab | _populate_data current_time 
    ``` py hl_lines="5"
    def _populate_data(self, state, arguments):

        data.current_time = (self._current_time_data.system.get().information.get().current_datetime)
    ```
    ///


You can now test the changes. Logout/login or open a new `sr_cli` session and execute the command again.  
Then you can use the new CLI command. 


/// tab | version_srx.py 
``` bash
show version_srexperts
```
///

/// tab | version_srx.py current_time output
``` bash hl_lines="4"
--{ + running }--[  ]--
A:g15-leaf11# show version_srexperts
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Current Time         : 2025-04-11 17:25:53.626118
Hostname             : g15-leaf11
Chassis Type         : 7220 IXR-D2L
Part Number          : Sim Part No.
Serial Number        : Sim Serial No.
System HW MAC Address: 1A:41:0D:FF:00:00
OS                   : SR Linux
Software Version     : v24.10.3
Build Number         : 201-g9d0e2b9371
Architecture         : x86_64
Last Booted          : 2025-03-31T15:58:31.303Z
Total Memory         : 88503363 kB
Free Memory          : 43477910 kB
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--{ + running }--[  ]--
A:g15-leaf11#
```
///



The current time is now displayed along with the output. This also shows that the source of information for the show command can be anything and not just a value extracted from the datastore.

///




#### Change the output format

You next task is to change the CLI command to display the output in a table format as shown below.  


/// tab | version_srx.py column format
``` bash
--{ + running }--[  ]--
A:g15-leaf11# show version_srexperts
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
+----------------------------+------------+--------------+--------------+----------------+-----------------------+----------+------------------+-----------------+------+--------------+--------------------------+--------------+-------------+
|        Current Time        |  Hostname  | Chassis Type | Part Number  | Serial Number  | System HW MAC Address |    OS    | Software Version |  Build Number   | Beta | Architecture |       Last Booted        | Total Memory | Free Memory |
+============================+============+==============+==============+================+=======================+==========+==================+=================+======+==============+==========================+==============+=============+
| 2025-04-11 17:36:04.680324 | g15-leaf11 | 7220 IXR-D2L | Sim Part No. | Sim Serial No. | 1A:41:0D:FF:00:00     | SR Linux | v24.10.3         | 201-g9d0e2b9371 |      | x86_64       | 2025-03-31T15:58:31.303Z | 88503363 kB  | 43677085 kB |
+----------------------------+------------+--------------+--------------+----------------+-----------------------+----------+------------------+-----------------+------+--------------+--------------------------+--------------+-------------+
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

```
///


You may refer to [SR Linux Classes and utility functions](https://documentation.nokia.com/srlinux/24-10/books/cli-plugin/classes-utility-functions.html) for guidance.


/// details | Tip
    type: tip
  
You just need to perform two small changes:  

1. You need to import the `ColumnFormatter` module from `srlinux.data`.
2. You need to edit the `_set_formaters()` method at the end of the `version_srx.py`

///




/// details | Solution: Change the output format to table
    type: success

Import the ColumnFormatter module
``` py
from srlinux.data import TagValueFormatter, Border, Data, ColumnFormatter
```

Edit the `_set_formaters()` method to use `ColumnFormatter()` instead ot `TagValueFormatter()`
``` py hl_lines="2"
def _set_formatters(self, data):
    data.set_formatter('/basic system info', Border(ColumnFormatter(), Border.Above | Border.Below))
```

///



And with these changes you create a modified version of a native plugin as a custom plugin.  
Are you ready now to create you own plugin from scratch? 


### Create `show traffic` custom CLI  

In this section you will create a new CLI command from scratch and step-by-step.  

The request is to create a `show traffic` plugin that displays an overview of the chassis traffic.  
The output shall include:  

 - a table with the input/output rates and utilization percentages per port (only for those admin-enabled).
 - the aggregate input and output for the chassis

The intended output is shown below: 

```title="show traffic"
--{ + running }--[  ]--
A:g15-leaf11# show traffic
+---------------------+--------+------------------------------------+------------------------------------+------------------------------------+
|        port         | speed  |            description             |               input                |               output               |
+=====================+========+====================================+====================================+====================================+
| mgmt0               | 1G     |                                    | 0.0% (14.33 Kbps)                  | 0.0% (265.67 Kbps)                 |
| ethernet-1/1        | 25G    | gnmi-test                          | 0.0% (0 bps)                       | 0.0% (153 bps)                     |
| ethernet-1/2        | 25G    | leaf12-client12                    | 0.0% (989 bps)                     | 0.0% (1.15 Kbps)                   |
| ethernet-1/49       | 100G   | leaf11-spine11                     | 0.0% (420 bps)                     | 0.0% (438 bps)                     |
| ethernet-1/50       | 100G   | leaf11-spine12                     | 0.0% (0 bps)                       | 0.0% (157 bps)                     |
+---------------------+--------+------------------------------------+------------------------------------+------------------------------------+
Total rate-in : 15.74 Kbps
Total rate-out: 267.57 Kbps
-------------------------------------------------------------------------------------------------------------------------------------------------
```


/// admonition 
    type: question
Is there another way to get this without a CLI plugin?   
///

/// details | Answer
    type: tip
  

You can use the command below but it doesn't give you the percentage or the total values and its not flexible.
/// tab | `from state / interface * traffic-rate`
``` bash
info from state / interface * traffic-rate | filter fields in-bps out-bps | as table
```
///
/// tab | Output
``` bash
--{ + running }--[  ]--
A:g15-leaf11# info from state / interface * traffic-rate | filter fields in-bps out-bps | as table
+---------------------+----------------------+----------------------+
|      Interface      |        In-bps        |       Out-bps        |
+=====================+======================+======================+
| ethernet-1/1        |                    0 |                  153 |
| ethernet-1/2        |                  990 |                 1148 |
| ethernet-1/3        |                      |                      |
| ethernet-1/4        |                      |                      |
| ethernet-1/5        |                      |                      |
| ethernet-1/6        |                      |                      |
| ethernet-1/7        |                      |                      |
| ethernet-1/8        |                      |                      |
| ethernet-1/9        |                      |                      |
| ethernet-1/10       |                      |                      |
| ethernet-1/11       |                      |                      |
| ethernet-1/12       |                      |                      |
| ethernet-1/13       |                      |                      |
| ethernet-1/14       |                      |                      |
| ethernet-1/15       |                      |                      |
| ethernet-1/16       |                      |                      |
| ethernet-1/17       |                      |                      |
| ethernet-1/18       |                      |                      |
| ethernet-1/19       |                      |                      |
| ethernet-1/20       |                      |                      |
| ethernet-1/21       |                      |                      |
| ethernet-1/22       |                      |                      |
| ethernet-1/23       |                      |                      |
| ethernet-1/24       |                      |                      |
| ethernet-1/25       |                      |                      |
| ethernet-1/26       |                      |                      |
| ethernet-1/27       |                      |                      |
| ethernet-1/28       |                      |                      |
| ethernet-1/29       |                      |                      |
| ethernet-1/30       |                      |                      |
| ethernet-1/31       |                      |                      |
| ethernet-1/32       |                      |                      |
| ethernet-1/33       |                      |                      |
| ethernet-1/34       |                      |                      |
| ethernet-1/35       |                      |                      |
| ethernet-1/36       |                      |                      |
| ethernet-1/37       |                      |                      |
| ethernet-1/38       |                      |                      |
| ethernet-1/39       |                      |                      |
| ethernet-1/40       |                      |                      |
| ethernet-1/41       |                      |                      |
| ethernet-1/42       |                      |                      |
| ethernet-1/43       |                      |                      |
| ethernet-1/44       |                      |                      |
| ethernet-1/45       |                      |                      |
| ethernet-1/46       |                      |                      |
| ethernet-1/47       |                      |                      |
| ethernet-1/48       |                      |                      |
| ethernet-1/49       |                  558 |                  439 |
| ethernet-1/50       |                  137 |                  158 |
| ethernet-1/51       |                      |                      |
| ethernet-1/52       |                      |                      |
| ethernet-1/53       |                      |                      |
| ethernet-1/54       |                      |                      |
| ethernet-1/55       |                      |                      |
| ethernet-1/56       |                      |                      |
| ethernet-1/57       |                      |                      |
| ethernet-1/58       |                      |                      |
| irb0                |                      |                      |
| lag1                |                  990 |                 1148 |
| mgmt0               |                14399 |               264282 |
| system0             |                      |                      |
+---------------------+----------------------+----------------------+

--{ + running }--[  ]--
A:g15-leaf11#
```
///


///

To create the new plugin you will follow these steps:  

1.  Create the `show_traffic.py` file  
2.  Define the import statements, the Plugin class and load method  
3.  Define the CLI command syntax  
4.  Define the schema  
5.  Callback  
    - Fetching state  
    - Populating data  
    - Adding formatters  
    - Printing output  
6. Test your new plugin

///note
The SR Linux CLI needs to be restarted to load new code changes made on CLI plugins. To avoid log-out and log-in often during your development, switch to SR Linux bash shell and run `sr_cli show traffic`. This implicitly executes a new SR Linux CLI instance before executing `show traffic`. 
///

#### Create the `show_traffic.py` file
Recall that at the start of a CLI session, SR linux scans the following directories to check for new CLI plugins: 

*  `/home/<user>/cli/plugins`: a plugin in this directory is usable only foth this user  

*  `/etc/opt/srlinux/cli/plugins`: a plugin in this directory is usable for all users  

Your first step is to deploy the `show_traffic.py` plugin under one of these folders. We suggest you to use VSCode to create the file. If you need guidance, have a look to the tip below. Then proceed to the following sections for guidance to deploy the plugin. 

/// details | Tip: Create the plugin file 
    type: tip
Create the plugin file using one of the following options:   


   - A) Using VSCode, create the file `show_traffic.py` under the server `~/clab-srexperts/leaf11/config/cli/plugins` folder. There's a bind between this directory and the leaf11's plugins folder, so if you create the file under this folder it will be automatically mapped to `leaf11`. After the file is created verify that it is present under leaf11's `/etc/opt/srlinux/cli/plugins/` folder.

/// tab | Server plugin directory
``` bash
cd ~/clab-srexperts/leaf11/config/cli/plugins
touch show_traffic.py
```
///
/// tab | Leaf11 plugin directory
``` bash
admin@g15-leaf11:~$ ls -al /etc/opt/srlinux/cli/plugins/
total 32
drwxrwxrwx+ 2 srlinux srlinux 4096 Apr 15 10:23 .
drwxrwxrwx+ 3 srlinux srlinux 4096 Mar 31 15:58 ..
-rw-r--r--  1 root    root    4603 Apr 15 10:19 show_traffic.py
admin@g15-leaf11:~$ 
```
///

  - B) As an alternative, e.g. if you prefer to use `vi` directly in the node, move to the cli plugin directory and create the `show_traffic.py` file.

/// tab | create the show_traffic.py file
``` bash
cd /etc/opt/srlinux/cli/plugins
touch show_traffic.py
```
///

> **Note:** You can copy/paste code directly to `vi`, howhever, to keep your indentation you need to enable paste mode (Esc + `:set paste`) then move to insertation mode and paste your code. 
///

#### Define the import statements, the Plugin class and load() method 

You need to import packages that are going to be required in the plugin. 
The plugin needs to have a class called Plugin that inherits from the CliPlugin with a `load` public method. The SR Linux CLI engine scans the user directories and loads all the plugins that match this signature.  

The `load` method of the Plugin class is the entry point for the CLI plugin. It is where you add your new CLI command to one of the CLI modes - `show`, `global` or `tools`.
Since we want to create a `show traffic` command, we are going to "mount" our command to the show hierarchy.  

The `add_command` method of the CLI mode receives the command definition arguments such as:  

- syntax - how the command is structured syntactically  
- schema - what schema defines the data that the command operates on  
- callback - what function to call when the command is executed  

///details | Hint
    type: tip
Copy the structure from the `show version` plugin or the github [uptime-cli-plugin](https://github.com/srl-labs/uptime-cli-plugin) and leave the details unimplemented for now using python `pass` command.
 > **Note:** The `_syntax()`, `_schema()` and `_print` methods will be covered in the following sections.
///

/// details | Start code: `import`, class `Plugin` and `load()` method
    type: success
``` py 
from srlinux.data import Border, Data, TagValueFormatter, ColumnFormatter
from srlinux.location import build_path
from srlinux.mgmt.cli import CliPlugin
from srlinux.mgmt.server.server_error import ServerError
from srlinux.schema import FixedSchemaRoot
from srlinux.syntax import Syntax

class Plugin(CliPlugin):
    def load(self, cli, arguments):
        cli.show_mode.add_command(
            syntax=self._syntax(),
            schema=self._schema(),
            callback=self._print,
        )
    def _syntax(self):
        pass
    def _schema(self):
        pass
    def _print(self):
        pass
```
///

#### Define the CLI command syntax 
The command's syntax defines the command representation - its name, help strings and the arguments it accepts. 
To define a command syntax, we need to create an object of the Syntax class; this is what the `_syntax()` method does.  

For our `show traffic` command we just define the command name and the help text in different flavors in the `_syntax()` object.

/// details | possible solution: CLI syntax
    type: success
``` py 
    def _syntax(self):
        return Syntax(
            name="traffic",
            short_help="Show real-time traffic rates and utilization across chassis",
            help="Show real-time traffic rates and utilization percentages for all enabled ports, plus total aggregate input/output rates for the chassis."
        )
```
///

#### Define the schema  
You might be wondering, what is a schema and why do we need it for such a simple thing as a CLI command?  
For a given show command the schema describes the data that the command intends to print out. As per our intent, the `show traffic` command should print out two things: 

 - a table with the input/output rates and utilization percentages per admin-enabled port.
 - the aggregate input/output rate for the chassis.

But, still, why do we need a schema to print values? Can't we just use print the values?  
The answer is that a schema makes it possible to have multiple output formats without implementing the logic for each of them. In SR Linux we can display the output using distinct output modifiers such as: default tag/value, table, json, yaml or xml.  
Without having a schema-modeled data structure, we would have to implement the logic for each of the output formats ourselves.

/// admonition 
    type: question
- You already know how the schema looks like for a fixed list of `key:value` pairs like in `show version` plugin. But how it would look like for a list table with a dynamic number of rows? 
///
///details | Hint
    type: tip
Check how it is done on a native plugin such as `show interface brief`.   [Recall](#__tabbed_3_2) where you can find the native plugin files for `show` reports.
///
///details | Hint
    type: tip
You might add multiple children to the schema. 

For example, you could create one to hold the ports data, and other to hold the chassis aggregate rate data. This would allow you to set different formatters and different data structures to each.
///

/// details | possible solution: schema
    type: success
``` py 
    def _schema(self):
        root = FixedSchemaRoot()
        root.add_child(
            'port',
            key='port',
            fields=[
                'speed',
                'description',
                'input',
                'output',
                ]
        )
        root.add_child(
            'chassis',
            fields = ['Total rate-in','Total rate-out']
        )
        return root
```
///
#### _print() Callback - Fetching state, Populating data, adding formatters and printing output

We described the syntax of the `show traffic` command and defined the schema for the data it operates on. The final task is to create the callback function - the one that gets called when the command is executed and does all the useful work.  
We provide the callback function as the second argument to the add_command method and it is up to us how we call it. Most often the show commands will have the callback function named _print, as show commands print out some data to the output.  

///tip 
From example native scripts such as `show version`, start by writing the high level `_print()` method and leave the called methods unimplemented for now.
///

/// details | possible solution: Callback skeleton code
    type: success
``` py 
def _print(self, state, arguments, output, **_kwargs):
        data = self._fetch_state(state)
        result = self._populate_data(data)
        self._set_formatters(result)
        output.print_data(result)

    def _fetch_state(self, state):
        pass
    
    def _populate_data(self, fetched_data):
        pass
    
    def _set_formatters(self, data):
        pass
```
///

#### Fetching state
Complete the `_fetch_state()` method. This is where you collect the data from `state` datastore that you will later manipulate to extract the ports and associated traffic-rate
/// admonition | Stop and take time to think here
    type: question
 - Which interfaces represent the ports?
 - Is there a YANG path that contains the traffic-rate information?
 - Which YANG path provide information about if a port is administratively enabled?
 - Which other piece of information you need to be able to calculate the utilization % of each port? 
///


///details | Hint: Ports
    type: tip
The ports are represented by the interface names `mgmt0` and all `ethernet-*`. other interfaces such as `irb`, `system`, `lag*` interfaces are virtual.
///
///details | Hint: YANG Paths
    type: tip
- `/interface[name=*]/traffic-rate`
- `/interface[name=*]/admin-state`
- `/interface[name=*]/ethernet/port-speed`
///
///details | Hint: Fetch path
    type: tip
Recursively fetching `/interface[name={mgmt0,ethernet-*}]` will include all the required data from all physical ports at once (the mgmt port + all inband ports). Fetching different paths separately into different variables would be also ok too.
///
///details | `stream_data` vs `get_data`
You will probably notice that some native plugins fetch state data using `stream_data` instead of `get_data`.
See [Using streaming to optimize reports](https://documentation.nokia.com/srlinux/25-3/books/cli-plugin/show-routines.html#use-stream-to-optimize-reports) for more details
///

#### Populating data
After data is collected from `state` you need to extract the relevant bits, and fill that in a `Data` object structured as per the `schema` you defined.

Complete the `_populate_state()` method
///details | Hint: high level steps
    type: tip
1. Create a `Data` object based on the schema.
2. Create temporary variables that will hold the sum of traffic-rates.
3. Loop through the collected interface data, create the port objects as you go, fill them with data.
4. Create the object that holds the aggregate rates and fill it.
5. Return the `Data` object
///

///details | Hint: how to create `Data` object
    type: tip
The `Data` object is created using `result = Data(self._schema())`
///
///details | Hint: calculating the port utilization
    type: tip
To calculate the port utilization percentage you can transform the `port-speed` to `bps` and divide `traffic-rate`(which is already in `bps` unit) by it:
///details | code
```py
port_speed_units = port.speed[-1]
port_speed_value = int(port.speed[:-1])
if port_speed_units == 'G':
    multiplier = 10**9
elif port_speed_units == 'T':
    multiplier = 10**12
elif port_speed_units == 'M':
    multiplier = 10**6
port_speed_bps = int(port_speed_value) * multiplier
percent = (traffic_rate_in_bps/port_speed_bps)*100
```
///
///

#### Adding formatters
What left is to set the formatters on the resulting `Data` object so that is printed according to your preference.  
Complete `_set_formatters()` method.

If you followed a similar schema to the one provided at beginning of the exercise, then your `Data` object has 2 children:

- One holds the ports data, which is dynamic and each port is identified by a key.
- The other holds the chassis aggregate rate information.

You can use different formatters for each.

/// admonition 
    type: question
- What would be the appropriate formatter for each child?
///

///details | Hint
    type: tip
Experiment with the `TagValueFormatter` and `ColumnFormatter`
///

#### Printing
After `Data` object is formatted, it just needs to be passed to the `output.print_data()` method. This was already done when defining the `_print()` callback

#### Test your new plugin
Logout/login or open a new session to the CLI on `leaf11`.

///tip
Optionally start some traffic between the clients. Run this from your group's Hackaton VM to start traffic from `client11` to `client13`:
```
sudo docker exec clab-srexperts-client11 /traffic.sh -a start -d client13.vprn.dci
```
///

You can now try `show <TAB>` or `show ?` to see the new `traffic` option and the help hints.
Finnally execute the `show traffic` to confirm the correct output of the new plugin.

/// tab | `show traffic`
``` bash
A:g15-leaf11# show traffic
+---------------------+--------+------------------------------------+------------------------------------+------------------------------------+
|        port         | speed  |            description             |               input                |               output               |
+=====================+========+====================================+====================================+====================================+
| mgmt0               | 1G     |                                    | 0.0% (11.32 Kbps)                  | 0.0% (261.43 Kbps)                 |
| ethernet-1/1        | 25G    | gnmi-test                          | 0.0% (0 bps)                       | 0.0% (0 bps)                       |
| ethernet-1/2        | 25G    | leaf12-client12                    | 0.0% (990 bps)                     | 0.0% (990 bps)                     |
| ethernet-1/49       | 100G   | leaf11-spine11                     | 0.0% (0 bps)                       | 0.0% (0 bps)                       |
| ethernet-1/50       | 100G   | leaf11-spine12                     | 0.0% (226 bps)                     | 0.0% (83 bps)                      |
+---------------------+--------+------------------------------------+------------------------------------+------------------------------------+
Total rate-in : 12.53 Kbps
Total rate-out: 262.5 Kbps
------------------------------------------------------------------------------------------------------------------------------------------------
```
///

/// tab | `show traffic help`
``` bash hl_lines="15 24-27"
A:g15-leaf11# show
usage: show

Show the show report of the current context

Local commands:
  /                 Moves you to the root
  acl
  arpnd
  interface         Show interface report
  lag               Show LAG report
  network-instance
  platform          Show platform environment
  system            Top-level container for system information
  traffic           Show real-time traffic rates and utilization across chassis
  tunnel
  tunnel-interface
  version           Show basic information of the system

*** Not all commands are listed, press '?' again to see all options ***

--{ + running }--[  ]--
A:g15-leaf11# show traffic
usage: traffic

Show real-time traffic rates and utilization percentages for all enabled ports, plus total aggregate input/output rates for the chassis.

*** Not all commands are listed, press '?' again to see all options ***

```
///

And that's it, you  create a custom CLI plugin!

You can find the full solution file below case you have any issue or you want to check it against yours.
///details | Possible solution: `show_traffic.py`
    type: success
``` py
#!/usr/bin/python
from srlinux.data import Border, Data, TagValueFormatter, ColumnFormatter
from srlinux.location import build_path
from srlinux.mgmt.cli import CliPlugin
from srlinux.mgmt.server.server_error import ServerError
from srlinux.schema import FixedSchemaRoot
from srlinux.syntax import Syntax

def bps2text(bps):
    '''transform bps units to a friendly text string'''
    current_value=bps
    current_unit='bps'
    units = ['Kbps','Mbps','Gbps']
    #convert units automatically
    while current_value > 999 and units:
        current_unit = units.pop(0)
        current_value = round(current_value/1000,2)
    return f"{current_value} {current_unit}"

class Plugin(CliPlugin):
    def load(self, cli, **_kwargs):
        cli.show_mode.add_command(
            syntax=self._syntax(),
            callback=self._print,
            schema=self._schema())
    
    def _syntax(self):
        return Syntax(
            name="traffic",
            short_help="Show real-time traffic rates and utilization across chassis",
            help="Show real-time traffic rates and utilization percentages for all enabled ports, plus total aggregate input/output rates for the chassis."
        )

    def _schema(self):
        root = FixedSchemaRoot()
        root.add_child(
            'port',
            key='port',
            fields=[
                'speed',
                'description',
                'input',
                'output',
                ]
        )
        root.add_child(
            'chassis',
            fields = ['Total rate-in','Total rate-out']
        )
        return root

    def _print(self, state, arguments, output, **_kwargs):
        data = self._fetch_state(state)
        result = self._populate_data(data)
        self._set_formatters(result)
        output.print_data(result)

    def _fetch_state(self, state):
        path = build_path('/interface[name={mgmt0,ethernet-*}]')
        return state.server_data_store.get_data(path, recursive=True)
    
    def _populate_data(self, fetched_data):
        result = Data(self._schema())
        total_in_bps = 0
        total_out_bps = 0
        for interface in fetched_data.interface.items():
            if interface.admin_state == "disable":
                continue
            port = result.port.create(interface.name)
            port.speed = interface.ethernet.get().port_speed
            port.description = interface.description

            port_speed_units = port.speed[-1]
            port_speed_value = int(port.speed[:-1])
            if port_speed_units == 'G':
                multiplier = 10**9
            elif port_speed_units == 'T':
                multiplier = 10**12
            elif port_speed_units == 'M':
                multiplier = 10**6
            port_speed_bps = int(port_speed_value) * multiplier

            traffic_rate = interface.traffic_rate.get()
            traffic_rate_in_bps = traffic_rate.in_bps
            traffic_rate_out_bps = traffic_rate.out_bps
            port.input = f"{round((traffic_rate_in_bps/port_speed_bps)*100,2)}% ({bps2text(traffic_rate_in_bps)})"
            port.output = f"{round((traffic_rate_out_bps/port_speed_bps)*100,2)}% ({bps2text(traffic_rate_out_bps)})"

            total_in_bps+=traffic_rate_in_bps
            total_out_bps+=traffic_rate_out_bps

        #chassis total
        total = result.chassis.create()
        total.total_rate_in=bps2text(total_in_bps)
        total.total_rate_out=bps2text(total_out_bps)

        return result
    
    def _set_formatters(self, data):
        data.set_formatter('/port', ColumnFormatter(widths={'Port': 19,'speed':6,'util-in':10,'util-out':10}))
        data.set_formatter('/chassis', Border(TagValueFormatter(), Border.Below))
```
///

## Summary and review

Congratulations! If you have got this far you have completed this activity and achieved the following:  

- Explored the native plugins folders, files and code.  
- Created a modified custom plugin based on the `show version` native plugin.  
- Created the `show traffic` CLI plugin that prints the interface and system traffic rate and added it to the CLI as if it was a built-in command.

The CLI Plugin infrastructure allows you to create commands that make operational sense for your network, whenever you want them and without any vendor involvement. It provides the full visibility into the system and makes it easy to get the data with all the output formats SR Linux supports - text, table, json, yaml, xml, etc.

The `show traffic` its just an example, you can explore existing show commands to have an idea of what it takes to create a more complex and feature rich commands. The custom CLI plugins use the same plugin infrastructure as SR Linux's native commands, and use the state engine to query the state of the system.

We hope you find this information useful and that you liked the activity.
Now we invite you to try another amazing Hackathon activity.


