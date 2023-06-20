# SR OS Event Handling Scripts

Inside this lab are two use-cases that can be addressed using Nokia SROS' event handling system (EHS) combined with pySROS.
These use-cases demonstrate how you can use pySROS on the router itself to let it handle situations automatically - without any outside intervention.

This could be useful for triaging problems automatically or for doing some repetitive sequential tasks automatically.

**Grading: Advanced**

**Elements: SR OS, pySROS**

## Drawing


![topo](./_images/sros-pysros-eh.png)

## High level tasks to complete this project

1. Connect to the tester1 and tester2 nodes, ensure generic.website is reachable.
2. Use the delivered tool `scripts/bgp_toggle.py` to shut down the interfaces towards the route reflectors
*This tool itself is written using pySROS*
3. Create a pySROS script that selectively disables the affected sros node's interfaces towards its tester.
4. To further demonstrate, and to avoid the same issue reoccurring in future, add another route reflector. The configuration required to do this is provided below.
5. With a CPM filter configured to only allow traffic from select IP addresses for specific protocols, these filters have to be updated as well. This can be tedious and error-prone. Use EHS and pySROS to create a script that will automatically add the BGP peer to the CPM-filter match-list whenever a BGP peer is added to the configuration so we have one less thing to worry about.

## Deploying the lab

From the labs directory enter the following command to run the lab.

```
sudo containerlab deploy
```

This can take around 5 minutes to completely bring up all SROS devices with associated routing.
*Note: It is always advisable to do all development in a non-`root` user.  `containerlab` requires `root` to run though so use `sudo` as in the example above for the `deploy` and `destroy` arguments*

## Tools needed  

| Role | Software |
| --- | --- |
| Router | SR OS release 23.3.R1 |
| Alpine Linux with nginx | small-scale traffic tester |


## Tool explanation

All tasks for the lab use-case can be completed on the provided nodes. The goal of this lab is to solve some tasks by writing code. Through container binds the nodes need only be made aware of the changes via the provided `tools` command. For the intended solution, required coding is limited to the sros1 and sros2 nodes (though feel free to experiment).

## Credentials and access

* sros1:            Default SR OS username and password
* sros2:            Default SR OS username and password
* tester1:          Default Alpine Linux username and password (root:alpine)
* tester2:          Default Alpine Linux username and password (root:alpine)
* server1:          Default Alpine Linux username and password (root:alpine)
* helper1:          Default SR OS username and password
* internet_rr1:     Default SR OS username and password
* internet_rr2:     Default SR OS username and password
* internet_rr3:     Default SR OS username and password

If you wish to have direct external access from your machine, use the public IP address of the VM and the external port numbers as per the table below:

| Node          | Software |  Direct SSH (Ext.)      | NETCONF (Ext.) | 
| -----         | ---------| ---------------------- | -------------- | 
| sros1         |  SR OS release 23.3.R1 |`ssh admin@IP:59001`   | `IP:59401`     |
| sros2         |  SR OS release 23.3.R1 |`ssh admin@IP:59002`   | `IP:59402`     |
| tester1       | Linux |`ssh admin@IP:59003`   | /     |
| tester2       | Linux   |`ssh admin@IP:59004`   | /     |
| server1       | Linux (nginx) |`ssh root@IP:59005`    | /     |
| helper1       | SR OS release 23.3.R1 |`ssh root@IP:59006`    | `IP:59406`     |
| internet_rr1  | SR OS release 23.3.R1 |`ssh admin@IP:59007`   | `IP:59407`     |
| internet_rr2  | SR OS release 23.3.R1 |`ssh admin@IP:59008`   | `IP:59408`     |
| internet_rr3  | SR OS release 23.3.R1 |`ssh admin@IP:59009`   | `IP:59409`     |

sros-eh.rc and sros-eh.remote.rc are included in the lab. The former can be used on the hackathon VM when working there, the latter can be used on your local machine to access the network after populating the public IP address of the VM. Simply source the desired file to load the aliases.

## Reference documentation

* [pySROS documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest)
* [EHS-specifics](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.ehs)
* [pySROS repo](https://github.com/nokia/pysros)
* [SR OS documentation](https://documentation.nokia.com/sr/)


## Tasks
* **Connect to the tester1 and tester2 nodes, ensure generic.website is reachable.**
    Ensure your access works. Issue a `wget generic.website` to ensure the topology is working correctly and traffic reaches through the sros and helper nodes before starting.
    If this traffic works, the BGP peerings between sros1, sros2 and the route reflectors are working.

* **Use the delivered tool `scripts/bgp_toggle.py` to shut down the interfaces towards the route reflectors**
    *This tool itself is written using pySROS and can take "up" or "down" as a parameter. As a default, "down" is used. When run from the hackathon VM this script will work as-is. When running it from your local machine, ensure the hostname of the helper node is set appropriately using the port mapping table shown above.*
    Previously mentioned BGP peerings go down, traffic that was working before is stopped. Repeating the action on the tester gives a vague error indicating the website has become unreachable.
    **NOTE: when executing this script for the first time, the script may take several minutes to complete as it is fetching the entire data model**

* **Create a pySROS script that selectively disables the affected sros node's interfaces towards its tester.**
    A file is expected in the topology scripts/ folder. The name configured on the router is `opergroup_bgp_sros.py`. Any Python code written in this file will be executed by the router after issuing the command
    `tools perform python python-script reload opergroup_bgp_sros`
    Configuration has been prepared such that any change in BGP peerings will lead to this script being executed. To give a concrete example, for sros1, this would be the interface tester1. 

    *Enhancement: If you wish to go a step further you can expand the script to re-enable the disabled interfaces whenever a route-reflector session is re-established.*

* **To further demonstrate, and to avoid the same issue reoccurring in future, add another route reflector to sros1 and sros2. The configuration required to do this is**
    ```
        configure {
            router "Base" {
                bgp {
                    neighbor "192.168.0.3" {
                        group "rr"
                    }
                }
            }
        }
    ```
    Does the session come up? What could be missing?

* **With a CPM filter configured to only allow traffic from select IP addresses for specific protocols, these filters have to be updated as well. This can be tedious and error-prone. Use EHS and pySROS to create a script that will automatically add any and all BGP peers to a prefix list to be used in the CPM-filter. This script should be run whenever a BGP peer is added to the configuration so we have one less thing to worry about.**
    Create a script that will automatically apply the required changes to a BGP ACL such that the previously configured peer would have come up correctly. For this case, code is expected in `prefix_list_ehs.py`. The tools command to reload the code is now `tools perform python python-script reload prefix_list_ehs`. You could modify the existing bgp_peers match_list. For this document a new match-list named "ehs_controlled_bgp_peers" is assumed. To apply this new match-list, required configuration is:
    ```
        system {
            security {
                cpm-filter {
                    ip-filter {
                        entry 200 {
                            match {
                                src-ip {
    -                               ip-prefix-list "bgp_peers"
    +                               ip-prefix-list "ehs_controlled_bgp_peers"
                                }
                            }
                        }
                        entry 210 {
                            match {
                                dst-ip {
    -                               ip-prefix-list "bgp_peers"
    +                               ip-prefix-list "ehs_controlled_bgp_peers"
                                }
                            }
                        }
                    }
                }
            }
        }
    ```
    *Enhancement: Can your program handle NTP and other protocols in a similar way?*
