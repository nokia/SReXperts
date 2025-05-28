---
tags:
  - gRPC
  - gNMI
  - gNSI
  - Authz
  - Authorization
  - SR Linux
---

# Securing gRPC services from unauthorized access


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Securing gRPC services from unauthorized access |
| **Activity ID**           | 3 |
| **Short Description**       | Secure access to the SR Linux file system by preventing unauthorized 3rd party gRPC clients from transferring corrupted files to the router |
| **Difficulty**              | Beginner |
| **Tools used**              | [gNMIc](https://gnmic.openconfig.net/), [gNOIc](https://gnoic.kmrd.dev/), [gNSIc (beta)](https://github.com/karimra/gnsic) |
| **Topology Nodes**          | :material-router: leaf11 |
| **References**              | [SR Linux documentation](https://documentation.nokia.com/srlinux/)<br/>[gRPC website](https://grpc.io/)<br/>[gNxI protobuf reference](https://gnxi.srlinux.dev/) |


A daily scheduled backup of the configuration file on `leaf11` is taken by a remote file server using the gRPC gNOI `File` service with `client1` as the username . A 3rd party got access to this file server and they use the gNOI File service to push a compromised configuration file to the SR Linux device. Using other unspecified methods, they reboot the router resulting in the compromised configuration to become active and thereby opening up the entire network for the attacker. Your task is to stop such an attack by denying the `client1` user from writing to the local filesystem of the router.

## Objective

On your groups hackathon VM, create a remote configuration file backup for `leaf11` using `client1` as the username and then use authorization policies on `leaf11` to prevent `client1` from pushing a corrupted file from the remote server to the router.

In this activity, we will:

1. Use gNOI to backup the configuration file for a SR Linux device.
2. Simulate how an attacker who got access to the VM can use gNOI to transfer a corrupted file to the router.
3. Use gNSI to deny access to gNOI requests for writing files on the router.
4. Repeat attacker simulation to verify if the authorization policy is working.

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
gNOI (gRPC Network Operations Interface) is a gRPC service for executing operational commands on a network device. gNOI supports many services for different operations including, File Get, File Put, System Ping, System Traceroute and others.  Refer to the [gNxI reference](https://gnxi.srlinux.dev/) to see the details of all the gNOI RPCs supported on SR Linux.

For this activity, our focus will be on gNOI File service. This service has the following RPCs:

1. `Stat` - list a file or directory on a remote router (similar to `ls` command on Linux)
2. `Get` - transfer a file from a remote router (similar to `scp`)
3. `Put` - transfer a file to a remote router (similar to `scp`)
4. `Remove` - delete a file on the remote router (similar to `rm` command on Linux)
5. `Transfer` - transfer a file on a remote router to a remote destination

### gNSI
gNSI (gRPC Network Security Interface) is a gRPC service for defining and retrieving security configuration on network devices. gNSI supports functions like TLS certificate management, gRPC service authorization and accounting to name a few. Refer to the [gNxI reference](https://gnxi.srlinux.dev/) to see the details of all the gNSI RPCs supported on SR Linux.

For this activity, our focus will be on gNSI Authz service. This service has the following RPCs:

1. `Get` - list the active gNSI Authz policy on the remote router
2. `Probe` - test if a particular gRPC call is permitted or denied for a specific user
3. `Rotate` - install and overwrite existing active Authz policy on the remote router. Only one policy can be installed which is always active.

## Preparing the router

### gRPC configuration on SR Linux

Before starting the tasks, let's verify the gRPC configuration on `leaf11`.

gRPC is enabled with TLS under gRPC server called `mgmt` and relevant gRPC services for this activity (gNMI, gNOI and gNSI) are also enabled under this gRPC server.

Verify the config of this grpc server.

/// tab | cmd

``` bash
info flat system grpc-server secure-mgmt
```

///
/// tab | expected output

``` bash
set / system grpc-server secure-mgmt admin-state enable
set / system grpc-server secure-mgmt rate-limit 65535
set / system grpc-server secure-mgmt session-limit 1024
set / system grpc-server secure-mgmt default-tls-profile true
set / system grpc-server secure-mgmt network-instance mgmt
set / system grpc-server secure-mgmt port 57401
set / system grpc-server secure-mgmt services [ gnmi gnoi gnsi p4rt ]
```
///

Based on the config, you will notice that the secure gRPC server is listening on port 57401.

### User configuration on SR Linux

Create 2 users described below on `leaf11`. These users will be used by gRPC clients for remote access to the router.

| Username | Password | Role |
|----------|----------|------|
| client1 | client1 | gNOI service |
| grclient1 | grclient1 | gNMI service |

/// tab | cmd

``` bash
set / system aaa authorization role ext-clients services [ gnoi ]
set / system aaa authentication user client1 password client1
set / system aaa authentication user client1 role [ ext-clients ]
set / system aaa authorization role gnmi-clients services [ gnmi ]
set / system aaa authentication user grclient1 password grclient1 role [ gnmi-clients ]
set / system configuration role gnmi-clients rule / action write
```

///
/// tab | verify after commit

``` bash
info flat from running system aaa | grep client
```

///
/// tab | expected output

``` bash
set / system aaa authentication user client1 password $y$j9T$c0b094a538ddae13$GtCdwrCxDIrMhva6AtwPrXBR9YKFj4Gkr3RhaqRBstB
set / system aaa authentication user client1 role [ ext-clients ]
set / system aaa authentication user grclient1 password $y$j9T$720580ea832aa30d$AP.4Qi6e1kFXyU6TG82/v1xs99r4tCk/H8kBmvPenpB
set / system aaa authentication user grclient1 role [ gnmi-clients ]
set / system aaa authorization role ext-clients services [ gnoi ]
set / system aaa authorization role gnmi-clients services [ gnmi ]
```
///

### Client Verification

We will be using gNOIc and gNSIc as our clients for gNOI and gNSI services respectively.

Verify these clients are installed on your group's hackathon VM.

/// note | gNSIc
The gNSIc client is in beta status at time of writing this activity.<br>
///

/// tab | gnoic

``` bash
gnoic version
```

///
/// tab | gnoic expected output

``` bash
❯ gnoic version
version : 0.1.0
 commit : a5e9584
   date : 2024-12-18T19:04:06Z
 gitURL : https://github.com/karimra/gnoic
   docs : https://gnoic.kmrd.dev
```
///
/// tab | gnsic

``` bash
gnsic version
```

///
/// tab | gnsic expected output

``` bash
❯ gnsic version
version : dev
 commit : none
   date : unknown
 gitURL : 
```
///

It is also acceptable to have newer versions of these clients.

If clients are not installed or if you need to update the clients to the latest version, refer to the sources listed below.

- [gNOIc](https://gnoic.kmrd.dev/)
- [gNSIc (beta)](https://github.com/karimra/gnsic)

### Test gNOIc connectivity to SR Linux device
Let's do a connectivity check for gNOI to ensure gRPC is running on `leaf11`. We will use the `client1` user for all gNOI operations.

For this test, we will be using the gNOI `System` service `Time` RPC to get the current timestamp on `leaf11`.

/// tab | cmd

``` bash
gnoic -a clab-srexperts-leaf11:57401 -u client1 -p client1 --skip-verify system time
```
///
/// tab | expected output

``` bash
+-----------------------------+------------------------------------------+---------------------+
|         Target Name         |                   Time                   |      Timestamp      |
+-----------------------------+------------------------------------------+---------------------+
| clab-srexperts-leaf11:57401 | 2025-04-25 22:32:58.749420494 +0300 EEST | 1745609578749420494 |
+-----------------------------+------------------------------------------+---------------------+
```
///

We received the current system timestamp from `leaf11` and this confirms that gNOI is enabled on the router.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Use gNOIc to get the configuration file from SR Linux
Our first task is to setup a remote configuration file backup service on the host VM.

Before we get the configuration file from `leaf11`, let's verify from the host using gNOI that the configuration exists on the router.

We will be using `gNOI File Stat` RPC for this purpose. The default configuration file for SR Linux is located at `/etc/opt/srlinux/config.json`.

/// tab | cmd

``` bash
gnoic -a clab-srexperts-leaf11:57401 -u client1 -p client1 --skip-verify file stat --path /etc/opt/srlinux/config.json
```
///
/// tab | expected output

``` bash
+-----------------------------+------------------------------+---------------------------+------------+------------+--------+
|         Target Name         |             Path             |       LastModified        |    Perm    |   Umask    |  Size  |
+-----------------------------+------------------------------+---------------------------+------------+------------+--------+
| clab-srexperts-leaf11:57401 | /etc/opt/srlinux/config.json | 2025-04-24T19:16:13+03:00 | -rw-rw-r-- | -----w--w- | 121885 |
+-----------------------------+------------------------------+---------------------------+------------+------------+--------+
```
///

We confirmed that the configuration file exists and we also got information on the last modified timestamp and the size of the file.

Now let's retrieve this file to our host.

Create a directory called `my-backups` on your host to store the configuration backup file.

```
mkdir ~/my-backups
```

We will be using `gNOI File Get` RPC to retrieve the file from `leaf11`.

/// tab | cmd

``` bash
gnoic -a clab-srexperts-leaf11:57401 -u client1 -p client1 --skip-verify file get --file /etc/opt/srlinux/config.json --dst ~/my-backups
```
///
/// tab | expected output

``` bash
INFO[0000] "clab-srexperts-leaf11:57401" received 64000 bytes 
INFO[0000] "clab-srexperts-leaf11:57401" received 57885 bytes 
INFO[0000] "clab-srexperts-leaf11:57401" file "/etc/opt/srlinux/config.json" saved 
```
///

Let's check that the file get operation was successful and the file exists on your groups hackathon VM.

/// tab | cmd

``` bash
ls -lrt ~/my-backups/etc/opt/srlinux
```
///
/// tab | expected output

``` bash
❯ ls -lrt ~/my-backups/etc/opt/srlinux
total 120
-rw-r--r-- 1 nokia nokia 121885 Apr 25 23:00 config.json
```
///

/// note
The destination file is created on the same path as the origin. In this case `/etc/opt/srlinux/`<br>
///

You may open the configuration backup to verify the contents.

/// note
This gnoic command can be added to a cron job on the host for taking regular configuration backups from your devices. This is outside the scope of this activity.
///

### Simulate unauthorized gRPC access from host
Let us now simulate how an unauthorized user who got access to the VM can use gNOI service to transfer a corrupt file or image to the router.

Create a file on your host that we will consider as a compromised file.

```
echo "This is a corrupted file" > ~/corrupt.img
```

We will use the `gNOI File Put` RPC to transfer this file to `leaf11` under the directory `/var/log/srlinux/`.

/// tab | cmd
``` bash
gnoic -a clab-srexperts-leaf11:57401 -u client1 -p client1  --skip-verify file put --file ~/corrupt.img --dst /var/log/srlinux/SRL-25-3.img
```
///
/// tab | expected output

``` bash
INFO[0000] "clab-srexperts-leaf11:57401" sending file="/home/nokia/corrupt.img" hash 
INFO[0000] "clab-srexperts-leaf11:57401" file "/home/nokia/corrupt.img" written successfully 
```
///

Let's verify that the file is now present on `leaf11`. We will use the `gNOI File Stat` service we used earlier.

/// tab | cmd
``` bash
gnoic -a clab-srexperts-leaf11:57401 -u client1 -p client1 --skip-verify file stat --path /var/log/srlinux/SRL-25-3.img
```
///
/// tab | expected output

``` bash
+-----------------------------+-------------------------------+---------------------------+------------+------------+------+
|         Target Name         |             Path              |       LastModified        |    Perm    |   Umask    | Size |
+-----------------------------+-------------------------------+---------------------------+------------+------------+------+
| clab-srexperts-leaf11:57401 | /var/log/srlinux/SRL-25-3.img | 2025-04-25T23:11:43+03:00 | -rwxrwxrwx | -----w--w- | 25   |
+-----------------------------+-------------------------------+---------------------------+------------+------------+------+
```
///

We confirmed that the file is present on `leaf11`.

Before we move on, let's delete that file on `leaf11` using `gNOI File Remove` RPC.

/// tab | cmd
``` bash
gnoic -a clab-srexperts-leaf11:57401 -u client1 -p client1 --skip-verify file remove --path /var/log/srlinux/SRL-25-3.img
```
///

### Secure gRPC access using gNSI

SR Linux has a default Authz policy that allows all gRPC operations. This can be verified from `leaf11` CLI.

/// tab | cmd
``` bash
info flat from state /system aaa authorization authz-policy
```
///
/// tab | expected output

``` bash
/ system aaa authorization authz-policy version 2023-06-01
/ system aaa authorization authz-policy created-on "2025-04-28T13:52:58.067Z (4 minutes ago)"
/ system aaa authorization authz-policy policy "{
  \"name\": \"Default policy\",
  \"allow_rules\": [
    {
      \"name\": \"admin-access\",
      \"source\": {
        \"principals\": [
          \"*\"
        ]
      },
      \"request\": {
        \"paths\": [
          \"/*\",
          \"\"
        ]
      }
    }
  ]
}
"
```
///

This default policy is allowing all gNOI operations including the `Put` RPC that was used to transfer the compromised file to the router.

Only one gNSI Authz policy can be configured on the router and it is always active. The policy is displayed in `JSON` format with escape characters (`\`) for each `"`.

The following are the components of an Authz policy:

1. `name` - Authz policy name
2. `allow_rules` - List of users/roles allowed access to the list of gRPC RPCs

    1. `name` - Name for allow rules
    2. `principals` - list of usernames and roles applicable to this allow rule
    3. `paths` - list of gRPC RPCs applicable to this allow rule
    
3. `deny_rules` - List of users/roles denied access to the list of gRPC RPCs

    1. `name` - Name for deny rules
    2. `principals` - list of usernames and roles applicable to this deny rule
    3. `paths` - list of gRPC RPCs applicable to this deny rule
    

The `paths` in the policy are obtained from the gNOI proto file from the [Openconfig git repo](https://github.com/openconfig/gnoi/blob/main/file/file.proto). For example, for gNOI File Get, the package name is `gnoi.file`, the service is `File` and the RPC is `Get`.

Refer to [SR Linux Documentation](https://documentation.nokia.com/srlinux/25-3/books/system-mgmt/gnsi.html#authz-policy) for more details.

Your task is to overwrite this default Authz policy with another policy that will have the following rules:

1. Allow gNOI File Stat and gNOI File Get for `client1` and role `ext-clients`
2. Deny gNOI File Put RPC for `client1` and role `ext-clients`

Once your Authz policy is ready to be configured, use Authz Rotate RPC in the gNSIc command to push the policy to `leaf11`. Here's an example. Replace the `json payload` part with your Authz policy in JSON format (remember to use the escape character `\` for the `"` character).

/// tab | cmd
``` bash
gnsic -a clab-srexperts-leaf11:57401 -u admin -p $EVENT_PASSWORD --skip-verify authz rotate --policy "json payload"
```
///
/// tab | expected output

``` bash
INFO[0000] targets: map[clab-srexperts-leaf11:57401:0xc00034c4e0] 
INFO[0000] "clab-srexperts-leaf11:57401": got UploadResponse 
INFO[0001] "clab-srexperts-leaf11:57401": sending finalize request 
INFO[0001] "clab-srexperts-leaf11:57401": closing stream 
```
///

### Repeat unauthorized access simulation
After the Authz policy is installed on `leaf11`, try to transfer the same compromised file to `leaf11`.

WIth the configured Authz policy, the system will deny the request to write a file on the local filesystem.

/// tab | cmd
``` bash
gnoic -a clab-srexperts-leaf11:57401 -u client1 -p client1 --skip-verify file put --file ~/corrupt.img --dst /var/log/srlinux/SRL-25-3.img
```
///
/// tab | expected output with Authz policy
``` bash
INFO[0000] "clab-srexperts-leaf11:57401" sending file="corrupt.img" hash  
ERRO[0000] "clab-srexperts-leaf11:57401" File Put failed: rpc error: code = PermissionDenied desc = User 'client1' is not authorized to use rpc '/gnoi.file.File/Put' 
Error: there was 1 error(s)
```
///

Check the Authz policy counters to verify that the `reject` counter has incremented. Repeat the above command and check the counter.

/// tab | cmd
``` bash
info flat from state system aaa authorization authz-policy counters | grep Put
```
///
/// tab | expected output
``` bash hl_lines="1"
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Put access-rejects 1
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Put last-access-reject "2025-04-29T02:16:31.582Z (3 minutes ago)"
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Put access-accepts 1
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Put last-access-accept "2025-04-29T01:57:08.730Z (22 minutes ago)"
```
///


## Solution

If you need help, refer to the Authz policy below.

/// details | gNSI Authz policy
    type: code
```json
{
  "name": "Ext-clients",
  "allow_rules": [
    {
      "name": "backup-access",
      "source": {
        "principals": [
          "client1","ext-clients"
        ]
      },
      "request": {
        "paths": [
          "/gnoi.file.File/Get",
          "/gnoi.file.File/Stat"
        ]
      }
    }
  ],
  "deny_rules": [
    {
      "name": "backup-access",
      "source": {
        "principals": [
          "client1","ext-clients"
        ]
      },
      "request": {
        "paths": [
          "/gnoi.file.File/Put"
        ]
      }
    }
  ]
}
```
///

Here's the command to push this policy to `leaf11` using `Authz Rotate` RPC.

/// tab | cmd
``` bash
gnsic -a clab-srexperts-leaf11:57401 -u admin -p $EVENT_PASSWORD --skip-verify authz rotate --policy "{\"name\":\"Ext-clients\",\"allow_rules\":[{\"name\":\"backup-access\",\"source\":{\"principals\":[\"client1\",\"ext-clients\"]},\"request\":{\"paths\":[\"/gnoi.file.File/Get\",\"/gnoi.file.File/Stat\"]}}],\"deny_rules\":[{\"name\":\"backup-access\",\"source\":{\"principals\":[\"client1\",\"ext-clients\"]},\"request\":{\"paths\":[\"/gnoi.file.File/Put\"]}}]}"
```
///
/// tab | expected output
``` bash
INFO[0000] targets: map[clab-srexperts-leaf11:57401:0xc00034c4e0] 
INFO[0000] "clab-srexperts-leaf11:57401": got UploadResponse 
INFO[0001] "clab-srexperts-leaf11:57401": sending finalize request 
INFO[0001] "clab-srexperts-leaf11:57401": closing stream 
```
///

/// tip | Using an input file
Although not officially supported, you could try putting the Authz payload in a file with the following workaround:\n

`gnsic -a clab-srexperts-leaf11:57401 -u admin -p $EVENT_PASSWORD --skip-verify authz rotate --policy "$(jq . authz.json)"`

where `authz.json` is the file with the Authz payload.
///

Verify the configured Authz policy on `leaf11` CLI.

/// tab | cmd
``` bash
info flat from state /system aaa authorization authz-policy
```
///
/// tab | expected output
``` bash
/ system aaa authorization authz-policy version ""
/ system aaa authorization authz-policy created-on "2417-02-18T14:54:24.465Z (392 years from now)"
/ system aaa authorization authz-policy policy "{\"name\":\"Ext-clients\",\"allow_rules\":[{\"name\":\"backup-access\",\"source\":{\"principals\":[\"client1\",\"ext-clients\"]},\"request\":{\"paths\":[\"/gnoi.file.File/Get\",\"/gnoi.file.File/Stat\"]}}],\"deny_rules\":[{\"name\":\"backup-access\",\"source\":{\"principals\":[\"client1\",\"ext-clients\"]},\"request\":{\"paths\":[\"/gnoi.file.File/Put\"]}}]}"
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Get access-rejects 0
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Get access-accepts 1
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Get last-access-accept "2025-04-29T01:56:45.028Z (6 minutes ago)"
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Put access-rejects 0
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Put access-accepts 1
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Put last-access-accept "2025-04-29T01:57:08.730Z (5 minutes ago)"
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Stat access-rejects 0
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Stat access-accepts 5
/ system aaa authorization authz-policy counters rpc /gnoi.file.File/Stat last-access-accept "2025-04-29T01:57:15.326Z (5 minutes ago)"
/ system aaa authorization authz-policy counters rpc /gnoi.system.System/Time access-rejects 0
/ system aaa authorization authz-policy counters rpc /gnoi.system.System/Time access-accepts 1
/ system aaa authorization authz-policy counters rpc /gnoi.system.System/Time last-access-accept "2025-04-29T01:55:42.746Z (7 minutes ago)"
/ system aaa authorization authz-policy counters rpc /gnsi.authz.v1.Authz/Rotate access-rejects 0
/ system aaa authorization authz-policy counters rpc /gnsi.authz.v1.Authz/Rotate access-accepts 3
/ system aaa authorization authz-policy counters rpc /gnsi.authz.v1.Authz/Rotate last-access-accept "2025-04-29T02:03:00.794Z (4 seconds ago)"
```
///

## Delete Authz policy

Login to `leaf11` and remove the configured Authz policy.

/// tab | cmd
``` bash
tools system aaa authorization authz-policy remove
```
///
/// tab | expected output
``` bash
/system/aaa:
    Authz authorization policy has been removed
```
///

## Additional Task

Streaming Telemetry is being sent from `leaf11` with `grclient1` username to an open source stats collector. An unauthorized 3rd party gets access to the CLI of this stats collector and uses gNMI Set RPC to disable BGP on `leaf11`. Your task is to secure `leaf11` from such an attack using gNSI Authz policies.

### gNMI commands

The `gnmic` client is installed on your host VM. This can be verified using:

/// tab | cmd
``` bash
gnmic version
```
///
/// tab | expected output
``` bash
version : 0.40.0
 commit : 3f13e44d
   date : 2025-01-27T22:03:58Z
 gitURL : https://github.com/openconfig/gnmic
   docs : https://gnmic.openconfig.net
```
///

If gnmic client is not installed, refer to  [gNMIc page](https://gnmic.openconfig.net/) for installation instructions.

Here are the commands to test Get, Set and Subscribe.

/// tab | gNMI Get
``` bash
gnmic -a clab-srexperts-leaf11:57401 -u grclient1 -p grclient1 --skip-verify get --type state --path "/interface[name=ethernet-1/1]/statistics/in-octets/" -e json_ietf
```
///
/// tab | gNMI Set
``` bash
gnmic -a clab-srexperts-leaf11:57401 -u grclient1 -p grclient1 --skip-verify set --update-path "/interface[name=ethernet-1/1]/description" --update-value "gnmi-test"
```
///
/// tab | gNMI Subscribe
``` bash
gnmic -a clab-srexperts-leaf11:57401 -u grclient1 -p grclient1 --skip-verify sub --path "/interface[name=ethernet-1/1]/statistics/in-octets/" --mode once
```
///

Test the above commands and verify the outputs.

Then apply an Authz policy to allow `Get` and `Subscribe` RPCs while denying `Set` RPC for user `grclient1` and role `gnmi-clients`.

Both the username and the role name should be added to the principals section.

Refer to the gNMI proto file [here](https://github.com/openconfig/gnmi/blob/master/proto/gnmi/gnmi.proto) to get the RPC name to include in the policy. The format is `package_name.servce_name/RPC`.

### Solution
If you need help, refer to the solution below.

/// details | Solution for gNMI Authz policy
    type: code
```json
{
  "name": "srex-gnmi",
  "allow_rules": [
    {
      "name": "gnmi-access",
      "source": {
        "principals": [
          "grclient1","gnmi-clients"
        ]
      },
      "request": {
        "paths": [
          "/gnmi.gNMI/Get",
          "/gnmi.gNMI/Subscribe"
        ]
      }
    }
  ],
  "deny_rules": [
    {
      "name": "gnmi-access",
      "source": {
        "principals": [
          "grclient1","gnmi-clients"
        ]
      },
      "request": {
        "paths": [
          "/gnmi.gNMI/Set"
        ]
      }
    }
  ]
}
```
///

/// details | gNSI request for gNMI Authz policy
```bash
gnsic -a clab-srexperts-leaf11:57401 -u admin -p $EVENT_PASSWORD --skip-verify authz rotate --policy "{\"name\":\"gnmi-access\",\"allow_rules\":[{\"name\":\"gnmi-access\",\"source\":{\"principals\":[\"grclient1\",\"gnmi-clients\"]},\"request\":{\"paths\":[\"/gnmi.gNMI/Get\",\"/gnmi.gNMI/Subscribe\"]}}],\"deny_rules\":[{\"name\":\"gnmi-access\",\"source\":{\"principals\":[\"grclient1\",\"gnmi-clients\"]},\"request\":{\"paths\":[\"/gnmi.gNMI/Set\"]}}]}"
```
///

## Summary

Congratulations! By this point you should have successfully completed the activity and restricted the rogue actor from inflitrating your network. With the work you have put in, you should now have a basic understanding of the following topics:

- Using gRPC to perform activities on a remote router
- Using the gNOI service to manipulate the file system
- Using the gNSI service to secure network services on a router

Good job in completing all the tasks in this activity! 
