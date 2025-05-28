# EDA

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>

Event Driven Automation (EDA) is the state of the art automation platform that completes Nokia's Data Center portfolio:

![portfolio](https://gitlab.com/rdodin/pics/-/wikis/uploads/8a5373e38de7ea4be5af8128ffab9d3c/CleanShot_2025-04-18_at_23.53.33_2x.png)

The design goals behind EDA were lofty and our ambitions were to create an infrastructure automation platform that addresses many challenges seen in the data center networking.

In the **configuration management** domain EDA breaks the status quo of imperative, box-by-box configuration and leverages declarative and abstracted configuration model. In this mode a user declares what services or components they want to get deployed by providing its desired state in the form of an input that abstracts the complexities and implementation details.

What is more important than the configuration intent - is the state the system is in. EDA takes a unique stance on **state handling** by coupling the configuration intent with its actual state and presenting it to the users. Having the state of the system aligned with the configuration inputs is crucial to operations.

For **operations** domain EDA provides a unified, instant network-wide view of the running configuration and state via its EDA Query Language (EQL) capabilities. Having a way to create a query that runs over your whole network and provides instant and live results is table stakes for auditing, troubleshooting and state correlation.

While the concept of declarative intents or blueprints is not new, in EDA made sure our users can **extend and program** almost every aspect of the platform. Do not agree how we modeled a DC fabric inputs? You have all the instruments to change it or even create your own implementation of it.

And it would be a miss to keep EDA anchored to Nokia-only devices, that is why we ensured that EDA core is **multivendor** and users can leverage EDA superpowers with other vendors and their devices and APIs[^1].

At SReXperts Hackathon, you get a unique chance to spend a day with EDA by venturing into the exercises meticulously crafted by the EDA team and be the judge of its capabilities.

## How to get through the exercises?

As EDA is likely a new system for you, we recommend you to start from the beginner-level exercises in the order they are presented, unless you feel adventurous and want to hit the ground running.

When inside a particular exercise, you should complete the tasks in the order they are presented. It might be tempting to skip ahead but a task may have a dependency on the previous step, so do tackle them in order.

## Access details

<!-- --8<-- [start:access-details] -->

The lab environment you work on features a DC network topology with EDA already installed and a number of SR Linux datacenter switches already onboarded onto the platform. In particular, EDA manages five switches in total: `leaf11`, `leaf12`, `leaf13`, `spine11`, `spine12`.

-{{ diagram(url='srexperts/hackathon-diagrams/main/eda.drawio', title='EDA Managed nodes', page=0, zoom=1.5) }}-

As you go through the exercise, you might connect to the EDA UI, one of the switches or clients connected to them.

/// tab | UI
Most of the exercises can be completed by using EDA Web UI. The UI is accessible over `https://{your-group-id}.srexperts.net:9443`.

The login credentials are available in the leaflet provided to you.
///

/// tab | Lab server
The lab server runs the EDA platform and the whole lab topology. You will need to login to the topology server when you want to SSH further into one of the switches or clients.

```
ssh nokia@{your-group-id}.srexperts.net
```

You will find the server credentials in the leaflet provided to you.
///

/// tab | SR Linux switches
While you will mostly work with EDA UI, you would want to SSH into the switches to verify the configuration you made in EDA. To access the switches you first need to login to the lab server, and then from the server's shell you SSH further to the desired switch.

```bash title="run from the lab server"
ssh admin@{switch-hostname}
```

The switch hostnames are:

* `clab-srexperts-leaf11`
* `clab-srexperts-leaf12`
* `clab-srexperts-leaf13`
* `clab-srexperts-spine11`
* `clab-srexperts-spine12`

You will find the switch credentials in the leaflet provided to you.
///

/// tab | Clients

Clients are the Linux containers connected to the switches that you would need to configure to perform end-to-end ping tests between the hosts.

To access the clients you first need to login to the lab server, and then from the server's shell you SSH further to the desired client.

```bash title="run from the lab server"
ssh user@{client-hostname}
```

The switch hostnames are:

* `clab-srexperts-client11`
* `clab-srexperts-client12`
* `clab-srexperts-client13`

The client's credentials are `user:multit00l`

///

<!-- --8<-- [end:access-details] -->

## EDA UI

Most exercises can be completed using EDA's Web UI. As any modern platform, EDA's UI is an API client of the backend API server and uses the same endpoints as any automation system would use, which means that technically every exercise can be solved using any automation interface that consumes EDA API.

Still, for the most part we expect you to follow the lead and use the UI to complete the majority of the tasks. Chances are high that this will be your first time seeing and using the EDA UI, so let us give you a quick introduction.

### Main page

When you log in to the EDA UI you land on the **Main** page, here are the main areas of interest:

![ui-1](https://gitlab.com/rdodin/pics/-/wikis/uploads/a33d12f0cb46c95563021ceba7992d96/CleanShot_2025-05-02_at_18.54.01_2x.png)

:material-numeric-1-circle: The home page features a dashboard that provides some key information about the managed nodes and their interfaces.

:material-numeric-2-circle: The home page has two dashboards to select from. The page picker lets you do this. The picker will be available on other pages as well.

:material-numeric-3-circle: Namespace selector. When you have more than one namespace (`eda` is the default namespace) you will be able to switch between them.

:material-numeric-4-circle: Transaction basket. This is where your uncommitted transactions will be stored. Clicking on the basket icon also lets you do operations on the transactions.

:material-numeric-5-circle: User menu. This is where you can change your password, log out, and access the help and about pages.

:material-numeric-6-circle: Side menu toggle. Expands/collapses the left side menu where all EDA apps and menu items are.

:material-numeric-7-circle: Application icon. Clicking on the icon in the collapsed view opens up the application page.

:material-numeric-8-circle: Application category toggle. Can be used to hide/show the application category.

:material-numeric-9-circle: Application search. Type in the search term and the apps list will be filtered.

### App page

When you select an app from the list :material-numeric-1-circle: you get a page that lists all instances of this particular app/resource created. In the screenshot below we selected the Nodes from the menu and get a list of Node resources that EDA manages.

![list-view](https://gitlab.com/rdodin/pics/-/wikis/uploads/4576290b23221c9c2e0dd863d5e1f6e9/CleanShot_2025-05-02_at_20.54.06_2x.png)

The important elements on this view are:

:material-numeric-2-circle: Context menu button. Opens up a menu with commands like edit, duplicate, delete.

:material-numeric-3-circle: Click on this icon to display the status bar for the selected resource.

### Status bar

When the status bar is expanded, it shows the current information about the selected :material-numeric-1-circle: resource.

![status](https://gitlab.com/rdodin/pics/-/wikis/uploads/b3b43d820586634a1151946e78e22d9c/CleanShot_2025-05-02_at_20.58.55_2x.png)

Every bit of the information about the resource will be available in the sidebar, starting with Metadata :material-numeric-2-circle:, then Status :material-numeric-3-circle: and continuing with specification of the selected resource.

### Edit page

Naturally, you will spend quite some time creating and editing resources. When you click **Create** button from the App page listing the resources or double click on the row in the grid, or choose **Edit** from the context menu, you will be presented with an Edit page:

![form](https://gitlab.com/rdodin/pics/-/wikis/uploads/ebe9ef4af3c0a0a3b2e10a6fe58d8418/CleanShot_2025-04-08_at_16.08.45_2x.png)

This form has three main areas (from left to right):

1. Navigation bar, aka Form fields
2. Form view
3. YAML view

When editing or creating a resource, you would use either the Form view where every resource field is represented as a form field, or the YAML view where you can edit the resource in YAML format. You can start with a form view and continue in YAML editor, the changes are always synchronized.

At the left bottom of this page you will find two buttons that allow you to either commit the resource straight away, or add it to a transaction basket.

### Transaction basket

The transaction basket allows you to group resources together and commit them as a single transaction in an all-or-nothing fashion. Transactions are the key ingredient in EDA's mission to drive human error to zero.

By adding resources to the transaction basket you can commit them all together or perform a Dry Run to ensure that the changes pass all sorts of validations before touching the network elements.

The workflow below demonstrates how a VLAN resource gets added to the transaction basket, after which a dry run is performed to validate the transaction and then the diffs are browsed to understand the scope of the changes this transaction would result in should we have proceeded with the commit.

-{{video(url="https://gitlab.com/rdodin/pics/-/wikis/uploads/078f88bffcf0c8685d144fa4b8d9c71f/CleanShot_2025-05-03_at_00.12.47.mp4")}}-

## Namespace selector

When you first login to EDA as administrator, you have access to all available EDA namespaces. Since in this hackathon you will only work in the default `eda` namespace, you can select it using the namespace selector as shown below:

![ns-select](https://gitlab.com/rdodin/pics/-/wikis/uploads/10f8c7779ea629e14214fb88c1280edb/CleanShot_2025-05-14_at_23.27.05_2x.png)

By switching from All Namespaces to the `eda` namespace the UI will fill in the namespace name in the [Edit Page](#edit-page) when you will create new EDA resources.

## Reset EDA

As you go through the exercises, you will create and modify quite a few resources in EDA. It might happen that the resources from one unfinished challenge will interfere with the tasks you attempt next.

In such cases you can manually delete conflicting resources, but if you want to reset EDA to a state as it was at the beginning of the hackathon, you can easily do this by running the following command from the lab server:

```bash
bash /opt/srexperts/restore-eda.sh
```

This script will immediately revert all changes happened in EDA since you first logged in so you can start fresh.

[^1]: Pending vendors' support for YANG and modern management interfaces.
