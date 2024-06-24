# Triggering remote backups on commit using SR Linux Event Handler

| Item              | Details                                                            |
| ----------------- | ------------------------------------------------------------------ |
| Short Description | Use SR Linux Event Handler System to perform configuration backups |
| Skill Level       | Beginner                                                           |
| Tools Used        | SR Linux, Event Handler, Python                                    |

When using SR Linux, a smart thing to do is set up an automatic configuration save every time a commit has been made. While this can be achieved with a system configuration setting, there is still an inherent risk of losing all your changes when the router suddenly fails. Following the [3-2-1 rule](https://www.seagate.com/de/de/blog/what-is-a-3-2-1-backup-strategy/), which says that you should maintain:

- 3 copies of the data
- 2 different media types
- 1 copy offsite

We clearly need to do some more work. We should find a way to copy the saved configuration to a remote location.

## Objective

In this lab, you will use the SR Linux [Event Handler](https://documentation.nokia.com/srlinux/24-3/books/event-handler/event-handler-overview.html) system to trigger a copy of the startup configuration file every time a commit is done to a remote location.

## Accessing a lab node

You can run this exercise on any SR Linux device in the topology. For example, on `clab-srexperts-leaf21` node. To login to this device, execute:

```bash
ssh admin@clab-srexperts-leaf21
```

## Documentation resources

Below are some resources you might find interesting:

- [Event handler documentation](https://documentation.nokia.com/srlinux/24-3/books/event-handler/event-handler-configuration.html?Chandler#event-handler-config)
- [SRLinux YANG browser](https://yang.srlinux.dev/v24.3.2): use this to look for gNMI paths
- [Introduction to operational groups tutorial](https://learn.srlinux.dev/tutorials/programmability/event-handler/oper-group/oper-group-intro/): a different use-case leveraging the Event Handler by shutting down all downlink interfaces when the BGP sessions to both route reflectors fails

## Step 1: creating the backups directory

As the whole purpose of this exercise is to store the device backups outside of the device filesystem, we first need to create a remote backup location that is reachable from an SR Linux device. For example, we can use the VM that runs the lab as a backup (`<your-lab>.srexperts.net`).

While logged in to a VM with the standard `nokia` user, create the `~/backups` directory.

## Step 2: Create script file

We need to create our Python event handling script on an SR Linux box, and prepare the event handler configuration context:

Log into the node, go to the linux CLI (by typing `bash network-instance mgmt`) and create the script `remote-backup.py` in the `/etc/opt/srlinux/eventmgr` directory.

```bash
--{ running }--[  ]--
A:leaf21# bash network-instance mgmt
admin@leaf21:~$ cd /opt/srlinux/eventmgr
admin@leaf21:/opt/srlinux/eventmgr$ sudo vim remote-backup.py
admin@leaf21:/opt/srlinux/eventmgr$ sudo chmod +x remote-backup.py
admin@leaf21:/opt/srlinux/eventmgr$ ls -l .
total 36
-rwxrwxrwx 1 root root 4587 Apr 10 23:01 change-history-with-yang.py
-rwxrwxrwx 1 root root 2826 Apr 10 23:01 change-history.py
-rwxrwxrwx 1 root root 6835 Apr 10 23:01 lldp-interface-descriptions.py
-rwxrwxrwx 1 root root 4015 Apr 10 23:01 oper-group.py
-rwxrwxrwx 1 root root 6230 Apr 10 23:01 perf-mon-with-yang.py
-rwxr-xr-x 1 root root    5 May 15 11:08 remote-backup.py
```

## Step 3: create the Event Handler instance

Using the [documentation](https://documentation.nokia.com/srlinux/24-3/books/event-handler/event-handler-configuration.html?handler#event-handler-config), refer to the python script you created in step 1. The following information should be added to the configuration context:

- The location to the python script you created in step 1
- A path monitoring the last time the configuration was changed (tip: use the [SRL YANG browser](https://yang.srlinux.dev/v24.3.2))
- A static value indicating the target destination (`nokia@<your-lab-ip>.srexperts.net:~/backups`)

**NOTE:**

To copy files to the remote location, you can use SCP **with the IP address of the hypervisor**. To ensure no password needs to be provided to the scp command, it is advised you set up key-authentication first. Below is a configuration session where this is demonstrated:

- Leave the password blank
- Make sure to test afterwards! This will add the hypervisor to the `known_hosts` file

```bash
--{ running }--[  ]--
A:leaf21# bash network-instance mgmt
admin@leaf21:~$ ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/home/admin/.ssh/id_rsa): /home/admin/id_rsa
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/admin/id_rsa
Your public key has been saved in /home/admin/id_rsa.pub
The key fingerprint is:
SHA256:XvotnwqZZoVbfl4seGmoy96GR4t1/RkAw8o2KmmgONE admin@leaf21
The key's randomart image is:
+---[RSA 3072]----+
|          .      |
|           +     |
| .      . . o    |
|. E.     *   .   |
|... . . S =  ..  |
|o.   + o Xoo.o.. |
| .  . . X=+o* o.o|
|       +o==* + ..|
|       .=+++=    |
+----[SHA256]-----+
```

On the hypervisor: add the contents of the generated `~/id_rsa.pub` file on your SRL box to the `~/.ssh/authorized_keys` file

Validation (on the SRL box)

```bash
root@leaf21:/home/admin# ssh -i ~/id_rsa nokia@10.128.<your_lab>.1
Linux rd-srx-ws1-155afda 6.1.0-0.deb11.17-cloud-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.69-1~bpo11+1 (2024-01-05) x86_64

Last login: Wed May 15 14:32:13 2024 from 10.150.29.173
❯ 
```

## Step 4: develop the `remote-backup.py` script

Using the documentation resources above, find a way to achieve the requested backup functionality. A list of intermediary steps can be found below for inspiration:

1) Parse the input paths and print their values
2) Parse the input options and print their values
3) Obtain the timestamp of the system's last configuration change
4) Find the location where your SRL's configuration is being stored (hint, execute `save startup` on your box)
5) Copy the startup configuration file to the target destination

**NOTE:**
You can instruct the event handler to run a bash script: the returned `action` list should contain an object with a key `run-script` and a dictionary value containing the key `cmdline`. The cmdline template is provided below. For a hint, closely inspect the returned format by the [oper-group script](https://learn.srlinux.dev/tutorials/programmability/event-handler/oper-group/script/)

```python
"cmdline": f"sudo ip netns exec srbase-mgmt /usr/bin/scp -i ~/id_rsa {startup_config} {target}/config-{timestamp}.json"
```

## Step 5 - test

This lab has been completed when the user does `admin save stay` and the startup file is correctly copied to the target destination. The file must:

- contain the changes that were made (hence the `save` to commit them to the startup file)
- contain the timestamp of when the last change was done (important! the name should be different every time the script is executed)

Two interesting commands:

1) reloading the python file after you've made changes to it: `/ tools system event-handler instance <instance> reload`
2) checking the execution output of your script: `/ info from state system event-handler instance <instance>`

Example:

```
--{ running }--[ system event-handler ]--
A:leaf21# / tools system event-handler instance backup-config-on-changes reload
/system/event-handler/instance[name=backup-config-on-changes]:
    instance backup-config-on-changes reloaded
```

If you did not manage to implement the solution fully, you can find an example solution [here](solution/solution.py)

## Step 5 - and beyond

Try out one of the other labs, or extend this script even further using your own imagination. Possible extensions are:

- include the user that committed the changes into the filename
