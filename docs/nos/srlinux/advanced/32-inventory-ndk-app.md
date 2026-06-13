---
tags:
  - SR Linux
  - NDK
  - Go
  - SR Linux
  - NDK
  - Golang
  - Python
  - Go
  - CLI plugin
---

# Extending SR Linux using the NDK: The Inventory App


|                             |                                                                                                                                                                                                                        |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Extending SR Linux using the NDK: The Inventory App  |
| **Activity ID**             | 32                                                                |
| **Short Description**       | Using the NetOps Development Kit (NDK), you can extend the data model of SR Linux to store information about the location of the switch. |
| **Difficulty**              | Advanced |
| **Tools used**              | [Go](https://go.dev)<br/>Bash<br/>[NetOps Development Kit](https://learn.srlinux.dev/ndk/)<br/>Any code editor (e.g. the hosted VS Code)                             |
| **Topology Nodes**          | :material-router: leaf21, :material-router: spine21                                                                              |
| **References**              | [NetOps Development Kit](https://learn.srlinux.dev/ndk/)<br/>[Go](https://go.dev)                                                         |

You are in the middle of a network upgrade, working together with your data center engineer colleagues who are busy racking and stacking. As you are verifying connectivity from the CLI in preparation for the network expansion, you get a message from one of the engineers in the DC: "Hey, what rack is this switch in again?"  
You can always look this up in your DCIM (Data Center Infrastructure Management) system, but have you ever wondered why your switch can't just... tell you where it is? Why is there no `show system location` command?

SR Linux does not come with rack ID and elevation in its data model, but with a little motivation, some elbow grease and cursory knowledge of the NetOps Development Kit (NDK), you can teach a new switch even newer tricks.

This activity demonstrates how you can use the NDK to extend the data model of SR Linux, use the data model, and query it from a custom `show` command CLI plugin.

## Prerequisites

This task will require you to be familiar with programming in order to complete on your own. If you are not versed in Go and Python, don't fret, because you can still follow along, albeit you will have to do more cut-and-paste than usual!  

As this is a programming task, please set some time aside for it, to allow you to understand what the code does, and how.

## Objective

For this activity, you have three main goals: 

1. Extend the data model of SR Linux by creating a custom YANG (Yet Another Next Generation) model
2. Create the NDK application to load the custom YANG model
3. Query the custom YANG model via a newly added `show` command.

This activity follows the development lifecycle of most NDK apps - an NDK binary to extend or enhance the featureset of the switch, a YANG model to let the application communicate with its users, and a CLI plugin to make the use of the app easier.

An initial, proof of concept version of this app has already been made by a colleague of yours, your task is to finish the development of the app, and bump that version number up to a nice even `1.0.0`!

At the end of this activity, you will be able to use the application to tell your colleague where the switch is, without leaving the SR Linux CLI!

## Technology explanation

This activity is programming-heavy - you will tackle YANG, Go and even Python at the same time! As an in-depth introduction to all of these languages would be a lot to chew, you will be provided with _skeletons_ of code, but you will need to complete the code for full functionality.

### YANG (Yet Another Next Generation)

YANG models are the lifeblood of SR Linux: no app can run without them, including the official Nokia applications! This ensures that no matter what method you use, be it gNMI, NETCONF, or even the CLI, to retrieve the state of applications, you will get the same consistent experience. But what is YANG, you might ask?

YANG is a data modelling language used to model the configuration and state data of network elements. It is a protocol-independent, thus can be converted into various formats, like XML or JSON, or even YAML.

A _module_ is the topmost hierarchical module in YANG. Inside a module are one or multiple _nodes_. Nodes can have multiple types, but this activity will focus on two specific types today: **container** and **leaf** nodes.  
_Container_ nodes are used to group related nodes - they do not contain any values directly, only child nodes. _Leaf_ nodes have a value, and this value can have many types, like a string, an integer, or even a reference to another leaf node. Leaf values are terminating nodes in a YANG tree, their values cannot be containers.  

As an analogy for readers with programming experience, _containers_ can be thought of as dictionaries (or hash-maps), while each _leaf_ is a key-value pair.

Leaf nodes can have different properties that help describe their behaviour - for example, the `config` property describes whether a leaf node is writeable (configurable) or not (read-only, state). The default value for this is true.  

Other properties, such as the `default` property, can be used to set the default value of the leaf node, and `range` can be used to limit the possible values of an integer type leaf node.

For example, a YANG model of a car would look something like this:

```
module example-car {
  yang-version 1.1;
  namespace "https://github.com/nokia/srexperts";
  prefix example-car;

  description
    "Car module";

  revision 2026-06-16 {
    description
      "initial release";
  }

  container car {
    leaf name {
      type string;
      description
        "Nickname of the car";
    }
    leaf speed {
      type uint16;
      description
        "Set speed of the car in km/h";
    }
    leaf odometer {
      type uint32;
      config false;
      description
        "Show how many kilometers the car has travelled";
    }
    container trunk {
      description
        "Everything related to the trunk";
      leaf usage {
        type uint8 {
          range "0..100";
        }
        config false;
        description
          "How full the trunk is, in percentage";
      }
      leaf open {
        type boolean;
        description
          "Trunk door status";
      }
    }
  }
}
```

For example, the YANG path `/car/name` represents the nickname of the car - it can be configured to your heart's content to any string of characters. The mile counter located at `/car/odometer` is something you can only read - much like in real life.  
If you want to figuratively peek in the trunk, `/car/trunk/open` should be set to `true`. You can see how full the trunk is in the `/car/trunk/usage` `leaf` node - as this is a percentage representation, the value can only be between `0` and `100`.
The path `/car/trunk` might look enticing to put something into, but it is a `container` node - it is not possible to store any value in it, it only helps with hierarchical grouping of other nodes.

For the purposes of this activity, you will not have to do any difficult data modelling - just a `container` and a few `leaf` nodes! The only leaf node types you will be using are `string` and `uint8`, which correspond to arbitrary text, and 8-bit unsigned integers respectively.  

### NetOps Development Kit (NDK)

Nokia SR Linux enables its users to develop and create applications that run alongside native apps on the SR Linux network OS. These "on-box custom applications" can deeply integrate with the rest of the SR Linux system, and can achieve things that are not possible to perform with traditional off-box automation.

These on-box custom applications, that we like to refer to as "agents", leverage the SR Linux development kit called **NetOps Development Kit** (or NDK for short).

NDK agents seamlessly integrate with SR Linux, and appear like any native application, like BGP or ACLs. The integration is achieved on multiple levels: 

- They run as any other native application
- They use the same lifecycle management
- They present their management interface by exposing configuration and state via the same management YANG tree as native applications
- They integrate natively into the real-time streaming telemetry framework of SR Linux


NDK agents not only provide configuration and state management, but also get access to SR Linux internals, allowing deep integration, letting you listen to RIB/FIB updates, or even have direct access to the data path. Pretty cool, eh?

NDK applications cannot run out of the box on SR Linux - as not all customers require running NDK apps - first, the NDK server must be enabled in the SR Linux configuration.

This task will not delve deep into the possibilities that the NDK offers - this agent will merely let you save location information into the data model.

### CLI Plugins

The pluggable architecture of SR Linux CLI allows you to create custom CLI commands using the same infrastructure as the native SR Linux commands.

The Python-based CLI engine allows a user to create the custom CLI commands in the following categories:

- **show** commands  
    These are your much-loved show commands that print out the state of the system in a human-readable format, often in a table.
- **global** commands  
    These are operational commands like `ping`, `traceroute`, `file`, `bash`, etc.
- **tools** commands  
    These represent a run-to-completion task or an operation. Like a reboot or a request to load a configuration from a file.

/// note

The configuration commands are not implemented as CLI plugins, they directly modify the candidate configuration datastore and are not subject to customization.

///

The CLI plugins infrastructure is used to support both SR Linux native and custom commands. Users can add their own command simply by putting a Python file in one of the directories used in the CLI plugin discovery process.

When the SR Linux CLI is started, the available commands (native and user-defined) are loaded by the engine based on the plugin discovery process that scans the known directories for Python files implementing the `CliPlugin` interface.

You will extend an existing `show` CLI plugin, which will display granular inventory location data in a formatted manner.

## Tasks

As part of this activity, you will first deploy the NDK app, then modify it to fit your needs.

### Enabling the NDK server

For security purposes, the NDK server (through which all NDK applications communicate) is disabled by default. The [NDK architecture documentation](https://learn.srlinux.dev/ndk/guide/architecture) provides an overview of how the NDK service (or server) is used by NDK applications to interact with the rest of the SR Linux NOS.

Your first task will be to first enable the NDK server on both switches you will be working on, :material-router: leaf21 and :material-router: spine21.
 
To verify the NDK server is running, use the `info from state /system ndk-server` command.

/// details | Enabling the NDK server

/// tab | Commands

To make changes to the configuration on SR Linux, don't forget to first enter the candidate datastore:

```
enter candidate
```

Enable the NDK server:

```
set system ndk-server admin-state enable
```

Commit the changes:

```
commit now
```

///

/// tab | Expected output

```{.text .no-copy .no-select}
# Run on both leaf21 and spine21
--{ running }--[  ]--
A:admin@leaf21# enter candidate

--{ candidate shared default }--[  ]--
A:admin@leaf21# set system ndk-server admin-state enable

--{ * candidate shared default }--[  ]--
A:admin@leaf21# commit now
```

///

/// tab | Verification

```
--{ running }--[  ]--
A:admin@leaf21# info from state / system ndk-server
    admin-state enable
```

///

///

### Setting up your development environment

The section is split into three segments:

1. Preparing the YANG model
2. Finishing the NDK app and deploying it
3. Adding the CLI plugin you developed into the plugins folder


You will find the task skeleton repository already cloned to your Hackathon instance in the `~/SReXperts/activities/nos/srlinux/activity-32` directory.

Let's make a copy of this directory to use as your work environment! We recommend that you use the VS Code web editor for this task, and use its built-in terminal to execute commands.

```bash
cp -r ~/SReXperts/activities/nos/srlinux/activity-32 ~/inventory-ndk-app
cd ~/inventory-ndk-app
# or open the newly copied directory in VS Code
```

Inside this directory, you can already try building the NDK app. Since you need to first get some Go module dependencies, and run the build command with additional build flags, we have supplied a helper script called `run.sh`.

```bash
# To build the app, use the helper script
./run.sh build-app 
```

Issuing this command will first perform _linting_ on the code, pull all dependencies of the application (including the NDK library), and then build the Go application. The resulting NDK agent binary will be output to the `./build/` directory.

Before you can get on with initial deployment, an important change needs to be made to the agent: the password must be correctly set for the NDK application to be able to authenticate against the gRPC server running on the switch!  
At the moment, this is set to the factory-default - you should change it before proceeding any further!

```diff title="main.go"
const (
  defaultUsername = "admin"
- defaultPassword = "${DEFAULT_PASSWORD}"
+ defaultPassword = "${EVENT_PASSWORD}"
)
```

### Initial deployment

To deploy the freshly built SR Linux NDK application, you will have to copy some files to an SR Linux node, let's use :material-router: leaf21.  

How can you tell what file to copy where? The [application configuration file](https://learn.srlinux.dev/ndk/guide/agent/#application-manager-and-application-configuration-file) `inventory.yml` will tell you!

*Can you identify where the different parts of the application should be copied?*

/// details | NDK install destination
The installation is to be done in the `/home/admin/inventory` directory. You should ensure this directory exists by running the `bash mkdir /home/admin/inventory` command on the switch.

The binary should be placed at the `/home/admin/inventory/inventory` path, while the directory containing the YANG models should be located at `/home/admin/inventory/yang`.
///

*The files should be copied using the `scp` command, which lets users copy files through SSH access.*

/// warning

The `scp` copy process might take a while! This is due to control plane policing behaviour in the containerized SR Linux simulator.

///

/// details | Delivering the NDK application files
The main binary file and the YANG directory needs to be copied over to the paths defined in the `inventory.yml` application configuration file.

```bash
# make sure the /home/admin/inventory directory exists
scp ./build/inventory admin@clab-srexperts-leaf21:/home/admin/inventory/inventory
# -r is the recursive flag needed for copying entire directories
scp -r ./yang admin@clab-srexperts-leaf21:/home/admin/inventory/yang
```
///

*Once you copy over the NDK application binary and the YANG modules to the switch, can you start using them immediately?*

/// details | NDK application deployment
No, since SR Linux has no information about this NDK app, or the YANG models you copied over.  
The application manifest contains this information, which might not be copied over yet.
///

If you haven't already, you will also need to ship the application manifest on the switch. This can be done by copying the file over to the [correct location](https://learn.srlinux.dev/ndk/guide/agent-install-and-ops/#loading-the-agent) on the file system.  

Once this is done, *reload the App Manager in order to load the newly-deployed NDK application!* You can use the `show system application inventory` command to verify that your NDK application loaded correctly.

/// details | Loading NDK applications
To copy over the application manifest, you need to `scp` it:

```bash
scp ./inventory.yml admin@clab-srexperts-leaf21:/etc/opt/srlinux/appmgr/inventory.yml
```

Following this step, you also need to reload the App Manager in order to load the NDK application configuration file, and by doing so, let the App Manager start the application itself:

/// tab | Command

```text
tools system app-management application app_mgr reload
```

///

/// tab | Expected output

```{.text .no-copy .no-select}
# SSH into the switch first
--{ running }--[  ]--
A:admin@leaf21# tools system app-management application app_mgr reload

--{ running }--[  ]--
A:admin@leaf21# show system application inventory
  +-----------+------+---------+---------+--------------------------+
  |   Name    | PID  |  State  | Version |       Last Change        |
  +===========+======+=========+=========+==========================+
  | inventory | 8553 | running | 0.8.0   | 2026-04-10T15:20:17.849Z |
  +-----------+------+---------+---------+--------------------------+
```

If you see that the application is not healthy (or keeps restarting), make sure that you changed the gRPC password in the NDK application's source code!  
The application logs are located in `/var/log/srlinux/debug/ndk_inventory.log`

///

///


**You have successfully deployed your NDK app by hand!**

### Using the NDK app

Just like any part of the built-in SR Linux configuration model, you can now leverage the newly-loaded YANG to configure the location of the switch.  

Let's say that the :material-router: leaf21 switch is located in "DC-Left Rack 1"!  
*Configure this location for the inventory app, and confirm that the state data model contains the entry with `info from state`.*  

For the seasoned gNMI users, *try querying the switch's location using `gnmic`!*

/// details | Configuring the location of the switch

/// tab | Commands

```text
set inventory location "DC-Left Rack 1"
```

```text
info from state /inventory location
```

///

/// tab | Expected output

```{.text .no-copy .no-select}
--{ running }--[  ]--
A:admin@leaf21# enter candidate

--{ candidate shared default }--[  ]--
A:admin@leaf21# set inventory location "DC-Left Rack 1"

--{ * candidate shared default }--[  ]--
A:admin@leaf21# diff
      inventory {
+         location "DC-Left Rack 1"
      }

--{ * candidate shared default }--[  ]--
A:admin@leaf21# commit stay
All changes have been committed. Starting new transaction.

--{ + candidate shared default }--[  ]--
A:admin@leaf21# info from state /inventory location
    location "DC-Left Rack 1"
```

///

///

/// details | Optional: Querying the switch location via gNMI

```bash
gnmic -a clab-srexperts-leaf21 --port 57400 --insecure -u admin -p ${EVENT_PASSWORD} -e json_ietf get --path /inventory/location
```

<div class="embed-result">

```{.json .no-copy .no-select}
[
  {
    "source": "leaf21",
    "timestamp": 1776428150633962254,
    "time": "2026-04-17T14:15:50.633962254+02:00",
    "updates": [
      {
        "Path": "inventory:inventory/location",
        "values": {
          "inventory:inventory/location": "DC-Left Rack 1"
        }
      }
    ]
  }
]
```

</div>

///

It would be much simpler to use the application with a proper "show" command - we have one already packaged for you to use in the `./plugin` directory!  

Using the [SR Linux CLI plugin guide](https://learn.srlinux.dev/cli/plugins/#user-defined-commands), *deploy the Python CLI plugin to :material-router: leaf21*, and try out the new command `show location` in the CLI!  

/// tip

After deploying the CLI plugin to the switch, make sure to logout and log back into the SR Linux CLI, as plugins are loaded on the initialization of the CLI.

///

/// details | Deploying and using the CLI plugin "show location"

The guide mentions that there are two locations where user-defined commands can be installed: `/etc/opt/srlinux/cli/plugins/` (for system-wide installations) and `/home/<username>/cli/plugins/`.  
For the sake of simplicity, you should install the plugin system-wide, by copying the Python CLI plugin to `/etc/opt/srlinux/cli/plugins/show_location.py`.

```bash
scp plugin/show_location.py admin@clab-srexperts-leaf21:/etc/opt/srlinux/cli/plugins/show_location.py
```

You can then use the added show command after logging out and logging back in to the SR Linux CLI:

```{.text .no-copy .no-select}
--{ + running }--[  ]--
A:admin@leaf21# show location
---------------------------------------
Location: DC-Left Rack 1
---------------------------------------
```

///

### Deploying to :material-router: spine21

Instead of repeating these same steps for :material-router: spine21, you can use the helper script `./run.sh` to deploy the NDK application and the plugin to the switches.

*Run the `./run.sh` script with the `deploy-app` command, and verify that the NDK application and its plugin also correctly works on :material-router: spine21!*

/// details | Deploying the app using the helper script

/// tab | Deploying on both switches

Deploying to both switches can be done by simply running the following:

```bash
./run.sh deploy-app
```

<div class="embed-result">

```{.text .no-copy .no-select}
Linting YAML files
Building application
Stopping NDK application
Copying application to nodes
Reloading application manager
Starting NDK application

Task completed in 3m15.254s
```

</div>

///

/// tab | Verification

```bash
ssh spine21
```

<div class="embed-result">

```{.text .no-copy .no-select}
--{ running }--[  ]--
A:admin@spine21# enter candidate

--{ candidate shared default }--[  ]--
A:admin@spine21# set inventory location "Some Location"

--{ * candidate shared default }--[  ]--
A:admin@spine21# commit now
All changes have been committed. Leaving candidate mode.

--{ + running }--[  ]--
A:admin@spine21# show location
---------------------------------------
Location: Some Location
---------------------------------------
```

</div>

///

///

By the end of this section, **you have learned how to build and deploy NDK applications and CLI plugins.** In the next section, you will modify the NDK application!

### Modifying the data model

The inventory NDK app in its current form can only store a string - this is an issue for storing granular information. However, since you have full control of the application's code, you can make changes to the application's behaviour!

Your first task in this section will be to modify the YANG model and add three additional, more granular inventory fields: **site, room, rack and elevation**.  

These new leafs should all be all configurable strings, except for the elevation, which should be an unsigned integer, and should only accept values from 1 to 42. Don't forget to also create a new revision entry in the YANG!

*Modify the YANG model, deploy it to the switches, and try setting these new fields! Try what happens if you try to set an invalid rack elevation value (e.g. 100)!*

/// details | Modifying the YANG model with granular location information

Let's add the three new leafs to the `inventory` container: 

```diff
...
    container inventory {
        leaf location {
            description "Node location";
            type string;
            config true;
        }
+       leaf site {
+           description "Site";
+           type string;
+           config true;
+       }
+       leaf room {
+           description "Room";
+           type string;
+           config true;
+       }
+       leaf rack {
+           description "Rack ID";
+           type string;
+           config true;
+       }
+       leaf elevation {
+           description "Position inside rack";
+           type uint8 {
+               range "1..42";
+           }
+           config true;
+       }
    }
```

A revision should also be added to the YANG, to keep track of changes:

```diff
+   revision "2026-06-17" {
+       description
+           "add granular location data";
+   }
```

Finally, deploy it to the switch using the automated script, and commit some values:

/// tab | Commands

```text
set inventory site "Test Site"

set inventory rack A123

set inventory room 0451

set inventory elevation 32
```

///

/// tab | Expected output

```diff
A:admin@leaf21# diff
      inventory {
+         site "Test Site"
+         rack A123
+         room 0451
+         elevation 32
      }
```

///

It is not possible to set an elevation value out of bounds:

```{.text .no-copy .no-select}
--{ + candidate shared default }--[  ]--
A:admin@leaf21# set inventory elevation 100
Parsing error: While parsing 'elevation': Wrong value for 'value': Got '100' expected 1..42
```

///

Once you have set the new granular values, try querying these from _both_ running and state!  

*What do you observe? Why do you think this is the case?*

/// details | Explanation

```{.text .no-copy .no-select}
--{ + running }--[  ]--
A:admin@leaf21# info /inventory
    location "DC-Left Rack 1"
    site "Test Site"
    room 0451
    rack A123
    elevation 32

--{ + running }--[  ]--
A:admin@leaf21# info from state /inventory
    location "DC-Left Rack 1"
```

The new leafs are only present in the _running_ datastore!

///

The lack of information in the state is surprising, but easily explained: committing the candidate configuration only copies the values to the `running` datastore, not to state as well.  

The NDK application is responsible for generating the contents of the state linked to the application!

This means you will have to modify the NDK application's code before you will see the inventory location data reflected in the state.

### Modifying the NDK application - Adding the new model fields

Modify the NDK application, so the state will also contain the new fields!

The code for the NDK app is organized as follows:

```{.text .no-copy .no-select}
main.go     # The entrypoint of the application - initializes the NDK agent connection and logging
inventory/
  app.go    # The main loop of the application
  config.go # Processing of configuration (e.g. when a new commit is made)
  state.go  # Maintaining the state
```

*Can you explain the main loop of the application?*

/// details | Main event loop of the application

```go title="inventory/app.go"
func (a *App) Start(ctx context.Context) {
	for {                                                   // Loop starts here - no limits, infinite loop
		select {                                            // The select keyword allows you to wait for values (or rather, notifications in this case) - two channels (or queues) are open  
		case <-a.NDKAgent.Notifications.FullConfigReceived: // This channel will receive a notification when a commit is made in SR Linux
			a.logger.Debug().Msg("Received full config")

			a.loadConfig()                                  // First load the incoming configuration from SR Linux

			a.processConfig()                               // Process the config, make changes to the agent

			a.updateState()                                 // Update the state datastore

		case <-ctx.Done():                                  // This channel will receive a notification when the application receives a shutdown signal
			return                                          // Break out of the loop if we need to shut down
		}
	}
}
```

///

If you look at the code, you will see that it is fairly straightforward:

- `loadConfig()`:  
   The configuration data is sent in JSON format and is unmarshalled - that is, parsed and loaded into an internal `ConfigState` data structure - and saved to an internal variable `configState`
- `processConfig()`:  
   No processing is performed
- `updateState()`:   
   The internal variable `configState` is marshalled (turned into a JSON string) and written back to the state datastore.

*Why do you think the state datastore does not contain the newly-introduced leafs?*

/// details | Why the leafs are missing

The key to answering this question lies in the unmarshalling step. When the configuration data JSON is parsed, the `ConfigState` data structure is used as a "pattern" which defines what fields of the JSON get loaded where in the internal data structure.  

```go
type ConfigState struct {
	// Location is the non-granular location string
	Location string `json:"location,omitempty"`
}
```

Since the `ConfigState` data structure only has a mapping for the `location` leaf, the other leafs in the `inventory` YANG container are ignored.

///

To make this work, *you will need to add the newly-added leafs in YANG model to the `ConfigState` data structure as well!* To add new members to the data structure, you will have to give them a name, a type and an annotation (between backticks).  

/// tip

- Hint \#1: The received configuration JSON is logged to the `/var/log/srlinux/debug/ndk_inventory.log` file.  
- Hint \#2: Not all structure members are going to be strings!  
- Hint \#3: The JSON (un)marshalling utilizes the field name in the annotation.
- Hint \#4: All fields should be capitalized - this makes the field public, which is a requirement for marshalling it.

///

/// details | Adding the leafs to the NDK app configuration data structure

Simply populate the data structure with the additional YANG leafs.

```diff
type ConfigState struct {
	// Location is the non-granular location string
	Location  string `json:"location,omitempty"`
+	Site      string `json:"site,omitempty"`
+	Room      string `json:"room,omitempty"`
+	Rack      string `json:"rack,omitempty"`
+	Elevation uint8  `json:"elevation,omitempty"`
}
```

The unmarshalling process will load the data from the received config JSON into the data structure, and when the state is written back, the reverse process happens - the data structure's contents are turned into a JSON string.

///

After the Go data structure is updated with the new leafs, *try re-deploying the app, and see the freshly-reloaded app populate the state with the new leafs!*

```
--{ + running }--[  ]--
A:admin@leaf21# info from state /inventory
    location "DC-Left Rack 1"
    site "Test Site"
    room 0451
    rack A123
    elevation 32
```

Once you have verified the correct functionality, it's time to ceremoniously update the version number!  

You are not done with the application yet, so let's motivate ourselves by bumping the version up to `0.9.0` :smile:

```diff title="main.go"
- var version = "0.8.0"
+ var version = "0.9.0"
```

### Modifying the NDK app - Adding logic to the application

So far, your application has been essentially copying the configuration to the state datastore. Let's make it _actually_ do some work for us!

The `location` leaf is part of the original YANG model, currently a free text entry configuration leaf. *Let's turn it into an automatically generated state leaf instead!*

First, you will need to delete it from the committed configuration, as you will be making changes to the underlying YANG:

```{.text .no-copy .no-select}
--{ + candidate shared default }--[  ]--
A:admin@leaf21# delete inventory location

--{ +* candidate shared default }--[  ]--
A:admin@leaf21# diff
      inventory {
-         location "hello world"
      }

--{ +* candidate shared default }--[  ]--
A:admin@leaf21# commit stay
All changes have been committed. Starting new transaction.
```

Following this step, your tasks are the following:

- Modify the YANG model to make the `location` leaf a state (read-only) leaf.  
- Add a step to the configuration processing function `processConfig` to set the `Location` field in the `configState` data structure to a generated string in the following format:

    `<Site> // <Room> - <Rack>:<Elevation>`

/// tip


- Hint \#1: The variable holding the `ConfigState` structure can be accessed as `a.configState`  
- Hint \#2: The function [`fmt.Sprintf`](https://pkg.go.dev/fmt#Sprintf) can be used to create strings based on templates: `%s` can be used to substitute in strings, `%d` is for integers.  
- Hint \#3: The `fmt.Sprintf` function can take multiple arguments, and will substitute them in order. The number of arguments and format "verbs" (e.g. `%s`) must match.  
- Hint \#4: If you are not using the Visual Studio Code IDE, you will also have to add the `"fmt"` package to the imports in `config.go`

///

/// details | Generating location from other configuration items

First, adjust the YANG model to make the `location` leaf read-only/state:

```diff
+   revision "2026-06-18" {
+       description
+           "location is now a state";
+   }
    container inventory {
...
        leaf location {
            description "Node location";
            type string;
-           config true;
+           config false;
        }
...
    }
```

Then, we need to add the code to generate the `Location` data structure field from the other fields in the `processConfig` function:

```go title="inventory/config.go"
// Note: the "fmt" package has been added to the imports above!

func (a *App) processConfig() {
	a.configState.Location = fmt.Sprintf(
		"%s // %s - %s:%d", 
		a.configState.Site, a.configState.Room, a.configState.Rack, a.configState.Elevation,
	)
}
```

///

Once you are done re-deploying the application, you can already see the fruits of your labor by running a `show location` or `info from state /inventory`:

```{.text .no-copy .no-select}
--{ running }--[  ]--
A:admin@leaf21# show location
---------------------------------------
Location: Test Site // 0451 - A123:32
---------------------------------------

--{ running }--[  ]--
A:admin@leaf21# info from state /inventory
    location "Test Site // 0451 - A123:32"
    site "Test Site"
    room 0451
    rack A123
    elevation 32
```

To verify that the location is no longer part of the running configuration datastore, check `info /inventory`:

```{.text .no-copy .no-select}
--{ running }--[  ]--
A:admin@leaf21# info /inventory
    site "Test Site"
    room 0451
    rack A123
    elevation 32
```

Congratulations! You have modified and deployed your own version of an NDK app! You are now a certified SR Linux coder 😎

Don't forget to update the version number to a victorious `1.0.0`!

```diff title="main.go"
- var version = "0.9.0"
+ var version = "1.0.0"
```

## Summary and review

Congratulations!  You have managed to create your own SR Linux application that runs alongside the native SR Linux applications and provides your team with the necessary information they need to make physical interactions within the data-center easier.

By getting this far, you have:

- Created your own YANG model and extended the SR Linux data model by loading it
- Developed a configurable SR Linux NDK application with its own data model
- Deployed a CLI plugin that shows the NDK application's state in a human-friendly format

If you'd like to use this as a reference later, make sure to save your work somewhere safe.  You put in a lot of work to achieve this!

Hopefully this information will be helpful at some point during your own SR Linux journey, and maybe we will see you in a popular NDK app's commit history in the near future!  

Once you are done digesting this SReXperts (h)ac(k)tivity, go on, pick a new one!