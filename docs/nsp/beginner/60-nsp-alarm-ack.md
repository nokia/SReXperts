---
tags:
  - NSP
  - Workflow Manager
  - Fault Management
  - SchemaForm
---

# Acknowledge Alarms

|     |     |
| --- | --- |
| **Activity name** |Acknowledge Alarms |
| **Activity ID** | 60 |
| **Short Description** | Get, Filter, and Acknowledge alarms using Workflow Manager |
| **Difficulty** | Beginner |
| **Tools used** | Workflow Manager (WFM) |
| **Topology Nodes** | all SR OS and SRLinux nodes |
| **References** | [Nokia  Developer Portal](https://network.developer.nokia.com) (Sign up for a free account) |

## Objective

Network operators often face an overwhelming number of network alarms in their daily work. Manually finding, filtering, and acknowledging alarms can be time-consuming, labor-intense, and error-prone. In this activity, you will use WFM to enable operators to:

- Retrieve and filter alarms from the network (by severity, alarm-type, or device).
- Present those alarms in a structured input form.
- Acknowledge selected alarms automatically via a workflow.

The outcome is an operator-focused workflow that reduces manual effort and ensures alarms are handled consistently. The technologies used enable DevOps teams to build more advanced automation use-cases like rule-based, programmatic self-healing.

## Technology Explanation

### Workflow Manager
WFM enables operators to automate repetitive or error-prone tasks. Instead of performing manual actions separately, WFM lets you chain API calls into a single, reusable process. In this exercise, WFM is used to:

- Call RESTCONF APIs to fetch alarms.
- Apply filters so operators can focus on the alarms most relevant to them.
- Wrap actions into re-usable building blocks (ad-hoc actions).
- Acknowledge alarms directly from a form-driven workflow.

By leveraging WFM, organizations can increase efficiency, improve reliability, and accelerate service delivery and assurance by automating complex, multi-step network tasks. This bridges the gap between raw APIs and operator-friendly network automation.

### REST and RESTCONF

**REST** is a widely adopted standard for programmatically interacting with NSP using common HTTP methods such as GET, POST, PATCH, and DELETE.

**RESTCONF** extends this model by providing a consistent framework for exposing network management data and operations. It builds on REST principles while adding:

* A standardized way to perform **CRUDL** (Create, Read, Update, Delete, List).
* Support for executing **operations** beyond basic data access.
* A data model based on **YANG**, the industry-standard modeling language for network management.

Within NSP, RESTCONF gives operators a unified, programmable API surface for both data retrieval and operational control—making automation workflows more reliable, scalable, and future-proof. In this activity, RESTCONF APIs serve as the building blocks, while WFM orchestrates them into a repeatable operator workflow.

### Visual Studio Code

While workflows can be designed directly in the NSP WebUI, many operators and developers prefer a full-featured editor for more advanced editing, testing, and version control.

We recommend using [Visual Studio Code with the WFM extension](https://network.developer.nokia.com/tutorials/vscode-extensions/workflow-manager-visual-studio-code-extension), available from [Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=Nokia.nokia-wfm).

With Visual Studio Code, you gain:

* Syntax highlighting and validation for workflow YAML.
* Seamless integration with source control (e.g., Git).
* Faster iteration and testing through built-in connectivity to NSP.
* An enhanced developer experience for building, debugging, and sharing workflows.

### YAQL (Yet Another Query Language)

[YAQL](https://yaql.readthedocs.io/en/latest) is a flexible query language designed to extract and transform data from structured inputs. In the context of WFM, YAQL expressions are used to filter and reshape API responses so that workflows can consume only the relevant data.

The Yaqluator is an interactive tool integrated into the WFM WebUI. It enables developers to quickly prototype and test YAQL expressions against real API responses before embedding them into workflows. This helps ensure that data is properly filtered and formatted without repeated trial-and-error inside a running workflow.

### Ad-hoc Actions

Ad-hoc actions are user-defined wrappers written in YAML around existing system-actions coded in Python. They act like templates, allowing you to preset frequently used input attributes and reuse them across multiple workflows. This avoids repeating the same or similar definitions, while still relying on the underlying system-action for execution.

In practice, an ad-hoc action:

* References a base system-action (coded in Python).
* Defines a set of default inputs (base-input) that are automatically applied whenever the action is used.
* Optionally declares parameters (input) that workflows must supply at runtime.
* Optionally defines how the output should be shaped.

This makes them especially useful for recurring patterns, such as standard notification emails, device configuration operations, or pre-validated API calls.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Get Alarms

Open NSP WebUI and open `Workflows` found under the `PROGRAMMING` category.

Select `Actions` view.

On the left side, we have two types of actions: `Ad-hoc Actions` and `System Actions`.

Let’s start by getting a list of all major alarms on the network:

* Navigate to the `Systems Actions` and search for the `nsp.https` action.
* Click on the 3 dots on the right side and choose `Run`.
* Explore the RESTCONF Alarms API in [Developer Portal](https://network.developer.nokia.com/api-documentation) including the corresponding [Postman collection](https://documenter.getpostman.com/view/26248101/2sAY4uCNvf#de0ea146-e51a-455a-84c5-19f438712103) to find API endpoints to query and acknowledge alarms.
* Retrieve a list of all major alarms in NSP using RESTCONF by running the `nsp.https` action from WFM WebUI.

If you got stuck, find the `nsp.https` action input below to retrieve the list of all major alarms.

/// details | Possible Solution
    type: success
```yaml
url: https://restconf-gateway/restconf/operations/nsp-inventory:find
method: POST
body:
  input:
    xpath-filter: /nsp-fault:alarms/alarm-list/alarm[perceived-severity = 'major']
    include-meta: false
```
///

Adjust the filter, for example by picking different severity levels like `critical`, `minor`, or `warning`.
Review the JSON response returned. Try to filter by other alarm attributes, such as alarm-type.

/// details | Possible Solution
    type: success
Update the `xpath-filter` to match your selection criteria. If you are filtering by `alarm-type-id` or `alarm-type-qualifier`, use the output from your initial query to ensure that the values correspond to existing entries.

```yaml
url: https://restconf-gateway/restconf/operations/nsp-inventory:find
method: POST
body:
  input:
    xpath-filter: >-
      /nsp-fault:alarms/alarm-list/alarm[alarm-type-qualifier = 'PeerConnectionDown']
    include-meta: false
```
///

### Process Alarm API Response

Copy the received response and navigate to the `Yaqluator` in the upper right corner of the Actions page. The Yaqluator functionality allows you to quickly prototype YAQL expressions based on the received response. Paste the response on the bottom left side YAML/JSON Context section.

In the upper YAQL Expression section use the following filter expression to get the list of alarm-names:

```yaml
$.result.content.get('nsp-inventory:output').data.select($.get('alarm-type-qualifier'))
```

Try to filter for other attributes like `alarm-fdn`, `alarm-type-id`, and `ne-id`.

### Create the Workflow

Navigate to the [Developer Portal](https://network.developer.nokia.com/api-documentation/) and search for the RESTCONF call that acknowledges an alarm based on a specific Full Distinguished Name (FDN), which uniquely identifies an alarm.

/// details | Example output
    type: success
The NSP Postman collection "Fault Management RESTCONF API" recommends using a PATCH request on `https://{{server}}:8545/restconf/data/nsp-fault:alarms/acknowledgement={{alarmFdn}}` to acknowledge an alarm.
In your workflow, instead of using the external NSP IP (and port 443 or 8545), you can directly access the RESTCONF gateway. With this, the URL becomes `https://restconf-gateway/restconf/data/nsp-fault:alarms/acknowledgement={{alarmFdn}}`.

///

Create a workflow that uses this API to acknowledge an alarm.

/// warning
Don't forget to use a unique name for your workflows, e.g. by adding your group number!
///

Workflow Manager uses OpenStack Mistral as engine for workflow execution. To write a new workflow, the following resource might be helpful to you:

* NSP Developer Portal: https://network.developer.nokia.com/learn/25_4/programming/workflows/wfm-workflow-development/
* OpenStack Mistral: https://docs.openstack.org/mistral/ocata/dsl/dsl_v2.html#workflows

Here a simple workflow boilerplate, you can start with:

```yaml
---
version: '2.0'

workflowname:
  type: direct
  
  description: brief description for the workflow

  input:
    - varname1: "default-value"
    - varname2: 100
    - varname3: true
    - varname4: []
    
  output:
    result: "success"

  tasks:
    task1:
      action: std.noop
...
```

Adjust workflow name, description, inputs and tasks as needed. You may start by just providing a single `alarmFdn` as input. The workflow itself, could be a single task that is running action `nsp.https` with the corresponding inputs, e.g. `method`, `url`, and `body`.

As a next step check the Mistral documentation for the [`with-items`](https://docs.openstack.org/mistral/ocata/dsl/dsl_v2.html#processing-collections) attribute, to process collections. While the update is rather small, your workflow is now able to acknowledge a list of alarms.

If you got stuck, the workflow below provides one way of solving this.

/// details | Possible Solution
    type: success
```yaml
version: '2.0'

<UNIQUE-WORKFLOW-NAME>:
  type: direct

  description: Acknowledge Alarm

  input:
    - alarms: []

  output:
    result: <% $.output %>

  tasks:
    acknowledgealarm:
      with-items: alarm in <% $.alarms %>
      action: nsp.https
      safe-rerun: true
      input:
        method: PATCH
        url: https://restconf-gateway/restconf/data/nsp-fault:alarms/acknowledgement=<% $.alarm.fdn %>
        body:
          nsp-fault:alarms: [{}]
      publish:
        output:  <% task().result %>
```
///

This workflow can be difficult to run as it requires a list of objects as input, and each object must include an attribute called `fdn`. To make execution easier, we will create a user-friendly input form that allows selecting from currently active alarms.

### Add a Workflow Input Form

To provide a user-friendly input form with alarm pickers, you first need to create an ad-hoc action. This action enables the picker component to query the backend for live alarm data.

#### Create An Ad-hoc Action

* Go to Ad-hoc Actions.
* Create a new action using the + button (upper right corner).
* Paste in the snippet below and replace `<UNIQUE-ACTION-NAME>` with a unique name.

```yaml
version: '2.0'

<UNIQUE-ACTION-NAME>:
  base: nsp.https
  base-input:
    url: https://restconf-gateway/restconf/operations/nsp-inventory:find
    method: POST
    body:
      input:
        xpath-filter: /nsp-fault:alarms/alarm-list/alarm[perceived-severity = 'major']
        include-meta: false
    resultFilter: $.content.get('nsp-inventory:output').data.select({alarmName=>$.get('alarm-type-qualifier'),fdn=>$.get('alarm-fdn'),alarmType=>$.get('alarm-type-id'), neId=>$.get('ne-id')} )  
    auth: <% $.token_auth %>
  input:
    - token_auth
    - formValues: {}
  output: <% $.content %>
```

From the NSP WFM WebUI tryout your new ad-hoc action after creation.

You should now see a filtered list including `alarmName`, `fdn`, `alarmType`, and `neId`. The `fdn` is required to acknowledge alarms via API.

#### Add the schema-form definition

Next, define a user-input form for alarm selection:

* In your workflow, open the drop-down menu and select `Input Form`.
* Paste the schemaForm definition (JSON) below, replacing `<UNIQUE-ACTION-NAME>` with the ad-hoc action name you just created.

```json
{
    "type": "object",
    "properties": [
        {
            "name": "alarms",
            "title": "List of Alarms",
            "description": "List of alarms",
            "columnSpan": 4,
            "newRow": true,
            "readOnly": false,
            "required": false,
            "type": "list",
            "suggest": {
                "action": "<UNIQUE-ACTION-NAME>"
            },
            "component": {
                "input": "picker"
            },
            "properties": [
                {
                    "name": "neId",
                    "type": "string",
                    "title": "Ne Id",
                    "description": "Ne Id"
                },
                {
                    "name": "alarmName",
                    "type": "string",
                    "title": "Alarm Name",
                    "description": "Alarm Name"
                },
                {
                    "name": "fdn",
                    "type": "string",
                    "title": "FDN",
                    "description": "FDN",
                    "visible": false
                },
                {
                    "name": "alarmType",
                    "type": "string",
                    "title": "Alarm Type",
                    "description": "Alarm Type"
                }
            ]
        }
    ]
}
```

### Run your workflow

Run your workflow by selecting the alarms that require acknowledgment. Then, verify in the NSP WebUI that the selected alarms have been acknowledged successfully.

## Summary

Congratulations!  You have completed this activity and tackled the real operator problem of too many alarms, and too much manual effort to process them. With WFM, you have:

* Queried alarms via RESTCONF APIs.
* Applied filters to make alarm lists meaningful.
* Wrapped API calls into reusable `Ad-hoc Actions`.
* Created a workflow with operator-friendly input form that let users acknowledge alarms directly.

The result: a repeatable, operator-friendly workflow that saves time, reduces errors, and ensures consistent handling of alarms.