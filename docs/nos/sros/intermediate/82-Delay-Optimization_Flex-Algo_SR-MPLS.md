---
tags:
  - SR OS
  - MD-CLI
  - Flexible Algorithm
  - SR-MPLS
  - TWAMP
  - Grafana
  - gNMI
---

# Dynamic delay‑sensitive traffic optimization in SR-MPLS


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Dynamic delay‑sensitive traffic optimization in SR-MPLS                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Activity ID**           | 82                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Short Description**       | Fix customer complaints about laggy and poor‑quality VoIP calls caused by traffic taking suboptimal paths across the SR-MPLS backbone, using TWAMP measurements and Flexible Algorithm.                                                                                                                                                                                                                                                                                                                                                     |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/)<br/>[Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/26-3/7750-sr/pdf/MD-CLI_User_Guide_26.3.R1.pdf)<br/>[gNMIC](https://gnmic.openconfig.net/)<br/>[Nokia YANG browser](https://yangbrowser.nokia.com/sros/26.3.R1?from=0&pathfmt=gnmi)<br/>[Grafana](https://grafana.com/)<br/>[TWAMP-Light](https://documentation.nokia.com/sr/26-3/7x50-shared/oam-diagnostics/oam-fault-performance-tools-protocols.html#ai9exgsu8f)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: PE1, :material-router: PE2, :material-router: P1                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/26-3/7750-sr/pdf/MD-CLI_User_Guide_26.3.R1.pdf)<br/>[Intro SR-MPLS](https://documentation.nokia.com/sr/26-3/7x50-shared/segment-routing-pce-user/segment-rout-with-mpls-data-plane-sr-mpls.html)<br/>[Flex-Algo](https://documentation.nokia.com/sr/26-3/7x50-shared/segment-routing-pce-user/segment-rout-with-mpls-data-plane-sr-mpls.html#ai9ekdb654)<br/>[OAM-PM](https://documentation.nokia.com/acg/25-10-3/books/oam-diagnostics-md/m1204-oam-pm-md-cli.html#ariaid-title1)<br/>[Link-Measurement](https://documentation.nokia.com/sr/26-3/7x50-shared/oam-diagnostics/oam-monitor-report.html#ai9exgstj4) |


By default, IGPs compute shortest paths using standard metrics, which do not account for the strict delay requirements of Real‑Time services such as VoIP, video conferencing, or industrial applications.
Networks often address this by using traffic engineered SR-MPLS paths, created manually or through a PCE. While effective, SR Policies add operational overhead, and a PCE can be costly for lower scale networks. SR-MPLS also introduces a sizable label stack, which reduces efficiency for small packet traffic such as VoIP.

Flex‑Algo offers a simpler and more elegant alternative: it lets the IGP compute paths based on constraints such as delay, without requiring SR policies or adding extra label stack overhead.

## Objective

You are a network engineer responsible for maintaining the performance of a national SR-MPLS backbone.
Recently, customer complaints have increased for latency‑sensitive services such as hosted voice, real‑time collaboration, and cloud‑based industrial applications.
Your operations team already uses TWAMP to measure in-service round‑trip delay for Internet and Real-Time Application traffic such as VoIP, with the results visualized in Grafana.

Your network is currently using default per-link metric in the IGP (IS-IS) which result in traffic taken the shortest path with no understanding of the delay on the network.

Your goal is to configure the network to automatically select the lowest‑delay paths for Real-Time Application traffic (VoIP).
To do that in this activity you deploy TWAMP for per-link measurement and configure Flexible Algorithm.
This approach is chosen instead of deploying SR policies as the additional label stack would significantly increase the size of small packets and offer no benefit for such traffic.

In this activity, you will:

- Use the Grafana dashboard to observe real‑time TWAMP‑based in-service round‑trip delay for VoIP and Internet traffic.
- Use gNMI to configure TWAMP link‑delay measurements and advertise delay‑based metrics across the network.
- Use gNMI to configure IS‑IS Flex‑Algo so the network can dynamically compute the lowest‑delay path for VoIP traffic.
- Use gNMI to modify in VPRN to use different SRv6 paths for VoIP and Internet traffic
- Use the Grafana dashboard to observe how your changes have improved real-time application traffic.

## Expected result
Using the TWAMP tool, you should clearly see the difference in the in-service round‑trip delay between the Internet and Voice IP prefixes on the **Grafana Dashboard**.

!!! info "You can access the dashboard `Flex-Algo SR-MPLS` in a web browser https://`1`,`2`,`n`.srexperts.net:3000, where `1`,`2`,`n` is your group ID."

## Technology explanation

Flexible Algorithm (Flex‑Algorithm) in Nokia SR OS extends IS‑IS and OSPF so the IGP can compute paths based on specific constraints, not just the default shortest‑path metric. This is done through a Flexible Algorithm Definition (FAD), which includes three key components:
- **Calculation type**: The IGP algorithm used (for example, shortest path, value 0)
- **Metric type**: The metric to optimize, such as IGP metric, TE metric, or delay
- **Constraints**: Include/exclude rules based on link administrative groups (colors), like exclude, include‑any, or include‑all

Each router advertises its FADs in the IGP, and all routers participating in the same Flex‑Algorithm must choose the same winning FAD to guarantee loop‑free forwarding.

When used with Segment Routing, each Flex‑Algorithm is assigned an ID (`128`–`255`). This ID maps to the corresponding SR‑MPLS node SID, allowing traffic to follow the constrained topology using a single MPLS label.
This reduces label‑stack depth while still providing traffic‑engineering‑like behavior.

## Lab topology Overview
1. The lab topology includes two PE routers (:material-router: PE1 and :material-router: PE2) and one P‑node (:material-router: P1).
2. Interfaces for both Internet and Voice traffic are configured within VPRN `201` on :material-router: PE1 and :material-router: PE2.
3. Initially, Internet and Voice traffic follow the same path and use the same SR-MPLS tunnel to the remote node SID.
4. The TWAMP setup is already preconfigured in the VPRN, and the in-service round‑trip delay for Internet and Voice traffic is visualized on a **Grafana Dashboard**. (

!!! info "You can access the dashboard `Flex-Algo SR-MPLS` in a web browser https://`1`,`2`,`n`.srexperts.net:3000, where `1`,`2`,`n` is your group ID."

The results indicate that **the measured delay is not suitable for Real-Time applications such as Voice**.

## Tasks

Here are a couple of general remarks that will be useful for the rest of the activity.

/// details | **Hint 1**
    type: tip
You can perform all tasks using the MD‑CLI alone; however, Nokia SR OS is far more than a CLI‑driven system. The platform fully supports automation through modern interfaces such as gNMI.
For this activity, we strongly encourage you to explore these programmatic interfaces and generate configuration dynamically, rather than relying exclusively on CLI commands. This approach not only aligns with industry best practices but also enables scalable, automated network operations.
/// admonition | Example using gnmic
/// tab | `gnmic` command
```
gnmic \
  -a clab-srexperts-pe1 \
  -u admin \
  -p $EVENT_PASSWORD \
  --insecure \
  set \
  --update-path '/configure/router[router-name=Base]' \
  --update-value '{"description":"This is the base router instance."}'
```
///
/// tab | `gnmic` output
```
{
  "source": "clab-srexperts-pe1",
  "timestamp": 1776776339438250115,
  "time": "2026-04-21T12:58:59.438250115Z",
  "results": [
    {
      "operation": "UPDATE",
      "path": "configure/router[router-name=Base]"
    }
  ]
}
```
///
/// tab | Result
```
[gl:/configure]
A:admin@pe1# info router "Base" description
    description "This is the base router instance."
```
///
///
///

/// details | **Hint 2**
    type: tip
/// admonition |
/// tab | Question?
If you use gNMI, where can you find the correct path syntax?
///

/// tab | Answer
You can either consult the [Nokia YANG browser](https://yangbrowser.nokia.com/sros/26.3.R1?from=0&pathfmt=gnmi), or you can check the path syntax directly in the MD‑CLI on the node.
///

/// tab | MD-CLI output
```
A:admin@pe1-sr1# tree gnmi-path /configure routing-options flexible-algorithm-definitions
/configure/routing-options/flexible-algorithm-definitions/apply-groups
/configure/routing-options/flexible-algorithm-definitions/apply-groups-exclude
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/admin-state
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/apply-groups
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/apply-groups-exclude
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/description
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/exclude
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/exclude/admin-group[group-name]
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/flags-tlv
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/include-all
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/include-all/admin-group[group-name]
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/include-any
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/include-any/admin-group[group-name]
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/metric-type
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/priority
```
///
///
///

/// details | **Hint 3**
    type: tip
If you go with gNMI, configure the first router and, optionally, write a small script to push the same configuration to the rest of the nodes.
///

!!! info "Connect to the server in your group's hackathon VM to run gNMI commands"
    ```bash
    ssh admin@clab-srexperts-gnmic
    ```

!!! info "Connect to :material-router: PE1 :material-router: PE2 :material-router: P1 from your group's hackathon VM to check configuration in MD-CLI"
    ```bash
    ssh admin@clab-srexperts-pe1
    ssh admin@clab-srexperts-pe2
    ssh admin@clab-srexperts-p1
    ```

### TWAMP reflector
Create a TWAMP reflector in the Base router instance to reply to the link‑performance measurement probes received from the peer router. Below is an MD‑CLI configuration example for :material-router:PE1, but you should configure all routers in the test segment (:material-router: PE1, :material-router: PE2 and :material-router: P1) using gNMI for network programming.

- The TWAMP reflector uses the default UDP port 862.
/// details | **Advice**
    type: note
Use only the link‑local IPv6 prefix on the TWAMP reflector to simplify link‑measurement configuration on direct interfaces.
///

/// tab | Twamp-Light Reflector configuration example
```
/configure router "Base" twamp-light
    reflector {
        admin-state enable
        udp-port 862
        allow-ipv6-udp-checksum-zero true
        prefix fe80::/64 {
        }
    }
```
///

### Link-Measurement profile
Create a link‑measurement profile to measure the average delay on the direct links, and apply it to all interfaces in the test segment (:material-router: PE1, :material-router: PE2, and :material-router: P1).
Below is an MD‑CLI configuration example for :material-router: PE1 on a single interface, but you should configure all routers in the test segment and all interfaces between them (:material-router: PE1, :material-router: PE2 and :material-router: P1) using gNMI for network programming.

/// details | **Advice**
    type: note
 Do not assign source or destination IPv6 addresses in the network interface twamp-light context so that link‑local addresses are used; this simplifies link‑measurement configuration on direct interfaces in the test segment.
///


/// tab | Link-Measurement Profile configuration example
```
/configure test-oam
    link-measurement {
        measurement-template "direct-if" {
            admin-state enable
            delay avg
            interval 1
            twamp-light {
                ipv6-destination-discovery {
                    admin-state enable
                }
            }
            sample-window {
                multiplier 2
                window-integrity 80
                threshold {
                    relative 10
                }
```
///

/// tab | Link-Measurement Profile on a network interface
```
/configure router "Base"
    interface "pe2" {
        if-attribute {
            delay {
                delay-selection dynamic
                dynamic {
                    measurement-template "direct-if"
                    twamp-light {
                        ipv6 {
                            admin-state enable
                        }
```
///

### Check per-link delay
Check the per-link delay values.

Below is an MD‑CLI output example for :material-router: PE1, but you should get these results from all routers in the test segment (:material-router: PE1, :material-router: PE2 and :material-router: P1) using gNMI.

/// tab | MD-CLI example
```
show test-oam link-measurement interface "interface_name" sample
```
///

/// tab | Expected output
```
A:admin@pe1# show test-oam link-measurement interface "pe2" sample

===============================================================================
Interface Link Measurement Information - pe2
===============================================================================
Template Name: direct-if
Oper State               : Up
Protocol                 : IPv6
Oper Source Address      : fe80::a8c1:abff:fe6a:401a
Source Auto-Assigned     : Yes
Oper Destination Address : fe80::a8c1:abff:fec2:3a8c
Destination Auto-Assigned: Yes
In-Use Src UDP Port      : 49153
In-Use Dst UDP Port      : 862
STAMP Session Identifier : 1001
Failure Condition(s)     : None
Detectable Tx Error      : None

-------------------------------------------------------------------------------
Reporting
-------------------------------------------------------------------------------
Reporting Operational      : Yes
Delay Measure Last Reported: 574us
Timestamp                  : 2026/03/05 09:58:12
Triggered By               : SampleThresholdRelative

-------------------------------------------------------------------------------
Sample Window Delay Measurement Detail                 Currently Reporting: Avg
-------------------------------------------------------------------------------
End Timestamp (UTC)       State  Rcv/Snt  Min(us) Max(us) Avg(us) E F I  Result
-------------------------------------------------------------------------------
N/A                  InProgress    1/1          0       0       0 N N -       0
2026/03/05 09:58:12  SwReported    2/2        515     633     574 N N Y     574
2026/03/05 09:58:10  SwReported    2/2        487     876     681 N N Y     681
2026/03/05 09:58:08  SwReported    2/2        516     534     525 N N Y     525
2026/03/05 09:58:06  SwReported    2/2        711     990     850 N N Y     850
2026/03/05 09:58:04  SwReported    2/2        541     568     554 N N Y     554
2026/03/05 09:58:02  SwReported    2/2        664     738     701 N N Y     701
2026/03/05 09:58:00   Completed    2/2        579     629     604 N N Y     604
2026/03/05 09:57:58  SwReported    2/2        564     592     578 N N Y     578

```
///

### Flexible Algorithm Definition
Create a Flexible Algorithm Definition (FAD) for the delay‑based metric.
Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure all routers in the test segment (:material-router: PE1, :material-router: PE2, and :material-router: P1) using gNMI for network programming.

/// tab | Flexible Algorithm Definition configuration example
```
/configure routing-options
    flexible-algorithm-definitions {
        flex-algo "fad128" {
            admin-state enable
            metric-type delay
        }
```
///

### Add IPv4/IPv6 SID index for Flex-Algo
In the IS‑IS instance, add an IPv4 and/or IPv6 node SID for the Flex‑Algo definition (FAD) you created. This advertises the Flex-Algo node SIDs throughout the network.
Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure all routers in the test segment (:material-router: PE1, :material-router: PE2 and :material-router: P1) using gNMI for network programming.

!!! note "Requirement"
    - Each router must use a different node SID index/label for each Flex-Algo to ensure uniqueness in the SR-MPLS domain
    - Example values for IPv4 Flex‑Algo node SID index: `8021`, `8022`, `8011`; and for IPv6: `8121`, `8122`, `8111`, assigned respectively to routers :material-router: PE1, :material-router: PE2, and :material-router: P1

/// tab | Node-SID MD-CLI configuration example for Algo 0 (default) and Algo 128 (delay-based)
```
/configure router "Base" isis 0
    interface "system" {
        flex-algo 128 {
            ipv4-node-sid {
                index 8021
            }
            ipv6-node-sid {
                index 8121
            }
. . .
```
///

### Add FAD to IS-IS to advertise delay metric
Advertise delay as an additional attribute of links throughout the network with any model-driven method available, and create a loop-free shortest path using delay as metric.
Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure all routers in the test segment (:material-router: PE1, :material-router: PE2 and :material-router: P1) using gNMI for network programming.

/// tab | Flexible Algorithm in IS-IS instance configuration example
```
/configure router "Base" isis 0
    flexible-algorithms {
        admin-state enable
        flex-algo 128 {
            participate true
            advertise "fad128"
        }
    }
```
///

### VPRN export policy
Create an export routing policy to advertise the local Voice L3VPN‑IPv4 prefixes and tag them with the pre‑configured color community.

Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure both PE routers in the test segment (:material-router: PE1, :material-router: PE2) using gNMI for network programming.

!!! info "The prefix-list for Voice subnet is pre-configured on the PE routers"

/// tab | Color and vrf-export communities MD-CLI configuration example
```
/configure policy-options
    community "color1" {
        member "color:00:1" { }
    }
    community "vprn201" {
        member "target:65000:201" { }
    }
```
///

/// tab | VPRN export policy MD-CLI configuration example
```
/configure policy-options policy-statement "export-vprn201"
    entry 10 {
        from {
            prefix-list ["Voice-201"]
        }
        action {
            action-type accept
            community {
                add ["color1" "vprn201"]
            }
        }
    }
    entry 1000 {
        action {
            action-type accept
            community {
                add ["vprn201"]
            }
        }
```
///

### VPRN import policy
Create an import routing policy to map the remote Voice L3VPN‑IPv4 prefixes marked with a color community to the created Flex‑Algo, ensuring that traffic to these destinations follows the best‑delay path.
Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure both PE routers in the test segment (:material-router: PE1, :material-router: PE2) using gNMI for network programming.

/// tab | VPRN import policy MD-CLI configuration example
```
/configure policy-options policy-statement "import-vprn201"
    entry 10 {
        from {
            community {
                expression "[vprn201] AND [color1]"
            }
        }
        action {
            action-type accept
            flex-algo 128
        }
    }
    entry 1000 {
        action {
            action-type accept
        }
    }
```
///

### VPRN update for Flex-Algo
Assign the previously created export and import policies to the VPRN service to advertise the Voice prefixes with the color community and steer the Voice traffic toward received prefixes using the specified color community along the best‑delay path.

Below is an MD‑CLI configuration example for the VPRN on :material-router: PE1, but you should configure it on both routers participating in the VPRN (:material-router: PE1 and :material-router: PE2) using gNMI for network programming.

/// tab | VRF export and import policies in the VPRN
```
/configure service vprn "201"
    bgp-ipvpn {
        mpls {
            vrf-import {
                policy ["import-vprn201"]
            }
            vrf-export {
                policy ["export-vprn201"]
            }
```
///

## Check the results
On the Grafana dashboard, you should now clearly see the difference in round‑trip delay between the base‑effort Internet traffic and the delay‑sensitive traffic such as Voice, VoIP, or video‑conferencing.

This improvement is achieved by using Flexible Algorithm in an SR-MPLS network running IS‑IS as the IGP, all without relying on an external PCE for traffic‑engineering path computation and without increasing of label-stack depth.


To wrap up, you can review a configuration example with the gNMI commands below.

/// details | **Configuration example using gNMI**
    type: success

TWAMP reflector
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path "/configure/router[router-name=Base]/twamp-light/reflector" --update-value '{"admin-state":"enable","allow-ipv6-udp-checksum-zero":true,"prefix":[{"ip-prefix":"fe80::/64"}],"udp-port":862}'
```

Link-Measurement profile
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path "/configure/test-oam" --update-value '{"link-measurement":{"measurement-template":[{"admin-state":"enable","delay":"avg","interval":1,"sample-window":{"multiplier":2,"threshold":{"relative":10},"window-integrity":80},"template-name":"direct-if","twamp-light":{"ipv6-destination-discovery":{"admin-state":"enable"}}}]}}'

gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path "/configure/router[router-name=Base]/interface[interface-name=pe2]/if-attribute/delay/delay-selection" --update-value "dynamic" --update-path "/configure/router[router-name=Base]/interface[interface-name=pe2]/if-attribute/delay/dynamic/link-measurement/link-measurement-template" --update-value "direct-if" --update-path "/configure/router[router-name=Base]/interface[interface-name=pe2]/if-attribute/delay/dynamic/twamp-light/ipv6/admin-state" --update-value "enable"
```

Flexible Algorithm Definition
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path "/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name=fad128]" --update-value '{"admin-state":"enable","metric-type":"delay"}'
```

Add IPv4/IPv6 SID index for Flex-Algo
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --replace-path '/configure/router[router-name=Base]/isis[isis-instance=0]/interface[interface-name=system]/flex-algo[flex-algo-id=128]' --replace-value '{"flex-algo-id":128,"ipv4-node-sid":{"index":"8021"},"ipv6-node-sid":{"index":"8121"}}'
```

Add FAD to IS-IS to advertise delay metric
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/router[router-name=Base]/isis[isis-instance=0]/flexible-algorithms' --update-value '{"admin-state":"enable","flex-algo":[{"advertise":"fad128","flex-algo-id":128,"participate":true}]}'
```

VPRN export policy
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/policy-options/policy-statement[name=export-vprn201]' --update-value '{"name":"export-vprn201","entry":[{"entry-id":10,"from":{"prefix-list":["Voice-201"]},"action":{"action-type":"accept","community":{"add":["color1","vprn201"]}}},{"entry-id":1000,"action":{"action-type":"accept","community":{"add":["vprn201"]}}}]}'
```

VPRN import policy
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --replace-path '/configure/policy-options/policy-statement[name=import-vprn201]' --replace-value '{"name":"import-vprn201","entry":[{"entry-id":10,"from":{"community":{"expression":"[vprn201] AND [color1]"}},"action":{"action-type":"accept","flex-algo":128}},{"entry-id":1000,"action":{"action-type":"accept"}}]}'
```

VPRN update for Flex-Algo
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/service/vprn[service-name=201]/bgp-ipvpn/mpls/vrf-export' --update-value '{"policy":["export-vprn201"]}'

gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/service/vprn[service-name=201]/bgp-ipvpn/mpls/vrf-import' --update-value '{"policy":["import-vprn201"]}'
```
///

Are these the commands you used for the Flex‑Algo configuration, or did you opt for a different approach?

## Summary and review
Congratulations! If you've made it this far you have completed this activity and achieved the following:

- You learned how to dynamically separate delay‑sensitive application traffic from base‑effort Internet traffic in an SR-MPLS network — without relying on an external PCE device.
- You built a working link‑measurement setup to monitor round‑trip delay on direct links.
- You created a Flexible Algorithm definition that automatically computes the best loop‑free path using a delay‑based metric.
- You created the SR‑MPLS node SID in the IS‑IS instance for this Flex‑Algo definition so it can be advertised and used to automatically compute the best loop‑free path based on the delay metric.
- You learned how to program a Nokia SR OS router using gNMIc and MD‑CLI.
- You monitored live traffic delay metrics using the Grafana visualization solution.

That’s a pretty extensive list of accomplishments — well done!


