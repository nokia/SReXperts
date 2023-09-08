# Remote correlation of information from multiple SR OS devices

Addressing this use-case will empower you to create a remote (off-box) pySROS application that obtains data from various SR OS devices and presents it in a useful way.

**Grading: Beginner / Intermediate**

**Elements: SR OS, pySROS**

## Lab diagram

![topo](./_images/topology-overview.png)


## High level tasks to complete this project

Write a pySROS application to be executed remotely (on your workstation or in the SReXperts instance) to:

1. Read in topology information from a containerlab deployed topology information file and identify router nodes of interest.
2. Connect to all devices and obtain various data elements.
3. Correlate the data together in a meaningful format and print it out using the SR OS table format.

## Deploying the lab

From the labs directory enter the following command to run the lab.

```
sudo containerlab deploy
```

*Note: It is always advisable to do all development in a non-`root` user.  `containerlab` requires `root` to run though so use `sudo` as in the example above for the `deploy` and `destroy` arguments*

## Tools needed  

| Role | Software |
| --- | --- |
| Router | SR OS release 23.7.R1 |


## Tool explanation

All tasks for the lab use-case can be completed using SR OS and Python code developed and tested on your local workstation or on the SReXperts instance server.

*Note: The containerlab topology file will be created on the SReXperts instance server when you create the lab, to use this locally you will need to take a copy of it.  Please note that this file will changes each time the lab is deployed.*

### Credentials & Access
#### Accessing the lab from within the VM
To access the lab nodes from within the VM, users should identify the names of the deployed nodes using the `sudo containerlab inspect` command:

```
sudo containerlab inspect
INFO[0000] Parsing & checking topology file: sros-pysros-device-correlation.clab.yml
+----+-----------------------------------------+--------------+------------------------------------+---------------+---------+------------------+----------------------+
| #  |                  Name                   | Container ID |               Image                |     Kind      |  State  |   IPv4 Address   |     IPv6 Address     |
+----+-----------------------------------------+--------------+------------------------------------+---------------+---------+------------------+----------------------+
|  1 | clab-sros-pysros-device-correlation-ce1 | 95f0589c3bb2 | vr-sros:23.7.R1                    | vr-nokia_sros | running | 172.20.20.211/24 | 2001:172:20:20::7/64 |
|  2 | clab-sros-pysros-device-correlation-ce2 | 7c77fb81d85c | vr-sros:23.7.R1                    | vr-nokia_sros | running | 172.20.20.212/24 | 2001:172:20:20::4/64 |
|  3 | clab-sros-pysros-device-correlation-ce3 | 96c706e423f3 | vr-sros:23.7.R1                    | vr-nokia_sros | running | 172.20.20.213/24 | 2001:172:20:20::5/64 |
|  4 | clab-sros-pysros-device-correlation-ce4 | 9e4837545726 | vr-sros:23.7.R1                    | vr-nokia_sros | running | 172.20.20.214/24 | 2001:172:20:20::9/64 |
|  5 | clab-sros-pysros-device-correlation-pe1 | 899009334c2a | vr-sros:23.7.R1                    | vr-nokia_sros | running | 172.20.20.201/24 | 2001:172:20:20::8/64 |
|  6 | clab-sros-pysros-device-correlation-pe2 | 3f5ffff951e4 | vr-sros:23.7.R1                    | vr-nokia_sros | running | 172.20.20.202/24 | 2001:172:20:20::3/64 |
|  7 | clab-sros-pysros-device-correlation-pe3 | 96723f8af960 | vr-sros:23.7.R1                    | vr-nokia_sros | running | 172.20.20.203/24 | 2001:172:20:20::6/64 |
|  8 | clab-sros-pysros-device-correlation-pe4 | 933343ea5df0 | vr-sros:23.7.R1                    | vr-nokia_sros | running | 172.20.20.204/24 | 2001:172:20:20::a/64 |
|  9 | clab-sros-pysros-device-correlation-rs1 | 8ae9896af53b | ghcr.io/srl-labs/network-multitool | linux         | running | 172.20.20.4/24   | 2001:172:20:20::d/64 |
| 10 | clab-sros-pysros-device-correlation-tg1 | b379b8af76ad | ghcr.io/srl-labs/network-multitool | linux         | running | 172.20.20.2/24   | 2001:172:20:20::b/64 |
| 11 | clab-sros-pysros-device-correlation-tg2 | 4e9c3e44f3e3 | ghcr.io/srl-labs/network-multitool | linux         | running | 172.20.20.3/24   | 2001:172:20:20::c/64 |
+----+-----------------------------------------+--------------+------------------------------------+---------------+---------+------------------+----------------------+
```
Using the names from the above output, we can login to the a node using the following command:

For example to access node `clab-pysros-dc-pe1` via ssh simply type:
```
ssh admin@clab-pysros-dc-pe1
```

#### Accessing the lab via Internet

Each public cloud instance has a port-range (50000 - 51000) exposed towards the Internet, as lab nodes spin up, a public port is dynamically allocated by the docker daemon on the public cloud instance.
You can utilize those to access the lab services straight from your laptop via the Internet.

With the `show-ports` command executed on a VM you get a list of mappings between external and internal ports allocated for each node of a lab:

```
~$ show-ports
Name                                     Forwarded Ports
clab-sros-pysros-device-correlation-ce1  50020 -> 22, 50019 -> 830, 50018 -> 57400
clab-sros-pysros-device-correlation-ce2  50011 -> 22, 50010 -> 830, 50009 -> 57400
clab-sros-pysros-device-correlation-ce3  50016 -> 22, 50014 -> 830, 50012 -> 57400
clab-sros-pysros-device-correlation-ce4  50026 -> 22, 50025 -> 830, 50024 -> 57400
clab-sros-pysros-device-correlation-pe1  50023 -> 22, 50022 -> 830, 50021 -> 57400
clab-sros-pysros-device-correlation-pe2  50008 -> 22, 50007 -> 830, 50006 -> 57400
clab-sros-pysros-device-correlation-pe3  50017 -> 22, 50015 -> 830, 50013 -> 57400
clab-sros-pysros-device-correlation-pe4  50029 -> 22, 50028 -> 830, 50027 -> 57400
clab-sros-pysros-elb-node0               50005 -> 22, 50004 -> 830
```

Each service exposed on a lab node gets a unique external port number as per the table above. 
As an example: NETCONF for `clab-sros-pysros-device-correlation-pe1` is available on port `50022` of the VM which is mapped to the nodes internal port of 830.


## Reference documentation

* [pySROS API documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest)
* [SR OS documentation](https://documentation.nokia.com/sr/)


## Tasks

1. **Read in the topology file created by containerlab as the topology is built.**

    This topology file is located in the `./clab-sros-pysros-device-correlation/topology-data.json` file.  This should be used as the 
    inventory for your application.

    Using this file identify the nodes that you wish to connect to.

2. **Connect to all of the SR OS devices.**

    Establish a pySROS connection to all of the devices you identified in task 1.

    *Optional enhancement: Do this by creating a new custom class instance per device where you can store each nodes data.*

3. **Using the `pysros.pprint` module create an SR OS style output that lists the devices that have BGP enabled (and operationally `up`).**

    You should list the devices with BGP enabled (and operationally `up`) on a single line (row) in the output as you will add more information to your output in subsequent tasks.

4. **Add the list of devices that have IS-IS enabled (and operationally `up`) to your output.**

5. **Add a new row with the CPU usage percentages per device shown.**

    Each device on the row should show it's name and the CPU usage value (in percent).

    *Optional enhancement: Show the devices in order from left to right with the highest CPU load to the left and the lowest CPU load to the right.*

6. **Add a new row with the number of IPv4 routes in the RIB for each device.**

    Each device on the row should show it's name and the number of routes in the RIB.

    *Optional enhancement: Show the devices in order from left to right with the highest number of routes in the RIB to the left and the lowest number of routes in the RIB to the right.*

7. **Add a count of the number of rows in your table to the table output.**

8. **Add your own data collated from all the devices and presented in a useful way.**




    


