# Checkpoint Management

|     |     |
| --- | --- |
| **Activity name** | Checkpoint Management |
| **Activity ID** | 40 |
| **Short Description** | Create and manage config checkpoints  |
| **Difficulty** | Advanced |
| **Topology Nodes** | Any SRL or SR OS node |
| **References** | [LSO Framework](https://network.developer.nokia.com/learn/25_11/API-reference/network-functions/device-management/lsom-framework-apis/#Guidelines), [Workflow Development](https://network.developer.nokia.com/learn/25_11/artifact-development/programming/workflows/wfm-workflow-development/) |


## Objective

When you change live network devices, mistakes or unexpected side effects are always possible. Operators need known-good restore points (checkpoints of the running configuration) and a repeatable way to create, roll back to, or clean up those snapshots. Doing that only by hand, or only on the box without a consistent operational pattern, is slow, error-prone, and hard to scale across many nodes.

In this activity you use **Device Operations** to create checkpoints, revert to one you already saved, then extend the flows instead of relying only on one-off CLI steps.

## Technology explanation

### Device Operations (Operations Manager)

The Device Management in NSP provides a set of tools for managing network devices throughout their lifecycle. These tools are grouped into Operations that can perform a wide range of tasks, including checking device configuration, taking backups, restoring data, and upgrading software.

These operations help oversees running those workflows, keeping track of their progress, and giving you control over when and how they run.

Each operation targets one or more devices. To run it, the workflow needs to know the device's ID (called `ne-id`). Extra fields come from the operation’s YANG model and mapping.

### Workflow Manager (WFM)

Workflows are written in YAML using [Mistral DSL v2](https://docs.openstack.org/mistral/ocata/dsl/dsl_v2.html): straightforward expressions, branching, and data passing between tasks. Skim the bundled examples first, then open the tasks you plan to change.

### Artifact Bundle

In NSP, an artifact bundle can group artifacts for several applications at once. In this activity, the bundle ships LSO device operations and the workflow assets those operations need. 

You can publish an updated bundle without withdrawing or deleting the previous one as long as the bundle and its artifacts use higher version numbers. Expect install to fail if a new operation-type ships a YANG model that is incompatible with the model from the version already installed.

/// note
The LSO deployer prevents Artifact Manager from uninstalling or removing the bundle until the operation is set to **`withdrawn`**. You should not need to uninstall anything here. The operation is meant to stay deployed while you add the enhancements in the tasks below.
///

## Tasks

**You should read these tasks from top to bottom before beginning the activity.**

It is tempting to skip ahead, but tasks may require you to have completed previous tasks before tackling them.

/// warning
Remember that you are using a shared NSP system. Include your group number in every workflow input that asks for **Group ID** (and in filters such as `g<N>-p1` where applicable).
///

### Quick start on NSP Web UI

|     |     |
| --- | --- |
| **NE Session** | `☰` → `Network Search and Inventory` → find your group's PE node (for example `g7-pe1`) → open the row context menu `⋮` → `Open in NE Session`. |
| **NSP Help** | `?` icon at the top right for context-aware quick help and to open the Help Center. On some pages, the `?` icon also links directly to related Help Center articles. |
| **Operations Manager** | `☰` → `Device Management` → `All Operations` |
| **Workflow Manager** | `☰` → `Workflows` |
| **Artifacts** | `☰` → `Artifacts` |

/// note

- The operation bundle will be unsigned, giving you the opportunity to update workflows without rebuilding and reinstalling the whole bundle each time. 
- Since installing an artifact is admin-only task, your user or group still needs to be granted access to the bundled workflows because of NSP access controls. Reach out to the team if you dont see your workflows.
- The supplied bundle already runs local checkpoint creation for SR Linux
- It is advised that you do **not** edit the operation artifact for this exercise but put your customizations as part of the workflows.

///

### Checkpoint creation

Defining a valid `checkpoint` operation bundle by hand means a lot of structural boilerplate before you reach any useful logic. Use the [**LSO Skeleton Bundle Generator**](./resources/nsp-activity-40/generator.html) instead. It generates an artifact bundle in the format NSP expects, so you start from a working template and focus on the workflows in this activity.

- When you want to inspect the bundle locally, download, unpack the archive and review the layout.
- When you trust the template, use the generator’s **Upload to NSP** to install the bundle.

/// details | Whats interesting about the bundle?
    type: example

```
% cd ne-checkpoint-revert-1.0.0-g00
% tree
.
├── content
│   ├── actions-revert-group00
│   │   ├── getFSCheckpoints-group00.action
│   │   └── getLCCheckpoints-group00.action
│   ├── ne-checkpoint-group00
│   │   ├── README.md
│   │   ├── ne-checkpoint-group00.json
│   │   └── ne-checkpoint-group00.yaml
│   ├── ne-revert-group00
│   │   ├── README.md
│   │   ├── ne-revert-group00.json
│   │   └── ne-revert-group00.yaml
│   └── operation-checkpoint
│       ├── ne-checkpoint-group00.yaml
│       ├── ne-checkpoint-group00.yang
│       └── operation_types.json
└── metadata.json

6 directories, 12 files
```

Explore the files:

- Map where you can view or edit code (**Artifact Manager**, **Workflow Manager**, **Operations Manager** / operation types) and note what is **read-only** versus editable.
- Trace how the **artifact bundle** is laid out: which folders map to operations, workflows, and supporting actions, and how NSP deploys them together.
- For one **operation artifact**, list the moving parts (YANG model, mapping, scripts or helpers, metadata) and describe how data flows from the Web UI into a workflow run.
- Read the **mapping profile** and explain how operation inputs and outputs bind to the underlying model fields.
- Compare **workflow** input and output definitions to the operation model and mapping, then confirm how that shows up in the **Operations Manager** forms you used earlier.
- On **rollback-style** flows, compare inputs such as "pick a backup operation" versus "raw path or filename". Trigger similar actions from **different** Web UI entry points and inspect the resulting workflow inputs to see why both styles sometimes exist.
- On SR Linux, follow where checkpoints land under `/etc/opt/srlinux/checkpoint/` (path may vary slightly by release; use device state or workflow logs to confirm the exact file layout on your node).

///

#### Run the checkpoint operation (optional)

When the bundle status is **`Installed`**, you can try this optional run.

1. Open **Operations Manager** and start `+ Operation`.
2. Select the checkpoint operation type that came from your bundle (the walk-through text uses `ne-checkpoint-groupNN`; your type name ends with your group id, for example `ne-checkpoint-group07`). Set an operation name, for example `first-demo-checkpoint-07`.
3. Under **Target NEs**, select one or more SR Linux nodes. If the operation input offers `Save to FS`, you can toggle it, but the starter bundle does not implement saving checkpoints to the file server yet. Adding that path is part of the main exercise, so treat this optional run as on-device checkpoints only.
4. Select `Execute Immediately`, then click `Run`. When the run finishes, the execution status should show **`completed`**.
5. Review the operation result. From the operation execution row, open the `⋮` menu and choose `Open in Workflows` to jump to the underlying workflow execution and its details.

### Revert to existing checkpoint

As part of the checkpoint creation, the bundle comes with a ready to use ne-revert workflow to perform the revert operation on SR Linux devices. 

#### Run the revert operation (optional)

1. Navigate to **Workflow Manager** and select **Workflows** from the drop down. 
2. Open the workflow definition **`ne-revert-group00`** (or your group’s name).
3. Click **Execute** (play).
4. Fill the inputs: pick **one SR Linux** node that already has a **local** checkpoint, choose the checkpoint file to revert to, and skip file-service options for this smoke test.
5. Run, then use the **quick-view** icon on the execution to inspect steps, inputs, and outputs.

/// details | How to explore the code?
    type: question

- In the Web UI, open **Definition** and skim every task: inputs, publishes, and branches.
- Decide **where** SR OS or "revert from NSP copy" logic should plug in before you edit.
- Compare workflow input/output definitions against the operation model and mapping. See how they align with the WebUI rendering.

///


### Extend to SR OS

#### Checkpoint Creation

To extend the flow for **SR OS**, the default execution stops because *createSROScheckpoint* is still a *std.noop* (no operation) placeholder. So your job is to:

- Find the **SR OS CLI** (or MD-CLI) steps that create a **local** checkpoint and where the `.cfg` (or equivalent) file ends up on disk.
- Replace *createSROScheckpoint* with **`nsp.managed_cli`** so those commands run on SR OS nodes.
- Test on **one SR OS** node and confirm the checkpoint file exists where you expect.
- **Publish** fields the rest of the workflow needs (same idea as SR Linux), e.g. `sourcePath` and `checkpoint` (watch spelling on `sourcePath`).

You can always refer to the [SR OS documentation](https://documentation.nokia.com/sr/26-3/index.html) and to [Workflow Development best practices](https://network.developer.nokia.com/learn/25_11/artifact-development/programming/workflows/wfm-workflow-development/wfm-best-practices/).

/// details | Expanded hint
    type: success

Updated definition for `createSROScheckpoint` task:

```yaml

    # SR OS dummy commit to create new config.cfg
    createSROScheckpoint:
      action: nsp.managed_cli
      input:
        neId: <% $.neId %>
        stopOn: <% $.stop %>
        idleTimeout: 30
        closeSession: true
        cmds:
          - /!md-cli
          - configure private
          - commit
          - exit
      publish:
        sourcePath: cf3:/config.cfg
        checkpoint: config.cfg
      on-success:
        - CheckpointSuccess
      on-error:
        - CheckpointFailed

```

///

#### Revert

If you look at the previous step, reverting from a **local checkpoint file** already works on **SR Linux**. For **SR OS**, the operation simply does not work. So we need to add **`revertFromFileSROS`** as a **`nsp.managed_cli`** task (the action name is **`managed_cli`**, not `manage_cli`).

- Look up how SR OS applies a **full-replace** load from a file on the device.
- Note where `.cfg` checkpoints live for your software train.
- Implement *revertFromFileSROS* and validate on **one** SR OS node (confirm the running config matches what you expect after revert).
- Publish whatever downstream tasks need (`loadFile`, status strings, etc.).

You can always refer to the [SR OS documentation](https://documentation.nokia.com/sr/26-3/index.html) and to [Workflow Development best practices]
(https://network.developer.nokia.com/learn/25_11/artifact-development/programming/workflows/wfm-workflow-development/wfm-best-practices/).

/// details | Expanded hint
    type: success

Create a new task for `revertFromFileSROS`:

```yaml

    revertFromFileSROS:
      action: nsp.managed_cli
      input:
        neId: <% $.neId %>
        stopOn: <% $.stop %>
        idleTimeout: 30
        closeSession: true
        cmds:
          - /!md-cli
          - configure private
          - load full-replace <% $.loadFile %>
          - commit
          - exit
      publish:
        lsoInfo: "Revert from file <% $.loadFile %> successfully completed"
      publish-on-error:
        lsoInfo: "Revert from file <% $.loadFile %> failed"
      on-success:
        - RevertSuccess
      on-error:
        - RevertFailed

```

///


### NSP File Service

#### Checkpoint creation

Now that we have seen how to create checkpoints within NE, lets explore how the same can be saved within NSP File Server. 

1. **Create the target folder** on the file service.
    - Reuse the same path pattern *getDeviceInfo* already publishes as `dirName` (vendor, family, `ne-id`, etc.), e.g. `/lsom/checkpoint/<% task().result.content.get("ne-vendor") %>/<% task().result.content.get("ne-family").replace(" ","_") %>/<% task().result.content.get("ne-id") %>`.
    - Call the directory API with **`nsp.https`** ([directory create](https://network.developer.nokia.com/api-collections/25.11/NSP_File_Server/#directory-apis-to-create-a-directory-on-nsp-file-storagePOST)).
2. **Transfer** the checkpoint file from the NE to that folder.
    - Use the predefined **`lso_transferFilesFromNe`** action with inputs such as:
        - `neId`: `<% $.neId %>`
        - `sourcePath`: `<% $.sourcePath %>`
        - `destinationPath`: `<% $.dirName %>/<% $.timestamp %>`
        - `ftUuid`: unique id for this transfer, e.g. `<% $.neId+"-nsp_"+$.timestamp %>`
3. **Rename** the uploaded file so a later task can fetch a predictable name. Use the file-service [rename API](https://network.developer.nokia.com/api-collections/25.11/NSP_File_Server/#file-apis-to-rename-a-file-available-at-nsp-file-storagePOST).


/// details | Expanded hint
    type: success

Updated definition:

```yaml
    createBackupFolder:
      action: nsp.https
      input:
        method: POST
        url: https://file-service/nsp-file-service-app/rest/api/v1/directory?dirName=<% $.dirName %>/<% $.timestamp %>
        resultFilter : $.content.data.fileName
      publish-on-error:
        lsoStageError: <% task().result %>
        lsoInfo: "Failed: creating checkpoint directory on file-server"
      on-success:
        - transferCheckpoint
      on-error:
        - CheckpointFailed
    
    transferCheckpoint:
      action: lso_transferFilesFromNe
      input:
        neId: <% $.neId %>
        sourcePath: <% $.sourcePath %>
        destinationPath: <% $.dirName %>/<% $.timestamp %>
        ftUuid: <% $.neId+"-nsp_"+$.timestamp %>
      publish:
        lsoInfo: "starting transfering file from node to server"
      publish-on-error:
        lsoInfo: "Files transfer from NE to File Server failed.Please check execution progress for details. Possible reasons for failure: FTP policy not assigned or has incorrect properties, file transfer failed due to interim failure, file service not functional, file transfer timeout, etc"
        lsoStageError: <% task().result.where((isDict($) and $.containsKey('errorType')) or not isDict($)).last() %>
        stage: "fileTransfer"
      on-success:
        - renameCheckpoint
      on-error:
        - CheckpointFailed
    
    renameCheckpoint:
      action: nsp.https
      input:
        method: POST
        url: https://file-service/nsp-file-service-app/rest/api/v1/file/rename?sourceFilePath=<% $.dirName %>/<% $.timestamp %>/<% $.checkpoint %>&&targetFilePath=<% $.dirName %>/<% $.timestamp %>/nsp_checkpoint.<% $.extension %>
      publish-on-error:
        lsoStageError: <% task().result %>
        lsoInfo: "Failed: creating checkpoint directory on file-server"
      on-success:
        - CheckpointSuccess
      on-error:
        - CheckpointFailed
```

Make sure you update the `createSRLcheckpoint` and `createSROScheckpoint` tasks to go to the previous two tasks only when required:

```yaml
      on-success:
        - createBackupFolder: <% $.saveFS %>
        - CheckpointSuccess: <% not $.saveFS %>
```

///


#### Revert

Copy a checkpoint **from the file service** back to the device, then feed that path into your existing revert tasks.

**Step**

1. **Transfer** from file service to NE with **`lso_transferFilesToNe`**, for example:
    - `neId`: `<% $.neId %>`
    - `sourcePath`: `"<% $.pathFS %>/nsp_checkpoint.<% $.fileExt %>"` (adjust if your rename step used another basename; `fileExt` is `json` vs `cfg` for SR Linux vs SR OS as appropriate)
    - `destinationPath`: `/tmp/` (or another agreed path on the box)
    - `ftUuid`: e.g. `<% $.neId+"-nsp_"+$.timestamp %>` (must stay unique per transfer)

/// details | Expanded hint
    type: success

Updated definition:

```yaml
    
    transferCheckpoint:
      action: lso_transferFilesToNe
      input:
        neId: <% $.neId %>
        sourcePath: "<% $.pathFS %>/nsp_checkpoint.<% $.fileExt %>"
        destinationPath: "/tmp/"
        ftUuid: <% $.neId+"-nsp_"+$.timestamp %>
      publish:
        lsoInfo: "Checkpoint file transferred to NE successfully"
        loadFile: "/tmp/nsp_checkpoint.<% $.fileExt %>"
      publish-on-error:
        lsoInfo: "Failed to transfer checkpoint file to NE"
      on-success:
        - revertFromFileSRL
      on-error:
        - RevertFailed

```

You can optionally update the  `createSRLcheckpoint` task to remove the file from the device, if needed:

```yaml

      - <% switch($.fromFS = true => "command to remove nsp_checkpoint file", $.fromFS = false => "do nothing") %>

```

///

## Summary

Congratulations! You have completed this activity. Take a moment to review what you achieved:

- Experienced Device Management Operations to manage checkpoints for Nokia devices.
- Learned how to navigate and view the created configuration checkpoints using File Service.
- Understand what artifacts are and install an artifact bundle in NSP.
- Extended the artifact bundle provided to support SR OS.
- Extended the artifact bundle provided to support file service integration.
- Explored the relationship of Device Operations, Workflows, Artifact Bundles and File Service.
- Looked in WFM design best-practices.
