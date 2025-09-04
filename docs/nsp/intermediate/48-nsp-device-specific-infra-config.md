---
tags:
  - NSP
  - Intent Manager
  - Service Management
  - Visual Studio Code
---

# Infrastructure Configuration

|     |     |
| --- | --- |
| **Activity name** | Infrastructure Configuration |
| **Activity ID** | 48 |
| **Short Description** | Auto-generate new device-specific infrastructure intent-types for SR OS and use them with Device Configuration |
| **Difficulty** | Intermediate |
| **Tools used** | NSP, Visual Studio Code |
| **Topology Nodes** | :material-router: PE1 |
| **References** | [Visual Studio Code IM Extension](https://github.com/nokia/vscode-intent-manager) |

## Objective

As a network operator, you probably deal with these common challenges:

* Device configurations are stored in different places (CLI history, text files, templates), so it’s never clear what the configuration baseline is.
* Manual CLI changes creep in over time, introducing drift and making it harder to align devices back to a known state.
* Onboarding new devices or enabling new features often means starting from scratch, repeating the same manual work again.

In this activity, you will:

* Learn how to auto-generate a brand-new intent-type from the device model so you can manage all configuration attributes consistently from day one.
* See how intents, once generated, become the central source of truth — enabling audits, drift detection, and realignment with far less manual effort.
* Understand how this tool-based approach shortens onboarding and provides more flexible options than relying only on pre-defined templates.

In this activity we are use Visual Studio Code (or code-server) with the NSP Intent Manager extension to create device-specific intent-types that can be used in the context of *Device Configuration*.

## Technology explanation

This section describes the concepts used in this activity.

### Visual Studio Code

**[Visual Studio Code (Visual Studio Code)](https://code.visualstudio.com/)** is a free, lightweight, and cross-platform source-code
editor developed by Microsoft, with its core available under [MIT License](https://github.com/microsoft/vscode/blob/main/LICENSE.txt).
While the official Microsoft distribution includes telemetry and branding, the underlying [open-source project](https://github.com/microsoft/vscode)
is actively developed by thousands of contributors worldwide. Backed by Microsoft and deeply integrated with [GitHub](https://github.com/),
Visual Studio Code offers rich extensibility through the [Visual Studio Code Marketplace](https://marketplace.visualstudio.com/vscode), enabling
developers to tailor their development environments with themes, debuggers, linters, and language support.

Visual Studio Code runs seamlessly on **Windows, MacOS X, and Linux**, and powers browser-based development via [code-server](https://github.com/coder/code-server)
and [GitHub Codespaces](https://github.com/features/codespaces). Features like built-in Git support, [Remote SSH](https://code.visualstudio.com/docs/remote/ssh),
IntelliSense, and live share collaboration making it a top choice for developers. The well-documented [extension API](https://code.visualstudio.com/api),
comprehensive [examples](https://github.com/microsoft/vscode-extension-samples), and clean [UX Guidelines](https://code.visualstudio.com/api/ux-guidelines)
encourage a thriving eco-system and consistent user experience.

You can download Visual Studio Code [here](https://code.visualstudio.com/Download) and start exploring the modern, extensible, and developer-friendly environment
shaping how code is written today.

Nokia is actively contributing Visual Studio Code extensions to improve Developer eXperience around our networking products and technologies being used.
In this hackathon, you have the opportunity to use the following extensions contributed by Nokia in action:

* [NSP Intent Manager extension](https://github.com/nokia/vscode-intent-manager)
* [NSP Workflow Manager extension](https://github.com/nokia/vscode-workflow-manager)
* [NSP Artifact Manager extension](https://marketplace.visualstudio.com/items?itemName=Nokia.artifactadminstrator)
* [NSP connect extension](https://marketplace.visualstudio.com/items?itemName=Nokia.nsp-connect)
* [EDA extension](https://marketplace.visualstudio.com/items?itemName=eda-labs.vscode-eda)
* [Containerlab extension](https://github.com/srl-labs/vscode-containerlab)
* [NETCONF extension](https://github.com/nokia/vscode-netconf)


/// warning | Disclaimer
The NSP Intent Manager Extension for Visual Studio Code including the intent-type generator tool is a community-driven open-source initiative. Support status of intent-types generated using Visual Studio Code is experimental! Before using those in production environments, extended testing must be applied to ensure functionality, robustness, usability, performance, and scale.
  
If you encounter issues with the generator tool or the intent-types being created, please submit a support request and share your feedback with the community by raising an issue on GitHub. If you’ve discovered a solution that works for you, we would greatly appreciate it if you contributed your code changes back to the project. In doing so, you become an active part of our community and help it grow.
///


### Intent Manager

Intent Manager is a module within the Nokia Network Services Platform (NSP) that enables intent-based networking (IBN) by translating higher-level objectives into automated network actions. It has the ability to abstract the complexity of network configuration by allowing operators to express what they want, rather than how to do it.

By separating declarative intent configuration (including validation) from intent operations like audits and synchronization, Intent Manager enables CRUD operations with operational lifecycle and control. The sync operation is used for deploying changes into the network but also to reconcile network object configuration in cases of misalignment, while audits are used to identify misalignments including network configuration drift.

The library of intent-types can be updated at runtime, while intent-types are developed in JavaScript using YANG-defined intent models. Using JavaScript enables full flexibility beyond pure configuration management. Intent Manager natively supports heterogeneous networks (multi-vendor, multi-domain).

### NSP Device Configuration

Device Management Configuration is an intent-based app for infrastructure configuration management (ICM). It uses Intent Manager as the engine underneath and comes with an optimized user-interface tailored for the needs of device-centric configuration. ICM adds advanced operational procedures for brownfield configuration discovery and cloning of intent instances.

There is the concept of *device-specific intent-types* in ICM, where a defined subtree of the device is exposed as intent-model. The main rational to use device models is to provide control over 100% of the device-level attributes, while device experts are not confused by any sort of normalization as the intent model is identical to what operators already know. Another advantage of this is that intent-types can be auto-generated. Keep in mind that going device-specific is a compromise, as intent-types become specific to given device vendors, families and releases, adding operational and integration complexity. While there is no abstraction using this approach, all configuration details are accessible via rich configuration forms, and it is possible to adjust those forms to show the relevant configuration attributes only.


## Tasks

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Install / Setup Visual Studio Code and the required extensions

Prepare your environment for creating ICM intents by installing and setting up Visual Studio Code on your computer.

/// tip | Using code-server
If you don't have the necessary privileges to install Visual Studio Code on your computer, the hackathon lab has code-server deployed, so you can run the editor and the extensions from your web-browser.
///

These are the steps you must perform. Below you can also find a short video demonstrating the process.

* Install Visual Studio Code
* Open Visual Studio Code and go to the Extensions sidebar
* Search for "NOKIA Intent Manager" and click "Install" to add the extension to your workspace
* Setup your NSP Connection (Option A, preferred)
    - If you use the *NSP connect* extension, you can configure/connect to your NSP straight from the sidebar
    - Add a new connection targeting your NSP system: `nsp.srexperts.net` with the username/password provided and connect
* Traditional Setup of your NSP Connection (Option B)
    - Open the Settings for the Intent Manager Extension
    - Adjust the connection details for your NSP system: `nsp.srexperts.net` with the username/password provided
    - Change should take effect immediately. In case it does not, please reload Visual Studio Code
* Once done, a new folder named *Intent Manager* appears in your Visual Studio Code workspace
* This folder contains subfolders for intent-types (definitions) and intents (instances). The content you see is polled from the live system.

/// tip | Video: Installing and setting up the extension
-{{video(url="https://gitlab.com/-/project/69754954/uploads/b96983518f12ecd4f7ca064fc71d6745/setup-extension.mp4")}}-
///
  
### Create a new Intent-type and a new Intent Instance

**Create and import intent-types:**

In a directory inside your workspace, create a file named `demo-icm-sros-ip-filter-group01.igen` with the desired NE configuration context, like this:

/// note | Example: `demo-icm-sros-ip-filter-group01.igen`
```json
{
    "description": "L3 ACL for Nokia SR OS devices (MD MODE)",
    "category": "policies",
    "role": "logical",
    "device": "fd00:fde8::1:21",
    "context": "/nokia-conf:configure/filter/ip-filter"
}
```
///

* The filename will become the name of the new intent-type, so it must be in kebap-case.
* The `device` value in your *.igen file must point to the `ne-id` of device with the correct vendor, family, and software release. In case of SR OS routers this is the IPv6 address of the system interface. For this hackathon, you may just select the system IP-address of PE1. The example above is for group 1. Adjust the filename and `device` to match your group!
* Right-click on the *.igen file and select `Generate intent-type` from the context menu.
* The generation might take some time. You can monitor the progress in the Visual Studio Code `OUTPUT` panel.
* Once creation finished, verify the contents of the generated intent-type.
* Right-click on the intent-type folder and select `Upload intent-type` from the context menu.
* The intent-type should appear on the [NSP WebUI](https://nsp.srexperts.net/web/intent-manager/intent-types) in `Released` state

To get a more detailed understanding about *.igen files, please check in the [reference section](#reference-intent-type-generator-files) below.

/// tip
Spend some time to go through the generated code. The intent-type uses a visionary modular design. Resources in the `common` folder are the same for all intent-types generated. A default view-config is created to improve WebUI usability. The main files that contain custom code are the YANG module and the `script-content.mjs`. If you've designed intent-types for NSP before, you may recognize the object-oriented design. Be aware, this takes advantage of the new JavaScript engine (GraalJS), that is available since NSP 24.11.
///

/// hint
To create an `ip-filter` in model-driven SR OS, you must provide both the `IP Filter Name` and the `Filter ID`. While the `Filter ID` is optional in the underlying YANG model, creating filters by name alone would require automatic identifier assignment, which is not enabled by default. The same principle applies to other nodal configuration objects such as customers and services.
///

**Import intent-types and creating templates in ICM**:

* Navigate to `Device Management > Configuration Intent Types`.
* Import the newly created intent-type.
* Navigate to `Configuration Templates`.
* Create a new template using your intent-type.

**Create an intent**:

Now you can move further to `Configuration Deployments`.

* Create a new deployment using the previous template.

/// tip | Example solution: Creating a new intent-type and intent instance to enable a port
-{{video(url="https://gitlab.com/-/project/69754954/uploads/c6334e7d83192a2d5e6aa5522825cb2c/enable-port.mp4")}}-
///

We've just learned step-by-step on how to quickly create brand new intent-types from small *.igen files. Now, turn is on you to create all required intent-types required for base router connectivity: Port Configuration, Interface Configuration and IS-IS Interface Configuration.

### Port Config

Let's start with port configuration.

/// tip
The most important part when creating *.igen files is device-model path. This is where the subtree starts, that is "owned" by the corresponding intents. In SR OS MD-CLI one can use the command `pwc model-path` to retrieve the corresponding string. You should consider removing the list-key identifiers along the path, to make those identifiers part of the intent target.

You may decide to exclude certain children's subtrees from the intent-type to reduce the intent complexity and to speed up rendering time using the `exclude` and/or `max-depth` statements.

For port configuration use `role: physical` and `category: port`.
///

/// details | Solution
    type: success

``` json
{ 
    "description": "Port configuration on Nokia SR OS devices (MD MODE)",
    "category": "port",
    "role": "physical",
    "device": "fd00:fde8::1:21",
    "context": "nokia-conf:/configure/port",
    "icmstyle": true,
    "maxdepth": 2,
    "exclude": ["sonet-sdh","tdm","otu","network","gnss","dwdm","access","scheduler","transceiver","dist-cpu-protection","ethernet","hybrid-buffer-allocation","modify-buffer-allocation"]
}
```

The example *.igen file above excludes `ethernet` attributes. If you want attributes such as mode, encapsulation, or mtu-size to be accessible from your intent-type, you can remove the `ethernet` context from the `exclude` list. Keep in mind that the `ethernet` subtree is relatively large, which will add significant detail to the configuration forms and increases the time required to generate the intent type.

Once again, be sure to update the `device` attribute so it matches the `PE1` node for your group. The example shown above corresponds to `group 1`.
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

(pr)[/]
A:admin@g1-pe1# configure port 1/1/c1

(pr)[/configure port 1/1/c1]
A:admin@g1-pe1# pwc model-path 
Present Working Context:
/nokia-conf:configure/port=1%2F1%2Fc1
```
///

Now, import the intent-type into ICM, create a template and deployments.

### Interface Config

We continue with the IP interface configuration associated with the `Base` router instance.

/// tip
Since the interfaces we configure in this section always reside in the `Base` routing instance, there is no need to remove that element from the model path. This avoids requiring an unnecessary selection. When creating your *.igen file, ensure that this selection filter is included in the model path.

The role *physical* is reserved for hardware configuration such as ports and cards. In all other cases, we use the role *logical*. The category field has no functional impact; it simply serves to group intent-types in a label-like manner.
///

/// details | Solution
    type: success

``` json
{ 
    "description": "Interfaces creation on Nokia SR OS devices (MD MODE)",
    "category": "interface",
    "role": "logical",
    "device": "fd00:fde8::1:21",
    "context": "nokia-conf:/configure/router=Base/interface",
    "icmstyle": true,
    "exclude": ["egress","ingress","ldp-sync-timer","load-balancing","lag","ptp-hw-assist","autoconfigure","ipsec","cflowd-parameters","hold-time","eth-cfm","ipv6","qos","if-attribute","untrusted","network-domains","external-reference","ipv4/icmp","ipv4/unnumbered","ipv4/urpf-check","ipv4/dhcp","ipv4/bfd","ipv4/secondary","ipv4/neighbor-discovery","ipv4/vrrp"]
}
```

Quick reminder: have you updated the `device` attribute to match your group?
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

As already done previously, import the intent-type into ICM, create a template and deployments. 

### IS-IS Interface Config

As a final step, create an intent-type that will allow operators to associate router network interface with the IS-IS protocol in model-driven SR OS using the NSP WebUI.

/// details | Example solution
    type: success

``` json
{
    "description": "ISIS Interfaces on Nokia SR OS devices (MD MODE)",
    "category": "interface",
    "role": "logical",
    "device": "fd00:fde8::1:21",
    "context": "nokia-conf:/configure/router=Base/isis=0/interface",
    "icmstyle": true
}
``` 

Hackathon activities are not meant to be simple copy-and-paste exercises. Even if you rely on the provided example solution, be sure to update the `device` attribute before generating the intent-type.

///

/// note | Device Configuration: ISIS Interface on PE1
``` bash
(pr)[/]
A:admin@g1-pe1# info configure router isis 0 interface p1
    interface-type point-to-point
```
///

Finally, import the intent-type into ICM, create a template and deployments.

/// hint
The generated intent-type uses the *string with autocomplete* schema-form widget to specify the ISIS interface name to be created. Existing ISIS interfaces on the node serve as the data source, which works well for creating intents in brownfield scenarios. For greenfield cases, you can simply enter the name of the ISIS interface to be created, ensuring it matches the name of the underlying *Base* router interface. To better support greenfield scenarios, you may adjust the suggest callback by modifying the path statement in `script-content.mjs` from `nokia-conf:/configure/router=Base/isis=0/interface` to `nokia-conf:/configure/router=Base/interface`.
///


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

## Summary

Well done — you’ve successfully completed this activity! By working with community-driven *.igen files, you’ve seen how intent-type development can be greatly simplified. This approach lets you focus on the network and management aspects without needing to be an expert in JavaScript or YANG.

But this is just the beginning. You might explore discovering a brownfield configuration from PE1, experiment by changing device settings directly through the CLI and then running audits and alignment, or dive deeper into schema-form customization with the graphical view-config editor.

The possibilities are wide open — how far you go is up to your curiosity and creativity.

## Reference: Intent-type Generator Files

The starting point for device-specific auto-generation is always an *.igen file, provided in JSON format. Since Visual Studio Code is a text editor, creating these files is straightforward. Below is the list of supported *.igen file attributes:

| Attribute | Type | Default | Usage |
|---|---|---|---|
| **category** | string | -- | icm_descriptor: helps to categorize the intent (shortcut) |
| **role** | string | -- | icm_descriptor: physical or logical (shortcut) |
| **description** | string | -- | icm_descriptor: description (shortcut) |
| **icmDescriptor** | dict | {} | icm_descriptor: transparent access to all descriptor fields |
| **context** | string | -- | device-model subtree to cover, example: nokia-conf:/configure/qos/sap-egress |
| **device** | string | -- | ne-id of the device used for auto-generation |
| **intent_type** | string | *filename of the *.igen file* | intent-type name |
| **author** | string | NOKIA | intent-type author |
| **exclude** | string[] | [] | list of children subtrees to be excluded |
| **maxdepth** | number | -1 | maximum depth to cover (deeper hierarchies are excluded) |
| **labels** | string[] | [] | additional labels, `InfrastructureConfiguration` is always added |
| **date** | string | today | date used for YANG model revision |
| **withdefaults** | boolean | false | enable/disable default values in YANG |
| **applygroups** | boolean | false | enable/disable apply-group statements |
| **constraints** | boolean | false | enable/disable WHEN statements |
| **icmstyle** | boolean | false | enable/disable top-level container to match ICM needs |

/// note | Example: demo-icm-sros-sap-ingress-policy.json
``` json
{
    "category": "policies",
    "role": "logical",
    "description": "SAP ingress QoS policy on Nokia SR OS devices (MD MODE)",

    "context": "nokia-conf:/configure/qos/sap-ingress",
    "device": "fd00:fde8::1:21",

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