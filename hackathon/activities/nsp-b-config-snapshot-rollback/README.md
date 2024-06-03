# NE snapshot/rollback using NSP

| Item | Details |
| --- | --- |
| Short Description | Take a configuration snapshot with NSP for later rollback |
| Skill Level | Beginner/Advanced |
| Tools Used | NSP WFM/LSO |

## Summary

The scope of this operation in Operations Manager is to run a backup and restore of Nokia SR OS running configuration and it can be easily extended to other chasis, it uses NSP MDC framework to backup and restore NE config.  

This operation provides user to select backup and restore of node config.

We will provide this operation as an unsigned bundle that the developer can import and install via Artifact management.

The default operation will include the mapping profile, yang model and operation types (meta).

## Goals to achieve

Basic NSP functionalities:
* Familiarized with Artifact management in NSP, by importing the bundle (zip) in NSP and monitoring the install process.
* Familiarized with Operations Manager, by creating an operation execution for few targets, to understand the framework and the capabilities provided by default within the new scan operation.
* All backup files will be stored in NSP file server with timestamp, user should be able to view these files.
Extend the operation capabilities:
* Add a new chaiss which is not supported bydefault, this requires reimport of the bundle.


Note that the provided operation is unsigned, allowing the user to directly modify the workflow without the need to recreating and reinstalling the bundle (convenient for prototyping).

## Steps

#### Discovery of the lab

If this is your first NSP activity for this hackathon, ensure to first execute the activity called `nsp-b-lab-discovery`. It should not take long!

#### To download, customize and install bundle:
1. Clone this repo to your local system.
2. Adjust the artifact-bundle content in [nsp-scan-artifact-bundle](./nsp-scan-artifact-bundle) for your group and build the artifact bundle.

Content of the folder is:
```
% cd cfg-snapshot-artifact-bundle
% tree
.
├── metadata.json
├── operation-rollback
│   ├── ne-rollback-groupxx.yaml
│   ├── ne-rollback-groupxx.yang
│   └── operation_types.json
├── operation-snapshot
│   ├── ne-snapshot-groupxx.yaml
│   ├── ne-snapshot-groupxx.yang
│   └── operation_types.json
├── workflow-rollback
│   ├── README.md
│   └── ne-rollback-groupxx.yaml
└── workflow-snapshot
    ├── README.md
    └── ne-snapshot-groupxx.yaml

4 directories, 11 files
```

Under the assumption your are in group 37, do the following:
- rename `operation-rollback/ne-rollback-groupxx.yaml` to `operation-rollback/ne-rollback-group37.yaml`
- rename `operation-rollback/ne-rollback-groupxx.yang` to `operation-rollback/ne-rollback-group37.yang`
- rename `operation-snapshot/ne-snapshot-groupxx.yaml` to `operation-snapshot/ne-snapshot-group37.yaml`
- rename `operation-snapshot/ne-snapshot-groupxx.yang` to `operation-snapshot/ne-snapshot-group37.yang`
- rename `workflow-rollback/ne-rollback-groupxx.yaml`  to `workflow-rollback/ne-rollback-group37.yaml`
- rename `workflow-snapshot/ne-snapshot-groupxx.yaml`  to `workflow-snapshot/ne-snapshot-group37.yaml`
- replace `groupxx` with `group37` in file `metadata.json` (10 occurences)
- replace `groupxx` with `group37` in file `operation-rollback/operation_types.json` (3 occurences)
- replace `groupxx` with `group37` in file `operation-rollback/ne-rollback-groupxx.yaml` (1 occurences)
- replace `groupxx` with `group37` in file `operation-rollback/ne-rollback-groupxx.yang` (5 occurences)
- replace `groupxx` with `group37` in file `operation-snapshot/operation_types.json` (3 occurences)
- replace `groupxx` with `group37` in file `operation-snapshot/ne-snapshot-groupxx.yaml` (1 occurences)
- replace `groupxx` with `group37` in file `operation-snapshot/ne-snapshot-groupxx.yang` (4 occurences)
- replace `groupxx` with `group37` in file `workflow-rollback/ne-rollback-groupxx.yaml` (2 occurences)
- replace `groupxx` with `group37` in file `workflow-snapshot/ne-snapshot-groupxx.yaml` (2 occurences)

Dependending on your local operating system, you may take advantage of command line tools.
Here an example on how to do it on MacOS X:

```
# cd nsp-scan-artifact-bundle
# mv operation-rollback/ne-rollback-groupxx.yaml operation-rollback/ne-rollback-group37.yaml
# mv operation-rollback/ne-rollback-groupxx.yang operation-rollback/ne-rollback-group37.yang
# mv operation-snapshot/ne-snapshot-groupxx.yaml operation-snapshot/ne-snapshot-group37.yaml
# mv operation-snapshot/ne-snapshot-groupxx.yang operation-snapshot/ne-snapshot-group37.yang
# mv workflow-rollback/ne-rollback-groupxx.yaml  workflow-rollback/ne-rollback-group37.yaml
# mv workflow-snapshot/ne-snapshot-groupxx.yaml  workflow-snapshot/ne-snapshot-group37.yaml
# sed -i '' s/groupxx/group37/g metadata.json */*
# zip -r cfg-snapshot-group37.zip *
```

3. Login to NSP. Access details will be provided during the hackathon.
4. In NSP, open the hamburger menu and select "Artifacts".
5. Select "Import and Install", find the zip file and install automatically the bundle. When marked as "Installed", you can continue to the next step.

#### To test the operation (level: beginner)
1. In NSP, select `Device Management` in the hamburguer menu.
2. In the dropdown menu, select `All Operations`
3. Select Operation Type `ne-snapshot-group37` (adjust to your group)
4. Provide operation name, for example `initial-cfg-snapshot-group37` (adjust to your group)
5. Select Target NEs to take backup (use: p1, p2, pe1, pe2, pe3, pe4)
6. After the creation the user can check the operation status, it should set to completed.
7. Snapshot content could be reviewed from `Device Management` and from `File Manager`

#### Taking it a step further (level: beginner)
1. Apply changes to a node using CLI or MDC and take another config snapshot! Do you see the changes?
2. Use the rollback operation to restore the initial configuration (without reboot)! Was the config restored?
3. Review the code examples provides for the operation-types and the workflows! What's required to make it a bundle?

#### Edit the operation (level: advanced)
You may now use either NSP WFM or Visual Studio Code (with WFM extension) to extend the operation/workflow.
The ask would be to extend the operation-types and workflows to support SR Linux.

The most notable difference would be, that SROS stores all configuration in a single root module (/nokia-conf:configure),
while SR Linux has uses multiple root-level modules. In addition, be aware that SR Linux is mixes configuration and 
corresponding read-only state attributes in the same subtree. As the ask is to capture the configuration only, the
query parameter `?content=config` must be added to the corresponding RESTCONF `GET` request.

As MDC does not support to fetch all module instance by accessing /root, and because we are not interested in OpenConfig models,
you may use the [SRL YANG Explorer](https://yang.srlinux.dev) or NSP MDC to find appropriate root paths. You may want to start
with the following subtrees:

```
  /restconf/data/network-device-mgr:network-devices/network-device=<% $.neId %>/root/srl_nokia-netinst:network-instance?content=config
  /restconf/data/network-device-mgr:network-devices/network-device=<% $.neId %>/root/srl_nokia-if:interface?content=config
  /restconf/data/network-device-mgr:network-devices/network-device=<% $.neId %>/root/srl_nokia-system:system?content=config
```

It's recommend to store the output of those queries in separate files. Review how the default NSP operations for SROS
are designed and consider storing all files in a ZIP archive.


Useful links within developer portal (ask the Nokia support if you do not have access):
* [Manage environments](https://network.developer.nokia.com/learn/24_4/network-programmability-automation-frameworks/workflow-manager-framework/wfm-workflow-development/wfm-Advanced-Concepts/#Advanced_concepts_Environments)
* [WFM actions](https://network.developer.nokia.com/learn/24_4/network-programmability-automation-frameworks/workflow-manager-framework/wfm-workflow-development/wfm-workflow-actions/)
* [Create alarm](https://network.developer.nokia.com/swagger/fm-24-4.html/#/alarms/createAlarmUsingPOST)
