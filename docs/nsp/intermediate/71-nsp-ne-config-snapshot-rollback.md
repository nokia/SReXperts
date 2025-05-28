---
tags:
  - NSP
  - Workflow Manager
  - Device Operations
  - Visual Studio Code
---

# NE config snapshot/rollback

|     |     |
| --- | --- |
| **Activity name** | NE config snapshot/rollback |
| **Activity ID** | 71 |
| **Short Description** | This activity is about device operation to take configurations snapshots from a device and to rollback to snapshots. |
| **Difficulty** | Intermediate |
| **Tools used** | VS Code with NSP extensions for Workflows and Artifacts |
| **Topology Nodes** | :material-router: PE1, :material-router: PE2, :material-router: PE3, :material-router: PE4, :material-router: P1, :material-router: P2 |
| **References** | [WFM Best Practices](https://network.developer.nokia.com/learn/24_11/programming/workflows/wfm-workflow-development/wfm-best-practices)<br/>[WFM Actions/Functions](https://network.developer.nokia.com/learn/24_11/programming/workflows/wfm-workflow-development/wfm-workflow-actions)<br/>[WFM with vsCode](https://network.developer.nokia.com/learn/24_4/network-programmability-automation-frameworks/workflow-manager-framework/wfm-workflow-development/workflow-manager-visual-studio-code-extension/?highlight=vscode)  |

## Prerequisites
* Basic knowledge the NSP UI
* Basic knowledge about Workflow Manager
* Basic knowledge about Device Operations
* No fear to touch code (for the 2nd part of this activity)

/// note | from beginner to intermediate
If you consider to do the coding part of this activity, you will need to explore the code and
eventually apply some code modification. For improved Developer eXperience, consider using
Visual Studio Code (or code-server) with the WFM VS Code extension available from
[marketplace](https://marketplace.visualstudio.com/items?itemName=Nokia.nokia-wfm).wh
///

## Objectives

The purpose of this activity is to take advantage of NSP Device Operations to take NE configuration snapsnhots allowing to
rollback to snapshots taken. NE snapshot/rollback operations will appear as backup/restore operation-category under NSP
Device Management.

The difference to backup/restore operations that come as part of the product is, that we are taking advantage of transactional,
declarative device management protocols (gNMI, NETCONF). One of the benefits of this approach is, that we can  directly access
the running configuration while there is no need to save the configuration prior to the download. Another
benefit is, that the solution can easily be adopted to other device vendors/families, as long those support NETCONF or gNMI.
Finally, there is no dependency to file-transfer (xFTP/SCP) and vendor-specific filenames.

In order to keep the barrier for executing this activity low, we will provide you with a template and simple recipe to
create your own unsigned artifact bundle, that you can import into NSP using Artifact Manager to get started.

## Goals to achieve

### Part 1 - Beginner (steps 1-5)

Grain practical experience in following areas of NSP:

* NSP Artifact Manager, by importing the artifact bundle and monitoring the installation process.
* NSP Operations Manager and Device Management by executing snapshot and rollback operations, view and compare snapshots
* NSP Workflow Manager, by checking the execution results

### Part 2 - Intermediate (step 6, 7)

Extend the operation capabilities by updating the workflows:

* Improve the workflow by applying some best practices
* Extend the workflow to support SR Linux nodes

## Tasks

/// note
The provided operation is unsigned, allowing the user to modify the workflows without the need to recreate and reinstall
the bundle (convenient for prototyping). However, due to access-control restrictions we will need to give your user/group
access to the workflows after importing.
///

/// warning
Remind, that you are using a single NSP system (shared), that is used for all groups. Therefore, ensure
your group-number is part of the operation and workflow names you are creating to ensure uniqueness.
///

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Step 1 - Download, customize and install bundle:

1. Clone this repo to your local system.
2. Check the content of [cfg-snapshot-artifact-bundles](./resources/cfg-snapshot-artifact-bundle.zip)
3. Adjust the artifact-bundle content for your group and build the artifact.
4. Login to NSP. Access details will be provided during the hackathon.
5. In NSP, open the hamburger menu and select `Artifacts`.
6. Select `Import and Install`, find the zip file and install the bundle.

/// details | Solution to make it your own bundle:
    type: success

/// note | Content of the folder is:
```
% cd cfg-snapshot-artifact-bundle
% tree
.
├── metadata.json
├── operation-rollback
│   ├── ne-rollback-groupxx.yaml
│   ├── ne-rollback-groupxx.yang
│   └── operation_types.json
├── operation-snapshot
│   ├── ne-snapshot-groupxx.yaml
│   ├── ne-snapshot-groupxx.yang
│   └── operation_types.json
├── workflow-rollback
│   ├── README.md
│   └── ne-rollback-groupxx.yaml
└── workflow-snapshot
    ├── README.md
    ├── ne-snapshot-groupxx.json
    └── ne-snapshot-groupxx.yaml

4 directories, 12 files
```
///

Here is how to replace `groupxx` with `group02`.
Please, adjust to the group that has been assigned to you!

/// tab | MacOS
```
export instance=group02
cp -r cfg-snapshot-artifact-bundle /tmp
cd /tmp/cfg-snapshot-artifact-bundle
find . -name '*groupxx*' -exec bash -c 'mv "$0" "${0//groupxx/$instance}"' {} \;
find . -type f -exec sed -i '' s/groupxx/$instance/g {} \;
zip -r /tmp/cfg-snapshot-$instance.zip *
```
///
/// tab | Linux
```
export instance=group02
cp -r cfg-snapshot-artifact-bundle /tmp
cd /tmp/cfg-snapshot-artifact-bundle
find . -name '*groupxx*' -exec bash -c 'mv "$0" "${0//groupxx/$instance}"' {} \;
find . -type f -exec sed -i s/groupxx/$instance/g {} \;
zip -r /tmp/cfg-snapshot-$instance.zip *
```
///
/// tab | Windows  PowerShell
```
Copy-Item -Path "cfg-snapshot-artifact-bundle" -Destination "C:\tmp" -Recurse -Force
Set-Location -Path "C:\tmp\cfg-snapshot-artifact-bundle"
$instance = "group002"
Get-ChildItem -Path "." -Filter "*groupxx*" | Rename-Item -NewName { $_.Name -replace 'groupxx', $instance }
Get-ChildItem -Path "." -File | ForEach-Object {
    $content = Get-Content -Path $_.FullName
    $newContent = $content -replace 'groupxx', $instance
    Set-Content -Path $_.FullName -Value $newContent
}
$outputZip = Join-Path -Path "C:\tmp" -ChildPath "cfg-snapshot-$instance.zip"
Compress-Archive -Path "*" -DestinationPath $outputZip -Force
```
///
/// tab | Details
- rename `operation-rollback/ne-rollback-groupxx.yaml` to `operation-rollback/ne-rollback-group02.yaml`
- rename `operation-rollback/ne-rollback-groupxx.yang` to `operation-rollback/ne-rollback-group02.yang`
- rename `operation-snapshot/ne-snapshot-groupxx.yaml` to `operation-snapshot/ne-snapshot-group02.yaml`
- rename `operation-snapshot/ne-snapshot-groupxx.yang` to `operation-snapshot/ne-snapshot-group02.yang`
- rename `workflow-rollback/ne-rollback-groupxx.yaml`  to `workflow-rollback/ne-rollback-group02.yaml`
- rename `workflow-snapshot/ne-snapshot-groupxx.yaml`  to `workflow-snapshot/ne-snapshot-group02.yaml`
- rename `workflow-snapshot/ne-snapshot-groupxx.json`  to `workflow-snapshot/ne-snapshot-group02.json`
- replace `groupxx` with `group02` in file `metadata.json` (11 occurrences)
- replace `groupxx` with `group02` in file `operation-rollback/operation_types.json` (3 occurrences)
- replace `groupxx` with `group02` in file `operation-rollback/ne-rollback-groupxx.yaml` (1 occurrences)
- replace `groupxx` with `group02` in file `operation-rollback/ne-rollback-groupxx.yang` (7 occurrences)
- replace `groupxx` with `group02` in file `operation-snapshot/operation_types.json` (3 occurrences)
- replace `groupxx` with `group02` in file `operation-snapshot/ne-snapshot-groupxx.yaml` (1 occurrences)
- replace `groupxx` with `group02` in file `operation-snapshot/ne-snapshot-groupxx.yang` (4 occurrences)
- replace `groupxx` with `group02` in file `workflow-rollback/ne-rollback-groupxx.yaml` (2 occurrences)
- replace `groupxx` with `group02` in file `workflow-snapshot/ne-snapshot-groupxx.yaml` (2 occurrences)
///
///

/// note
At this point, we recommend the explore usage of the [Artifact Manager VS Code extension](https://marketplace.visualstudio.com/items?itemName=Nokia.artifactadminstrator).
It will help you to explore/download artifact bundles installed to NSP, Create, Update and Package artifact bundles, and finally upload/install artifact bundles in NSP.

Documentation is available on [Developer Portal](https://network.developer.nokia.com/learn/24_11/nsp-administration/artifacts/artifact-visual-studio-codeextension/).
///

/// warning
If an artifact bundle contains device operations, you may struggle to update/uninstall/delete this bundle using Artifact Manager. Reason is,
that after installation the device operation is assumed in-use, so you first need to deprecate it by setting the lifecycle state accordingly.
///

**Once your bundle is shown as `Installed`, you can continue...**

### Step 2 - Test the operation
1. In NSP, select `Device Management` in the hamburger menu.
2. In the dropdown menu, select `All Operations`
3. Click on "+ OPERATION" to create a new operation
4. Select Operation Type `ne-snapshot-group02` (adjust to your group)
5. Provide operation name, for example `initial-cfg-snapshot-group02` (adjust to your group)
6. Select P1, P2, PE1, PE2, PE3, PE4 as `Target NEs` to take a snapshot (adjust to your group)
7. After the creation the user can check the operation status, it should set to completed.
8. Check the operation result and cross-navigate to see the underlying workflow executions

### Step 3 - Explore NSP WebUI shortcuts
The `Operation` section under `Device Management` is common for all NSP operations.
To simplify usability, you can access the snapshot/rollback operations and results
from the `Managed Network Elements` view.

1. In NSP, select `Device Management` in the hamburger menu.
2. In the dropdown menu, select `Managed Network Elements`
3. Click on the 3 dots for your `P1` node to open the context menu for device specific `Operations` (adjust to your group)
4. Explore the options to access operation history, review backups and create backups.
5. In NSP, select `File Server` in the hamburger menu (section: `NSP Administration`)

/// note | Questions
- What are the different ways to list and display configuration snapshots?
- In what format are configuration snapshots stored?
- Find a way to compare configuration snapshots!
- What is the directory, in which backups/snapshots are stored on the File Server?
- Do you spot differences between `File Server` and `View all backup files`?
///

### Step 4 - Taking it a step further
1. Apply changes to a node using CLI or MDC and take another config snapshot!
   Example: Add/Update location and contact information under `configure > system`.
   Do you see the changes?
2. Use the rollback operation to restore the initial configuration (without reboot)! Was the config restored?
3. Update your operations to become the default operation. What has changed?
4. Try the option to `Compare with current NE config` (only works, if your operation is the default operation)
5. Delete snapshot operations. Do you still have access to the snapshot itself? Can it be displayed/restored?
6. Create a scheduled operation, that takes NE snapshots from all SR OS nodes every hour.

/// warning
Be aware, that only one backup operation and one restore operation can be made `default`! In conclusion,
you may experience issues if other hackathon participants execute this activity, as we are using a shared
NSP system.
///

### Step 5 - Digging into the code
Review the code examples provides for the operation-types and the workflows.
There is different ways to access the code using vsCode or from WebUI.

/// admonition | Questions
     type: question
- Explore the different spots in the NSP WebUI that show the code! Which ones allow write-access?
- What are the components of an artifact bundle?
- What are the components of an operation artifact?
- What's the function of the mapping profile in operations?
- Compare the workflow input/output against the operation model/mapping and WebUI rendering!
- The rollback operation input has redundancies (`backup_operation` versus backup path and filename). Do you know why?
- The path to store snapshots contains the nodal release. Explore, why this is the case!
///

### Step 6 - Improve the operation
Review the workflow that takes the configuration snapshot.
Check, if there is anything that can be improved!
Are best practices appropriately applied?

You may find, that action `getConfigSROS` publishes the configuration as JSON string.
This approach works well for smaller configurations, like in context of this Hackathon.
But considering production-scale nodal configurations, be reminded that publishing
mega-bytes of data is not recommended, as it impacts resource usage of the WFM services
and DB footage.

To work around this, you may consider updating the workflow. The `nsp.https` action allows
to store the result in the local file-system by using the input attribute called `fileName`.
Change the task to store the JSON response as file under the path
`/tmp/<% $.neName %>.nokia-conf.json`. When applying this change, you need to consider
to add another input attribute `resultFilter : $.content`. This applies a YAQL expression
to the response before writing it to a file, else everything would be wrapped into a
top-level element called `content`.

Please ensure to use an unique filename, as multiple snapshot operations for different
targets may run in parallel.

To upload the file to the file-service, you need to update the task `writeConfigFile`. Uploading
files is relatively easy using the `nsp.uploadFile` action.

As `/tmp` is a shared file-system, validate if you can take multiple snapshots from different devices
in parallel! We are not removing files from `/tmp`. Does this cause any further issues?

You may spot, that the JSON file is now minified, while it was prettified before. This impacts
usability when displaying or comparing backups. As of today, the action `nsp.https` does not
have an option to store the result as pretty JSON. You may consider using python to make it pretty.

While we've applied the best practices change for taking a configuration snapshots, you may
observe that the rollback workflow publishes the configuration too and renders a full blown
`nsp.https` request, that contains the entire config in the body payload. Please note, the action
`nsp.https` does not have an option to load the payload body from the filesystem.

/// details | Cheatsheet

Updated definition for `getConfigSROS`:
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

Updated definition for `writeConfigFile`. You may even consider renaming it to `uploadConfigFile`:
```
action: nsp.uploadFile
input:
  fileServicePath: <% $.dirName %>/<% $.timestamp %>
  localFilePath: /tmp/<% $.neName %>.nokia-conf.json
on-success:
  - zipConfig
```

To prettify a JSON file in the file-system, the following task in Python may help:
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

### Step 7 - Extend the operation
Congrats, if you already made it to this point! You've mastered operations and workflows and even
you've done a bit of coding. This is excellent! In the final part of this activity, we want to go
practical. The ask is to extend the snapshot operation/workflow to support SR Linux.

/// warning
If you've modified your snapshot workflow in the previous part of this activity, please consider
to copy the workflow content to your local system to avoid losing it.
///

Let's start with the operation first. As the mapping profile associates supported device-types
with workflows to be executed, you need to extend the mapping profile to support the corresponding
SR Linux families. Take a look into the NSP operation `nsp-ne-backup` that is installed by default.
It contains the entries `7220 IXR SRLinux` and `7250 IXR SRLinux` for `family_type`. Extend
the list of supported families for your own operations, while we will keep the same workflows!

/// note
Updating an operation in NSP is supported neither from the NSP WebUI nor there is a vsCode extension
for Operation Manager. Therefore, the only way to update operations in NSP is via Artifact Manager!
In consequence, you will need to update the mapping profile on your local machine and rebuild the bundle.
Because bundles and artifacts are versioned, Artifact Manager will not update installed artifacts if
the version number stays the same. You may consider to either uninstall/remove your artifact bundle
(option 1) or increase the version numbers (option 2). In case of option 1, please be aware that
operation-types can only be removed when marked as `withdrawn` in `Device Administration`.
///

After you've imported your updated bundle, you may consider running a test to validate, that the
existing functionality still works. Once this is done you can start updating your workflows.

The most notable difference between SR OS and SR Linux would be, that SR OS stores all configuration
in a single root module (/nokia-conf:configure) while SR Linux uses multiple root-level modules.

In addition, be aware that SR Linux mixes configuration (read/write) and state attributes (read-only)
in the same subtree. As the ask is to capture the configuration only, the RESTCONF query parameter
`?content=config` should be added to the corresponding RESTCONF `GET` request.

/// note
The NSP implementation executes a `<get-config/>` netconf rpc, if the query-parameter
`?content=config` is provided. For gNMI the behavior depends on the path being queried.
If a class (yang list) is requested, gNMI Subscribe is used. If an object (yang list entry)
is requested, gNMI Get is used. Only the later (gNMI Get) has an object to restrict the
content to configuration only.

In this activity we are focusing on root-paths to be queried, which are all classes
(not objects). In consequence the responses will contain state attributes regardless of
the query-option `?content=config` being provided or not.
///

As MDC does not support to fetch all module instance by accessing /root, and because we are not
interested in OpenConfig models, you may use the [SRL YANG Explorer](https://yang.srlinux.dev) or
NSP MDC to find appropriate root paths. You may want to start with the following root paths:

* srl_nokia-network-instance:/network-instance
* srl_nokia-interfaces:/interface
* srl_nokia-system:system

It's recommended to store the output of those queries in separate files, while the ZIP archive would
now contain multiple files.
