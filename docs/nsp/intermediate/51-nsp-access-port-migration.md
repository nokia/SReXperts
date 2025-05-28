---
tags:
  - NSP
  - Workflow Manager
  - Service Management
---

# Access Port Migration Automation

|     |     |
| --- | --- |
| **Activity name** | Access Port Migration Automation |
| **Activity ID** | 51 |
| **Short Description** | Migration of EPIPE SAPs from one port to another |
| **Difficulty** | Intermediate |
| **Tools used** | Visual Studio Code (or code-server) |
| **Topology Nodes** | :material-router: PE1, :material-router: PE3 |
| **References** |     |

In this activity we use NSP Workflow Manager to move SAPs from one port to a backup port. This can be useful
for activities like planned maintenance (card swap) or as temporary solution to quick fix a port that went
down. The workflow is expected to be triggered manually from the NSP WebUI. This exercise will focus on
**`redundant-eline`** and  **`epipe`** services, but the implementation could be extended in context of
this hackathon to support other services like VPLS and VPRN.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Ensure Port Configuration and Usage

In this activity we are planning to use ports `1/1/c6/1` and `1/1/c8/1` on **PE1** and **PE3**.
Port `1/1/c6/1` should be used for initial service configuration.
Port `1/1/c8/1` is about to become our backup port to move the configuration to.

Execute the following steps on PE1 and PE3:

* Check if the corresponding break-out ports `1/1/c6` and `1/1/c8` are setup. Configure if needed!
* Check if the ports `1/1/c6` and `1/1/c8` are setup as access port, with dot1q encap. Configure if needed!
* Check for pre-existing services, to avoid conflicts running this activity
 
### Create an ELINE service

Configure at least one service of type `redundant-eline` or `epipe` between PE1 to PE3 using port `1/1/c6/1`.
Ideally, you want multiple services to be created while even a mix of epipes and redundant elines is possible.

### Create Workflows in NSP

Create the following two workflows in NSP. As NSP is shared across all hackathon labs, make sure using unique
names. Because the first workflow is calling the second as sub-workflow, make sure to apply the renaming
consistently.

At this stage, we are providing you with full working examples of those workflows.

/// tab | Main Workflow `PortMigration`
```yaml
version: '2.0'

PortMigration:
  type: direct
  
  description: to be added by you
  
  input:
    - neId
    - port
    - backupPort
    - intentType
    - intentTypeVersion
  output:
    status: <% $.status %>
    message: <% $.message %>
  tasks:
    getServiceInfo:
      action: nsp.https
      input:
        url: https://restconf-gateway/restconf/operations/ibn:search-intents
        method: POST
        accept: application/yang-data+json
        contentType: application/yang-data+json
        body:
          ibn:input:
            search-from: ES
            filter:
              intent-type-list:
                - intent-type: "<% $.intentType %>"
                  intent-type-version: <% $.intentTypeVersion %>
              config-required: "true"
              predicate: MATCHES
              argument:
                - name: port-id
                  value: "<% $.port %>"
                - name: device-id
                  value: "<% $.neId %>"
      publish:
        service_data: <% switch(task().result.content["ibn:output"]["total-count"] > 0 => task().result.content["ibn:output"]["intents"]["intent"], true => []) %>
        taskStatus: <% task().state %>
      publish-on-error:
        message: 'Getting Services from NSP failed, please check input params'
        status: "failed"
      on-success:
        - patchIntentServices: <% len($.service_data) > 0 %>
        - noServiceFound: <% len($.service_data) = 0 %>

    noServiceFound:
      action: std.noop
      publish:
         message: "No SAPs found on port <% $.port %> on <% $.neId %>"
         status: "success"

    patchIntentServices:
      with-items: intent_data in <% $.service_data %>
      concurrency: 5
      workflow: PortMigrationSubworkflow
      input:
        neId: <% $.neId %>
        port: <% $.port %>
        backupPort: <% $.backupPort %>
        intent: <% $.intent_data %>
      publish:
        patchIntentStatus: <% task(patchIntentServices).result.status %>
        message: "Service SAPs successfully moved to backup port"
        status: "success"
      publish-on-error:
        message: 'Patch operation failed on one or more intents'
        status: "failed"
      on-success:
        - done

    done:
      action: std.noop
      publish:
        status: "success"
        message: <% str($.patchIntentStatus) %>
```
///

/// tab | Sub Workflow `PortMigrationSubworkflow`
```yaml
version: '2.0'

PortMigrationSubworkflow:
  type: direct

  description: to be added by you

  input:
    - neId
    - port
    - backupPort
    - intent

  output:
    status: <% $.status %>

  tasks:
    generatePatchPayload:
      action: nsp.python
      input:
        context: <% $ %>
        script: |
          from urllib.parse import quote

          def build_patch_payload(intent, nodeId, portId, backupPortId):
            service_name = intent.get("target")
            intent_type = intent.get("intent-type")
            intent_data = intent["intent-specific-data"]
            delete_url = None

            if intent_type == "redundant-eline":
                sites = intent_data["redundant-eline:redundant-eline"]["site-details"]["site"]
                for site in sites:
                    if site.get("device-id") == nodeId:
                      for sap in site.get("sap-details", {}).get("sap", []):
                          if sap.get("port-id") == portId:
                              inner = sap.get("inner-vlan-tag", -1)
                              outer = sap.get("outer-vlan-tag", -1)
                              encoded_port = quote(portId, safe='')
                              delete_url = (
                                  f"data/nsp-service-intent:intent-base/intent={service_name},{intent_type}/"
                                  f"intent-specific-data/redundant-eline:redundant-eline/site-details/"
                                  f"site={nodeId}/sap-details/sap={encoded_port},{inner},{outer}"
                              )
                              sap["port-id"] = backupPortId

            elif intent_type == "epipe":
              epipe_data = intent_data["epipe:epipe"]
              for site_key in ["site-a", "site-b"]:
                  site = epipe_data.get(site_key, {})
                  if site.get("device-id") == nodeId:
                      for ep in site.get("endpoint", []):
                          if ep.get("port-id") == portId:
                              inner = ep.get("inner-vlan-tag", -1)
                              outer = ep.get("outer-vlan-tag", -1)
                              encoded_port = quote(portId, safe='')
                              delete_url = (
                                  f"data/nsp-service-intent:intent-base/intent={service_name},{intent_type}/"
                                  f"intent-specific-data/epipe:epipe/{site_key}/"
                                  f"endpoint={encoded_port},{inner},{outer}"
                              )
                              ep["port-id"] = backupPortId

            return {
              "url": f"data/nsp-service-intent:intent-base/intent={service_name},{intent_type}",
              "target": service_name,
              "delete_url": delete_url,
              "body": {
                  "nsp-service-intent:intent": [
                      {
                          "intent-type": intent_type,
                          "service-name": service_name,
                          "intent-specific-data": intent_data
                      }
                  ]
              }
          }

          return build_patch_payload(<% $.intent %>, '<% $.neId %>', '<% $.port %>', '<% $.backupPort %>')
      publish:
        svcInfo: <% task().result %>
      publish-on-error:
        status: {"error": "<% task().result %>", "state": "FAILED"}
      on-success:
        - checkStatus

    checkStatus:
      action: std.noop
      on-success:
        - deleteServiceAccessPoints: <% $.svcInfo.delete_url != null %>
      publish:
        status: "No SAPs found"

    deleteServiceAccessPoints:
      action: nsp.https
      input:
        url: https://restconf-gateway/restconf/<% $.svcInfo.delete_url %>
        method: DELETE
        accept: "application/json"
        contentType: "application/json"
      on-success:
        - sendPatchRequest
      publish-on-error:
        status: {"error": "<% task().result %>", "state": "FAILED"}

    sendPatchRequest:
      action: nsp.https
      input:
        url: https://restconf-gateway/restconf/<% $.svcInfo.url %>
        method: PATCH
        accept: application/yang-data+json
        contentType: application/yang-data+json
        body: <% $.svcInfo.body %>
      publish:
        status: "success"
        patchResponse: <% task().result %>
      publish-on-error:
        status: {"error": "<% task().result %>", "state": "FAILED"}
      on-success:
        - finish

    finish:
      action: std.noop
      publish:
        status:
          state: "success"
          neId: <% $.neId %>
          port: <% $.port %>
          backupPort: <% $.backupPort %>
          service-name: <% $.svcInfo.target %>
```
///

Study both workflows carefully!

/// admonition | Questions
     type: question
What are the workflows doing and how do they interact?
Update the workflow descriptions accordingly!

/// details | Solution
    type: success
The first workflow is the main workflow to be called by the operator. It consumes the
node, the port and the backup port. It calls the Intent Manager RESTCONF API to get
the list of all SAPs terminating on the node/port provided. It calls the 2nd workflow
as sub-workflow with a concurrency of 5 executions.

The 2nd workflow is doing the actual SAP migration, one intent-instance at a time.

As the first workflow requires intent-type and version as input, if there is a mix
of service intent-types being used, the script may need to be called multiple times.
///

Would those workflows support other service-types but `redundant-eline` or `epipe`?
What would need to be changed to make it work for other service-types?

/// details | Solution
    type: success
Dependencies exist mainly in the 2nd workflow, as the API calls to
migrate services require adjustments based on the service-type.
///
///

/// tip
We  want to execute the `PortMigration` workflow from the **Service Management**
application in NSP. That's why the workflow must be labeled correctly using the
**`sf-network-operation`** tag.
///

Edit the `PortMigration` workflow and ensure the following tag is present:

```yaml
  tags:
    - sf-network-operation
```

Feel free to add other tags!

**Don't forget to update the status from `DRAFT` to `PUBLISHED`!**

### Generate input forms

To improve usability, generate input-forms. Give it a start using the `AUTO GENERATE UI` button.
There are some rules in place, that auto-render the form based on attribute-names and default-values.

In the given examples, the auto-generator does not work for `BACKUP PORT`and `INTENT TYPE VERSION`.
Consider using `PORT` as template to come up with your own definition of `BACKUP PORT`.

/// details | Possible solution (only look here as a last resort!)
    type: success

```yaml
  - name: backupPort
    title: BACKUP PORT
    description: move all SAPs here
    columnSpan: 4
    newRow: true
    readOnly: false
    required: false
    type: string
    component:
      input: autoComplete
    suggest:
      action: nspWebUI.portList
      name:
        - name
```
///

### Simulate a Port Down Scenario

* Ensure a service (`redundant-eline` or `epipe`) is provisioned with SAP on a port like `1/1/c6/1`
* The corresponding node (e.g., `PE1`) must have a backup port available (e.g., `1/1/c8/1`)

### Run the Workflow via Service Management

1. Go to **NSP > Service Management**
2. Find and select an existing service instance
3. Click `⋮` (3-dot menu) > **Execute Workflow**
4. Choose `PortMigration` from the list (use your custom name!)
5. Fill in the inputs:

| Field                 | Description                                             |
| --------------------- | ------------------------------------------------------- |
| `NE ID`               | Source port to be retired (`1/1/c6/1`)                  |
| `PORT`                | Node where port exists (`PE1`)                          |
| `BACKUP PORT`         | New port to migrate SAPs to (e.g., `1/1/c8/1`)          |
| `INTENT TYPE`         | Set to `redundant-eline`                                |
| `INTENT TYPE VERSION` | Typically `2` or `3`, depending on the deployed service |

6. Click **Run**

### Validate the Outcome

* Check using `Service Management`
* Ensure all SAPs have been moved to the backup port (`1/1/c6/1` ==>  `1/1/c8/1`)

### Bonus

Here some additional ideas on how to continue:

* Try to run the sub-workflow directly
* Run the python-code outside WFM to test changes in isolation
* Further optimize the input (auto-pick intent-type-version)
* Generate a HTML/PDF report, which SAPs have been migrated
* Implement a dry-run option, to validate which services/saps would be affected
* Extend the workflows to support other service-types like ELAN or L3VPN
* Combine both workflows into a single one
* Maximize experience: Ask for NE, port and backup-port only! Migrate all services found!
* Trigger the workflow automatically, based on kafka events (port-down alarm raised on topic `nsp-fm-alerts`)
* Rollback configuration changes, if PATCH failed