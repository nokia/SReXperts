# Using gNOI with SR Linux

| Item | Details |
| --- | --- |
| Short Description | Use gNOI file service for managing files on SR Linux |
| Skill Level | Beginner |
| Tools Used | SR Linux, gNOIc, Programming language of your choice |

The gRPC Network Operations Interface (gNOI) defines a set of gRPC-based micro-services for executing operational commands on network devices. [gNOI service](https://github.com/openconfig/gnoi) is defined by OpenConfig.

gNOI supports Remote Procedure Calls (RPC) that can be used for Device reset, File operations, Hardware health check, Software upgrade and some general services like ping. gNOI like other gRPC services works in a client-server model where the client sends a RPC request to the server which executes the requested action and returns a response.

```
gNOI client (on VM) -------------(Request)-------------> gNOI server (SRLinux)
gNOI client (on VM) <------------(Response)------------- gNOI server (SRLinux)
```

For an easy read on gNOI RPCs and their parameters, visit [gNxI Documentation](https://gnxi.srlinux.dev/) developed by Nokia SR Linux team using the same gNxI RPC information from GitHub.

Refer to [Nokia SR Linux guide](https://documentation.nokia.com/srlinux/24-3/books/system-mgmt/gnoi-system-mgmt.html) for more information on SR Linux implementation of gNOI services.

If you prefer to listen rather than read, take a look at this [NANOG Video](https://www.youtube.com/watch?v=DldQtjPjKDk) by Nokia on gNOI services and a demo of SR Linux software upgrade using gNOI.

There are many clients that support gNOI services, the most common one is [gNOIc](https://gnoic.kmrd.dev/) developed by Nokia.

## SReXperts Hackathon

As part of this SReXperts Hackathon, we will be exploring gNOI file services on SR Linux.

## gNOI File Service

In the gNOI file service, OpenConfig defines a generic interface to perform file operational tasks. For information see [gNOI specification](https://github.com/openconfig/gnoi/blob/master/file/file.proto)

SR Linux supports the following gNOI file RPCs:

- Get RPC 
- Put RPC
- Stat RPC
- Remove RPC

## Getting Ready

### SR Linux Configuration for gNOI

Choose a SR Linux device in your topology.

Login to the SR Linux device and configure/verify the following. When deploying a SR Linux container using [Containerlab](https://containerlab.dev/), gRPC and gNOI are enabled by Containerlab by default. It is ready to use.

The below example is provided as a reference for an insecure connection that should only be used in lab environments. By default, Containerlab sets up a secured TLS connection for gRPC services.

```
set / system grpc-server mgmt admin-state enable
set / system grpc-server mgmt network-instance mgmt
set / system grpc-server mgmt services [ gnoi ]

```

To view configuration, use `info from running /system grpc-server mgmt`.
Below is the actual configuration pushed by Containerlab to all SR Linux nodes. Check that this configuration exists in your lab environment.

```
--{ running }--[  ]--
A:leaf11# info system grpc-server mgmt
    system {
        grpc-server mgmt {
            admin-state enable
            rate-limit 65000
            tls-profile clab-profile
            network-instance mgmt
            trace-options [
                request
                response
                common
            ]
            services [
                gnmi
                gnoi
                gribi
                p4rt
            ]
            unix-socket {
                admin-state enable
            }
        }
    }

--{ running }--[  ]--

--{ running }--[  ]--
A:leaf11# info system tls server-profile clab-profile
    system {
        tls {
            server-profile clab-profile {
                key $aes1$ATDdSPG9IXSBnW8=$/IvtXhKLj5l1H9
                certificate "-----BEGIN CERTIFICATE-----
MIID0jCCArqgAwIBAgICBnowDQYJKoZIhvcNAQELBQAwVTELMAkGA1UEBhMCVVMx
ZVmupvtACHHh5GiTgiXO9xXoATYDVA==
-----END CERTIFICATE-----
"
                authenticate-client false
            }
        }
    }

--{ running }--[  ]--
```


### gNOI client

gNOIc is already installed on the server that runs the lab topology.

To test this, run the below command on the VM:

```
# gnoic version
version : 0.0.21
 commit : bc327f6
   date : 2024-04-25T00:20:06Z
 gitURL : https://github.com/karimra/gnoic
   docs : https://gnoic.kmrd.dev  
```

## Introduction to gNOI File RPCs

We are going to do a quick review of the gNOI file RPCs supported on SR Linux.

After this review, we will start using gNOI to simulate real world use cases.

### Listing Files on SR Linux Filesystem

We are going to start this exercise by listing the files on the SR Linux filesystem.

The Stat RPC returns metadata about files on the target node.

If the path specified in the StatRequest references a directory, the StatResponse returns the metadata for all files and folders, including the parent directory. If the path references a direct path to a file, the StatResponse returns metadata for the specified file only.

The target node returns an error if:
- The file does not exist.
- An error occurs while accessing the metadata.

Let's go ahead and list files in the /opt/srlinux directory. We will be using the `--skip-verify` flag in gNOIc to indicate that the target should skip the signature verification steps.

```
# gnoic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify file stat --path /opt/srlinux
+-----------------------------+-------------------------+---------------------------+------------+------------+------+
|         Target Name         |          Path           |       LastModified        |    Perm    |   Umask    | Size |
+-----------------------------+-------------------------+---------------------------+------------+------------+------+
| clab-srexperts-leaf11:57400 | /opt/srlinux/appmgr     | 2024-05-04T02:52:34+03:00 | drwxr-xr-x | -----w--w- | 0    |
|                             | /opt/srlinux/bin        | 2024-05-04T02:52:44+03:00 | drwxr-xr-x | -----w--w- | 0    |
|                             | /opt/srlinux/python     | 2024-02-16T04:54:07+02:00 | drwxr-xr-x | -----w--w- | 0    |
|                             | /opt/srlinux/snmp       | 2024-05-04T02:52:37+03:00 | drwxr-xr-x | -----w--w- | 0    |
|                             | /opt/srlinux/systemd    | 2024-05-04T02:52:34+03:00 | drwxr-xr-x | -----w--w- | 0    |
|                             | /opt/srlinux/usr        | 2024-02-16T04:54:07+02:00 | drwxr-xr-x | -----w--w- | 0    |
|                             | /opt/srlinux/var        | 2024-02-16T04:54:18+02:00 | drwxr-xr-x | -----w--w- | 0    |
|                             | /opt/srlinux/ztp        | 2024-05-04T02:52:37+03:00 | drwxr-xr-x | -----w--w- | 0    |
+-----------------------------+-------------------------+---------------------------+------------+------------+------+

```

Tip - Try adding the `--format json` option at the end to see the above output in json format.

### Getting Files from SR Linux

Next we are going to transfer a file from the device to our host VM.

The Get RPC reads and streams the contents of a file from a target node to the client using sequential messages, and sends a final message containing the hash of the streamed data before closing the stream.

The target node returns an error if:

- An error occurs while reading the file.
- The file does not exist.

Create a directory on the VM and name it `srl-gnoi-<yourname>`. We will transfer the `srl_boot.log` file from the router to this directory. Verify the file was transferred to the VM.

```
For example, if your name is Chris, the directory will be named srl-gnoi-chris.

# mkdir srl-gnoi-chris
# cd srl-gnoi-chris
```

```
# gnoic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify file get --file /var/log/srlinux/srl_boot.log --dst .
INFO[0000] "clab-srexperts-leaf11:57400" received 27572 bytes 
INFO[0000] "clab-srexperts-leaf11:57400" file "/var/log/srlinux/srl_boot.log" saved 
```

```
# tail var/log/srlinux/srl_boot.log
[23:52:35.906]:[sr_boot_run.sh]: Entering srl_boot_run.sh
[23:52:35.923]:[11_sr_createuser.sh]: Executed: 'sudo sed -i s/^[       ]*#[    ]*\(HOME_MODE[  ]\+0700.*\)/\1/ /etc/login.defs'
[23:52:35.955]:[11_sr_createuser.sh]: Executed: '/usr/sbin/groupadd ntwkadmin -g 997'
[23:52:35.957]:[11_sr_createuser.sh]: Created group ntwkadmin
[23:52:35.988]:[11_sr_createuser.sh]: Executed: '/usr/sbin/groupadd ntwkuser -g 996
```

### Putting Files to SR Linux

Now we are ready to transfer a file from our VM to the SR Linux device.

The Put RPC streams data to the target node and writes the data to a file. The client streams the file using sequential messages. The initial message contains information about the filename and permissions. The final message includes the hash of the streamed data.

The target node returns an error if:

- An error occurs while writing the data.
- The location does not exist.

Select or create a file on your VM (in your own directory) to be transferred over to the device. Verify the file transferred on the router.

```
# echo "show interface" > show-int.txt
```

```
# gnoic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify file put --file show-int.txt --dst /home/admin/show-int.txt
INFO[0000] "clab-srexperts-leaf11:57400" sending file="show-int.txt" hash 
INFO[0000] "clab-srexperts-leaf11:57400" file "show-int.txt" written successfully
```

```
On the router:

--{ running }--[  ]--
A:leaf11# bash cat show-int.txt
show interface

--{ running }--[  ]--
```

Tip: Try executing the file we just transferred using the `source` command in SR Linux.

### Removing Files from SR Linux

Next we are going to remove or delete the file that we just transferred.

The Remove RPC removes the specified file from the target node.

The target node returns an error if:

- An error occurs during the remove operation (for example, permission denied).
- The file does not exist.
- The path references a directory instead of a file.

```
# gnoic -a clab-srexperts-leaf11 -u admin -p SReXperts2024 --skip-verify file remove --path /home/admin/show-int.txt
INFO[0000] "clab-srexperts-leaf11:57400" file "/home/admin/show-int.txt" removed successfully 
```

```
On the router:

--{ running }--[  ]--
A:leaf11# bash cat show-int.txt
cat: show-int.txt: No such file or directory

--{ running }--[  ]--
```

## Practical scenarios with gNOI

Now that you are an expert on gNOI, let's start using gNOI for some real world scenarios.

### Confiuration Backups

The goal of this hackathon activity is to establish regular configuration backups of your SR Linux device on an external machine.

Try writing a script in the language of your choice that will use gNOI file service to get the configuration file from the device. After the file transfer is completed, rename the file with the current timestamp and copy it to a directory specifically created for backups. Schedule the script to run every 10 minutes on the server.

For ideas and solutions, refer to the [Solutions](./solutions/README.md) page.

### Bulk File Transfers

Your Network Automation team developed a new agent that works similar to ChatGPT for information on the device. You are responsible to transfer the agent package file to all 1000 SR Linux devices in your network.

The goal of this hackathon activity is to use gNOI file service to transfer files to your SR Linux device.

Try writing a script in the language of your choice that will use gNOI file service to run through a list of devices and transfer the agent package file. After the transfer is completed, verify that the file exists on the device using gNOI file service.

For ideas and solutions, refer to the [Solutions](./solutions/README.md) page.

Note - The same use case also applies to file transfer of software images as part of the software upgrade process. SR Linux also supports the gNOI OS service that can be used to transfer the software image and perform the software upgrade.

### Bulk File Deletions

Let's assume we completed a network wide software upgrade 6 months ago and now we can initiate a deletion of the old software files from our devices in order to reduce the flash disk usage.

The goal of this hackathon activity is to use gNOI file service to verify that the file exists on the device and then delete the old software files on all routers in your network.

Try writing a script in the language of your choice that will use gNOI file service to run through a list of devices, list the file and delete file on each device. After the delete operation is completed, verify that the file does not exist anymore on the router.

Since we are using containerlab for this hackathon and there are no software files stored on SR Linux container nodes deployed in this lab, we will be deleting the file we transferred in the previous use case (my-gpt.deb).

For ideas and solutions, refer to the [Solutions](./solutions/README.md) page.

## Summary

In this hackathon activity, we learned about using gRPC gNOI service for file management. We used Get, Put, List and Delete RPCs for real world use cases.

Now that you are an expert in gNOI, start thinking of taking advantage of this service in your network. For any questions, please reach out to any of the members in the Hackathon team or contact your Account team.

Thank you for choosing this use case ! We hope you enjoyed this activity.

