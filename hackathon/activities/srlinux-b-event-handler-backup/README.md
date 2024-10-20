# Triggering remote backups on commit using SR Linux Event Handler

| Item              | Details                                                            |
| ----------------- | ------------------------------------------------------------------ |
| Short Description | Use SR Linux Event Handler System to perform configuration backups |
| Skill Level       | Beginner/Intermediate                                              |
| Tools Used        | SR Linux, Event Handler, Python                                    |

When using SR Linux, a smart thing to do is set up an automatic configuration save every time a commit has been made. While this can be achieved with a system configuration setting, there is still an inherent risk of losing all your changes when the router suddenly fails. Following the [3-2-1 rule](https://www.seagate.com/de/de/blog/what-is-a-3-2-1-backup-strategy/), which says that you should maintain:

- 3 copies of the data
- 2 different media types
- 1 copy offsite

Let's find a way to copy the locally-stored configuration to a remote location every time a commit is done, effectively creating a backup solution for your SR Linux device config.

## Objective

Use the SR Linux [Event Handler](https://documentation.nokia.com/srlinux/24-7/books/event-handler/event-handler-overview.html) system to trigger a copy of the startup configuration file to a remote location every time a commit is done.

## Accessing a lab node

You can run this exercise on any SR Linux device in the topology. For example, on `clab-srexperts-leaf21` node. To login to this device, execute:

```bash
ssh admin@clab-srexperts-leaf21
```

## Documentation resources

Below are some resources you might find interesting:

- [Event handler documentation](https://documentation.nokia.com/srlinux/24-7/books/event-handler/event-handler-configuration.html)
- [SR Linux YANG browser](https://yang.srlinux.dev/v24.7.1): use this to look for gNMI paths
- [Introduction to operational groups tutorial](https://learn.srlinux.dev/tutorials/programmability/event-handler/oper-group/oper-group-intro/): a different use-case leveraging the Event Handler by shutting down all downlink interfaces when the BGP sessions to both route reflectors fails

## Step 1: creating the backups directory

As the whole purpose of this exercise is to store the device backups outside of the device filesystem, we first need to create a remote backup location that is reachable from an SR Linux device. For example, we can use the VM that runs the lab as a backup (`<groupID>.srexperts.net`).

While logged in to a VM with the standard `nokia` user, create the `~/backups` directory.

## Step 2: Create the Event-Handler script file

We need to create our Python event handling script on an SR Linux device, and prepare the event handler configuration context that would execute the script.

First of all, let's create an empty event handler script file, you will populate it later.

1. Log into the SR Linux CLI (if you haven't done so)
2. go to the Linux shell (by typing `bash`)
3. and create the empty file `remote-backup.py` in the predefined location - `/etc/opt/srlinux/eventmgr`. This is a well-known directory where Event Handler scripts are meant to be stored.
4. Make this file executable by running `chmod +x remote-backup.py`

Below is a run down of the steps you have to take:

```bash
--{ running }--[  ]--
A:leaf21# bash
admin@leaf21:~$ cd /opt/srlinux/eventmgr
admin@leaf21:/opt/srlinux/eventmgr$ touch remote-backup.py
admin@leaf21:/opt/srlinux/eventmgr$ chmod +x remote-backup.py
```

Then listing the contents of the directory should show the newly created file.

```bash
admin@leaf21:/opt/srlinux/eventmgr$ ll
admin@g2-leaf21:/etc/opt/srlinux/eventmgr$ ll
total 16
drwxrwxr-x+  2 srlinux srlinux  4096 Oct 10 13:42 .
drwxrwxrwx+ 14 srlinux srlinux  4096 Oct 10 07:18 ..
-rwxrwxr-x+  1 admin   ntwkuser    0 Oct 10 13:42 remote-backup.py
```

## Step 3: create the Event Handler instance

With the script file created, we can now create the Event Handler instance that will execute the script based on the "events".

Using the [Event Handler documentation](https://documentation.nokia.com/srlinux/24-7/books/event-handler/event-handler-configuration.html) try to create the configuration for the Event Handler context. It should contain the following:

- The location to the python script you created in step 1
- A path monitoring the last time the configuration was changed (tip: use the [SRL YANG browser](https://yang.srlinux.dev/v24.7.1))
- A static value indicating the backup destination (`nokia@<groupID>.srexperts.net:~/backups`). This destination is meant to be used in the script to instruct `scp` where to copy the file to.

If you feel like stuck, you can find a configuration snippet that you can paste in the CLI `candidate` mode [here](./solution/eh.cfg).

## Step 4: Enabling key-based SSH authentication

To copy the config file to the remote location, SR Linux can leverage its underlying Linux OS and use SCP with the address of the VM that hosts the lab. To ensure no password needs to be provided to the scp command, you need to set up key-based authentication first. To do so we will generate a set of keys on SR Linux first, and then copy the public key to the VM.

Starting again with the Linux shell of SR Linux, make use of the `ssh-keygen` command to generate the key pair and leave the passphrase empty.

Pay attention to the key location, we will have to deviate from the default and put the key in `/home/admin` instead of the default `~/.ssh`.

```bash
--{ running }--[  ]--
A:leaf21# bash
admin@g2-leaf21:~$ ssh-keygen -f ~/id_rsa -P ''
Generating public/private rsa key pair.
Your identification has been saved in /home/admin/id_rsa
Your public key has been saved in /home/admin/id_rsa.pubssh-cop 
```

Now that the keys are generated, copy the public key to the VM that hosts your lab with using `ssh-copy-id` and the address of your VM, which is `nokia@<groupID>.srexperts.net` (of course substitute, the group ID with your actual ID). The example below is for GroupID: 2, hence the address is `nokia@2.srexperts.net`.

```bash
admin@g2-leaf21:~$ sudo ssh-copy-id -i ~/id_rsa nokia@2.srexperts.net
```

Now we can test if the password-less SSH access is working, by logging in to the VM address:

```bash
root@leaf21:/home/admin# ssh -i ~/id_rsa nokia@<groupID>.srexperts.net
```

If all goes well, you should be logged in to the VM and see the VM's prompt.

## Step 5: develop the `remote-backup.py` script

Using the documentation resources above, find a way to achieve the requested backup functionality. A list of intermediary steps can be found below for inspiration:

1) Parse the input paths and print their values
2) Parse the input options and print their values
3) Obtain the timestamp of the system's last configuration change
4) Find the location where your SR Linux's configuration is being stored (hint, execute `save startup` on your box)
5) Copy the startup configuration file to the target destination

**NOTE:**
You can instruct the event handler to run a bash script: the returned `action` list should contain an object with a key `run-script` and a dictionary value containing the key `cmdline`. The cmdline template is provided below. For a hint, closely inspect the returned format by the [oper-group script](https://learn.srlinux.dev/tutorials/programmability/event-handler/oper-group/script/)

```python
"cmdline": f"sudo ip netns exec srbase-mgmt /usr/bin/scp -i ~/id_rsa {startup_config} {target}/config-{timestamp}.json"
```

Getting to know a new framework, even a slim one like Event Handler can take time, if you just want to see it in action, peek into the [solutions](solution/solution.py) to see the resulting script. You can paste it in your `remote-backup.py` file created earlier.

## Step 6 - test

This activity is cleared when a user does `commit save stay` or `save startup` and the startup file is correctly copied to the target destination. The file must:

- contain the changes that were made (hence the `save` to commit them to the startup file)
- contain the timestamp of when the last change was done (important!/to  the name should be different every time the script is executed)

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

## Step 7 - and beyond

Try out one of the other labs, or extend this script even further using your own imagination. Possible extensions are:

- include the user that committed the changes into the filename
