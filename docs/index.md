---
hide:
  - navigation
---

# Welcome to the Hackathon event at SReXperts 2026

Welcome to the 2026 Hackathon event at SReXperts.

We are very glad to welcome you to our annual event, currently the 6th edition of the Hackathon.

Nokia prides itself on the excellent technical products, solutions that we deliver to the market, and this event is no exception.  A large team of engineers,
developers and product managers have been working hard to deliver what, we'll hope you agree, is a challenging and informative set of activities to challenge
you, no matter what your experience level is.

## Open to all and something for everyone

Whether you're a relative novice to Nokia's products, or a seasoned expert, there is something in this event for you!  All you will need is your trusty laptop,
an afternoon of focus and possibly some coffee (supplied!) and you should find something to benefit both you and your organizations.

## Getting started

This page is your starting point into the event, it should get you familiar with the lab environment provided by Nokia, and provide an overview of the suggested sample activities.

**Please read this page all the way through before attempting any of the activities.**

During the afternoon you will work in groups (or alone if you prefer) on any projects that you are inspired to tackle or on one of the pre-provided activities of varying difficulty.

As long as you have a laptop with the ability to SSH and a web browser, we have example activities and a generic lab topology to help you progress if you don’t have something specific already in mind.

Need help, not a problem, pop your hand in the air and an eager expert will be there to guide you.

## Lab Environment

For this event each (group of) participant(s) will receive their own dedicated cloud instance (VM) running a copy of the generic lab topology.  You will see this called "your VM",
"your group's hackathon VM", "your group's event VM", "your instance", "your server" and other similar phrases in the activities.  They all mean the same thing, your own dedicated cloud instance.

If everything went according to plan, you should have received a physical piece of paper which contains:

- a group ID allocated to your group (or to yourself if you're working alone).
- SSH credentials to a public cloud instance dedicated to your group.
- HTTPS URL's for this repository and access to a web based IDE in case you don't have one installed on your operating system.

/// warning
The public cloud compute instances will be destroyed once the event is concluded.</p>
Please make sure to backup any code, config, etc. <u>offline</u> (e.g. onto your laptop) if you'd like to keep it after the hackathon.
///

### Group ID

Please refer to the paper provided by the event session leader. If nothing has been provided, not a problem, pop your hand in the air and someone will allocate you one before you can say "Aequeosalinocalcalinoceraceoaluminosocupreovitriolic".

| Group ID | hostname instance |
| --- | --- |
| 1 | 1.srexperts.net |
| 2 | 2.srexperts.net |
| ... | ... |
| **X** | **X**.srexperts.net |

### SSH

The simplest way to get going is to use your SSH client to connect to your group's event VM instance and work from there.  All tools and applications are pre-installed and you will have direct access to your entire network.

SSH is also important if you want to directly access your network from your laptop but more on that later.

|     |     |
| --- | --- |
| hostname | `refer to the paper provided or the slide presented` |
| username | `refer to the paper provided or the slide presented` |
| password | `refer to the paper provided or the slide presented` |

/// tip
If you're familiar with SSH and wish to setup passwordless access, you can use `ssh-keygen -h` to generate a public/private key pair and then `ssh-copy-id` to copy it towards your group's event instance.
///

### WiFi

WiFi is important here.  Without it your event experience is going to be rather dull.  To connect to the hackathon event's WiFi, refer to the paper provided or the slide presented.

### Topology

When accessing your event VM instance you'll find that the [SReXperts GitHub repository](https://github.com/nokia/srexperts) that contains all of the documentation, examples, solutions and loads of other great stuff, has already been cloned for you.

In this event, every group has their own complete service-provider network at their disposal.  Your network comprises an IP backbone with Provider (P) and Provider Edge (PE) routers, a broadband dial-in network, a peering edge network, an internet exchange point, multiple data-centers and a number of client and subscriber devices.  This network is already deployed, provisioned and is ready to go!

*Don't worry: This is your personal group network, you cannot impact any other groups.*

-{{ diagram(path='./images/srx.clab.drawio', title='Topology', page=0) }}-

The above topology contains a number of functional blocks to help you in areas you might want to focus on, it contains:

- Routing:
    - SR-MPLS (Dual-Stack ISIS)
    - MP-BGP (SAFIs with IPv6 next-hop) ; single node (vRR) route-reflector
    - 2x P-nodes (SR OS)
    - 4x PE-nodes (SR OS)
    - 1x route-reflector (SR Linux)
- Data Centers:
    - DC1: a CLOS model - managed by EDA
        - 2x spines (spine11|spine12) and 3 leaf switches (leaf11|leaf12|leaf13)
    - DC2: a CLOS model - standalone
        - 2x spines (spine21|spine22) and 3 leaf switches (leaf21|leaf22|leaf23)
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

#### From your group's event instance VM

To access the lab nodes from within the VM, users should identify the names of the deployed nodes using the `sudo containerlab inspect -a` command.  You will notice they all start with `clab-srexperts-`.  Your entire network is [powered by ContainerLab](https://containerlab.dev).

If you'd like to see the full list of devices, their hostnames and IP addresses in your network use the following command.

/// tab | cmd

``` bash
sudo containerlab inspect -a
```

///
/// tab | output

``` bash
╭─────────────────────────────┬───────────┬───────────────────────────┬─────────────────────────────────────────┬────────────┬────────────────╮
│           Topology          │  Lab Name │            Name           │                Kind/Image               │    State   │ IPv4/6 Address │
├─────────────────────────────┼───────────┼───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ SReXperts/clab/srx.clab.yml │ srexperts │ clab-srexperts-agg1       │ nokia_srlinux                           │ running    │ 10.128.4.52    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-bngblaster │ linux                                   │ running    │ 10.128.4.61    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client01   │ linux                                   │ running    │ 10.128.4.25    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client02   │ linux                                   │ running    │ 10.128.4.26    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client03   │ linux                                   │ running    │ 10.128.4.27    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client04   │ linux                                   │ running    │ 10.128.4.28    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client11   │ linux                                   │ running    │ 10.128.4.36    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client12   │ linux                                   │ running    │ 10.128.4.37    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client13   │ linux                                   │ running    │ 10.128.4.38    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client21   │ linux                                   │ running    │ 10.128.4.46    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client22   │ linux                                   │ running    │ 10.128.4.47    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-client23   │ linux                                   │ running    │ 10.128.4.48    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-dns        │ linux                                   │ running    │ 10.128.4.15    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-gnmic      │ linux                                   │ running    │ 10.128.4.71    │
│                             │           │                           │ ghcr.io/openconfig/gnmic:0.43.0         │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-grafana    │ linux                                   │ running    │ 10.128.4.73    │
│                             │           │                           │ grafana/grafana:12.3.3                  │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-ixp1       │ nokia_srlinux                           │ running    │ 10.128.4.51    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-leaf11     │ nokia_srlinux                           │ running    │ 10.128.4.33    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-leaf12     │ nokia_srlinux                           │ running    │ 10.128.4.34    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-leaf13     │ nokia_srlinux                           │ running    │ 10.128.4.35    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-leaf21     │ nokia_srlinux                           │ running    │ 10.128.4.43    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-leaf22     │ nokia_srlinux                           │ running    │ 10.128.4.44    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-leaf23     │ nokia_srlinux                           │ running    │ 10.128.4.45    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-loki       │ linux                                   │ running    │ 10.128.4.76    │
│                             │           │                           │ grafana/loki:3.5.10                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-p1-1       │ nokia_srsim                             │ running    │ 10.128.4.11    │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-p1-a       │ nokia_srsim                             │ running    │ N/A            │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-p2-1       │ nokia_srsim                             │ running    │ 10.128.4.12    │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-p2-a       │ nokia_srsim                             │ running    │ N/A            │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe1-1      │ nokia_srsim                             │ running    │ 10.128.4.21    │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe1-a      │ nokia_srsim                             │ running    │ N/A            │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe2-1      │ nokia_srsim                             │ running    │ 10.128.4.22    │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe2-a      │ nokia_srsim                             │ running    │ N/A            │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe3-1      │ nokia_srsim                             │ running    │ 10.128.4.23    │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe3-a      │ nokia_srsim                             │ running    │ N/A            │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe4-1      │ nokia_srsim                             │ running    │ 10.128.4.24    │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe4-2      │ nokia_srsim                             │ running    │ N/A            │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe4-a      │ nokia_srsim                             │ running    │ N/A            │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-pe4-b      │ nokia_srsim                             │ running    │ N/A            │
│                             │           │                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-peering2   │ nokia_srlinux                           │ running    │ 10.128.4.53    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-prometheus │ linux                                   │ running    │ 10.128.4.72    │
│                             │           │                           │ quay.io/prometheus/prometheus:v2.54.1   │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-promtail   │ linux                                   │ running    │ 10.128.4.75    │
│                             │           │                           │ grafana/promtail:3.5.10                 │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-radius     │ linux                                   │ running    │ 10.128.4.14    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-rpki       │ linux                                   │ running    │ 10.128.4.55    │
│                             │           │                           │ rpki/stayrtr                            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-spine11    │ nokia_srlinux                           │ running    │ 10.128.4.31    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-spine12    │ nokia_srlinux                           │ running    │ 10.128.4.32    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-spine21    │ nokia_srlinux                           │ running    │ 10.128.4.41    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-spine22    │ nokia_srlinux                           │ running    │ 10.128.4.42    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-syslog     │ linux                                   │ running    │ 10.128.4.74    │
│                             │           │                           │ quay.io/linuxserver.io/syslog-ng:4.10.2 │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-telegraf   │ linux                                   │ restarting │ N/A            │
│                             │           │                           │ telegraf:latest                         │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-transit1   │ linux                                   │ running    │ 10.128.4.54    │
│                             │           │                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
│                             │           ├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│                             │           │ clab-srexperts-vRR        │ nokia_srlinux                           │ running    │ 10.128.4.13    │
│                             │           │                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
╰─────────────────────────────┴───────────┴───────────────────────────┴─────────────────────────────────────────┴────────────┴────────────────╯
```

///

Using the names from the above output, we can login to a node using the following command:

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
-------------------------  ---------------------------------------------------------------------------------------------------------------------------------------------------------
eda-demo-control-plane     {'32760': '9506', '32761': '9505', '32762': '9504', '32763': '9503', '32764': '9502', '32765': '9501', '32766': '51206', '32767': '9443', '6443': '6443'}
edgeshark                  {'5001': '5001'}
clab-srexperts-client04    {'22': '50028'}
clab-srexperts-client21    {'22': '50046'}
clab-srexperts-client11    {'22': '50036'}
clab-srexperts-client01    {'22': '50025'}
clab-srexperts-bngblaster  {'22': '50061'}
clab-srexperts-radius      {'22': '50014'}
clab-srexperts-client02    {'22': '50026'}
clab-srexperts-client12    {'22': '50037'}
clab-srexperts-client23    {'22': '50048'}
clab-srexperts-transit1    {'22': '50054'}
clab-srexperts-client03    {'22': '50027'}
clab-srexperts-client22    {'22': '50047'}
clab-srexperts-client13    {'22': '50038'}
clab-srexperts-dns         {'22': '50015'}
clab-srexperts-prometheus  {'9090': '9090'}
clab-srexperts-grafana     {'3000': '3000'}
clab-srexperts-agg1        {'22': '50052', '57400': '50352'}
clab-srexperts-leaf22      {'22': '50044', '57400': '50344'}
clab-srexperts-spine21     {'22': '50041', '57400': '50341'}
clab-srexperts-vRR         {'22': '50013', '57400': '50313', '830': '50413'}
clab-srexperts-pe4         {'22': '50024', '57400': '50324', '830': '50424'}
clab-srexperts-pe2         {'22': '50022', '57400': '50322', '830': '50422'}
clab-srexperts-p1          {'22': '50011', '57400': '50311', '830': '50411'}
clab-srexperts-pe1         {'22': '50021', '57400': '50321', '830': '50421'}
clab-srexperts-pe3         {'22': '50023', '57400': '50323', '830': '50423'}
clab-srexperts-p2          {'22': '50012', '57400': '50312', '830': '50412'}
clab-srexperts-peering2    {'22': '50053', '57400': '50353'}
clab-srexperts-leaf21      {'22': '50043', '57400': '50343'}
clab-srexperts-leaf13      {'22': '50035', '57400': '50335'}
clab-srexperts-spine22     {'22': '50042', '57400': '50342'}
clab-srexperts-ixp1        {'22': '50051', '57400': '50351'}
clab-srexperts-leaf12      {'22': '50034', '57400': '50334'}
clab-srexperts-spine11     {'22': '50031', '57400': '50331'}
clab-srexperts-leaf11      {'22': '50033', '57400': '50333'}
clab-srexperts-spine12     {'22': '50032', '57400': '50332'}
clab-srexperts-leaf23      {'22': '50045', '57400': '50345'}
```

///

Each service exposed on a lab node gets a unique external port number as per the table above. For example, Grafana's web interface is available on port `3000` of the VM which is mapped to the Grafana node's internal port of `3000`.

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
ssh admin@clab-srexperts-client11

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

No worries, we have got you covered! Each instance is running a [**web-based VS Code code-server**](./tools/tools-code-server.md) that, when accessing it at `https://<my group id>.srexperts.net`, should prompt you for a password (which is documented on the physical paper provided), and you should be able to access the topology through the terminal there. Detailed instructions on how to use the code-server are available in the [VS Code server documentation](./tools/tools-code-server.md).

Should code-server prove ineffective for your situation reach out to the staff on-site and we will try to figure out a suitable alternative for you.

### Help! I've bricked my lab, how do I redeploy?

First we destroy the lab:
/// tab | cmd

``` bash
sudo -E clab destroy -t $HOME/SReXperts/clab/srx.clab.yml --cleanup
```

///

/// tab | output

``` bash
14:13:50 INFO Parsing & checking topology file=srx.clab.yml
14:13:51 INFO Parsing & checking topology file=srx.clab.yml
14:13:51 INFO Destroying lab name=srexperts
14:13:51 INFO Removed container name=clab-srexperts-telegraf
14:13:52 INFO Removed container name=clab-srexperts-gnmic
14:13:53 INFO Removed container name=clab-srexperts-promtail
14:13:53 INFO Removed container name=clab-srexperts-loki
14:13:53 INFO Removed container name=clab-srexperts-rpki
14:13:53 INFO Removed container name=clab-srexperts-spine11
14:13:53 INFO Removed container name=clab-srexperts-prometheus
14:13:54 INFO Removed container name=clab-srexperts-syslog
14:13:54 INFO Removed container name=clab-srexperts-p1-1
14:13:54 INFO Removed container name=clab-srexperts-p1-a
14:13:54 INFO Removed container name=clab-srexperts-grafana
14:13:54 INFO Removed container name=clab-srexperts-spine21
14:13:54 INFO Removed container name=clab-srexperts-vRR
14:13:54 INFO Removed container name=clab-srexperts-peering2
14:13:54 INFO Removed container name=clab-srexperts-ixp1
14:13:54 INFO Removed container name=clab-srexperts-pe2-1
14:13:54 INFO Removed container name=clab-srexperts-client02
14:13:54 INFO Removed container name=clab-srexperts-p2-1
14:13:54 INFO Removed container name=clab-srexperts-leaf21
14:13:54 INFO Removed container name=clab-srexperts-pe2-a
14:13:54 INFO Removed container name=clab-srexperts-leaf11
14:13:54 INFO Removed container name=clab-srexperts-leaf22
14:13:54 INFO Removed container name=clab-srexperts-spine12
14:13:54 INFO Removed container name=clab-srexperts-spine22
14:13:54 INFO Removed container name=clab-srexperts-pe1-1
14:13:54 INFO Removed container name=clab-srexperts-pe4-1
14:13:54 INFO Removed container name=clab-srexperts-pe4-2
14:13:55 INFO Removed container name=clab-srexperts-leaf12
14:13:55 INFO Removed container name=clab-srexperts-client21
14:13:55 INFO Removed container name=clab-srexperts-radius
14:13:55 INFO Removed container name=clab-srexperts-pe1-a
14:13:55 INFO Removed container name=clab-srexperts-pe4-b
14:13:55 INFO Removed container name=clab-srexperts-p2-a
14:13:55 INFO Removed container name=clab-srexperts-pe3-1
14:13:55 INFO Removed container name=clab-srexperts-leaf23
14:13:55 INFO Removed container name=clab-srexperts-leaf13
14:13:55 INFO Removed container name=clab-srexperts-client23
14:13:55 INFO Removed container name=clab-srexperts-client03
14:13:55 INFO Removed container name=clab-srexperts-agg1
14:13:55 INFO Removed container name=clab-srexperts-pe4-a
14:13:55 INFO Removed container name=clab-srexperts-pe3-a
14:13:55 INFO Removed container name=clab-srexperts-dns
14:13:55 INFO Removed container name=clab-srexperts-client01
14:13:55 INFO Removed container name=clab-srexperts-client11
14:13:56 INFO Removed container name=clab-srexperts-transit1
14:13:56 INFO Removed container name=clab-srexperts-client04
14:13:56 INFO Removed container name=clab-srexperts-client13
14:13:56 INFO Removed container name=clab-srexperts-client12
14:13:56 INFO Removed container name=clab-srexperts-bngblaster
14:13:56 INFO Removed container name=clab-srexperts-client22
14:13:56 INFO Removing host entries path=/etc/hosts
14:13:56 INFO Removing SSH config path=/etc/ssh/ssh_config.d/clab-srexperts.conf
```

///
/// tab | alternate
This takes on average 20 min to redeploy, can't wait that long? Pop your hand up and ask for a new instance!

``` bash
sudo reboot
```

///

Secondly, we can deploy the lab again:
/// tab | cmd

``` bash
sudo -E clab deploy -t $HOME/SReXperts/clab/srx.clab.yml --reconfigure
```

///

/// tab | output

``` bash
14:14:18 INFO Containerlab started version=0.75.0
14:14:18 INFO Parsing & checking topology file=srx.clab.yml
14:14:18 INFO Removing directory path=/home/nokia/SReXperts/clab/clab-srexperts
14:14:18 INFO Creating docker network name=srexperts IPv4 subnet=10.128.4.0/24 IPv6 subnet="" MTU=0
14:14:18 INFO Creating lab directory path=/home/nokia/SReXperts/clab/clab-srexperts
14:14:18 INFO node "bngblaster" is being delayed for 120 seconds
14:14:18 INFO node "dns" is being delayed for 120 seconds
14:14:18 INFO node "promtail" is being delayed for 120 seconds
14:14:18 INFO node "client12" is being delayed for 120 seconds
14:14:18 INFO node "radius" is being delayed for 120 seconds
14:14:18 INFO node "telegraf" is being delayed for 120 seconds
14:14:18 INFO node "loki" is being delayed for 120 seconds
14:14:18 INFO node "gnmic" is being delayed for 120 seconds
14:14:18 INFO node "prometheus" is being delayed for 120 seconds
14:14:18 INFO node "client02" is being delayed for 120 seconds
14:14:18 INFO node "rpki" is being delayed for 120 seconds
14:14:18 INFO node "client21" is being delayed for 120 seconds
14:14:18 INFO node "client22" is being delayed for 120 seconds
14:14:18 INFO node "grafana" is being delayed for 120 seconds
14:14:18 INFO node "syslog" is being delayed for 120 seconds
14:14:18 INFO node "client04" is being delayed for 120 seconds
14:14:18 INFO node "transit1" is being delayed for 120 seconds
14:14:18 INFO node "client01" is being delayed for 120 seconds
14:14:18 INFO Creating container name=leaf13
14:14:18 INFO Creating container name=leaf12
14:14:18 INFO Creating container name=spine12
14:14:18 INFO Creating container name=spine22
14:14:18 INFO Creating container name=leaf22
14:14:18 INFO Creating container name=leaf23
14:14:18 INFO Creating container name=leaf21
14:14:18 INFO Creating container name=peering2
14:14:18 INFO Creating container name=vRR
14:14:18 INFO Creating container name=pe2-1
14:14:18 INFO Creating container name=pe1-1
14:14:18 INFO Creating container name=p2-1
14:14:18 INFO Creating container name=p1-1
14:14:18 INFO Creating container name=pe4-1
14:14:20 INFO Running postdeploy actions kind=nokia_srlinux node=leaf13
14:14:20 INFO Running postdeploy actions kind=nokia_srlinux node=leaf22
14:14:20 INFO Created link: spine22:e1-2 ▪┄┄▪ leaf22:e1-32
14:14:20 WARN Failed to write chassis_info.json to lab dir node=pe2-a path=/home/nokia/SReXperts/clab/clab-srexperts/pe2 error="/opt/nokia/chassis_info.json not found in image graph driver (UpperDir/MergedDir)"
14:14:20 INFO Retrieved SR OS version from image node=pe2-a version=26.3.1
14:14:20 WARN SR-SIM node has no type set for component in slot, skipping component SR OS config generation. node=pe2-a slot=1
14:14:20 INFO Adding configuration node=clab-srexperts-pe2-a type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe2.partial.cfg
14:14:20 INFO Creating container name=pe2-a
14:14:20 INFO Running postdeploy actions kind=nokia_srlinux node=vRR
14:14:20 INFO Running postdeploy actions kind=nokia_srlinux node=leaf12
14:14:21 INFO Created link: spine22:e1-3 ▪┄┄▪ leaf23:e1-32
14:14:21 INFO Running postdeploy actions kind=nokia_srlinux node=spine22
14:14:21 INFO Created link: spine22:e1-1 ▪┄┄▪ leaf21:e1-32
14:14:21 INFO Running postdeploy actions kind=nokia_srlinux node=leaf23
14:14:21 INFO Running postdeploy actions kind=nokia_srlinux node=peering2
14:14:21 WARN Failed to write chassis_info.json to lab dir node=p1-a path=/home/nokia/SReXperts/clab/clab-srexperts/p1 error="/opt/nokia/chassis_info.json not found in image graph driver (UpperDir/MergedDir)"
14:14:21 INFO Retrieved SR OS version from image node=p1-a version=26.3.1
14:14:21 WARN SR-SIM node has no type set for component in slot, skipping component SR OS config generation. node=p1-a slot=1
14:14:21 INFO Adding configuration node=clab-srexperts-p1-a type=partial source=/home/nokia/SReXperts/clab/configs/sros/p1.partial.cfg
14:14:21 INFO Creating container name=p1-a
14:14:21 INFO Running postdeploy actions kind=nokia_srlinux node=leaf21
14:14:21 INFO Creating container name=pe4-2
14:14:21 WARN Failed to write chassis_info.json to lab dir node=p2-a path=/home/nokia/SReXperts/clab/clab-srexperts/p2 error="/opt/nokia/chassis_info.json not found in image graph driver (UpperDir/MergedDir)"
14:14:21 INFO Retrieved SR OS version from image node=p2-a version=26.3.1
14:14:21 WARN SR-SIM node has no type set for component in slot, skipping component SR OS config generation. node=p2-a slot=1
14:14:21 INFO Adding configuration node=clab-srexperts-p2-a type=partial source=/home/nokia/SReXperts/clab/configs/sros/p2.partial.cfg
14:14:21 INFO Creating container name=p2-a
14:14:21 WARN Failed to write chassis_info.json to lab dir node=pe4-b path=/home/nokia/SReXperts/clab/clab-srexperts/pe4 error="/opt/nokia/chassis_info.json not found in image graph driver (UpperDir/MergedDir)"
14:14:21 INFO Retrieved SR OS version from image node=pe4-b version=26.3.1
14:14:21 INFO Adding configuration node=clab-srexperts-pe4-b type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe4.partial.cfg
14:14:21 INFO Creating container name=pe4-b
14:14:21 INFO Created link: pe2:e1-1-c4-1 (1/1/c4/1) ▪┄┄▪ spine12:e1-32
14:14:22 WARN Failed to write chassis_info.json to lab dir node=pe1-a path=/home/nokia/SReXperts/clab/clab-srexperts/pe1 error="/opt/nokia/chassis_info.json not found in image graph driver (UpperDir/MergedDir)"
14:14:22 INFO Retrieved SR OS version from image node=pe1-a version=26.3.1
14:14:22 WARN SR-SIM node has no type set for component in slot, skipping component SR OS config generation. node=pe1-a slot=1
14:14:22 INFO Adding configuration node=clab-srexperts-pe1-a type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe1.partial.cfg
14:14:22 INFO Creating container name=pe1-a
14:14:22 WARN Failed to write chassis_info.json to lab dir node=pe4-a path=/home/nokia/SReXperts/clab/clab-srexperts/pe4 error="/opt/nokia/chassis_info.json not found in image graph driver (UpperDir/MergedDir)"
14:14:22 INFO Created link: spine12:e1-2 ▪┄┄▪ leaf12:e1-32
14:14:22 INFO Retrieved SR OS version from image node=pe4-a version=26.3.1
14:14:22 INFO Adding configuration node=clab-srexperts-pe4-a type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe4.partial.cfg
14:14:22 INFO Creating container name=pe4-a
14:14:22 INFO Created link: spine12:e1-3 ▪┄┄▪ leaf13:e1-32
14:14:22 INFO Running postdeploy actions kind=nokia_srlinux node=spine12
14:14:22 INFO Running postdeploy actions kind=nokia_srsim node=pe2
14:14:22 INFO Created link: p1:e1-1-c4-1 (1/1/c4/1) ▪┄┄▪ pe4:e1-1-c1-1 (1/1/c1/1)
14:14:23 INFO Created link: p1:e1-1-c6-1 (1/1/c6/1) ▪┄┄▪ pe2:e1-1-c7-1 (1/1/c7/1)
14:14:23 INFO Created link: p2:e1-1-c4-1 (1/1/c4/1) ▪┄┄▪ pe4:e1-1-c2-1 (1/1/c2/1)
14:14:23 INFO Created link: pe4:e1-1-c4-1 (1/1/c4/1) ▪┄┄▪ spine22:e1-32
14:14:23 INFO Created link: p1:e1-1-c11-1 (1/1/c11/1) ▪┄┄▪ p2:e1-1-c11-1 (1/1/c11/1)
14:14:23 INFO Created link: p2:e1-1-c12-1 (1/1/c12/1) ▪┄┄▪ p1:e1-1-c12-1 (1/1/c12/1)
14:14:23 INFO Created link: pe1:e1-1-c4-1 (1/1/c4/1) ▪┄┄▪ spine22:e1-31
14:14:23 INFO Created link: p2:e1-1-c5-1 (1/1/c5/1) ▪┄┄▪ vRR:e1-2
14:14:23 INFO Created link: p1:e1-1-c5-1 (1/1/c5/1) ▪┄┄▪ vRR:e1-1
14:14:23 INFO Running postdeploy actions kind=nokia_srsim node=p2
14:14:23 INFO Running postdeploy actions kind=nokia_srsim node=pe4
14:14:23 INFO Created link: pe1:e1-1-c8-1 (1/1/c8/1) ▪┄┄▪ pe2:e1-1-c5-1 (1/1/c5/1)
14:14:23 INFO Running postdeploy actions kind=nokia_srsim node=p1
14:14:23 INFO Running postdeploy actions kind=nokia_srsim node=pe1
14:14:36 INFO Saving node "clab-srexperts-pe2" config as startup...
14:14:37 INFO Saved running configuration node=pe2 addr=10.128.4.22 config-mode=model-driven
14:14:37 INFO node "client11" is being delayed for 120 seconds
14:14:37 INFO Saving node "clab-srexperts-p1" config as startup...
14:14:38 INFO Saving node "clab-srexperts-pe4" config as startup...
14:14:38 INFO Saving node "clab-srexperts-p2" config as startup...
14:14:38 INFO Saving node "clab-srexperts-pe1" config as startup...
14:14:38 INFO Saved running configuration node=p1 addr=10.128.4.11 config-mode=model-driven
14:14:38 INFO Creating container name=ixp1
14:14:38 INFO Saved running configuration node=p2 addr=10.128.4.12 config-mode=model-driven
14:14:38 INFO Creating container name=pe3-1
14:14:38 INFO Saved running configuration node=pe1 addr=10.128.4.21 config-mode=model-driven
14:14:38 INFO Creating container name=agg1
14:14:38 WARN Failed to write chassis_info.json to lab dir node=pe3-a path=/home/nokia/SReXperts/clab/clab-srexperts/pe3 error="/opt/nokia/chassis_info.json not found in image graph driver (UpperDir/MergedDir)"
14:14:38 INFO Retrieved SR OS version from image node=pe3-a version=26.3.1
14:14:38 WARN SR-SIM node has no type set for component in slot, skipping component SR OS config generation. node=pe3-a slot=1
14:14:38 INFO Adding configuration node=clab-srexperts-pe3-a type=partial source=/home/nokia/SReXperts/clab/configs/sros/pe3.partial.cfg
14:14:38 INFO Creating container name=pe3-a
14:14:39 INFO Created link: pe1:e1-1-c7-1 (1/1/c7/1) ▪┄┄▪ ixp1:e1-1
14:14:39 INFO Created link: peering2:e1-2 ▪┄┄▪ ixp1:e1-2
14:14:39 INFO Created link: pe4:e1-1-c5-1 (1/1/c5/1) ▪┄┄▪ agg1:e1-32
14:14:39 INFO Running postdeploy actions kind=nokia_srlinux node=ixp1
14:14:39 INFO Created link: p1:e1-1-c3-1 (1/1/c3/1) ▪┄┄▪ pe3:e1-1-c1-1 (1/1/c1/1)
14:14:39 INFO Created link: p2:e1-1-c3-1 (1/1/c3/1) ▪┄┄▪ pe3:e1-1-c2-1 (1/1/c2/1)
14:14:39 INFO Running postdeploy actions kind=nokia_srlinux node=agg1
14:14:39 INFO Created link: pe3:e1-1-c4-1 (1/1/c4/1) ▪┄┄▪ spine12:e1-31
14:14:39 INFO Running postdeploy actions kind=nokia_srsim node=pe3
14:14:41 INFO Creating container name=spine21
14:14:41 INFO Created link: pe1:e1-1-c3-1 (1/1/c3/1) ▪┄┄▪ spine21:e1-31
14:14:41 INFO Created link: pe4:e1-1-c3-1 (1/1/c3/1) ▪┄┄▪ spine21:e1-32
14:14:41 INFO Created link: spine21:e1-1 ▪┄┄▪ leaf21:e1-31
14:14:41 INFO Created link: spine21:e1-2 ▪┄┄▪ leaf22:e1-31
14:14:41 INFO Created link: spine21:e1-3 ▪┄┄▪ leaf23:e1-31
14:14:41 INFO Running postdeploy actions kind=nokia_srlinux node=spine21
14:14:42 INFO Creating container name=leaf11
14:14:43 INFO Created link: spine12:e1-1 ▪┄┄▪ leaf11:e1-32
14:14:43 INFO Running postdeploy actions kind=nokia_srlinux node=leaf11
14:14:44 INFO node "client13" is being delayed for 120 seconds
14:14:45 INFO Creating container name=spine11
14:14:46 INFO node "client23" is being delayed for 120 seconds
14:14:46 INFO Created link: pe2:e1-1-c3-1 (1/1/c3/1) ▪┄┄▪ spine11:e1-32
14:14:46 INFO Created link: pe3:e1-1-c3-1 (1/1/c3/1) ▪┄┄▪ spine11:e1-31
14:14:46 INFO node "client03" is being delayed for 120 seconds
14:14:46 INFO Created link: spine11:e1-1 ▪┄┄▪ leaf11:e1-31
14:14:46 INFO Created link: spine11:e1-2 ▪┄┄▪ leaf12:e1-31
14:14:46 INFO Created link: spine11:e1-3 ▪┄┄▪ leaf13:e1-31
14:14:46 INFO Running postdeploy actions kind=nokia_srlinux node=spine11
14:14:49 INFO Saved running configuration node=pe4 addr=10.128.4.24 config-mode=model-driven
14:14:55 INFO Saving node "clab-srexperts-pe3" config as startup...
14:14:55 INFO Saved running configuration node=pe3 addr=10.128.4.23 config-mode=model-driven
14:16:18 INFO Creating container name=radius
14:16:18 INFO Creating container name=client22
14:16:18 INFO Creating container name=loki
14:16:18 INFO Creating container name=client04
14:16:18 INFO Creating container name=telegraf
14:16:18 INFO Creating container name=client21
14:16:18 INFO Creating container name=dns
14:16:18 INFO Creating container name=bngblaster
14:16:18 INFO Creating container name=rpki
14:16:18 INFO Creating container name=prometheus
14:16:18 INFO Creating container name=client02
14:16:18 INFO Creating container name=promtail
14:16:18 INFO Creating container name=client01
14:16:18 INFO Creating container name=syslog
14:16:18 INFO Creating container name=transit1
14:16:18 INFO Creating container name=client12
14:16:18 INFO Creating container name=grafana
14:16:18 INFO Creating container name=gnmic
14:16:19 INFO Created link: pe1:e1-1-c5-1 (1/1/c5/1) ▪┄┄▪ transit1:eth1
14:16:19 INFO Created link: leaf21:e1-1 ▪┄┄▪ client21:eth1
14:16:19 INFO Created link: peering2:e1-1 ▪┄┄▪ transit1:eth2
14:16:19 INFO Created link: leaf21:e1-2 ▪┄┄▪ client22:eth1
14:16:19 INFO Created link: ixp1:e1-3 ▪┄┄▪ transit1:eth3
14:16:20 INFO Created link: leaf22:e1-2 ▪┄┄▪ client22:eth2
14:16:20 INFO Created link: pe4:e1-1-c6-1 (1/1/c6/1) ▪┄┄▪ client04:eth1
14:16:20 INFO Created link: leaf23:e1-2 ▪┄┄▪ client22:eth3
14:16:20 INFO Created link: pe2:e1-1-c6-1 (1/1/c6/1) ▪┄┄▪ client02:eth1
14:16:21 INFO Created link: leaf11:e1-2 ▪┄┄▪ client12:eth1
14:16:21 INFO Created link: vRR:e1-4 ▪┄┄▪ dns:eth1
14:16:21 INFO Created link: leaf12:e1-2 ▪┄┄▪ client12:eth2
14:16:21 INFO Created link: pe1:e1-1-c6-1 (1/1/c6/1) ▪┄┄▪ client01:eth1
14:16:21 INFO Created link: leaf13:e1-2 ▪┄┄▪ client12:eth3
14:16:21 INFO Created link: vRR:e1-3 ▪┄┄▪ radius:eth1
14:16:21 INFO Created link: agg1:e1-1 ▪┄┄▪ bngblaster:eth1
14:16:22 INFO Created link: agg1:e1-2 ▪┄┄▪ bngblaster:eth2
14:16:22 INFO Created link: agg1:e1-3 ▪┄┄▪ bngblaster:eth3
14:16:37 INFO Creating container name=client11
14:16:41 INFO Created link: leaf11:e1-1 ▪┄┄▪ client11:eth1
14:16:44 INFO Creating container name=client13
14:16:46 INFO Creating container name=client23
14:16:46 INFO Creating container name=client03
14:16:47 INFO Created link: pe3:e1-1-c6-1 (1/1/c6/1) ▪┄┄▪ client03:eth1
14:16:47 INFO Created link: leaf13:e1-3 ▪┄┄▪ client13:eth1
14:16:47 INFO Created link: p2:e1-1-c2-1 (1/1/c2/1) ▪┄┄▪ pe2-p2:p2-1/1/c2/1
14:16:47 INFO Created link: p1:e1-1-c1-1 (1/1/c1/1) ▪┄┄▪ pe1-p1:p1-1/1/c1/1
14:16:47 INFO Created link: p1:e1-1-c2-1 (1/1/c2/1) ▪┄┄▪ pe2-p1:p1-1/1/c2/1
14:16:47 INFO Created link: leaf23:e1-3 ▪┄┄▪ client23:eth1
14:16:48 INFO Created link: p2:e1-1-c1-1 (1/1/c1/1) ▪┄┄▪ pe1-p2:p2-1/1/c1/1
14:16:48 INFO Created link: pe2:e1-1-c1-1 (1/1/c1/1) ▪┄┄▪ pe2-p1:pe2-1/1/c1/1
14:16:48 INFO Created link: pe2:e1-1-c2-1 (1/1/c2/1) ▪┄┄▪ pe2-p2:pe2-1/1/c2/1
14:16:48 INFO Created link: pe1:e1-1-c2-1 (1/1/c2/1) ▪┄┄▪ pe1-p2:pe1-1/1/c2/1
14:16:48 INFO Created link: pe1:e1-1-c1-1 (1/1/c1/1) ▪┄┄▪ pe1-p1:pe1-1/1/c1/1
14:18:02 INFO Executed command node=spine22 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=leaf21 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=vRR command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=leaf11 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=client04 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client04 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=client02 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client02 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=client13 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client13 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=leaf12 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=leaf13 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=leaf23 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=agg1 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=spine21 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=transit1 command="bash -c envsubst < /gobgp/gobgp.tmpl.yml | tee /gobgp/gobgp.yml"
  stdout=
  │ # Copyright 2023 Nokia
  │ # Licensed under the BSD 3-Clause License.
  │ # SPDX-License-Identifier: BSD-3-Clause
  │
  │ global:
  │   config:
  │     as: 64599
  │     router-id: 10.46.4.51
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
14:18:02 INFO Executed command node=transit1 command="bash /client.sh"
  stdout=
  │ failed to parse: unknown evpn subtype: 249

14:18:02 INFO Executed command node=radius command="bash -c envsubst < /etc/network/interfaces.tmpl | tee /etc/network/interfaces"
  stdout=
  │ auto eth1
  │ iface eth1
  │     address 10.64.13.0/31
  │     address fd00:fde8:0:1:4:13:14:1/127
  │     up ip r a 10.0.0.0/8 via 10.64.13.1 dev eth1
  │     up ip -6 r a fd00:fde8::/32 via fd00:fde8:0:1:4:13:14:0 dev eth1

14:18:02 INFO Executed command node=radius command="bash -c envsubst < /etc/raddb/clients.tmpl.conf | tee /etc/raddb/clients.conf"
  stdout=
  │ client pe4 {
  │     ipaddr = 10.46.4.24
  │     secret = pe4-secret
  │ }

14:18:02 INFO Executed command node=radius command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=radius command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=client21 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client21 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=peering2 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=bngblaster command="bash -c sysctl net.ipv6.conf.eth1.disable_ipv6=1"
  stdout=
  │ net.ipv6.conf.eth1.disable_ipv6 = 1

14:18:02 INFO Executed command node=bngblaster command="bash -c sysctl net.ipv6.conf.eth2.disable_ipv6=1"
  stdout=
  │ net.ipv6.conf.eth2.disable_ipv6 = 1

14:18:02 INFO Executed command node=bngblaster command="bash -c sysctl net.ipv6.conf.eth3.disable_ipv6=1"
  stdout=
  │ net.ipv6.conf.eth3.disable_ipv6 = 1

14:18:02 INFO Executed command node=bngblaster command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=bngblaster command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=bngblaster command="bash -c bngblaster -S ctrl.sock -L /bngblaster.log -C /bngblaster.json &"
  stdout=
  │ Jun 08 14:16:22.513207 Total PPS of all streams: 0.00

14:18:02 INFO Executed command node=client22 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client22 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=client01 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client01 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=client12 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client12 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=client11 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client11 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=client23 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client23 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=client03 command="bash /client.sh" stdout=""
14:18:02 INFO Executed command node=client03 command="bash -c echo 'nameserver 10.128.4.15' | sudo tee /etc/resolv.conf"
  stdout=
  │ nameserver 10.128.4.15

14:18:02 INFO Executed command node=spine11 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=spine12 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=leaf22 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=ixp1 command="usermod -aG ntwkadmin admin" stdout=""
14:18:02 INFO Executed command node=dns command="bash -c envsubst < /etc/dnsmasq.tmpl.conf | tee /etc/dnsmasq.d/dns.conf"
  stdout=
  │ # PE loopbacks in GRT domain
  │ host-record=p1.grt,g4-p1.grt,clab-srexperts-p1.grt,10.46.4.11,fd00:fde8::4:11
  │ host-record=p2.grt,g4-p2.grt,clab-srexperts-p2.grt,10.46.4.12,fd00:fde8::4:12
  │ host-record=vRR.grt,g4-vRR.grt,clab-srexperts-vRR.grt,10.46.4.13,fd00:fde8::4:13
  │ host-record=pe1.grt,g4-pe1.grt,clab-srexperts-pe1.grt,10.46.4.21,fd00:fde8::4:21
  │ host-record=pe2.grt,g4-pe2.grt,clab-srexperts-pe2.grt,10.46.4.22,fd00:fde8::4:22
  │ host-record=pe3.grt,g4-pe3.grt,clab-srexperts-pe3.grt,10.46.4.23,fd00:fde8::4:23
  │ host-record=pe4.grt,g4-pe4.grt,clab-srexperts-pe4.grt,10.46.4.24,fd00:fde8::4:24
  │ host-record=spine11.grt,g4-spine11.grt,clab-srexperts-spine11.grt,10.46.4.31,fd00:fde8::4:31
  │ host-record=spine12.grt,g4-spine12.grt,clab-srexperts-spine12.grt,10.46.4.32,fd00:fde8::4:32
  │ host-record=leaf11.grt,g4-leaf11.grt,clab-srexperts-leaf11.grt,10.46.4.33,fd00:fde8::4:33
  │ host-record=leaf12.grt,g4-leaf12.grt,clab-srexperts-leaf12.grt,10.46.4.34,fd00:fde8::4:34
  │ host-record=leaf13.grt,g4-leaf13.grt,clab-srexperts-leaf13.grt,10.46.4.35,fd00:fde8::4:35
  │ host-record=spine21.grt,g4-spine21.grt,clab-srexperts-spine21.grt,10.46.4.41,fd00:fde8::4:41
  │ host-record=spine22.grt,g4-spine22.grt,clab-srexperts-spine22.grt,10.46.4.42,fd00:fde8::4:42
  │ host-record=leaf21.grt,g4-leaf21.grt,clab-srexperts-leaf21.grt,10.46.4.43,fd00:fde8::4:43
  │ host-record=leaf22.grt,g4-leaf22.grt,clab-srexperts-leaf22.grt,10.46.4.44,fd00:fde8::4:44
  │ host-record=leaf23.grt,g4-leaf23.grt,clab-srexperts-leaf23.grt,10.46.4.45,fd00:fde8::4:45
  │ host-record=peering2.grt,g4-peering2.grt,clab-srexperts-peering2.grt,10.46.4.53,fd00:fde8::4:53
  │ # PE OOB addresses
  │ host-record=p1,p1.oob,g4-p1,g4-p1.oob,clab-srexperts-p1,clab-srexperts-p1.oob,10.128.4.11
  │ host-record=p2,p2.oob,g4-p2,g4-p2.oob,clab-srexperts-p2,clab-srexperts-p2.oob,10.128.4.12
  │ host-record=vRR,vRR.oob,g4-vRR,g4-vRR.oob,clab-srexperts-vRR,clab-srexperts-vRR.oob,10.128.4.13
  │ host-record=pe1,pe1.oob,g4-pe1,g4-pe1.oob,clab-srexperts-pe1,clab-srexperts-pe1.oob,10.128.4.21
  │ host-record=pe2,pe2.oob,g4-pe2,g4-pe2.oob,clab-srexperts-pe2,clab-srexperts-pe2.oob,10.128.4.22
  │ host-record=pe3,pe3.oob,g4-pe3,g4-pe3.oob,clab-srexperts-pe3,clab-srexperts-pe3.oob,10.128.4.23
  │ host-record=pe4,pe4.oob,g4-pe4,g4-pe4.oob,clab-srexperts-pe4,clab-srexperts-pe4.oob,10.128.4.24
  │ host-record=spine11,spine11.oob,g4-spine11,g4-spine11.oob,clab-srexperts-spine11,clab-srexperts-spine11.oob,10.128.4.31
  │ host-record=spine12,spine12.oob,g4-spine12,g4-spine12.oob,clab-srexperts-spine12,clab-srexperts-spine12.oob,10.128.4.32
  │ host-record=leaf11,leaf11.oob,g4-leaf11,g4-leaf11.oob,clab-srexperts-leaf11,clab-srexperts-leaf11.oob,10.128.4.33
  │ host-record=leaf12,leaf12.oob,g4-leaf12,g4-leaf12.oob,clab-srexperts-leaf12,clab-srexperts-leaf12.oob,10.128.4.34
  │ host-record=leaf13,leaf13.oob,g4-leaf13,g4-leaf13.oob,clab-srexperts-leaf13,clab-srexperts-leaf13.oob,10.128.4.35
  │ host-record=spine21,spine21.oob,g4-spine21,g4-spine21.oob,clab-srexperts-spine21,clab-srexperts-spine21.oob,10.128.4.41
  │ host-record=spine22,spine22.oob,g4-spine22,g4-spine22.oob,clab-srexperts-spine22,clab-srexperts-spine22.oob,10.128.4.42
  │ host-record=leaf21,leaf21.oob,g4-leaf21,g4-leaf21.oob,clab-srexperts-leaf21,clab-srexperts-leaf21.oob,10.128.4.43
  │ host-record=leaf22,leaf22.oob,g4-leaf22,g4-leaf22.oob,clab-srexperts-leaf22,clab-srexperts-leaf22.oob,10.128.4.44
  │ host-record=leaf23,leaf23.oob,g4-leaf23,g4-leaf23.oob,clab-srexperts-leaf23,clab-srexperts-leaf23.oob,10.128.4.45
  │ host-record=peering2,peering2.oob,g4-peering2,g4-peering2.oob,clab-srexperts-peering2,clab-srexperts-peering2.oob,10.128.4.53
  │ host-record=4.srexperts.net.oob,4.srexperts.net,10.128.4.1
  │ # Short names clients
  │ host-record=client01.grt,10.64.21.11,fd00:fde8:0:21::11
  │ host-record=client02.grt,10.64.22.11,fd00:fde8:0:22::11
  │ host-record=client03.grt,10.64.23.11,fd00:fde8:0:23::11
  │ host-record=client04.grt,10.64.24.11,fd00:fde8:0:24::11
  │ host-record=client11.grt,10.64.30.11,fd00:fde8:0:30::11
  │ host-record=client12.grt,10.64.30.12,fd00:fde8:0:30::12
  │ host-record=client13.grt,10.64.30.13,fd00:fde8:0:30::13
  │ host-record=client21.grt,10.64.40.21,fd00:fde8:0:40::21
  │ host-record=client22.grt,10.64.40.22,fd00:fde8:0:40::22
  │ host-record=client23.grt,10.64.40.23,fd00:fde8:0:40::23
  │ host-record=client01.vprn.dci,192.168.21.11,fd00:ffdd:0:21::11
  │ host-record=client02.vprn.dci,192.168.22.11,fd00:ffdd:0:22::11
  │ host-record=client03.vprn.dci,192.168.23.11,fd00:ffdd:0:23::11
  │ host-record=client04.vprn.dci,192.168.24.11,fd00:ffdd:0:24::11
  │ host-record=client11.vprn.dci,192.168.30.11,fd00:ffdd:0:30::11
  │ host-record=client12.vprn.dci,192.168.30.12,fd00:ffdd:0:30::12
  │ host-record=client13.vprn.dci,192.168.30.13,fd00:ffdd:0:30::13
  │ host-record=client21.vprn.dci,192.168.40.21,fd00:ffdd:0:40::21
  │ host-record=client22.vprn.dci,192.168.40.22,fd00:ffdd:0:40::22
  │ host-record=client23.vprn.dci,192.168.40.23,fd00:ffdd:0:40::23
  │ host-record=client11.edavpls.dci,10.30.0.11,fd00:fdfd:0:3000::11
  │ host-record=client12.edavpls.dci,10.30.0.12,fd00:fdfd:0:3000::12
  │ host-record=client13.edavpls.dci,10.30.0.13,fd00:fdfd:0:3000::13
  │ host-record=client11.edavprn.dci,10.30.1.11,fd00:fdfd:0:3001::11
  │ host-record=client12.edavprn.dci,10.30.2.12,fd00:fdfd:0:3002::12
  │ host-record=client13.edavprn.dci,10.30.3.13,fd00:fdfd:0:3003::13
  │ # Short names point-to-points
  │ #p1
  │ host-record=1.p2.interface.p1.router,10.64.11.22,fd00:fde8:0:1:4:11:12:0
  │ host-record=2.p2.interface.p1.router,10.64.12.23,fd00:fde8:0:1:4:12:11:1
  │ host-record=pe1.interface.p1.router,10.64.11.0,fd00:fde8:0:1:4:11:21:0
  │ host-record=pe2.interface.p1.router,10.64.11.2,fd00:fde8:0:1:4:11:22:0
  │ host-record=pe3.interface.p1.router,10.64.11.4,fd00:fde8:0:1:4:11:23:0
  │ host-record=pe4.interface.p1.router,10.64.11.6,fd00:fde8:0:1:4:11:24:0
  │ host-record=vRR.interface.p1.router,10.64.11.8,fd00:fde8:0:1:4:11:13:0
  │ #p2
  │ host-record=1.p1.interface.p2.router,10.64.11.23,fd00:fde8:0:1:4:11:12:1
  │ host-record=2.p1.interface.p2.router,10.64.12.22,fd00:fde8:0:1:4:12:11:0
  │ host-record=pe1.interface.p2.router,10.64.12.0,fd00:fde8:0:1:4:12:21:0
  │ host-record=pe2.interface.p2.router,10.64.12.2,fd00:fde8:0:1:4:12:22:0
  │ host-record=pe3.interface.p2.router,10.64.12.4,fd00:fde8:0:1:4:12:23:0
  │ host-record=pe4.interface.p2.router,10.64.12.6,fd00:fde8:0:1:4:12:24:0
  │ host-record=vRR.interface.p2.router,10.64.12.8,fd00:fde8:0:1:4:12:13:0
  │ #pe1
  │ host-record=p1.interface.pe1.router,10.64.11.1,fd00:fde8:0:1:4:11:21:1
  │ host-record=p2.interface.pe1.router,10.64.12.1,fd00:fde8:0:1:4:12:21:1
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
  │ host-record=p1.interface.pe2.router,10.64.11.3,fd00:fde8:0:1:4:11:22:1
  │ host-record=p2.interface.pe2.router,10.64.12.3,fd00:fde8:0:1:4:12:22:1
  │ host-record=client02.interface.pe2.router,10.64.22.1,fd00:fde8:0:22::1
  │ host-record=client02.interface.pe2.vprn.dci,192.168.22.1,fd00:ffdd:0:22::1
  │ host-record=spine11.interface.pe2.router,fd00:fde8:0:1:4:22:31:0
  │ host-record=spine12.interface.pe2.router,fd00:fde8:0:1:4:22:32:0
  │ #pe3
  │ host-record=p1.interface.pe3.router,10.64.11.5,fd00:fde8:0:1:4:11:23:1
  │ host-record=p2.interface.pe3.router,10.64.12.5,fd00:fde8:0:1:4:12:23:1
  │ host-record=client03.interface.pe3.router,10.64.23.1,fd00:fde8:0:23::1
  │ host-record=client03.interface.pe3.vprn.dci,192.168.23.1,fd00:ffdd:0:23::1
  │ host-record=spine11.interface.pe3.router,fd00:fde8:0:1:4:23:31:0
  │ host-record=spine12.interface.pe3.router,fd00:fde8:0:1:4:23:32:0
  │ #pe4
  │ host-record=p1.interface.pe4.router,10.64.11.7,fd00:fde8:0:1:4:11:24:1
  │ host-record=p2.interface.pe4.router,10.64.12.7,fd00:fde8:0:1:4:12:24:1
  │ host-record=client04.interface.pe4.router,10.64.24.1,fd00:fde8:0:24::1
  │ host-record=client04.interface.pe4.vprn.dci,192.168.24.1,fd00:ffdd:0:24::1
  │ # Special addresses
  │ host-record=anycast-gw.irb0.1.leafs.dc1,10.64.30.1,fd00:fde8:0:30::1
  │ host-record=anycast-gw.irb0.101.vprn.dci.leafs.dc1,192.168.30.1,fd00:ffdd:0:30::1
  │ host-record=anycast-gw.irb0.1.leafs.dc1,10.64.40.1,fd00:fde8:0:40::1
  │ host-record=anycast-gw.irb0.101.vprn.dci.leafs.dc1,192.168.40.1,fd00:ffdd:0:40::1
  │ #
  │ address=/web1.srexperts.topology/10.64.21.11
  │ address=/web2.srexperts.topology/10.64.22.11
  │ address=/web3.srexperts.topology/10.64.23.11
  │ # [/]
  │ # A:admin@pe1# ping clab-srexperts-pe1
  │ # PING 10.64.21.1 56 data bytes
  │ # 64 bytes from 10.64.21.1: icmp_seq=1 ttl=64 time=0.120ms.
  │ interface=eth0
  │ interface=eth1.1
14:18:02 INFO Executed command node=dns command="bash /client.sh" stdout=""
14:18:02 INFO Adding host entries path=/etc/hosts
14:18:03 INFO Adding SSH config for nodes path=/etc/ssh/ssh_config.d/clab-srexperts.conf
14:18:03 INFO containerlab version
  🎉=
  │ A newer containerlab version (0.76.0) is available!
  │ Release notes: https://containerlab.dev/rn/0.76/
  │ Run 'clab version upgrade' or see https://containerlab.dev/install/ for other installation options.
╭───────────────────────────┬─────────────────────────────────────────┬────────────┬────────────────╮
│            Name           │                Kind/Image               │    State   │ IPv4/6 Address │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-agg1       │ nokia_srlinux                           │ running    │ 10.128.4.52    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-bngblaster │ linux                                   │ running    │ 10.128.4.61    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client01   │ linux                                   │ running    │ 10.128.4.25    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client02   │ linux                                   │ running    │ 10.128.4.26    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client03   │ linux                                   │ running    │ 10.128.4.27    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client04   │ linux                                   │ running    │ 10.128.4.28    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client11   │ linux                                   │ running    │ 10.128.4.36    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client12   │ linux                                   │ running    │ 10.128.4.37    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client13   │ linux                                   │ running    │ 10.128.4.38    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client21   │ linux                                   │ running    │ 10.128.4.46    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client22   │ linux                                   │ running    │ 10.128.4.47    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-client23   │ linux                                   │ running    │ 10.128.4.48    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-dns        │ linux                                   │ running    │ 10.128.4.15    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-gnmic      │ linux                                   │ running    │ 10.128.4.71    │
│                           │ ghcr.io/openconfig/gnmic:0.43.0         │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-grafana    │ linux                                   │ running    │ 10.128.4.73    │
│                           │ grafana/grafana:12.3.3                  │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-ixp1       │ nokia_srlinux                           │ running    │ 10.128.4.51    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-leaf11     │ nokia_srlinux                           │ running    │ 10.128.4.33    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-leaf12     │ nokia_srlinux                           │ running    │ 10.128.4.34    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-leaf13     │ nokia_srlinux                           │ running    │ 10.128.4.35    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-leaf21     │ nokia_srlinux                           │ running    │ 10.128.4.43    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-leaf22     │ nokia_srlinux                           │ running    │ 10.128.4.44    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-leaf23     │ nokia_srlinux                           │ running    │ 10.128.4.45    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-loki       │ linux                                   │ running    │ 10.128.4.76    │
│                           │ grafana/loki:3.5.10                     │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-p1-a       │ nokia_srsim                             │ running    │ 10.128.4.11    │
│                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-p2-a       │ nokia_srsim                             │ running    │ 10.128.4.12    │
│                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-pe1-a      │ nokia_srsim                             │ running    │ 10.128.4.21    │
│                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-pe2-a      │ nokia_srsim                             │ running    │ 10.128.4.22    │
│                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-pe3-a      │ nokia_srsim                             │ running    │ 10.128.4.23    │
│                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-pe4-a      │ nokia_srsim                             │ running    │ 10.128.4.24    │
│                           │ nokia_srsim:26.3.R1                     │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-peering2   │ nokia_srlinux                           │ running    │ 10.128.4.53    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-prometheus │ linux                                   │ running    │ 10.128.4.72    │
│                           │ quay.io/prometheus/prometheus:v2.54.1   │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-promtail   │ linux                                   │ running    │ 10.128.4.75    │
│                           │ grafana/promtail:3.5.10                 │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-radius     │ linux                                   │ running    │ 10.128.4.14    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-rpki       │ linux                                   │ running    │ 10.128.4.55    │
│                           │ rpki/stayrtr                            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-spine11    │ nokia_srlinux                           │ running    │ 10.128.4.31    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-spine12    │ nokia_srlinux                           │ running    │ 10.128.4.32    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-spine21    │ nokia_srlinux                           │ running    │ 10.128.4.41    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-spine22    │ nokia_srlinux                           │ running    │ 10.128.4.42    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-syslog     │ linux                                   │ running    │ 10.128.4.74    │
│                           │ quay.io/linuxserver.io/syslog-ng:4.10.2 │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-telegraf   │ linux                                   │ restarting │ N/A            │
│                           │ telegraf:latest                         │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-transit1   │ linux                                   │ running    │ 10.128.4.54    │
│                           │ ghcr.io/srl-labs/network-multitool      │            │ N/A            │
├───────────────────────────┼─────────────────────────────────────────┼────────────┼────────────────┤
│ clab-srexperts-vRR        │ nokia_srlinux                           │ running    │ 10.128.4.13    │
│                           │ ghcr.io/nokia/srlinux:26.3.1            │            │ N/A            │
╰───────────────────────────┴─────────────────────────────────────────┴────────────┴────────────────╯
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

- [SR OS Release 26.3](https://documentation.nokia.com/sr/26-3/index.html)
- [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)
- [Network Developer Portal](https://network.developer.nokia.com/sr/learn/)

### Misc Tools/Software

#### Windows

- [WSL environment](https://learn.microsoft.com/en-us/windows/wsl/install)
- [Windows Terminal](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701)
- [MobaXterm](https://mobaxterm.mobatek.net/download.html)
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

As you can imagine, creating the activities that make up this event is a lot of work.  The event team would like to thank the following team members (in alphabetical order) for their contributions: Alejandro Aguado Martin, Alexandre Nogueira, Asad Arafat, Bhavish Khatri, Conar McGill, Diogo Pinheiro, Emre Cinar, Gordon Gidófalvy, Gustavo Ruggirello, Hans Thienpondt, James Cumming, Jeroen Rommens, João Machado, Kaelem Chandra, Karan Singh Khandelwal, Kleber Yoshiki Sato, Laleh Kiani, Louis Van Eeckhoudt, Maged Makramalla, Mathis Bramkamp, Miguel Redondo Ferrero, Roman Dodin, Saju Salahudeen, Samier Barguil, Siva Sivakumar, Sven Wisotzky, Thomas Hendriks, Tiago Amado, Victor Alenin, Víctor Serrano Bazán, Vijayalakshmi Gangireddy, Vincent Delannoy and Zeno Dhaene.
