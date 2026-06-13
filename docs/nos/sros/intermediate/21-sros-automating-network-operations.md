---
tags:
  - gRPC
  - gNOI
  - Operation
  - Ping
  - SR OS
---

# Automating network reachability tests using gNOI


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Automating network reachability tests using gNOI |
| **Activity ID**           | 21 |
| **Short Description**       | Automate network reachability ICMP Ping test using gRPC gNOI and Ansible |
| **Difficulty**              | Intermediate |
| **Tools used**              | [gNMIc](https://gnmic.openconfig.net/), [gNOIc](https://gnoic.kmrd.dev/), [Ansible for SR OS](https://github.com/nokia/sros-ansible-collection) |
| **Topology Nodes**          | :material-router: PE1 |
| **References**              | [SR OS documentation](https://documentation.nokia.com/sr/)<br/>[gRPC website](https://grpc.io/)<br/>[gNxI protobuf reference](https://gnxi.srlinux.dev/) |


You are a NOC engineer starting your shift. There is a report of packet loss in a core network link which may impact reachability to multiple applications from the edge of the data center network. You have been tasked to check the reachability of 10 applications from all 1000 multi-vendor leaf switches each containing 10 VRFs (one for each application). Your target is to complete this task in under 30 minutes.  After completing that task, you have also been asked to take a configuration backup of all 1000 switches.

If these actions were performed manually, you would be issuing 10,000 `ping` commands and another 1,000 `scp` commands to take the configuration backups. You could easily add another 2-3 hours to consolidate the output and find potential failures.

This is where automation comes to the rescue!

## Objective

On your group's hackathon instance, you will create an Ansible playbook to check the reachability of devices from :material-router: PE1. The playbook will use the gRPC Network Operations Interface (gNOI) remote procedure calls (RPCs) to perform this task. At the end of the activity, take configuration backups of :material-router: PE1, :material-router: PE2 and :material-router: PE3 and store them on your hackathon instance.

In this activity, you will:

1. Use gNOI to perform a `ping` test to a remote destination from an SR OS router
2. Automate the `ping` operation using an Ansible playbook
3. Use gNOI to backup the configuration file for a SR OS device

## Technology explanation

### gRPC

gRPC is an open source Remote Procedure Call (RPC) framework that implements gRPC services. To use a gRPC service, a gRPC client and a gRPC server are required. In this activity, the gRPC server is the router and the gRPC client is the server.  The client sends a gRPC request to the server who will then process the request and respond back to the client.

```
gRPC (client) --------(Request)-----------> gRPC (server)
gRPC (client) <-------(Response)----------- gRPC (server)
```

Examples of gRPC servers include SR OS and SR Linux.
Examples of gRPC clients include gNMIc, gNOIc and gNSIc.

### gNOI

gNOI (gRPC Network Operations Interface) is a gRPC service for executing operational commands on a network device. gNOI supports many services for different operations including, File Get, File Put, System Ping, System Traceroute and others.  Refer to the [gNxI reference](https://gnxi.srlinux.dev/) to see the details of all the gNOI RPCs.

For this activity, our focus will be on the gNOI `System` service. Some of the common RPCs in this service are:

- `Ping`: Ping executes the `ping` command on the target and streams the results back to the client
- `Traceroute`: Traceroute executes the `traceroute` command on the target and streams the results back to the client
- `Time`: Time returns the current time on the target
- `Reboot`: Reboot causes the target to reboot
- `SwitchControlProcessor`: SwitchControlProcessor will force a switchover from the current route processor (CPM) to the provided route processor (CPM)

### Ansible

[Ansible](https://www.ansible.com/) is a suite of software tools that enables infrastructure as code. The suite is open-source and includes software provisioning, configuration management and application deployment functionality. Ansible is designed with several key principles in mind. It has to be simple to understand, readable, extensible and there should be a gentle learning curve. The language used for defining what Ansible should do is YAML. Check out [some of the documentation](https://docs.ansible.com/ansible/latest/reference_appendices/YAMLSyntax.html) for the reasoning behind it and to see how YAML is used.

#### Inventory

In any Ansible deployment an inventory must be defined. This inventory includes the target hosts that could be used as well as some key information about them. This could include credentials, reachability information or specific details required to be able to connect to the device.

#### Plays

Solutions built as Ansible playbooks are broken down into smaller pieces known as plays that are called from a playbook. A play may refer to a mapping of a role to one or more target hosts, though in general it refers to an ordered grouping of tasks mapped to specific hosts.

#### Playbooks

Finally, a playbook is what is executed from the CLI, potentially with some additional input flags. A playbook can call plays and import roles to perform complicated workflows.

## Preparing the network device

### gRPC configuration on SR OS

Before starting the tasks, verify the gRPC configuration on :material-router: PE1 by logging in to it via SSH and inspecting the configuration.

You should find that unsecured gRPC (without TLS encryption) is already enabled on your network, and the relevant gRPC services for this activity (gNOI) have been enabled.

One way to confirm this is by running the command below on :material-router: PE1.

/// tab | cmd

``` bash
admin show configuration full-context /configure system grpc
```

///
/// tab | expected output

``` bash
/configure system grpc admin-state enable
/configure system grpc allow-unsecure-connection
/configure system grpc gnmi admin-state enable
/configure system grpc gnmi auto-config-save true
/configure system grpc gnoi cert-mgmt admin-state enable
/configure system grpc gnoi file admin-state enable
/configure system grpc gnoi system admin-state enable
/configure system grpc rib-api admin-state enable
```
///

The default TCP port for gRPC (`57400`) is used and is therefore not explicitly mentioned in the configuration.

The user `admin` should be allowed access to the gRPC service. Run the command below on :material-router: PE1 to verify this.

/// tab | cmd

``` bash
admin show configuration full-context /configure system security user-params local-user user "admin" | match grpc
```

///
/// tab | expected output
``` bash
/configure system security user-params local-user user "admin" access grpc true
```
///

### Client verification

We will be using [gNOIc](https://gnoic.kmrd.dev) as the clients for the gNOI service.

Verify this client is installed on your group's hackathon instance.

/// tab | cmd

``` bash
gnoic version
```

///
/// tab | expected output

``` bash
❯ gnoic version
version : 0.2.1
 commit : 27bc5a6
   date : 2026-02-27T18:18:08Z
 gitURL : https://github.com/karimra/gnoic
   docs : https://gnoic.kmrd.dev
```
///

Your version may be newer, and that's OK!

If your clients do not have `gnoic` installed or if you need to update the clients to the latest version, refer to the [gNOIc documentation](https://gnoic.kmrd.dev/).

### Ansible verification

Ansible is installed on your hackathon instance. Verify this by executing the following command on your instance.

/// tab | cmd

``` bash
ansible --version
```

///
/// tab | expected output

``` bash
❯ ansible --version
ansible [core 2.20.6]
  config file = None
  configured module search path = ['/home/nokia/.ansible/plugins/modules', '/usr/share/ansible/plugins/modules']
  ansible python module location = /usr/local/lib/python3.13/dist-packages/ansible
  ansible collection location = /home/nokia/.ansible/collections:/usr/share/ansible/collections
  executable location = /usr/local/bin/ansible
  python version = 3.13.5 (main, May  5 2026, 21:05:52) [GCC 14.2.0] (/usr/bin/python3)
  jinja version = 3.1.6
  pyyaml version = 6.0.3 (with libyaml v0.2.5)
```
///

In this activity your group's hackathon instance is taken as the development environment of choice. If you wish to use another environment for any reason make sure Ansible is installed. You can run the following commands to install it.

/// details | Ansible installation steps (if required only)
    type: code
```bash
sudo apt install -y ansible
sudo apt install -y python3-pip
```
///

### Test gNOIc connectivity to the SR OS device

Now do a connectivity check for gNOI to ensure that gRPC is running correctly on :material-router: PE1. We will use the `admin` user for all gNOI operations. The password is provided in the sheet distributed during the hackathon and is available as an environment variable in your hackathon instance.

For this test, we will be using the gNOI `System` service's `Time` RPC to get the current time on :material-router: PE1.

/// tab | cmd

``` bash
gnoic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure system time
```
///
/// tab | expected output

``` bash
+-----------------------------+------------------------------------------+---------------------+
|         Target Name         |                   Time                   |      Timestamp      |
+-----------------------------+------------------------------------------+---------------------+
| clab-srexperts-pe1:57400    | 2026-04-25 22:32:58.749420494 +0300 EEST | 1745609578749420494 |
+-----------------------------+------------------------------------------+---------------------+
```
///

Hopefully you received the current system timestamp from :material-router: PE1 and this confirms that gNOI is enabled on the router.  If you did not, double-check the router's configuration and ensure you provided the expected username and password to your `gnoic` command.  You should also ensure you are providing the `--insecure` flag to `gnoic`.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Use gNOIc to perform a remote ping from SR OS

Our first task is to prepare the `gnoic` command to check the reachability of an IP address from :material-router: PE1.

We will be using the gNOI `System` `Ping` RPC for this purpose. We will check the reachability of the system IPv4 address of :material-router: PE2. This addresses matches `10.46.${INSTANCE_ID}.22`, replace the variable by your assigned ID to find the address you should use.

Run the below command from your hackathon instance. Replace `$EVENT_PASSWORD` with the password from your hackathon leaflet.

/// tab | cmd

``` bash
gnoic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure system ping --destination 10.46.${INSTANCE_ID}.22 --ns Base --count 1 --wait 1s
```
///
/// tab | expected output for instance 2

``` bash
64 bytes from 10.46.2.22: icmp_seq=1 ttl=63 time=5.352ms
--- 10.46.2.22 ping statistics ---
1 packets sent, 1 packets received, 0.00% packet loss
round-trip min/avg/max/stddev = 5.352/5.352/5.352/0.000 ms
```
///

You have confirmed that the IP is reachable from :material-router: PE1. The `--ns` option in the above command indicates the router instance used for the reachability test.

To get the output in JSON format, add the `--format json` option.

/// tab | cmd

``` bash
gnoic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure system ping --destination 10.46.${INSTANCE_ID}.22 --ns Base --count 1 --wait 1s --format json
```
///
/// tab | expected output for instance 2

``` json
{
  "target": "clab-srexperts-pe1:57400",
  "response": {
    "source": "10.46.2.22",
    "time": 2932000,
    "bytes": 64,
    "sequence": 1,
    "ttl": 63
  }
}
{
  "target": "clab-srexperts-pe1:57400",
  "response": {
    "source": "10.46.2.22",
    "time": 228446652,
    "sent": 1,
    "received": 1,
    "min_time": 2932000,
    "avg_time": 2932000,
    "max_time": 2932000
  }
}
```
///

### Create an Ansible playbook to check reachability of multiple IPs

With the knowledge gained from the previous task, create an Ansible playbook to check the reachability of the following IPs from :material-router: PE1 and :material-router: PE3. Keep the router instance name as a variable. All IPs should be reachable using `Base` router instance.

You may use either a CLI, or JSON formatted response.

| IP | VRF |
|----------|----------|
| 10.46.${INSTANCE_ID}.22 | Base |
| 10.46.${INSTANCE_ID}.24 | Base |
| 10.46.${INSTANCE_ID}.11 | Base |

These are the `system` loopback IPs on :material-router: PE2, :material-router: PE4 and :material-router: P1.

To take this challenge up a notch, add logic to return an error when an IP address is not reachable. Test this using a random IP (for example, `3.3.3.3`) in your Ansible inventory.

Feel free to consult any documentation or your favorite AI tool to assist you with this activity.

The expected result of your playbook execution is that for each target host you have three succesful task executions and possibly a single failed task, if you ended up adding a non-existant IP address to your inventory as a test. Based on your findings and results in this staging environment you'll have a strong foundational playbook you can easily extend with more IP addresses and targets to address your network reachability challenges.

### Solution

If you need ideas or the complete solution, refer to the playbook below.

Here's a sample inventory file. Make sure to replace $EVENT_PASSWORD and $INSTANCE_ID with the information provided on your hackathon leaflet or rely on the environment variables.

/// details | Ansible inventory
    type: code
```yaml
all:
  children:
    nokia_routers:
      hosts:
        # Define each router and its management IP here
        pe1:
          ansible_host: clab-srexperts-pe1
        pe3:
          ansible_host: clab-srexperts-pe3

      vars:
        # Common credentials for all switches in this group
        gnoi_port: 57400
        gnoi_user: admin
        gnoi_pass: $EVENT_PASSWORD
        
        # The universal ping list
        ping_targets:
          - { ip: "10.46.${INSTANCE_ID}.22", vrf: "Base" }
          - { ip: "10.46.${INSTANCE_ID}.24", vrf: "Base" }
          - { ip: "10.46.${INSTANCE_ID}.11", vrf: "Base" }
          - { ip: "3.3.3.3", vrf: "Base" }
```
///

This sample Ansible playbook implements the desired behavior. Is it done in the way you expected or would you go about this differently?

/// details | Ansible playbook
    type: code
```yaml
---
- name: gNOI Ping for SReXperts
  hosts: nokia_routers
  gather_facts: false
  connection: local

  tasks:
    - name: Run gNOIc
      ansible.builtin.shell: >
        gnoic -a {{ ansible_host }}:{{ gnoi_port }} 
        -u {{ gnoi_user }} 
        -p {{ gnoi_pass }} 
        --insecure 
        system ping 
        --destination {{ item.ip }} 
        --ns {{ item.vrf }}
        --count 1
        --wait 1s
      loop: "{{ ping_targets }}"
      register: raw_ping_results
      changed_when: false
      ignore_errors: true 

    - name: Report Successful Pings
      vars:
        is_ok: "{{ '0.00% packet loss' in item.stdout and '1 packets received' in item.stdout }}"
      ansible.builtin.debug:
        msg: "[{{ inventory_hostname }}] {{ item.item.ip }} ({{ item.item.vrf }}) -> OK"
      when: is_ok
      loop: "{{ raw_ping_results.results }}"
      loop_control:
        label: "{{ item.item.ip }}"

    - name: Report Failed Pings
      vars:
        is_ok: "{{ '0.00% packet loss' in item.stdout and '1 packets received' in item.stdout }}"
      ansible.builtin.fail:
        msg: "[{{ inventory_hostname }}] {{ item.item.ip }} ({{ item.item.vrf }}) -> NOK"
      when: not is_ok
      loop: "{{ raw_ping_results.results }}"
      loop_control:
        label: "{{ item.item.ip }}"
      register: failure_check
      ignore_errors: false
      failed_when: false
```
///

The playbook and inventory as shown above produce the output below.

/// details | Ansible output for instance 2
    type: code
```yaml
PLAY [gNOI Ping for SReXperts] ***********************************************************************************************

TASK [Run gNOIc] *************************************************************************************************************
ok: [pe1] => (item={'ip': '10.46.2.22', 'vrf': 'Base'})
ok: [pe3] => (item={'ip': '10.46.2.22', 'vrf': 'Base'})
ok: [pe1] => (item={'ip': '10.46.2.24', 'vrf': 'Base'})
ok: [pe3] => (item={'ip': '10.46.2.24', 'vrf': 'Base'})
ok: [pe1] => (item={'ip': '10.46.2.11', 'vrf': 'Base'})
ok: [pe3] => (item={'ip': '10.46.2.11', 'vrf': 'Base'})
failed: [pe1] (item={'ip': '3.3.3.3', 'vrf': 'Base'}) => {"ansible_loop_var": "item", "changed": false, "cmd": "gnoic -a clab-srexperts-pe1:57400  -u admin  -p $EVENT_PASSWORD  --insecure  system ping  --destination 3.3.3.3  --ns Base --count 1 --wait 1s\n", "delta": "0:00:00.333641", "end": "2026-04-23 14:29:15.775995", "item": {"ip": "3.3.3.3", "vrf": "Base"}, "msg": "non-zero return code", "rc": 1, "start": "2026-04-23 14:29:15.442354", "stderr": "time=\"2026-04-23T14:29:15Z\" level=error msg=\"\\\"clab-srexperts-pe1:57400\\\" rcv Ping stream failed: rpc error: code = NotFound desc = MINOR: GMI #2402: Destination address unreachable - address '3.3.3.3' - No route to destination - 'router-instance' \\\"Base\\\"\"\ntime=\"2026-04-23T14:29:15Z\" level=error msg=\"\\\"clab-srexperts-pe1:57400\\\" System Ping failed: rpc error: code = NotFound desc = MINOR: GMI #2402: Destination address unreachable - address '3.3.3.3' - No route to destination - 'router-instance' \\\"Base\\\"\"\nError: there was 1 error(s)", "stderr_lines": ["time=\"2026-04-23T14:29:15Z\" level=error msg=\"\\\"clab-srexperts-pe1:57400\\\" rcv Ping stream failed: rpc error: code = NotFound desc = MINOR: GMI #2402: Destination address unreachable - address '3.3.3.3' - No route to destination - 'router-instance' \\\"Base\\\"\"", "time=\"2026-04-23T14:29:15Z\" level=error msg=\"\\\"clab-srexperts-pe1:57400\\\" System Ping failed: rpc error: code = NotFound desc = MINOR: GMI #2402: Destination address unreachable - address '3.3.3.3' - No route to destination - 'router-instance' \\\"Base\\\"\"", "Error: there was 1 error(s)"], "stdout": "", "stdout_lines": []}
...ignoring
failed: [pe3] (item={'ip': '3.3.3.3', 'vrf': 'Base'}) => {"ansible_loop_var": "item", "changed": false, "cmd": "gnoic -a clab-srexperts-pe3:57400  -u admin  -p $EVENT_PASSWORD  --insecure  system ping  --destination 3.3.3.3  --ns Base --count 1 --wait 1s\n", "delta": "0:00:00.340032", "end": "2026-04-23 14:29:15.846696", "item": {"ip": "3.3.3.3", "vrf": "Base"}, "msg": "non-zero return code", "rc": 1, "start": "2026-04-23 14:29:15.506664", "stderr": "time=\"2026-04-23T14:29:15Z\" level=error msg=\"\\\"clab-srexperts-pe3:57400\\\" rcv Ping stream failed: rpc error: code = NotFound desc = MINOR: GMI #2402: Destination address unreachable - address '3.3.3.3' - No route to destination - 'router-instance' \\\"Base\\\"\"\ntime=\"2026-04-23T14:29:15Z\" level=error msg=\"\\\"clab-srexperts-pe3:57400\\\" System Ping failed: rpc error: code = NotFound desc = MINOR: GMI #2402: Destination address unreachable - address '3.3.3.3' - No route to destination - 'router-instance' \\\"Base\\\"\"\nError: there was 1 error(s)", "stderr_lines": ["time=\"2026-04-23T14:29:15Z\" level=error msg=\"\\\"clab-srexperts-pe3:57400\\\" rcv Ping stream failed: rpc error: code = NotFound desc = MINOR: GMI #2402: Destination address unreachable - address '3.3.3.3' - No route to destination - 'router-instance' \\\"Base\\\"\"", "time=\"2026-04-23T14:29:15Z\" level=error msg=\"\\\"clab-srexperts-pe3:57400\\\" System Ping failed: rpc error: code = NotFound desc = MINOR: GMI #2402: Destination address unreachable - address '3.3.3.3' - No route to destination - 'router-instance' \\\"Base\\\"\"", "Error: there was 1 error(s)"], "stdout": "", "stdout_lines": []}
...ignoring

TASK [Report Successful Pings] ***********************************************************************************************
ok: [pe1] => (item=10.46.2.22) => {
    "msg": "[pe1] 10.46.2.22 (Base) -> OK"
}
ok: [pe1] => (item=10.46.2.24) => {
    "msg": "[pe1] 10.46.2.24 (Base) -> OK"
}
ok: [pe3] => (item=10.46.2.22) => {
    "msg": "[pe3] 10.46.2.22 (Base) -> OK"
}
ok: [pe1] => (item=10.46.2.11) => {
    "msg": "[pe1] 10.46.2.11 (Base) -> OK"
}
skipping: [pe1] => (item=3.3.3.3) 
ok: [pe3] => (item=10.46.2.24) => {
    "msg": "[pe3] 10.46.2.24 (Base) -> OK"
}
ok: [pe3] => (item=10.46.2.11) => {
    "msg": "[pe3] 10.46.2.11 (Base) -> OK"
}
skipping: [pe3] => (item=3.3.3.3) 

TASK [Report Failed Pings] ***************************************************************************************************
skipping: [pe1] => (item=10.46.2.22) 
skipping: [pe1] => (item=10.46.2.24) 
skipping: [pe1] => (item=10.46.2.11) 
skipping: [pe3] => (item=10.46.2.22) 
skipping: [pe3] => (item=10.46.2.24) 
ok: [pe1] => (item=3.3.3.3)
skipping: [pe3] => (item=10.46.2.11)
ok: [pe3] => (item=3.3.3.3)

PLAY RECAP *******************************************************************************************************************
pe1                        : ok=2    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
pe3                        : ok=2    changed=0    unreachable=0    failed=1    skipped=0    rescued=0    ignored=1   
```
///

## Additional Task

### Use gNOIc to get the configuration file from SR OS

Your final task is to setup a remote configuration file backup service on your hackathon instance.

Here are some guidelines to help you:

- The default SR OS configuration file is `cf3:/config.cfg`
- Use the gNOI `File` `Stat` RPC to check the presence of the config file. Use option `--path` to specify the config file path
- Create a directory on your hackathon instance to store the config backups
- Use gNOI `File` `Get` RPC to transfer the config file to your backup directory. Use the `--file` option to specify the config file path and `--dst` to specify the destination directory.
- Verify the config is now present on your hackathon instance
- Create an Ansible playbook to take configuration backups of :material-router: PE2 and :material-router: PE3.

### Solution

If you need help, refer to the steps below.

Use the gNOI `File` `Stat` RPC to check the presence of the config file. The default configuration file for SR OS is located at `cf3:/config.cfg`.

/// tab | cmd

``` bash
gnoic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure file stat --path cf3:/config.cfg
```
///
/// tab | expected output

``` bash
+--------------------------+-----------------+----------------------+------------+------------+-------+
|       Target Name        |      Path       |     LastModified     |    Perm    |   Umask    | Size  |
+--------------------------+-----------------+----------------------+------------+------------+-------+
| clab-srexperts-pe1:57400 | cf3:\\config.cfg | 2026-04-21T10:05:02Z | -rwxrwxrwx | -rwxrwxrwx | 41603 |
+--------------------------+-----------------+----------------------+------------+------------+-------+
```
///

You confirmed that the configuration file exists and you also got information on the last modified timestamp and the size of the file.

Now retrieve this file and store it on your hackathon instance.

Create a directory called `my-backups` on your hackathon instance to store the configuration backup file.

```
mkdir -p ~/my-backups/pe1
```

Use the gNOI `File` `Get` RPC to retrieve the file from :material-router: pe1.

/// tab | cmd

``` bash
gnoic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure file get --file cf3:/config.cfg --dst ~/my-backups/pe1
```
///
/// tab | expected output

``` bash
INFO[0000] "clab-srexperts-pe1:57400" received 41603 bytes 
INFO[0000] "clab-srexperts-pe1:57400" file "cf3:\config.cfg" saved 
```
///

Check that the `File` `Get` operation was successful and the file exists on your groups hackathon instance.

/// tab | cmd

``` bash
ls -lrt ~/my-backups/pe1/cf3:/
```
///
/// tab | expected output

``` bash
❯ ls -lrt ~/my-backups/pe1/cf3:/
total 44
-rw-rw-r-- 1 nokia nokia 41603 Apr 23 14:37 config.cfg
```
///

/// note
The destination file is created on the same path as the origin. In this case `cf3:/config.cfg`<br>
///

Open the configuration backup to verify the contents match those on the router.

Re-use the Ansible solution provided above to build an Ansible playbook for configuration backups.

## Summary

Congratulations! If you made it this far, you have successfully completed the activity to check the reachability of your applications and take the configuration backups of all your network devices. With the work you have put in, you should now have a good understanding of the following topics:

- Using gRPC to perform activities on a remote router
- Using gNOI service and Ansible to automate network reachability tests
- Using the gNOI service to manipulate the file system
- Using gNOI service and Ansible to automate configuration backups

Good job in completing all the tasks in this activity!


