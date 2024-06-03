# Automatically updating configurations

| Difficulty    | Execution time|
| ------------- |:-------------:|
| Advanced      | 120 min         |


## Objective
In this lab, we'll take on an adventure of automating parts of our SR OS configuration to keep them aligned and updated with information taken from external APIs. In the first task we will attempt to create ACL configuration based on information made available via MaxMind, providing a list of IP addresses linked to their geographic regions. For the second task, we will look at rPKI.

The lab makes use of Python, using pySROS both on SR OS and running remotely, over NETCONF. A well-known tool for querying AS and BGP information, `bgpq4`, is used and information is retrieved from publicly available repositories.

## Accessing the lab
In this lab you will interact with model-driven SR OS, so any model-driven SR OS router in the topology would work. For this text we will assume the `pe1` node is used.
```
ssh -l admin clab-srexperts-pe1
```

## Task 1: MaxMind GeoIP data for ACL configuration
According to Wikipedia, [MaxMind](https://en.wikipedia.org/wiki/MaxMind) is a Massachusetts-based data company that provides location and other data for IP addresses, and fraud detection data used to screen hundreds of millions of online transactions monthly. The usecase made possible by Maxmind that we're mostly interested in is enforcing digital rights. A service that is available on the public Internet is by design available to anyone, and in some cases this is not desired. To restrict the possible set of clients to only a set geographic region, Maxmind's data can be used.

There are two distinct approaches possible for implementing this task, which we will both explore. The building blocks remain the same, though depending on preference and availability one method may be preferable over the other. Globally, the steps needed are:

1. Collect data from MaxMind
2. From the retrieved data, build an ACL configuration and send it to the router
3. Make sure your code behaves correctly when the data changes on a subsequent run of the script

One possible approach for tackling this task is to run a pySROS program from a Python-capable platform that can reach both the MaxMind API and the target router. The pySROS program collects the data, parses it, molds it into an ACL that is wrapped into a payload that is accepted by the target router. The program then sends the payload to the router and applies it to the router configuration. Another approach involves a simple script collecting the data and uploading it as a file to the router. Using on-box Python executions in a cron schedule, this data is then periodically loaded from the file to keep it up-to-date.

Since both approaches will have the same general building blocks, we'll start by defining and building those.

### Subtask 1: Build a Python script that makes an API call to MaxMind to retrieve IP address information

Create a file `prefixes.py` somewhere on your cloud instance or on your local system. It should be executed from a machine with access to the internet. The on-board Python interpreter of SR OS has no way to reach outside of the router and so is eliminated as an option.

1. Download a CSV database from MaxMind. A database containing example data can freely be downloaded [here](https://dev.maxmind.com/static/GeoIP2-Country-CSV_Example.zip). Alternatively, if you want to create or you have an account already, feel free to download non-example data. These databases contain files listing locations identified by IDs and links IP addresses to those IDs.
2. Choose a country you would like to build a prefix-list for. For the example solution using the example archive linked above, we used "United Kingdom".
3. Parse the GeoIP2-Country-Blocks.IPv4.csv file to find the IP prefixes located in that country according to MaxMind. How many prefixes are there?
4. (optional) If you wrote the archive to disk as an intermediate step, can you do it completely in memory?

In [examples/prefixes.py](./examples/prefixes.py) you may be able to find some inspiration should you become stuck.

### Subtask 2: Add Python code using pySROS to create an ACL

Using the list of IP prefixes found in the previous exercise as input, we will now use pySROS to craft this list into a payload consumable by the model-driven SR OS router `pe1` in your topology and send that payload up to the router. Depending on your personal preference, either expand the `prefixes.py` file with this function that should take the output of subtask 1 as input or create a new file for the function. The following steps are a rough outline of how you can approach this.

1. Start by creating the prefix-list payload from the prefixes. You can use [the YANG model](https://github.com/nokia/7x50_YangModels/blob/2a28af0e7fba2170eeec83315aafe27f54e221f2/latest_sros_23.10/nokia-submodule/nokia-conf-filter.yang#L507) as a reference (or the MD-CLI, or .. ).
2. Using pySROS, send an `edit-config` RPC containing the new prefix-list to the router to create it.
3. Follow up on that by creating an ACL (ip-filter) that makes use of that prefix-list.
4. (optional) Can you wrap 2. and 3. in a single pySROS operation?

### Subtask 3: Updating the ACL

Now the building blocks are present, change the country targeted to Sweden and let your program run as before (you could re-use the downloaded database, however).

1. What happens to the ACL?

   1.1. How many prefixes are in the ACL on the router now?

   1.2. how many prefixes were assigned to Sweden in the MaxMind database?

   1.3. How many prefixes were in the list for the United Kingdom?

If there are more prefixes in the ACL prefix-list on the router than only those belonging to Sweden, what went wrong?

2. How would you go about automating this process?

### Subtask 4: (alternative / optional) On-box CRON

Having completed the task at hand, we will now consider an alternative implementation where data is collected on one platform and uploaded to the router as a file. On the router, this file is regularly read and used to update the configuration.

1. Instead of passing the list of prefixes to your pySROS code, upload it to the router as a file, `cf3:/prefixes.txt`. An example is included in [prefixes_uploadonly.py](./examples/prefixes_uploadonly.py).
2. Modify and re-use your pySROS code from the previous steps to build the `ip-prefix-list` and ACL configuration as before, using the uploaded file as input.
3. Configure a CRON schedule such that this script runs automatically every minute.

Configuration to look at to create a `python-script` object in SR OS, a `script-policy` to make use of it and a `cron schedule` to make use of that `script-policy` is:

```
/configure python python-script <string>
/configure system script-control script-policy <string> owner <string>
/configure system cron schedule <string> owner <string>
```

Test your Python code before creating the SR OS `python-script` object that uses it for a smoother experience. You can trigger a reload of the `python-script` to re-read the file using

```
/perform python python-script reload script < script name >
```

A configuration snippet to assist you is included in the [prefixes_onbox.py](./examples/prefixes_onbox.py) example.

Note: MaxMind makes a Python binding available in [GeoIP2-python](https://github.com/maxmind/GeoIP2-python), but it only allows querying based on IP addresses and wouldn't be fit for our usecase.

## Task 2: Automating and augmenting IXP peerings

In this task, several topics come together and some background is required to fully understand them. The following two sections offer some background and are meant as a reference. Feel free to skip over these sections.

### Terminology and abbreviations

Resource Public Key Infrastructure (RPKI), also known as Resource Certification, is a specialized public key infrastructure (PKI) framework to support improved security for the Internet's BGP routing infrastructure. One of the organizations advocating for the global implementation of RPKI is Mutually Agreed Norms for Routing Security [MANRS](https://manrs.org/). With this in mind, MANRS is based around a set of actions, some compulsory, some recommended.

In general, these actions mention many different abbreviations and words that would be entirely unfamiliar to anyone not actively working with them. Among these are AS-SET, AUT-NUM, RIR, IRR, RPSL, RPKI and ROA. For the purposes of this usecase, a short description of each of these terms follows:

- `as-set`:  An as-set is, as the name suggests, a set of Autonomous Systems (AS). Names of as-sets begin with `AS-`. It can contain AS numbers and other as-sets.

- `aut-num`: AS numbers are specified using the aut-num class. The key of an aut-num object is the AS number of the AS described by this object. The as-name attribute is a symbolic name (in RPSL name syntax) of the AS. The import, export and default routing policies of the ASes are specified using import, export and default attributes respectively.

- `route`: Specifically for this lab usecase, route objects are taken to mean any inter-AS route originated by an AS. This object's key is made up of an address prefix of the route as well as an origin attribute that identifies the AS originating the route.

- `RPSL`: Originally defined in [rfc2280](https://datatracker.ietf.org/doc/html/rfc2280), the Routing Policy Specification Language (RPSL) allows network operators to specify routing policies at various levels of the Internet hierarchy. It is intended to contain enough detail to allow low-level (i.e. router configuration level) routing policies to be created.

- `RIR`: There are five Regional Internet Registries (RIRs) in the world. RIRs manage, distribute, and register Internet number resources (IPv4 and IPv6 address space and Autonomous System (AS) Numbers) within their respective regions. These regions are AFRINIC for Africa, APNIC for Asia Pacific, ARIN for USA, LACNIC for Latin America and the Caribbean and RIPE NCC for Europe, the Middle East and parts of Central Asia.

- `IRR`: The global Internet Routing Registry (IRR) is comprised of a network of distributed databases maintained by Regional Internet Registries (RIRs) such as  ARIN, service providers, and third parties. Some of these databases contain only routing information for a particular region, network, or ISP.

- `RPKI`: Resource Public Key Infrastructure (RPKI) provides a trust system for IP address and AS number information. Custodians of internet resources (IANA, RIR, ISPs, ..) are given the power to sign certificates that, amongst other things, can link IP addresses and AS numbers together to identify which AS is allowed to advertise specific IP addresses.

- `ROA`: Route Origin Authorization (ROA) are used for Route Origin Validation (ROV). This is the primary function of RPKI. A ROA contains the AS number that is authorized, the prefix that is originated from that AS and the most specific prefix that AS may announce. By creating ROAs, the risk of routing errors will be minimized and most accidental route hijacks are prevented.


### Tools and APIs

For this usecase, we'll rely on several databases and tools available online. We will be using the following tools:

- RADb: The Routing Assets Database (RADb) is a public database in which the operators of Internet networks publish authoritative declarations of routing policy for their Autonomous System (AS) which are, in turn, used by the operators of other Internet networks to configure their inbound routing policy filters. The RADb, operated by the University of Michigan's Merit Network, was the first such database and others followed in its wake, forming a loose confederation of Internet routing registries, containing sometimes-overlapping, and sometimes-conflicting routing policy data, expressed in Routing Policy Specification Language (RPSL) syntax.    ([source - Wikipedia](https://en.wikipedia.org/wiki/Routing_Assets_Database))

- PeeringDB is a freely available, user-maintained database of networks, and the go-to location for interconnection data. The database facilitates the global interconnection of networks at Internet Exchange Points (IXPs), data centers, and other interconnection facilities, and is the first stop in making interconnection decisions. PeeringDB exposes an API making it particularly suited for (parts of) this usecase.    ([source - Wikipedia](https://en.wikipedia.org/wiki/PeeringDB))

- [Hurricane Electric BGP Toolkit](https://bgp.he.net/): According to [Wikipedia](https://en.wikipedia.org/wiki/Hurricane_Electric), Hurricane Electric is a global Internet service provider offering Internet transit, tools, and network applications, as well as data center colocation and hosting services at two locations in Fremont, California, where the company is based. They provide a tool that allows users to search information about AS numbers, prefixes, in addition to many other interesting features. Similar tools exist, a well-known example is [bgp.tools](bgp.tools).

- [bgpq4](https://github.com/bgp/bgpq4) is a tool that can automatically execute complex recursive lookups through whois databases and output information in formats consumable by machines, routers and people alike, depending on the tool settings used. It is available as a package on most Linux distributions and the source code is available on the link above.

- WHOIS (pronounced as the phrase "who is"), currently defined in [RFC3912](https://datatracker.ietf.org/doc/html/rfc3912) is a query and response protocol that is used for querying databases that store an Internet resource's registered users or assignees. These resources include domain names, IP address blocks and autonomous systems, but it is also used for a wider range of other information. The protocol stores and delivers database content in a human-readable format. WHOIS communicates over TCP port 43 and has quite a history ([source - Wikipedia](https://en.wikipedia.org/wiki/WHOIS#History)) behind it.

- [gobgpd](https://github.com/osrg/gobgp) is a BGP server implemented in Go. In the lab topology, we use gobgpd as a BGP speaker on the node `transit1`. It is used to inject BGP routes and RPKI information into the topology based on information downloaded from RIPE.

### Subtask 1: Create peering configurations

In this task, you'll create a Python script that takes as input an organization name and IX location. In the example solution we use `Netflix (AS 2906)` and `AMS-IX`. The script will go to the PeeringDB API to retrieve information about the peering offered by Netflix at AMS-IX. Using this information and pySROS, configure that peering in router `pe1`. Use these steps to guide you, as well as the [peeringdb_rpki.py](./examples/peeringdb_rpki.py) file provided to you in the [examples](./examples/) folder should you require any additional inspiration.

1. In your Python script, use the `argparse` module or your preferred alternative to accept inputs for an IX location and an ASN and a target node to receive configuration. The example configuration uses `pe1`.
2. Use either the [PeeringDB Python bindings](https://docs.peeringdb.com/tools/) or the publicly available [PeeringDB API](https://www.peeringdb.com/apidocs/) to discover the ASN, IPv6 address and / or IPv4 address to peer with your chosen AS at the chosen peering point.
3. If the chosen organization has an AS-SET, resolve it to it's ASN members and create a routing policy to use as import policy to the peering you will set up that accepts only routes from those members. You can use `whois` or `bgpq4` for this.
4. Using `bgpq4`, create a prefix list corresponding to the AS you have used as input.
5. Aggregate this information into a payload that will

   - set up a BGP peering, though instead of the IP address and peer AS you found via the API, use `fd00:fc00:0:51::3` and `64599`. This keeps the peering local to the topology. Use address family `ipv6`. Enable `origin-validation` for the IPv6 address family on this BGP session.
   - add the import policy created in step 3 to this BGP peering.
   - create the prefix list you retrieved the information for in step 4 on the router, do not use the prefix-list anywhere.

6. Apply the payload to the router configuration and ensure the BGP peering comes up as expected.

### Subtask 2: rPKI configuration

Nokia advertises rPKI information. For this exercise, imagine there is no RPKI server available to you in the lab topology. The BGP peering created in the previous task advertises several prefixes advertised by Nokia in AS 38016. In this subtask you'll create a Python script that uses online tools to learn which prefixes Nokia advertises in this AS and, if those are rPKI validated, creates the bindings between the AS and the prefix with pySROS.

1. Check which prefixes are being advertised in the BGP peering set up in the previous step. Use `show router bgp neighbor fd00:fc00:0:51::3 received-routes ipv6`. Alternatively or additionally, can you verify these prefixes are advertised by AS 38016 in another way?
2. Check the `Origin Validation` state for these prefixes, what do you find here?
3. Use Python to generate static entries on `pe1` under `/configure router "Base" origin-validation` using some of the online tools listed above. The example solution uses the [Hurricane Electric BGP Toolkit's Super Looking Glass](https://bgp.he.net/super-lg/). Do your changes in the configuration have an effect on the advertised prefixes' state?
