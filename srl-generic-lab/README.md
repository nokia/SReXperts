# Nokia SR Linux Generic Lab

Welcome to the generic SR Linux lab, where you can learn and experience Nokia's SR Linux network operating system.

In this lab, you do the following:

- Deploy the pre-configured SR Linux fabric (Leaf-Spine) and workloads (Alpine hosts) with containerlab.
- Explore the underlay routing with eBGP and a typical BGP EVPN setup with Route Reflectors.
- Examine the IP-VRF and MAC-VRF network instances, VXLAN tunnels, and IRB interfaces.
- Verify VXLAN datapath by pinging between the hosts.
- And discover everything you want to know about SR Linux...

**Difficulty:** Beginner

## Topology

The lab represents a 2-Tier Clos data center fabric topology with four hosts.

The Leaf and Spine nodes are running containerized Nokia SR Linux (7220 IXR D3L) NOS and the hosts are based on Alpine Linux.

Topology diagram:

![pic](https://github.com/hansthienpondt/SReXperts/assets/17744051/1724972b-395c-470b-8f8c-1356e4afe914)

Every node in the data center fabric is configured with eBGP as an underlay routing protocol. iBGP EVPN used to setup overlay ip-vrf and mac-vrf services.

Hosts are connected to the respective overlay services as per the diagram below:

![image](https://github.com/hansthienpondt/SReXperts/assets/17744051/a7088c77-f7af-409d-acbe-f87341f1e802)

## Deploying the lab

Deploy the topology with containerlab.

```
sudo containerlab deploy -c -t srl-generic.clab.yml
```

## Tools needed

| Role          | Software                                  |
| ------------- | ----------------------------------------- |
| Lab Emulation | [containerlab](https://containerlab.dev/) |

## Credentials & Access

Once the lab is deployed, you can access the network elements through the exposed network management interfaces. The connection can be made from the VM where the lab is deployed or from the internet using the public IP address assigned to the VM.

For access via a VM, use the addresses presented by containerlab at the end of the deployment process or use the values from the lab file. You can always refresh yourself on which nodes are available by running `sudo containerlab inspect --all`.

If you wish to have direct external access from your machine, use the public IP address of the VM and the external port numbers as per the table below:

| Node   | Direct SSH           | gNMI       | JSON-RPC          | User/Pass            |
| ------ | -------------------- | ---------- | ----------------- | -------------------- |
| spine1 | `ssh admin@IP:51001` | `IP:51301` | `http://IP:51101` | `admin`:`NokiaSrl1!` |
| spine2 | `ssh admin@IP:51002` | `IP:51302` | `http://IP:51102` | `admin`:`NokiaSrl1!` |
| leaf1  | `ssh admin@IP:51003` | `IP:51303` | `http://IP:51103` | `admin`:`NokiaSrl1!` |
| leaf2  | `ssh admin@IP:51004` | `IP:51304` | `http://IP:51104` | `admin`:`NokiaSrl1!` |
| leaf3  | `ssh admin@IP:51005` | `IP:51305` | `http://IP:51105` | `admin`:`NokiaSrl1!` |
| leaf4  | `ssh admin@IP:51006` | `IP:51306` | `http://IP:51106` | `admin`:`NokiaSrl1!` |
| h1     | `ssh root@IP:51007`  |            |                   | `root`:`clab`        |
| h2     | `ssh root@IP:51008`  |            |                   | `root`:`clab`        |
| h3     | `ssh root@IP:51009`  |            |                   | `root`:`clab`        |
| h4     | `ssh root@IP:51010`  |            |                   | `root`:`clab`        |

> If you prefer to connect nodes from the lab VM use default port numbers of the protocols.

Optionally, you may source the `srl-generic.rc` file to create convenient bash aliases to access nodes in a quick way; e.g. `l1` instead of `ssh admin@clab-srl-generic-leaf1`

## Exploring SR Linux

### Explore the underlay configuration

The eBGP is configured on the inter-switch links between Spine and Leaf routers.

![pic](https://github.com/hansthienpondt/SReXperts/assets/17744051/c5ef8017-b902-4cb9-aa83-82cdd2b0e899)

Connect to nodes and check the inter-switch links, eBGP sessions, AS numbers of Leaf and Spine, underlay network reachability between nodes by pinging the system IP addresses.

A list of useful show commands:

- `show interface brief`
- `show interface ethernet-1/3*`
- `show network-instance default route-table all`
- `show network-instance default protocols bgp neighbor`
- `show network-instance default protocols bgp neighbor 100.64.1.1 advertised-routes ipv4`
- `show network-instance default protocols bgp neighbor 100.64.1.1 received-routes ipv4`

`info` commands to see the configurations:

- `info interface ethernet-1/3*`
- `info network-instance default`

And the state information:

- `info from state interface ethernet-1/31 subinterface 1 statistics`
- `info from state network-instance default protocols bgp neighbor * received-messages`

### iBGP EVPN as Network Virtualization Overlay

EVPN use MP-BGP as control plane protocol between the tunnel endpoints. Typically, route-reflectors(RRs) are configured for the scalability. In this lab, spine routers are configured as RRs. All the leaf routers are peering with the spine routers for iBGP EVPN routes.

![pic](https://github.com/hansthienpondt/SReXperts/assets/17744051/4931dbd1-1e40-4c6d-b805-3b03dc86a240)

Connect to the nodes and check RR configuration on spines, iBGP EVPN sessions across the data center fabric.

Some useful commands:

- `show network-instance default protocols bgp neighbor 10.0.0.5 advertised-routes evpn`
- `show network-instance default protocols bgp neighbor 10.0.0.5  received-routes evpn`
- `info network-instance default protocols bgp group ibgp-evpn`
- `info from state network-instance default protocols bgp neighbor 10.0.0.5 peer-type`

### MAC-VRFs & IP-VRFs with EVPN

MAC-VRFs are layer 2 EVPN instances usually mapped to a single broadcast domain and forward based on the mac-table.
IP-VRFs are layer 3 instances with IP routing tables and they can be binded with MAC-VRFs with IRB interfaces.

Connect to the SR Linux nodes to check the EVPN service building blocks; IP-VRF and MAC-VRF configurations, VXLAN tunnel and IRB interfaces.

Look again at the overlay topology for this part:

![pic](https://github.com/hansthienpondt/SReXperts/assets/17744051/d5a3661c-e1af-4526-adf3-5226d377a994)

Some useful commands:

- `info network-instance ip-vrf-1`
- `info from state network-instance mac-vrf-1 protocols`
- `show network-instance mac-vrf-1 bridge-table mac-table all`
- `show network-instance ip-vrf-1 route-table all`
- `info tunnel-interface vxlan1 vxlan-interface *`
- `show tunnel-interface vxlan1 vxlan-interface * detail`
- `info interface irb1`
- `info interface ethernet-1/1*`
- `show network-instance default protocols bgp routes evpn route-type summary`

### Ping between hosts

Connect to the hosts and `ping` from:

- **h1 to h4** *(ping goes over mac-vrf-1)*
- **h1 to eth1 of h3** *(ping goes over ip-vrf-1)*
- **h2 to eth2 of h3** *(ping goes over ip-vrf-2)*
- **h3 to 100.100.100.100** *(ping an address on ip-vrf-1 and ip-vrf-2)*

Check the mac/ip table entries and EVPN route advertisements on the related SR Linux nodes with:

- `show network-instance mac-vrf-1 bridge-table mac-table mac`
- `show network-instance ip-vrf-1 route-table all`
- `show network-instance default protocols bgp neighbor 10.0.0.5  received-routes evpn`
- `show network-instance default protocols bgp routes evpn route-type summary`
- `show network-instance default protocols bgp routes evpn route-type 2 detail`
- `show network-instance default tunnel-table ipv4`
- `show tunnel-interface vxlan1 vxlan-interface * detail`
- `info from state tunnel vxlan-tunnel vtep * statistics`
