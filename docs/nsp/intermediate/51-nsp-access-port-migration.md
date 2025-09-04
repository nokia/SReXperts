---
tags:

- NSP
- Workflow Manager
- Service Management
- Service Fulfillment Operations
---

# Access Port Migration

|     |     |
| --- | --- |
| **Activity name** | Access Port Migration |
| **Activity ID** | 51 |
| **Short Description** | Migration automation of `epipe` SAPs from one port to another |
| **Difficulty** | Intermediate |
| **Tools used** | NSP, Visual Studio Code |
| **Topology Nodes** | :material-router: PE1, :material-router: PE3 |
| **References** | [NSP Docs](https://infocenter.nokia.com), [OpenStack Mistral](https://docs.openstack.org/mistral/latest/) |

## Objective

In this activity you will address a common operational challenge: migrating customer services from one access port to another. Whether you are preparing for a planned card replacement or reacting to a sudden failure, moving SAPs and services manually is both slow and prone to error.
Using NSP Workflow Manager, you will automate this migration. You will prepare the target port, deploy a workflow that moves SAPs and associated services, and validate the outcome. By the end, you will have applied NSP automation to a real-world problem, reducing manual steps, minimizing risk, and accelerating recovery — all while keeping control of the process.

## Technology Explanation

Automation of access port migration relies on two main capabilities in NSP: **Workflows** and **Intents**. Together, Workflows and Intents allow you to move beyond manual CLI operations, enabling structured, repeatable, and reliable service migrations while maintaining control and oversight.

### Workflow Manager

Workflow Manager (WFM) enables operators to automate repetitive or error-prone tasks. Instead of performing manual actions individually, WFM lets you chain API calls into a single, reusable process. This allows you to define end-to-end procedures, including validation, execution, and post-operation checks, all in a structured and repeatable way.

Besides name and description, workflows may have optional tags. While these tags are mainly informational and allow for quicker filtering, in NSP some values, like `KafkaTrigger`, enable usage in specific contexts. In this exercise, we encourage triggering workflows in-context from the Service Activation WebUI, which requires adding the tag `sf-network-operation`. For more details, check the [Developer Portal](https://network.developer.nokia.com/learn/25_4/programming/workflows/workflow-manager-apis).

### Intent Manager

Intent Manager is a module within the Nokia Network Services Platform (NSP) that enables intent-based networking (IBN) by translating higher-level objectives into automated network actions. It has the ability to abstract the complexity of network configuration by allowing operators to express what they want, rather than how to do it.

By separating declarative intent configuration (including validation) from intent operations like audits and synchronization, Intent Manager enables CRUD operations with operational lifecycle and control. The sync operation is used for deploying changes into the network but also to reconcile network object configuration in cases of misalignment, while audits are used to identify misalignments including network configuration drift.

The library of intent-types can be updated at runtime, while intent-types are developed in JavaScript using YANG-defined intent models. Using JavaScript enables full flexibility beyond pure configuration management. Intent Manager natively supports heterogeneous networks (multi-vendor, multi-domain).

### Tools

These capabilities are complemented by operator-facing tools that make automation accessible and integrated into daily workflows:

* **NSP WebUI**: Manage workflows, intents, and services end-to-end in a graphical interface.
* **Visual Studio Code Plugin**: Author and validate workflows and forms locally, then publish directly to NSP, providing a smooth development experience.

---

## Tasks

### Validate Port Configuration

Ensure the following on PE1 and PE3:

- The breakout ports `1/1/c6` and `1/1/c8` exist
- Ports `1/1/c6/1` and `1/1/c8/1` are configured as access ports with dot1q encapsulation
- Check for services bound to these ports, as those are potentially subject for migration

Use NSP MDC or CLI to check and modify configurations. If conflicting services exist, either:

- Use a different port pair, or
- Remove the existing service if it's not required for this activity

---

### Create a Sample Service

Provision a service using NSP IBSF (Intent-Based Service Fulfillment):

- Service type: `epipe` or `redundant-eline`
- Endpoint A: PE1, port `1/1/c6/1`
- Endpoint B: PE3, port `1/1/c6/1`

Options:

- Use NSP WebUI IBSF wizard
- Use Visual Studio Code Plugin (recommended for versioning and local validation)
- Use RESTCONF APIs directly (advanced)

This service will later be migrated using the workflow.

---

### Create Workflows in NSP

Create two workflows using the YAML content provided below:

- Main Workflow: `PortMigration_<GroupID>`
- Sub-Workflow: `PortMigrationSubworkflow_<GroupID>`

Ensure:

- Workflow tags include `sf-network-operation`
- Status is set to `PUBLISHED`
- Group ID is inserted in workflow names for uniqueness

/// admonition | What are the workflows doing?
     type: question
/// details | Answer
    type: success
The main workflow queries intents on a specific port and calls the sub workflow to patch them with a backup port. The sub workflow builds the PATCH payload and executes RESTCONF operations.
///
///

/// admonition | What changes are needed for other service types?
     type: question
/// details | Answer
    type: success
Add parsing and payload logic for other intent types (e.g., `vpls`, `vprn`) in the Python block of `generatePatchPayload`.
///
///

---

### Create Input Forms

Use `AUTO GENERATE UI` in NSP to auto-fill basic input fields. Then manually enhance forms with the following example for `backupPort`:

```yaml
- name: backupPort
  title: BACKUP PORT
  description: move all SAPs here
  columnSpan: 4
  newRow: true
  readOnly: false
  required: true
  type: string
  component:
    input: autoComplete
  suggest:
    action: nspWebUI.portList
    name:
      - name
```

This enables dynamic suggestions in the UI based on available NSP ports.

---

### Pre-Migration Check

Scenario: Migrate a service on PE1 from `1/1/c6/1` to `1/1/c8/1`.

Using NSP WebUI, CLI, or MDC:

- Confirm that the source port `1/1/c6/1` is in use by the service
- Ensure `1/1/c8/1` is configured and not already in use

Only proceed once pre-checks validate the environment.

---

### Run the Workflow via NSP

1. Navigate to **NSP > Service Management**
2. Select an active service with SAPs on `1/1/c6/1`
3. Click the 3-dot menu and choose **Execute Workflow**
4. Select your custom `PortMigration_<GroupID>` workflow
5. Enter inputs based on your validation:
```yaml
neId: PE1
port: 1/1/c6/1
backupPort: 1/1/c8/1
intentType: redundant-eline
intentTypeVersion: 2
```
6. Click **Run**

---

### Validate Migration

After execution, verify:

- Service intent now references `1/1/c8/1`
- Old SAP on `1/1/c6/1` has been removed

Use NSP Service Management view, RESTCONF API, or CLI output to confirm.

---

## Summary

Congratulations — you’ve completed this activity! Take a moment to look back at what you achieved:

* Prepared port configurations
* Deployed a test `epipe` or `redundant-eline` service
* Built and published NSP workflows
* Customized workflow UI forms
* Executed a migration through Service Management
* Verified SAP movement to the backup port

You’ve now seen how NSP simplifies port migration through reusable automation.

## Next Steps

If you’d like to explore further, you could:

* Extend the logic to support `vpls` or `vprn` services
* Add rollback handling in case of a PATCH failure
* Consolidate the subworkflow into the main workflow

This gives you the chance to deepen your understanding and push NSP workflows even further.

---

## Full YAML Workflows

/// note
Remember, your NSP system is shared! Don't just copy paste the workflows below! Ensure to replace `<GroupID>` with the id of your group to avoid conflicts with other groups executing the same activity.
///

### Main Workflow: PortMigration

```yaml
version: '2.0'
PortMigration_<GroupID>:
  type: direct
  description: Migrate SAPs from source port to backup port
  tags:
    - sf-network-operation
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
      workflow: PortMigrationSubworkflow_<GroupID>
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

### Sub-Workflow: PortMigrationSubworkflow

```yaml
version: '2.0'

PortMigrationSubworkflow_<GroupID>:
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