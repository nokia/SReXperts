---
tags:
  - SR Linux
  - gNMIc
  - Prometheus
  - Grafana
---

# SR Linux streaming telemetry


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | SR Linux streaming telemetry                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Activity ID**           | 53                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Short Description**       | SR Linux integration in a streaming telemetry stack with gNMIc, Prometheus and Grafana </p>                                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [gNMIc](https://gnmic.openconfig.net/)<br/>[Prometheus](https://prometheus.io/) <br/> [Grafana](https://grafana.com/docs/grafana/latest/)<br/>[Nokia YANG browser](https://yangbrowser.nokia.com/srlinux/26.3.1?from=0)                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Topology Nodes**          |  :material-router: Leaf21, :material-router: Spine21                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **References**              | [SR Linux documentation](https://documentation.nokia.com/srlinux/26-3/index.html)<br/>  [SR Linux gRPC server](https://documentation.nokia.com/srlinux/26-3/books/config-basics/management-servers.html#ariaid-title3)<br/> |

You are a Network Engineer working on a project to deploy a new data-center with SR Linux nodes. You have already installed, configured and integrated the IP fabric into the existing network, and the next step before it's ready for production is to integrate the nodes into the management systems.  

You have been asked to configure and integrate the nodes into the streaming telemetry stack comprising of gNMIc, Prometheus and Grafana.  

## Objective
The objective is to deploy streaming telemetry from the SR Linux nodes through the monitoring stack and understand the benefits of this modern approach to network monitoring.  

Before you start you will need to get familiar with streaming telemetry on SR Linux by making use of gNMI (gRPC Network Management Interface) to retrieve data from the nodes using a gNMI client tool called [`gnmic`](https://gnmic.openconfig.net/). You will learn the building blocks, the advantages of telemetry and how the monitoring stack works by collecting additional data and visualizing this data in Grafana. In particular you will look at:  

- The differences between SNMP and streaming telemetry
- How to identify and subscribe to streaming telemetry metrics
- How the components of the telemetry monitoring stack work together
- How to configure and enable streaming telemetry using gNMI over gRPC on SR Linux
- How to create visualizations of the metrics you receive in Grafana

## Technology explanation

Today's networks require reliable monitoring in the WAN, Edge, and data center domains, emphasizing real-time data collection and transmission for network visibility.
Streaming telemetry is the comprehensive practice of transmitting measurements from various network devices in real time to a collector for storage and further processing, ultimately creating a monitoring and reporting system.

A streaming telemetry monitoring stack typically consists of:

- A telemetry collector (for example, in this activity we will use [gNMIc](https://gnmic.openconfig.net/)) to retrieve the metrics from the network elements
- A time-series database (TSDB) (for example, in this activity we will use [Prometheus](https://prometheus.io/)) to collect, store and aggregate the collected metrics.
- A visualization tool (for example, in this activity we will use [Grafana](https://grafana.com/docs/grafana/latest/)) to visualize the collected data and run queries on top of it

gNMI is a modern gRPC-based network management interface that is currently the most popular protocol to collect streaming telemetry data from networking devices. It is important to understand, that Streaming Telemetry with gNMI operates on the configuration and state data streamed from the network devices, but it does not provide flow extraction/sampling like NetFlow/IPFIX.

### Streaming telemetry vs. SNMP

The alternative to streaming telemetry data is the widely used SNMP (Simple Network Management Protocol) a pull-based model where the monitoring system periodically requests data from network devices. This method can cause delays in detecting issues and consumes considerable resources on both the monitored device and the monitoring system.

In contrast, streaming telemetry’s push-based approach allows network devices to stream data continuously and automatically to a centralized location. This approach enables near real-time network data collection, significantly improving the visibility and responsiveness of network monitoring. 

### What is gNMI

[gRPC Network Management Interface (gNMI)](https://www.openconfig.net/docs/gnmi/gnmi-specification/) is a protocol to manage and report a network element’s configuration and operational data. gNMI is built on top of Google’s widely deployed gRPC protocol. gRPC provides protocol buffers (protobufs), a language neutral mechanism to transport structured data efficiently over networks making it an ideal method for streaming operational data from network elements.

There are 4 remote procedure calls (RPC) services defined by the gNMI specification which are supported by SR Linux:  

* **Capabilities** - Provides the client with information about the device, such as gNMI version, used data models and supported encodings. Frequently used to test the gNMI connection.  
* **Get** - Retrieve information from the device, typically small amount of data.  
* **Set** - Is used to set, modify or delete configuration on a network device.  
* **Subscribe** - Used for streaming telemetry - receiving a stream of state or configuration data from the device. The `subscribe` RPC supports different modes: In a `sample` mode, the data is returned with a cadence governed by a client-provided interval; in an `on_change` mode data is streamed every time there is a change in the subscribed data elements.  

### `gnmic` as a command line interface to gNMI

[`gnmic`](https://gnmic.openconfig.net/) is a command line tool developed by Nokia and donated to the [OpenConfig](https://www.openconfig.net/) project. It lets you interact with the gNMI server running on the SR Linux nodes. It can be used to run the various RPCs we discussed above against SR Linux. It has been pre-installed on your hackathon instance although you may install it locally if you'd prefer (follow the [installation instructions](https://gnmic.openconfig.net/install/) if you would like to do this (it is not necessary to complete this activity)). 

Log into your lab server and run `gnmic` command with the `--help` parameter. Take a look at the available commands this tool offers. You should recognize the 4 gNMI RPCs: Capabilities, Get, Set, and Subscribe.

> Note, that the `gnmic` CLI tool is already installed on your hackathon instance.

/// details | Output: `gnmic --help`
    type: output
```bash
$ gnmic --help
run gnmi rpcs from the terminal (https://gnmic.openconfig.net)

Usage:
  gnmic [command]

Available Commands:
  capabilities query targets gnmi capabilities
  get          run gnmi get on targets
  help         Help about any command
  ...          ...
  set          run gnmi set on targets
  subscribe    subscribe to gnmi updates on targets
  version      show gnmic version

```
///

### Identify the gNMI path to subscribe to

The next step is fetching or subscribing to data from SR Linux. Since SR Linux is a fully YANG-modelled NOS, we need the identify the gNMI paths that point to the data we want to fetch. You can find these paths in the SR Linux CLI.

Open a second terminal where you log into :material-router: Leaf21.
/// details | SSH to :material-router: Leaf21
    type: info
    open: true
```bash
ssh admin@clab-srexperts-leaf21
```
///

Let's say you want to retrieve the `host-name` of this device. You can find the XPath by running the following command in SR Linux CLI
/// details | xpath system name
    type: example
    open: true

/// tab | Command
```bash
tree xpath system name
```
///

/// tab | Output: `tree xpath system name`
```bash
--{ running }--[  ]--
A:admin@g51-leaf21# tree xpath system name
/system/name
/system/name/domain-name:
/system/name/host-name:
```
///
///

From the output you can see that to retrieve the `host-name` you will need to use the following gNMI path (referenced here as an Xpath) `/system/name/host-name`.  CLI users who are well familiar with the SR Linux YANG model may use this approach, but in many cases you may not know where or what you are looking for.  
In this situation the [Nokia YANG browser](https://yangbrowser.nokia.com/srlinux/26.3.1?from=0) may be a good option to try.  
The YANG browser lets you do a search through the SR Linux YANG model. By simply typing for certain keywords (for example "host-name"), the YANG browser will return any matches found.


## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### gNMI get

You are trying to integrate your DC SR Linux nodes into the telemetry monitoring stack, however, before you start with the telemetry stack you need to learn how to stream metrics from SR Linux nodes.  
Start by testing `gnmic` connectivity. Use `gnmic` `capabilities` operation to fetch the capabilities or the `get` operation to fetch the `host-name` of :material-router: Leaf21 using the gNMI path you identified earlier. 




/// details | Tip: How to test `gnmic`
    type: tip

Use `gnmic --help` to get all the options or refer to the [`gnmic` web page](https://gnmic.openconfig.net/cmd/capabilities/) for instructions.

You will need to execute `gnmic` with:  

* hostname: clab-srexperts-leaf21  
* port: 57401  
* user: admin  
* password: $EVENT_PASSWORD  
* insecure: skip-verify  
* encoding: ascii or json_ietf (ascii for Human-readable or json_ietf for automation)
* request: `capabilities` or `get` the `hostname` path  

///

You'll need to have visibility over the **traffic-rate** of the interfaces. 
Find the gNMI path for the traffic-rate and run `gnmic` with the `get` operation again. You will notice that there is a match in the YANG browser for `ingress-bps` and `egress-bps`.


/// details | Tip: How to get the gNMI path (Xpath)?
    type: tip

Use the [YANG Browser](https://yangbrowser.nokia.com/srlinux/26.3.1?from=0) or use the CLI command below to find the xpath from within `state` mode.  
You can use `enter state` to move into `state` mode.  
/// tab | tree xpath
```bash
tree xpath from state / interface traffic-rate
```
///

/// tab | Output
```bash
--{ state }--[  ]--
A:admin@g51-leaf21# tree xpath /interface traffic-rate
/interface[name=*]/traffic-rate
/interface[name=*]/traffic-rate/in-bps:
/interface[name=*]/traffic-rate/out-bps:
```
///
///

/// details | Question: For which interface are you getting the traffic-rate values?
    type: question
If you don't specify the interface you will receive traffic rates for all interface available on the device. This is because we are matching all interfaces in the YANG path.  
Try to fetch the traffic-rate for interface `ethernet-1/31` only. 
///





/// details | If you are stuck, click here for a solution  
    type: solution


/// tab | `gnmic capabilities`

The command to retrieve the capabilities is:

```bash
gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD \
    --skip-verify -e json_ietf capabilities
```

Output:
```bash
$ gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD \
    --skip-verify -e json_ietf capabilities
gNMI version: 0.10.0
supported models:
  - urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring:ietf-netconf-monitoring, IETF NETCONF (Network Configuration) Working Group, 2010-10-04
  - urn:ietf:params:xml:ns:yang:ietf-yang-library:ietf-yang-library, IETF NETCONF (Network Configuration) Working Group, 2019-01-04
  - urn:nokia.com:srlinux:aaa:aaa:srl_nokia-aaa, Nokia, 2026-03-31
  - urn:nokia.com:srlinux:aaa:aaa-password:srl_nokia-aaa-password, Nokia, 2026-03-31
  - urn:nokia.com:srlinux:aaa:aaa-types:srl_nokia-aaa-types, Nokia, 2023-03-31
  - urn:nokia.com:srlinux:acl:acl:srl_nokia-acl, Nokia, 2026-03-31
  
<snippet>

  - http://openconfig.net/yang/vlan:openconfig-vlan, OpenConfig working group, 2023-02-07
supported encodings:
  - JSON_IETF
  - PROTO
  - ASCII
  - 52
  - 42
  - 43
  - 45
  - 44
  - 46
  - 47
  - 48
  - 49
  - 50
  - 53


```
///



/// tab | `gnmic get` for the `host-name`  

The command to retrieve the `host-name` is:

```bash
gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD \
    --skip-verify -e json_ietf get \
    --path /system/name/host-name
```

Output:
```bash
$ gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD --skip-verify -e json_ietf get \
--path /system/name/host-name
[
  {
    "source": "clab-srexperts-leaf21:57401",
    "timestamp": 1776852553304462822,
    "time": "2026-04-22T06:09:13.304462822-04:00",
    "updates": [
      {
        "Path": "srl_nokia-system:system/srl_nokia-system-name:name/host-name",
        "values": {
          "srl_nokia-system:system/srl_nokia-system-name:name/host-name": "g51-leaf21"
        }
      }
    ]
  }
]

```
///


/// tab | `gnmic get` for the `traffic-rate`

The command to retrieve the traffic-rate is:

```bash
gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD \
    --skip-verify -e json_ietf get \
    --path '/interface[name=*]/traffic-rate'
```

Output:

```bash
$ gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD --skip-verify -e json_ietf get \
--path '/interface[name=*]/traffic-rate'
[
  {
    "source": "clab-srexperts-leaf21:57401",
    "timestamp": 1776853507694583905,
    "time": "2026-04-22T06:25:07.694583905-04:00",
    "updates": [
      {
        "Path": "",
        "values": {
          "": {
            "srl_nokia-interfaces:interface": [
              {
                "name": "ethernet-1/1",
                "traffic-rate": {
                  "in-bps": "0",
                  "out-bps": "0"
                }
              },
              {
                "name": "ethernet-1/2",
                "traffic-rate": {
                  "in-bps": "0",
                  "out-bps": "0"
                }
              },
<snippet>
```
///

/// tab | `gnmic get` for the `traffic-rate` on `ethernet-1/31` only

The command to retrieve the `traffic-rate` for interface `ethernet-1/31` is:
```bash
gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD \
    --skip-verify -e json_ietf get \
    --path '/interface[name=ethernet-1/31]/traffic-rate'
```
Output:
```bash
$  gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD --skip-verify -e json_ietf get \
--path '/interface[name=ethernet-1/31]/traffic-rate'
[
  {
    "source": "clab-srexperts-leaf21:57401",
    "timestamp": 1776853570356331216,
    "time": "2026-04-22T06:26:10.356331216-04:00",
    "updates": [
      {
        "Path": "srl_nokia-interfaces:interface[name=ethernet-1/31]/traffic-rate",
        "values": {
          "srl_nokia-interfaces:interface/traffic-rate": {
            "in-bps": "221",
            "out-bps": "158"
          }
        }
      }
    ]
  }
]
```
///

///



### gNMI subscriptions

To collect telemetry data and create visualization dashboards you need continuously streaming data. This is done using the gNMI `subscribe` RPC.  
Instead of performing a gNMI `get`, use the `subscribe` RPC to stream the `traffic-rate` for interface `ethernet-1/31` every 5 seconds.


Use the `gnmic` command with the `subscribe` parameter.  You will also need to set the `stream-mode` to  `sample` and the `sample-interval` to `5` seconds. The `traffic-rate` should now display on your terminal every 5 seconds.


/// details | Solution: `gnmic subscribe` as a `sample` with a specific `sample-interval`
    type: solution

The command to subscribe is:
```bash
gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD --skip-verify -e json_ietf subscribe \
--stream-mode sample --sample-interval 5s \
--path '/interface[name=ethernet-1/31]/traffic-rate'

```
Output:
```bash
gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD --skip-verify -e json_ietf subscribe \
--stream-mode sample --sample-interval 5s \
--path '/interface[name=ethernet-1/31]/traffic-rate'
{
  "source": "clab-srexperts-leaf21:57401",
  "subscription-name": "default-1776859390",
  "timestamp": 1776859390882674691,
  "time": "2026-04-22T08:03:10.882674691-04:00",
  "updates": [
    {
      "Path": "srl_nokia-interfaces:interface[name=ethernet-1/31]/traffic-rate",
      "values": {
        "srl_nokia-interfaces:interface/traffic-rate": {
          "in-bps": "324",
          "out-bps": "326"
        }
      }
    }
  ]
}
{
  "sync-response": true
}
<update every 5 seconds>
}
```
///


Choosing a stream mode of `sample` is useful when you have fast changing data, but there are other cases where your operational data doesn't change frequently. Think about BGP neighborship states or interface operational states. It wouldn't be useful to receive their status every 5 seconds if it almost never changes. It would be much more efficient if we only receive an update when their state changes. For these cases you can use the on-change stream mode.

Search the [YANG browser](https://yangbrowser.nokia.com/srlinux/26.3.1?from=0) for the gNMI path corresponding to the `oper-state` of the `ethernet-1/32` interface.  

Adjust the stream mode to `on-change` and try to fetch the `oper-state` of the interface, then disable and re-enable the interface in the configuration (don't forget to commit your changes). You should notice that we only will receive an update when the operational state of interface `ethernet-1/32` changes.

/// details | Solution: `gnmic subscribe` using the `on-change` stream mode 
    type: solution

The command to subscribe is:
```bash
gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD --skip-verify -e json_ietf subscribe \
--stream-mode on-change \
--path '/interface[name=ethernet-1/32]/oper-state'
```
Output:
```bash
received signal 'interrupt'. terminating...
$ gnmic -a clab-srexperts-leaf21:57401 -u admin -p $EVENT_PASSWORD --skip-verify -e json_ietf subscribe \
--stream-mode on-change \
--path '/interface[name=ethernet-1/32]/oper-state'
{
  "source": "clab-srexperts-leaf21:57401",
  "subscription-name": "default-1776864133",
  "timestamp": 1776864133878651697,
  "time": "2026-04-22T09:22:13.878651697-04:00",
  "updates": [
    {
      "Path": "srl_nokia-interfaces:interface[name=ethernet-1/32]",
      "values": {
        "srl_nokia-interfaces:interface": {
          "oper-state": "up"
        }
      }
    }
  ]
}
{
  "sync-response": true
}
{
  "source": "clab-srexperts-leaf21:57401",
  "subscription-name": "default-1776864133",
  "timestamp": 1776864156401439327,
  "time": "2026-04-22T09:22:36.401439327-04:00",
  "updates": [
    {
      "Path": "srl_nokia-interfaces:interface[name=ethernet-1/32]",
      "values": {
        "srl_nokia-interfaces:interface": {
          "oper-state": "down"
        }
      }
    }
  ]
}
{
  "source": "clab-srexperts-leaf21:57401",
  "subscription-name": "default-1776864133",
  "timestamp": 1776864171327957343,
  "time": "2026-04-22T09:22:51.327957343-04:00",
  "updates": [
    {
      "Path": "srl_nokia-interfaces:interface[name=ethernet-1/32]",
      "values": {
        "srl_nokia-interfaces:interface": {
          "oper-state": "up"
        }
      }
    }
  ]
}

```
///



### Streaming telemetry using the telemetry monitoring stack

Now that you know how to stream metrics from SR Linux nodes, it's time to take it to the next level. Visualizing the data using a telemetry monitoring stack is crucial for understanding what is happening in your network in real-time. A telemetry monitoring stack typically consists of three elements:

1. A telemetry collector (We will use gNMIc)
2. A time series database (TSDB) (We will use Prometheus)
3. A visualization dashboard (We will use Grafana)

-{{image(url='./../../../../../images/53-SRL_Telemetry/gpg-stack.JPG', title='Fig. 1 - Streaming Telemetry Stack')}}-


Let's have a closer look at the telemetry stack components and try to understand what their roles are.

#### gNMIc

gNMIc is used to subscribe to the telemetry data from the fabric nodes and expose it to the Prometheus time-series database.

The gNMIc configuration file `config.yml`(file at `~/SReXperts/clab/configs/gnmic/config.yml`) is applied to the gNMIc container at startup. It instructs the container to subscribe to telemetry data and export it to the Prometheus time-series database. Examine the file to locate where the gNMI paths are described. You should also note Prometheus is defined as an output. 



/// details | Output: gNMIc `config-yml`
    type: output

You may find the configuration file at `~/SReXperts/clab/configs/gnmic/config.yml`.  
Find below an excerpt including the SR Linux subscriptions. 

/// tab | gNMIc `config.yml` 
```yaml
username: admin
password: ${GNMIC_PASSWORD}
port: 57400
timeout: 10s

loader:
  type: docker

  address: unix:///run/docker.sock
  filters:

    - containers:
        # containers returned by `docker ps -f "label=clab-node-kind=nokia_srlinux"`
        - label: clab-node-kind=nokia_srlinux
      network:
        # networks returned by `docker network ls -f "name=srexperts"`
        name: srexperts

      port: "57400"
      config:
        username: admin
        insecure: true
        encoding: proto
        subscriptions:
          - srl_platform
          - srl_apps
          - srl_if_stats
          - srl_if_lag_stats
          - srl_net_instance
          - srl_bgp_stats
          - srl_event_handler_stats

#<snippet>

subscriptions:
  srl_if_stats:
    paths:
      - /interface[name=ethernet-1/*]/statistics
      - /interface[name=*]/subinterface[index=*]/statistics/
      - /interface[name=ethernet-1/*]/oper-state
      - /interface[name=ethernet-1/*]/traffic-rate
    mode: stream
    stream-mode: sample
    sample-interval: 5s
#<snippet>

outputs:
  prom:
    type: prometheus
    listen: :9273
    path: /metrics
    export-timestamps: true
    strings-as-labels: true
    debug: false
    event-processors:
      - trim-sros-prefixes
      - add-labels
      - trim-regex
      - group-by-interface
      - up-down-map
#<snippet>

```
///
///


#### Prometheus

[Prometheus](https://prometheus.io) is a popular open-source time-series database (TSDB). It is used in this lab to scrape and store the telemetry data exposed by the telemetry collector (gNMIc) every 5 seconds. Metrics are stored with the timestamp (Time Series Data) at which they were recorded, alongside optional key-value pairs called labels.


/// details | Output: Prometheus configuration file `prometheus.yml`
    type: output

If you need to adjust the data that is scraped by Prometheus you have to edit the `prometheus.yml` file (file at ~/SReXperts/clab/configs/prometheus/prometheus.yml).

```yaml
global:
  scrape_interval: 5s

# metrics_path defaults to '/metrics'
# scheme defaults to 'http'.
scrape_configs:
  - job_name: "gnmic"
    static_configs:
      - targets: ["gnmic:9273"]

```
///


Open Prometheus and execute the query: `interface_oper_state{source="clab-srexperts-leaf21"}`


> To open up [Prometheus](https://prometheus.io/) UI on your laptop use `http://<group-id>.srexperts.net:9090` address.


-{{image(url='./../../../../../images/53-SRL_Telemetry/prom.JPG', title='Fig. 2 - Prometheus')}}-



#### Grafana

[Grafana](https://grafana.com) is another key component of the telemetry monitoring stack, as it provides visualization for the collected telemetry data. There are preconfigured reference dashboards that provide multiple views on the collected real-time data.


> To open up the [Grafana](https://grafana.com) UI on your laptop, use your browser to go to the `http://<group-id>.srexperts.net:3000` address.

Grafana is pre-configured with anonymous access enabled so that you can view the dashboards without authentication. To edit the dashboards you have to login with the username `admin` and password `$EVENT_PASSWORD`. The login button is in the top right corner of the Grafana UI. There are some preconfigured dashboards available. 

Navigate to the `SR Linux Telemetry` dashboard to explore the look and feel of what is available. Check which panels are available and what data they show. Try to understand how the data is collected and how it is visualized.

-{{image(url='./../../../../../images/53-SRL_Telemetry/grafana-nav.gif', title='Fig. 3 - Grafana')}}-


### Create new dashboards

To create dashboards you will need to log in. Click on the `Sign in` button in the top right. User `admin` with password `$EVENT_PASSWORD`.

Under the `SR Linux Telemetry` dashboard you have several visualization panels. If you hover the top right of each panel you will see the `⋮` (kebab menu icon) that opens the menu and shows the edit option.  You may click this to inspect the panel configuration. 

The `BGP Peer stats` panel displays three gauges: 

- Up peers
- Total Peers
- Disabled Peers

You can edit it to inspect the configurations as shown in the Fig.4 below.


-{{image(url='./../../../../../images/53-SRL_Telemetry/grafana_panel_edit.jpg', title='Fig. 4 - Grafana Dashboard Panels')}}-


Your task is to create a dashboard that visualizes if there are any BGP sessions down in the data center fabric. There is no metric that corresponds to the amount of BGP down session, but we can calculate it from the total amount of BGP Total peers available and subtract the total amount BGP sessions in Up state. You may create a color scheme with thresholds green=0, yellow=1 and red=2. 

Bellow is an example of what your dashboard showing the BGP sessions that are down in the fabric might look like.


-{{image(url='./../../../../../images/53-SRL_Telemetry/down_bgp_sessions2.jpg', title='Fig. 5 - Example BGP sessions down Panel')}}-


/// details | Solution: Create BGP peers down dashboard
    type: solution

You first need to create a new dashboard showing the total number of peers and then calculate the number of BGP sessions that are down

/// tab | Create a new dashboard

1. Click `Dashboards` in the menu on the left and then select `New` and  `New Dashboard`
2. Click `+ Add visualization` and select `Prometheus`
3. At the bottom you should see the query builder menu. 
4. Change the Metric view from `Builder` to `Code` (on the right)
5. Type `total_peers` in the Metric browser and observe the available options. From the list, type or select `network_instance_protocols_bgp_statistics_total_peers`
6. Click `> Options` and choose `Custom` from the `Legend` dropdown menu
7. Type `{{source}}` in the `Legend` box
8. In the upper right, click `Time series` to expand the dropdown menu
9. Choose `Gauge` from the dropdown

Your panel should now look like this with gauges showing only the `total peers`


-{{image(url='./../../../../../images/53-SRL_Telemetry/create-panel.JPG', title='Fig. 6 - Total peers panel')}}-
///


/// tab | Calculate total BGP session that are down


1. In the Metric browser subtract the number of up peers (`network_instance_protocols_bgp_statistics_up_peers`) from the total number of peers (`network_instance_protocols_bgp_statistics_total_peers`)
2. In the `Panel options` section on the right, type `Down BGP session in DC fabric` in the `Title` box
3. In the Visualization options on the right, select the color scheme "From Thresholds (by value)"
4. In the Thresholds set base color to green, yellow=1 and red=2 
5. Click `apply` in the upper right corner and `Save dashboard`. 

You should now see the total amount of BGP sessions that are down in the fabric.


-{{image(url='./../../../../../images/53-SRL_Telemetry/grafana-task.JPG', title='Fig. 7 - BGP sessions Panel')}}-

///

///




## Summary and Review

Congratulations! You managed to integrate the nodes into the streaming telemetry stack as requested. A few more dashboards and your network is ready for production!

If you have got this far you have completed this activity and achieved the following:

- Learnt how streaming telemetry is used for network monitoring and the advantages over SNMP
- Understood how to identify and subscribe to streaming telemetry metrics with `gnmic` using the subscribe RPC
- Examined how the components of the telemetry monitoring stack work together
- Learnt how to configure and enable streaming telemetry using gNMI over gRPC on SR Linux
- Used the Grafana visualization tool to create your own dashboard using the metrics streamed from SR Linux


This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity!  Perhaps try a topic that is new to you?  



<!-- This is required to render drawio  -->
<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>