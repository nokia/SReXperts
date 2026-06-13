---
tags:
  - SROS
  - NOS
  - gRPC
  - TLS
  - Security
---

# Securing gRPC


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Securing gRPC                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Activity ID**           | 27                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Short Description**       | Securing the gRPC data-path from interception and attack                                                                                                                                                                                                                                                                    |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [gNMIc](https://gnmic.openconfig.net/) <br>[TShark](https://tshark.dev/)                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Topology Nodes**          | :material-router: P1                                                                                                                                                                                                                                                                                                                                                         |
| **References**              | [gRPC](https://grpc.io/docs/what-is-grpc/introduction/)<br/>[gRPC on SR OS in release 26.3.R1](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/grpc.html#ai9exgst78)<br/>[TLS on SR OS in release 26.3.R1](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/transport-layer-security.html#ai9exgst94)<br/>[gNMIc](https://gnmic.openconfig.net) |


You have just joined the organization as a security engineer and as part of your initial audit you have identified
that the network telemetry streams that carry the live network analytics to the management and monitoring stations
are transmitted without encryption and so are subject to interception concerns.

## Objective

Your task is the ensure that the telemetry streams are secured and can no longer be viewed.  You will use gNMI to
make these configuration changes so you can automate all device changes without needing to log onto each node.

You will initially use :material-router: P1. You may choose to expand this to secure the whole network later.

## Technology explanation

In this activity you will configure TLS to secure the gRPC protocol over which the gNMI service runs.  Further reading
can be found in the links below if you need assistance or are just interested in learning more:

- [gRPC](https://grpc.io/docs/what-is-grpc/introduction/)
- [gRPC on SR OS in release 26.3.R1](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/grpc.html#ai9exgst78)
- [TLS on SR OS in release 26.3.R1](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/transport-layer-security.html#ai9exgst94)
- [gNMIc utility](https://gnmic.openconfig.net)

This activity is not going to go into the details of how gRPC works or how to enable it, however, there are other gRPC activities
to tackle if this sounds of interest.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Check that gNMI streaming telemetry is operational

First we need to confirm that gNMI streaming telemetry is possible from :material-router: P1.  We are going to subscribe to IPv4 statistics state information
for the interface between :material-router: P1 and :material-router: PE2 (this interface is called `pe2` on :material-router: P1).

From your hackathon instance, start an insecure gNMI subscription to the following gNMI path in a new window/screen
`/state/router[router-name=Base]/interface[interface-name=pe2]/ipv4/statistics` using the `gnmic` client.  Ensure that you see interface data
being received on the screen.

Leave this stream running.

/// details | If you need assistance click here
    type: tip

/// tab | gNMIc command
``` bash
gnmic -a clab-srexperts-p1:57400 -u admin -p $EVENT_PASSWORD --insecure \
    subscribe --path=/state/router[router-name=Base]/interface[interface-name=pe2]/ipv4/statistics
```
///

/// tab | Example output
```
{
  "source": "clab-srexperts-p1:57400",
  "subscription-name": "default-1779697014",
  "timestamp": 1779697014691733320,
  "time": "2026-05-25T08:16:54.69173332Z",
  "prefix": "state/router[router-name=Base]/interface[interface-name=pe2]/ipv4/statistics",
  "updates": [
    {
      "Path": "out-packets",
      "values": {
        "out-packets": "336850"
      }
    },
    {
      "Path": "out-octets",
      "values": {
        "out-octets": "36222830"
      }
    },
    {
      "Path": "out-discard-packets",
      "values": {
        "out-discard-packets": "0"
      }
    },
    {
      "Path": "out-discard-octets",
      "values": {
        "out-discard-octets": "0"
      }
    },
    {
      "Path": "in-packets",
      "values": {
        "in-packets": "0"
      }
    },
    {
      "Path": "in-octets",
      "values": {
        "in-octets": "0"
      }
    },
    {
      "Path": "urpf-check-fail-packets",
      "values": {
        "urpf-check-fail-packets": "0"
      }
    },
    {
      "Path": "urpf-check-fail-octets",
      "values": {
        "urpf-check-fail-octets": "0"
      }
    },
    {
      "Path": "out-discard-dbcast-packets",
      "values": {
        "out-discard-dbcast-packets": "0"
      }
    },
    {
      "Path": "out-discard-dbcast-octets",
      "values": {
        "out-discard-dbcast-octets": "0"
      }
    },
    {
      "Path": "in-ip-helper-redirects-packets",
      "values": {
        "in-ip-helper-redirects-packets": "0"
      }
    },
    {
      "Path": "in-ip-helper-redirects-octets",
      "values": {
        "in-ip-helper-redirects-octets": "0"
      }
    }
  ]
}
{
  "sync-response": true
}
```
///
///

### Intercept the streaming telemetry data

From your hackathon instance, intercept the management traffic containing the streaming telemetry data using the `tshark` utility.
The command to use is:

/// tab | `tshark` command
``` bash
sudo tshark -ni any -f "src clab-srexperts-p1 and port 57400" -P -x
```
///

This will output packet dumps between your management station and :material-router: P1 from TCP port 57400 on the SR OS device (this
is the gRPC port configured on :material-router: P1) to the screen.

You will notice that in the ASCII decoding section you can identify the data coming from the streaming telemetry session.  A good string
to look out for is the word `statistics`.

/// details | Example output
    type: tip

```
   68 0.058525467  10.128.2.11 → 192.168.6.101 TCP 1078 57400 → 47693 [ACK] Seq=45672 Ack=610 Win=32768 Len=1012 TSval=3581509808 TSecr=3593588971

0000  52 54 00 14 ad 46 52 54 00 f0 31 61 08 00 45 88   RT...FRT..1a..E.
0010  04 28 c2 7f 00 00 3f 06 e1 30 0a 80 02 0b c0 a8   .(....?..0......
0020  06 65 e0 38 ba 4d 63 0d f0 dc b7 7e 87 8b 80 10   .e.8.Mc....~....
0030  80 00 3f d5 00 00 01 01 08 0a d5 79 80 b0 d6 31   ..?........y...1
0040  d0 eb 00 00 08 06 01 00 00 00 00 02 04 10 10 09   ................
0050  0e 07 07 00 04 43 00 00 00 00 00 01 00 00 00 00   .....C..........
0060  63 0a 61 08 e0 d9 c9 a0 d9 c9 8a d4 18 12 33 1a   c.a...........3.
0070  07 0a 05 73 74 61 74 65 1a 1a 0a 04 70 6f 72 74   ...state....port
0080  12 12 0a 07 70 6f 72 74 2d 69 64 12 07 31 2f 31   ....port-id..1/1
0090  2f 63 31 34 1a 0c 0a 0a 73 74 61 74 69 73 74 69   /c14....statisti
00a0  63 73 22 20 0a 17 1a 15 0a 13 6f 75 74 2d 75 6e   cs" ......out-un
00b0  69 63 61 73 74 2d 70 61 63 6b 65 74 73 1a 05 52   icast-packets..R
00c0  03 22 30 22 00 00 00 00 5a 0a 58 08 95 85 ca a0   ."0"....Z.X.....
00d0  d9 c9 8a d4 18 12 33 1a 07 0a 05 73 74 61 74 65   ......3....state
00e0  1a 1a 0a 04 70 6f 72 74 12 12 0a 07 70 6f 72 74   ....port....port
00f0  2d 69 64 12 07 31 2f 31 2f 63 32 32 1a 0c 0a 0a   -id..1/1/c22....
0100  73 74 61 74 69 73 74 69 63 73 22 17 0a 0e 1a 0c   statistics".....
0110  0a 0a 6f 75 74 2d 6f 63 74 65 74 73 1a 05 52 03   ..out-octets..R.
0120  22 30 22 00 00 00 00 63 0a 61 08 b8 da d0 a0 d9   "0"....c.a......
0130  c9 8a d4 18 12 33 1a 07 0a 05 73 74 61 74 65 1a   .....3....state.
0140  1a 0a 04 70 6f 72 74 12 12 0a 07 70 6f 72 74 2d   ...port....port-
0150  69 64 12 07 31 2f 31 2f 63 31 35 1a 0c 0a 0a 73   id..1/1/c15....s
0160  74 61 74 69 73 74 69 63 73 22 20 0a 17 1a 15 0a   tatistics" .....
0170  13 6f 75 74 2d 75 6e 69 63 61 73 74 2d 70 61 63   .out-unicast-pac
0180  6b 65 74 73 1a 05 52 03 22 30 22 00 00 00 00 5a   kets..R."0"....Z
0190  0a 58 08 bd 8b d4 a0 d9 c9 8a d4 18 12 33 1a 07   .X...........3..
01a0  0a 05 73 74 61 74 65 1a 1a 0a 04 70 6f 72 74 12   ..state....port.
01b0  12 0a 07 70 6f 72 74 2d 69 64 12 07 31 2f 31 2f   ...port-id..1/1/
01c0  63 32 33 1a 0c 0a 0a 73 74 61 74 69 73 74 69 63   c23....statistic
01d0  73 22 17 0a 0e 1a 0c 0a 0a 6f 75 74 2d 6f 63 74   s".......out-oct
01e0  65 74 73 1a 05 52 03 22 30 22 00 00 00 00 63 0a   ets..R."0"....c.
01f0  61 08 bd cd d7 a0 d9 c9 8a d4 18 12 33 1a 07 0a   a...........3...
0200  05 73 74 61 74 65 1a 1a 0a 04 70 6f 72 74 12 12   .state....port..
0210  0a 07 70 6f 72 74 2d 69 64 12 07 31 2f 31 2f 63   ..port-id..1/1/c
0220  31 36 1a 0c 0a 0a 73 74 61 74 69 73 74 69 63 73   16....statistics
0230  22 20 0a 17 1a 15 0a 13 6f 75 74 2d 75 6e 69 63   " ......out-unic
0240  61 73 74 2d 70 61 63 6b 65 74 73 1a 05 52 03 22   ast-packets..R."
0250  30 22 00 00 00 00 5a 0a 58 08 80 f2 dc a0 d9 c9   0"....Z.X.......
0260  8a d4 18 12 33 1a 07 0a 05 73 74 61 74 65 1a 1a   ....3....state..
0270  0a 04 70 6f 72 74 12 12 0a 07 70 6f 72 74 2d 69   ..port....port-i
0280  64 12 07 31 2f 31 2f 63 32 34 1a 0c 0a 0a 73 74   d..1/1/c24....st
0290  61 74 69 73 74 69 63 73 22 17 0a 0e 1a 0c 0a 0a   atistics".......
02a0  6f 75 74 2d 6f 63 74 65 74 73 1a 05 52 03 22 30   out-octets..R."0
02b0  22 00 00 00 00 63 0a 61 08 a2 ab df a0 d9 c9 8a   "....c.a........
02c0  d4 18 12 33 1a 07 0a 05 73 74 61 74 65 1a 1a 0a   ...3....state...
02d0  04 70 6f 72 74 12 12 0a 07 70 6f 72 74 2d 69 64   .port....port-id
02e0  12 07 31 2f 31 2f 63 31 37 1a 0c 0a 0a 73 74 61   ..1/1/c17....sta
02f0  74 69 73 74 69 63 73 22 20 0a 17 1a 15 0a 13 6f   tistics" ......o
0300  75 74 2d 75 6e 69 63 61 73 74 2d 70 61 63 6b 65   ut-unicast-packe
0310  74 73 1a 05 52 03 22 30 22 00 00 00 00 56 0a 54   ts..R."0"....V.T
0320  08 9f a0 eb a0 d9 c9 8a d4 18 12 2f 1a 07 0a 05   .........../....
0330  73 74 61 74 65 1a 16 0a 04 70 6f 72 74 12 0e 0a   state....port...
0340  07 70 6f 72 74 2d 69 64 12 03 41 2f 31 1a 0c 0a   .port-id..A/1...
0350  0a 73 74 61 74 69 73 74 69 63 73 22 17 0a 0e 1a   .statistics"....
0360  0c 0a 0a 6f 75 74 2d 6f 63 74 65 74 73 1a 05 52   ...out-octets..R
0370  03 22 30 22 00 00 00 00 63 0a 61 08 c8 88 ee a0   ."0"....c.a.....
0380  d9 c9 8a d4 18 12 33 1a 07 0a 05 73 74 61 74 65   ......3....state
0390  1a 1a 0a 04 70 6f 72 74 12 12 0a 07 70 6f 72 74   ....port....port
03a0  2d 69 64 12 07 31 2f 31 2f 63 31 38 1a 0c 0a 0a   -id..1/1/c18....
03b0  73 74 61 74 69 73 74 69 63 73 22 20 0a 17 1a 15   statistics" ....
03c0  0a 13 6f 75 74 2d 75 6e 69 63 61 73 74 2d 70 61   ..out-unicast-pa
03d0  63 6b 65 74 73 1a 05 52 03 22 30 22 00 00 00 00   ckets..R."0"....
03e0  56 0a 54 08 e2 cc f3 a0 d9 c9 8a d4 18 12 2f 1a   V.T.........../.
03f0  07 0a 05 73 74 61 74 65 1a 16 0a 04 70 6f 72 74   ...state....port
0400  12 0e 0a 07 70 6f 72 74 2d 69 64 12 03 41 2f 33   ....port-id..A/3
0410  1a 0c 0a 0a 73 74 61 74 69 73 74 69 63 73 22 17   ....statistics".
0420  0a 0e 1a 0c 0a 0a 6f 75 74 2d 6f 63 74 65 74 73   ......out-octets
0430  1a 05 52 03 22 30                                 ..R."0

   69 0.059059964  10.128.2.11 → 192.168.6.101 TCP 799 57400 → 47693 [PSH, ACK] Seq=46684 Ack=610 Win=32768 Len=733 TSval=3581509808 TSecr=3593588972

0000  52 54 00 14 ad 46 52 54 00 f0 31 61 08 00 45 88   RT...FRT..1a..E.
0010  03 11 c2 80 00 00 3f 06 e2 46 0a 80 02 0b c0 a8   ......?..F......
0020  06 65 e0 38 ba 4d 63 0d f4 d0 b7 7e 87 8b 80 18   .e.8.Mc....~....
0030  80 00 d2 54 00 00 01 01 08 0a d5 79 80 b0 d6 31   ...T.......y...1
0040  d0 ec 22 00 00 00 00 63 0a 61 08 b2 94 f6 a0 d9   .."....c.a......
0050  c9 8a d4 18 12 33 1a 07 0a 05 73 74 61 74 65 1a   .....3....state.
0060  1a 0a 04 70 6f 72 74 12 12 0a 07 70 6f 72 74 2d   ...port....port-
0070  69 64 12 07 31 2f 31 2f 63 31 39 1a 0c 0a 0a 73   id..1/1/c19....s
0080  74 61 74 69 73 74 69 63 73 22 20 0a 17 1a 15 0a   tatistics" .....
0090  13 6f 75 74 2d 75 6e 69 63 61 73 74 2d 70 61 63   .out-unicast-pac
00a0  6b 65 74 73 1a 05 52 03 22 30 22 00 01 89 00 00   kets..R."0".....
00b0  00 00 00 01 00 00 00 00 56 0a 54 08 e9 bd 82 a1   ........V.T.....
00c0  d9 c9 8a d4 18 12 2f 1a 07 0a 05 73 74 61 74 65   ....../....state
00d0  1a 16 0a 04 70 6f 72 74 12 0e 0a 07 70 6f 72 74   ....port....port
00e0  2d 69 64 12 03 41 2f 34 1a 0c 0a 0a 73 74 61 74   -id..A/4....stat
00f0  69 73 74 69 63 73 22 17 0a 0e 1a 0c 0a 0a 6f 75   istics".......ou
0100  74 2d 6f 63 74 65 74 73 1a 05 52 03 22 30 22 00   t-octets..R."0".
0110  00 00 00 63 0a 61 08 e9 9b 83 a1 d9 c9 8a d4 18   ...c.a..........
0120  12 33 1a 07 0a 05 73 74 61 74 65 1a 1a 0a 04 70   .3....state....p
0130  6f 72 74 12 12 0a 07 70 6f 72 74 2d 69 64 12 07   ort....port-id..
0140  31 2f 31 2f 63 32 30 1a 0c 0a 0a 73 74 61 74 69   1/1/c20....stati
0150  73 74 69 63 73 22 20 0a 17 1a 15 0a 13 6f 75 74   stics" ......out
0160  2d 75 6e 69 63 61 73 74 2d 70 61 63 6b 65 74 73   -unicast-packets
0170  1a 05 52 03 22 30 22 00 00 00 00 59 0a 57 08 fd   ..R."0"....Y.W..
0180  91 92 a1 d9 c9 8a d4 18 12 32 1a 07 0a 05 73 74   .........2....st
0190  61 74 65 1a 19 0a 04 70 6f 72 74 12 11 0a 07 70   ate....port....p
01a0  6f 72 74 2d 69 64 12 06 41 2f 67 6e 73 73 1a 0c   ort-id..A/gnss..
01b0  0a 0a 73 74 61 74 69 73 74 69 63 73 22 17 0a 0e   ..statistics"...
01c0  1a 0c 0a 0a 6f 75 74 2d 6f 63 74 65 74 73 1a 05   ....out-octets..
01d0  52 03 22 30 22 00 00 00 00 63 0a 61 08 d7 8d 93   R."0"....c.a....
01e0  a1 d9 c9 8a d4 18 12 33 1a 07 0a 05 73 74 61 74   .......3....stat
01f0  65 1a 1a 0a 04 70 6f 72 74 12 12 0a 07 70 6f 72   e....port....por
0200  74 2d 69 64 12 07 31 2f 31 2f 63 32 31 1a 0c 0a   t-id..1/1/c21...
0210  0a 73 74 61 74 69 73 74 69 63 73 22 20 0a 17 1a   .statistics" ...
0220  15 0a 13 6f 75 74 2d 75 6e 69 63 61 73 74 2d 70   ...out-unicast-p
0230  61 63 6b 65 74 73 1a 05 52 03 22 30 22 00 00 68   ackets..R."0"..h
0240  00 00 00 00 00 01 00 00 00 00 63 0a 61 08 dc b4   ..........c.a...
0250  9a a1 d9 c9 8a d4 18 12 33 1a 07 0a 05 73 74 61   ........3....sta
0260  74 65 1a 1a 0a 04 70 6f 72 74 12 12 0a 07 70 6f   te....port....po
0270  72 74 2d 69 64 12 07 31 2f 31 2f 63 32 32 1a 0c   rt-id..1/1/c22..
0280  0a 0a 73 74 61 74 69 73 74 69 63 73 22 20 0a 17   ..statistics" ..
0290  1a 15 0a 13 6f 75 74 2d 75 6e 69 63 61 73 74 2d   ....out-unicast-
02a0  70 61 63 6b 65 74 73 1a 05 52 03 22 30 22 00 00   packets..R."0"..
02b0  68 00 00 00 00 00 01 00 00 00 00 63 0a 61 08 bb   h..........c.a..
02c0  b2 a1 a1 d9 c9 8a d4 18 12 33 1a 07 0a 05 73 74   .........3....st
02d0  61 74 65 1a 1a 0a 04 70 6f 72 74 12 12 0a 07 70   ate....port....p
02e0  6f 72 74 2d 69 64 12 07 31 2f 31 2f 63 32 33 1a   ort-id..1/1/c23.
02f0  0c 0a 0a 73 74 61 74 69 73 74 69 63 73 22 20 0a   ...statistics" .
0300  17 1a 15 0a 13 6f 75 74 2d 75 6e 69 63 61 73 74   .....out-unicast
0310  2d 70 61 63 6b 65 74 73 1a 05 52 03 22 30 22      -packets..R."0"

   70 0.059616886  10.128.2.11 → 192.168.6.101 TCP 506 57400 → 47693 [PSH, ACK] Seq=47417 Ack=640 Win=32753 Len=440 TSval=3581509808 TSecr=3593588973

0000  52 54 00 14 ad 46 52 54 00 f0 31 61 08 00 45 88   RT...FRT..1a..E.
0010  01 ec c2 81 00 00 3f 06 e3 6a 0a 80 02 0b c0 a8   ......?..j......
0020  06 65 e0 38 ba 4d 63 0d f7 ad b7 7e 87 a9 80 18   .e.8.Mc....~....
0030  7f f1 bf a5 00 00 01 01 08 0a d5 79 80 b0 d6 31   ...........y...1
0040  d0 ed 00 00 68 00 00 00 00 00 01 00 00 00 00 63   ....h..........c
0050  0a 61 08 88 f7 a8 a1 d9 c9 8a d4 18 12 33 1a 07   .a...........3..
0060  0a 05 73 74 61 74 65 1a 1a 0a 04 70 6f 72 74 12   ..state....port.
0070  12 0a 07 70 6f 72 74 2d 69 64 12 07 31 2f 31 2f   ...port-id..1/1/
0080  63 32 34 1a 0c 0a 0a 73 74 61 74 69 73 74 69 63   c24....statistic
0090  73 22 20 0a 17 1a 15 0a 13 6f 75 74 2d 75 6e 69   s" ......out-uni
00a0  63 61 73 74 2d 70 61 63 6b 65 74 73 1a 05 52 03   cast-packets..R.
00b0  22 30 22 00 00 64 00 00 00 00 00 01 00 00 00 00   "0"..d..........
00c0  5f 0a 5d 08 f9 86 b0 a1 d9 c9 8a d4 18 12 2f 1a   _.].........../.
00d0  07 0a 05 73 74 61 74 65 1a 16 0a 04 70 6f 72 74   ...state....port
00e0  12 0e 0a 07 70 6f 72 74 2d 69 64 12 03 41 2f 31   ....port-id..A/1
00f0  1a 0c 0a 0a 73 74 61 74 69 73 74 69 63 73 22 20   ....statistics"
0100  0a 17 1a 15 0a 13 6f 75 74 2d 75 6e 69 63 61 73   ......out-unicas
0110  74 2d 70 61 63 6b 65 74 73 1a 05 52 03 22 30 22   t-packets..R."0"
0120  00 00 64 00 00 00 00 00 01 00 00 00 00 5f 0a 5d   ..d.........._.]
0130  08 b3 c7 b8 a1 d9 c9 8a d4 18 12 2f 1a 07 0a 05   .........../....
0140  73 74 61 74 65 1a 16 0a 04 70 6f 72 74 12 0e 0a   state....port...
0150  07 70 6f 72 74 2d 69 64 12 03 41 2f 33 1a 0c 0a   .port-id..A/3...
0160  0a 73 74 61 74 69 73 74 69 63 73 22 20 0a 17 1a   .statistics" ...
0170  15 0a 13 6f 75 74 2d 75 6e 69 63 61 73 74 2d 70   ...out-unicast-p
0180  61 63 6b 65 74 73 1a 05 52 03 22 30 22 00 00 64   ackets..R."0"..d
0190  00 00 00 00 00 01 00 00 00 00 5f 0a 5d 08 8a 9c   .........._.]...
01a0  c2 a1 d9 c9 8a d4 18 12 2f 1a 07 0a 05 73 74 61   ......../....sta
01b0  74 65 1a 16 0a 04 70 6f 72 74 12 0e 0a 07 70 6f   te....port....po
01c0  72 74 2d 69 64 12 03 41 2f 34 1a 0c 0a 0a 73 74   rt-id..A/4....st
01d0  61 74 69 73 74 69 63 73 22 20 0a 17 1a 15 0a 13   atistics" ......
01e0  6f 75 74 2d 75 6e 69 63 61 73 74 2d 70 61 63 6b   out-unicast-pack
01f0  65 74 73 1a 05 52 03 22 30 22                     ets..R."0"

   71 0.100592024  10.128.2.11 → 192.168.6.101 TCP 195 57400 → 47693 [PSH, ACK] Seq=47857 Ack=640 Win=32768 Len=129 TSval=3581509808 TSecr=3593589014

0000  52 54 00 14 ad 46 52 54 00 f0 31 61 08 00 45 88   RT...FRT..1a..E.
0010  00 b5 c2 82 00 00 3f 06 e4 a0 0a 80 02 0b c0 a8   ......?.........
0020  06 65 e0 38 ba 4d 63 0d f9 65 b7 7e 87 a9 80 18   .e.8.Mc..e.~....
0030  80 00 4c 72 00 00 01 01 08 0a d5 79 80 b0 d6 31   ..Lr.......y...1
0040  d1 16 00 00 67 00 00 00 00 00 01 00 00 00 00 62   ....g..........b
0050  0a 60 08 d6 a8 ca a1 d9 c9 8a d4 18 12 32 1a 07   .`...........2..
0060  0a 05 73 74 61 74 65 1a 19 0a 04 70 6f 72 74 12   ..state....port.
0070  11 0a 07 70 6f 72 74 2d 69 64 12 06 41 2f 67 6e   ...port-id..A/gn
0080  73 73 1a 0c 0a 0a 73 74 61 74 69 73 74 69 63 73   ss....statistics
0090  22 20 0a 17 1a 15 0a 13 6f 75 74 2d 75 6e 69 63   " ......out-unic
00a0  61 73 74 2d 70 61 63 6b 65 74 73 1a 05 52 03 22   ast-packets..R."
00b0  30 22 00 00 08 06 01 00 00 00 00 02 04 10 10 09   0"..............
00c0  0e 07 07
```

///

As you can see, this data is not encrypted and clearly visible to attackers.

Let's get to work securing our connection.

### Configure the nodes to secure the telemetry sessions with TLS

Using TLS and certificates is a complicated topic and this activity, rated **beginner**, does not delve into the details.  If you would like to know more you can [read this guide](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/transport-layer-security.html) or tackle one of the other TLS activities provided this year which delve into a little more detail.

This section will walk you through a process of:

- Creating a TLS certificate
- Creating a TLS certificate authority (CA)
- Signing your certificate with your CA
- Uploading your certificates to SR OS
- Installing your certificates into the SR OS PKI system
- Configuring the router to use a TLS server profile
- Configuring gRPC to use the new TLS server profile

Stop your gNMI subscription (`ctrl-c`) but **leave the `tshark` command running in another window**.

Before you progress, it is recommended to create a new directory and change into it so that any files you
create as part of this activity are separated from other files.

/// tab | Command
```
mkdir ~/tls-certs
cd ~/tls-certs
```
///

#### Generate certificates and sign them with your certificate authority (CA)

Now, on your hackathon instance, use the `containerlab` tool to generate a certificate authority (CA) certificate and key.
The command to run is this:

/// tab | Command
```
containerlab tools cert ca create
```
///
/// tab | Example output
``` {.no-copy}
19:56:11 INFO Certificate attributes: CN=containerlab.dev, C=Internet, L=Server, O=Containerlab, OU=Containerlab Tools, Validity period=87600h
```
///

This will have created two files in your current directory:

- `ca.pem`: The CA certificate
- `ca.key`: The CA certificate key

/// details | Example output: file list CA certificate
    type: example
/// tab | CA certificate and key files
```
$ ls -al
total 8
drwxrwxr-x  2 nokia nokia   80 May 25 08:38 .
drwxrwxrwt 11 root  root   480 May 25 08:38 ..
-rw-rw-r--  1 nokia nokia 1675 May 25 08:38 ca.key
-rw-rw-r--  1 nokia nokia 1367 May 25 08:38 ca.pem
```
///
///

Now you need to create the :material-router: P1 certificate and sign it using the CA you just created.  This can also be done using the built-in helper from `containerlab`.

/// tab | Command
```
containerlab tools cert sign --ca-cert ca.pem --ca-key ca.key --hosts clab-srexperts-p1
```
///
/// tab | Example output
```text {.no-copy}
20:17:34 INFO Creating and signing certificate Hosts=[clab-srexperts-p1] CN=containerlab.dev C=Internet L=Server O=Containerlab OU="Containerlab Tools"
```
///

This will have created two more files in your current directory:

- `cert.pem`: The TLS certificate
- `cert.key`: The TLS certificate key

/// details | Example output: file list :material-router: P1 certificate
    type: example
/// tab | CA certificate and key files
```
$ ls -al
total 16
drwxrwxr-x  2 nokia nokia  120 May 25 08:46 .
drwxrwxrwt 11 root  root   480 May 25 08:38 ..
-rw-rw-r--  1 nokia nokia 1675 May 25 08:38 ca.key
-rw-rw-r--  1 nokia nokia 1367 May 25 08:38 ca.pem
-rw-rw-r--  1 nokia nokia 1675 May 25 08:46 cert.key
-rw-rw-r--  1 nokia nokia 1363 May 25 08:46 cert.pem
```
///
///

You now have all the certificates you need to configure :material-router: P1 to use TLS for gRPC connections.

#### Copy the certificates to the router and install them into the routers PKI system

Now copy the signed certificate file and the certificate key to `cf3:/` on :material-router: P1.

/// details | If you need assistance click here
    type: tip

/// tab | copy commands
``` bash
scp -q cert.key admin@clab-srexperts-p1:cf3:/
scp -q cert.pem admin@clab-srexperts-p1:cf3:/
```
///

///

SSH to :material-router: P1 and install the certificate and key files you just copied to ``cf3:/`` using the
``admin system security pki import`` command to import the certificate and the certificate key into the SR OS PKI system.

/// details | If you need assistance click here
    type: tip

/// tab | copy commands
```
admin system security pki import input-url cf3:/cert.pem format pem output-file srx.crt type certificate
admin system security pki import input-url cf3:/cert.key format pem output-file srx.key type key
```
///

///

You should now have two files in the ``cf3:/system-pki/`` directory, ``srx.crt`` and ``srx.key``.  Confirm this now.

/// details | If you need assistance click here
    type: tip

/// tab | Command
```
file list cf3:/system-pki/
```
///
/// tab | Example output
```
Volume in drive cf3 on slot A has no label.

Directory of cf3:\system-pki\

04/22/2026  08:34p      <DIR>          ./
04/22/2026  08:34p      <DIR>          ../
04/22/2026  08:34p                1029 srx.crt
04/22/2026  08:34p                1254 srx.key
               2 File(s)                   2283 bytes.
               2 Dir(s)            123782176768 bytes free.
```
///
///

Now from the router's CLI prompt, confirm that the certificate looks to be correctly installed.  Use the
`admin system security pki show file-content` command to do this.

/// hint | Hint
The certificate will now be in `der` format.
///


/// details | If you need assistance click here
    type: tip

/// tab | Command
```
admin system security pki show file-content cf3:/system-pki/srx.crt format der type certificate
```
///
/// tab | Example output
```
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 1658 (0x67a)
        Signature Algorithm: sha256WithRSAEncryption
        Issuer: C=Internet, L=Server, O=Containerlab, OU=Containerlab Tools, CN=containerlab.dev
        Validity
            Not Before: Apr 22 20:17:34 2026 GMT
            Not After : Apr 19 20:17:34 2036 GMT
        Subject: C=Internet, L=Server, O=Containerlab, OU=Containerlab Tools, CN=containerlab.dev
        Subject Public Key Info:
            Public Key Algorithm: rsaEncryption
                Public-Key: (2048 bit)
                Modulus:
                    00:b6:32:15:93:aa:eb:51:51:e8:a6:75:2e:c3:69:
                    d6:af:cd:d0:c4:15:34:a7:42:76:10:95:fd:9b:f3:
                    10:7c:e1:60:5e:7f:5f:50:ae:0d:e2:37:b2:44:a3:
                    f3:cf:0a:9e:4c:28:ed:b6:37:86:58:a2:e8:9c:67:
                    6c:5a:35:f7:f2:0d:7f:8d:ad:d7:84:ee:ed:5c:c3:
                    43:f2:ce:96:aa:42:73:4d:ee:04:b8:46:f8:04:01:
                    f0:6f:ff:d7:09:4c:f5:eb:07:e6:a7:d5:8c:cb:98:
                    29:70:f9:c1:b0:fd:1e:18:b9:9d:c5:48:ff:2a:2e:
                    c4:7c:46:5e:f8:cf:40:98:60:20:43:56:59:6d:66:
                    78:f8:bd:7e:83:1b:a1:30:27:38:5b:99:a8:a1:48:
                    88:5b:1b:0b:35:ba:93:f9:bf:18:41:2d:83:80:5d:
                    bb:43:63:50:12:96:29:b6:a8:50:8a:00:4b:0c:62:
                    7e:21:60:87:77:9a:26:0b:6f:5b:92:2a:54:d7:ae:
                    6e:f0:28:b7:6e:eb:7d:c2:d3:83:a1:45:d2:30:3e:
                    08:26:ce:69:eb:bd:cf:d4:15:5a:83:19:21:55:b2:
                    28:59:25:03:61:49:82:27:70:f4:0d:09:82:e0:e3:
                    19:ed:1a:c2:a1:1d:fe:b9:d7:be:8d:e9:fd:04:af:
                    dd:2d
                Exponent: 65537 (0x10001)
        X509v3 extensions:
```
///
///

#### Configure the router to use TLS for gRPC

It is now time to configure the SR OS device :material-router: P1 to enable TLS for gRPC.

The configuration for TLS is extensive and so it is provided for you.

Apply the configuration below and use the `compare` command **before** you `commit` to visualize the changes.

/// tab | Configuration
```
+   /configure system grpc tls-server-profile "srx-tls-profile"
+   /configure system security tls cert-profile "srexperts" admin-state enable
+   /configure system security tls cert-profile "srexperts" entry 1 certificate-file "srx.crt"
+   /configure system security tls cert-profile "srexperts" entry 1 key-file "srx.key"
+   /configure system security tls server-cipher-list "srx-ciphers" tls12-cipher 1 name tls-rsa-with3des-ede-cbc-sha
+   /configure system security tls server-tls-profile "srx-tls-profile" admin-state enable
+   /configure system security tls server-tls-profile "srx-tls-profile" cert-profile "srexperts"
+   /configure system security tls server-tls-profile "srx-tls-profile" cipher-list "srx-ciphers"
```
///
/// tab | `compare` output
``` bash hl_lines="4 5"
    configure {
        system {
            grpc {
+               tls-server-profile "srx-tls-profile"
-               allow-unsecure-connection
            }
            security {
+               tls {
+                   cert-profile "srexperts" {
+                       admin-state enable
+                       entry 1 {
+                           certificate-file "srx.crt"
+                           key-file "srx.key"
+                       }
+                   }
+                   server-cipher-list "srx-ciphers" {
+                       tls12-cipher 1 {
+                           name tls-rsa-with3des-ede-cbc-sha
+                       }
+                   }
+                   server-tls-profile "srx-tls-profile" {
+                       admin-state enable
+                       cert-profile "srexperts"
+                       cipher-list "srx-ciphers"
+                   }
+               }
            }
        }
    }
```
Note that when you configure TLS, SR OS automatically disables unsecure connections.

In SR OS only a single gRPC server can be enabled, and it is set up with or without encryption, but you cannot have both in simultaneously. This is different in SR Linux, where multiple gRPC server configurations can coexist as long as they are using different TCP ports.
///

The configuration is comprised of four sections:

- A certificate profile that references the TLS keys we created
- A cipher list detailing the encryption ciphers that are to be used
- A TLS server profile used to tie the certificate profile and the cipher list together
- Configuration of the gRPC server to use TLS encryption instead of the insecure method

Once you are ready, you can `commit` your configuration.

### Intercept the streaming telemetry data again

You had previously stopped your streaming telemetry session.  You now need to start it again.

First try to start the streaming telemetry session using the exact command you used earlier.

/// details | If you need assistance click here
    type: tip

/// tab | Command
```
gnmic -a clab-srexperts-p1:57400 -u admin -p $EVENT_PASSWORD --insecure \
     subscribe --path=/state/router[router-name=Base]/interface[interface-name=pe2]/ipv4/statistics
```
///
///

You will notice that your session does not produce any output.

You can also check (in another window, leave the `gnmic` command running) that you do
not actually have a connection to the router.  You can check this using the following command on SR OS.

/// tab | Command
```
show system grpc connection
```
///
/// tab | Example output
```
===============================================================================
gRPC Server connections
===============================================================================
No. of connections        : 0
===============================================================================
```
///

The reason you have no connection is that you attempted to make an insecure connection (without TLS) to a TLS enabled router.

Now you can request a secure gNMI streaming telemetry session.  Use the ``gnmic`` tool again but replace the ``--insecure`` flag with
the appropriate TLS options.

/// hint | Hint
You will need to supply the signed TLS certificate, and the CA certificate.
///

/// details | If you need assistance click here
    type: tip

/// tab | Command
```
gnmic -a clab-srexperts-p1:57400 subscribe -u admin -p $EVENT_PASSWORD  \
    --path=/state/router[router-name=Base]/interface[interface-name=pe2]/ipv4/statistics \
    --tls-ca ca.pem
```
///
/// tab | Example output
``` json
{
  "source": "clab-srexperts-p1:57400",
  "subscription-name": "default-1779701013",
  "timestamp": 1779701013348159447,
  "time": "2026-05-25T09:23:33.348159447Z",
  "prefix": "state/router[router-name=Base]/interface[interface-name=pe2]/ipv4/statistics",
  "updates": [
    {
      "Path": "out-packets",
      "values": {
        "out-packets": "343169"
      }
    },
    {
      "Path": "out-octets",
      "values": {
        "out-octets": "36902326"
      }
    },
    {
      "Path": "out-discard-packets",
      "values": {
        "out-discard-packets": "0"
      }
    },
    {
      "Path": "out-discard-octets",
      "values": {
        "out-discard-octets": "0"
      }
    },
    {
      "Path": "in-packets",
      "values": {
        "in-packets": "0"
      }
    },
    {
      "Path": "in-octets",
      "values": {
        "in-octets": "0"
      }
    },
    {
      "Path": "urpf-check-fail-packets",
      "values": {
        "urpf-check-fail-packets": "0"
      }
    },
    {
      "Path": "urpf-check-fail-octets",
      "values": {
        "urpf-check-fail-octets": "0"
      }
    },
    {
      "Path": "out-discard-dbcast-packets",
      "values": {
        "out-discard-dbcast-packets": "0"
      }
    },
    {
      "Path": "out-discard-dbcast-octets",
      "values": {
        "out-discard-dbcast-octets": "0"
      }
    },
    {
      "Path": "in-ip-helper-redirects-packets",
      "values": {
        "in-ip-helper-redirects-packets": "0"
      }
    },
    {
      "Path": "in-ip-helper-redirects-octets",
      "values": {
        "in-ip-helper-redirects-octets": "0"
      }
    }
  ]
}
{
  "sync-response": true
}
```
///
///

Now with your TLS secured gNMI streaming telemetry session running in one window, look back at your running `tshark` process in the other window.
You should now see that you cannot decipher the data traveling over the wire to the management station (if you recall, we could clearly see, as
an example, the word "statistics" before).  You have solved the interception concerns!

/// hint | Hint
If you accidentally closed your ``tshark`` process, the command to run it is:

```
sudo tshark -ni any -f "src clab-srexperts-p1 and port 57400" -P -x
```
///

### Final cleanup task

You have completed all the tasks but before you go to another one you must restore the gRPC `allow-unsecure-connection` configuration on :material-router: P1 to avoid impact on other activities.  You may use the MD-CLI or `gnmic` to do this.

You will find both options below, but you only need to do the configuration in one.

If you choose to use `gnmic`, you will use a gRPC session secured with TLS, to switch the protocol to insecure mode.  As you apply the configuration, you will notice that SR OS closes the TLS session.

/// tab | MD-CLI commands on :material-router: P1
``` text
/configure system grpc allow-unsecure-connection
```

Don't forget to `commit`.
///

/// tab | `gnmic` from your hackathon instance

/// tab | Command
``` bash
gnmic -a clab-srexperts-p1 -u admin -p $EVENT_PASSWORD \
  --tls-cert cert.pem --tls-ca ca.pem set \
  --update-path '/configure/system/grpc' \
  --update-value '{"allow-unsecure-connection":[null]}'
```
///
/// tab | Expected output
```
target "clab-srexperts-p1" set request failed: target "clab-srexperts-p1" SetRequest failed: rpc error: code = Canceled desc = INFO: MGMT_CORE #2003: Session terminated - server shutdown
Error: one or more requests failed
```

Note that despite the error, the configuration is applied.
///
///

Validate the configuration and use `gnmic` to confirm that gRPC is once again working insecurely.

/// tab | Command
``` bash
gnmic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure capabilities
```
///
/// tab | Expected output
```bash {.no-copy}
gNMI version: 0.8.0
supported models:
  - nokia-conf, Nokia, 26.3.R1
  - nokia-state, Nokia, 26.3.R1
  - nokia-bof-conf, Nokia, 26.3.R1
  - nokia-bof-state, Nokia, 26.3.R1
  - nokia-debug-conf, Nokia, 26.3.R1
  - nokia-debug-state, Nokia, 26.3.R1
  - nokia-li-conf, Nokia, 26.3.R1
  - nokia-li-state, Nokia, 26.3.R1
supported encodings:
  - JSON
  - BYTES
  - PROTO
  - JSON_IETF
```
///


## Summary

Congratulations!  If you've got this far you have achieved your goal of securing your streaming telemetry data.

In this activity you have:

- Learned a little about streaming telemetry and seen it in action reporting interface statistics
- Dealt with YANG modelled gNMI paths
- Created, signed and installed TLS certificates
- Created and used a certificate authority (CA)
- Provisioned a gRPC server to provide secure streaming telemetry communications
- Saved your organization from potential data loss

If you'd like to extend this activity further you could:

- Secure the gNMI streaming telemetry on other routers
- Write a script to rollout the deployment of the certificates and the TLS configuration

Alternatively, consider trying this years activity on enabling mutual TLS (mTLS) certificates.

