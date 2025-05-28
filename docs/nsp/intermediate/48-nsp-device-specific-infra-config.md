---
tags:
  - NSP
  - Intent Manager
  - Service Management
  - Visual Studio Code
---

# NSP Device Configuration


|     |     |
| --- | --- |
| **Activity name**           | NSP Device Configuration                                      |
| **Activity ID**             | 48                                                            |
| **Short Description**       | Use generator tool to build new intent-types for SR OS        |
| **Difficulty**              | Intermediate                                                  |
| **Tools used**              | IM VS Code Extension, ICM                                     |
| **Topology Nodes**          | :material-router: PE1 |
| **References**              | [VSCode IM Extension](https://github.com/nokia/vscode-intent-manager) |

## Objective

Use Visual Studio Code (or code-server) with the NSP Intent Manager extension to create
device-specific intent-types that can be used in the context of *Device Configuration*.

## Technology explanation

### Visual Studio Code

**[Visual Studio Code (VS Code)](https://code.visualstudio.com/)** is a free, lightweight, and cross-platform source-code
editor developed by Microsoft, with its core available under [MIT License](https://github.com/microsoft/vscode/blob/main/LICENSE.txt).
While the official Microsoft distribution includes telemetry and branding, the underlying [open-source project](https://github.com/microsoft/vscode)
is actively developed by thousands of contributors worldwide. Backed by Microsoft and deeply integrated with [GitHub](https://github.com/),
VS Code offers rich extensibility through the [Visual Studio Code Marketplace](https://marketplace.visualstudio.com/vscode), enabling
developers to tailor their development environments with themes, debuggers, linters, and language support.

VS Code runs seamlessly on **Windows, MacOS X, and Linux**, and also powers browser-based development via [code-server](https://github.com/coder/code-server)
and [GitHub Codespaces](https://github.com/features/codespaces). Features like built-in Git support, [Remote SSH](https://code.visualstudio.com/docs/remote/ssh),
IntelliSense, and live share collaboration making it a top choice for developers. The well-documented [extension API](https://code.visualstudio.com/api),
comprehensive [examples](https://github.com/microsoft/vscode-extension-samples), and clean [UX Guidelines](https://code.visualstudio.com/api/ux-guidelines)
encourage a thriving eco-system and consistent user experience.

You can download VS Code [here](https://code.visualstudio.com/Download) and start exploring the modern, extensible, and developer-friendly environment
shaping how code is written today.

NOKIA is actively contributing VS Code extensions to improve Developer eXperience around our networking products and technologies being used.
In this hackathon, you have the opportunity to use the following extensions contributed by Nokia in action:

* [NSP Intent Manager extension](https://github.com/nokia/vscode-intent-manager)
* [NSP Workflow Manager extension](https://github.com/nokia/vscode-workflow-manager)
* [NSP Artifact Manager extension](https://marketplace.visualstudio.com/items?itemName=Nokia.artifactadminstrator)
* [NSP connect extension](https://marketplace.visualstudio.com/items?itemName=Nokia.nsp-connect)
* [EDA extension](https://marketplace.visualstudio.com/items?itemName=eda-labs.vscode-eda)
* [Containerlab extension](https://github.com/srl-labs/vscode-containerlab)
* [NETCONF extension](https://github.com/nokia/vscode-netconf)

### Intent Manager

Intent Manager is a module within the Nokia Network Services Platform (NSP) that enables intent-based networking (IBN) by translating
higher-level objectives into automated network actions. It has the ability to abstract the complexity of network configuration by
allowing operators to express what they want, rather than how to do it.

By separating declarative intent configuration (w/ validation) from intent operations like audits and synchronization, Intent Manager
enables CRUD operations with operational lifecycle and control. The sync operation is used for deploying changes into the network but
also to reconcile network object configuration in cases of misalignment, while audits are used to identify misalignments including
network configuration drift.

The library of intent-types can be updated at runtime, while intent-types are developed in JavaScript using YANG-defined intent
models. Using JavaScript enables full flexibility beyond pure configuration management. Intent Manager supports natively
heterogeneous networks (multi-vendor, multi-domain).

### NSP Device Configuration

Device Management Configuration is an intent-based app for infrastructure configuration management (ICM). It uses Intent Manager
as engine underneath, but comes with an optimized user-interface tailored for the needs of device-centric configuration. ICM adds
advanced operational procedures for brownfield configuration discovery and cloning of intent instances.

There is the concept of *device-specific intent-types* in ICM, where a defined subtree of the device is exposed as intent-model.
The main rational to use device models is to provide control over 100% of the device-level attributes, while device experts are
not confused by any sort of normalization as the intent model is identical to what operators already know. Another advantage of
this is, that intent-types can be widely auto-generated. Remind, going device-specific is a compromise, as intent-types
become specific to given device vendors, families and releases, adding operational and integration complexity. While there is
no abstraction using this approach, all configuration details are accessible via rich configuration forms, however, it is
possible to adjust configuration forms to show the relevant configuration attributes only.

## Before you start

/// warning | Disclaimer
The NSP Intent Manager Extension for VS Code including the intent-type generator tool is a community-driven
open-source initiative. Support status of intent-types generated using Visual Studio Code is experimental!
Before using those in production environments, extended testing must be applied to ensure functionality,
robustness, usability, performance, and scale.
  
If you find issues around the generator tool or the intent-types being created, please issue your support
requests and provide feedback to the community directly, by raising issues on GitHub! If you've found a
solution that works for you, we if you contribute code changes back to the project.
By this you become part of our community helping it to grow.
///

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Install / Setup VS Code and the required extensions

/// tip | Using code-server
If you don't have the necessary privileges to install Visual Studio Code on your computer, the
hackathon lab has code-server deployed, so you can run the editor and the extensions from your
web-browser.
///

* Install Visual Studio Code
* Open VS Code and go to the Extensions side-bar
* Search for "NOKIA Intent Manager" and click "Install" to add the extension to your workspace.
* Open the Settings for the Intent Manager Extension
* Adjust the connection details for your NSP system: `nsp.srexperts.net`with the username/password provided
* Change will take effect immediately; Reload is not required
* If you use the *NSP connect* extension (preferred), you can configure/connect to your NSP straight from the sidebar
* Once done, a new folder named *Intent Manager* appears in your VS Code workspace.
* This folder contains subfolders for intent-types (definitions) and intents (instances).

/// tip | Video: Installing and setting up the extension
-{{video(url="https://gitlab.com/-/project/69754954/uploads/b96983518f12ecd4f7ca064fc71d6745/setup-extension.mp4")}}-
///
  
###  Create a new Intent-Type and Intent Instance

**Create and import intent-types:**

* In your workspace, create an *.igen file with the desired NE configuration context (see [below](#intent-type-generator-files)).
* As your NSP instance is shared between all participating groups, use unique filenames.
* The filename will become the name of the new intent-type, so it must be in kebap-case.
* Remind, the device must point to the `ne-id` (device-id) of a device with matching vendor,
  family, and release. In case of **SR** OS routers this is the IP-address of the system interface.
  For this hackathon, you may just select the system ip-address of PE1.
* You find an example below the instructions;
* Right-click on the *.igen file and select `Generate intent-type` from the context menu.
* The generation might take some time. You can monitor the progress in the `OUTPUT` panel.
* Check the intent-type contents.
* Right-click on the intent-type folder and select `Upload intent-type` from the context menu.
* The intent-type should appear on the NSP GUI https://nsp.srexperts.net/web/intent-manager/intent-types
	
/// note | Example: `demo-icm-sros-ip-filter-group50.igen`
```json
{
    "description": "L3 ACL for Nokia SR OS devices (MD MODE)",
    "category": "policies",
    "role": "logical",
    "device": "XXXXXXXX",
    "context": "/nokia-conf:configure/filter/ip-filter"
}
```
///

/// tip
Spend some time to go through the generated code. The intent-type uses a visionary decomposed design. Resources
in the `common` folder are the same for all intent-types generated. A default view-config is created to improve
WebUI usability. The main files that contain custom code are the YANG module and the `script-content.mjs`. If
you've designed intent-types for NSP before, you may recognize the object-oriented design. Be aware, this takes
advantage of the new JavaScript engine (GraalJS), that is available since 24.11.
///

**Import intent-types and creating templates in ICM**:

* Navigate to `Device Management > Configuration intent-types`.
* Import the newly created intent-type.
* Navigate to `Configuration Templates`.
* Create a new template using your intent-type.

**Create an intent**:

* Now you can move to Configuration Deployments.
* Create a new deployment using the previous template.

/// tip | Video: Creating a new Intent-Type and Intent Instance to enable a port
-{{video(url="https://gitlab.com/-/project/69754954/uploads/c6334e7d83192a2d5e6aa5522825cb2c/enable-port.mp4")}}-
///

### Create intent-types to configure ports, interfaces and ISIS bindings

We've just learned step-by-step on how to quickly create brand new intent-types from small *.igen
files. Now, turn is on you to create all required intent-types required for base router connectivity:
Port Configuration, Interface Configuration and IS-IS Interface Configuration.

#### Port Config

Let's start with port configuration.

/// tip
The most important part when creating *.igen files is device-model path. This is where
the subtree starts, that is owned by the corresponding intents. In SR OS MD-CLI one can
use the command `pwc model-path` to retrieve the corresponding string. You should consider
removing the list-key identifiers along the path, to make those identifiers part of the
intent target.

You may decide to exclude certain children subtrees from the intent-type to reduce the
intent complexity and to speed up rendering time using the `exclude` and/or `max-depth`
statements.

Port configuration is a special case, using `role: physical` and `category: port`.
///

/// details | Solution
    type: success

``` json
{ 
    "description": "Port configuration on Nokia SR OS devices (MD MODE)",
    "category": "port",
    "role": "physical",
    "device": "XXXXXXXX",
    "context": "nokia-conf:/configure/port",
    "icmstyle": true,
    "maxdepth": 2,
    "exclude": ["sonet-sdh","tdm","otu","network","gnss","dwdm","access","scheduler","transceiver","dist-cpu-protection","ethernet","hybrid-buffer-allocation","modify-buffer-allocation"]
}
``` 
///

/// note | Device Configuration: Port on PE1
``` bash
[/]
A:admin@g1-pe1# edit-config private 
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(pr)[/]
A:admin@g1-pe1# info configure port  1/1/c1
    admin-state enable
    connector {
        breakout c1-100g
    }

(pr)[/]
A:admin@g1-pe1# info configure port 1/1/c1/1
    admin-state enable
    description "link to P1"
    ethernet {
        mode network
    }
```
///

Now, import the intent-type into ICM, create a template and deployments. 

#### Interface Config

We continue with the IP interface configuration associated with the Base router instance.

/// tip
In this case we may keep the router instance reference `router=Base` as part of the
model-path. In this case, the operator cannot select the  routing instance anymore and
it would be hardcoded using the `Base` instance.

As role *physical* is used exclusively for hardware configuration like ports and cards,
in all other cases we use role *logical*. The *category* has no functional meaning
and is rather used as a way to categorize intent-types similar to labels.
///

/// details | Solution
    type: success

``` json
{ 
    "description": "Interfaces creation on Nokia SR OS devices (MD MODE)",
    "category": "interface",
    "role": "logical",
    "device": "XXXXXXXX",
    "context": "nokia-conf:/configure/router=Base/interface",
    "icmstyle": true,
    "exclude": ["egress","ingress","ldp-sync-timer","load-balancing","lag","ptp-hw-assist","autoconfigure","ipsec","cflowd-parameters","hold-time","eth-cfm","ipv6","qos","if-attribute","untrusted","network-domains","external-reference","ipv4/icmp","ipv4/unnumbered","ipv4/urpf-check","ipv4/dhcp","ipv4/bfd","ipv4/secondary","ipv4/neighbor-discovery","ipv4/vrrp"]
}
```
///

/// note | Device Configuration: Interface on PE1
``` bash
(pr)[/]
A:admin@g1-pe1# info configure router interface p1
    port 1/1/c1/1
    ipv4 {
        primary {
            address 10.64.11.1
            prefix-length 31
        }
    }
    ipv6 {
        forward-ipv4-packets true
        address fd00:fde8:0:1:1:11:21:1 {
            prefix-length 127
        }
    }
```
///

Again, import the intent-type into ICM, create a template and deployments. 

#### IS-IS Interface Config

This is now out last step intent-type to bind the new IP interface to the IS-IS protocol.

/// details | Solution
    type: success

``` json
{
    "description": "ISIS Interfaces on Nokia SR OS devices (MD MODE)",
    "category": "interface",
    "role": "logical",
    "device": "XXXXXXXX",
    "context": "nokia-conf:/configure/router=Base/isis=0/interface",
    "icmstyle": true
}
``` 
///

/// note | Device Configuration: ISIS Interface on PE1
``` bash
(pr)[/]
A:admin@g1-pe1# info configure router isis 0 interface p1
    interface-type point-to-point
```
///

Finally, import the intent-type into ICM, create a template and deployments.

/// note | Device Configuration and State: ISIS Interface on PE1
``` bash
(pr)[/]
A:admin@g1-pe1# quit-config 
INFO: CLI #2074: Exiting private configuration mode

[/]
A:admin@g1-pe1# show router isis interface 

===============================================================================
Rtr Base ISIS Instance 0 Interfaces 
===============================================================================
Interface                        Level CircID  Oper      L1/L2 Metric     Type
                                               State                      
-------------------------------------------------------------------------------
system                           L2    1       Up        -/0              p2p
p1                               L1L2  3       Up        10/10            p2p
p2                               L1L2  4       Up        10/10            p2p
-------------------------------------------------------------------------------
Interfaces : 3
===============================================================================

[/]
A:admin@g1-pe1# show  router isis adjacency 

===============================================================================
Rtr Base ISIS Instance 0 Adjacency 
===============================================================================
System ID                Usage State Hold Interface                     MT-ID
-------------------------------------------------------------------------------
g1-p1                    L2    Up    23   p1                            0
g1-p2                    L2    Up    22   p2                            0
-------------------------------------------------------------------------------
Adjacencies : 2
===============================================================================
```
///

## What else could you do???

Brilliant, you've mastered this exercise. Using the community approach with *.igen files
really makes the job of intent-type development easy. Even if you are expert on the node
or management systems - but not soo much a JavaScript/YANG developer.

But you don't need to stop here. Have you already tried the discover a brownfield
configuration from PE1, or did you create a new one? Have you tried to change the
device configuration directly using CLI and then run audits and reconcile? There
are many things to try out. Maybe you just want to get more knowledgeable on
schema-form customization using our new graphical view-config editor. Remind,
the limit is your own creativity.

Here some more asks, if you are overwhelmed by the simplicity of this approach and your
creativity got blocked:

* create an intent-type for customers
* create an intent-type for lag
* create an intent-type for ISIS instance but exclude interfaces.

## Reference

### Intent Type Generator Files

Remember, the starting point for device-specific auto-generation is always an *.igen file, which are in JSON format.
As Visual Studio Code is a text editor, nothing is as easy to create those files.
Here is the list of supported attributes of *.igen files:

| Attribute | Type | Default | Usage |
|---|---|---|---|
| **category** | string | -- | icm_descriptor: helps to categorize the intent (shortcut) |
| **role** | string | -- | icm_descriptor: physical or logical (shortcut) |
| **description** | string | -- | icm_descriptor: description (shortcut) |
| icmDescriptor | dict | {} | icm_descriptor: transparent access to all descriptor fields |
| **context** | string | -- | device-model subtree to cover, example: nokia-conf:/configure/qos/sap-egress |
| **device** | string | -- | ne-id of the device used for auto-generation |
| intent_type | string | *filename of the igen-file* | intent-type name |
| author | string | NOKIA | intent-type author |
| exclude | string[] | [] | list of children subtrees to be excluded |
| maxdepth | number | -1 | maximum depth to cover (deeper hierarchies are excluded) |
| labels | string[] | [] | additional labels, `InfrastructureConfiguration` is always added |
| date | string | today | date used for YANG model revision |
| withdefaults | boolean | false | enable/disable default values in YANG |
| applygroups | boolean | false | enable/disable apply-group statements |
| constraints | boolean | false | enable/disable WHEN statements |
| icmstyle | boolean | false | enable/disable top-level container to match ICM needs |

/// note | Example: demo-icm-sros-sap-ingress-policy.json
``` json
{
    "category": "policies",
    "role": "logical",
    "description": "SAP ingress QoS policy on Nokia SR OS devices (MD MODE)",

    "context": "nokia-conf:/configure/qos/sap-ingress",
    "device": "XXXXXXXX",

    "intent_type": "icm-sros-sap-ingress-policy",
    "author": "hackthon25",
    "exclude": [],
    "maxdepth": -1,
    "labels": ["GraalJS", "ApprovedMisalignments"],
    "date": "2025-02-28",

    "withdefaults": true,
    "applygroups": true,
    "constraints": true,
    "icmstyle": true
}
```
///
