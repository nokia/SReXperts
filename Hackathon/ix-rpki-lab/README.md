# Secure 🔒 the Future 🔮: Automating and securing internet peering

This lab is an open invitation to explore next-generation capabilities for BGP peering, with a special focus on security and automation. We will be mimicking an IXP peering deployment at a site of your choosing, using virtual Nokia equipment.

**Platforms: SR Linux (focus) and SR OS**

**Grading: advanced**

## Task summary

1. [Emulating an IXP peering use case](#1-emulating-an-ixp-peering-use-case)
2. [Customizing an IXP peering use case for your situation](#2-customizing-an-ixp-peering-use-case-for-your-situation)
3. [Automated provisioning of peering IPs and prefix lists, including IPv6](#3-automated-provisioning-of-peering-ips-and-prefix-lists-including-ipv6)
4. [RPKI validation of prefixes using a custom agent](#4-rpki-validation-of-prefixes-using-a-custom-agent)
5. [Developing and testing custom agents](#5-developing-and-testing-custom-agents)

## Topologies

This lab has two topology files:

* [topology.clab.yml](topology.clab.yml) that is used for the basic IXP use cases outlined in the first 3 tasks of this lab
* [rpki-topology.clab.yml](rpki-topology.clab.yml) that is designed to showcase automated RPKI validation of BGP routes using custom agents.

Both topologies consist of the same set of components:

* Emulated IXP network represented by a Linux bridge `ixp-net`.
* Nokia SR Linux node representing an IXP member.
* Nokia SR OS node representing another IXP member.

![image](https://gitlab.com/rdodin/pics/-/wikis/uploads/8c5c43f98c7328d08db0baa743b3e684/image.png)

## Tools needed

The following tools and frameworks are used in the lab and are available on the lab VM:

| Role                                                      | Software                                  |
| --------------------------------------------------------- | ----------------------------------------- |
| Lab Emulation                                             | [containerlab](https://containerlab.dev/) |
| Automation Framework                                      | [Ansible](https://www.ansible.com/)       |
| BGP filter generation                                     | [bgpq4](https://github.com/bgp/bgpq4)     |
| RPKI-to-Router protocol (RFC 6810, RFC 8210, RFC 8210bis) | [stayrtr](https://github.com/bgp/stayrtr) |

## Credentials & Access

Once the lab is deployed, you can access the network elements either from within the VM or via Internet.

### Accessing the lab from within the VM

To access the lab nodes from within the VM, users should identify the names of the deployed nodes using `sudo containerlab inspect` command:

```bash
sudo containerlab inspect -t topology.clab.yml
INFO[0000] Parsing & checking topology file: topology.clab.yml
+---+--------------------------+--------------+------------------------------+---------------+---------+--------------------+--------------+
| # |           Name           | Container ID |            Image             |     Kind      |  State  |    IPv4 Address    | IPv6 Address |
+---+--------------------------+--------------+------------------------------+---------------+---------+--------------------+--------------+
| 1 | clab-IXP-Peering-srlinux | 5aa1a28ea8ca | ghcr.io/nokia/srlinux:23.7.1 | nokia_srlinux | running | 192.168.121.103/24 | N/A          |
| 2 | clab-IXP-Peering-sros    | 40c7cfe25a8b | vr-sros:23.7.R1              | vr-nokia_sros | running | 192.168.121.102/24 | N/A          |
+---+--------------------------+--------------+------------------------------+---------------+---------+--------------------+--------------+
```

Using the names from the above output, we can login to the SR Linux node using the following command:

```bash
ssh admin@clab-IXP-Peering-srlinux
```

### Accessing the lab via Internet

To access the lab nodes via Internet you should use the DNS name of the assigned VM and the external ports assigned to each node.

To list external ports run `show-ports` command on the lab VM:

```bash
Name                            Forwarded Ports
clab-IXP-Peering-srlinux        50174 -> 22, 50172 -> 80, 50170 -> 57400
clab-IXP-Peering-sros           50175 -> 22, 50173 -> 830, 50171 -> 57400
```

The following table shows internal ports used in this lab and is meant to help you find the correct exposed port for the services.

| Service | Internal Port number |
| ------- | -------------------- |
| SSH     | 22                   |
| HTTP    | 80                   |
| gNMI    | 57400                |

Using the above information, you can connect to the SR Linux node with SSH using the following command:

```bash
# where X is the Group ID assigned to you
ssh admin@X.srexperts.net -p 50174
```

## Tasks

### 1. Emulating an IXP peering use case

The first topology [topology.clab.yml](./topology.clab.yml) emulates a [peering situation at AMS-IX](https://www.peeringdb.com/ix/26).

Filtering for 800G members we find (potential) peers "T-Mobile Thuis" (AS 50266, IP 80.249.211.171) and "NovoServe BV" (AS 24875, IP 80.249.208.126) in the peering subnet 80.249.208.0/22. Let's take these as an example for our peering use case.

T-Mobile Thuis peering member will be running SR Linux, NovoServe BV will be running SR OS. Both will connect to the peering LAN using their respective first interfaces.

With this input the topology takes the following shape:

![image](https://gitlab.com/rdodin/pics/-/wikis/uploads/7283efe114fdac3443cc1e40b6978cc3/image.png)

Start this topology using:

```bash
cd ix-rpki-lab
sudo -E clab deploy -c -t topology.clab.yml
```

The lab deployment will take a few minutes to deploy; the nodes will boot and apply the configuration that is captured in the self-contained [topology.clab.yml](./topology.clab.yml) file.

We can verify that the config captured in `startup-config` of the topology file is successfully applied by logging to the nodes and checking that the static routes configured on both routers are exchanged via the BGP peering session:

```bash
# login performed from the lab VM
# SR Linux admin password: NokiaSrl1!
ssh admin@clab-IXP-Peering-srlinux
```

Once logged in, we can check the route table on the SR Linux side, which should have the static route from the remote SR OS peer:

```bash
/show network-instance default route-table all
/show network-instance default protocols bgp routes ipv4 summary
```

Pings to any IP address from the received network would fail, since we have no end systems connected and use the blackhole next-hop for the static route.

### 2. Customizing an IXP peering use case for your situation

The routers' configuration captured in the topology file can be parametrized by leveraging the env variables injected in their configuration blobs.

A closer look at config blobs inside the topology.clab.yml file reveals the following variables and their default values:

* `IP1`, `IP2` - IP addresses assigned to the IXP-LAN interfaces of the SR Linux and SR OS nodes respectively.
* `AS1`, `AS2` - AS numbers used in the BGP peering session.
* `PFX1`, `PFX2` - for sample prefixes used in the peering session.

Using containerlab's ability to [inject environment variables](https://containerlab.dev/manual/topo-def-file/#environment-variables) into the configuration blobs, we can customize the peering lab for our situation without touching the core of the lab topology.

The whole process of customizing the peering boils down to the following three steps:

1. Determine an IXP site of interest (e.g. LINX LON1)
2. Pick 2 AS numbers and 2 corresponding peering IPv4 addresses for peers at that site
3. Use `bgpq4` or bgp.tools to lookup a sample prefix advertised by each AS

For example, let's transform our lab to use ["LINX LON1"](https://www.peeringdb.com/ix/18) IXP site with ["NEAR IP" AS 49600](https://bgp.tools/as/49600) and "01 Telecom (01T)" AS 201933 peering members.

To identify IPv4 addresses used by these members we use PeeringDB where we can find that:

* NEAR IP uses 195.66.224.63 IP address
* 01 Telecom uses 195.66.227.214 IP address

As per PeeringDB peering LAN of [LINX LON1](https://www.peeringdb.com/ix/18) is 195.66.224.0/21.

Now put [bgpq4](https://github.com/bgp/bgpq4) tool to work to find a sample prefix for each AS:

```bash
# grep any prefix from the output
# the -n2 option generates a prefix list in SR Linux format
docker run -it --rm ghcr.io/bgp/bgpq4:latest -n2 AS49600
```

Now that we have all the required parameters, we can set the following environment variables and redeploy the lab

```bash
export IP1=195.66.224.63
export IP2=195.66.227.214
export AS1=49600
export AS2=201933
export PFX1=45.141.242.0/24
export PFX2=45.90.42.0/24

sudo -E clab deploy -c -t topology.clab.yml
```

Using the show commands from task #1 you should see the BGP peering established and the static routes exchanged.

### 3. Automated provisioning of peering IPs and prefix lists, including IPv6

In the previous tasks we only configured a single IPv4 prefix that is announced for each peer (see e.g. [here](./topology.clab.yml#L53)). To better reflect reality, use
the provided [Ansible playbook](./setup_peering_bgpq4.yml) to provision the full IPv4/6 prefix lists for the given AS peers:

```bash
# Assumes environment variables AS1/AS2 are set as before, IP addresses are looked up automatically
export IXP="LINX LON1"
ansible-playbook ./setup_peering_bgpq4.yml -i hosts.yml
```

This playbook uses PeeringDB API and the [bgpq4](https://github.com/bgp/bgpq4) tool to get infromation about the peers and generate prefix lists based on IRR database lookups:

```bash
# generating prefix set named "demo" for AS201933 in SR Linux format (-n2 flag)
$ docker run -it --rm ghcr.io/bgp/bgpq4:latest -n2 -l demo AS201933
/routing-policy
delete prefix-set "demo"
prefix-set "demo" {
    prefix 45.90.42.0/24 mask-length-range exact { }
    prefix 91.193.116.0/22 mask-length-range exact { }
    prefix 91.193.118.0/24 mask-length-range exact { }
}
```

This multi-vendor tool supports other formats as well, for example '-N' for SR OS classic CLI:

```bash
$ docker run -it --rm ghcr.io/bgp/bgpq4:latest -N -l demo AS201933
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

The Ansible playbook that we just executed provisions the peering only on SR Linux side; To complete the IPv6 peering, configure the IPs for IPv6 on the SR OS side:

See what got configured on the SR Linux side:

```bash
docker exec clab-IXP-Peering-srlinux sr_cli 'info from running /interface ethernet-1/1 subinterface 0'
docker exec clab-IXP-Peering-srlinux sr_cli 'info from running /network-instance default protocols bgp neighbor *'
```

Then configure those IPv6 addresses on SR OS side, in reverse:

```bash
# SR OS credentials admin:admin
ssh admin@clab-IXP-Peering-sros
# once logged in, enter configuration mode
[/]
A:admin@sros# edit-config exclusive

/configure router "Base" interface "i1/1/c1/1" ipv6 address 2001:7f8:4::c1c0:1 prefix-length 64
/configure router "Base" bgp neighbor "2001:7f8:4::3:14cd:1" group "ebgp" peer-as 201933
/configure router "Base" bgp neighbor "2001:7f8:4::3:14cd:1" family ipv6 true
commit
```

To verify successful peering:

```
/show router bgp summary
```

To add additional IPv4/6 prefixes to be announced (tip: you can use `-6` with bgpq4 to list IPv6 prefixes):

```
/configure router "Base" static-routes route 2a06:40c0::/29 route-type unicast blackhole admin-state enable generate-icmp true
commit
```

Bonus: To explore automated SR OS provisioning, see [pysros/README.md](pysros/README.md)

### 4. RPKI validation of prefixes using a custom agent

In order to secure the Internet, many providers have adopted or are adopting RPKI([RFC6810](https://datatracker.ietf.org/doc/rfc6810/)) to implement more restrictive BGP policies. RPKI provides infrastructure and protocols to verify the proper authorization of a given AS to announce a given prefix.

Nokia SR OS offers a native implementation of RPKI (see [NANOG67](https://archive.nanog.org/sites/default/files/GrHankins.pdf)), but SR Linux does not yet have this capability. In this exercise, we are going to add RPKI functionality using a custom Python agent.

1. Destroy the lab from the first 3 steps: `sudo clab destroy -c -t topology.clab.yml`
2. Start the RPKI lab topology (substituting your parameters):
    `sudo IP1=1.2.3.4 IP2=1.2.3.5 AS1=1234 AS2=5678 clab deploy -c -t rpki-topology.clab.yml`

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

```bash
# SR Linux credentials admin:NokiaSrl1!
ssh admin@clab-IXP-Peering-with-RPKI-srlinux
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

Note the `baseline update` command which refreshes the CLI's view of the config - this is required to see changes made by the agent in the background. Alternatively, logging out/in of the CLI would refresh things too.

To take the above prefix list into account, BGP policies will have to be adjusted. Take a look at [the user guide](https://documentation.nokia.com/srlinux/23-7/books/routing-protocols/rout-policies.html) and see if you can figure out how to reject or de-prioritize routes that are not valid.

If you were asked to assess the impact of enabling RPKI, could you tell what percentage of customer routes would be affected?
Create a custom 'show rpki impact' alias command to illustrate:

```
environment alias "show rpki impact" "..."
```

Hint: Using 'jq' and 'wc' one could count the number of attribute sets with local-pref equal to 100:
```
info from state /network-instance default bgp-rib attr-sets | as json | jq ".. | objects | select(.[\"local-pref\"]==100?) | .[\"next-hop\"]" | wc -l
```

Hint: Though 'awk' is not currently available for piping in the CLI, an AWK program like
```
awk "$0~/99/ {count++} END {printf(\"%.2f%%\n\", 100*count/NR)}" input.txt
```
would print the percentage of lines containing '99'. 
Available piping options are defined in `/opt/srlinux/python/virtual-env/lib/python3.6/site-packages/srlinux/mgmt/cli/plugins/bash_output_modifiers.py`

To copy that file to the VM:
```
docker cp clab-IXP-Peering-with-RPKI-srlinux:/opt/srlinux/python/virtual-env/lib/python3.6/site-packages/srlinux/mgmt/cli/plugins/bash_output_modifiers.py .
```

To add 'awk' (copied from 'jq'):
```
def load():
...
    add_bash_output_modifier(cli, get_awk_syntax(), accepted_return_codes=standard_accepted_return_codes)
...

def get_awk_syntax():
    syntax = Syntax('awk',help=dedent('Process the output using awk.'))
    syntax.add_unnamed_argument('args', help='arguments passed on to awk', min_count=0, max_count='*')
    return syntax
```

To mount an edited version, in rpki-topology.clab.yml:
```
...
binds:
  # Make agent source code editable from outside
  - srl-rpki-agent-to-modify.py:/opt/demo-agents/rpki-agent/srl-rpki-agent.py
  # Load customized CLI pipe options
  - bash_output_modifiers.py:/opt/srlinux/python/virtual-env/lib/python3.6/site-packages/srlinux/mgmt/cli/plugins/bash_output_modifiers.py
```

Hence:
```
A:srlinux# info from state /network-instance default bgp-rib attr-sets | awk "$0~/100/ {count++} END {printf(\"%.2f%%\n\", 100*count/NR)}" 
7.56%
```

### 5. Developing and testing custom agents

The source code for the RPKI agent can be found in `srl-rpki-agent-to-modify.py`, it is mounted under `/opt/demo-agents/rpki-agent/srl-rpki-agent.py`. The complete GitHub project can be found [here](https://github.com/jbemmel/srl-rpki-agent)

After editing its contents (e.g. using VS code), restart the agent using

```
tools /system app-management application srl_rpki_agent restart
```

The debug output can be found at `/var/log/srlinux/stdout/srl_rpki_agent.log` (enter `bash` to get a shell)

This sample agent uses [pyGNMI](https://github.com/akarneliuk/pygnmi) to subscribe to changes in routes, triggering a RPKI lookup.
