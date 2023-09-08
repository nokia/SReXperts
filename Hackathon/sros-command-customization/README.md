# Using Python to customize commands in SROS

In this lab, we demonstrate the basics to interact with SR OS devices through pySROS. The pySROS libraries provide a model-driven management interface for Python developers to integrate with supported Nokia routers. pySROS programs can be executed on the router itself using a local Python interpreter, as well as remotely using NETCONF. In both cases the programs produce the same results.

**Grading: beginner**

## Lab Diagram

![SROS command customization lab diagram](./srx-clab.png)

## Deploying the lab

```
sudo containerlab deploy -t srx.clab.yaml
```

## Tools needed

Visual Studio Code: to view/edit the python script (you don't run this file!)

## Credentials section

To access the devices, ssh to the IP or host-name with the credentials in the table below

* sros1:            Default SR OS username and password
* sros2:            Default SR OS username and password

Example:

```
ssh admin@clab-srx-sros1
```

## Connecting to a project from your laptop
Each public cloud instance has a port-range (50000 - 51000) exposed towards the Internet, as lab nodes spin up, a public port is dynamically allocated by the docker daemon on the public cloud instance.
You can utilize those to access the lab services straight from your laptop via the Internet.

With the `show-ports` command executed on a VM you get a list of mappings between external and internal ports allocated for each node of a lab. Consider the following example:
```
~$ show-ports
Name           Forwarded Ports
clab-srx-sros1  50149 -> 22, 50148 -> 830
clab-srx-sros2  50147 -> 22, 50146 -> 830
```
Each service exposed on a lab node gets a unique external port number as per the table above.
In the given case, sros1's SSHD is available on port 50149 of the VM, this is mapped to the container's port 22.

Optional:
> You can generate `ssh-config` using the `generate-ssh-config` command and store the output on your local laptop's SSH client, in order to connect directly to nodes.

## Tasks

### Task 1

The first task is to solve a common problem where the column width of an SR OS show command output is too small, resulting in a truncated output. One command where this truncation might happen is the SR OS show command that displays the LLDP neighbor list.

Consider the following SR OS show command for LLDP neighbors:

```
[/]
A:admin@srx-hackathon-sros1-23.7.R1# show system lldp neighbor
Link Layer Discovery Protocol (LLDP) System Information

===============================================================================
NB = nearest-bridge   NTPMR = nearest-non-tpmr   NC = nearest-customer
===============================================================================
Lcl Port      Scope Remote Chassis ID  Index  Remote Port     Remote Sys Name
-------------------------------------------------------------------------------
1/1/c1/1      NB    52:54:00:7C:D3:00  1      1/1/c1/1        srx-hackathon-w*
===============================================================================
* indicates that the corresponding row element may have been truncated.
Number of neighbors : 1
```

In the above example, the "Remote Sys Name" column values are truncated. In this first task the goal is to make a python script that we can call where the column widths are dynamically set based on data found in the router's state information.

An example lldp_neighbor.py script is found in the scripts folder. This script is available on the SR OS nodes at tftp://172.31.255.29/lldp_neighbor.py.

As a result you get the following output:

```
[/]
A:admin@srx-hackathon-sros1-23.7.R1# pyexec tftp://172.31.255.29/lldp_neighbor.py
======================================================================================================================
NB = nearest-bridge   NTPMR = nearest-non-tpmr   NC = nearest-customer  EMOJIs : 😀 💩 🤠
======================================================================================================================
Lcl Port      Scope Remote Chassis ID  Index  Remote Port                                  Remote Sys Name
1/1/c1/1      NB    52:54:00:7C:D3:00  1      1/1/c1/1, 100-Gig Ethernet, "port 1/1/c1/1"  srx-hackathon-sros2-23.7.R1
======================================================================================================================
Number of neighbors : 1
```

#### More details on the script:
A pySROS script must set up a connection to a device before it can perform any interactions with the device. The generally accepted way of establishing a connection uses a get_connection function, so this script implements one.

A translating dictionary is added to include abbreviations of LLDP types in their equivalent "Scope" column notation. A print_table function is implemented that uses the data provided to it to determine how wide each of the columns should be, respecting the minimum width required to still properly show the column headers. Some code is included here that shows how to change the color of text in the output and how to include emojis.

The last function implemented is named lldp_check with a helper function find_lldp_ports. The helper function checks the router's configuration to find those ports that might have LLDP neighbors. Connector ports (1/1/c1) would not be expected to have LLDP information associated with them, for example. Any port that has LLDP configured is added to a dictionary to be checked; this dictionary is returned by the helper.

Based on information available in the state model and entries in this dictionary, lldp_check finds the data that feeds into the function call to print_table. In the main function, this is all tied together to produce the final result.

### Task 2

In the second task we will create an alias for this script so it can be used as if it's a default SR OS CLI command.

First configure a python script on the NE:

```
edit-config private
    configure {
        python {
            python-script "lldp-neighbor-enhanced" {
                admin-state enable
                urls ["tftp://172.31.255.29/lldp_neighbor.py"]
                version python3
            }
        }
    }
```

Now, create a command alias referencing the python script and defining the CLI mount point from which it should be accessible:

```
configure {
    system {
        management-interface {
            cli {
                md-cli {
                    environment {
                        command-alias {
                            alias "lldp-neighbor-enhanced" {
                                admin-state enable
                                python-script "lldp-neighbor-enhanced"
                                mount-point "/show" { }
                            }
                        }
                    }
                }
            }
        }
    }
}
```



Commit these changes to the NE and make sure to logout and log back in to the NE before executing the show command:
```
commit
logout
```
As a result you should be able to execute the new show command:

```
[/]
A:admin@srx-hackathon-sros1-23.7.R1# show lldp-neighbor-enhanced
======================================================================================================================
NB = nearest-bridge   NTPMR = nearest-non-tpmr   NC = nearest-customer  EMOJIs : 😀 💩 🤠
======================================================================================================================
Lcl Port      Scope Remote Chassis ID  Index  Remote Port                                  Remote Sys Name
1/1/c1/1      NB    52:54:00:7C:D3:00  1      1/1/c1/1, 100-Gig Ethernet, "port 1/1/c1/1"  srx-hackathon-sros2-23.7.R1
======================================================================================================================
Number of neighbors : 1
```
*Enhancement: Can you make it so that the command "show system lldp neighbor" from the first task yields the untruncated output?*

### Task 3

In the third task we explore possibilities of taking the script we have now seen working as both an executed script on the router and as a command alias to off-box execution. To run it, create an environment where you could execute the script on your local machine or on your assigned VM. Copy the script there, edit the call to get_connection so that one of your lab nodes is targeted and execute it. The output should be the same as the end-result of the earlier two tasks.

**Note: the first time you run the python3 command, it can take a while until all required files are downloaded from the node (up to about 3 minutes)**

```
$ python3 scripts/lldp_neighbor.py
======================================================================================================================
NB = nearest-bridge   NTPMR = nearest-non-tpmr   NC = nearest-customer  EMOJIs : 😀 💩 🤠
======================================================================================================================
Lcl Port      Scope Remote Chassis ID  Index  Remote Port                                  Remote Sys Name
1/1/c1/1      NB    0C:00:88:EE:66:00  1      1/1/c1/1, 100-Gig Ethernet, "port 1/1/c1/1"  srx-hackathon-sros2-23.7.R1
======================================================================================================================
```

How is the script interacting with the node now?

## Destroying the lab

When you have completed this scenario and don't want to continue playing with the setup, it can be destroyed by issuing the following command:

```
sudo containerlab destroy --cleanup
```
