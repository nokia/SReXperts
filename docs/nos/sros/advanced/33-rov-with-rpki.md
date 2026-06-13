---
tags:
  - SROS
  - NOS
  - RPKI
  - ROV
  - BGP
  - gRPC
  - gNMI
  - Python
  - Security
---

# Route Origin Validation with RPKI

|     |     |
| --- | --- |
| **Activity name** | Route Origin Validation with RPKI  |
| **Activity ID**           | 33 |
| **Short Description** | Monitor and influence ROV in SR OS through configuration and using RPKI infrastructure. |
| **Difficulty** | Intermediate |
| **Tools used** | [Python](https://www.python.org/)<br/>[MicroPython](https://docs.micropython.org/en/latest/library/index.html#)<br/>[pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/26.3.1/index.html)<br/>[gobgpd](https://github.com/osrg/gobgp)<br/>[RPKI server](https://github.com/bgp/stayrtr#stayrtr) |
| **Topology Nodes** | :material-router: PE1 |
| **References** | [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/26.3.1/index.html)<br/>[SR OS Yang browser](https://yangbrowser.nokia.com/sros/26.3.R1)<br/>[SR OS BGP Prefix Origin Validation](https://documentation.nokia.com/sr/26-3/7x50-shared/unicast-routing-protocols/bgp.html#d497e11185)<br/>[RTR Protocol](https://datatracker.ietf.org/doc/html/rfc8210) |

## Objective

Having dealt with several occurrences of prefix hijacking recently, you are now aiming to prevent such incidents from affecting your environment. A common approach that protects the network is Route Origin Validation (ROV) using Resource Public Key Infrastructure (RPKI). A server has been introduced in your network that advertises this routing information. It is now up to you to make sure that origin validation is being done correctly by the devices in your network, and to monitor the results. Knowing that there may be additional information available that hasn't yet propagated through the RPKI infrastructure, you will also create a way to override information provided by the RPKI server for exceptional situations.

## Technology Description

In this activity you will come into contact with ROV configuration in SR OS, as well as explore what information is advertised by an RPKI server. In this section a few concepts are introduced, and additional reading is proposed. These are not strictly required to continue on with the activity and serve mainly as a reference.

### Border Gateway Protocol (BGP)

BGP routes traffic between networks (Autonomous Systems (AS)) on the internet, selecting paths based on policies rather than shortest distance. It does not include any built-in validation, so it relies on the assumption that networks advertise prefixes legitimately. For additional reading on BGP you may be interested in the [RFC](https://datatracker.ietf.org/doc/html/rfc4271) or this [article by Cloudflare](https://www.cloudflare.com/learning/security/glossary/what-is-bgp/).

### Prefix Hijacking

BGP prefix hijacking is said to occur when an Autonomous System (AS) announces ownership of IP address space it does not control. As BGP is largely based on trust and validation is not enabled by default, this could lead to traffic being redirected away from the legitimate owner of the affected IP addresses. That traffic could be intercepted and modified or dropped to cause a deliberate denial of service attack. While prefix hijacking isn't always malicious, the results remain disruptive.

### Resource Public Key Infrastructure (RPKI)

Also known as Resource Certification, RPKI is a specialized public key infrastructure framework to support improved security for the Internet's BGP routing infrastructure. One of the organizations advocating for the global implementation of RPKI is [Mutually Agreed Norms for Routing Security (MANRS)](https://manrs.org/). MANRS published a set of actions, some compulsory, some recommended.

Most notably amongst the various abbreviations used in RPKI is the Route Origin Authorization (ROA). An ROA is a signed RPKI object that can be used by the owner of an IP address to grant permission to an AS to originate routes for that specific address. The RPKI server in this activity converts ROA to tuples of prefix, length, ASN and shares them with :material-router: PE1 using the RPKI-to-Router (RTR) protocol. These tuples are referred to as Validated ROA Payloads (VRPs). More reading is available [here](https://datatracker.ietf.org/doc/draft-yan-sidrops-rpki-terminology/).

### Route Validation in SR OS

For a network element configured to validate routes received in BGP advertisements, the outcome is one of `Valid`, `Invalid` or `Not-Found` when no VRP was found that covers the route. Depending on the network element's configuration, these routes may or may not be considered usable. Origin validation configuration for SR OS is documented [here](https://documentation.nokia.com/sr/26-3/7x50-shared/unicast-routing-protocols/bgp.html#d497e11185).

## Tasks
**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

In this activity you will:

- Confirm that an RPKI session is configured and operational
- Verify that route origin validation has been enabled
- Create a quick and easy way to display an overview of route origin validation results
- Build automation that configures overrides of origin validation information

### Confirming RPKI

As a first step in this activity, SSH into :material-router: PE1 either from your group's hackathon instance or directly via the exposed SSH port (refer to the `show-ports` command). Once you are logged in, look for the configuration of the `origin-validation` server.

??? question "In which router-instance is the RTR session configured?"
    It is configured in the `management` router-instance.
    ```text {.no-copy}
    2026-05-09T19:47:11.38+00:00
    [/]
    A:admin@g2-pe1# /admin show configuration full-context |match rpki-session
        /configure router "management" origin-validation rpki-session 10.128.4.55 admin-state enable
        /configure router "management" origin-validation rpki-session 10.128.4.55 port 8282
    ```

Use an appropriate `show` or `info` command to verify the operational state of the RTR session with the RPKI Server.

!!! note "Setup Reference"
    In the hackathon topology, two elements help us simulate an RPKI server and a BGP peer sending a large amount of routes. The RPKI server is built using the [rpki/stayrtr](https://github.com/bgp/stayrtr#stayrtr) image while the BGP peer downloads data from RIPE to advertise and it does so using [`gobgp`](https://github.com/osrg/gobgp).

??? question "Is :material-router: PE1 receiving any information from the RPKI Server?"
    Yes, yes it is! At the time of this writing there are **664848** IPv4 records and **194123** IPv6 records being sent by the RPKI Server.

??? example "Only if you are stuck: commands to find RPKI information"
    This information can be found via the `/state` tree combined with the `info` command or by using the appropriate `show` command.
    /// tab | Commands
    ```text
    info /state router "management" origin-validation
    show router "management" origin-validation rpki-session detail
    ```
    ///
    /// tab | Output
    ```text {.no-copy}
    2026-05-09T19:53:23.28+00:00
    [gl:/configure router "management" origin-validation]
    A:admin@g2-pe1# info /state router "management" origin-validation
    rpki-session 10.128.3.55 {
        session-state established
        session-flaps 0
        established-time 2026-05-09T19:23:11.1+00:00
        active-ipv4-records 664848
        active-ipv6-records 194123
        serial-id 331
        session-id 7803
    }

    2026-05-09T19:53:24.81+00:00
    [gl:/configure router "management" origin-validation]
    A:admin@g2-pe1# show router "management" origin-validation rpki-session detail

    ===============================================================================
    RPKI Session Information
    ===============================================================================
    IP Address         : 10.128.3.55
    Description        : (Not Specified)
    -------------------------------------------------------------------------------
    Port               : 8282               Oper State         : established
    Uptime             : 0d 00:32:40        Flaps              : 0
    Active IPv4 Records: 664848             Active IPv6 Records: 194123
    Admin State        : Up                 Local Address      : n/a
    Hold Time          : 600                Refresh Time       : 300
    Stale Route Time   : 3600               Connect Retry      : 120
    Serial ID          : 331                Session ID         : 7803
    ===============================================================================
    No. of Sessions    : 1
    ===============================================================================
    ```
    ///

### Verify Origin Validation

Having confirmed that you see VRPs arriving to our peering router :material-router: PE1, the next step is verifying if there is any observeable effect caused by these records. In this task you'll have to figure out if and where origin-validation is enabled, and to see if there are prefixes being rejected due to a failed validation step.

!!! info "Real data"
    Note that because the VRPs are real, routes from the internet are imported into the lab via :material-router: transit1, a Linux container running `gobgpd`. That means the data and IP addresses being looked at with regard to whether or not they have associated origin validation are directly taken from the real world. There is a random element to this activity because the IP addresses advertised by :material-router: transit1 are determined when the topology is deployed and may be different every time.

In this task, look at the BGP neighbor `10.64.54.0` as that IP address corresponds with :material-router: transit1.

??? question "Is ROV enabled for this peer?"
    Yes, via the associated BGP group configuration.
    ```text {.no-copy}
    2026-05-09T20:02:06.87+00:00
    [gl:/configure router "Base" bgp]
    A:admin@g2-pe1# info neighbor "10.64.54.0" group
        group "eBGP-transit-v4"

    2026-05-09T20:02:09.60+00:00
    [gl:/configure router "Base" bgp]
    A:admin@g2-pe1# info group eBGP-transit-v4 origin-validation
        ipv4 true

    2026-05-09T20:02:13.70+00:00
    [gl:/configure router "Base" bgp]
    A:admin@g2-pe1# info group eBGP-transit-v6 origin-validation
        ipv6 true

    ```

Look specifically at the result of origin-validation against the IPv4 prefixes advertised by this neighbor. Once again, use the appropriate `show` commands, or combine `info` with `/state` to find what you are looking for. The [Nokia YANG browser](https://yangbrowser.nokia.com/sros/26.3.R1) may help you here, or try to combine `info full-context` with `match` statements to get closer to what you're looking for.

Interpret the output you see, as ROV may not be happening. In the following three subsections you will more closely look at what is happening to the routes received from :material-router: transit1 and how ROV affects that.

#### Confirm route-validation results are present

First, look at information received from :material-router: transit1. In particular, make sure you use the appropriate `show` command with any possible details revealed.

??? question "Is ROV being done?"
    Yes, but as you might have seen the result is not populated in the `state` information for a given route. The `show` command has output for it.
    /// tab | Commands
    ```bash
    /show router bgp routes ipv4 detail
    info full-context /state router bgp rib ipv4-unicast local-rib | match 10.64.54.0 | match origin-validation-state
    ```
    ///
    /// tab | Example outputs
    ```bash hl_lines="39 48-50"
    2026-05-09T21:11:21.80+00:00
    [gl:/configure]
    A:admin@g2-pe1# /show router bgp routes ipv4 detail
    ===============================================================================
    BGP Router ID:10.46.2.21       AS:65000       Local AS:65000
    ===============================================================================
    Legend -
    Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                    l - leaked, x - stale, > - best, b - backup, p - purge,
                    w - unused-weight-only
    Origin codes  : i - IGP, e - EGP, ? - incomplete

    ===============================================================================
    BGP IPv4 Routes
    ===============================================================================
    Original Attributes

    Network        : 0.0.0.0/0
    Nexthop        : 10.64.54.0
    Path Id        : None
    From           : 10.64.54.0
    Res. Protocol  : LOCAL                  Res. Metric    : 0
    Res. Nexthop   : 10.64.54.0
    Local Pref.    : n/a                    Interface Name : ixp1
    Aggregator AS  : None                   Aggregator     : None
    Atomic Aggr.   : Not Atomic             MED            : None
    AIGP Metric    : None                   IGP Cost       : 0
    Connector      : None
    Community      : No Community Members
    Cluster        : No Cluster Members
    Originator Id  : None                   Peer Router Id : 10.46.2.53
    Fwd Class      : None                   Priority       : None
    Origin         : IGP
    Flags          : Used Valid Best In-RTM
    Route Source   : External
    AS-Path        : 64699 64599 55720 3257
    Route Tag      : 0
    Neighbor-AS    : 64699
    DB Orig Val    : NotFound               Final Orig Val : N/A
    Source Class   : 0                      Dest Class     : 0
    Add Paths Send : Default
    RIB Priority   : Normal
    Last Modified  : 03d06h21m
    ...
    2026-05-09T21:11:57.43+00:00
    [gl:/configure]
    A:admin@g2-pe1# info full-context /state router bgp rib ipv4-unicast local-rib | match 10.64.54.0 | match origin-validation-state
        /state router "Base" bgp rib ipv4-unicast local-rib routes 0.0.0.0/0 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state not-applicable
        /state router "Base" bgp rib ipv4-unicast local-rib routes 1.128.0.0/11 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state not-applicable
        /state router "Base" bgp rib ipv4-unicast local-rib routes 1.224.0.0/11 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state not-applicable
        ...
    ```
    ///

In the next section you will look at why that is.

#### Confirm route-validation results are used

In the `/show` command output, the result of ROV is included but it is not straightforward to filter to only the neighbor you are interested in, while the `/state` output shows `not-applicable` even though ROV was applied as seen in the `/show` output.

To show the result in the `/state` output, you must modify the configuration to change a default behavior in SR OS so that the ROV result becomes applicable. Can you guess which default behavior that is?

??? tip "Default SR OS behavior?"
    By default, SR OS enforces mandatory policy control for eBGP peers. If no import or export policies are configured, the router rejects all incoming and outgoing routes to and from eBGP peers. The result of ROV does not change the rejected route's fate, this can affect the outputs you see.

??? example "Updating default behavior"
    To change this behavior the configuration has to be updated. One option is shown here.
    /// tab | Commands
    ``` text
    /configure router bgp neighbor "10.64.54.0" ebgp-default-reject-policy import false
    ```
    ///
    /// tab | Verification
    ```text
    info full-context /state router bgp rib ipv4-unicast local-rib | match 10.64.54.0 | match origin-validation-state
    ```
    ///
    /// tab | Outcome
    ``` text {.no-copy}
    2026-05-09T21:11:05.31+00:00
    [/]
    A:admin@g2-pe1# info full-context /state router bgp rib ipv4-unicast local-rib | match 10.64.54.0 | match origin-validation-state
    ...
    /state router "Base" bgp rib ipv4-unicast local-rib routes 38.0.0.0/8 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state valid
    /state router "Base" bgp rib ipv4-unicast local-rib routes 39.64.0.0/11 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state valid
    /state router "Base" bgp rib ipv4-unicast local-rib routes 39.128.0.0/10 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state not-found
    ...
    ```
    ///

    Now, despite the route-origin evaluating to `not-found`, the route to `39.128.0.0/10` still appears in the global routing table (GRT):

    ```text {.no-copy}
    2026-05-09T21:12:39.45+00:00
    [/]
    A:admin@g2-pe1# /show router route-table 39.128.0.0/10

    ===============================================================================
    Route Table (Router: Base)
    ===============================================================================
    Dest Prefix[Flags]                            Type    Proto     Age        Pref
          Next Hop[Interface Name]                                    Metric
    -------------------------------------------------------------------------------
    39.128.0.0/10                                 Remote  BGP       00h01m48s  170
          10.64.54.0                                                   0
    -------------------------------------------------------------------------------
    No. of Routes: 1
    Flags: n = Number of times nexthop is repeated
          B = BGP backup route available
          L = LFA nexthop available
          S = Sticky ECMP requested
    ===============================================================================
    ```
    Remember that this prefix `39.128.0.0/10` may not be present in the topology in your situation. If it isn't you can pick any other one that evaluated to `not-found` in that situation and use it in place of `39.128.0.0/10`.

The idea was to be as strict as possible about origin validation, routes that can't be validated shouldn't be accepted. Implementing this will require additional changes to the configuration.

Make sure you are targeting a prefix that is installed in the global routing table (GRT) and has an `origin-validation-state` equal to `not-found` to proceed with the next section.

#### Enable strict validation
Explicitly rejecting routes that don't have matching VRPs can be done via routing policy. First, find a route learned via :material-router: transit1 that has an `origin-validation-state` equal to `not-found` and confirm that it is in the global routing table (GRT). In this case, `39.128.0.0/10` was chosen:

```text {.no-copy}
2026-05-09T21:15:28.36+00:00
[/]
A:admin@g2-pe1# info full-context /state router bgp rib ipv4-unicast local-rib | match 10.64.54.0 | match not-found
    ....
    /state router "Base" bgp rib ipv4-unicast local-rib routes 38.0.0.0/8 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state not-found
    /state router "Base" bgp rib ipv4-unicast local-rib routes 39.64.0.0/11 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state not-found
    /state router "Base" bgp rib ipv4-unicast local-rib routes 39.128.0.0/10 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state not-found
    ....

2026-05-09T21:15:48.87+00:00
[/]
A:admin@g2-pe1# /show router route-table 39.128.0.0/10

===============================================================================
Route Table (Router: Base)
===============================================================================
Dest Prefix[Flags]                            Type    Proto     Age        Pref
      Next Hop[Interface Name]                                    Metric
-------------------------------------------------------------------------------
39.128.0.0/10                                 Remote  BGP       00h07m09s  170
       10.64.54.0                                                   0
-------------------------------------------------------------------------------
No. of Routes: 1
Flags: n = Number of times nexthop is repeated
       B = BGP backup route available
       L = LFA nexthop available
       S = Sticky ECMP requested
===============================================================================
```

Create a `policy-statement` that will explicitly reject any routes that don't have a `valid` outcome for their ROV. Apply this policy in the correct place(s) in SR OS to make sure none of the eBGP transit peers' routes can be imported without a corresponding VRP. Verify your policy has the intended result of `39.128.0.0/10` and any other unverifiable prefixes no longer being installed in the routing table.

??? example "Only if you get stuck: policy configuration"
    One way of reaching the desired state is by adding an import policy to the eBGP transit groups in the BGP configuration:
    ```text
    /configure policy-options policy-statement "reject-not-found" entry 10 from origin-validation-state not-found
    /configure policy-options policy-statement "reject-not-found" entry 10 action action-type reject
    /configure policy-options policy-statement "reject-not-found" default-action action-type accept
    /configure router "Base" bgp group "eBGP-transit-v4" import policy ["reject-not-found"]
    /configure router "Base" bgp group "eBGP-transit-v6" import policy ["reject-not-found"]
    ```

    The route for 39.128.0.0/10 no longer appears in the GRT:

    ```text {.no-copy}
    2026-05-09T21:17:58.54+00:00
    (gl)[/]
    A:admin@g2-pe1# show router route-table 39.128.0.0/10

    ===============================================================================
    Route Table (Router: Base)
    ===============================================================================
    Dest Prefix[Flags]                            Type    Proto     Age        Pref
          Next Hop[Interface Name]                                    Metric
    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    No. of Routes: 0
    Flags: n = Number of times nexthop is repeated
          B = BGP backup route available
          L = LFA nexthop available
          S = Sticky ECMP requested
    ===============================================================================
    ```

### Monitor Origin Validation Results

As you have now seen, enforcing ROV where you only use routes with valid VRP will only allow you to route traffic to part of the internet, so it is not something you can consider now. Remove the strict requirement for valid VRPs and, instead, build a way to easily visualize the coverage of VRPs for a given peer and the prefixes it advertises.

!!! success "Remove strict requirement"
    ```text
    /configure router "Base" bgp group eBGP-transit-v4 delete import
    /configure router "Base" bgp group eBGP-transit-v6 delete import
    ```

In this task you will build a small Python script that connects to your :material-router: PE1 router using pySROS to provide an overview of how many prefixes are identified as `Valid`, `Invalid` and `Not-Found`. Your script should accept an IP address as input to specify the BGP neighbor to look at. Apply it to the BGP neighbor you have looked at so far, `10.64.54.0`.

You can use the Python interpreter on your group's hackathon instance or the onboard interpreter on :material-router: PE1 directly for an easy way to get a view on this information. One expected result could be:

``` bash
For the 92 routes received from 10.64.54.0, the results are
> 36 routes are Valid
> 56 routes are Not-Found
> 0 routes are Invalid
```

!!! note "Cached model information"
    Executing the pySROS `connect()` method remotely might take some time when it connects for the first time, as it needs to transfer information from the node to store its model information before establishing the connection. On subsequent connections this function will execute much faster, as the information is cached.

Refer to the online [pySROS documentation](https://network.developer.nokia.com/static/sr/learn/pysros/26.3.1/index.html), the [Nokia YANG browser](https://yangbrowser.nokia.com/sros/26.3.R1) and the `pwc` command with appropriate modifers to get started. Consider that an easy way to count prefixes per status in Python is with a dictionary. The dictionary's keys can be the possible status with their values initialized as 0, the value of each key then acts as a counter.

!!! info "Authentication"
    When you run a pySROS script from your group's hackathon instance you may find you don't need to specify a password. pySROS will use `~/.ssh/id_rsa` by default if it exists. It does exist on the hackathon instance and containerlab provisions this key as a valid credential for the `admin` user on :material-router: PE1.

!!! warning "Hostkey verification"
    You might have noticed while using pySROS to connect to a device that you get a Python `RuntimeError` due to the target device presenting an unknown host key. The correct way to avoid this is to explicitly trust the known good host keys presented by the device. For lab and transient environments like the one you are working on, this is not efficient and the danger of this vulnerability is limited. You can instead set the `hostkey_verify` parameter in the `connect` call to `False`, as is the case in the examples below. In any live network environment `hostkey_verify` should be set to `True`.

??? tip "Programmatically retrieving BGP RIB info"
    To retrieve RIB entries from :material-router: PE1 with pySROS, you need to retrieve the RIB from the following YANG path:

    `/state/router[router-name='Base']/bgp/rib/ipv4-unicast/local-rib/routes`

    You can try this out using the interactive Python interpreter in your group's hackathon instance:
    /// tab | Code
    ```python
    from pysros.management import connect
    connection = connect(host="clab-srexperts-pe1", username="admin", hostkey_verify=False)
    # this will take a moment!
    rib_routes = connection.running.get("/state/router[router-name='Base']/bgp/rib/ipv4-unicast/local-rib/routes")
    # check out one of the values in the RIB
    rib_entry = rib_routes.popitem()
    rib_entry
    ```
    ///
    /// tab | Python REPL Output from a hackathon instance
    ```bash {.no-copy}
    ~$ python
    >>> from pysros.management import connect
    >>> connection = connect(host="clab-srexperts-pe1", username="admin", hostkey_verify=False)
    # this will take a moment!
    >>> rib_routes = connection.running.get("/state/router[router-name='Base']/bgp/rib/ipv4-unicast/local-rib/routes")
    # check out one of the values in the RIB
    >>> rib_entry = rib_routes.popitem()
    >>> rib_entry
    (('223.64.0.0/10', '10.64.51.2', 'bgp', 1, 0), Container({'prefix': Leaf('223.64.0.0/10'), 'neighbor': Leaf('10.64.51.2'), 'owner': Leaf('bgp'), 'router-instance-origin': Leaf(1), 'path-id': Leaf(0), 'attr-id': Leaf(1779), 'peer-router-id': Leaf('10.46.3.53'), 'last-modified-date': Leaf('2026-04-29T18:01:23.3Z'), 'used-route': Leaf(False), 'valid-route': Leaf(False), 'best-route': Leaf(False), 'backup-route': Leaf(False), 'group-best': Leaf(False), 'sticky-ecmp': Leaf(False), 'stale-route': Leaf(False), 'unused-weight-only': Leaf(False), 'long-live-gr-stale': Leaf(False), 'rtm-install-disabled': Leaf(False), 'origin-validation-state': Leaf('not-applicable'), 'rib-priority': Leaf('normal'), 'leakable-route': Leaf(False), 'leaked-route': Leaf(False), 'in-rtm': Leaf(False), 'invalid-reason': Container({'rejected-route': Leaf(True), 'as-loop': Leaf(False), 'next-hop-unresolved': Leaf(False), 'cluster-loop': Leaf(False), 'd-path-loop': Leaf(False)})}))
    ```
    ///

??? example "Only if you get stuck: example implementation"
    While the on-board interpreter can run this Python script, running the script off-box for what you're trying to achieve is possible too. You may want to compare the two environments.
    /// tab | Script `rpki.py`
    ``` python
    import argparse
    from pysros.management import connect


    def getRPKIStats(connection, peer):
        data = connection.running.get(
            "/state/router[router-name='Base']/bgp/rib/ipv4-unicast/local-rib/routes",
        )
        result = {
            "valid": 0,
            "invalid": 0,
            "not-applicable": 0,
            "not-found": 0,
            "total": 0,
        }

        for route_key, route_data in data.items():
            if route_key[1] == peer:
                result["total"] += 1
                result[route_data["origin-validation-state"].data] += 1
        return result


    def main():
        parser = argparse.ArgumentParser(
            prog="RPKImon",
            description="Gather and show aggregate RPKI data",
            epilog="Depending on the script mode, add a static VRP or display, for the specified peer, the count of the various ROV results and total number of routes.",
        )
        parser.add_argument("address")
        parser.add_argument("-n", "--node", default="clab-srexperts-pe1")
        parser.add_argument("-u", "--username", default="admin")

        args = parser.parse_args()
        connection = connect(
            host=args.node,
            username=args.username,
            hostkey_verify=False,
        )

        print(getRPKIStats(connection, args.address))


    if __name__ == "__main__":
        main()
    ```
    ///
    /// tab | Execution on hackathon instance
    ```bash {.no-copy}
    nokia@2:~$ python rpki.py 10.64.54.0
    {'valid': 44, 'invalid': 0, 'not-applicable': 0, 'not-found': 48, 'total': 92}
    ```
    ///
    /// tab | Execution on :material-router: PE1
    ```bash {.no-copy}
    2026-05-10T12:33:23.27+00:00
    [/]
    A:admin@g2-pe1# pyexec rpki.py 10.64.54.0
    {'total': 92, 'valid': 44, 'invalid': 0, 'not-applicable': 0, 'not-found': 48}
    ```
    ///

### Overwrite RPKI information

In some situations there may be a need to create static VRP entries to augment or override those learned via an RPKI server. Static entries may be useful when testing, or for legacy equipment that does not support the RTR protocol. For your environment, the benefit is a decreased response time for prefix hijacks. Statically creating VRPs lets you mark a route as invalid or valid based on inputs you receive that haven't yet had a chance to propagate through the RPKI infrastructure.

For this task, amend your script from earlier. In addition to being able to read the resulting RPKI information from the BGP RIB, it should now have a mode in which it can take a VRP as input (the exact input format, and how to differentiate the modes is left up to you) and will configure a static ROA as output.

??? tip "Programmatically configuring with pySROS"
    Configuring network elements with pySROS may seem daunting due to the datastructures and models involved, however keep in mind that you can configure the result you want to see on the node and retrieve that same configuration in pySROS to see what the expected input should be.

    Combining that with the interactive Python interpreter can give you some quick feedback on things you are trying.

    /// tab | Configuring an entry
    ```text {.no-copy}
    2026-05-10T12:37:44.39+00:00
    *[pr:/configure]
    A:admin@g2-pe1# compare /
        configure {
            router "Base" {
                origin-validation {
    +               static-entry 192.168.33.0/30 upto 32 origin-as 65005 {
    +                   valid true
    +               }
                }
            }
        }
    ```
    ///
    /// tab | Retrieve and build an entry with the interactive Python interpreter
    ```python
    from pysros.management import connect
    connection = connect(host="clab-srexperts-pe1", username="admin", hostkey_verify=False)
    # this won't take a moment, if it is no longer your first time connecting!
    path = '/nokia-conf:configure/router[router-name="Base"]/origin-validation/static-entry'
    existing_entries = connection.running.get(path)
    existing_entries
    prefix = "192.168.33.4"
    prefix_len = "30"
    asn = "65006"
    key = (prefix+"/"+prefix_len, int(prefix_len), int(asn))
    contents = { "ip-prefix": prefix+"/"+prefix_len, "upto": int(prefix_len), "origin-as": int(asn), "valid": True}
    payload = {key:contents}
    connection.candidate.set(path, payload, commit=True)
    connection.running.get(path)
    ```
    ///
    /// tab | Example output
    ```bash {.no-copy}
    ~$ python
    Python 3.13.5 (main, May  5 2026, 21:05:52) [GCC 14.2.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from pysros.management import connect
    >>> connection = connect(host="clab-srexperts-pe1", username="admin", hostkey_verify=False)
    >>> # this won't take a moment, if it is no longer your first time connecting!
    >>> path = '/nokia-conf:configure/router[router-name="Base"]/origin-validation/static-entry'
    >>> existing_entries = connection.running.get(path)
    >>> existing_entries
    {('192.168.33.0/30', 32, 65005): Container({'ip-prefix': Leaf('192.168.33.0/30'), 'upto': Leaf(32), 'origin-as': Leaf(65005), 'valid': Leaf(True)})}
    >>> prefix = "192.168.33.4"
    >>> prefix_len = "30"
    >>> asn = "65006"
    >>> key = (prefix+"/"+prefix_len, int(prefix_len), int(asn))
    >>> contents = { "ip-prefix": prefix+"/"+prefix_len, "upto": int(prefix_len), "origin-as": int(asn), "valid": True}
    >>> payload = {key:contents}
    >>> connection.candidate.set(path, payload, commit=True)
    >>> connection.running.get(path)
    {('192.168.33.0/30', 32, 65005): Container({'ip-prefix': Leaf('192.168.33.0/30'), 'upto': Leaf(32), 'origin-as': Leaf(65005), 'valid': Leaf(True)}), ('192.168.33.4/30', 30, 65006): Container({'ip-prefix': Leaf('192.168.33.4/30'), 'upto': Leaf(30), 'origin-as': Leaf(65006), 'valid': Leaf(True)})}
    ```
    ///

To test your automation, pick a prefix that is currently reported as `not-found` and override it to observe that it changes to `valid`, because of your script. Once again, you can do this using on-box or off-box Python with pySROS, there is no strict requirement as the end-result will be the same.

??? tip "BGP State information"
    Next to the `origin-validation-state` in the `/state` tree, RIB entries also contain a reference to additional attributes associated to the BGP advertisement. To find the AS Path (to know which AS you could input into your script to have an impact) you will have to find the referenced attributes.

!!! tip "Easily see configuration changes"
    By opening a private candidate configuration session to the network element you are modifying, :material-router: PE1 in this case, you will be able to compare the private candidate to the running configuration at any time to quickly learn if there have been any modifications. There is even an indicator signaling when changes are present (`!`).

    Whenever the indicator is present, you can see the delta using

    ```text
    compare baseline running
    ```

    Using the `update` command you can pull changes from the `running` configuration into your `candidate` session.

??? example "Only if you get stuck: example implementation"
    For the example environment, prefix `208.192.0.0/10` shows up as not having any associated RPKI information available, evidenced by the `/state` entry being marked as `not-found` for the ROV result. A static entry will be created to override this to confirm the script works.

    Situation before:
    ```text hl_lines="4 17"
    2026-05-10T15:38:54.34+00:00
    [/]
    A:admin@g2-pe1# info /state router bgp rib ipv4-unicast local-rib routes 208.192.0.0/10 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0
        attr-id 8020
        peer-router-id 10.46.4.51
        last-modified-date 2026-05-09T22:04:46.6+00:00
        used-route true
        valid-route true
        best-route true
        backup-route false
        group-best false
        sticky-ecmp false
        stale-route false
        unused-weight-only false
        long-live-gr-stale false
        rtm-install-disabled false
        origin-validation-state not-found
        rib-priority normal
        leakable-route false
        leaked-route false
        in-rtm true
        invalid-reason {
            rejected-route false
            as-loop false
            next-hop-unresolved false
            cluster-loop false
            d-path-loop false
        }
    ```

    As you can see from the output above, the related attribute set is identified by the number `8020`. These attributes can be found in the following model path:

    ```
    /nokia-state:state/router=Base/bgp/rib/attr-sets
    ```

    For this route and that attribute set, you may find the following:

    ```text hl_lines="20"
    2026-05-10T15:40:11.01+00:00
    [/]
    A:admin@g2-pe1# info /state router bgp rib attr-sets attr-set rib-in index 8020
        origin igp
        next-hop 10.64.54.0
        med 0
        as-path {
            segment 1 {
                type as-sequence
                as-numbers 1 {
                    as-number 64599
                }
                as-numbers 2 {
                    as-number 852
                }
                as-numbers 3 {
                    as-number 3257
                }
                as-numbers 4 {
                    as-number 701
                }
            }
        }
    ```

    This shows us that the original AS for this prefix is `701`, this information is needed when configuring a static VRP.

    /// tab | Updated script `rpki.py`
    ``` python
    import argparse
    from pysros.management import connect


    def static_origin_entry(connection, asn, prefix, prefix_len):
        path = '/nokia-conf:configure/router[router-name="Base"]/origin-validation/static-entry'
        payload = {}
        payload[prefix + "/" + prefix_len, int(prefix_len), int(asn)] = {
            "ip-prefix": prefix + "/" + prefix_len,
            "upto": int(prefix_len),
            "origin-as": int(asn),
            "valid": True,
        }
        connection.candidate.set(path, payload, commit=True)


    def getRPKIStats(connection, peer):
        data = connection.running.get(
            "/state/router[router-name='Base']/bgp/rib/ipv4-unicast/local-rib/routes",
        )
        result = {
            "valid": 0,
            "invalid": 0,
            "not-applicable": 0,
            "not-found": 0,
            "total": 0,
        }

        for route_key, route_data in data.items():
            if route_key[1] == peer:
                result["total"] += 1
                result[route_data["origin-validation-state"].data] += 1
        return result


    def main():
        parser = argparse.ArgumentParser(
            prog="RPKImon",
            description="Gather and show aggregate RPKI data",
            epilog="For the specified peer, display the count of the various ROV results and total number of routes.",
        )
        parser.add_argument("address")
        parser.add_argument("-pl", "--pfxlen", required=False, default=None)
        parser.add_argument("-as", "--asn", required=False, default=None)
        parser.add_argument("-n", "--node", default="clab-srexperts-pe1")
        parser.add_argument("-u", "--username", default="admin")

        args = parser.parse_args()
        connection = connect(
            host=args.node,
            username=args.username,
            hostkey_verify=False,
        )

        # differentiate between GET mode and SET mode by the arguments specified
        # provided: 1 (address->peer) in the GET case and 3 (address->prefix, pfxlen
        # and ASN) in the SET case
        if args.pfxlen is None and args.asn is None:
            print(getRPKIStats(connection, args.address))
        else:
            static_origin_entry(connection, args.asn, args.address, args.pfxlen)


    if __name__ == "__main__":
        main()
    ```
    ///
    /// tab | Execution (Linux VM, use pyexec for :material-router: PE1)
    ``` bash
    python rpki.py 10.64.54.0
    python rpki.py 208.192.0.0 --pfxlen 10 --asn 701
    python rpki.py 10.64.54.0
    ```
    ///
    /// tab | Execution Output
    ```python {.no-copy}
    nokia@2:~$ python rpki.py 10.64.54.0
    {'valid': 44, 'invalid': 0, 'not-applicable': 0, 'not-found': 48, 'total': 92}
    nokia@2:~$ python rpki.py 208.192.0.0 --pfxlen 10 --asn 701
    nokia@2:~$ python rpki.py 10.64.54.0
    {'valid': 45, 'invalid': 0, 'not-applicable': 0, 'not-found': 47, 'total': 92}
    ```
    ///
    /// tab | Resulting Configuration
    ``` text hl_lines="2"
    2026-05-10T15:56:19.69+00:00
    !(pr)[/]
    A:admin@g2-pe1# compare baseline running
        configure {
            router "Base" {
    +           origin-validation {
    +               static-entry 208.192.0.0/10 upto 10 origin-as 701 {
    +                   valid true
    +               }
    +           }
            }
        }
    ```
    ///

    After adding this entry, the prefix is considered valid:
    ``` text {.no-copy}
    2026-05-10T15:58:04.97+00:00
    [/]
    A:admin@g2-pe1# info /state router bgp rib ipv4-unicast local-rib routes 208.192.0.0/10 neighbor "10.64.54.0" owner bgp router-instance-origin 1 path-id 0 origin-validation-state
        origin-validation-state valid
    ```

## Summary

Congratulations!  If you have got this far you now have a firm grasp on how the reliability of BGP information used by your network can be guaranteed and managed. As time goes on more and more networks may begin using RPKI and you are now ready for it.

In this exercise you have:

- Verified RPKI and Origin Validation configuration
- Automated a way of keeping track of ROV coverage of prefixes you receive from a BGP peer
- Accounted for exceptional circumstances requiring bespoke configuration to override RPKI information
- Built automation to deal with the need for such bespoke configuration.

Well done!

If you're hungry for more have a go at another activity!  Perhaps try a topic that is new to you?

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>
