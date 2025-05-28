
# Notifications

|                       |                                                                               |
| --------------------- | ----------------------------------------------------------------------------- |
| **Short Description** | Delivering notifications from your EDA system to popular notification systems |
| **Difficulty**        | Beginner                                                                      |
| **Tools used**        | EDA UI                                                                        |
| **Topology Nodes**    | :material-router: leaf1                                                       |
| **References**        | [Notifier App documentation][notifier-docs]                                   |

[notifier-docs]: https://docs.eda.dev/apps/notifier/

Modern day data center management is far from only dealing with configuration provisioning.
More so, the day2+ operations are what teams are dealing with most of the time. Things like monitoring, alarm management and notifications come to mind.

EDA is not only the powerful configuration management platform, but is also no stranger to operations. It packs a powerful set of applications and integrations to simplify operations and extend the core set of capabilities.

This exercise introduces you to the EDA [**Notifier**](https://docs.eda.dev/apps/notifier/) application that allows an operator to create custom notifications based on the events registered by EDA and deliver them to popular notification and chat systems.

## Objective

Our objective is to configure EDA in such a way that it can emit a notification when a certain event occurs. To be precise, let's have a goal of sending a notification when any physical interface on any switch in our fabric changes its operational status from UP to DOWN. We will work towards sending a message to the Discord group monitored by the operations team.

In exercise we will learn the following:

1. How to extend EDA core capabilities by installing applications from EDA Store
2. What events EDA can filter on and pass over to the Notifier application
3. How to configure different notification systems

## Technology explanation

Before jumping into the exercise, let's clarify what we consider an event in EDA.

As the name suggests, EDA - Event Driven Automation - is all about events, but what does it really mean? In a nutshell it means that all internal EDA processes are triggered by different kinds of events happening in and outside of the EDA system.  
EDA is a system of event producers and consumers, where everything is based on event streaming and asynchronous communication.

For example, if a transceiver dies and triggers the port to go down, this event will be immediately available in EDA thanks to streaming telemetry. Once the event of a port changing its state from UP to DOWN is available in the EDA system, all the applications that registered themselves as a consumer for such events will start and work on the basis of this event.  
For example:

- an Interface application that is in charge of the interfaces will raise an appropriate alarm
- the ISL (inter-switch link) application that defines the ISL links will recalculate the health of a corresponding link and will mark it as degraded
- the Components application that tracks the state of node components will raise an alarm that Transceiver went down
- and so on and so forth. A single event triggers dozens of applications.

This reactivity to the events in the core of the EDA engine is what makes it a pure event-driven system.

With a strong focus on openness, EDA doesn't keep events only to itself, but allows non-core applications to subscribe to the vast majority of these events and react to them.

One such application - [Notifier][notifier-docs] - was written by Nokia to unlock notification capabilities for all EDA users. After installing the app, you can configure your notification sources and destinations. You have the option to choose between two sources — Alarm or Query — and can send notifications to multiple destinations.

When the Notifier app is installed, it extends the EDA API with the new Resources (aka Intents)[^1]:

1. **Notifier**  
    Allows an operator to configure which events/sources to use to create notification messages. Can be either a list of alarms, or a list of EQL queries. Notifier resource can act on sources from the namespace it is created in.

    <small>The `ClusterNotifier` resource is a cluster-scoped version of the Notifier resource that can act on sources from all namespaces.</small>

    /// details | Notifier resource fields
        type: subtle-note
    Notifier resource has the following fields:
    <!-- --8<-- [start:notifier-resource] -->
    ```yaml
    apiVersion: notifiers.eda.nokia.com/v1
    kind: Notifier
    metadata:
      name: ''
      namespace: ''
    spec:
      description: ''
      enabled: true
      providers: []
      sources:
        alarms:
          include: []
          exclude: []
        query:
          table: ''
          where: ''
          fields: []
          title: ''
          template: ''
          color: ''
    ```
    <!-- --8<-- [end:notifier-resource] -->
    ///

2. **Provider**  
    Allows an operator to configure notification systems (destinations) that notification messages produced by the Notifier resource can be sent to. The `Provider` resource is namespace scoped and can be referenced by the `Notifier` resource in the same namespace.

    <small>`ClusterProvider` resource can be referenced by the `ClusterNotifier` resource.</small>

    /// details | Provider resource fields
        type: subtle-note
    Provider resource has the following fields:

    ```yaml
    apiVersion: notifiers.eda.nokia.com/v1
    kind: Provider
    metadata:
      name: ''
      namespace: ''
    spec:
      description: ''
      enabled: true
      uri: ''

    ```

    ///

By configuring these two resources a user can define what events to take in as a source for notifications and where to deliver them.

Both `Notifier` and `Provider` resources are configured in a user's namespace (in our lab setup the namespace is called `eda`) as we will consume notifications in the same namespace. For cluster-wide setup one could have used `ClusterNotifier` and `ClusterProvider` resources.

## Tasks

As per this exercises' [objective](#objective) you are tasked with providing your operations team who uses Discord with a notification stream for link up/down events.

### Install Notifier App

EDA is an extensible framework where a user is free to choose what application they need to install. To foster extensibility and community involvement, EDA allows everyone to write applications that can be installed on the platform. Of course, many initial applications will come from Nokia.  
Notifier is an example of an app that doesn't come preinstalled and is available in the Nokia App Catalog that is configured in your EDA system.

Login to the EDA UI using the assigned Group ID and EDA credentials provided to you.

Install the Notifier application by switching to the **System Administration** view and choosing the **Notifier** application from the list of applications.

![install](https://gitlab.com/rdodin/pics/-/wikis/uploads/d532dafe546597164876d1538d6ace49/CleanShot_2025-04-07_at_21.34.54_2x.png)

Once the application is installed, switch back to the **Main** view where you will see the **Notifier** menu group in the left sidebar with the **Notifier** and **Provider** resources in it.

### Send Interface Alarms to Discord

You are tasked with configuring the Notifier app to send Interface Up/Down alarms to a Discord server that we created for you. To accomplish this task you will need to perform the following steps:

1. Configure the Discord Provider resource that will receive the notifications about interface state changes.
2. Identify the alarm type raised by the system when an interface changes its state.
3. Create an instance of the Notifier resource that matches the identified alarm type and directs the notifications to the Discord Provider.

#### Configuring the Discord Provider

Start with configuring the Discord Provider. In the context of the Notifier app, a Provider resource configures the destination where alarms can be sent.  
You can configure many [different providers](https://docs.eda.dev/apps/notifier/#providers) in the Notifier app, but for this task we will use Discord, as it is easy to set up in a short amount of time we have.

##### Logging in to Discord

Naturally, you will need to log in to Discord to see the notifications popping up when you are done with the configuration task. To login to Discord server where we created a channel for this exercise you can either install the Discord app or use the web interface.

To join the EDA Discord server follow this link - **https://eda.dev/discord**

After choosing the username, you should see a list of channels, where one of them is named `srx-hackathon-notifier`. There we will send our notifications.

##### Create Provider resource

As part of this exercise, no matter what group you're assigned to, you get a Discord webhook link from us that is associated with the channel `srx-hackathon-notifier`.

```
https://discord.com/api/webhooks/1356633431169302688/1eigFh5nBoSRYkIU93OmkVll8xo8uEoCYvOQrEiRwjCTPvDt0E5Ntpg4D5MlU3k9q3dV
```

In the EDA UI sidebar find the **Notifier** group and choose the **Provider** menu item. Next open the Provider resource form by clicking on the Create button:

![prov1](https://gitlab.com/rdodin/pics/-/wikis/uploads/023546bc2ac219f9719cb30b8d81de12/CleanShot_2025-04-01_at_15.15.50_2x.png)

Edit the resource by giving your provider a name, for example `discord`, and paste the Discord URL in the `uri` field.

/// warning
When pasting the discord webhook link you should replace the `https://` schema with `discord://` to indicate to the Notifier that it is a Discord webhook.
///

Commit the transaction.

/// details | Solution
    type: example
The Provider resource should look like this:

```yaml
apiVersion: notifiers.eda.nokia.com/v1
kind: Provider
metadata:
  name: discord
  namespace: eda
spec:
  enabled: true
  uri: >-
    discord://discord.com/api/webhooks/1356633431169302688/1eigFh5nBoSRYkIU93OmkVll8xo8uEoCYvOQrEiRwjCTPvDt0E5Ntpg4D5MlU3k9q3dV
```

///

#### Identifying Alarm Types

Let's have another look at the specification of the Provider resource that we should use to tell EDA what notifications to send to the configured Provider:

--8<-- "docs/eda/beginner/notifications.md:notifier-resource"

As we are tasked with notifying our ops team with Interface alarms, you might have guessed that we will focus on the following bit of the Notifier specification:

```yaml hl_lines="4-8" title="portion of the Notifier spec"
spec:
  enabled: true
  providers: []
  sources:
    alarms:
      namespaces: []
      include: []
      exclude: []
```

As the field's name suggest, we might want to include some alarms in the `include` list, but what exactly we need to type there?

To answer this question, have a look at the Alarms page in the EDA UI:

![pic2](https://gitlab.com/rdodin/pics/-/wikis/uploads/db3b7fdf33e594f295b2cdac586d6e32/CleanShot_2025-04-01_at_15.22.51_2x.png)

What you see in the Type column is the Alarm Type, and the Notifier app expects you to provide this value in the `.spec.alarms.include` field. Great, one piece of a puzzle solved. But there may be many alarm types in your list, and none of them may be relevant to the interface state we are after.

We need to find the relevant Alarm Type that is raised when an interface goes Up->Down or Down->Up. In future, EDA docs will have a list of alarms published, but until then, let's shut one interface down and monitor the list of alarms.

##### Generating Interface Down Event

To generate the relevant alarm we need to connect to the **server** hosting the network topology using the credentials provided.

Once logged in, paste this script that shuts down the `ethernet-1/1` on `leaf11` node:

/// tab | Run command
Run in the bash shell of the server:

```shell title="bring down leaf1:ethernet-1/1"
docker exec clab-srexperts-leaf11 \
sr_cli -ec "/interface ethernet-1/1 admin-state disable"
```

///
/// tab | Expected output
After running the command, you should see

```
All changes have been committed. Leaving candidate mode.
```

///

Now have a look at the alarm list again and filter on the Last Changed column to have most recent events appear on top. You will

![pic3](https://gitlab.com/rdodin/pics/-/wikis/uploads/93c13dc4a9be61ad71be0c918ebbd612/CleanShot_2025-04-01_at_15.54.51_2x.png)

Write down the Alarm Type that was raised when we shut down the interface.

/// details | Hint
    type: example
Alarm Type: `InterfaceDown`
///

/// admonition | Restore Interface State
    type: warning
Bring back the interface state by running the following command in the bash shell of the server:

```shell
docker exec clab-srexperts-leaf11 \
sr_cli -ec "/interface ethernet-1/1 admin-state enable"
```

///

#### Configuring Notifier

Knowing the Alarm Type, you can proceed with creating the Notifier resource:

![not-1](https://gitlab.com/rdodin/pics/-/wikis/uploads/2a59c40580dd7945dc8514161295399d/CleanShot_2025-04-01_at_15.15.50_2x.png)

Add the Alarm Type to the `.spec.sources.include` list and bind the Notifier resource to the Provider we created earlier.

/// details | Solution
    type: example

```yaml
apiVersion: notifiers.eda.nokia.com/v1
kind: Notifier
metadata:
  name: interface-alarm
  namespace: eda
spec:
  enabled: true
  providers:
    - discord
  sources:
    alarms:
      include:
        - InterfaceDown
```

///

#### Testing notifications

With both Notifier and Provider resources configured you should be able to test the Notifier app in action.

We will use the familiar interface down command that we used to find the Alarm type. You should execute this command in the bash shell of the server that runs your topology:

/// tab | Disable interface

```shell title="bring down leaf1:ethernet-1/1"
docker exec clab-srexperts-leaf11 \
sr_cli -ec "/interface ethernet-1/1 admin-state disable"
```

///
/// tab | Enable interface

```shell title="bring up leaf1:ethernet-1/1"
docker exec clab-srexperts-leaf11 \
sr_cli -ec "/interface ethernet-1/1 admin-state enable"
```

///

Triggering the interface admin state should raise the Alarm in the EDA UI as well as send a notification to the configured Provider. Watch the Discord channel for new messages to appear when the alarm is raised and cleared.

### Try other providers

For an extra challenge, try configuring another provider (slack, email, teams) and add it to the same Notifier resource as an additional provider. This should deliver the alarm notification to all configured providers at once.

[^1]: If this a new term for you, check out the [Declarative Intents](declarative-intents.md) exercise first.
