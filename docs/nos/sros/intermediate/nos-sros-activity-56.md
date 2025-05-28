---
tags:
  - SR OS
  - Ansible
  - NETCONF
  - configuration
  - MD-CLI
---

# Network troubleshooting and configuration with SR OS and Ansible

|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Network troubleshooting and configuration with SR OS and Ansible                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Activity ID**             | 56                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Short Description**       | With Ansible you can build automation once and re-use implemented solutions for other devices easily. In this activity, we will apply that to configuration management for model-driven SR OS devices using NETCONF. |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/), [Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html), [Ansible](https://docs.ansible.com/), [SR OS with Ansible](https://network.developer.nokia.com/sr/learn/sr-os-ansible/), [Ansible.Netcommon](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/index.html)                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Topology Nodes**          | :material-router: PE1, :material-account-circle-outline: client01, :material-router: leaf21, :material-account-circle-outline: client21  |
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/md-cli-user.html)<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/titles/system-management.html)<br/>[SR OS with Ansible](https://network.developer.nokia.com/sr/learn/sr-os-ansible/)<br/>[Ansible Netcommon](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/index.html)<br/>[Ansible network best practices](https://docs.ansible.com/ansible/latest/network/user_guide/network_best_practices_2.5.html) |

Ansible is a well-known suite of software tools that started gaining traction with the wider IT community over a decade ago. It has since been acquired by Red Hat and over the years it has found its way towards the networking industry. The existing community had at that point provided how-to guides, reusable plugins and modules for IT services and the Network functionality was then added. This activity follows that same transition.  We will start from an Ansible playbook used for another task against a Linux host and expand upon it to include some of our network automation tasks.

You will be introduced to automated management of SR OS using Ansible's NETCONF [netcommon](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/) collection. The `netcommon` modules are created and supported by Red Hat. They provide a consistent and supported multi-vendor interface.

## Objective

To accomplish this activity, several tasks are outlined below for you to go through and experience. The existing playbook sends a `ping` command to the Linux node `client01` that is connected to `pe1`. The playbook is executed whenever a test of connectivity between `client01` and `pe1` is required and ensures the VPRN service is functioning correctly.

1. Inspect the existing playbook available for you in the Hackathon repository under `activities/nos/sros/activity-56/`. You can find a copy of the repository in your group's hackathon VM under `/home/nokia/SReXperts/`.
2. Run the playbook as an initial test to assess the current situation
3. Add a task to your playbook that connects to `pe1` and retrieves data about the service meant for `client01`
4. Based on the outcome of the previous task, update the configuration of `pe1`.
5. Introduce an additional step where the ping is originated from `pe1` towards `client01`.

## Technology explanation

In this chapter, we will discuss the tools and concepts that will be used throughout the exercise.

### Ansible

[Ansible](https://www.ansible.com/) is a suite of software tools that enables infrastructure as code. The suite is open-source and includes software provisioning, configuration management and application deployment functionality. Ansible is designed with several key principles in mind. It has to be simple to understand, readable, extensible and there should be a gentle learning curve. The language used for defining what Ansible should do is YAML. Check out [some of the documentation](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) for the reasoning behind it and to see how YAML is used.

In addition to what is being used in this activity, a commercial offering of Ansible exists in the Ansible Automation Platform (AAP) from RHEL that includes additional functionality and support that isn't available out of the box in the regular version.

#### Core and Community

When installing Ansible you may be confronted with several versioning systems. This stems from the differentation that is made between `Ansible Core` and `Ansible Community`. The former provides the language and the runtime that powers any automation use cases driven with Ansible while the latter includes the `Core` functionality as well as a number of collections. `Ansible Community` is available for installation as the Python `ansible` package.

It is `Ansible Community` that is used for this activity, with special mention for some of the modules that come bundled with it. The version of the package that is used is `11.5.0` and the version of `ansible-core` that is provided with it is `2.18.5`. The bundled collections that come with the package include some that are maintained directly by Ansible, some that are maintained by partner organizations and others that are maintained by community teams. Among these modules is a collection of network-specific plugins and modules (including those for NETCONF) that are developed and maintained directly by Ansible.

#### Ansible Netcommon

Created by the Ansible Network Community, the Netcommon collection contains numerous resources that allow it to interface with network devices. The collection contains vendor agnostic elements so any networking equipment that exposes standards-based interfaces can be interfaced with. The collection includes modules and plugins for NETCONF, gRPC, plain CLI, RESTCONF, file operations and a few other tasks, as documented [here](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/index.html#modules).

In this activity, in addition to some [`builtin`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/index.html) modules, the `netcommon.netconf` modules will be used.

#### Jargon

Before diving into the remaining technical topic and the tasks to be completed, let's introduce some of the terms used when talking about automation with Ansible to establish a shared language. The list of terms that will come up is as follows:

> **Inventory**

In any Ansible deployment an inventory must be defined. This inventory includes the target hosts that could be used as well as some key information about them. This could include credentials, reachability information or some specific details required to be able to connect to the device.

>**Collections, modules and plugins**

Plugins augment Ansible's core functionality and are accessible to modules, they are written in Python. Modules are small programs that perform actions on local machines, APIs or remote hosts when instructed to do so by tasks. They can be written in any language though are often written in Python. Finally, collections are a distribution format for Ansible content. They typically address a usecase like interacting with networking equipment, as is the case for the `netcommon` collection.

> **Roles**

Roles are a logical way of labelling and grouping tasks according to certain variables or files they need access to, tasks they need to execute or information that is applicable to them. By defining them in a role this information doesn't have to be repeated as often. By assigning or un-assigning roles to hosts they can easily be controlled without having to re-do the implementation of the role's tasks. Roles are created by adhering to a file hierarchy and naming structure.

> **Plays**

Solutions built as Ansible playbooks are broken down into smaller pieces known as plays that are called from a playbook. A play may refer to a mapping of a role to one or more target hosts, though in general it refers to an ordered grouping of tasks mapped to specific hosts.

> **Playbooks**

Finally, a playbook is what is executed from the CLI, potentially with some additional input flags. A playbook can call plays and import roles to perform complicated workflows.

<br/>

With these terms in mind, we will be able to identify the different elements in the Ansible-based automation we are building in this activity.

### Model-driven SR OS

As the term "model-driven" suggests, a model-driven Network Operating System (NOS) such as SR OS has one or more data models at its core. These data models compile together to provide the schema for the system. These data models are written using a language called YANG and, in the case of SR OS, are available [online](https://github.com/nokia/7x50_YangModels). In this activity, you will need to interact with the SR OS system in various ways and knowing where to find information will be useful here.

Configuration added to model-driven SR OS has to be loaded into the candidate datastore before it can be applied to the system via a `commit` operation. To begin configuring the router, an operator must first enter a configuration session using `configure private` or `edit-config private`. Operations other than `commit` exist, key among which is `ping` that will also be used as part of this activity. Knowing this, when looking through the `netcommon` modules, try to understand what is and isn't being abstracted away for you.

Model-driven SR OS is built to enable automation by providing several helpful commands:

- `pwc` can show you in a number of formats what path you are currently in
- `tree` shows you what values would be valid further down the tree, useful when you are looking for a certain attribute
- `compare` returns the difference between the currently active candidate datastore session and the running configuration. This command has several optional flags, key among which are `netconf-rpc` and `summary`. Combining these gives you back an XML payload that would be usable by a NETCONF client to make the same changes again.

Between NETCONF, gRPC and the MD-CLI model-driven SR OS boasts three model-driven interfaces. Each of these three interfaces can be used interchangeably, albeit with some differences in underlying transport and encoding. As such, when looking at the activity, any choice of module won't necessarily be the correct one as this can be up to personal preference.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Explore the existing implementation

Look at the Hackathon repository that is available on your group's hackathon VM under `/home/nokia/SReXperts`. In the folder `activities/nos/sros/activity-56` the existing playbook and accompanying files used to test service availability from the `client01` machine are included. Look into this folder and try to map the terms introduced previously to the different files. The structure is as follows:

```bash
- activity-56/
  - ansible.cfg
  - inventory.yml
  - playbook.yml
  - roles
    - linux_ping/
      - files/
      - tasks/
        - main.yml
      - templates/
```

Look inside the files to understand where each piece of information is stored and discover where the ping command is actually being sent.

??? note "Existing situation"
    The inventory file `inventory.yml` contains a group named `linux_hosts` with a single member, `clab-srexperts-client01`. In addition, this file sets some variables required to connect to the target host. Setting variables in the inventory file is only one way of doing this, some other options are documented [here](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html#splitting-out-vars).

    The playbook file `playbook.yml` contains a play mapping the `linux_ping` role to the `linux_hosts` group so that any tasks in the role are executed using those hosts as targets when the playbook runs.

    In the `roles/` directory the aforementioned role named `linux_ping` exists in the form of a subdirectory and three subdirectories exist for that role. The `files` subdirectory would contain any generated files or other static content required for the task while the `templates` directory could contain templates used to generate those files. In this case, both are empty. The only subfolder with any content is `tasks`, which contains the `main.yml` file. Inside that file the `ping` command is defined.

    The `ansible.cfg` file is included to disable SSH hostkey verification. While acceptable in the ephemeral lab environment provided to you for the Hackathon, this isn't recommended for live or production environments. By adding this setting we avoid having to manually check every individual SSH host key in this activity.

### Run the existing playbook and look at the output

Run the existing playbook using the `ansible-playbook` command. Use a CLI flag to point to the inventory file and check the output. What do you notice?

/// Details | Output
/// tab | Command
```bash
$ ansible-playbook playbook.yml -i inventory.yml
```
///
/// tab | Expected Output
```bash
$ ansible-playbook playbook.yml -i inventory.yml

PLAY [Linux ping to test provisioned service] ************************************************************************************************************************

TASK [linux_ping : Test service on PE1] ******************************************************************************************************************************
fatal: [clab-srexperts-client01]: FAILED! => {"changed": true, "msg": "non-zero return code", "rc": 1,
"stderr": "Shared connection to clab-srexperts-client01 closed.\r\n", "stderr_lines": ["Shared
  connection to clab-srexperts-client01 closed."], "stdout": "PING 10.70.11.101 (10.70.11.101) 56(84)
  bytes of data.\r\nFrom 10.70.11.1 icmp_seq=1 Destination Host Unreachable\r\n\r\n--- 10.70.11.101
  ping statistics ---\r\n1 packets transmitted, 0 received, +1 errors, 100% packet loss, time 0ms
  \r\n\r\n", "stdout_lines": ["PING 10.70.11.101 (10.70.11.101) 56(84) bytes of data.", "From 10.70.11.1
  icmp_seq=1 Destination Host Unreachable", "", "--- 10.70.11.101 ping statistics ---", "1 packets
  transmitted, 0 received, +1 errors, 100% packet loss, time 0ms", ""]}
```

The ping is currently failing so the service provided from PE1 is not in the expected state.

///
///

### Add a step to retrieve state information from `pe1`

Don't worry, it is expected that your `ping` from the previous task is not working. We're going to fix it now.

The expected service configuration that should be present on node `pe1` is the following:

```
    configure {
        service {
+           vprn "ansible-vprn" {
+               admin-state enable
+               service-id 600
+               customer "1"
+               interface "client01" {
+                   ipv4 {
+                       primary {
+                           address 10.70.11.101
+                           prefix-length 24
+                       }
+                   }
+                   sap 1/1/c6/1:600 {
+                   }
+               }
+           }
        }
    }
```

There should similarly be an entry in the system's `running` state that signifies that the service and the interface inside it are operationally up. The corresponding paths in the MD-CLI are

- `/state service vprn "ansible-vprn" oper-state`
- `/state service vprn "ansible-vprn" interface "client01" oper-state`

We could log in using SSH and get to work troubleshooting and fixing any issues, however, that wouldn't be very automated. Let's use Ansible instead. First, using the [`ansible.netcommon.netconf_get`](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/netconf_config_module.html) module, make sure that the state paths above are present and the values are in line with our expectations. That not being the case would be the easiest explanation for the failing connectivity check. Note that this check should only be done if the ping from the previous section failed.

To accomplish this, you’ll need to complete the following steps:

- Create a group called `sros_nodes` in your inventory and add `clab-srexperts-pe1` to it. Look for [information](https://docs.ansible.com/ansible/latest/network/user_guide/platform_index.html#settings-by-platform) on the `ansible_network_os` and `ansible_connection` attributes as they will be crucial here.
- Change the existing role `linux_ping` to publish a variable `ping_result` and not fail on errors
- Create a new role called `check_service` based on the `linux_ping` role that uses `netconf_get` to collect data from the target SR OS nodes
- Call this role from your playbook after the `linux_ping` role if the connectivity play returned a nonzero return code
- Make sure the rest of the playbook knows the outcome of this state verification by publishing another variable, use the builtin [`set_fact`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/set_fact_module.html) to reduce the output variable to be `true` or `false` as a response to the question whether the service is operational.

!!! tip "A few pointers to get you started"
    When a task is executed against a host by Ansible and a value is returned using the `register` directive, this variable is added to the host's `hostvars`. Look towards the [documentation](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html) for more information on variables and how to access them throughout the playbook.

    The [`netconf_get`](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/netconf_get_module.html) task can take an XML payload to be used to filter the amount of data retrieved from the target host. You can specify this in the role's `main.yml` file however to reduce clutter it may be preferable to use the builtin [`lookup`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_lookup.html) function.

!!! tip "Debugging information"
    Ansible has several ways in which it can display debugging information. You can make the output of the playbook execution more verbose by adding more `v` flags to the command, e.g. `-v` or `-vvvvv` depending on the desired level of verbosity. The builtin [`debug`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/debug_module.html) module lets you print out variables as part of the playbook itself. Use these freely to follow what is going on whenever you execute your playbook.

    Use the debug module to see which attribute(s) of the `ping_result` variable can tell you whether the ping succeeded or failed.

/// Details | Solution - `check_service`
/// tab | Expected Result
```bash hl_lines="16"
$ ansible-playbook playbook.yml -i inventory.yml -v
Using /home/nokia/SReXperts/activities/nos/sros/activity-56/ansible.cfg as config file

PLAY [Linux ping to test provisioned service] **************************************************************

TASK [linux_ping : Test service on PE1] ********************************************************************
fatal: [clab-srexperts-client01]: FAILED! => {"...(snip)", "rc": 1, "stderr": "... (snip)]}
...ignoring

PLAY [Check configuration state on SR OS node] **************************************************************

TASK [check_service : Pre-check PE1 service oper-state] ****************************************************
ok: [clab-srexperts-pe1] => {"changed": false, "output": null, "stdout": "<data xmlns=\"...(snip)</data>"]}

TASK [check_service : Render retrieved state to boolean `true` if service exists, false otherwise] *********
ok: [clab-srexperts-pe1] => {"ansible_facts": {"service_found": false}, "changed": false}

PLAY RECAP *************************************************************************************************
clab-srexperts-client01    : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=1
clab-srexperts-pe1         : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
///
/// tab | Inventory
Add the following lines to `inventory.yml` to make Ansible aware of the SR OS node:
```yaml
sros_nodes:
  hosts:
    clab-srexperts-pe1:
      ansible_connection: "ansible.netcommon.netconf"
      ansible_network_os: "<network-os>"
      ansible_user: "admin"
      ansible_password: #PROVIDED#
```
///
/// tab | Modify `linux_ping`
Change the existing role to publish a variable and not fail on errors:
```yaml
---
- name: Test service on PE1
  raw: ping -c 1 10.70.11.101
  ignore_errors: true
  register: ping_result
```
///
/// tab | Add a new role
Build a new role, `check_service`, by copying the file structure from `linux_ping`. Populate the `files` subdirectory with `filter.xml`. This file should contain a payload for filtering the `oper-state` of the VPRN and its associated interface to limit the amount of data received.
```xml
<state xmlns="urn:nokia.com:sros:ns:yang:sr:state" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nokia-attr="urn:nokia.com:sros:ns:yang:sr:attributes">
    <service>
        <vprn>
            <service-name>ansible-vprn</service-name>
            <oper-state/>
            <interface>
                <interface-name>client01</interface-name>
                <ipv4>
                    <oper-state/>
                </ipv4>
            </interface>
        </vprn>
    </service>
</state>
```
Then, add a task to your role that checks the state:
```yaml
---
- name: Pre-check PE1 service oper-state
  connection: netconf
  ansible.netcommon.netconf_get:
    filter: "{{ lookup('file', './filter.xml') }}"
  register: netconf_service_state

- name: Render retrieved state to boolean `true` if service exists, false otherwise
  set_fact:
    service_found: "{{ 'state' in (netconf_service_state.stdout |ansible.utils.from_xml() | from_json )['data'] }}"
```
/// admonition | from_json
    type: warning
As you might notice in the example solution above, to get to the dictionary variable that we would expect is returned by the call to `from_xml` we first have to pipe it through the `from_json` function. This is a known [issue](https://github.com/ansible-collections/ansible.utils/issues/114) with a fix [available](https://github.com/ansible-collections/ansible.utils/pull/361/files) however the ansible version downloaded by default with `pip` in this environment does not include it.
///
///
/// tab | Append to playbook
Add a play to `playbook.yml` to map the SR OS nodes group to your new role when the ping fails:
```yaml
- name: Check configuration state on SR OS node
  hosts: sros_nodes
  gather_facts: False
  roles:
    - role: check_service
      when: hostvars['clab-srexperts-client01'].ping_result.rc != 0
  tags: ['check_service']
```
///
///

### Make changes to the `pe1` configuration so that service 600 works properly

While we could address the original issue of the ping failing by adding the missing configuration manually that would not serve us should this issue reoccur. Instead, add the necessary changes to the Ansible files already present so that the action taken when the ping fails and the previous check finds the service missing is to apply the desired configuration to the router.

You can find this configuration in the previous section. Make sure the configuration is not pushed needlessly, so only do this when the configuration is shown to be missing and after we found the ping to not be working.

Use what you have learned so far, try to use the available documentation and example resources online to get as far as you can before looking at the proposed solution.

??? tip "Some more pointers to get you started"
    Create another role, `config_service`, and add a play to your playbook that calls to it whenever the existing ping command returned a nonzero return code and the state check failed.

    Try to use the MD-CLI to help you build the configuration step by letting `compare` generate the input needed for [`ansible.netcommon.netconf_config`](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/netconf_config_module.html). The examples available on the [Nokia developer portal](https://network.developer.nokia.com/sr/learn/sr-os-ansible/sr-os-ansible-examples/) may come in handy.

/// Details | Solution - `config_service`
/// tab | Expected Result
```bash hl_lines="21"
$ ansible-playbook playbook.yml -i inventory.yml -v
Using /home/nokia/SReXperts/activities/nos/sros/activity-56/ansible.cfg as config file

PLAY [Linux ping to test provisioned service] **************************************************************

TASK [linux_ping : Test service on PE1] ********************************************************************
fatal: [clab-srexperts-client01]: FAILED! => {"...(snip)", "rc": 1, "stderr": "... (snip)]}
...ignoring

PLAY [Check configuration state on SR OS node] *************************************************************

TASK [check_service : Pre-check PE1 service oper-state] ****************************************************
ok: [clab-srexperts-pe1] => {"changed": false, "output": null, "stdout": "<data xmlns=\"...(snip)</data>"]}

TASK [check_service : Render retrieved state to boolean `true` if service exists, false otherwise] *********
ok: [clab-srexperts-pe1] => {"ansible_facts": {"service_found": false}, "changed": false}

PLAY [Add configuration to SR OS node] *********************************************************************

TASK [config_service : Configure PE1 service] **************************************************************
changed: [clab-srexperts-pe1] => {"changed": true, "server_capabilities": [...(snip)]}

PLAY RECAP *************************************************************************************************
clab-srexperts-client01    : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=1
clab-srexperts-pe1         : ok=3    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
///
/// tab | Playbook
Add a play to `playbook.yml` to execute your new role against the SR OS nodes when the ping fails and the service configuration is found to be missing:
```yaml
- name: Add configuration to SR OS node
  hosts: sros_nodes
  gather_facts: False
  roles:
    - role: config_service
      when: hostvars['clab-srexperts-client01'].ping_result.rc != 0 and not hostvars['clab-srexperts-pe1'].service_found
  tags: ['config_service']
```
///
/// tab | New role `config_service`
Copy the file structure from `check_service` and rename `filter.xml` to `service.xml`. Replace the contents of the file with a payload that will configure the service.
```xml
<nc:config xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
    <configure xmlns="urn:nokia.com:sros:ns:yang:sr:conf" xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" xmlns:nokia-attr="urn:nokia.com:sros:ns:yang:sr:attributes">
        <service>
            <vprn>
                <service-name>ansible-vprn</service-name>
                <admin-state>enable</admin-state>
                <service-id>600</service-id>
                <customer>1</customer>
                <interface>
                    <interface-name>client01</interface-name>
                    <ipv4>
                        <primary>
                            <address>10.70.11.101</address>
                            <prefix-length>24</prefix-length>
                        </primary>
                    </ipv4>
                    <sap>
                        <sap-id>1/1/c6/1:600</sap-id>
                    </sap>
                </interface>
            </vprn>
        </service>
    </configure>
</nc:config>
```
Add a task to your role to configure the service using this payload:
```yaml
- name: Configure PE1 service
  connection: netconf
  ansible.netcommon.netconf_config:
    content: "{{ lookup('file', './service.xml') }}"
    commit: true
    target: candidate
    lock: never
    format: xml
```
///
///

!!! tip "Check your work"
    Make sure your configuration was applied correctly, either by checking the node directly or by running your playbook again. If the configuration is now present that should have a noticeable impact on your playbook's behavior.

### Send a ping from `pe1` to `client01` via Ansible

As `client01` isn't model-driven and does not come with a Python interpreter installed, our options on the Ansible side are somewhat limited. If you have followed the example solution, this translates into being able to distinguish between different return codes from the raw `ping` command or text-scraping.

Let's add a ping that will give us some modeled output that we can more easily interpret within our automation. To do this and to introduce a little `read-your-writes` verification to your playbook, add another task to the `check_service` role that will send this ping for you. Add another play to your playbook that repeats the `check_service` role after the `config_service` play was executed.

Use a [`jinja2`](https://jinja.palletsprojects.com/en/stable/) template that takes input variables so that the task will be reusable for any other services or IP addresses you may need later on. Implement the new task in a way that ensures it will be skipped if there is no destination IP specified.

You can use the [`netcommon.netconf_rpc` module](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/netconf_rpc_module.html) for this. Use it to trigger a modeled [`ping`](https://github.com/nokia/7x50_YangModels/blob/master/latest_sros_25.3/nokia-oper-global.yang#L9304) operation on `pe1` with the following parameters:

- payload size of 800 bytes
- destination IP of 10.70.11.1
- source IP of 10.70.11.101
- in routing instance `ansible-vprn`
- only send a single ping request

!!! tip "Command-line arguments"
    We haven't talked about the tags we have been adding in the example solution yet. These let you single out one or more tasks by using the `-t` parameter when you invoke the playbook. Adding a unique [tag](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_tags.html) to this second instance of `check_service` may make it easier to troubleshoot this task as it gives you the ability to call it directly.

    Another useful thing you can do through CLI parameters uses the `-e` flag, which lets you define variables from the CLI. Try to override the programmed count of `1` to be `4` instead, using the CLI.

??? tip "Ping payload and result"
    For potential comparison with your implementation, consider the following two tabs that contain the an example input and output for the `ping` operation as seen in verbose Ansible logs.
    /// tab | Input
    ```xml
    <global-operations xmlns=\"urn:nokia.com:sros:ns:yang:sr:oper-global\">
        <ping>
        <destination>10.70.11.1</destination>
            <router-instance>ansible-vprn</router-instance>
            <source-address>10.70.11.101</source-address>
            <count>1</count>
            <size>800</size>
        </ping>
    </global-operations>
    ```
    ///
    /// tab | Output
    ```xml
    <rpc-reply xmlns:nc=\"urn:ietf:params:xml:ns:netconf:base:1.0\" xmlns=\"urn:ietf:params:xml:ns:netconf:base:1.0\" xmlns:nokiaoper=\"urn:nokia.com:sros:ns:yang:sr:oper-global\" message-id=\"urn:uuid:d6ebb25b-d5fa-4599-9f81-00fcd6f7ab42\">
        <nokiaoper:operation-id>35</nokiaoper:operation-id>
        <nokiaoper:start-time>2025-05-18T12:34:52.8Z</nokiaoper:start-time>
        <nokiaoper:results>
            <nokiaoper:test-parameters>
                <nokiaoper:destination>10.70.11.1</nokiaoper:destination>
                <nokiaoper:bypass-routing>false</nokiaoper:bypass-routing>
                <nokiaoper:router-instance>ansible-vprn</nokiaoper:router-instance>
                <nokiaoper:source-address>10.70.11.101</nokiaoper:source-address>
                <nokiaoper:srv6-policy>false</nokiaoper:srv6-policy>
                <nokiaoper:candidate-path>false</nokiaoper:candidate-path>
                <nokiaoper:preference>100</nokiaoper:preference>
                <nokiaoper:count>1</nokiaoper:count>
                <nokiaoper:output-format>detail</nokiaoper:output-format>
                <nokiaoper:do-not-fragment>false</nokiaoper:do-not-fragment>
                <nokiaoper:fc>nc</nokiaoper:fc>
                <nokiaoper:interval>1</nokiaoper:interval>
                <nokiaoper:pattern>sequential</nokiaoper:pattern>
                <nokiaoper:size>800</nokiaoper:size>
                <nokiaoper:timeout>5</nokiaoper:timeout>
                <nokiaoper:tos>0</nokiaoper:tos>
                <nokiaoper:ttl>64</nokiaoper:ttl>
            </nokiaoper:test-parameters>
            <nokiaoper:probe>
                <nokiaoper:probe-index>1</nokiaoper:probe-index>
                <nokiaoper:status>response-received</nokiaoper:status>
                <nokiaoper:round-trip-time>1443</nokiaoper:round-trip-time>
                <nokiaoper:response-packet>
                    <nokiaoper:size>808</nokiaoper:size>
                    <nokiaoper:source-address>10.70.11.1</nokiaoper:source-address>
                    <nokiaoper:icmp-sequence-number>1</nokiaoper:icmp-sequence-number>
                    <nokiaoper:ttl>64</nokiaoper:ttl>
                </nokiaoper:response-packet>
            </nokiaoper:probe>
            <nokiaoper:summary>
                <nokiaoper:statistics>
                    <nokiaoper:packets>
                        <nokiaoper:sent>1</nokiaoper:sent>
                        <nokiaoper:received>1</nokiaoper:received>
                        <nokiaoper:loss>0.0</nokiaoper:loss>
                    </nokiaoper:packets>
                    <nokiaoper:round-trip-time>
                        <nokiaoper:minimum>1064</nokiaoper:minimum>
                        <nokiaoper:average>1064</nokiaoper:average>
                        <nokiaoper:maximum>1064</nokiaoper:maximum>
                        <nokiaoper:standard-deviation>0</nokiaoper:standard-deviation>
                    </nokiaoper:round-trip-time>
                </nokiaoper:statistics>
            </nokiaoper:summary>
        </nokiaoper:results>
        <nokiaoper:status>completed</nokiaoper:status>
        <nokiaoper:end-time>2025-05-18T12:34:57.3Z</nokiaoper:end-time>
    </rpc-reply>
    ```
    ///

/// details | Solution - add `ping` to `check_service`
/// tab | Expected Output with CLI parameters
```bash
$ ansible-playbook playbook.yml -i inventory.yml -v -t check_service_after -e count=4
Using /home/nokia/SReXperts/activities/nos/sros/activity-56/ansible.cfg as config file

PLAY [Linux ping to test provisioned service] **************************************************************

PLAY [Check configuration state on SR OS node] *************************************************************

PLAY [Add configuration to SR OS node] *********************************************************************

PLAY [Check service state on SR OS node] *******************************************************************

TASK [check_service : Pre-check PE1 service oper-state] ****************************************************
ok: [clab-srexperts-pe1] => {"changed": false, "output": null, "stdout": "<data ... (snip)</data>"]}

TASK [check_service : Render retrieved state to boolean `true` if service exists, false otherwise] *********
ok: [clab-srexperts-pe1] => {"ansible_facts": {"service_found": true}, "changed": false}

TASK [check_service : Send a ping from the router to the client to confirm activity] ***********************
ok: [clab-srexperts-pe1] => {"changed": false, "output": null, "stdout": "<rpc-reply xmlns:nc...(snip)"</rpc-reply>"]}

PLAY RECAP *************************************************************************************************
clab-srexperts-pe1         : ok=3    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0

```
///
/// tab | Create a template
Add a template to the `check_service` role in the file `templates/ping.j2`:
```xml
<global-operations xmlns="urn:nokia.com:sros:ns:yang:sr:oper-global">
  <ping>
    <destination>{{dest_ip}}</destination>
    <router-instance>{{rtr_inst}}</router-instance>
    <source-address>{{src_ip}}</source-address>
    <count>{{count}}</count>
    <size>{{size}}</size>
  </ping>
</global-operations>
```
///

/// tab | Update `check_service`
To render the template into payload `ping.xml` use the [`template`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_lookup.html) and `lookup` builtins.

Add a test using Jinja2's `defined` test on the variable that represents the destination IP, `dest_ip` in our case, so that the task is usable if the `ping` isn't desired.

Send it with the [`netcommon.netconf_rpc`](https://docs.ansible.com/ansible/latest/collections/ansible/netcommon/netconf_rpc_module.html) module.
```yaml
- name: Send a ping from the router to the client to confirm activity
  when: dest_ip is defined
  ansible.netcommon.netconf_rpc:
    rpc: action
    xmlns: urn:ietf:params:xml:ns:yang:1
    content: "{{ lookup('ansible.builtin.template', './ping.j2') }}"
```
///

/// tab | Extend your playbook
Modify `playbook.yml` to make use of this functionality via an additional play.
```
- name: Check service state on SR OS node
  hosts: sros_nodes
  vars:
    dest_ip: "10.70.11.1"
    rtr_inst: "ansible-vprn"
    src_ip: "10.70.11.101"
    count: "1"
    size: "800"
  gather_facts: False
  roles:
    - role: check_service
  tags: ['check_service_after']
```
///
///

### [Optional] Add `leaf21` to the service provided and test the connectivity

As an optional extension, can you build the same automation for SR Linux? This time you'll use `client21` and `leaf21`. There are some resources available online ([1](https://github.com/nokia/srlinux-ansible-collection), [2](https://learn.srlinux.dev/ansible/collection/)) that may be able to help get you started working with the SR Linux Ansible Collection.

To be able to use the collection, the JSON-RPC interface on SR Linux needs to be enabled. This is done by default in the provided topology. The interfaces on `client21` and `leaf21` re-use the IP addressing information from `client01` and `pe1`. The target configuration for `leaf21` is the following:

```
+     network-instance ansible-vprn {
+         type ip-vrf
+         admin-state enable
+         interface client01 {
+             interface-ref {
+                 interface ethernet-1/1
+                 subinterface 600
+             }
+         }
+     }
+     interface ethernet-1/1 {
+         subinterface 600 {
+             type routed
+             ipv4 {
+                 admin-state enable
+                 address 10.70.11.101/24 {
+                 }
+             }
+             vlan {
+                 encap {
+                     single-tagged {
+                         vlan-id 600
+                     }
+                 }
+             }
+         }
+     }
```

Several ways exist of integrating these additional nodes into your automation. We have chosen one such approach for the example solution however don't feel pressured, you can experiment.

/// details | Example solution
/// tab | Expected Result
```bash hl_lines="41"
ansible-playbook playbook.yml -i inventory.yml -v
Using /home/nokia/SReXperts/activities/nos/sros/activity-56/ansible.cfg as config file

PLAY [Linux ping to test provisioned service] **************************************************************

TASK [linux_ping : Test service on PE1] ********************************************************************
changed: [clab-srexperts-client01] => {"...(snip)", "rc": 0, "stderr": "... (snip)]}
fatal: [clab-srexperts-client21]: FAILED! => {"...(snip)", "rc": 1, "stderr": "... (snip)]}
...ignoring

PLAY [Check configuration state on SR OS node] *************************************************************

TASK [check_service : Pre-check PE1 service oper-state] ****************************************************
skipping: [clab-srexperts-pe1] => {"...(snip)", "skip_reason": "Conditional result was False"}

TASK [check_service : Render retrieved state to boolean `true` if service exists, false otherwise] *********
skipping: [clab-srexperts-pe1] => {"...(snip)", "skip_reason": "Conditional result was False"}

TASK [check_service : Send a ping from the router to the client to confirm activity] ***********************
skipping: [clab-srexperts-pe1] => {"...(snip)", "skip_reason": "Conditional result was False"}

PLAY [Add configuration to SR OS node] *********************************************************************

TASK [config_service : Configure PE1 service] **************************************************************
skipping: [clab-srexperts-pe1] => {"...(snip)", "skip_reason": "Conditional result was False"}

PLAY [Check service state on SR OS node] *******************************************************************

TASK [check_service : Pre-check PE1 service oper-state] ****************************************************
ok: [clab-srexperts-pe1] => {"changed": false, "output": null, "stdout": "<data xmlns=\"...(snip)</data>"]}

TASK [check_service : Render retrieved state to boolean `true` if service exists, false otherwise] *********
ok: [clab-srexperts-pe1] => {"ansible_facts": {"service_found": true}, "changed": false}

TASK [check_service : Send a ping from the router to the client to confirm activity] ***********************
ok: [clab-srexperts-pe1] => {"changed": false, "output": null, "stdout": "<rpc-reply xmlns:nc=\"...(snip)</rpc-reply>"]}

PLAY [Add configuration to SR Linux node] ******************************************************************

TASK [config_service_srl : Configure Leaf21 service] *******************************************************
changed: [clab-srexperts-leaf21] => {"changed": true, "jsonrpc_req_id": "2025-05-21 08:55:00:898354", "saved": false}

PLAY RECAP *************************************************************************************************
clab-srexperts-client01    : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
clab-srexperts-client21    : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=1
clab-srexperts-leaf21      : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
clab-srexperts-pe1         : ok=3    changed=0    unreachable=0    failed=0    skipped=4    rescued=0    ignored=0
```
///
/// tab | Inventory
Add the additional linux host `client21` and to your inventory file under the `linux_hosts` group. Create a new group for `srlinux_nodes` that contains `clab-srexperts-leaf21`:
```yaml
linux_hosts:
  hosts:
    clab-srexperts-client01:
      ansible_connection: "ssh"
      ansible_ssh_user: "user"
      ansible_ssh_private_keyfile: "/home/nokia/.ssh/id_rsa"
    clab-srexperts-client21:
      ansible_connection: "ssh"
      ansible_ssh_user: "user"
      ansible_ssh_private_keyfile: "/home/nokia/.ssh/id_rsa"
sros_nodes:
  hosts:
    clab-srexperts-pe1:
      ansible_connection: "ansible.netcommon.netconf"
      ansible_network_os: "<network-os>"
      ansible_ssh_user: "admin"
      ansible_ssh_pass: #PROVIDED#
srl_nodes:
  hosts:
    clab-srexperts-leaf21:
      ansible_connection: "ansible.netcommon.httpapi"
      ansible_network_os: "nokia.srlinux.srlinux"
      ansible_user: "admin"
      ansible_password: #PROVIDED#
```
///
/// tab | Role
Create a new role, `config_service_srl` and add a task to create the configuration in `main.yml` using the `nokia.srlinux` collection.
```yaml
---
  - name: Configure Leaf21 service
    nokia.srlinux.config:
      update:
        - path: /interface[name=ethernet-1/1]/subinterface[index=600]
          value:
            index: 600
            type: routed
            ipv4:
              admin-state: enable
              address:
                ip-prefix: 10.70.11.101/24
            vlan:
              encap:
                single-tagged:
                  vlan-id: 600
        - path: /network-instance[name=ansible-vprn]
          value:
            type: ip-vrf
            admin-state: enable
            interface:
                name: client01
                interface-ref:
                  "interface": ethernet-1/1
                  "subinterface": 600
```
///
/// tab | Playbook
You are free to add another ping check or try other verifications. The only thing that is definitely needed is a configuration play that calls the new role to configure the SR Linux node.
```yaml
---
...
- name: Add configuration to SR Linux node
  hosts: srl_nodes
  gather_facts: False
  roles:
    - role: config_service_srl
      when: hostvars['clab-srexperts-client21'].ping_result.rc != 0
  tags: ['config_service_srl']
```
///
///

## Summary and review

Congratulations!  If you have made it this far you have completed this activity and achieved the following:

- You have used a virtual machine provided to you as a development environment
- You have built upon existing automation to add your own contributions and improvements
- You have learned how to interface from Ansible to SR OS (and optionally SR Linux)
- You have written YAML, XML and Jinja2 files
- You have seen that Ansible is a tool that allows putting things together to make something greater than the sum of its parts

This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity, or try to expand upon this one if you have some more ideas. If you are interested in taking some of this home with you, perhaps try to [install Ansible](https://docs.ansible.com/ansible/2.9/installation_guide/intro_installation.html#installing-ansible-with-pip) on your own machine and see if your playbook works from that platform. The relevant SSH, NETCONF and JSON-RPC ports are exposed on your group's hackathon VM so reachability should not be a problem.