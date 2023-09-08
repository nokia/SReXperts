# SR OS enhanced login banner with pySROS

Addressing this use-case will empower you to adjust your SR OS system to provide the
information that you require each time you connect to the device in MD-CLI.

**Grading: Beginner**

**Elements: SR OS, pySROS**

## Lab diagram

devices needed (hostname, type, ...)

![topo](./_images/sros-pysros-elb.png)

## High level tasks to complete this project

* Identify some data that should be displayed on login to SR OS using the MD-CLI pwc and info commands to navigate around the YANG-modelled data
* Write a Python 3 application using the pySROS libraries that extracts this data and prints it out
* Create a login-script that calls your Python application on login to display the chosen data

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

All tasks for the lab use-case can be completed on the provided SR OS node.  Python code may be developed and tested remotely and uploaded to the node in order to complete the lab if that is preferable.


## Credentials & Access
### Accessing the lab from within the VM

To access the lab nodes from within the VM, users should identify the names of the deployed nodes using the `sudo containerlab inspect` command:

```
sudo containerlab inspect
INFO[0000] Parsing & checking topology file: sros-pysros-enhanced-login-banner.clab.yml 
+---+----------------------------+--------------+-----------------+---------+---------+-----------------+----------------------+
| # |            Name            | Container ID |      Image      |  Kind   |  State  |  IPv4 Address   |     IPv6 Address     |
+---+----------------------------+--------------+-----------------+---------+---------+-----------------+----------------------+
| 1 | clab-sros-pysros-elb-node0 | e398e98aef7b | vr-sros:23.7.R1 | vr-sros | running | 172.20.20.20/24 | 2001:172:20:20::2/64 |
+---+----------------------------+--------------+-----------------+---------+---------+-----------------+----------------------+
```
Using the names from the above output, we can login to the a node using the following command:

For example to access node `clab-sros-pysros-elb-node0` via ssh simply type:
```
ssh admin@clab-sros-pysros-elb-node0
```

### Accessing the lab via Internet

Each public cloud instance has a port-range (50000 - 51000) exposed towards the Internet, as lab nodes spin up, a public port is dynamically allocated by the docker daemon on the public cloud instance.
You can utilize those to access the lab services straight from your laptop via the Internet.

With the `show-ports` command executed on a VM you get a list of mappings between external and internal ports allocated for each node of a lab:

```
~$ show-ports
Name                                     Forwarded Ports
clab-sros-pysros-elb-node0               50031 -> 22, 50030 -> 830
```

Each service exposed on a lab node gets a unique external port number as per the table above. 
As an example: SSH for `clab-sros-pysros-elb-node0` is available on port `50031` of the VM which is mapped to the nodes internal port of `22`.

## Credentials and access

* node0: Default SR OS username and password


## Reference documentation

* [pySROS API documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest)
* [SR OS documentation](https://documentation.nokia.com/sr/)


## Tasks

1. **Identify some data that should be displayed on login to SR OS using the MD-CLI pwc and info commands to navigate around the YANG-modelled data**

    Explore the MD-CLI using the `info` and `pwc` commands for both configuration and state data in order to choose a selection of data points that you will find beneficial to see at login.

    *Enhancement: If you wish to go a step further you can create a new data metric that you would like to display using a mathematical formula given one or more existing data points.*
 
2. **Write a Python 3 application using the pySROS libraries that extracts this data and prints it out**
    
    Create a simple Python application using the pySROS libraries to obtain the identified data and print it to the screen.  This may be done on the device using the `file edit` command to edit to file on the device itself or on your local machine or the lab server.  Once you are happy with the application you can copy it to the router and run it locally (take a look at the `pyexec` command).

    An example pySROS application is shown [here](./example_solution/elb.py) to get you started.

    To test your code remotely ensure your `Connection` object has all the required parameters and just run it.  Communication with the node will be handled by pySROS.

3. **Create a login-script that calls your Python application on login to display the chosen data**

    * Copy your `elb.py` pySROS application to `cf3:`
    * Create a login script file called `login.scr` in `cf3:` that
      runs `pyexec cf3:\elb.py`
    * Configure `node0` to call the login-script for all users on login

## Destroying the lab

When you are complete with the lab, it can be destroyed by issuing the following command:

```
sudo containerlab destroy --cleanup
```

