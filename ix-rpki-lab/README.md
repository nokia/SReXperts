# Secure 🔒 the Future 🔮: Automating and securing internet peering

This lab is an open invitation to explore next generation capabilities for BGP peering, with special focus on security and automation.
Taking advantage of the rare *syzygy* - alignment of planets in the universe - taking place at SRxPerts this week, we hope to
fuel the discussion on features and roadmap based on hands-on experience and feedback from our audience.

In short, we will be mimicking an IXP peering deployment at a site of your choosing, using virtual Nokia equipment.

**Platforms: SR Linux (focus) and SR OS**

**Grading: advanced**

## Task summary

1. [Emulating an IXP peering use case](#1-emulating-an-ixp-peering-use-case)
2. [Customizing an IXP peering use case for your situation](#2-customizing-an-ixp-peering-use-case-for-your-situation)
3. [Automated provisioning of peering IPs and prefix lists, including IPv6](#3-automated-provisioning-of-peering-ips-and-prefix-lists-including-ipv6)
4. [RPKI validation of prefixes using a custom agent](#4-rpki-validation-of-prefixes-using-a-custom-agent)
5. [Developing and testing custom agents](#5-developing-and-testing-custom-agents)

## Drawing

![image](https://github.com/hansthienpondt/SReXperts/assets/2031627/92c9aa75-079f-4173-92a6-ba1ad9a7921a)

## Deploying the lab

This lab consists of 2 topologies; for example, for the first one

```
sudo containerlab deploy -t topology.clab.yml --reconfigure
```

To access:

```
ssh admin@clab-IXP-Peering-sros (admin/admin)
```

```
ssh admin@clab-IXP-Peering-srlinux (admin/NokiaSrl1!)
```

## Tools needed  

| Role | Software |
| --- | --- |
| Lab Emulation | [containerlab](https://containerlab.dev/) |
| Ansible | [Automation framework](https://www.ansible.com/) |
| BGP filter generation | [bgpq4](https://github.com/bgp/bgpq4) |
| RPKI-to-Router protocol (RFC 6810, RFC 8210, RFC 8210bis) | [stayrtr](https://github.com/bgp/stayrtr) |

## Credentials & Access
Once the lab is deployed, you can access the network elements through the exposed network management interfaces. The connection can be made from a shell inside the VM where the lab is deployed or from the internet using the public IP address assigned to the VM.

For access from the shell, use the addresses presented by containerlab at the end of the deployment process or use the values from the lab file. You can always check which nodes are available by running `sudo containerlab inspect --all`.

If you wish to have direct external access from your machine, use the public IP address of the VM and the external port numbers as per the table below:

| Node   | Direct SSH           | gNMI       | NETCONF         | JSON-RPC          | User/Pass            |
| ------- | -------------------- | ---------- | ----------------- | -------------------- | ----------------- |
| sros    | `ssh admin@IP:52001` | `IP:52301` | `IP:52401` | n/a | `admin`:`admin` |
| srlinux | `ssh admin@IP:52002` | `IP:52302` | n/a | `http://IP:52102` | `admin`:`NokiaSrl1!` |

## Tasks

# 1. Emulating an IXP peering use case

The first topology [topology.clab.yml](./topology.clab.yml) emulates a [peering situation at AMS-IX](https://www.peeringdb.com/ix/26).
Filtering for 800G we find (potential) peers "T-Mobile Thuis" (AS 50266, IP 80.249.211.171) and "NovoServe BV" (AS 24875, IP 80.249.208.126) in
subnet 80.249.208.0/22.

Start this topology using

```
sudo clab deploy -t topology.clab.yml --reconfigure
```

and verify that route prefixes are being exchanged by logging into the SR Linux node:

```
ssh admin@clab-IXP-Peering-srlinux (password NokiaSrl1!)
/show network-instance default route-table all
/show network-instance default protocols bgp routes ipv4 summary
```

Note how the [topology file](./topology.clab.yml) is fully self-contained, including (hardcoded) router configuration in only 100 lines of YAML.
Specific releases of SR Linux or SR OS can be tested using different ```SROS_VERSION``` or ```SRLINUX_VERSION``` parameters (when launching the lab).
A similar approach can be used for validation of other basic use cases (like OSPF, IS-IS, BGP unnumbered, ...)

# 2. Customizing an IXP peering use case for your situation

The topology has parameters IP1, IP2 and AS1, AS2 for the respective peering IPs and AS numbers. Using [PeeringDB](https://www.peeringdb.com/) we can customize
this for your situation; for example, at "LINX LON1" IXP site you can find "(aq) networks" with AS 33920 and "01 Telecom (01T)" with AS 201933.

Determine an IXP site of interest, and pick 2 AS numbers and 2 corresponding peering IPv4s. Then destroy the lab (```sudo clab destroy -t topology.clab.yml```) and rebuild it using the new parameters:

```
sudo IP1=1.2.3.4 IP2=1.2.3.5 AS1=1234 AS2=5678 clab deploy -t topology.clab.yml --reconfigure
```

# 3. Automated provisioning of peering IPs and prefix lists, including IPv6

In the sample configuration only a single IPv4 prefix is announced for each peer (see e.g. [here](./topology.clab.yml#L53)). To better reflect reality, use
the provided [Ansible playbook](./setup_peering_bgpq4.yml) to provision the full IPv4/6 prefix lists for the given AS peers:

```
AS1=1234 AS2=5678 ansible-playbook ./setup_peering_bgpq4.yml -i hosts.yml
```

This playbook uses the [bgpq4](https://github.com/bgp/bgpq4) tool to generate prefix lists based on IRR database lookups, in SR Linux (-n2) format:

```
$ docker run -it --rm ghcr.io/bgp/bgpq4:latest -n2 -ldemo AS201933
/routing-policy
delete prefix-set "demo"
prefix-set "demo" {
    prefix 45.90.42.0/24 mask-length-range exact { }
    prefix 91.193.116.0/22 mask-length-range exact { }
    prefix 91.193.118.0/24 mask-length-range exact { }
}
```

This multi-vendor tool supports other formats as well, for example '-N' for SR OS classic CLI:

```
$ docker run -it --rm ghcr.io/bgp/bgpq4:latest -N -ldemo AS201933
configure router policy-options
begin
no prefix-list "demo"
prefix-list "demo"
    prefix 45.90.42.0/24 exact
    prefix 91.193.116.0/22 exact
    prefix 91.193.118.0/24 exact
exit
commit
```

To complete the IPv6 peering, configure the IPs on the SR OS side:

```
ssh admin@clab-IXP-Peering-sros (password: admin)
/configure global
/configure router "Base" interface "i1/1/c1/1" ipv6 address <xxxx> prefix-length 64
/configure router "Base" bgp neighbor "yyyy" group "ebgp" peer-as nnnnn
commit
```

To verify successfull peering:

```
/show router bgp summary
```

To add additional IPv4/6 prefixes to be announced:

```
/configure router "Base" static-routes route xxxx/64 route-type unicast blackhole admin-state enable
commit
```

Bonus: To explore automated SR OS provisioning, see [pysros/README.md](pysros/README.md)

# 4. RPKI validation of prefixes using a custom agent

In order to secure the Internet, many providers have adopted or are adopting RPKI([RFC6810](https://datatracker.ietf.org/doc/rfc6810/)) to implement more restrictive BGP policies. RPKI provides infrastructure and protocols to verify proper authorization of a given AS to announce a given prefix.

Nokia SR OS offers a native implementation of RPKI (see [NANOG67](https://archive.nanog.org/sites/default/files/GrHankins.pdf)), but SR Linux does not yet have this capability. In this exercise, we are going to add RPKI functionality using a custom Python agent.

1. Destroy the lab from the first 3 steps: ```sudo clab destroy -t topology.clab.yml```
2. Start the RPKI lab topology (substituting your parameters):
```sudo IP1=1.2.3.4 IP2=1.2.3.5 AS1=1234 AS2=5678 clab deploy -t rpki-topology.clab.yml --reconfigure```

To check RPKI origin validation on SR OS:

```
/show router bgp routes detail
```

```
A:admin@sros# /show router bgp routes detail
===============================================================================
 BGP Router ID:10.0.0.1         AS:50266       Local AS:50266      
===============================================================================
 Legend -
 Status codes  : u - used, s - suppressed, h - history, d - decayed, * - valid
                 l - leaked, x - stale, > - best, b - backup, p - purge
 Origin codes  : i - IGP, e - EGP, ? - incomplete

===============================================================================
BGP IPv4 Routes
===============================================================================
Original Attributes
 
Network        : 2.58.21.0/24
Nexthop        : 80.249.208.126
...
Neighbor-AS    : 24875
DB Orig Val    : Valid                  Final Orig Val : N/A
...
Last Modified  : 00h54m34s              
```

This can be verified manually at <https://rpki-validator.ripe.net/ui/2.58.21.0%2F24?validate-bgp=true>

In order to achieve something similar on the SR Linux side, enable the custom agent:

```
ssh admin@clab-IXP-Peering-with-RPKI-srlinux (password NokiaSrl1!)
enter candidate
/network-instance default protocols rpki admin-state enable rpki-server 192.168.121.106
commit stay
```

After about a minute or so, the agent should start populating a prefix list for each peer:

```
A:srlinux# baseline update  
--{ + candidate shared default }--[ routing-policy ]--
A:srlinux# info 
    prefix-set rpki-validated-50266 {
        prefix 5.132.0.0/17 mask-length-range exact {
        }
    }
    policy accept-all {
        default-action {
            policy-result accept
        }
    }
```

In the example above, the prefix 5.132.0.0/17 was validated against RPKI and AS 50266 was found to be an authorized origin (see <https://rpki-validator.ripe.net/ui/5.132.0.0%2F17?validate-bgp=true>).
Note how the max-length for that prefix is 24, so 'mask-length-range exact' is a little too restrictive.

Note the ```baseline update``` command which refreshes the CLI's view of the config - this is required to see changes made by the agent in the background. Alternatively, logging out/in of the CLI would refresh things too.

To take the above prefix list into account, BGP policies will have to be adjusted. Take a look at [the user guide](https://documentation.nokia.com/srlinux/22-6/SR_Linux_Book_Files/Configuration_Basics_Guide/configb-routing_policies.html) and see if you can figure out how to reject or de-prioritize routes that are not valid.

If you were asked to assess the impact of enabling RPKI, could you tell what percentage of customer routes would be affected?
Create a custom 'show rpki impact' alias command to illustrate:

```
environment alias "show rpki impact" "..."
```

# 5. Developing and testing custom agents

The source code for the RPKI agent can be found in ```srl-rpki-agent-to-modify.py```, it is mounted under ```/opt/demo-agents/rpki-agent/srl-rpki-agent.py```
The complete GitHub project can be found [here](https://github.com/jbemmel/srl-rpki-agent)

After editing its contents (e.g. using VS code), restart the agent using
```tools /system app-management application srl_rpki_agent restart```

The debug output can be found at ```/var/log/srlinux/stdout/srl_rpki_agent.log``` (enter ```bash``` to get a shell)

This sample agent uses [pyGNMI](https://github.com/akarneliuk/pygnmi) to subscribe to changes in routes, triggering a RPKI lookup
