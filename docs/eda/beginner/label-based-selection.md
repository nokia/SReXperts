# Label-based Selection

|                       |                                                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Short Description** | Loose coupling of resources delivers flexible relationships between resources.<br/>At the helm of this concept sits labeling mechanism that is widely used in microservices and container orchestration. |
| **Difficulty**        | Beginner                                                                                                    |
| **Topology Nodes**    | leaf11, leaf12, leaf13, spine11, spine12                                                                    |
| **Tools used**        | EDA UI                                                                                                      |

On a broader scale the relationship between the resources can either be **tightly coupled** or **loosely coupled**.

The tight coupling binds the resources explicitly to each other, typically using a unique identifier. An example of a tight coupling all of you might have used in the past is an inventory system that lists the IP addresses of the devices that you target with your automation scripts.  
The tight coupling allows for a more deterministic selection of the target nodes your automation acts against, but it is less flexible and requires more effort to maintain.

The loose coupling binds the resources implicitly to each other, typically using a concept of a label or tag. An example of a loose coupling would select a label as a target for your automation, and the objects that were having this tag would be the ones that your automation would act against.  
The loose coupling allows for flexible and dynamic target selection, making it easier to adapt to changes in the network topology and provide more cloud-native resource management.

## Objective

The goal of this exercise is to introduce you to the concept of loose coupling of resources and how it is achieved in EDA via the concept of labels. You will see how labels are first class citizen in EDA with every resource having an option of being tagged with one or more labels.

## Technology Explanation

The concept of label-based loose coupling is not new. You may have used it when managing resources in the cloud provider of your choice or with the security platforms where resource tags are used to group resources together.  
Overall, the concept of tags/labels is well known especially in the cloud-native domain where resources are managed at scale.

From the technical perspective, labels are typically implemented as key/value pairs that are attached to a resource and become part of the resource's metadata. A resource with a label is often called labeled or tagged resource.

A resource may have none, one or more labels attached to it. The automation system then can select resources using the label selectors and not by pointing to a unique resource identifier (IP or name). Due to the fact that labels are key/value pairs, they have to be uniquely keyed, for example having a set of labels like:

- `nic-type=storage`
- `nic-type=100G`

is not valid, since the two labels have the same key `nic-type`. You should choose different keys for the labels.

In the diagram below you see how EDA leverages labels to select resources for its intents. The EDA-managed nodes - leafs and spine elements, are labeled with a label that encodes the role of the device (e.g. `eda.nokia.com/role=spine` for the spine devices)

-{{ diagram(url='srexperts/hackathon-diagrams/main/eda.drawio', title='Label-based coupling', page=1, zoom=1.5) }}-

With the resource being uniformly labeled, EDA can select resources for its intents using the label selectors, instead of specifying the target nodes by their IP addresses or names.

### Labeled resources in EDA

You will see labeled resources a lot in EDA, but probably the first time you get to see and interact with labels is when you look at the list of nodes managed by EDA.

/// note
Labels are assigned by an operator or a system that creates the resource.
///

Have one more look at the diagram above that depicts a leaf-spine topology managed by EDA and let's find this list of nodes in the EDA UI.

When logged into the EDA UI you can find the list of nodes managed by EDA using the left side bar navigation and selecting **Targets** → **Nodes** menu.

![nodes](https://gitlab.com/rdodin/pics/-/wikis/uploads/1ff53dfbf11061f7ecf42f00d901a96b/CleanShot_2025-04-09_at_20.49.31_2x.png)

You should see the familiar node names (we call these resources **TopoNodes**) as depicted in the diagram above and the associated metadata, specification and status. In the same table view you can find the **Labels** column that shows the labels attached to each node; they are collapsed under the `+5` icon, which means there are 5 labels attached to each node and there is no space to display them all in line.

If you hover over this icon you should see the list of labels, but you can also select the **Configuration View** menu element at the end of each row to see the expanded view of the TopoNode resource:

![conf view](https://gitlab.com/rdodin/pics/-/wikis/uploads/a0e58751d2a06913a79967add24a9b49/CleanShot_2025-04-09_at_20.56.20_2x.png)

In the configuration view labels are shown expanded, and we can see all five of them listed there, each carrying our some meaning:

![labels](https://gitlab.com/rdodin/pics/-/wikis/uploads/07e690121aa6e93b13edb459ce52bd7a/CleanShot_2025-04-09_at_20.57.30_2x.png)

As I selected the `leaf13` node, the important label it has attached to it is:

- `eda.nokia.com/role = leaf` - this label carries out the role of the node in the topology

> This label has a key - `eda.nokia.com/role` and a value - `leaf`.

When onboarding the nodes of the topology to EDA we manually assigned labels to each nodes to identify their role and make it possible for EDA to select the nodes for the intents based on these labels.

## Tasks

You will find EDA both strict and loose coupling used in EDA. Often the same intent will offer you the choice of using either approach. In the following tasks you will be using label-based selection to select the resources for your intents as well as using strict coupling based on element names.

### Configure Login Banner on a single element

Your first task is to configure a Login Banner on a single - `spine11` - element. You will find the **Banners** resource in the sidebar menu under the **Site Profiles** group.

> Don't know what a resource is? Check out the [Declarative Intents](../beginner/declarative-intents.md) exercise.

Click the Create button to open the resource editor. In the specification section of the Banner resource you will find both strict and loose coupling options for you to choose:

![banner-spec](https://gitlab.com/rdodin/pics/-/wikis/uploads/9d44a70436eec380449f80a2fd7a176e/CleanShot_2025-04-09_at_16.17.53_2x.png)

Since you are tasked with configuring a Login Banner on a single spine element, choose the the option that will allow you to specify the target element by its name.

After selecting the `spine11` element, commit your changes.

#### Verification

Once the changes have been committed, you can verify the changes using the network-wide queries.  
EDA comes with a built-in network-wide query engine that allows you to query the network devices in a performant and scalable way. Using the sidebar navigation, go to the **Queries** resource and paste the following in the EQL[^1] Query input field:

```shell
.namespace.node.srl.system.banner fields [ login-banner ] #(1)!
```

1. This query will return the value of the `/system/banner/login-banner` field from all SR Linux nodes managed by EDA.

You should see only `spine11` feature the `login-banner` message, as other nodes shouldn't have been targeted by the Banner resource you have created.

![verif](https://gitlab.com/rdodin/pics/-/wikis/uploads/88785fcadb995d9642da2e13c544b6b7/CleanShot_2025-04-09_at_16.37.06_2x.png)

### Configure Login Banner on multiple elements

Now that you have configured a Login Banner on a single spine element using the strict coupling with a node name, your next task is to configure a Login Banner on all leaf nodes.

You will use the loose coupling enabled by the labels to achieve that. Recall the labeling scheme we covered in the [technology explanation section](#technology-explanation) where all leaf nodes have the `eda.nokia.com/role=leaf` label.

Go on and **edit** the Banner resource you created in the first task and add the **Node Selector** field with the label all leaf nodes have in common. After you added the Node Selector, add the change to the transaction and run the Dry Run to ensure that all three leaf nodes will be targeted with the same banner.

> Don't know how to use the Dry Run feature? Check out the [Declarative Intents](declarative-intents.md#dry-run) exercise first.

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>

[^1]: EQL stands for EDA Query Language that is resembles other query languages like PromQL, Jira QL and so on.
