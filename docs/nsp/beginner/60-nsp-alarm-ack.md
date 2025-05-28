---
tags:
  - NSP
  - Workflow Manager
  - Fault Management
  - SchemaForm
---

# Acknowledge alarms using workflows

|                             |                                                                                               |
|-----------------------------|-----------------------------------------------------------------------------------------------|
| **Activity name**           | Acknowledging specific alarms using workflows                                                 |
| **Activity ID**             | 60                                                                                            |
| **Short Description**       | In this exercise we will use the Workflow Manager to choose and acknowledge a specific alarm |
| **Difficulty**              | Beginner                                                                                      |
| **Tools used**              | WFM                                                                                           |
| **Topology Nodes**          |  |
| **References**              |  |

The main purpose of this exercise is to get familiar with NSP WFM ad-hoc actions that can be used as a “suggest” functions
to provide input-forms widgets (pickers, suggest) with data retrieved from NSP. In this particular case we will query
the list of active alarms, while the workflow will acknowledge the corresponding alarm.

If you consider to do the coding part of this activity, you could also explore the code and eventually apply some modifications.
For improved Developer eXperience, consider using Visual Studio Code with the WFM extension available from
[marketplace](https://marketplace.visualstudio.com/items?itemName=Nokia.nokia-wfm).
Steps to install the VS Code extension can be found on our
[Developer Portal](https://network.developer.nokia.com/tutorials/vscode-extensions/workflow-manager-visual-studio-code-extension).

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Get Alarms

Open NSP WebUI and open `Workflows` found under the `PROGRAMMING` category.

Select `Actions` view.

On the left hand side we have two types of actions: “Ad-Hoc Actions” and "System Actions".

Let’s start by getting a list of all major alarms on the network:

* Navigate to the “Systems Actions” and search for the “nsp.https” action.
* Click on the 3 dots on the right side and choose “Run”
* Search for the restconf based Alarms API in the [Developer Portal](https://network.developer.nokia.com/api-documentation/)
* You can also find a lot of examples in [this postman collection](https://documenter.getpostman.com/view/26248101/2sAY4uCNvf#de0ea146-e51a-455a-84c5-19f438712103)
* Use it to retrieve a list of all major alarms in NSP

/// details | This is url if you get stuck |
    type: tip
url: https://restconf-gateway/restconf/operations/nsp-inventory:find
///

```yaml
url: <url>
method: POST
body:
  input:
    xpath-filter: /nsp-fault:alarms/alarm-list/alarm[perceived-severity = 'major']
    include-meta: false
```

Try to adjust the filter, for example by picking different severity levels like critical, minor, or warning.

### Yaqulator

Copy the received response and navigate to the “Yaqulator” in the upper right corner of the Actions page.
The Yaqulator functionality allows developers to quickly prototype YAQL expressions based on the received response.

Paste the response on the bottom left side YAML/JSON Context section

In the upper YAQL Expression section use the following filter expression to get the list of alarm names:

```yaml
$.result.content.get('nsp-inventory:output').data.select($.get('alarm-type-qualifier'))
```

Do the same exercise to filter for “fdn”, “alarmTypes” & “neId”

### Create Ad-Hoc Action

Next, navigate back to the ad-hoc Actions and create a new action using the button in the upper right corner.
Paste in the below snippet while substituting the action name with a unique name for the Alram list action

```yaml
version: '2.0'

< UNIQUE-ACTION-NAME>:  
  base: nsp.https
  base-input:
    url: <url>
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

“Validate” then “Create”, then try it out by choosing “Run” in the 3 dots button on the action you just created.
You should get a response of a list of major alarms while filtering the response for alarmName, fdn, alarmType and neId.

### Create the Workflow

To test the newly created action, create a new workflow that acknowledges an alarm selected by a user.
First navigate to [Developer Portal](https://network.developer.nokia.com/api-documentation/) and search for the RESTCONF call that acknowledges an alarm based on a specific FDN.

/// details | This is url if you get stuck |
    type: success
url: https://restconf-gateway/restconf/data/nsp-fault:alarms/acknowledgement=<% $.alarm.fdn %>
///

Then create a workflow that uses this API call to acknowledge an alarm.
Don't forget to use a unique name for the newly created Workflow, as well as adding the appropriate API call in the url section.

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
        url: <ACK-ALARM-URI>
        body:
          nsp-fault:alarms: [{}]
      publish:
        output:  <% task().result %>
```

Validate, Create then Publish the Workflow

### Create Input Form

Create a user input form by navigating to “Input Form” in the Workflow’s drop down menu
Paste the following JSON based schemaForm while substituting the suggestFunction with your unique AD-Hoc action name:

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
                "action": "< UNIQUE-ACTION-NAME>"
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

### Execute 

Execute your Workflow by choosing the alarms on the list that require acknowledgment.
