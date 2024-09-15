# SROS Streaming Telemetry

**Difficulty**: Beginner

---

This lab demonstrates streaming telemetry data using gNMI over gRPC on the SR OS network operating system.

Additionally, it uses a network telemetry stack consisting of a collector ([gNMIc](https://gnmic.openconfig.net)), a time-series database ([prometheus](https://prometheus.io)), and a visualization dashboard ([grafana](https://grafana.com)) in order to graphically demonstrate streaming telemetry from SR OS in action.

```
  ┌──────┐                           Scrape     ┌────────────┐
  │  R1  ├──────┐             ┌────────────────►│            │
  └──────┘      │             │                 │    TSDB    │
                │       ┌─────┴─────┐           │(prometheus)│
  ┌──────┐      │       │           │           └──────┬─────┘
  │  R2  ├──────┼──────►│ collector │                  │
  └──────┘      │       │  (gNMIc)  │       datasource │
                │       └───────────┘       connection │
  ┌──────┐      │                                      ▼
  │  R3  ├──────┘                               ┌─────────────┐
  └──────┘                                      │             │
            Streaming                           │visualization│
            Telemetry                           │  (grafana)  │
              (gNMI)                            └─────────────┘
```

By the end of this lab, the user will understand:

- differences between SNMP and streaming telemetry
- how to identify and subscribe to streaming telemetry metrics
- how the components of the telemetry stack work together
- how to configure and enable streaming telemetry using gNMI over gRPC on SR OS
- how to create visualizations of the metrics

## Telemetry Stack Reference

| Role                | Software                              | Access                                                     |
| ------------------- | ------------------------------------- | ---------------------------------------------------------- |
| network device      | SROS 24.3.R2                          | `ssh admin@clab-srexperts-p1`                              |
| Telemetry collector | [gnmic](https://gnmic.openconfig.net) |                                                            |
| Time-Series DB      | [prometheus](https://prometheus.io)   | `ssh -NL 9090:10.128.<lab id>.72:9090 <user>@<lab server>` |
| Visualization       | [grafana](https://grafana.com)        | `ssh -NL 3000:10.128.<lab id>.73:3000 <user>@<lab server>` |

## SNMP and Streaming Telemetry

Since the mid 1990s, it has been common to use SNMP to monitor networking devices. In an environment utilizing SNMP, telemetry data are collected by periodically polling the network devices to retrieve the desired stats which are identified by unique OIDs.

Due to its many limitations, SNMP is not capable of providing the granular real-time statistics that are required to effectively monitor modern networks.

These are just some of the limitations of using SNMP for network monitoring.

- **Polling overhead** - continuous polling is heavily taxing on both the device being polled and the management system doing the polling.
- **Scalability** - As the number of devices and complexity in a network increases, the SNMP polling frequency would need to be reduced to avoid overwhelming the network devices or management system.
- **Security** - SNMP v1 and v2c both lack authentication and encryption mechanisms. While v3 does improve on security, the adoption has been slow due to configuration complexity and vendor compatibility.
- **Reliablity** - SNMP relies on UDP primarily due to its low overhead, but UDP does not provide any mechanisms for reliable data delivery which can lead to lost or out-of-order data points.

This is where streaming telemetry comes in.

Streaming telemetry is a newer approach to network monitoring that provides continuous, real-time data streaming from network devices.

Instead of a system having to ask the network devices for a particular data point, the network devices are able to _stream_ or push data to any system that is configured to receive it.

This lab utilizes [gNMI](https://www.openconfig.net/docs/gnmi/gnmi-specification/) for streaming telemetry.

[gNMI](https://www.openconfig.net/docs/gnmi/gnmi-specification/) is a protocol for configuration manipulation and state retrieval, and is built on top of [gRPC](https://grpc.io/docs/what-is-grpc/introduction/) which adds the benefits of [HTTP/2](https://datatracker.ietf.org/doc/html/rfc7540).

[gNMI](https://www.openconfig.net/docs/gnmi/gnmi-specification/) utilizes [protobuf](https://protobuf.dev/) for payload encoding which makes it extremely fast and highly scalable because the payload is encoded into a bit stream with very low overhead.

There are four supported RPCs in [gNMI](https://www.openconfig.net/docs/gnmi/gnmi-specification/):

1. **Capabilities** - obtain the encodings and models supported by the target
2. **Set** - change the writable state of a target
3. **Get** - obtain the state of a path or prefix at a given time
4. **Subscribe** - streaming telemetry from target.

- There are three different subscription modes: **[ once | poll | stream ]**
- There are two different stream subscription modes: **[ sample | on-change ]**

## Telemetry Stack Components

### gNMIc

[gNMIc](https://gnmic.openconfig.net) was developed by Nokia and donated to the Openconfig project. It allows subscribing to streaming telemetry data from network devices and export it to a variety of destinations. In this lab, gnmic is used to subscribe to the telemetry data from the lab routers and export it to the prometheus time-series database.

The gnmic configuration file ([config.yml](../../../clab/configs/gnmic/config.yml)), is applied to the gnmic container at the startup and instructs it to subscribe to thebbb telemetry data and export it to the prometheus time-series database.

#### Using gNMIc From CLI

Although [gnmic](https://gnmic.openconfig.net) is functioning as the streaming telemetry collector in this topology, it can be used from the command line to test paths and see the metrics.

Starting simple, recall there were four RPCs supported in [gNMI](https://www.openconfig.net/docs/gnmi/gnmi-specification/). Capabilities shows the supported models and encodings on the server.

SSH to the lab server and run the capabilities RPC with gNMIc:
`gnmic -a clab-srexperts-p1 -u admin -p admin --insecure capabilities`

```
❯ gnmic -a clab-srexperts-p1 -u admin -p admin --insecure capabilities
gNMI version: 0.8.0
supported models:
  - nokia-conf, Nokia, 24.3.R2-1
  - nokia-state, Nokia, 24.3.R2-1
  - nokia-li-state, Nokia, 24.3.R2-1
supported encodings:
  - JSON
  - BYTES
  - PROTO
  - JSON_IETF
```

> A very useful feature in SROS is the ability to easily output the gNMI path directly from the CLI. This makes it extremely easy to find the path to a particular metric even if you do not have a YANG browser available. The metric paths are what will be used by the collector - the configuration file will be reviewed shortly.

From the lab server, ssh directly into clab-srexperts-p1 and do the following:

```
[/]
A:admin@p1# /state router route-table unicast ipv4 statistics isis

[/state router "Base" route-table unicast ipv4 statistics isis]
A:admin@p1# pwc gnmi-path
Present Working Context:
/state/router[router-name=Base]/route-table/unicast/ipv4/statistics/isis
```

Copy the path, and return to the lab server. This time perform a GET RPC using that path:

```
❯ gnmic -a clab-srexperts-pe1 -u admin -p admin --insecure get --type all --path 'state/router[router-name=Base]/route-table/unicast/ipv4/statistics/isis/'
[
  {
    "source": "clab-srexperts-pe1",
    "timestamp": 1715191538493353284,
    "time": "2024-05-08T21:05:38.493353284+03:00",
    "updates": [
      {
        "Path": "state/router[router-name=Base]/route-table/unicast/ipv4/statistics/isis",
        "values": {
          "state/router/route-table/unicast/ipv4/statistics/isis": {
            "active-routes": 24,
            "available-routes": 24
          }
        }
      }
    ]
  }
]
```

\*_Tip: gNMIC also supports finding YANG paths using YANG models. Visit the [SROS YANG Models Repo](https://github.com/nokia/7x50_YangModels) if you want to use this feature._

Click for more information on [gNMIC Search](https://gnmic.openconfig.net/cmd/path/#search)

#### Reviewing gNMIC Collector Configuration

**Take a look through the [config.yml](../../../clab/configs/gnmic/config.yml) and try to figure out what is going on before moving on to the explanations.**

\*_TIP: The [gNMIc User Guide](https://gnmic.openconfig.net/user_guide/configuration_intro/) is a great place to reference._

> Understanding how to configure the gNMIc collector is key to being able to visualize the appropriate data in a way that is most effective!

This section reviews each of the main parts of the configuration for the collector. Consider where the collector fits into the telemetry stack, the streaming options from [gNMI](https://www.openconfig.net/docs/gnmi/gnmi-specification/) and how to find paths while completing this section.

**Global Flags Section**

At the top of the [config.yml](../../../clab/configs/gnmic/config.yml) are the [global flags](https://gnmic.openconfig.net/user_guide/configuration_file/#global-flags):

```
username: admin
password: <redacted>
port: 57400
timeout: 10s
skip-verify: true
encoding: json_ietf
```

As is common, these are used unless they are defined in a more specific location later.

**Targets / Loader Section**

The next section is the [targets](https://gnmic.openconfig.net/user_guide/targets/targets/) but instead of defining the targets individually, they are discovered using the [loader](https://gnmic.openconfig.net/user_guide/targets/target_discovery/file_discovery/) option - in this case, it is the [Docker discovery](https://gnmic.openconfig.net/user_guide/targets/target_discovery/docker_discovery/).

There are two different [filters](https://gnmic.openconfig.net/user_guide/targets/target_discovery/docker_discovery/#filter-fields-explanation) defined for this [docker loader](https://gnmic.openconfig.net/user_guide/targets/target_discovery/docker_discovery/); one for the SR Linux containers and one for the SROS containers.

> Note that the global flags are overwritten in the loader to be able to provide different encoding and passwords for each type

There are different [subscriptions](https://gnmic.openconfig.net/user_guide/subscriptions/) listed for each type as well. These reference those defined in the [subscriptions](https://gnmic.openconfig.net/user_guide/subscriptions/) section.

**Subscriptions Section**

Each of these [subscriptions](https://gnmic.openconfig.net/user_guide/subscriptions/) is named by the user and could be any form, but should be easy to quickly understand and differentiate.

A [subscription](https://gnmic.openconfig.net/user_guide/subscriptions/) specifies the data to be collected and the method for collecting that data. It is configured using a set of flags including:

- `paths:` a list of paths to be subscribed to for this set
- `mode:` [once | poll | stream]
- `stream-mode:` [target-defined | sample | on-change] - sampling constantly gets the data at the [sample-interval](https://gnmic.openconfig.net/cmd/subscribe/#sample-interval) rate
- `sample-interval:` the sample interval to be used by the [target](https://gnmic.openconfig.net/user_guide/targets/targets/) to send samples to the client

**Outputs Section**

[gNMIc](https://gnmic.openconfig.net) supports multiple [output](https://gnmic.openconfig.net/user_guide/outputs/output_intro/) options. This lab is configured to use [prometheus](https://prometheus.io).

Although it is possible to push metrics to a [prometheus](https://prometheus.io) server, this lab is configured to allow [prometheus](https://prometheus.io) to pull metrics using the [scrape-based](https://gnmic.openconfig.net/user_guide/outputs/prometheus_output/) configuration.

For more detail, please reference the [documentation](https://gnmic.openconfig.net/user_guide/outputs/prometheus_output/), but these are some of the important options:

- `name` is user-defined. In this case, it is set to `prom` to signify that this is the [prometheus](https://prometheus.io) output.
- `listen` defines the local port to listen for scrape requests.
- `path` this is the path where the metrics are stored
- `event-processors` this is the list of [processors](https://gnmic.openconfig.net/user_guide/event_processors/intro/), keep in mind these are executed as a pipeline in the order they are defined here.

**Processors Section**

\*_Advanced Topic!_ This section covers a more advanced topic. Feel free to skim or skip it entirely.

[Processors](https://gnmic.openconfig.net/user_guide/event_processors/intro/) provide a way to configure a set of functions that allow an event message to be transformed as necessary to create effective visualization in the dashboard.

Understanding the [event message](https://gnmic.openconfig.net/user_guide/event_processors/intro/) is key to being able to understand how to transform the data.

![event message](images/notification_message.png)

> Looking at the event messages using [gNMIc](https://gnmic.openconfig.net) on the cli is useful for looking at the actual data and then deciding on an approach for transforming the data using [processors](https://gnmic.openconfig.net/user_guide/event_processors/intro/).

_Please refer to the [documentation](https://gnmic.openconfig.net/user_guide/event_processors/intro/) to construct [processors](https://gnmic.openconfig.net/user_guide/event_processors/intro/)._

### Prometheus

[Prometheus](https://prometheus.io) is a popular open-source time-series database. It is used in this lab to store the telemetry data exported by gnmic. The prometheus configuration file - [prometheus.yml](../../../clab/configs/prometheus/prometheus.yml) - has a minimal configuration and instructs prometheus to scrape the data from the gnmic collector with a 5s interval.

Time Series Data:

- Metrics are stored with the timestamp at which they were recorded, alongside optional key-value pairs called labels.

The [prometheus.yml](../../../clab/configs/prometheus/prometheus.yml) file used in this lab is very basic. It simply defines a scrape interval and the server name and port to scrape.

\*_To change the metrics being delivered to [grafana](https://grafana.com), the [config.yml](../../../clab/configs/gnmic/config.yml) is the only location where changes need to be made. [Prometheus](https://github.com/prometheus) will scrape all available metrics from [gnmic](https://gnmic.openconfig.net)._

> To be able to view the [prometheus](https://github.com/prometheus) dashboard on your laptop, use ssh forwarding: \
> `ssh -NL 9090:10.128.<lab id>.72:9090 <user>@<lab server>`\
> Now you can access the [prometheus](https://github.com/prometheus) dashboard at: [http://127.0.0.1:9090](http://127.0.0.1:9090)

### Grafana

[Grafana](https://grafana.com) is another key component of this lab as it provides the visualization for the collected telemetry data. The topology file includes [grafana](https://grafana.com) node and configuration parameters such as dashboards, datasources and required plugins.

The preconfigured reference dashboard included with this repository provides multiple views on the collected real-time data.

(\*_connect using the instructions below before moving on_)

> To be able to view the [grafana](https://grafana.com) dashboard on your laptop, use ssh forwarding: \
> `ssh -NL 3000:10.128.<lab id>.73:3000 <user>@<lab server>`\
> Now you can access the [grafana](https://grafana.com) dashboard at: [http://127.0.0.1:3000](http://127.0.0.1:3000)

The login is `admin/admin`. When you log in, it will tell you to change the password but you can skip this by clicking skip at the bottom of the login window.

There are some [preconfigured dashboards](http://127.0.0.1:3000/dashboards)

Select `SROS Telemetry` to view the one for this lab.

#### Creating A Dashboard

\*_TIP: Use the [preconfigured dashboard](http://127.0.0.1:3000/dashboards) as a reference if needed._

##### Add Datasource

\*_It is not necessary to add a datasource because it has been added as part of the lab instantiation. However, it is good to know how to add a datasource._

1. Be sure to be logged into the [dashboard](http://127.0.0.1:3000) and then click the `burger menu -> Connections -> Data sources`
2. In the main window, click on the [Prometheus](https://prometheus.io) option to open the configuration panel.
3. Look through the configuration panel and take notes of the `Prometheus server URL` and the `scrape interval`
4. At the bottom of the panel, click the `Test` button to make sure the datasource is reachable with the configured parameters

When adding a datasource, always test it to be sure the configuration is correct.

##### Explore Metrics

Before creating a panel, it is important to get comfortable with the metrics.

Be sure to be logged into the [dashboard](http://127.0.0.1:3000) and then click the `burger menu -> Explore`

1. In the explore window, look for the `Metric` box.
2. Type `path_mem` into the `Metric` box and the matching metrics will show up below
3. Click on `router_bgp_statistics_path_memory` to select it
4. Create a filter for `source` and choose one of the available routers from the dropdown
5. Click on `+ Operations` -> `Range functions` -> `Rate`
6. Click `Run Query` in the upper right corner
7. Review the graph, try to change it and understand how the
   filters, operations and graph options work.

##### Create New Dashboard & First Panel

1. Click the `burger menu` -> `Dashboards` -> `New` -> `New Dashboard`
2. Click `+ Add visualization` and select `Prometheus`
3. Click in the `Metrics` box and select `Metrics explorer`
4. Type `bgp_max` in the box and select `system_memory_pools_bgp_max_so_far`
5. Click `> Options` and choose `Custom` from the `Legend` dropdown menu
6. Type `{{source}}` in the `Legend` box
7. Click `Time series` in the upper right to expand the dropdown menu
8. Choose `Gauge` from the dropdown
9. In the `Panel options` section, type `Max BGP Memory Usage` in the `Title` box
10. Scroll down to the `Show threshold markers` slider and slide it to the `off` position
11. Scroll down to the `Standard options` section and click the `Unit` -> `Misc` -> `short` option
12. In the `Min` box, type `16000000` and in the `Max` box, type `256000000`
13. Scroll all the way down to the bottom and click the `Percentage` box
14. Click `apply` in the upper right corner

##### Create Second Panel & Row

Now there is a single panel in the dashboard.

1. Add another panel by clicking the `Add` button near the middle of the menu bar and choose `Visualization` from the dropdown.
2. Repeat the same steps from above but instead of `system_memory_pools_bgp_max_so_far`, use `system_memory_pools_bgp_current_size`
3. When you have both panels on the dashboard, drag them around to make them side-by-side.
4. Now, add a `Row header` from the `Add` button near the middle of the menu bar
5. Click the `gear` icon next to the `Row title` and rename the `Row title` to `BGP Memory Pool Usage`
6. Click the `>` next to `BGP Memory Pool Usage` to _roll up / hide_ the entire row.

##### Add Variables

Sometimes you will want to create a visualization with the option to select from a list - dashboard variables are used for this purpose.

1. Save the current dashboard by clicking the `floppy disk icon` on the menu bar and naming your dashboard
2. Click the `gear icon` next to the `floppy disk icon` - this is the `dashboard settings`
3. On the left side, click `Variables`
4. Click `Add variable`
5. In the `Name` box, type `Node`
6. Scroll down to `Query type` dropdown and choose `Label values` from the dropdown
7. In the `Label*` dropdown, type `source`
8. Scroll all the way to the bottom - look at the `Preview of values` list - there are many routers listed that are SR Linux based routers.
9. In the `Regex` box, type `clab-srexperts-p(?!eering).*`
10. Review the `Preview of values` list and note that it has changed to just the routers that match the regex (only the SROS routers in this topology).

This type of variable can be used to create any list that makes sense from the list of label values. Add as many different variables as are needed.

##### New Panel Using Variable Filter

1. From the menu bar, click the new dashboard
2. Add a new visualization
3. Add the `router_interface_statistics_in_packets` metric
4. In `Label filters` use the left dropdown box to select `source` and in the right box select `$Node`
5. Click the `Options` -> `Custom` and type `{{interface_interface_name}}`
6. Click `Apply`
7. Now you can select different `Nodes` from the dropdown list - even if there is no traffic in the graph, there will be different interface names in each node.

### Adding New Metrics

#### Identify & Test New Metric

It is possible to test a new subscription from the cli using [gnmic](https://gnmic.openconfig.net).

1. Open an ssh session to the lab server.
2. Run the following command from the cli
   `gnmic -a clab-srexperts-p1 -u admin -p admin --insecure get --path /state/system/security/ssh/connections`
3. Open another ssh session to the lab server and from this new session, ssh to `clab-srexperts-p1`
4. In the original lab server session, run the command again and note the different output.

#### Add New Subscription

In order to add additional metrics, the [config.yml](../../../clab/configs/gnmic/config.yml) will need to be updated.

Edit the [config.yml](../../../clab/configs/gnmic/config.yml) file, adding the following new subscription:

```
  sros_ssh_connections:
    paths:
      - /state/system/security/ssh/
    mode: stream
    stream-mode: sample
    sample-interval: 5s
```

Also, add the new subscription to the SROS container on `line 61` add the new subscription to the list: `- sros_ssh_connections`

#### Restart the gNMIc Container

To see the changes, restart the docker container:

1. find the container id using `sudo clab inspect --all | grep gnmic`
2. restart the container: `docker restart <container_id>`

#### Use New Metric

Back to the [dashboard](http://127.0.0.1:3000), go back to `Explore` and try to make a visualization for `system_security_ssh_connections_connection_user{user="admin"}`

#### Finally Create Full Dashboard

Finally, take what you have learned and try to create the most creative dashboard you can!

## Thank You!
