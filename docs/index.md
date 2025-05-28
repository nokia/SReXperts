---
hide:
  - navigation
---

# Welcome to the Hackathon at SReXperts 2025

Welcome to the 2025 SReXperts hackathon.

We are very glad to welcome you to this special event, the 20th anniversary for SReXperts (and the 5th for the hackathon).

Nokia prides itself on the excellent technical products, solutions that we deliver to the market, and this hackathon is no exception.  A large team of engineers,
developers and product managers have been working hard to deliver what, we'll hope you agree, is a challenging and informative set of activities to challenge
you, no matter what you experience level.

## Open to all and something for everyone

Whether you're a relative novice to Nokia's products, or a seasoned expert, there is something in this hackathon for you!  All you will need is your trusty laptop,
an afternoon of focus and possibly some coffee (supplied!) and you should find something to benefit both you and your organizations.

## Getting started

This page is your starting point into the hackathon, it should get you familiar with the lab environment provided by Nokia, and provide an overview of the suggested sample activities.

**Please read this page all the way through before attempting any of the activities.**

During the afternoon you will work in groups (or alone if you prefer) on any projects that you are inspired to tackle or on one of the pre-provided activities of varying difficulty.

As long as you have a laptop with the ability to SSH and a web broswer, we have example activities and a generic lab topology to help you progress if you don’t have something specific already in mind.

Need help, not a problem, pop your hand in the air and an eager expert will be there to guide you.

## Lab Environment

For this hackathon each (group of) participant(s) will receive their own dedicated cloud instance (VM) running a copy of the generic lab topology.  You will see this called "your VM",
"your group's hackathon VM", "your instance", "your server" and other similar phrases in the activities.  They all mean the same thing, your own dedicated could instance.

If everything went according to plan, you should have received a physical piece of paper which contains:

- a group ID allocated to your group (or to yourself if you're working alone).
- SSH credentials to a public cloud instance dedicated to your group.
- HTTPS URL's for this repository and access to a web based IDE in case you don't have one installed on your operating system.

/// warning
The public cloud compute instances will be destroyed once the hackathon is concluded.</p>
Please make sure to backup any code, config, etc. <u>offline</u> (e.g. onto your laptop) if you'd like to keep it after the hacakthon.
///

### Group ID

Please refer to the paper provided by the hackathon session leader. If nothing has been provided, not a problem, pop your hand in the air and someone will allocate you one before you can say "Aequeosalinocalcalinoceraceoaluminosocupreovitriolic".

| Group ID | hostname instance |
| --- | --- |
| 1 | 1.srexperts.net |
| 2 | 2.srexperts.net |
| ... | ... |
| **X** | **X**.srexperts.net |

### SSH

The simplest way to get going is to use your SSH client to connect to your group's hackathon VM instance and work from there.  All tools and applications are pre-installed and you will have direct access to your entire network. 

SSH is also important if you want to driectly access your network from your laptop but more on that later.

|     |     |
| --- | --- |
| hostname | `refer to the paper provided or the slide presented` |
| username | `refer to the paper provided or the slide presented` |
| password | `refer to the paper provided or the slide presented` |

/// tip
If you're familiar with SSH and wish to setup passwordless access, you can use `ssh-keygen -h` to generate a public/private key pair and then `ssh-copy-id` to copy it towards your group's hackathon instance.
///

### WiFi

WiFi is important here.  Without it your hackathon experience is going to be rather dull.  To connect to the hackthon event's WiFi, refer to the paper provided or the slide presented.

### Topology

When accessing your hackathon VM instance you'll the [SReXperts GitHub repository](https://github.com/nokia/srexperts) that contains all of the documentation, examples, solutions and loads of other great stuff, has already been cloned for you.

In this hackathon, every group has their own complete service-provider network at their disposal.  Your network comprises an IP backbone with Provider (P) and Provider Edge (PE) router, a broadband dial-in network, a peering edge network, an internet exchange point, multiple data-centers and a number of client and subscriber devices.  This network is already deployed and provisioned and is ready to go!

*Don't worry: This is your personal group network, you cannot impact any other groups.*

-{{ diagram(url='srexperts/hackathon-diagrams/main/SReXperts2025.drawio', title='Topology', page=0) }}-

The above topology contains a number of functional blocks to help you in area's you might want to focus on, it contains:

- Routing:
    - SR-MPLS (Dual-Stack ISIS)
    - MP-BGP (SAFIs with IPv6 next-hop) ; single node (vRR) route-reflector
    - 2x P-nodes (SR OS)
    - 4x PE-nodes (SR OS)
    - 1x route-reflector (SR Linux)
- Data Centers:
    - DC1: a CLOS model
        - 2x spines (spine11|spine12) and 3 leaf switches (leaf11|leaf12|leaf13)
    - DC2: a single leaf (leaf21) to demonstrate Data Center Interconnect usecases
    - IPv6 BGP unnumbered configured in the underlay
    - DCGW Integration:
        - DC1: PE2 and PE3
        - DC2: PE1 and PE4
    - a Data Center interconnect using a MPLS IP-VPN (EVPN/IPVPN integration):
        - VPRN "DCI" and EVPN/VPLS "IPVRF201" and EVPN/VPLS "IPVRF202"
- Subscriber management (BNG+NAT) on PE4
- a Transit/Peering setup with RPKI available on PE1
- a fully working telemetry stack (gNMIc/prometheus/grafana + syslog/promtail/loki)
- Linux clients are attached to both the GRT and VPRN services allowing a full mesh of traffic.

### Accessing Topology nodes

#### From your group's hackathon instance VM

To access the lab nodes from within the VM, users should identify the names of the deployed nodes using the `sudo containerlab inspect -a` command.  You will notice they all start with `clab-srexperts-`.  Your entire network is [powered by ContainerLab](https://containerlab.dev).

If you'd like to see the full list of devices, their hostnames and IP addresses in your network use the following command.

/// tab | cmd

``` bash
sudo containerlab inspect -a
```

///
/// tab | output

``` bash
╭─────────────────────────────┬───────────┬────────────────────────────────────┬─────────────────────────────────────────────┬───────────┬────────────────╮
│           Topology          │  Lab Name │                Name                │                  Kind/Image                 │   State   │ IPv4/6 Address │
├─────────────────────────────┼───────────┼────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│ SReXperts/clab/srx.clab.yml │ srexperts │ clab-srexperts-agg1                │ nokia_srlinux                               │ running   │ 10.128.1.52    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-client01            │ linux                                       │ running   │ 10.128.1.25    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-client02            │ linux                                       │ running   │ 10.128.1.26    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-client03            │ linux                                       │ running   │ 10.128.1.27    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-client04            │ linux                                       │ running   │ 10.128.1.28    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-client11            │ linux                                       │ running   │ 10.128.1.36    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-client12            │ linux                                       │ running   │ 10.128.1.37    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-client13            │ linux                                       │ running   │ 10.128.1.38    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-client21            │ linux                                       │ running   │ 10.128.1.42    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-codeserver          │ linux                                       │ running   │ 10.128.1.90    │
│                             │           │                                    │ ghcr.io/coder/code-server:latest            │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-dns                 │ linux                                       │ running   │ 10.128.1.15    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-gnmic               │ linux                                       │ running   │ 10.128.1.71    │
│                             │           │                                    │ ghcr.io/openconfig/gnmic:0.38.2             │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-grafana             │ linux                                       │ running   │ 10.128.1.73    │
│                             │           │                                    │ grafana/grafana:10.3.5                      │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-ixp1                │ nokia_srlinux                               │ running   │ 10.128.1.51    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-leaf11              │ nokia_srlinux                               │ running   │ 10.128.1.33    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-leaf12              │ nokia_srlinux                               │ running   │ 10.128.1.34    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-leaf13              │ nokia_srlinux                               │ running   │ 10.128.1.35    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-leaf21              │ nokia_srlinux                               │ running   │ 10.128.1.41    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-loki                │ linux                                       │ running   │ 10.128.1.76    │
│                             │           │                                    │ grafana/loki:2.9.7                          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-netbox              │ linux                                       │ running   │ 10.128.1.81    │
│                             │           │                                    │ docker.io/netboxcommunity/netbox:v4.2-3.2.0 │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-netbox-housekeeping │ linux                                       │ running   │ 10.128.1.83    │
│                             │           │                                    │ docker.io/netboxcommunity/netbox:v4.2-3.2.0 │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-netbox-worker       │ linux                                       │ running   │ 10.128.1.82    │
│                             │           │                                    │ docker.io/netboxcommunity/netbox:v4.2-3.2.0 │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-p1                  │ nokia_sros                                  │ running   │ 10.128.1.11    │
│                             │           │                                    │ vr-sros:25.3.R1                             │ (healthy) │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-p2                  │ nokia_sros                                  │ running   │ 10.128.1.12    │
│                             │           │                                    │ vr-sros:25.3.R1                             │ (healthy) │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-pe1                 │ nokia_sros                                  │ running   │ 10.128.1.21    │
│                             │           │                                    │ vr-sros:25.3.R1                             │ (healthy) │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-pe2                 │ nokia_sros                                  │ running   │ 10.128.1.22    │
│                             │           │                                    │ vr-sros:25.3.R1                             │ (healthy) │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-pe3                 │ nokia_sros                                  │ running   │ 10.128.1.23    │
│                             │           │                                    │ vr-sros:25.3.R1                             │ (healthy) │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-pe4                 │ nokia_sros                                  │ running   │ 10.128.1.24    │
│                             │           │                                    │ vr-sros:25.3.R1                             │ (healthy) │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-peering2            │ nokia_srlinux                               │ running   │ 10.128.1.53    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-postgres            │ linux                                       │ running   │ 10.128.1.84    │
│                             │           │                                    │ docker.io/postgres:17-alpine                │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-prometheus          │ linux                                       │ running   │ 10.128.1.72    │
│                             │           │                                    │ prom/prometheus:v2.51.2                     │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-promtail            │ linux                                       │ running   │ 10.128.1.75    │
│                             │           │                                    │ grafana/promtail:2.9.7                      │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-radius              │ linux                                       │ running   │ 10.128.1.14    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-redis               │ linux                                       │ running   │ 10.128.1.85    │
│                             │           │                                    │ docker.io/valkey/valkey:8.0-alpine          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-redis-cache         │ linux                                       │ running   │ 10.128.1.86    │
│                             │           │                                    │ docker.io/valkey/valkey:8.0-alpine          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-rpki                │ linux                                       │ running   │ 10.128.1.55    │
│                             │           │                                    │ rpki/stayrtr                                │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-spine11             │ nokia_srlinux                               │ running   │ 10.128.1.31    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-spine12             │ nokia_srlinux                               │ running   │ 10.128.1.32    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-sub1                │ linux                                       │ running   │ 10.128.1.61    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-sub2                │ linux                                       │ running   │ 10.128.1.62    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-sub3                │ linux                                       │ running   │ 10.128.1.63    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-syslog              │ linux                                       │ running   │ 10.128.1.74    │
│                             │           │                                    │ linuxserver/syslog-ng:4.5.0                 │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-transit1            │ linux                                       │ running   │ 10.128.1.54    │
│                             │           │                                    │ ghcr.io/srl-labs/network-multitool          │           │ N/A            │
│                             │           ├────────────────────────────────────┼─────────────────────────────────────────────┼───────────┼────────────────┤
│                             │           │ clab-srexperts-vRR                 │ nokia_srlinux                               │ running   │ 10.128.1.13    │
│                             │           │                                    │ ghcr.io/nokia/srlinux:24.10.4               │           │ N/A            │
╰─────────────────────────────┴───────────┴────────────────────────────────────┴─────────────────────────────────────────────┴───────────┴────────────────╯
```

///

Using the names from the above output, we can login to the a node using the following command:

For example, to access the `clab-srexperts-pe1` node via ssh simply type:

``` bash
ssh admin@clab-srexperts-pe1
```

#### From the Internet

Each public cloud instance has a port-range (`50000` - `51000`) exposed towards the Internet, as lab nodes spin up, a public port is allocated by the docker daemon on the public cloud instance. You can utilize those to access the lab services straight from your laptop via the Internet.

With the `show-ports` command executed on a VM you get a list of mappings between external and internal ports allocated for each node of a lab:
/// tab | cmd

``` bash
show-ports
```

///
/// tab | output

``` bash
Name                       Forwarded Ports
clab-srexperts-agg1        50052 -> 22, 50352 -> 57400
clab-srexperts-client01    50025 -> 22
clab-srexperts-client02    50026 -> 22
clab-srexperts-client03    50027 -> 22
clab-srexperts-client04    50028 -> 22
clab-srexperts-client11    50036 -> 22
clab-srexperts-client12    50037 -> 22
clab-srexperts-client13    50038 -> 22
clab-srexperts-client21    50042 -> 22
clab-srexperts-codeserver  80 -> 8080
clab-srexperts-dns         50015 -> 22
clab-srexperts-grafana     3000 -> 3000
clab-srexperts-ixp1        50051 -> 22, 50351 -> 57400
clab-srexperts-leaf11      50033 -> 22, 50333 -> 57400
clab-srexperts-leaf12      50034 -> 22, 50334 -> 57400
clab-srexperts-leaf13      50035 -> 22, 50335 -> 57400
clab-srexperts-leaf21      50041 -> 22, 50341 -> 57400
clab-srexperts-netbox      8000 -> 8080
clab-srexperts-p1          50011 -> 22, 50411 -> 830, 50311 -> 57400
clab-srexperts-p2          50012 -> 22, 50412 -> 830, 50312 -> 57400
clab-srexperts-pe1         50021 -> 22, 50421 -> 830, 50321 -> 57400
clab-srexperts-pe2         50022 -> 22, 50422 -> 830, 50322 -> 57400
clab-srexperts-pe3         50023 -> 22, 50423 -> 830, 50323 -> 57400
clab-srexperts-pe4         50024 -> 22, 50424 -> 830, 50324 -> 57400
clab-srexperts-peering2    50053 -> 22, 50353 -> 57400
clab-srexperts-prometheus  9090 -> 9090
clab-srexperts-radius      50014 -> 22
clab-srexperts-spine11     50031 -> 22, 50331 -> 57400
clab-srexperts-spine12     50032 -> 22, 50332 -> 57400
clab-srexperts-sub1        50061 -> 22
clab-srexperts-sub2        50062 -> 22
clab-srexperts-sub3        50063 -> 22
clab-srexperts-transit1    50054 -> 22
clab-srexperts-vRR         50013 -> 22, 50413 -> 830, 50313 -> 57400
```

///

Each service exposed on a lab node gets a unique external port number as per the table above. For example, Grafana's web interface is available on port `3000` of the VM which is mapped to Grafana's node internal port of `3000`.

The following table shows common container internal ports which can assist you to find the correct exposed port for the services.

| Service    | Internal Port number |
| ---------- | -------------------- |
| SSH        | 22                   |
| VSCode     | 80                   |
| Netconf    | 830                  |
| gNMI       | 57400                |
| HTTP/HTTPS | 80/443               |
| Grafana    | 3000                 |
| Netbox     | 8000                 |
| EDA        | 9443                 |

Subsequently you can access the lab node on the external port for your given instance using the DNS name of the assigned VM.

| Group ID | hostname instance |
| --- | --- |
| **X** | **X**.srexperts.net |

In the example above, accessing `pe1` would be possible by:

```
ssh admin@X.srexperts.net -p 50021
```

In the example above, accessing grafana would be possible browsing towards **http://X.srexperts.net:3000** (where X is the group ID you've been allocated)

/// details | ssh-config
    type: tip

You can generate `ssh-config` using the `generate-ssh-config` command and store the output on your local laptop's SSH client, in order to connect directly to nodes.
///

### Generate Traffic

In the generic topology, linux clients are attached to a number of routers:

- the PE layer
- the leafs in each data center
- in multiple VRFs: global routing table (grt) and vprn "dci" (vprn.dci)

One can start and/or stop traffic by connecting to the relevant client using SSH, and running `/traffic.sh`, for example:

```
ssh user@clab-srexperts-client11

client11:~$ /traffic.sh [-a <start|stop>] [-d <dns hostname>]
```

The dns hostname is composed out of the client name and a domain suffix.

| SSH | Client | Global Routing Table suffix | VPRN "DCI" suffix |
| --- | --- | --- | --- |
| clab-srexperts-client01 | client01 | .grt | .vprn.dci |
| clab-srexperts-client02 | client02 | .grt | .vprn.dci |
| clab-srexperts-client03 | client03 | .grt | .vprn.dci |
| clab-srexperts-client04 | client04 | .grt | .vprn.dci |
| clab-srexperts-client11 | client11 | .grt | .vprn.dci |
| clab-srexperts-client12 | client12 | .grt | .vprn.dci |
| clab-srexperts-client13 | client13 | .grt | .vprn.dci |
| clab-srexperts-client14 | client21 | .grt | .vprn.dci |

For example, if you'd like to start a unidirectional traffic flow from `client11` to `client21` in the global routing table:

```
client11:~$ /traffic.sh -a start -d client21.grt
starting traffic to client21.grt, binding on client11.grt, saving logs to /tmp/client21.grt.log
```

Stopping the traffic flow would be achieved by:

```
client11:~$ /traffic.sh -a stop -d client21.grt
stopping traffic to client21.grt
```

However, if you'd like to start a full mesh of traffic between `client11` and the rest of the clients, this could be achieved by executing:

```
client11:~$ /traffic.sh -a start -d all.grt
starting traffic to client01.grt, binding on client11.grt, saving logs to /tmp/client01.grt.log
starting traffic to client02.grt, binding on client11.grt, saving logs to /tmp/client02.grt.log
starting traffic to client03.grt, binding on client11.grt, saving logs to /tmp/client03.grt.log
starting traffic to client04.grt, binding on client11.grt, saving logs to /tmp/client04.grt.log
starting traffic to client12.grt, binding on client11.grt, saving logs to /tmp/client12.grt.log
starting traffic to client13.grt, binding on client11.grt, saving logs to /tmp/client13.grt.log
starting traffic to client21.grt, binding on client11.grt, saving logs to /tmp/client21.grt.log

client11:~$ /traffic.sh -a stop -d all.grt
stopping traffic to client01.grt
stopping traffic to client02.grt
stopping traffic to client03.grt
stopping traffic to client04.grt
stopping traffic to client12.grt
stopping traffic to client13.grt
stopping traffic to client21.grt
```

## FAQ

### My employer/security department locked down my laptop

No worries, we have got you covered! Each instance is running a web-based VSCode code server, when accessing it at `http://<my group id>.srexperts.net` should prompt you for a password (which is documented on the physical paper provided), and you should be able to access the topology through the terminal there.

### Help! I've bricked my lab, how do I redeploy?

First we destroy the lab:
/// tab | cmd

``` bash
sudo -E clab destroy -t $HOME/SReXperts/clab/srx.clab.yml --cleanup
```

///

/// tab | output

``` bash
12:41:14 INFO Parsing & checking topology file=srx.clab.yml
12:41:14 INFO Parsing & checking topology file=srx.clab.yml
12:41:15 INFO Destroying lab name=srexperts
12:41:15 INFO Removed container name=clab-srexperts-netbox
12:41:17 INFO Removed container name=clab-srexperts-redis
12:41:19 INFO Removed container name=clab-srexperts-loki
12:41:24 INFO Removed container name=clab-srexperts-agg1
12:41:24 INFO Removed container name=clab-srexperts-syslog
12:41:24 INFO Removed container name=clab-srexperts-netbox-worker
12:41:25 INFO Removed container name=clab-srexperts-codeserver
12:41:25 INFO Removed container name=clab-srexperts-leaf11
12:41:25 INFO Removed container name=clab-srexperts-redis-cache
12:41:26 INFO Removed container name=clab-srexperts-vRR
12:41:26 INFO Removed container name=clab-srexperts-leaf21
12:41:26 INFO Removed container name=clab-srexperts-peering2
12:41:26 INFO Removed container name=clab-srexperts-netbox-housekeeping
12:41:26 INFO Removed container name=clab-srexperts-spine11
12:41:27 INFO Removed container name=clab-srexperts-prometheus
12:41:27 INFO Removed container name=clab-srexperts-rpki
12:41:27 INFO Removed container name=clab-srexperts-postgres
12:41:27 INFO Removed container name=clab-srexperts-promtail
12:41:27 INFO Removed container name=clab-srexperts-ixp1
12:41:27 INFO Removed container name=clab-srexperts-leaf12
12:41:27 INFO Removed container name=clab-srexperts-spine12
12:41:28 INFO Removed container name=clab-srexperts-gnmic
12:41:28 INFO Removed container name=clab-srexperts-grafana
12:41:28 INFO Removed container name=clab-srexperts-sub2
12:41:28 INFO Removed container name=clab-srexperts-client04
12:41:28 INFO Removed container name=clab-srexperts-leaf13
12:41:28 INFO Removed container name=clab-srexperts-radius
12:41:28 INFO Removed container name=clab-srexperts-dns
12:41:28 INFO Removed container name=clab-srexperts-sub3
12:41:28 INFO Removed container name=clab-srexperts-client03
12:41:28 INFO Removed container name=clab-srexperts-client11
12:41:28 INFO Removed container name=clab-srexperts-client21
12:41:29 INFO Removed container name=clab-srexperts-sub1
12:41:29 INFO Removed container name=clab-srexperts-client13
12:41:29 INFO Removed container name=clab-srexperts-client02
12:41:29 INFO Removed container name=clab-srexperts-client01
12:41:29 INFO Removed container name=clab-srexperts-transit1
12:41:29 INFO Removed container name=clab-srexperts-client12
12:41:29 INFO Removed container name=clab-srexperts-pe2
12:41:29 INFO Removed container name=clab-srexperts-pe4
12:41:29 INFO Removed container name=clab-srexperts-pe1
12:41:30 INFO Removed container name=clab-srexperts-pe3
12:41:30 INFO Removed container name=clab-srexperts-p1
12:41:30 INFO Removed container name=clab-srexperts-p2
12:41:30 INFO Removing host entries path=/etc/hosts
12:41:30 INFO Removing SSH config path=/etc/ssh/ssh_config.d/clab-srexperts.conf
```

///
/// tab | alternate
This takes on average 20 min to redeploy, can't wait that long? pop up your hand and ask for a new instance!

``` bash
sudo reboot
```

///

Secondly, we can deploy the lab again:
/// tab | cmd

``` bash
CLAB_LABDIR_BASE=/home/nokia sudo -E clab deploy -t $HOME/SReXperts/clab/srx.clab.yml --reconfigure
```

///

/// tab | output

``` bash
12:45:38 INFO Containerlab started version=0.66.0
12:45:38 INFO Parsing & checking topology file=srx.clab.yml
12:45:38 INFO Creating docker network name=srexperts IPv4 subnet=10.128.1.0/24 IPv6 subnet="" MTU=0
12:45:38 INFO Creating lab directory path=/home/nokia/SReXperts/clab-srexperts
12:45:38 INFO Creating container name=p2
12:45:38 INFO Creating container name=p1
12:45:40 INFO Created link: p1:eth11 ▪┄┄▪ p2:eth11
12:45:40 INFO Adding configuration node=clab-srexperts-p2 type=partial source=/home/nokia/SReXperts/clab/configs/sros/p2.partial.cfg
12:45:40 INFO Adding public keys configuration node=clab-srexperts-p2
12:45:40 INFO Created link: p2:eth12 ▪┄┄▪ p1:eth12
12:45:40 INFO Waiting for node to be ready. This may take a while node=clab-srexperts-p2 log="docker logs -f clab-srexperts-p2"
12:45:41 INFO Adding configuration node=clab-srexperts-p1 type=partial source=/home/nokia/SReXperts/clab/configs/sros/p1.partial.cfg
12:45:41 INFO Adding public keys configuration node=clab-srexperts-p1
12:45:41 INFO Waiting for node to be ready. This may take a while node=clab-srexperts-p1 log="docker logs -f clab-srexperts-p1"
12:47:09 INFO node "p1" turned healthy, continuing
12:47:09 INFO Creating container name=pe1
12:47:09 INFO Creating container name=pe2
12:47:10 INFO Created link: p1:eth2 ▪┄┄▪ pe2:eth1
12:47:10 INFO Created link: p1:eth1 ▪┄┄▪ pe1:eth1
12:47:10 INFO Created link: p1:eth6 ▪┄┄▪ pe2:eth7
12:47:10 INFO Created link: p2:eth1 ▪┄┄▪ pe1:eth2
12:47:11 INFO Created link: p2:eth2 ▪┄┄▪ pe2:eth2
12:47:12 INFO Adding configuration node=clab-srexperts-pe2 type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe2.partial.cfg
12:47:12 INFO Adding public keys configuration node=clab-srexperts-pe2
12:47:12 INFO Waiting for node to be ready. This may take a while node=clab-srexperts-pe2 log="docker logs -f clab-srexperts-pe2"
12:47:12 INFO Adding configuration node=clab-srexperts-pe1 type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe1.partial.cfg
12:47:12 INFO Adding public keys configuration node=clab-srexperts-pe1
12:47:12 INFO Waiting for node to be ready. This may take a while node=clab-srexperts-pe1 log="docker logs -f clab-srexperts-pe1"
12:49:10 INFO node "pe2" turned healthy, continuing
12:49:10 INFO Creating container name=pe3
12:49:11 INFO node "pe1" turned healthy, continuing
12:49:11 INFO Creating container name=pe4
12:49:11 INFO Created link: p1:eth3 ▪┄┄▪ pe3:eth1
12:49:11 INFO Created link: p2:eth3 ▪┄┄▪ pe3:eth2
12:49:11 INFO Adding configuration node=clab-srexperts-pe3 type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe3.partial.cfg
12:49:11 INFO Adding public keys configuration node=clab-srexperts-pe3
12:49:11 INFO Waiting for node to be ready. This may take a while node=clab-srexperts-pe3 log="docker logs -f clab-srexperts-pe3"
12:49:12 INFO Created link: p1:eth4 ▪┄┄▪ pe4:eth1
12:49:12 INFO Created link: p2:eth4 ▪┄┄▪ pe4:eth2
12:49:13 INFO Adding configuration node=clab-srexperts-pe4 type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe4.partial.cfg
12:49:13 INFO Adding public keys configuration node=clab-srexperts-pe4
12:49:13 INFO Waiting for node to be ready. This may take a while node=clab-srexperts-pe4 log="docker logs -f clab-srexperts-pe4"
12:50:42 INFO node "pe4" turned healthy, continuing
12:50:42 INFO node "client11" is being delayed for 120 seconds
12:50:42 INFO node "client01" is being delayed for 120 seconds
12:50:42 INFO node "rpki" is being delayed for 120 seconds
12:50:42 INFO node "client21" is being delayed for 120 seconds
12:50:42 INFO node "client12" is being delayed for 120 seconds
12:50:42 INFO node "sub2" is being delayed for 120 seconds
12:50:42 INFO node "prometheus" is being delayed for 120 seconds
12:50:42 INFO node "promtail" is being delayed for 120 seconds
12:50:42 INFO node "client03" is being delayed for 120 seconds
12:50:42 INFO node "radius" is being delayed for 120 seconds
12:50:42 INFO node "netbox-worker" is being delayed for 120 seconds
12:50:42 INFO node "client04" is being delayed for 120 seconds
12:50:42 INFO node "redis-cache" is being delayed for 120 seconds
12:50:42 INFO node "netbox-housekeeping" is being delayed for 120 seconds
12:50:42 INFO node "codeserver" is being delayed for 120 seconds
12:50:42 INFO node "grafana" is being delayed for 120 seconds
12:50:42 INFO node "loki" is being delayed for 120 seconds
12:50:42 INFO node "transit1" is being delayed for 120 seconds
12:50:42 INFO node "sub3" is being delayed for 120 seconds
12:50:42 INFO node "client02" is being delayed for 120 seconds
12:50:42 INFO node "dns" is being delayed for 120 seconds
12:50:42 INFO node "netbox" is being delayed for 120 seconds
12:50:42 INFO node "redis" is being delayed for 120 seconds
12:50:42 INFO node "client13" is being delayed for 120 seconds
12:50:42 INFO node "syslog" is being delayed for 120 seconds
12:50:42 INFO Creating container name=peering2
12:50:42 INFO Creating container name=vRR
12:50:42 INFO node "postgres" is being delayed for 120 seconds
12:50:42 INFO node "gnmic" is being delayed for 120 seconds
12:50:42 INFO Creating container name=ixp1
12:50:42 INFO Creating container name=spine11
12:50:42 INFO Creating container name=agg1
12:50:42 INFO node "sub1" is being delayed for 120 seconds
12:50:42 INFO Creating container name=leaf12
12:50:42 INFO Creating container name=leaf11
12:50:42 INFO Creating container name=leaf13
12:50:42 INFO Creating container name=spine12
12:50:42 INFO Creating container name=leaf21
12:50:44 INFO Created link: pe2:eth3 ▪┄┄▪ spine11:e1-32
12:50:45 INFO Created link: pe4:eth3 ▪┄┄▪ agg1:e1-50
12:50:45 INFO Created link: pe3:eth3 ▪┄┄▪ spine11:e1-31
12:50:45 INFO Running postdeploy actions kind=nokia_srlinux node=peering2
12:50:45 INFO Created link: pe1:eth5 ▪┄┄▪ leaf21:e1-49
12:50:45 INFO Created link: pe2:eth4 ▪┄┄▪ spine12:e1-32
12:50:46 INFO Created link: spine11:e1-1 ▪┄┄▪ leaf11:e1-49
12:50:46 INFO Created link: p1:eth5 ▪┄┄▪ vRR:e1-1
12:50:46 INFO Created link: pe4:eth5 ▪┄┄▪ leaf21:e1-50
12:50:46 INFO Created link: p2:eth5 ▪┄┄▪ vRR:e1-2
12:50:46 INFO Created link: pe3:eth4 ▪┄┄▪ spine12:e1-31
12:50:46 INFO Running postdeploy actions kind=nokia_srlinux node=leaf21
12:50:46 INFO Created link: spine11:e1-2 ▪┄┄▪ leaf12:e1-49
12:50:47 INFO Created link: pe1:eth4 ▪┄┄▪ ixp1:e1-1
12:50:47 INFO Created link: spine12:e1-1 ▪┄┄▪ leaf11:e1-50
12:50:47 INFO Created link: spine11:e1-3 ▪┄┄▪ leaf13:e1-49
12:50:47 INFO Running postdeploy actions kind=nokia_srlinux node=spine11
12:50:47 INFO Running postdeploy actions kind=nokia_srlinux node=leaf12
12:50:47 INFO Created link: spine12:e1-2 ▪┄┄▪ leaf12:e1-50
12:50:47 INFO Running postdeploy actions kind=nokia_srlinux node=agg1
12:50:47 INFO Running postdeploy actions kind=nokia_srlinux node=leaf11
12:50:47 INFO Running postdeploy actions kind=nokia_srlinux node=vRR
12:50:47 INFO Created link: peering2:e1-2 ▪┄┄▪ ixp1:e1-2
12:50:48 INFO Created link: spine12:e1-3 ▪┄┄▪ leaf13:e1-50
12:50:48 INFO Running postdeploy actions kind=nokia_srlinux node=spine12
12:50:48 INFO Running postdeploy actions kind=nokia_srlinux node=ixp1
12:50:48 INFO Running postdeploy actions kind=nokia_srlinux node=leaf13
12:52:42 INFO Creating container name=transit1
12:52:42 INFO Creating container name=codeserver
12:52:42 INFO Creating container name=client04
12:52:42 INFO Creating container name=redis-cache
12:52:42 INFO Creating container name=netbox-worker
12:52:42 INFO Creating container name=syslog
12:52:42 INFO Creating container name=client21
12:52:42 INFO Creating container name=prometheus
12:52:42 INFO Creating container name=netbox
12:52:42 INFO Creating container name=promtail
12:52:42 INFO Creating container name=redis
12:52:42 INFO Creating container name=postgres
12:52:42 INFO Creating container name=client13
12:52:42 INFO Creating container name=client01
12:52:42 INFO Creating container name=client11
12:52:42 INFO Creating container name=dns
12:52:42 INFO Creating container name=client03
12:52:42 INFO Creating container name=netbox-housekeeping
12:52:42 INFO Creating container name=grafana
12:52:42 INFO Creating container name=gnmic
12:52:42 INFO Creating container name=rpki
12:52:42 INFO Creating container name=client12
12:52:42 INFO Creating container name=client02
12:52:42 INFO Creating container name=sub2
12:52:42 INFO Creating container name=radius
12:52:42 INFO Creating container name=sub1
12:52:42 INFO Creating container name=sub3
12:52:42 INFO Creating container name=loki
12:52:44 INFO Created link: pe2:eth6 ▪┄┄▪ client02:eth1
12:52:44 INFO Created link: pe1:eth3 ▪┄┄▪ transit1:eth1
12:52:45 INFO Created link: peering2:e1-1 ▪┄┄▪ transit1:eth2
12:52:45 INFO Created link: leaf11:e1-2 ▪┄┄▪ client12:eth1
12:52:45 INFO Created link: leaf12:e1-2 ▪┄┄▪ client12:eth2
12:52:45 INFO Created link: ixp1:e1-3 ▪┄┄▪ transit1:eth3
12:52:45 INFO Created link: leaf13:e1-2 ▪┄┄▪ client12:eth3
12:52:45 INFO Created link: leaf21:e1-1 ▪┄┄▪ client21:eth1
12:52:46 INFO Created link: vRR:e1-3 ▪┄┄▪ radius:eth1
12:52:46 INFO Created link: pe1:eth6 ▪┄┄▪ client01:eth1
12:52:47 INFO Created link: leaf11:e1-1 ▪┄┄▪ client11:eth1
12:52:47 INFO Created link: leaf13:e1-3 ▪┄┄▪ client13:eth1
12:52:48 INFO Created link: agg1:e1-3 ▪┄┄▪ sub3:eth1
12:52:48 INFO Created link: pe4:eth6 ▪┄┄▪ client04:eth1
12:52:48 INFO Created link: vRR:e1-4 ▪┄┄▪ dns:eth1
12:52:48 INFO Created link: agg1:e1-2 ▪┄┄▪ sub2:eth1
12:52:48 INFO Created link: agg1:e1-1 ▪┄┄▪ sub1:eth1
12:52:48 INFO Created link: pe3:eth6 ▪┄┄▪ client03:eth1
12:55:03 INFO Executed command node=spine11 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=peering2 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=leaf12 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=vRR command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=spine12 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=client02 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=client02 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=transit1 command="bash -c envsubst < /gobgp/gobgp.tmpl.yml | tee /gobgp/gobgp.yml"
  stdout=
  │ # Copyright 2023 Nokia
  │ # Licensed under the BSD 3-Clause License.
  │ # SPDX-License-Identifier: BSD-3-Clause
  │
  │ global:
  │   config:
  │     as: 64599
  │     router-id: 10.46.15.51
  │   apply-policy:
  │     config:
  │       export-policy-list:
  │         - next-hop-self
  │       default-export-policy: accept-route
  │ neighbors:
  │   - config:
  │       neighbor-address: 10.64.54.1
  │       peer-as: 65000
  │     afi-safis:
  │       - config:
  │           afi-safi-name: ipv4-unicast
  │   - config:
  │       neighbor-address: fd00:fde8:0:54::1
  │       peer-as: 65000
  │     afi-safis:
  │       - config:
  │           afi-safi-name: ipv6-unicast
  │   - config:
  │         neighbor-address: fd00:fc00:0:51::1
  │         peer-as: 65000
  │     afi-safis:
  │       - config:
  │           afi-safi-name: ipv6-unicast
  │   - config:
  │       neighbor-address: 10.64.54.3
  │       peer-as: 64699
  │     afi-safis:
  │       - config:
  │           afi-safi-name: ipv4-unicast
  │   - config:
  │       neighbor-address: fd00:fde8:0:54::3
  │       peer-as: 64699
  │     afi-safis:
  │       - config:
  │           afi-safi-name: ipv6-unicast
  │
  │ policy-definitions:
  │   - name: "next-hop-self"
  │     statements:
  │       - name: "nhs"
  │         actions:
  │           bgp-actions:
  │             set-next-hop: "self"
  │           route-disposition: "accept-route"
12:55:03 INFO Executed command node=transit1 command="bash /client.sh"
  stdout=
  │ failed to open file: open /tmp/latest-bview: no such file or directory
  │ failed to open file: open /tmp/latest-bview: no such file or directory

12:55:03 INFO Executed command node=client12 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=client12 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=sub3 command="ip link set dev eth1 address 00:d0:f6:03:03:03" stdout=""
12:55:03 INFO Executed command node=sub3 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=sub3 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=sub2 command="ip link set dev eth1 address 00:d0:f6:02:02:02" stdout=""
12:55:03 INFO Executed command node=sub2 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=sub2 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=ixp1 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=agg1 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=leaf21 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=netbox-housekeeping command="chown -R unit:root /opt/netbox/netbox/media/" stdout=""
12:55:03 INFO Executed command node=netbox-housekeeping command="chown -R unit:root /opt/netbox/netbox/reports/" stdout=""
12:55:03 INFO Executed command node=netbox-housekeeping command="chown -R unit:root /opt/netbox/netbox/scripts/" stdout=""
12:55:03 INFO Executed command node=client21 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=client21 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=client11 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=client11 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=leaf13 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=client01 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=client01 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=netbox-worker command="chown -R unit:root /opt/netbox/netbox/media/" stdout=""
12:55:03 INFO Executed command node=netbox-worker command="chown -R unit:root /opt/netbox/netbox/reports/" stdout=""
12:55:03 INFO Executed command node=netbox-worker command="chown -R unit:root /opt/netbox/netbox/scripts/" stdout=""
12:55:03 INFO Executed command node=sub1 command="ip link set dev eth1 address 00:d0:f6:01:01:01" stdout=""
12:55:03 INFO Executed command node=sub1 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=sub1 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=leaf11 command="bash -c sr_cli /tools system configuration generate-checkpoint name final-config"
  stdout=
  │ /system:
  │     Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'final-config' and comment ''
  │

12:55:03 INFO Executed command node=radius command="bash -c envsubst < /etc/network/interfaces.tmpl | tee /etc/network/interfaces"
  stdout=
  │ auto eth1
  │ iface eth1
  │     address 10.64.13.0/31
  │     address fd00:fde8:0:1:15:13:14:1/127
  │     up ip r a 10.0.0.0/8 via 10.64.13.1 dev eth1
  │     up ip -6 r a fd00:fde8::/32 via fd00:fde8:0:1:15:13:14:0 dev eth1

12:55:03 INFO Executed command node=radius command="bash -c envsubst < /etc/raddb/clients.tmpl.conf | tee /etc/raddb/clients.conf"
  stdout=
  │ client pe4 {
  │     ipaddr = 10.46.15.24
  │     secret = pe4-secret
  │ }

12:55:03 INFO Executed command node=radius command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=radius command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=client13 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=client13 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=dns command="bash -c envsubst < /etc/dnsmasq.tmpl.conf | tee /etc/dnsmasq.d/dns.conf"
  stdout=
  │ # CLAB Names
  │ host-record=clab-srexperts-p1,10.46.15.11,fd00:fde8::15:11
  │ host-record=clab-srexperts-p2,10.46.15.12,fd00:fde8::15:12
  │ host-record=clab-srexperts-vRR,10.46.15.13,fd00:fde8::15:13
  │ host-record=clab-srexperts-pe1,10.46.15.21,fd00:fde8::15:21
  │ host-record=clab-srexperts-pe2,10.46.15.22,fd00:fde8::15:22
  │ host-record=clab-srexperts-pe3,10.46.15.23,fd00:fde8::15:23
  │ host-record=clab-srexperts-pe4,10.46.15.24,fd00:fde8::15:24
  │ host-record=clab-srexperts-spine11,10.46.15.31,fd00:fde8::15:31
  │ host-record=clab-srexperts-spine12,10.46.15.32,fd00:fde8::15:32
  │ host-record=clab-srexperts-leaf11,10.46.15.33,fd00:fde8::15:33
  │ host-record=clab-srexperts-leaf12,10.46.15.34,fd00:fde8::15:34
  │ host-record=clab-srexperts-leaf13,10.46.15.35,fd00:fde8::15:35
  │ host-record=clab-srexperts-leaf21,10.46.15.41,fd00:fde8::15:41
  │ host-record=clab-srexperts-peering2,10.46.15.53,fd00:fde8::15:53
  │ # Short names clients
  │ host-record=client01.grt,10.64.21.11,fd00:fde8:0:21::11
  │ host-record=client02.grt,10.64.22.11,fd00:fde8:0:22::11
  │ host-record=client03.grt,10.64.23.11,fd00:fde8:0:23::11
  │ host-record=client04.grt,10.64.24.11,fd00:fde8:0:24::11
  │ host-record=client11.grt,10.64.30.11,fd00:fde8:0:30::11
  │ host-record=client12.grt,10.64.30.12,fd00:fde8:0:30::12
  │ host-record=client13.grt,10.64.30.13,fd00:fde8:0:30::13
  │ host-record=client21.grt,10.64.41.21,fd00:fde8:0:41::21
  │ host-record=client01.vprn.dci,192.168.21.11,fd00:ffdd:0:21::11
  │ host-record=client02.vprn.dci,192.168.22.11,fd00:ffdd:0:22::11
  │ host-record=client03.vprn.dci,192.168.23.11,fd00:ffdd:0:23::11
  │ host-record=client04.vprn.dci,192.168.24.11,fd00:ffdd:0:24::11
  │ host-record=client11.vprn.dci,192.168.30.11,fd00:ffdd:0:30::11
  │ host-record=client12.vprn.dci,192.168.30.12,fd00:ffdd:0:30::12
  │ host-record=client13.vprn.dci,192.168.30.13,fd00:ffdd:0:30::13
  │ host-record=client21.vprn.dci,192.168.41.21,fd00:ffdd:0:41::21
  │ host-record=client11.edavpls.dci,10.30.0.11,fd00:fdfd:0:3000::11
  │ host-record=client12.edavpls.dci,10.30.0.12,fd00:fdfd:0:3000::12
  │ host-record=client13.edavpls.dci,10.30.0.13,fd00:fdfd:0:3000::13
  │ host-record=client11.edavprn.dci,10.30.1.11,fd00:fdfd:0:3001::11
  │ host-record=client12.edavprn.dci,10.30.2.12,fd00:fdfd:0:3002::12
  │ host-record=client13.edavprn.dci,10.30.3.13,fd00:fdfd:0:3003::13
  │ # Short names point-to-points
  │ #p1
  │ host-record=1.p2.interface.p1.router,10.64.11.22,fd00:fde8:0:1:15:11:12:0
  │ host-record=2.p2.interface.p1.router,10.64.12.23,fd00:fde8:0:1:15:12:11:1
  │ host-record=pe1.interface.p1.router,10.64.11.0,fd00:fde8:0:1:15:11:21:0
  │ host-record=pe2.interface.p1.router,10.64.11.2,fd00:fde8:0:1:15:11:22:0
  │ host-record=pe3.interface.p1.router,10.64.11.4,fd00:fde8:0:1:15:11:23:0
  │ host-record=pe4.interface.p1.router,10.64.11.6,fd00:fde8:0:1:15:11:24:0
  │ host-record=vRR.interface.p1.router,10.64.11.8,fd00:fde8:0:1:15:11:13:0
  │ #p2
  │ host-record=1.p1.interface.p2.router,10.64.11.23,fd00:fde8:0:1:15:11:12:1
  │ host-record=2.p1.interface.p2.router,10.64.12.22,fd00:fde8:0:1:15:12:11:0
  │ host-record=pe1.interface.p2.router,10.64.12.0,fd00:fde8:0:1:15:12:21:0
  │ host-record=pe2.interface.p2.router,10.64.12.2,fd00:fde8:0:1:15:12:22:0
  │ host-record=pe3.interface.p2.router,10.64.12.4,fd00:fde8:0:1:15:12:23:0
  │ host-record=pe4.interface.p2.router,10.64.12.6,fd00:fde8:0:1:15:12:24:0
  │ host-record=vRR.interface.p2.router,10.64.12.8,fd00:fde8:0:1:15:12:13:0
  │ #pe1
  │ host-record=p1.interface.pe1.router,10.64.11.1,fd00:fde8:0:1:15:11:21:1
  │ host-record=p2.interface.pe1.router,10.64.12.1,fd00:fde8:0:1:15:12:21:1
  │ host-record=client01.interface.pe1.router,10.64.21.1,fd00:fde8:0:21::1
  │ host-record=client01.interface.pe1.vprn.dci,192.168.21.1,fd00:ffdd:0:21::1
  │ host-record=ixp1.interface.pe1.router,10.64.51.1,fd00:fc00:0:51::1
  │ host-record=ixp1.interface.peering2.router,10.64.51.2,fd00:fc00:0:51::2
  │ host-record=ixp1.interface.tramsit1.router,10.64.51.3,fd00:fc00:0:51::3
  │ host-record=pe1.interface.transit1.router,10.64.54.0,fd00:fde8:0:54::0
  │ host-record=transit1.interface.pe1.router,10.64.54.1,fd00:fde8:0:54::1
  │ host-record=peering2.interface.transit1.router,10.64.54.2,fd00:fde8:0:54::2
  │ host-record=transit1.interface.peering2.router,10.64.54.3,fd00:fde8:0:54::3
  │ #pe2
  │ host-record=p1.interface.pe2.router,10.64.11.3,fd00:fde8:0:1:15:11:22:1
  │ host-record=p2.interface.pe2.router,10.64.12.3,fd00:fde8:0:1:15:12:22:1
  │ host-record=client02.interface.pe2.router,10.64.22.1,fd00:fde8:0:22::1
  │ host-record=client02.interface.pe2.vprn.dci,192.168.22.1,fd00:ffdd:0:22::1
  │ host-record=spine11.interface.pe2.router,fd00:fde8:0:1:15:22:31:0
  │ host-record=spine12.interface.pe2.router,fd00:fde8:0:1:15:22:32:0
  │ #pe3
  │ host-record=p1.interface.pe3.router,10.64.11.5,fd00:fde8:0:1:15:11:23:1
  │ host-record=p2.interface.pe3.router,10.64.12.5,fd00:fde8:0:1:15:12:23:1
  │ host-record=client03.interface.pe3.router,10.64.23.1,fd00:fde8:0:23::1
  │ host-record=client03.interface.pe3.vprn.dci,192.168.23.1,fd00:ffdd:0:23::1
  │ host-record=spine11.interface.pe3.router,fd00:fde8:0:1:15:23:31:0
  │ host-record=spine12.interface.pe3.router,fd00:fde8:0:1:15:23:32:0
  │ #pe4
  │ host-record=p1.interface.pe4.router,10.64.11.7,fd00:fde8:0:1:15:11:24:1
  │ host-record=p2.interface.pe4.router,10.64.12.7,fd00:fde8:0:1:15:12:24:1
  │ host-record=client04.interface.pe4.router,10.64.24.1,fd00:fde8:0:24::1
  │ host-record=client04.interface.pe4.vprn.dci,192.168.24.1,fd00:ffdd:0:24::1
  │ # Special addresses
  │ host-record=anycast-gw.irb0.1.leafs.dc1,10.64.30.1,fd00:fde8:0:30::1
  │ host-record=anycast-gw.irb0.101.vprn.dci.leafs.dc1,192.168.30.1,fd00:ffdd:0:30::1
  │ host-record=anycast-gw.irb0.1.leaf21.dc2,10.64.41.1,fd00:fde8:0:41::1
  │ host-record=anycast-gw.irb0.102.vprn.dci.leaf21.dc2,192.168.41.1,fd00:ffdd:0:41::1
  │ #
  │ address=/web1.srexperts.topology/10.64.21.11
  │ address=/web2.srexperts.topology/10.64.22.11
  │ address=/web3.srexperts.topology/10.64.23.11
  │ # [/]
  │ # A:admin@pe1# ping clab-srexperts-pe1
  │ # PING 10.64.21.1 56 data bytes
  │ # 64 bytes from 10.64.21.1: icmp_seq=1 ttl=64 time=0.120ms.

12:55:03 ERRO Failed to execute command command="bash /client.sh" node=dns rc=5 stdout=""
  stderr=
  │ ifup: could not acquire exclusive lock for eth1.1: Resource temporarily unavailable
  │ chpasswd: password for 'user' changed
  │
  │ dnsmasq: failed to create inotify: No file descriptors available

12:55:03 INFO Executed command node=client04 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=client04 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:03 INFO Executed command node=client03 command="bash /client.sh" stdout=""
12:55:03 INFO Executed command node=client03 command="bash -c echo 'nameserver 10.128.15.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.15.15

12:55:04 INFO Adding host entries path=/etc/hosts
12:55:04 INFO Adding SSH config for nodes path=/etc/ssh/ssh_config.d/clab-srexperts.conf
🎉 A newer containerlab version (0.68.0) is available!
Release notes: https://containerlab.dev/rn/0.68/
Run 'sudo clab version upgrade' or see https://containerlab.dev/install/ for installation options.
╭────────────────────────────────────┬─────────────────────────────────────────────┬─────────┬────────────────╮
│                Name                │                  Kind/Image                 │  State  │ IPv4/6 Address │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-agg1                │ nokia_srlinux                               │ running │ 10.128.15.52   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-client01            │ linux                                       │ running │ 10.128.15.25   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-client02            │ linux                                       │ running │ 10.128.15.26   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-client03            │ linux                                       │ running │ 10.128.15.27   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-client04            │ linux                                       │ running │ 10.128.15.28   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-client11            │ linux                                       │ running │ 10.128.15.36   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-client12            │ linux                                       │ running │ 10.128.15.37   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-client13            │ linux                                       │ running │ 10.128.15.38   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-client21            │ linux                                       │ running │ 10.128.15.42   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-codeserver          │ linux                                       │ running │ 10.128.15.90   │
│                                    │ ghcr.io/coder/code-server:latest            │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-dns                 │ linux                                       │ running │ 10.128.15.15   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-gnmic               │ linux                                       │ running │ 10.128.15.71   │
│                                    │ ghcr.io/openconfig/gnmic:0.38.2             │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-grafana             │ linux                                       │ running │ 10.128.15.73   │
│                                    │ grafana/grafana:10.3.5                      │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-ixp1                │ nokia_srlinux                               │ running │ 10.128.15.51   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-leaf11              │ nokia_srlinux                               │ running │ 10.128.15.33   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-leaf12              │ nokia_srlinux                               │ running │ 10.128.15.34   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-leaf13              │ nokia_srlinux                               │ running │ 10.128.15.35   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-leaf21              │ nokia_srlinux                               │ running │ 10.128.15.41   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-loki                │ linux                                       │ running │ 10.128.15.76   │
│                                    │ grafana/loki:2.9.7                          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-netbox              │ linux                                       │ running │ 10.128.15.81   │
│                                    │ docker.io/netboxcommunity/netbox:v4.2-3.2.0 │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-netbox-housekeeping │ linux                                       │ running │ 10.128.15.83   │
│                                    │ docker.io/netboxcommunity/netbox:v4.2-3.2.0 │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-netbox-worker       │ linux                                       │ running │ 10.128.15.82   │
│                                    │ docker.io/netboxcommunity/netbox:v4.2-3.2.0 │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-p1                  │ nokia_sros                                  │ running │ 10.128.15.11   │
│                                    │ vr-sros:25.3.R1                             │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-p2                  │ nokia_sros                                  │ running │ 10.128.15.12   │
│                                    │ vr-sros:25.3.R1                             │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-pe1                 │ nokia_sros                                  │ running │ 10.128.15.21   │
│                                    │ vr-sros:25.3.R1                             │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-pe2                 │ nokia_sros                                  │ running │ 10.128.15.22   │
│                                    │ vr-sros:25.3.R1                             │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-pe3                 │ nokia_sros                                  │ running │ 10.128.15.23   │
│                                    │ vr-sros:25.3.R1                             │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-pe4                 │ nokia_sros                                  │ running │ 10.128.15.24   │
│                                    │ vr-sros:25.3.R1                             │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-peering2            │ nokia_srlinux                               │ running │ 10.128.15.53   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-postgres            │ linux                                       │ running │ 10.128.15.84   │
│                                    │ docker.io/postgres:17-alpine                │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-prometheus          │ linux                                       │ running │ 10.128.15.72   │
│                                    │ prom/prometheus:v2.51.2                     │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-promtail            │ linux                                       │ running │ 10.128.15.75   │
│                                    │ grafana/promtail:2.9.7                      │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-radius              │ linux                                       │ running │ 10.128.15.14   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-redis               │ linux                                       │ running │ 10.128.15.85   │
│                                    │ docker.io/valkey/valkey:8.0-alpine          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-redis-cache         │ linux                                       │ running │ 10.128.15.86   │
│                                    │ docker.io/valkey/valkey:8.0-alpine          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-rpki                │ linux                                       │ running │ 10.128.15.55   │
│                                    │ rpki/stayrtr                                │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-spine11             │ nokia_srlinux                               │ running │ 10.128.15.31   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-spine12             │ nokia_srlinux                               │ running │ 10.128.15.32   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-sub1                │ linux                                       │ running │ 10.128.15.61   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-sub2                │ linux                                       │ running │ 10.128.15.62   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-sub3                │ linux                                       │ running │ 10.128.15.63   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-syslog              │ linux                                       │ running │ 10.128.15.74   │
│                                    │ linuxserver/syslog-ng:4.5.0                 │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-transit1            │ linux                                       │ running │ 10.128.15.54   │
│                                    │ ghcr.io/srl-labs/network-multitool          │         │ N/A            │
├────────────────────────────────────┼─────────────────────────────────────────────┼─────────┼────────────────┤
│ clab-srexperts-vRR                 │ nokia_srlinux                               │ running │ 10.128.15.13   │
│                                    │ ghcr.io/nokia/srlinux:24.10.4               │         │ N/A            │
╰────────────────────────────────────┴─────────────────────────────────────────────┴─────────┴────────────────╯
```

///

### Cloning this repository

If you would like to work locally on your personal device you should clone this repository. This can be done using one of the following commands.

HTTPS:

```bash
git clone https://github.com/nokia/SReXperts.git
```

SSH:

```bash
git clone git@github.com:nokia/SReXperts.git
```

GitHub CLI:

```bash
gh repo clone nokia/SReXperts
```

## Useful links

- [Network Developer Portal](https://network.developer.nokia.com/)

- [containerlab](https://containerlab.dev/)
- [gNMIc](https://gnmic.openconfig.net/)

### SR Linux

- [Learn SR Linux](https://learn.srlinux.dev/)
- [YANG Browser](https://yang.srlinux.dev/)
- [gNxI Browser](https://gnxi.srlinux.dev/)

### SR OS

- [SR OS Release 25.3](https://documentation.nokia.com/sr/25-3/index.html)
- [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)
- [Network Developer Portal](https://network.developer.nokia.com/sr/learn/)

### Misc Tools/Software

#### Windows

- [WSL environment](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701)
- [MobaXterm](https://mobaxterm.mobatek.net/download.html)
- [PuTTY Installer](https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.78-installer.msi)
- [PuTTY Binary](https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe)

#### MacOS

- [Ghostty](https://ghostty.org/)
- [iTerm2](https://iterm2.com/downloads/stable/iTerm2-3_4_19.zip)
- [Warp](https://app.warp.dev/get_warp)
- [Hyper](https://hyper.is/)
- [Terminal](https://support.apple.com/en-gb/guide/terminal/apd5265185d-f365-44cb-8b09-71a064a42125/mac)

#### Linux

- [Ghostty](https://ghostty.org/)
- [Gnome Console](https://apps.gnome.org/en/app/org.gnome.Console/)
- [Gnome Terminal](https://help.gnome.org/users/gnome-terminal/stable/)

#### IDEs

- [VS Code](https://code.visualstudio.com/Download)
- [VS Code Web](https://vscode.dev/)
- [Sublime Text](https://www.sublimetext.com/download)
- [IntelliJ IDEA](https://www.jetbrains.com/idea/download/)
- [Eclipse](https://www.eclipse.org/downloads/)
- [PyCharm](https://www.jetbrains.com/pycharm/download)

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>

## Thanks and contributions

As you can imagine, creating the activities that make up this hackathon is a lot of work.  The hackathon team would like to thanks the following team members (in alphabetical order) for their contributions: Asad Arafat, Diogo Pinheiro, Guilherme Cale, Hans Thienpondt, James Cumming, Joao Machado, Kaelem Chandra, Laleh Kiani, Louis Van Eeckhoudt, Maged Makramalla, Miguel Redondo Ferrero, Roman Dodin, Saju Salahudeen, Samier Barguil, Shafkat Waheed, Shashi Sharma, Simon Tibbitts, Siva Sivakumar, Subba Konda, Sven Wisotzky, Thomas Hendriks, Tiago Amado. Zeno Dhaene, Tim Raphael and Vasileios Tekidis