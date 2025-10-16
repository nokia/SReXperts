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

* Open NSP WebUI.
* Click on `☰` icon on the top left corner to open the so-called hamburger menu and select `Workflows` found under the `PROGRAMMING` category.
* Click on `Main` → `Dashboard` to open the dropdown menu and select the `Actions` view.
* On the left, you will see two types of actions: `Ad-hoc Actions` and `System Actions`.
* Navigate to `System Actions` and search for the `nsp.https` action.
* Open the `nsp.https` context-menu (three dots on the right) and select `Run`.
* Provide the `Input` in YAML format as shown below to execute a [RESTCONF](https://www.rfc-editor.org/rfc/rfc8040.html)-compliant `GET` query and click on the `RUN` button to execute the request.

/// note | `nsp.https` input to list **all** alarms
```yaml
url: https://restconf-gateway/restconf/data/nsp-fault:alarms/alarm-list/alarm
method: GET
```

To explore the NSP APIs more deeply, the [Developer Portal](https://network.developer.nokia.com/api-documentation) and the corresponding [Postman collection](https://documenter.getpostman.com/view/26248101/2sAY4uCNvf#de0ea146-e51a-455a-84c5-19f438712103) are good starting points. You will find the API endpoints required to query and acknowledge alarms.
///

* Now, lets retrieve a list of all major alarms in NSP, by adjusting the `nsp.https` input like this:

/// note | `nsp.https` input to list **major** alarms
```yaml
url: https://restconf-gateway/restconf/operations/nsp-inventory:find
method: POST
body:
  input:
    xpath-filter: /nsp-fault:alarms/alarm-list/alarm[perceived-severity = 'major']
    include-meta: false
```

While the filtering options available through a standard RESTCONF GET request are quite limited, the NSP-specific operation `nsp-inventory:find` provides support for XPATH filters. By adjusting the path expression, it becomes straightforward to filter for specific attribute values.
///

* Adjust the filter, for example by picking different severity levels like `critical`, `minor`, or `warning` by updating the `xpath-filter` value.
* Review the JSON response and identify additional attributes to filter on, such as alarm-type. Update the xpath-filter accordingly, and when filtering by alarm-type-id or alarm-type-qualifier, use the values from the initial query to ensure they match existing entries.


/// note | `nsp.https` input to list alarms of specific `alarm-type` value
```yaml
url: https://restconf-gateway/restconf/operations/nsp-inventory:find
method: POST
body:
  input:
    xpath-filter: /nsp-fault:alarms/alarm-list/alarm[alarm-type-qualifier = 'PeerConnectionDown']
    include-meta: false
```

Make sure your query response includes alarms, since the next step will use YAQL to transform the YAML output.

///

### Process Alarm API Response

Copy the response into your clipboard.

/// Warning
The `COPY` button in the action run dialogue copies the request, not the response! To copy the response use your operating system’s standard shortcuts (on macOS: `CMD-A`, `CMD-C`; on Windows: `CTRL-A`, `CTRL-C`).
///

Open Yaqluator using the **`.*`** button. Yaqluator lets you quickly prototype YAQL expressions against the received response. Paste the YAML response from your clipboard into the `Context` field (replacing the default `{}`), then enter the following string in the `Expression` field to list the alarm types:

```yaml
$.result.content.get('nsp-inventory:output').data.select($.get('alarm-type-qualifier'))
```

Click the `EVALUATE` button. The alarm type value for each alarm in the response is shown the `Result` section.

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

/// tip | Pro Tip
Earlier we warned that the `COPY` button in the action execution dialog does not copy the response. However, it is very useful: Pressing this button copies an instrumentalized task definition into your clipboard, which you can directly paste into your workflow definition.
///

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

From the WebUI, a workflow must first be `Validated` and `Created`. At this point it is in `DRAFT` mode. To run it, you need to publish it to `RELEASED`. If you want to make further edits, switch it back to `DRAFT`. When working in Visual Studio Code, you can save time: the workflow extension automatically handles these steps for you.

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