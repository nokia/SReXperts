# Using gNOI with SR OS

| Item | Details |
| --- | --- |
| Short Description | Use gNOI file service for managing files on SR OS |
| Skill Level | Beginner |
| Tools Used | SR OS, gNOIc, Programming language of your choice |

The gRPC Network Operations Interface (gNOI) defines a set of gRPC-based micro-services for executing operational commands on network devices. [gNOI service](https://github.com/openconfig/gnoi) is defined by OpenConfig.

gNOI supports Remote Procedure Calls (RPC) that can be used for Device reset, TLS certificate management, File operations and some general services like ping. gNOI like other gRPC services works in a client-server model where the client sends a RPC request to the server which executes the requested action and returns a response.

```
gNOI client (on VM) -------------(Request)-------------> gNOI server (SR OS)
gNOI client (on VM) <------------(Response)------------- gNOI server (SR OS)
```

For an easy read on gNOI RPCs and their parameters, visit [gNxI Documentation](https://gnxi.srlinux.dev/) developed by Nokia SR Linux team using the same gNxI RPC information from GitHub.

Refer to [Nokia SR OS guide](https://documentation.nokia.com/sr/24-3/7x50-shared/system-management/grpc.html#ai9exgst86) for more information on SR OS implementation of gNOI services.

There are many clients that support gNOI services, the most common one is [gNOIc](https://gnoic.kmrd.dev/) developed by Nokia.

## SReXperts Hackathon

As part of this SReXperts Hackathon, we will be exploring gNOI file services on SR OS.

## gNOI File Service

In the gNOI file service, OpenConfig defines a generic interface to perform file operational tasks. For information see [gNOI specification](https://github.com/openconfig/gnoi/blob/master/file/file.proto)

SR OS supports the following gNOI file RPCs:

- Get RPC 
- Put RPC
- Stat RPC
- Remove RPC
- TransferToRemote RPC

## Getting Ready

### SR OS Configuration for gNOI

Choose a SR OS device in your topology.

Login to the SR OS device and configure/verify the following.

To enter configuration context, use `edit-config private`. Once you are done with your configuration changes, use `commit` to apply and save the changes.

In the example below, `allow-unsecure-connection` disables TLS and should only be used for lab environments.

```
/configure system grpc admin-state enable
/configure system grpc allow-unsecure-connection
/configure system grpc gnoi file admin-state enable
```

To view configuration, use `info /configure system grpc`.

```
A:admin@p1# info /configure system grpc
    admin-state enable
    allow-unsecure-connection
    gnoi {
        file {
            admin-state enable
        }
    }

[/]
A:admin@p1# 
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

We are going to do a quick review of the gNOI file RPCs supported on SR OS.

After this review, we will start using gNOI to simulate real world use cases.

### Listing Files on SR OS Flash card

We are going to start this exercise by listing the files on the SR OS flash card.

A Stat RPC returns metadata (that is, statistical information) about a file on the target location. An error is returned when:

- the file does not exist
- an error is encountered while accessing the metadata

Let's go ahead and list files in the cf3: directory:

```
# gnoic -a clab-srexperts-p1 --insecure -u admin -p SReXperts2024 file stat --path cf3:
+-------------------------+-----------------------+---------------------------+------------+------------+-------+
|       Target Name       |         Path          |       LastModified        |    Perm    |   Umask    | Size  |
+-------------------------+-----------------------+---------------------------+------------+------------+-------+
| clab-srexperts-p1:57400 | cf3:\.commit-history\ | 2024-05-10T22:22:32+03:00 | drwxrwxrwx | -rwxrwxrwx | 0     |
|                         | cf3:\CONFIG.CFG       | 2024-05-03T15:15:26+03:00 | -rwxrwxrwx | -rwxrwxrwx | 0     |
|                         | cf3:\NVRAM.DAT        | 2024-05-03T15:15:26+03:00 | -rwxrwxrwx | -rwxrwxrwx | 101   |
|                         | cf3:\SYSLINUX\        | 2024-05-03T15:15:26+03:00 | drwxrwxrwx | -rwxrwxrwx | 0     |
|                         | cf3:\TIMOS\           | 2024-05-03T15:15:26+03:00 | drwxrwxrwx | -rwxrwxrwx | 0     |
|                         | cf3:\bof.cfg          | 2024-05-08T15:37:06+03:00 | -rwxrwxrwx | -rwxrwxrwx | 1021  |
|                         | cf3:\bof.cfg.1        | 2024-05-08T15:37:04+03:00 | -rwxrwxrwx | -rwxrwxrwx | 1021  |
|                         | cf3:\bof.cfg.2        | 2024-05-03T15:15:26+03:00 | -rwxrwxrwx | -rwxrwxrwx | 196   |
|                         | cf3:\bootlog.txt      | 2024-05-08T15:38:06+03:00 | -rwxrwxrwx | -rwxrwxrwx | 11506 |
|                         | cf3:\nvsys.info       | 2024-05-08T15:36:44+03:00 | -rwxrwxrwx | -rwxrwxrwx | 317   |
|                         | cf3:\restcntr.txt     | 2024-05-08T15:36:56+03:00 | -rwxrwxrwx | -rwxrwxrwx | 1     |
+-------------------------+-----------------------+---------------------------+------------+------------+-------+
```
Tip - Try adding the `--format json` option at the end to see the above output in json format.


### Getting Files from SR OS

Next we are going to transfer a file from the device to our host VM.

A Get RPC reads and streams the contents of a file from a target location. The file is streamed using sequential messages and a final message containing the hash of the streamed data is sent before the stream is closed. An error is returned when:

- the file does not exist
- there is a problem reading the file

Create a directory on the VM and name it `sros-gnoi-<yourname>`. We will transfer the `bof.cfg` file from the router to this directory. Verify the file was transferred to the VM.

For example, if your name is Chris, the directory will be named sros-gnoi-chris.

```
# mkdir sros-gnoi-chris
# cd sros-gnoi-chris
```

```
# gnoic -a clab-srexperts-p1 --insecure -u admin -p SReXperts2024 file get --file cf3:\bof.cfg
INFO[0000] "clab-srexperts-p1:57400" received 1021 bytes 
INFO[0000] "clab-srexperts-p1:57400" file "cf3:\\bof.cfg" saved 
```

```
# cat cf3:/bof.cfg

# TiMOS-B-24.3.R2-1 both/x86_64 Nokia 7750 SR Copyright (c) 2000-2024 Nokia.
# All rights reserved. All use subject to applicable license agreements.
# Built on Fri May 3 12:15:20 PDT 2024 by builder in /builds/243B/R2-1/panos/main/sros
<--snip-->

primary-image    cf3:\timos\
primary-config   tftp://172.31.255.29/config.txt
license-file     tftp://172.31.255.29/license.txt
address          172.31.255.30/30 active
address          200::1/127 active
<--snip-->
# Finished 2024-05-08T12:37:06.5Z
```

### Putting Files to SR OS

Now we are ready to transfer a file from our VM to the SR OS device.

A Put RPC streams data to be written on a file on the target location. The file is streamed using sequential messages and a final message that includes the hash of the streamed data is sent prior to closing the stream. An error is returned when:

- the location does not exist
- an error is encountered while writing the data

Select or create a file on your VM (in your own directory) to be transferred over to the device. Verify the file transferred on the router.

```
# echo "show port" > show-port.txt
```

```
# gnoic -a clab-srexperts-p1 --insecure -u admin -p SReXperts2024 file put --file show-port.txt --dst cf3:\show-port.txt
INFO[0000] "clab-srexperts-p1:57400" sending file="show-port.txt" hash 
INFO[0000] "clab-srexperts-p1:57400" file "show-port.txt" written successfully 
```

```
On the router:

A:admin@p1# file show cf3:\show-port.txt
File: show-port.txt
-------------------------------------------------------------------------------
show port

===============================================================================

[/]
```

Tip: Try executing the file we just transferred using the `exec` command in SR OS.

### Removing Files from SR OS

Next we are going to remove or delete the file that we just transferred.

A Remove RPC removes the specified file from the target location. An error is returned when:

- the file does not exist
- there is a directory instead of a file
- an error is encountered during the remove operation (for example, permission denied)

```
# gnoic -a clab-srexperts-p1 --insecure -u admin -p SReXperts2024 file remove --path cf3:\show-port.txt
INFO[0000] "clab-srexperts-p1:57400" file "cf3:show-port.txt" removed successfully 
```

```
On the router:

A:admin@p1# file show cf3:\show-port.txt
MINOR: MGMT_AGENT #2007: Operation failed - open file "cf3:\show-port.txt"

[/]
```

## Practical scenarios with gNOI

Now that you are an expert on gNOI, let's start using gNOI for some real world scenarios.

### Confiuration Backups

The goal of this hackathon activity is to establish regular configuration backups of your SR OS device on an external machine.

Try writing a script in the language of your choice that will use gNOI file service to get the configuration file (cf3:\CONFIG.CFG) from the device. After the file transfer is completed, rename the file with the current timestamp and copy it to a directory specifically created for backups. Schedule the script to run every 10 minutes on the server.

For ideas and solutions, refer to the [Solutions](./solutions/README.md) page.

### Bulk File Transfers

Your Engineering team has given you the responsibility to create 2 new loopbacks on all 1000 SR OS devices in your network.

The goal of this hackathon activity is to use gNOI file service to transfer files to your SR OS device.

Try writing a script in the language of your choice that will use gNOI file service to run through a list of devices and transfer the configuration file that holds the commands to configure these loopbacks.

Create a file on your local VM with the commands to configure loopbacks on SR OS.

```
/configure router interface <your-name>-gnoi-LB1 loopback ipv4 primary address 192.168.24.10 prefix-length 32
/configure router interface <your-name>-gnoi-LB2 loopback ipv4 primary address 192.168.24.20 prefix-length 32
```

For ideas and solutions, refer to the [Solutions](./solutions/README.md) page.

Note - The same use case also applies to file transfer of software images as part of the software upgrade process.


### Bulk File Deletions

Let's assume we completed a network wide software upgrade 6 months ago and now we can initiate a deletion of the old software files from our devices in order to reduce the flash disk usage.

The goal of this hackathon activity is to use gNOI file service to verify that the file exists on the device and then delete the old software files on all routers in your network.

Try writing a script in the language of your choice that will use gNOI file service to run through a list of devices, list the file and delete file on each device.

Since we are using containerlab for this hackathon and there are no software files stored on SR OS container nodes deployed in this lab, we will be deleting the configuration file we transferred in the previous use case.

For ideas and solutions, refer to the [Solutions](./solutions/README.md) page.

## Summary

In this hackathon activity, we learned about using gRPC gNOI service for file management. We used Get, Put, List and Delete RPCs for real world use cases.

Now that you are an expert in gNOI, start thinking of taking advantage of this service in your network. For any questions, please reach out to any of the members in the Hackathon team or contact your Account team.

Thank you for choosing this use case ! We hope you enjoyed this activity.

