# NE Security Scan using NSP

| Item | Details |
| --- | --- |
| Short Description | Assuring Management/Control Plane Security using Workflows and Operations |
| Skill Level | Advanced |
| Tools Used | NSP WFM/LSO with nmap |

## Prerequisites
1. Basic knowledge the NSP UI
2. Familiarity with NSP Workflow Manager
3. Familiarity with NSP Operations Manager

For improved DevOps experience, consider using the WFM vsCode extension from [marketplace](https://marketplace.visualstudio.com/items?itemName=Nokia.nokia-wfm).

## Objective

The purpose of this activity is to run a security scan against network elements to find open TCP ports.
For achieve this, you will use NSP Workflow Manager and NSP Operation Manager.

We will provide this operation as an unsigned bundle that the developer can import and install via Artifact management.

The default operation will include the mapping profile, yang model and operation types (meta).

The goal is for the developer to be able to download, import and enhance the functionality of the provided operation / workflow.

### Goals to achieve

Basic NSP functionalities:
* Familiarized with Artifact management in NSP, by importing the bundle (zip) in NSP and monitoring the install process.
* Familiarized with Operations Manager, by creating an operation execution for few targets, to understand the framework and the capabilities provided by default within the new scan operation.

Extend the operation capabilities by updating the workflow:
* Make the port list configurable as through workflow environments.
* Extend the current support to fail the workflow for targets that have specific ports open.
* On top of the previous, automatically create a new alarm in FM app including the list of undesired ports open for a given target.

Note that the provided operation is unsigned, allowing the user to directly modify the workflow without the need to recreating and reinstalling the bundle (convenient for prototyping).

## Access to the Lab
Access details to NSP will be provided in the hackathon. There is no requirement to access the NEs directly.

## Steps

#### Discovery of the lab

If this is your first NSP activity for this hackathon, ensure to first execute the activity called `nsp-b-lab-discovery`. It should not take long!

#### To download, customize and install bundle:
1. Clone this repo to your local system.
2. Adjust the artifact-bundle content in [nsp-scan-artifact-bundle](./nsp-scan-artifact-bundle) for your group and build the artifact bundle.

Content of the folder is:
```
% cd nsp-scan-artifact-bundle
% tree
.
├── content
├── metadata.json
├── nsp-scan-operation
│   ├── nsp-scan-groupxx.yaml
│   ├── nsp-scan-groupxx.yang
│   └── operation_types.json
└── nsp-scan-workflow
    └── nsp-scan-groupxx.yaml
```

Under the assumption your are in group 33, do the following:
- rename `nsp-scan-operation/nsp-scan-groupxx.yaml` to `nsp-scan-operation/nsp-scan-group33.yaml`
- rename `nsp-scan-operation/nsp-scan-groupxx.yang` to `nsp-scan-operation/nsp-scan-group33.yang`
- rename `nsp-scan-workflow/nsp-scan-groupxx.yaml`  to `nsp-scan-workflow/nsp-scan-group33.yaml`
- replace `groupxx` with `group33` in file `metadata.json` (5 occurences)
- replace `groupxx` with `group33` in file `nsp-scan-operation/nsp-scan-groupxx.yaml` (1 occurence)
- replace `groupxx` with `group33` in file `nsp-scan-operation/nsp-scan-groupxx.yang` (4 occurences)
- replace `groupxx` with `group33` in file `nsp-scan-operation/operation_types.json` (3 occurences)
- replace `groupxx` with `group33` in file `nsp-scan-workflow/nsp-scan-groupxx.yaml` (2 occurences)
- create a zip archive with the content of folder `nsp-scan-artifact-bundle` names `nsp-scan-group33.zip`

Depending on your local operating system, you may take advantage of command line tools.
Here an example on how to do it on MacOS or Linux:

```
export instance=group33
cp -r nsp-scan-artifact-bundle /tmp
cd /tmp/nsp-scan-artifact-bundle
find . -name '*groupxx*' -exec bash -c 'mv "$0" "${0//groupxx/$instance}"' {} \;
find . -type f -exec sed -i '' s/groupxx/$instance/g {} \;
zip -r /tmp/nsp-scan-$instance.zip *
```

3. Login to NSP. Access details will be provided during the hackathon.
4. In NSP, open the hamburger menu and select "Artifacts".
5. Select "Import and Install", find the zip file and install automatically the bundle. When marked as "Installed", you can continue to the next step.

#### To test the operation
1. In NSP, select "Device Management" in the hamburguer menu.
2. In the dropdown menu, select "All Operations".
3. You can create a new operation of type _nsp-scan-groupxx_, selecting the targets (NEs).
4. After the creation the user can check the operation status and see the open ports from the predefined list of ports scanned.

#### To edit the operation (exercise)
You can directly edit the workflow, called _nsp-scan-groupxx, in Workflow Manager ("Workflows" in hamburguer menu).

You can also refer to the Visual Studio Code plugin for WFM, if you wish to use an existing IDE for workflow development.

To achieve the recommended tasks described in the Objective section, the user need to understand:
* how to create and update environment, how to import them in the workflow and how to use them within. This requires using basic YAQL expressions.
* add new action to check the result of the scan and decide on the success/failure on the scan. As a recommendation, we encourage to use python for this checks. However, the user may decide to use Javascript for this matter, or complex YAQL expressions.
* create a new action of type _nsp.https_ to create an alarm in the fault management application.

## Useful Links & Cheatsheet

Useful links within developer portal (ask the Nokia support if you do not have access):
* [Manage environments](https://network.developer.nokia.com/learn/24_4/network-programmability-automation-frameworks/workflow-manager-framework/wfm-workflow-development/wfm-Advanced-Concepts/#Advanced_concepts_Environments)
* [WFM actions](https://network.developer.nokia.com/learn/24_4/network-programmability-automation-frameworks/workflow-manager-framework/wfm-workflow-development/wfm-workflow-actions/)

Examples/Cheatsheet of the contributions expected:

* Replace the ports in the shell action to incorporate the ones defined in the environments section
```yaql
<% env().ports %>
```
* Use the python action to verify the ports that should not be open. The example below does not show how to filter, it is only meant to show a python action and to explain how input attributes are passed to the python script:
```yaml
testPython:
  action: nsp.python
  input:
    context:
        port: <% $.port %>
    script: |
      import urllib.parse
      def myFunction(encode):
        output = urllib.parse.quote(encode)
        output = output.replace('/', '%2F')
        LOG.info("python action logging into executor logs")
        #LOG.info('context object=%s', context['var'])
        return output
      return myFunction(context["port"]);
```
* For publishing the alarm, follow the example below. This is simply an example with hardcoded values, which you can customize some of the entries to better show the details of the undesired port and extend based on the swagger documentation exposed above:
```yaml
    sendAlarm:
      action: nsp.https
      input:
        url: https://restconf-gateway/restconf/data/nsp-fault:alarms/alarm-list
        method: POST
        contentType: application/json
        body:
          nsp-fault:alarm:
          - resource: "fdn:app:mdm-ami-cmodel:10.33.0.1:equipment:NetworkElement"
            source-type: nsp
            source-system: fdn:app:external
            perceived-severity: major
            probable-cause-string: softwareError
            alarm-type-qualifier: UndesiredOpenPorts
            alarm-type-id: securityServiceOrMechanismViolationAlarm
            affected-object-type: equipment.NetworkElement
            affected-object-name: paris
            implicitly-cleared: false
            additional-text: List of undesired open ports
            ne-id: 10.33.0.1
            ne-name: paris
            alt-resource: "uniquetexttoidentifyalarm"
      publish:
        result: $.content.response
```
