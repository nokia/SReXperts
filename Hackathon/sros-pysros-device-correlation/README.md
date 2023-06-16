# Remote correlation of information from multiple SR OS devices

Addressing this use-case will empower you to create a remote (off-box) pySROS application that obtains data from various SR OS devices and presents it in a useful way.

**Grading: Beginner / Intermediate**

**Elements: SR OS, pySROS**

## Drawing

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
| Router | SR OS release 23.3.R1 |


## Tool explanation

All tasks for the lab use-case can be completed using SR OS and Python code developed and tested on your local workstation or on the SReXperts instance server.

*Note: The containerlab topology file will be created on the SReXperts instance server when you create the lab, to use this locally you will need to take a copy of it.  Please note that this file will changes each time the lab is deployed.*

## Credentials and access

* All SR OS nodes: Default SR OS username and password

If you wish to have direct external access from your machine, use the public IP address of the VM and the external port numbers as per the table below:

| Node | Direct SSH (Ext.)      | NETCONF (Ext.) | gNMI (Ext.) | 
| -----| ---------------------- | -------------- | ----------- |
| pe1  | `ssh admin@IP:57001`   | `IP:57401`     | `IP:57301`  |
| pe2  | `ssh admin@IP:57002`   | `IP:57402`     | `IP:57302`  |
| pe3  | `ssh admin@IP:57003`   | `IP:57403`     | `IP:57303`  |
| pe4  | `ssh admin@IP:57004`   | `IP:57404`     | `IP:57304`  |
| ce1  | `ssh admin@IP:57005`   | `IP:57405`     | `IP:57305`  |
| ce2  | `ssh admin@IP:57006`   | `IP:57406`     | `IP:57306`  |
| ce3  | `ssh admin@IP:57007`   | `IP:57407`     | `IP:57307`  |
| ce4  | `ssh admin@IP:57008`   | `IP:57408`     | `IP:57308`  |


## Reference documentation

* [pySROS API documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest)
* [SR OS documentation](https://documentation.nokia.com/sr/)


## Tasks

