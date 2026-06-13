---
tags:
  - SR OS
  - MD-CLI
  - Flexible Algorithm
  - SRv6
  - TWAMP
  - Grafana
  - gNMI
---

# Dynamic delay‑sensitive traffic optimization in SRv6


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Dynamic delay‑densitive traffic optimization in SRv6                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Activity ID**           | 17                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Short Description**       | Fix rising customer complaints about laggy and poor quality VoIP calls caused by traffic taking suboptimal paths across the SRv6 backbone using TWAMP measurements and Flexible Algorithm.                                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/)<br/>[Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/26-3/7750-sr/pdf/MD-CLI_User_Guide_26.3.R1.pdf)<br/>[gNMIC](https://gnmic.openconfig.net/)<br/>[Nokia YANG browser](https://yangbrowser.nokia.com/sros/26.3.R1?from=0&pathfmt=gnmi)<br/>[Grafana](https://grafana.com/)<br/>[TWAMP-Light](https://documentation.nokia.com/sr/26-3/7x50-shared/oam-diagnostics/oam-fault-performance-tools-protocols.html#ai9exgsu8f)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: PE1, :material-router: PE2, :material-router: P1                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/26-3/7750-sr/pdf/MD-CLI_User_Guide_26.3.R1.pdf)<br/>[Intro SRv6](https://documentation.nokia.com/sr/26-3/7x50-shared/segment-routing-pce-user/segment-rout-with-ipv6-data-plane-srv6.html#ariaid-title2)<br/>[Flex-Algo](https://documentation.nokia.com/sr/26-3/7x50-shared/segment-routing-pce-user/segment-rout-with-ipv6-data-plane-srv6.html#ariaid-title13)<br/>[OAM-PM](https://documentation.nokia.com/acg/25-10-3/books/oam-diagnostics-md/m1204-oam-pm-md-cli.html#ariaid-title1)<br/>[Link-Measurement](https://documentation.nokia.com/sr/26-3/7x50-shared/oam-diagnostics/oam-monitor-report.html#ai9exgstj4) |


By default, IGPs compute shortest paths using standard metrics, which do not account for the strict delay requirements of Real‑Time services such as VoIP, video conferencing, or industrial applications.  
Networks often address this by using traffic engineered SRv6 paths, created manually or through a PCE. While effective, SR Policies add operational overhead, and a PCE can be costly for lower scale networks. SRv6 also introduces a sizable SRH, which reduces efficiency for small packet traffic such as VoIP.  

Flex‑Algo offers a simpler and more elegant alternative: it lets the IGP compute paths based on constraints such as delay, without requiring SRv6 policies or adding extra SRH overhead.

## Objective

You are a network engineer responsible for maintaining the performance of a national SRv6 backbone.
Recently, customer complaints have increased for latency‑sensitive services such as hosted voice, real‑time collaboration, and cloud‑based industrial applications.
Your operations team already uses TWAMP to measure in-service round‑trip delay for Internet and Real-Time Application traffic such as VoIP, with the results visualized in Grafana.

Your network is currently using default per-link metric in the IGP (ISIS) which result in traffic taken the shortest path with no understanding of the delay on the network.

Your goal is to configure the network to automatically select the lowest‑delay paths for Real-Time Application traffic (VoIP).
To do that in this activity you deploy TWAMP for per-link measurement and configure Flexible Algorithm.
This approach is chosen instead of deploying SRv6 policies as the additional SRH would significantly increase the size of small packets and offer no benefit for such traffic.

In this activity, you will:

- Use the Grafana dashboard to observe in-service real‑time TWAMP‑based round‑trip delay for VoIP and Internet traffic.
- Use gNMI to configure TWAMP link‑delay measurements and advertise delay‑based metrics across the network.
- Use gNMI to configure IS‑IS Flex‑Algo so the network can dynamically compute the lowest‑delay path for VoIP traffic.
- Use gNMI to configure and advertise SRv6 micro‑SID locators used by VoIP traffic to reach their destination.
- Use gNMI to modify the VPRN to use different SRv6 paths for Voice and Internet traffic.
- Use the Grafana dashboard to observe how your changes have improved real-time application traffic.

## Expected result
Using the TWAMP tool, you should clearly see the difference in round‑trip delay between the Internet and Voice IP prefixes on the **Grafana Dashboard**.

!!! info "You can access the dashboard `Flex-Algo SRv6` in a web browser https://`1`,`2`,`n`.srexperts.net:3000, where `1`,`2`,`n` is your group ID." 

## Technology explanation

Flexible Algorithm (Flex‑Algorithm) in Nokia SR OS extends IS‑IS and OSPF so the IGP can compute paths based on specific constraints, not just the default shortest‑path metric. This is done through a Flexible Algorithm Definition (FAD), which includes three key components:

- **Calculation type**: The IGP algorithm used (for example, shortest path, value 0) 
- **Metric type**: The metric to optimize, such as IGP metric, TE metric, or delay
- **Constraints**: Include/exclude rules based on link administrative groups (colors), like exclude, include‑any, or include‑all 

Each router advertises its FADs in the IGP, and all routers participating in the same Flex‑Algorithm must choose the same winning FAD to guarantee loop‑free forwarding.

When used with Segment Routing over IPv6 (SRv6), each Flex‑Algorithm is assigned an ID (`128`–`255`). This ID maps to the corresponding SRv6 locator, allowing traffic to follow the constrained topology using a single locator‑derived SID placed in the IPv6 destination address.  This eliminates the need for an SRv6 Header (SRH), reducing network overhead while still providing traffic‑engineering‑like behavior.

## Lab topology Overview
1. The lab topology includes two PE routers (:material-router: PE1 and :material-router: PE2) and one P‑node (:material-router: P1). 
3. Interfaces for both Internet and Voice traffic are configured within VPRN `200` on :material-router: PE1 and :material-router: PE2. 
4. Initially, Internet and Voice traffic follow the same path and use the same SRv6 micro‑segment locator. 
5. The TWAMP setup is already preconfigured in the VPRN, and the in-service round‑trip delay for Internet and Voice traffic is visualized on a **Grafana Dashboard**.

!!! info "You can access the dashboard `Flex-Algo SRv6` in a web browser https://`1`,`2`,`n`.srexperts.net:3000, where `1`,`2`,`n` is your group ID." 

The results indicate that **the measured delay is not suitable for Real-Time applications such as Voice in this activity**.

## Tasks

Here are a couple of general remarks that will be useful for the rest of the activity.

/// details | **Hint 1**
    type: tip    
You can perform all tasks using the MD‑CLI alone; however, Nokia SR OS is far more than a CLI‑driven system. The platform fully supports automation through modern interfaces such as gNMI.  
For this activity, we strongly encourage you to explore these programmatic interfaces and generate configuration dynamically, rather than relying exclusively on CLI commands. This approach not only aligns with industry best practices but also enables scalable, automated network operations. 
/// admonition | Example using `gnmic`
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
A:admin@pe1# tree gnmi-path /configure routing-options flexible-algorithm-definitions
/configure/routing-options/flexible-algorithm-definitions/apply-groups
/configure/routing-options/flexible-algorithm-definitions/apply-groups-exclude
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]
/configure/routing-options/flexible-algorithm-definitions/flex-algo[flex-algo-name]/admin-state
/configure/routing-optionsflexible-algorithm-definitions/flex-algo[flex-algo-name]/apply-groups
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
    ```
    ssh admin@clab-srexperts-gnmic
    ```
!!! info "Connect to :material-router: PE1 :material-router: PE2 :material-router: P1 from your group's hackathon instance to check the configuration in MD-CLI"
    ```
    ssh admin@clab-srexperts-pe1
    ssh admin@clab-srexperts-pe2
    ssh admin@clab-srexperts-p1
    ```

### TWAMP reflector
Create a TWAMP reflector in the Base router instance to reply to the link‑performance measurement probes received from the peer router. 
Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure all routers in the test segment (:material-router: PE1, :material-router: PE2 and :material-router: P1) using gNMI for network programming. 

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
Check per-link delay using either MD-CLI or gNMI interface command.

Below is an MD‑CLI output example for :material-router: PE1, but you should get these results all routers in the test segment (:material-router: PE1, :material-router: PE2 and :material-router: P1) using gNMI. Try to find how to check it with gNMI.

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

### SRv6 micro-segment block and micro-segment locator
Create a SRv6 micro‑segment block and a micro‑segment locator to be used for delay-sensitive applications (Voice). 

Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure all PE routers in the test segment (:material-router: PE1, :material-router: PE2) using gNMI for network programming. The micro-segment block and locator configuration is **not required** on a transit node (:material-router: P1).  

!!! note "Requirement" 
    - Each router must use a different unique node (`un`) value to ensure uniqueness of the SRv6 micro‑segment locator  
    - Example values: `121` and `122` for :material-router: PE1 and :material-router: PE2

/// tab | micro-segment and micro-segment locator configuration example
```
/configure router "Base" segment-routing segment-routing-v6
    micro-segment {
         block "ublock-128" {
            admin-state enable
            termination-fpe [1]
            label-block "srv6-ublock-128"
            prefix {
                ip-prefix 5f00:128::/32
            }
            static-function {
                max-entries 96
            }
        }
    micro-segment-locator "ulocator-128" {
        admin-state enable
        algorithm 128
        block "ublock-128"
        un {
            value 121
        }
    }
```  
///

### Delay metric advertisement in ISIS
Advertise delay as an additional attribute of links throughout the network with any model-driven method available, and create a loop-free shortest path using delay as metric. 

Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure all routers in the test segment (:material-router: PE1, :material-router: PE2 and :material-router: P1) using gNMI for network programming.  

/// tab | Flexible Algorithm in ISIS instance configuration example  
```
/configure router "Base" isis 0
A:admin@pe1# info
    flexible-algorithms {
        admin-state enable
        flex-algo 128 {
            participate true
            advertise "fad128"
        }
    }
```  
///

### Flex-Afgo micro-segment locator advertisement in ISIS on PE routers
Advertise SRv6 micro-SID locators for the paths to be used by delay-sensitive applications. 

Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure PE routers in the test segment (:material-router: PE1, :material-router: PE2) using gNMI for network programming.  

/// tab | Flex-Algo micro-segment locator in the IS-IS configuration example
```
/configure router "Base" isis 0
    segment-routing-v6 {
        admin-state enable
        micro-segment-locator "ulocator-128" {
            level-capability 2
        }
```  
///

### Enable SRv6 Locator TLVs in ISIS on P1 router
Although the micro‑segment block and locator configuration are not required on a transit :material-router: P1 router, SRv6 must be enabled in IS‑IS so that the :material-router: P1 router processes the SRv6 Locator TLVs and installs the algorithm 128 locator routes. 

Below is an MD‑CLI configuration example for :material-router: P1, but you should configure it using gNMI to configure this router.  
/// tab | Enable SRv6 in IS-IS
```
/configure router "Base" isis 0 segment-routing-v6
    admin-state enable

```  
///

### VPRN export policy
Create a routing policy to advertise the L3VPN‑IPv4 prefixes for the Voice interface using the Flex‑Algo micro‑segment locator.  

Below is an MD‑CLI configuration example for :material-router: PE1, but you should configure both PE routers in the test segment (:material-router: PE1, :material-router: PE2) using gNMI for network programming.  

!!! info "The prefix-list for Voice subnet is pre-configured on the PE routers"

/// tab | VPRN export policy MD-CLI configuration example
```
/configure policy-options policy-statement "export-vprn200"
    entry 10 {
        from {
            prefix-list ["Voice-200"]
        }
        action {
            action-type accept
            srv6-micro-segment-locator "ulocator-128"
            community {
                add ["vprn200"]
            }
        }
    }
    entry 1000 {
        action {
            action-type accept
            community {
                add ["vprn200"]
            }
        }
    }
```  
///

### VPRN update for FAD and SRv6 micro-segment locator function
Assign the SRv6 micro‑segment locator with the UDT4 or UDT46 function and the previously created export policy to the VPRN service to advertise the Voice prefixes using this locator.  

Below is an MD‑CLI configuration example for the VPRN on :material-router: PE1, but you should configure it on both PE routers participating in the VPRN (:material-router: PE1 and :material-router: PE2) using gNMI for network programming.  

/// tab | SRv6 micro-segment locator function configuration example 
```
/configure service vprn "200"
    segment-routing-v6 1 {
        micro-segment-locator "ulocator-128" {
            function {
                udt46 {
                }
            }
        }
```  
///
/// tab | VRF export policy in the VPRN
```
/configure service vprn "200"
    bgp-ipvpn {
        segment-routing-v6 1 {
            vrf-export {
                policy ["export-vprn200"]
            }
```  
///

## Check the results
On the Grafana dashboard, you should now clearly see the difference in round‑trip delay between the base‑effort Internet traffic and the delay‑sensitive traffic such as Voice, VoIP, or video‑conferencing.

This improvement is achieved by using Flexible Algorithm together with SRv6 micro‑segment locator/function capabilities in an SRv6 network running IS‑IS as the IGP, all without relying on an external PCE for traffic‑engineering path computation.

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

SRv6 micro-segment block and micro-segment locator  
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure  set --update-path "/configure/router[router-name=Base]/segment-routing/segment-routing-v6/micro-segment/block[block-name=ublock-128]" --update-value '{"admin-state":"enable","label-block":"srv6-ublock-128","prefix":{"ip-prefix":"5f00:128::/32"},"static-function":{"max-entries":96},"termination-fpe":[1]}'

gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path "/configure/router[router-name=Base]/segment-routing/segment-routing-v6/micro-segment-locator[locator-name=ulocator-128]" --update-value '{"admin-state":"enable","algorithm":128,"block":"ublock-128","un":{"value":121}}'
```

Delay metric advertisement in ISIS  
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/router[router-name=Base]/isis[isis-instance=0]/flexible-algorithms' --update-value '{"admin-state":"enable","flex-algo":[{"advertise":"fad128","flex-algo-id":128,"participate":true}]}'
```

Flex-Afgo micro-segment locator advertisement in ISIS on PE router  
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/router[router-name=Base]/isis[isis-instance=0]/segment-routing-v6/micro-segment-locator[locator-name=ulocator-128]' --update-value '{"locator-name":"ulocator-128","level-capability":"2"}'
```

Enable SRv6 Locator TLVs in ISIS on P1 router  
```
gnmic -a clab-srexperts-p1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/router[router-name=Base]/isis[isis-instance=0]/segment-routing-v6' --update-value '{"admin-state":"enable"}'
```

VPRN export policy  
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/policy-options/policy-statement[name=export-vprn200]' --update-value '{"name":"export-vprn200","entry":[{"entry-id":10,"from":{"prefix-list":["Voice-200"]},"action":{"action-type":"accept","srv6-micro-segment-locator":"ulocator-128","community":{"add":["vprn200"]}}},{"entry-id":1000,"action":{"action-type":"accept","community":{"add":["vprn200"]}}}]}'
```

VPRN update for FAD and SRv6 micro-segment locator function 
```
gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/service/vprn[service-name=200]/segment-routing-v6[instance=1]/micro-segment-locator[locator-name=ulocator-128]'   --update-value '{"locator-name":"ulocator-128","function":{"udt46":{}}}'

gnmic -a clab-srexperts-pe1:57400 -u admin -p $EVENT_PASSWORD --insecure set --update-path '/configure/service/vprn[service-name=200]/bgp-ipvpn/segment-routing-v6[bgp-instance=1]/vrf-export' --update-value '{"policy":["export-vprn200"]}'
```
/// 


Are these the commands you used for the Flex‑Algo and SRv6 micro‑segment‑locator configuration, or did you opt for a different approach?

## Summary and review
Congratulations! If you've made it this far you have completed this activity and achieved the following:  

- You learned how to dynamically separate delay‑sensitive application traffic from base‑effort Internet traffic in an SRv6 network — without relying on an external PCE device.  
- You built a working link‑measurement setup to monitor round‑trip delay on direct links.  
- You created a Flexible Algorithm definition that automatically computes the best loop‑free path using a delay‑based metric.  
- You configured the SRv6 setup (micro‑segment block and micro‑segment locator advertised in IS‑IS, and the micro‑segment‑locator function in the VPRN) to be used by the delay‑based FAD.  
- You learned how to program a Nokia SR OS router using gNMI and MD‑CLI.  
- You monitored live traffic delay metrics using the Grafana visualization solution.  

That’s a pretty extensive list of accomplishments — well done!


