# Declarative Abstracted Intents

|                       |                                                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Short Description** | Declarative Abstracted Intents is the main EDA concept and it is used to define the behavior of a resource. |
| **Difficulty**        | Beginner                                                                                                    |
| **Topology Nodes**    | leaf11, leaf12, leaf13, spine11, spine12                                                                    |
| **Tools used**        | EDA UI                                                                                                      |

The EDA framework was built around the core concepts of the **declarative abstracted intents**, **event sourcing**, **loose coupling** and **transactions** which set EDA aside from other traditional network automation systems.

While many existing network automation frameworks still leverage the imperative configuration paradigm and state polling, we believe that the future of a reliable network automation lies in the event-based, declarative space.

## Objective

The goal of this exercise is to introduce you to the main EDA concepts such as declarative resource model, label-based coupling and transactions. By completing the set of tasks you will get a good understanding of the base EDA principles and explore the novel features of configuration management with declarative abstracted intents.

No matter if you're coming from a traditional network engineering background, or you're a seasoned network automation engineer, we believe you will find something new in the way EDA-based network automation is done.

## Technology explanation

This exercise is titled Declarative Abstracted Intents as it is one of the main EDA concepts that enables the next-gen network automation. Let's dissect this term and explore what it means:

* The somewhat overloaded **intent** term refers to a user's input to the EDA automation system. Typically it is provided in the form of a configuration snippet done in one of the serializable data formats such as YAML, JSON, XML, etc.
* The **declarative** part of the intent refers to a declarative configuration paradigm that prescribes that the input to the system should say what should be done, not how to do it.

    For example, compare the declarative and imperative forms of the same intent of configuring two interfaces on a network device:
    /// tab | declarative

    ```yaml
    interfaces:
      ethernet-1-1:
        description: "First interface"
      ethernet-1-2:
        description: "Second interface"
    ```

    ///
    /// tab | imperative

    ```srl
    enter candidate
    set / interface ethernet-1/1 description "First interface"
    set / interface ethernet-1/2 description "Second interface"
    commit now
    ```

    ///

    The declarative form says what needs to be configured and leaving the "how" to the system, while the imperative form also needs to specify how to do it.

* The **abstracted** part of the intent serves two main purposes:
    * simplify the intent by abstracting away the details of the network device or technology.
    * make the intent vendor-agnostic, so that the same input can be used with many vendor devices.

### EDA Resources

In EDA, the declarative abstracted intents are implemented as **Resources**. Here is an example of the EDA Interface Resource that captures the declarative abstracted intent of configuring a physical interface on a network device:

```yaml
apiVersion: interfaces.eda.nokia.com/v1alpha1
kind: Interface
metadata:
  name: leaf13-ethernet-1-49
  namespace: eda
spec:
  description: inter-switch link to spine11
  enabled: true
```

Observant readers will immediately notice that this EDA Resource is modeled after the [Kubernetes Resource Model](https://github.com/kubernetes/design-proposals-archive/blob/main/architecture/resource-management.md), which is a declarative model that describes the interfaces in Kubernetes.

You see how this resource has the **declarative** and **abstracted** parts of the intent?

### Loose Coupling

Another important concept in EDA is **loose coupling** that is enabled by the use of **Labels**.

The concept of a loose coupling says that the resources may be loosely coupled between each other. Instead of explicitly saying that the Resource-A depends on Resource-B and Resource-C, we can label the Resource-B and Resource-C with a label `BC` and in the Resource-A we can use the `BC` label to find the resources to act upon.

The power of the loose coupling is that it allows for dynamic dependencies between the resources. If we suddenly add another resource labeled with `BC` label, the Resource-A will automatically pick up the new resource and act on it. Through the hackathon exercise you will see how this concept is used to a great effect.

### Transactions

The holy grail of worry-free operations is atomic transactions. The worst thing that can happen during the automated configuration provisioning is a partially applied configuration due to not all nodes accepting the configuration.

EDA solves this problem by adding a concept of **Transactions**. The user-submitted declarative intents are all transacted together and either all of them are applied by the nodes or all of them will be rolled back.

The transaction-based model also allows for Dry Runs - seeing what changes will be rolled out to your network before actually applying them.

## EDA UI

Every hackathon group has access to an EDA instance and its interfaces. In this exercise you will be using EDA Web UI that you can reach over public Internet by navigating your browser to https://{group-ID}.srexperts.net:9443

> Use the provided leaflet to get the authentication details and Internet access instructions.

After a successful login you will see the main EDA UI page:

![ui](https://gitlab.com/rdodin/pics/-/wikis/uploads/e4e0ab87c7063977adfd3de4f91320ae/CleanShot_2025-04-08_at_14.48.42_2x.png)

Clicking on the **Menu** icon toggles the side menu:

![side menu](https://gitlab.com/rdodin/pics/-/wikis/uploads/8dda8fba62c5334fda162f21ed6505cb/CleanShot_2025-04-08_at_14.53.37_2x.png)

While you don't have a visual memory of the resource groups icons, using the side menu in the expanded view will help you navigate the UI. Also you will find the search bar at the top quite handy.

## Tasks

Tired of theory? Time to back it up with practical challenges and learn the details by doing.

### Adding an Interface

As a warmup, you are tasked with enabling additional interfaces on the leaf switches. According to the [lab diagram](../index.md#access-details), EDA manages `leaf11`, `leaf12`, `leaf13` nodes.

These nodes already have a number of interfaces configured, let's find out what they are. Since EDA acts as a source of truth for **all** configuration on the managed nodes, we should see the list of already configured interfaces in the UI.

In the left sidebar scroll down to the **Topology** resource group and select **Interfaces** resource. A table view with the list of interfaces configured in the system will appear, where we can filter the interfaces which name starts with `l` character that will narrow down the list to the interfaces.

> Remember, that our leaf switches are named `leaf11`, `leaf12`, `leaf13`. So all of them have `leaf1` as a prefix as well as the lag interface configured between the three switches called `lag1`.

![ifaces](https://gitlab.com/rdodin/pics/-/wikis/uploads/89b53ee6db6d409fd12a19d317b843c7/CleanShot_2025-04-08_at_15.34.56_2x.png)

We have selected the Interface resources on leaf switches that point to the client devices, and you can match these resources to the topology information:

-{{ diagram(url='srexperts/hackathon-diagrams/main/eda.drawio', title='EDA Managed nodes', page=0, zoom=1.5) }}-

Based on this information we can see that our leaf switches have interfaces `1`, `2`, `3`, `49` and `50` already configured either in the direction to the client or spine devices. So let's configure some non-connected interface on the leaf switches - for example, interface `ethernet-1/5`.

#### Query Interfaces with EQL

Before you proceed with creating the `ethernet-1/5` interface, let's query the interfaces on the leaf switches to make sure that there are no interfaces with the same name already configured.

Typically you would connect to the leaf switches and run `show` commands, or use a custom script that does the same in a more automated way. But there is a better way to interrogate the network devices...

EDA comes with a built-in network-wide query engine that allows you to query the network devices in a performant and scalable way. Using the sidebar navigation, go to the **Queries** resource and paste the following in the EQL[^1] Query input field:

/// warning
In the query below, replace `g1` in the node name list with the group ID you have been assigned to.

For example, if your group ID is 32, then the list should look like:

```
[ "g32-leaf11","g32-leaf12","g32-leaf13" ]
```

///

```
.namespace.node.srl.interface fields [admin-state] where (.namespace.node.name in [ "g1-leaf11","g1-leaf12","g1-leaf13" ] and .namespace.node.srl.interface.name = "ethernet-1/5")
```

![eql](https://gitlab.com/rdodin/pics/-/wikis/uploads/d6739ceef3d3e91b5f69a35d1b2d68af/CleanShot_2025-04-08_at_15.56.48_2x.png)

> While this exercise is not about EQL specifically, it is a good opportunity to leverage the power of the query engine to understand the state of the network.

You can see that all three leaves have interfaces `ethernet-1/5` in `admin-state=disable`. So you are clear to configure those interfaces!

#### Interface Resource Form

Go to the **Topology** -> **Interfaces** menu item where before we looked at the configured interfaces and click the **Create** button to open the resource creation form. You can also use the search bar and filter for Interface:

![search](https://gitlab.com/rdodin/pics/-/wikis/uploads/6720dd1597f7a87905fbc824f0839bcb/CleanShot_2025-04-08_at_16.06.57_2x.png)

The creation form has the following important panels:

![form](https://gitlab.com/rdodin/pics/-/wikis/uploads/ebe9ef4af3c0a0a3b2e10a6fe58d8418/CleanShot_2025-04-08_at_16.08.45_2x.png)

The form has three distinct sections, as per the screenshot above, and as a user you will be using the form or YAML view to configure the resource and use the navigation to quickly navigate to the relevant fields.

> You can use the form and YAML views interchangeably, as every change made in one view will be reflected in the other.

#### Choosing the Fields

The form has quite some number of fields, but not all of them are relevant to our task or required to be filled in. You must provide the following fields:

* Metadata -> Name: the name of the interface
* Specification -> Members: a list of the port name + node name combinations that identify what ports to configure on which nodes

#### Interface Members

If you chose to configure the interface via the form view, you have to click **+ Add** button to invoke another modal window where interface members are configured.

You will have to provide the Interface name in the sanitized format, where spaces and `/` are replaced with `-`. For instance, `ethernet-1/5` should become `ethernet-1-5`.

And after the interface name is sorted, you should provide the node name using the drop down menu.

![members](https://gitlab.com/rdodin/pics/-/wikis/uploads/8030869abec5a3c6464a166e8e268a96/CleanShot_2025-04-08_at_16.24.55_2x.png)

/// warning | When to use multiple members?
You might have an urge to configure ethernet-1/5 port on multiple nodes by adding them as members, but this would be a mistake.

The members interface list is used for LAG interfaces, the distinct interfaces should be configured with separate Interface resources.

This means, that if you are configuring `interface-1/5` on `leaf11`, then your Interface resource may be named as `leaf11-ethernet-1-5`.
///

When you fill in the required fields (name and members), you will see that the two buttons in the bottom right corner of the form will become active, allowing you to directly commit the changes or to add them to a transaction.

Feel free to choose your path, but adding all the Interface resources you want to create to a single transaction is a good idea, since we want all the resources to be created in a single transaction.

Continue adding other interfaces to the transaction bucket, you should have three interface resources in total.

#### Dry Run

Once you added three interfaces to the transaction bucket you can **Dry Run** the transaction and see what your intended changes would look like.

![dryrun](https://gitlab.com/rdodin/pics/-/wikis/uploads/f718637c278dfb0fc3d7134b705ec7a1/CleanShot_2025-04-08_at_16.45.06_2x.png)

Executing the Dry Run will either succeed or fail, with an icon indicating the result. The interesting part is checking the diffs

![diff](https://gitlab.com/rdodin/pics/-/wikis/uploads/77a8d33567f9c14112247b6d47ac456b/CleanShot_2025-04-08_at_16.48.38_2x.png){width="50%"}

Looking at the diffs view should give you a precise idea of what changes will be made to the configuration:

![diff-node](https://gitlab.com/rdodin/pics/-/wikis/uploads/068d8a2c575f5ccbf3d1b057b034096b/CleanShot_2025-04-08_at_16.52.06_2x.png)

The top three menu items in the left side bar will display configuration diff in the native config of the Network OS the changes will be applied to. In our case, it is SR Linux config that we are looking at and we see how all three nodes get additions of the `ethernet-1/5` interface!

#### Commit Transaction

Remember, that we are browsing the diff of the Dry Run operations, none of the proposed changes have been applied to the nodes yet, they all have been deduced based on the known state kept in the EDA database.

Since the change is looking good you can proceed with committing the configuration and applying the changes to the nodes by closing the Diff view and clicking on the **Commit** button.

In a moment you will see a confirmation that the transaction was committed successfully. Now you can repeat the EQL query and check the admin state of the `ethernet-1/5` interface on all three nodes. They all should be `enabled` now.

### Configuring NTP

If you are a seasoned network automation engineer with YAML tattoos on your forearms, you might appreciate a more challenging task. Go on and configure the NTP client on all the nodes of your fabric!

You will have to use a local NTP server running on `10.128.<YOUR GROUP ID>.1` and choose the management router as the VRF context in your intent.

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>

[^1]: EQL stands for EDA Query Language that is resembles other query languages like PromQL, Jira QL and so on.
