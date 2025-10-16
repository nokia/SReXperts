---
tags:
  - NSP
  - Workflow Manager
  - Device Operations
  - Visual Studio Code
---

# Network Element Configuration Snapshot/Rollback

|     |     |
| --- | --- |
| **Activity name** | Network Element Configuration Snapshot/Rollback |
| **Activity ID** | 71 |
| **Short Description** | Take nodal configuration snapshots and rollback without the need to reboot. |
| **Difficulty** | Intermediate |
| **Tools used** | NSP<br/>Visual Studio Code with NSP extensions for Workflows and Artifacts |
| **Topology Nodes** | :material-router: PE1, :material-router: PE2, :material-router: PE3, :material-router: PE4, :material-router: P1, :material-router: P2 |
| **References** | [Nokia Developer Portal](https://network.developer.nokia.com/learn/24_11/programming/workflows/wfm-workflow-development/wfm-best-practices) (Sign up for a free account)<br/>[WFM Best Practices](https://network.developer.nokia.com/learn/24_11/programming/workflows/wfm-workflow-development/wfm-best-practices)<br/>[WFM Actions/Functions](https://network.developer.nokia.com/learn/24_11/programming/workflows/wfm-workflow-development/wfm-workflow-actions)<br/>[WFM with vsCode](https://network.developer.nokia.com/learn/24_4/network-programmability-automation-frameworks/workflow-manager-framework/wfm-workflow-development/workflow-manager-visual-studio-code-extension/?highlight=vscode) |

## Objectives

Network device configurations evolve continuously, and it is common practice to track configuration drift over time. When recent changes cause issues, you need to quickly understand what changed and when. Beyond analysis, you want the ability to revert to a known stable configuration—ideally applying a rollback as a quick fix without disrupting other services, avoiding outages that would otherwise need to wait for the next scheduled maintenance window.

In this activity, you will explore an alternative to the traditional NE Backup/Restore capabilities in NSP. Key differences include:

* **On-demand snapshots**: Capture configurations at any time without persisting the full nodal configuration (e.g., `admin save`).
* **Partial coverage**: Focus snapshots on specific configuration subtrees rather than capturing the entire configuration.
* **In-service rollbacks**: Revert only the delta, avoiding service interruptions and nodal reboots.

In this activity, you will create your own unsigned artifact bundle, which can be imported into NSP via Artifact Manager to get started quickly. A template and simple recipe are provided to minimize setup overhead.

The design goal is to make snapshot/rollback operations appear as standard Device Operations (LSO) in NSP. As a result, you will be able to:

* Capture snapshots of individual devices or groups, on-demand, and scheduled.
* View configuration snapshots directly from the Device Management WebUI.
* Compare snapshots to identify changes (e.g. drift).
* Rollback to a snapshot safely, without disrupting ongoing services.

## Technology Explanation

NSP snapshots leverage transactional, declarative device management protocols (e.g., NETCONF, gNMI), providing a universal and lightweight approach for configuration capture and rollback. This avoids dependency on vendor-specific file formats or file transfer protocols and reduces the risk of service disruption during configuration changes.

## Tasks

/// note
The device operation bundle you are developing is unsigned, allowing you to modify the workflows without the need to recreate and reinstall the bundle (convenient for prototyping). However, due to access-control restrictions we will need to give your user/group access to the contained workflows after importing.
///

/// warning
Remember that you are using a shared NSP system. Therefore, ensure your group-number is part of the operation and workflow names you are creating to ensure uniqueness.
///

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

---

In the first part of this activity, you will gain practical experience in following areas of NSP:

* **Artifact Manager** will be used to import the artifact bundle and monitor the installation process.
* **Operations Manager** and **Device Management** control snapshot and rollback operations.
* **Workflow Manager** can be used to examine an operation execution's result.

### Getting Started

Creating things from scratch can feel daunting and even overwhelming. To save you from piecing together all the required components that define the structure and format of the `snapshot` and `rollback` operations, we provide you with a [**LSO Skeleton Bundle Generator**](./resources/bundle-generate-71.html). This tool creates an artifact bundle in the exact structure expected by the system, giving you a ready-made starting point. From there, you can easily build upon it and move on to more advanced use cases.

* Unpack and review the content.

/// note | Artifact Bundle Content:
```
% cd ne-snapshot-rollback-2
% tree
.
├── metadata.json
├── operation-types
│   ├── rollback
│   │   ├── ne-rollback-2.yaml
│   │   ├── ne-rollback-2.yang
│   │   └── operation_types.json
│   └── snapshot
│       ├── ne-snapshot-2.yaml
│       ├── ne-snapshot-2.yang
│       └── operation_types.json
└── workflows
    ├── rollback
    │   ├── ne-snapshot-2.yaml
    │   └── README.md
    └── snapshot
        ├── ne-snapshot-2.json
        ├── ne-snapshot-2.yaml
        └── README.md

7 directories, 12 files
```
///

* Import the customized artifact bundle into NSP
    * Login to NSP.
    * Open the hamburger menu and select `Artifacts`.
    * Select `IMPORT & INSTALL`.
    * Select the zip-file to proceed by clicking on `IMPORT & INSTALL`.

/// note
For easier bundle management, consider using the [Artifact Manager Visual Studio Code extension](https://marketplace.visualstudio.com/items?itemName=Nokia.artifactadminstrator). It helps with listing, packaging, and installing artifacts directly from your IDE. Documentation is available on the [Developer Portal](https://network.developer.nokia.com/learn/24_11/nsp-administration/artifacts/artifact-visual-studio-codeextension/).
///

/// warning
Your artifact bundle contains device operations (LSO artifacts). These are considered in-use after deployment. The LSO deployer blocks Artifact Manager uninstalling or removing the bundle until such operations are `withdrawn`.

Updating your bundle works without withdrawing/deleting the previous version, as long the updated bundle and artifacts have higher version numbers. Updating an operation-type may fail if the new YANG model is incompatible with model of the previously installed operation-type.
///

Once your bundle is shown as `Installed`, you can continue.

### Taking Configuration Snapshots

In this step you will test your new operation. We continue using group 2 as an example. Please remember to adjust it to your group in the steps below.

1. In NSP, select `Device Management` in the hamburger menu.
2. In the dropdown menu, select `All Operations`.
3. Click on `+ OPERATION` to create a new operation.
4. Select Operation Type `ne-snapshot-2`.
5. Provide operation name, for example `initial-cfg-snapshot-2`.
6. Select P1, P2, PE1, PE2, PE3, PE4 as `Target NEs` to take a snapshot.
7. After the creation the user can check the operation status, it should set to `completed`.
8. Check the operation result and cross-navigate to see the underlying workflow executions.

After finishing all steps, we would have successfully used a custom workflow to create NE snapshots without relying on copying `config.cfg` from the NE.

### Access Configuration Snapshots

The `Operation` section under `Device Management` is common for all NSP operations. To simplify usability, you can access the snapshot/rollback operations and results from the `Managed Network Elements` view.

1. In NSP, select `Device Management` in the hamburger menu.
2. In the dropdown menu, select `Managed Network Elements`
3. Click on the 3 dots for your `P1` node to open the context menu for device specific `Operations`
4. Explore the options to access operation history, review and create backups.
5. In NSP, select `File Server` in the hamburger menu (under `NSP Administration`) to locate the backup files.

/// admonition | Questions
    type: question
- What are the different ways to list and display configuration snapshots?
- In what format are configuration snapshots stored?
- Find a way to compare configuration snapshots!
- What is the directory, in which backups/snapshots are stored on the File Server?
///

### Compare and Rollback Configuration Snapshots

1. Apply changes to a node using CLI or Model Driven Configurator WebUI and take another config snapshot! Example: Add or update location and contact information under `configure > system`. Do you see the changes?
2. Use the rollback operation to restore the initial configuration (without reboot)! Was the config restored?
3. Update your `snapshot` operation to become the default `backup` operation.
4. Try the option to `Compare with current NE config` (only works, if your operation is the default operation)
5. Create a scheduled operation, that takes NE snapshots from all SR OS nodes every hour.

/// warning
Be aware, that only one(!) backup operation can be made default! In conclusion, you may experience issues if others execute this activity, as we are using a shared NSP system.
///

---

In the second part of this activity, we will get into coding. We will extend the operation capabilities by updating the underlying workflows to:

* Improve the workflow by applying best practices
* Extend the workflow to support SR Linux nodes

### Digging into the Code

Review the code examples provided for operation-types and workflows.
You can access the code either through Visual Studio Code or directly in the Workflow Manager WebUI.

Exploration Points:

* Identify where in the NSP WebUI you can view code, and note which areas provide read-only vs. editable access. Check Artifact Manager, Workflow Manager, and Device Operation-Types (LSOM).
* Break down the components of an artifact bundle to understand how artifacts are packaged and deployed.
* Analyze the elements of an operation artifact (operation model, mapping, script, etc.) and how they work together.
* Examine the role of the mapping profile in linking inputs and outputs to the underlying model.
* Compare workflow input/output definitions against the operation model and mapping. See how they align with the WebUI rendering.
* Notice redundancies in rollback operation inputs (e.g., backup operation vs. backup path/filename). Reflect on why these exist, by triggering rollbacks from different WebUI contexts to observe differences in workflow execution inputs.
* Observe how the snapshot storage path includes the nodal release and consider how this design choice ensures version accuracy and compatibility.

### Improve your Snapshot Operation

Review the workflow that takes configuration snapshots. Check, if there is anything that can be improved! Are [best practices]("https://network.developer.nokia.com/learn/24_4/network-programmability-automation-frameworks/workflow-manager-framework/wfm-workflow-development/wfm-best-practices/") appropriately applied?

You may find that the action `getConfig` publishes the configuration as a JSON string. This approach works well for smaller configurations like we have in this hackathon. Applying this approach to production-scale nodal configurations can lead to publishing megabytes of data and is not recommended as it impacts resource consumption.

To work around this, you may consider updating the workflow. The `nsp.https` action allows to store the result in the local filesystem by using the input attribute called `fileName`. Change the task to store the JSON response as file under the path `/tmp/<% $.neName %>.nokia-conf.json`. When applying this change, you need to consider adding another input attribute `resultFilter : $.content`. This applies a YAQL expression to the response before writing it to a file, else everything would be wrapped into a top-level element called `content`.

/// warning
By using `/tmp` for temporary storage, consider the case that multiple snapshots (typically on different target nodes) are generated in parallel. Therefore, consider using unique filenames, so parallel operation executions will not impact each other.
///

To upload the file to the file-service, you need to update the task `uploadConfig`. Uploading files is relatively easy using the `nsp.uploadFile` action.

You may spot that the JSON payload is now minified, while it was prettified before. This impacts usability when displaying or comparing backups. As of today, the action `nsp.https` does not have an option to store the result as pretty JSON. You may consider using Python to make it pretty.

/// warning
While we've applied the best practices changes on the snapshot artifacts, you may observe that the rollback workflow renders a large `nsp.https` request, that contains the entire config in the body payload. Please note, the action `nsp.https` does not have an option to load the payload body from the filesystem.
///

/// details | Cheatsheet

Updated definition for `getConfig`:
```
action: nsp.https
input:
  method: GET
  url: https://restconf-gateway/restconf/data/network-device-mgr:network-devices/network-device=<% $.neId %>/root/nokia-conf:configure
  fileName: /tmp/<% $.neName %>.nokia-conf.json
  resultFilter : $.content        
publish-on-error:
  lsoInfo: "Failed: getting config from MD-SROS node"
  lsoStageError: <% task().result %>      
on-success:
  - createBackupFolder
```

Updated definition for `uploadConfig`:
```
action: nsp.uploadFile
input:
  fileServicePath: <% $.dirName %>/<% $.timestamp %>
  localFilePath: /tmp/<% $.neName %>.nokia-conf.json
on-success:
  - zipConfig
```

To prettify a JSON file in the filesystem, the following task in Python may help:
```
    prettify:
      action: nsp.python
      input:
        context:
          filename: /tmp/<% $.neName %>.nokia-conf.json
        script: |
          import json
          import sys
          with open(context["filename"], 'r') as f:
            data = json.load(f)
          with open(context["filename"], 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)
```

///

### Extend your Snapshot Operation to support SR Linux

If you made it to this point you have mastered operations and workflows and have even done a bit of coding. In this final part of this activity, we want to extend the snapshot operation/workflow to support SR Linux.

/// note
If you've modified your snapshot workflow in the previous part of this activity, please consider copying the workflow content to your local system to avoid losing it.
///

Let's start with the operation first. As the mapping profile associates supported device-types with workflows to be executed, you need to extend the mapping profile to support the corresponding SR Linux families. Take a look into the NSP operation `nsp-ne-backup` that is installed by default. It contains the entries `7220 IXR SR Linux` and `7250 IXR SR Linux` for `family_type`. Extend the list of supported families for your own snapshot operation while still pointing to the same workflows!

/// note
Updating an operation-type in NSP is not supported from the NSP WebUI nor through the use of APIs. Therefore, the only way to update operations in NSP is via Artifact Manager. You will need to update the mapping profile on your local machine and rebuild the bundle. Because bundles and artifacts are versioned, Artifact Manager will not update installed artifacts if the version number stays the same. You must either uninstall your artifact bundle or increase the version numbers. In case of option 1, please be aware that operation-types can only be removed when marked as `withdrawn` in `Device Administration`. Increasing the version number is the recommended approach.
///

After you've imported your updated bundle, run a test to validate that the existing functionality still works.

The most notable difference between SR OS and SR Linux would be that SR OS stores all configuration in a single root module `/nokia-conf:configure` while SR Linux has multiple root-level modules.

In addition, be aware that SR Linux mixes configuration (read/write) and state attributes (read-only) in the same subtree. As the ask is to capture the configuration only, the RESTCONF query parameter `?content=config` should be added to the corresponding RESTCONF `GET` request.

/// note
The NSP implementation executes a `get-config` NETCONF RPC if the query-parameter `?content=config` is provided. For gNMI, the behavior depends on the path being queried. If a class (e.g. YANG `list`) is requested, gNMI Subscribe is used. If an object (e.g. YANG `list entry` or `container`) is requested, gNMI Get is used. Only the latter has a means of restricting the content received in response to configuration only.

In this activity, we focus on root paths that are all classes. As a result, responses will always include state attributes, regardless of whether the query-option `?content=config` is used. Consequently, SR Linux snapshots will contain both configuration and state. For this reason, we’ll stick with the snapshot operation so you can verify that snapshots can be displayed and compared as expected.
///

You may use the [SRL YANG Explorer](https://yang.SR Linux.dev) or
NSP MDC to find appropriate root paths. You may want to start with the following root paths:

* srl_nokia-network-instance:network-instance
* srl_nokia-interfaces:interface
* srl_nokia-system:system

It's recommended to store the output of those queries in separate files when creating your configuration snapshot, the resulting ZIP archive should now contain multiple files.

/// details
    type: success

If you got stuck with the coding exercises, use the [**Complete LSO Bundle Generator**](./resources/bundle-generate-71.html?kind=complete) to create a bundle that contains an updated snapshot operation, to apply best-practices and support SRLinux. Compare the original operation with the updated operation, to understand the updates that have been applied.
///


## Summary

Congratulations! You have completed this activity. Take a moment to review what you achieved:

* Experienced Device Management Operations to trigger configuration snapshot and rollback operations.
* Learned how to display and compare configuration snapshots to detect configuration drift.
* Understood the differences between traditional backup/restore and snapshot/rollback operations.
* Customized and installed an artifact bundle using NSP Artifact Manager.
* Extended the artifact bundle provided to support SR Linux.
* Explored the relationship of Device Operations, Workflows, Artifact Bundles and File Service.
* Looked in WFM design best-practices.