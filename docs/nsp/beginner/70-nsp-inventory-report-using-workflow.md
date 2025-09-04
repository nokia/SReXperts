---
tags:
- NSP
- RESTCONF
- Workflow Manager
---

# Inventory Reports

|     |     |
| --- | --- |
| **Activity name** | Inventory Report |
| **Activity ID** | 70 |
| **Short Description** | Collect detailed information about installed transceivers |
| **Difficulty** | Beginner |
| **Tools used** | NSP, Workflow Manager |
| **Topology Nodes** | all SR OS and SR Linux nodes |
| **References** | [NSP Developer Portal](https://developer.nokia.com/nsp) (free account required) |

## Objective

In daily operations, it is difficult to get a clear, up-to-date view of physical equipment installed across the network. Information is scattered across devices, time-consuming to retrieve, and hard to track over longer periods. This can slow down lifecycle management tasks such as identifying parts running out of maintenance or support. Furthermore, it impacts investigation of issues like optical signal degradation, when you need to correlate network insights with the inventory of optical transceivers.

In this activity, you will build an NSP workflow that automatically generates an operator-friendly HTML report of all installed transceivers (e.g. SFPs) in the network. The report makes transceiver information easy to retrieve, store, and review, giving you a reliable basis for both routine lifecycle tasks and problem investigations.

## Technology Explanation

The following technologies work together to create a practical framework for automating the collection, transformation, and presentation of network inventory data. The process starts with retrieving raw device information and ends with sharing results in user-friendly or machine-readable formats.

### RESTCONF API

The **RESTCONF API** provides access to network inventory. It allows secure retrieval of physical and logical details from network elements, such as installed optical transceivers. In this activity, calls are made through `nsp.https`, which handles authentication and encryption, so you don’t have to manage credentials manually.

### Workflows

At the core of the automation is the **workflow engine**, which defines the sequence of tasks:

1. Collecting inventory data.
2. Applying filters and transformations.
3. Formatting the results.
4. Delivering the output to the user or an external system.

Workflows are written in [Mistral DSL](https://docs.openstack.org/mistral/ocata/dsl/dsl_v2.html), a YAML-based domain-specific language. YAML is easy to read and write, making workflows approachable even for beginners.

#### Supporting Technologies for Workflow Authors

To enrich workflow logic and presentation, several technologies can be combined:

* **YAQL (Yet Another Query Language):** Used to filter, extract, and restructure data. For example, you might select only transceivers above a certain speed and reshape the results into a compact summary.
* **Jinja2:** A templating language for generating text dynamically. It’s often used to turn processed data into user-friendly reports.
* **Python / JavaScript:** For more advanced tasks, workflows can include snippets of Python or JavaScript to implement custom logic or handle data beyond what YAQL or Jinja2 can easily cover.

### Output and Delivery Techniques

Once the data is processed, workflows offer multiple ways to present or distribute the results:

* **Direct HTML Output:** A workflow can generate an HTML report and return it directly to the user, making results instantly viewable in a browser.
* **Machine-Readable Formats:** Data can also be returned as JSON, YAML, XML, or CSV, which makes it easier to feed into other tools.
* **PDF Conversion:** For archival or distribution, reports can be exported as PDF files.
* **File Service:** Instead of showing results immediately, workflows can dump outputs into files stored on the file-service for later retrieval.
* **Email Delivery:** Results can be sent as email attachments or inline reports, making it simple to distribute findings to a broader audience.

### Putting It All Together

Think of this framework as a **recipe**:

* The **RESTCONF API** is your ingredient supplier (raw inventory data).
* The **workflow** is the cooking process (steps in order).
* **YAQL** acts as your knife and strainer (selecting and reshaping the data).
* **Jinja2, Python, and JavaScript** are your seasoning and plating tools (making the output useful and appealing).
* The **output and delivery techniques** are the serving options—whether you hand someone a plated meal (HTML report), a recipe card (JSON/YAML), or a packaged lunchbox (PDF or email).

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

/// warning
Remember that you are using a shared NSP system. Ensure your group number is part of the workflow name to guarantee uniqueness.
///


You will build a workflow-based solution using the following core NSP capabilities and supporting technologies that work together to query, process, and present hardware inventory data in a consumable format.

### Retrieve NSP hardware inventory via RESTCONF API

Check the [NSP API documentation](https://network.developer.nokia.com/api-documentation) on the *Developer Portal*. As you are about to report the inventory of optical transceivers, search for *Physical Inventory*. In the corresponding Postman collection, you will find the required information under *Network Infrastructure Management* and then *Network Inventory* (Restconf API).

To query NSP, you may have the choice between using either the a basic GET request (part of the RESTCONF standard) or the advanced `nsp-inventory:find` operation (using POST). More information about how to query information from NSP can be found under [Learn NSP](https://network.developer.nokia.com/learn/25_4/network-functions/network-inventory/get_find_apis) on the Developer Portal.

/// admonition | What's the XPATH (RESTCONF/YANG) to retrieve optical transceiver information?
    type: question
/// details | Answer
    type: success
The following xpath could be used to query transceiver information:

```
/nsp-equipment:network/network-element/hardware-component/port/transceiver-details
```

Both `network-element` and `port` are both lists. The key for `network-element` is the `ne-id` and the key for `port` is the `component-id`.
///
///

NSP API calls require authentication. API users must first generate an auth-token, which is then provided as a Bearer Token for all subsequent API requests. Note that tokens have a limited lifetime (default: 1 hour). To prevent token expiration, you can either refresh the token or request a new one if the previous token has expired. It is also recommended to revoke the token once it is no longer needed. Examples of token management are available in the corresponding Postman collections.

Details about authentication and access-control can be found [here](https://network.developer.nokia.com/learn/25_4/common-functions/access-authentication-apis).

* Use NSP action-execution (preferred), Postman, or `curl` to query transceiver data from NSP.

/// details | Example Solution
    type: success
/// tab | Solution using HTTP GET:

**REQUEST:**

```yaml
url: https://restconf-gateway/restconf/data/nsp-equipment:network/network-element/hardware-component/port/transceiver-details
method: GET
```

**RESPONSE:**

```yaml
result:
  url: >-
    https://restconf-gateway/restconf/data/nsp-equipment:network/network-element/hardware-component/port/transceiver-details
  content:
    nsp-equipment:transceiver-details:
      - '@':
          nsp-model:schema-nodeid: >-
            /nsp-equipment:network/network-element/hardware-component/port/transceiver-details
          nsp-model:identifier: >-
            /nsp-equipment:network/network-element[ne-id='fd00:fde8::2:11']/hardware-component/port[component-id='shelf=1/cardSlot=1/card=1/mdaSlot=1/mda=1/port=1/1/c6/breakout-port=1/1/c6/1']/transceiver-details
          nsp-model:creation-time: '2025-08-18T19:05:31.479Z'
          nsp-model:last-modified-time: '2025-08-21T08:24:40.428Z'
          nsp-model:sources:
            - >-
              fdn:app:mdm-ami-cmodel:fd00:fde8::2:11:equipment:TransceiverDetails:/port[port-id='1/1/c6/1']
            - >-
              fdn:yang:nsp-network:/nsp-network:network/node[node-id='fd00:fde8::2:11']/node-root/nokia-state:state/port[port-id='1/1/c6/1']
            - >-
              fdn:yang:nsp-network:/nsp-network:network/node[node-id='fd00:fde8::2:11']/node-root/nokia-conf:configure/port[port-id='1/1/c6/1']
        connector-code: null
        vendor-o-u-i: null
        diagnostic-capable: false
        laser-wave-length: null
        optical-compliance: null
        specific-type: ''
        media: N/A
        number-of-lanes: null
        connector-type: null
        link-length-support: null
        laser-tunability: Unequipped
      - '@':
          nsp-model:schema-nodeid: >-
            /nsp-equipment:network/network-element/hardware-component/port/transceiver-details
          nsp-model:identifier: >-
            /nsp-equipment:network/network-element[ne-id='fd00:fde8::2:11']/hardware-component/port[component-id='shelf=1/cardSlot=1/card=1/mdaSlot=1/mda=1/port=1/1/c1/breakout-port=1/1/c1/1']/transceiver-details
          nsp-model:creation-time: '2025-08-18T19:05:31.846Z'
          nsp-model:last-modified-time: '2025-08-21T08:24:40.428Z'
          nsp-model:sources:
            - >-
              fdn:yang:nsp-network:/nsp-network:network/node[node-id='fd00:fde8::2:11']/node-root/nokia-conf:configure/port[port-id='1/1/c1/1']
            - >-
              fdn:yang:nsp-network:/nsp-network:network/node[node-id='fd00:fde8::2:11']/node-root/nokia-state:state/port[port-id='1/1/c1/1']
            - >-
              fdn:app:mdm-ami-cmodel:fd00:fde8::2:11:equipment:TransceiverDetails:/port[port-id='1/1/c1/1']
        connector-code: null
        vendor-o-u-i: null
        diagnostic-capable: false
        laser-wave-length: null
        optical-compliance: null
        specific-type: ''
        media: N/A
        number-of-lanes: null
        connector-type: null
        link-length-support: null
        laser-tunability: Unequipped
```

///
/// tab | Solution using `nsp-inventory:find` (POST):

**REQUEST:**

```yaml
url: https://restconf-gateway/restconf/operations/nsp-inventory:find
method: POST
body:
  input:
    xpath-filter: /nsp-equipment:network/network-element/hardware-component/port/transceiver-details
    include-meta: false
```

**RESPONSE:**

```yaml
result:
  url: https://restconf-gateway/restconf/operations/nsp-inventory:find
  content:
    nsp-inventory:output:
      data:
        - connector-code: null
          vendor-o-u-i: null
          diagnostic-capable: false
          laser-wave-length: null
          optical-compliance: null
          specific-type: ''
          media: N/A
          number-of-lanes: null
          connector-type: null
          link-length-support: null
          laser-tunability: Unequipped
        - connector-code: null
          vendor-o-u-i: null
          diagnostic-capable: false
          laser-wave-length: null
          optical-compliance: null
          specific-type: ''
          media: N/A
          number-of-lanes: null
          connector-type: null
          link-length-support: null
          laser-tunability: Unequipped
        - connector-code: lc
          vendor-o-u-i: 00:00:5f
          diagnostic-capable: true
          laser-wave-length: 1302
          optical-compliance: 100GBASE-LR4
          specific-type: cfp2-or-qsfp28
          media: ethernet
          number-of-lanes: 4
          connector-type: qsfp
          link-length-support: 10km for SMF
          laser-tunability: Unequipped
```

///
/// tab | Alternative solution using `nsp-inventory:find` (POST)

**REQUEST:**

```
url: https://restconf-gateway/restconf/operations/nsp-inventory:find
method: POST
body:
  input:
    xpath-filter: /nsp-equipment:network/network-element/hardware-component/port[admin-state='unlocked']
    include-meta: false
    fields: ne-id;name;description;oper-state;transceiver-details(vendor-o-u-i;diagnostic-capable;laser-wave-length;optical-compliance;media)
resultFilter: $.content.get('nsp-inventory:output').data
```

**RESPONSE:**

```
result:
  url: https://restconf-gateway/restconf/operations/nsp-inventory:find
  content:
    - name: ethernet-1/1
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:52
    - name: ethernet-1/1
      oper-state: enabled
      description: spine12-leaf1
      ne-id: fd00:fde8::2:32
    - name: ethernet-1/2
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:52
    - name: ethernet-1/1
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:51
    - name: ethernet-1/3
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:52
    - name: ethernet-1/2
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:51
    - name: ethernet-1/1
      oper-state: enabled
      description: peering2-transit1
      ne-id: fd00:fde8::2:53
    - name: ethernet-1/2
      oper-state: enabled
      description: peering2-ixp1
      ne-id: fd00:fde8::2:53
    - name: ethernet-1/3
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:51
    - name: ethernet-1/2
      oper-state: disabled
      description: leaf12-client12
      ne-id: fd00:fde8::2:35
    - name: ethernet-1/3
      oper-state: enabled
      description: leaf13-client13
      ne-id: fd00:fde8::2:35
    - name: ethernet-1/2
      oper-state: enabled
      description: spine12-leaf2
      ne-id: fd00:fde8::2:32
    - name: ethernet-1/3
      oper-state: enabled
      description: spine12-leaf3
      ne-id: fd00:fde8::2:32
    - name: ethernet-1/31
      oper-state: enabled
      description: spine11-pe3
      ne-id: fd00:fde8::2:32
    - name: ethernet-1/32
      oper-state: enabled
      description: spine11-pe2
      ne-id: fd00:fde8::2:32
    - name: ethernet-1/50
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:52
    - name: ethernet-1/49
      oper-state: enabled
      description: leaf3-spine11
      ne-id: fd00:fde8::2:35
    - name: ethernet-1/50
      oper-state: enabled
      description: leaf3-spine12
      ne-id: fd00:fde8::2:35
    - name: ethernet-1/1
      oper-state: enabled
      description: spine11-leaf1
      ne-id: fd00:fde8::2:31
    - name: ethernet-1/2
      oper-state: enabled
      description: spine11-leaf2
      ne-id: fd00:fde8::2:31
    - name: ethernet-1/3
      oper-state: enabled
      description: spine11-leaf3
      ne-id: fd00:fde8::2:31
    - name: ethernet-1/31
      oper-state: enabled
      description: spine11-pe3
      ne-id: fd00:fde8::2:31
    - name: ethernet-1/32
      oper-state: enabled
      description: spine11-pe2
      ne-id: fd00:fde8::2:31
    - name: ethernet-1/1
      oper-state: enabled
      description: leaf21-client21
      ne-id: fd00:fde8::2:41
    - name: ethernet-1/49
      oper-state: enabled
      description: leaf1-pe1
      ne-id: fd00:fde8::2:41
    - name: ethernet-1/50
      oper-state: enabled
      description: leaf1-pe4
      ne-id: fd00:fde8::2:41
    - name: ethernet-1/1
      oper-state: enabled
      description: leaf11-client11
      ne-id: fd00:fde8::2:33
    - name: ethernet-1/2
      oper-state: disabled
      description: leaf12-client12
      ne-id: fd00:fde8::2:33
    - name: ethernet-1/49
      oper-state: enabled
      description: leaf11-spine11
      ne-id: fd00:fde8::2:33
    - name: ethernet-1/50
      oper-state: enabled
      description: leaf11-spine12
      ne-id: fd00:fde8::2:33
    - name: ethernet-1/2
      oper-state: disabled
      description: leaf12-client12
      ne-id: fd00:fde8::2:34
    - name: ethernet-1/49
      oper-state: enabled
      description: leaf12-spine11
      ne-id: fd00:fde8::2:34
    - name: ethernet-1/50
      oper-state: enabled
      description: leaf12-spine12
      ne-id: fd00:fde8::2:34
    - name: 1/1/c1
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:11
      transceiver-details:
        - vendor-o-u-i: 00:00:5f
          diagnostic-capable: true
          laser-wave-length: 1302
          optical-compliance: 100GBASE-LR4
          media: ethernet
    - name: 1/1/c2
      oper-state: enabled
      description: null
      ne-id: fd00:fde8::2:11
      transceiver-details:
        - vendor-o-u-i: 00:00:5f
          diagnostic-capable: true
          laser-wave-length: 1302
          optical-compliance: 100GBASE-LR4
          media: ethernet
```
///
///

* Inspect the JSON output to understand the data structure! You should see the following fields in the output: `connector-code`, `vendor-o-u-i`, `laser-wave-length`, `optical-compliance`, `specific-type`, `number-of-lanes`, `connector-type`, and `link-length-support`.

/// tip
Based on the queries and responses above, you may notice a key challenge when working with nested tables or tables containing child containers: if the meta information is excluded, the response will only return the requested data as a list, with no way to link it back to a specific device or port. Since those keys are not repeated at child level, it is better to keep the meta information included - even though this adds significant overhead to the responses.

The alternative solution example from above gives some direction for a reasonable compromise. It queries the ports including transceiver information, while using filters to reduce the output for what is considered important. By this, we remove the dependency on model meta, while providing native access to fields like `ne-id` and port `name`. You may want to spend some time to tweak the `xpath-filter` and `resultFilter` (YAQL expression) to simplify the processing of the data generated.

///

### Create a Basic Workflow to Retrieve Transceiver Data

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
    
  output:
    result: "success"

  tasks:
    task1:
      action: std.noop
...
```

Adjust workflow name, description, inputs and tasks as needed. You may start without any input. The workflow itself, could be a single task that is running action `nsp.https` with the corresponding inputs, e.g. `method`, `url`, and `body`.

The workflow action execution from before is a great way to write this new workflow. If you use the `COPY` button in the `Run Action Execution` form, the system will generate a fully populated task definition into your clipboard that you can simply paste into a new workflow.

YAQL is a great way to transform objects and extract information in workflows. More information about YAQL can be found [here](https://yaql.readthedocs.io/). In this case, you can keep it simple the task result can be accessed by `<% task().result %>`.

Don't forget to use a unique name for your workflows, e.g. by adding your group number!

/// details | Solution
    type: success
```yaml
version: '2.0'
InventoryReportGroupXX:
  type: direct
  output:
    result: <% $.response %>
  tasks:
    getInfo:
      action: nsp.https
      input:
        url: https://restconf-gateway/restconf/data/nsp-equipment:network/network-element/hardware-component/port/transceiver-details
        method: GET
      publish:
        response: <% task().result %>
```
///

### Enhance Output into a Human-Centric Format

NSP workflows allow transforming structured data into readable formats.
Let’s render HTML. You can use Javascript, Python, or Jinja2.

If you consider using JavaScript, you will find the corresponding information from OpenStack Mistral documentation [here](https://docs.openstack.org/mistral/ocata/dsl/dsl_v2.html#std-javascript).

[Jinja Templating Language](https://jinja.palletsprojects.com/en/stable/templates) is another great way to render HTML from user data. The [usage of Jinja Template](https://network.developer.nokia.com/learn/25_4/programming/workflows/wfm-workflow-development/wfm-Advanced-Concepts#Advanced_concepts_Jinja_Templates) is discussed on the Developer Portal.

To render the HTML you need to add another task to the workflow. Use `on-success`, `on-error`, or `on-complete` to transition from one task to another. While you may have the option to make task transitions conditional, in the case of reporting this might not be necessary.

Use `publish` (and `publish-on-error`) to publish a dictionary of variables to the workflow context, so it can be used by follow-up actions using simple YAQL expressions (or Jinja) like this `<% $.variable_name %>`.

/// details | Possible Solution
    type: success

```yaml
version: '2.0'
NspSfpInventoryGroupXX:
  type: direct
  output:
    result: <!DOCTYPE html><% $.html %>
  tasks:
    getInfo:
      action: nsp.https
      input:
        url: https://restconf-gateway/restconf/data/nsp-equipment:network/network-element/hardware-component/port/transceiver-details
        method: GET
      publish:
        testdata:
          - "Create a Transceiver Inventory list with all equipped SFPs using a RESTCONF API call"
          - "url= <% task().result.url %>"
          - "status= <% task().result.status %>"
          - "elapsed= <% task().result.elapsed %> s"
          - <% task().result.content["nsp-equipment:transceiver-details"]
               .select([$.get("connector-code"),
                        $.get("vendor-o-u-i"),
                        $.get("laser-wave-length"),
                        $.get("optical-compliance"),
                        $.get("specific-type"),
                        $.get("number-of-lanes"),
                        $.get("connector-type"),
                        $.get("link-length-support"),
                        $.get("@")])
               .orderBy($[1]) %>
      on-success:
        - renderTable

    renderTable:
      action: std.js
      input:
        context: <% $.testdata %>
        script: |
          var row = $[4];
          var report = "<html><style>table {font-family: sans-serif;border-collapse: collapse;} th, td {border: 1px solid #ddd;text-align: left;padding: 8px;}</style><body>";
          report += "<table><tr><th>Connector</th><th>OUI</th><th>Wavelength</th><th>Compliance</th><th>Type</th><th>Lanes</th><th>Connector Type</th><th>Link Length</th><th>Position</th></tr>";
          for (var i = 0; i < row.length; i++) {
            let text = row[i][8]["nsp-model:identifier"] || "";
            let pos = (text.match(/\[(.*?)\]/g) || []).join(" ");
            report += `<tr><td>${row[i][0]}</td><td>${row[i][1]}</td><td>${row[i][2]}</td><td>${row[i][3]}</td><td>${row[i][4]}</td><td>${row[i][5]}</td><td>${row[i][6]}</td><td>${row[i][7]}</td><td>${pos}</td></tr>`;
          }
          report += "</table></body></html>";
          return report;
      publish:
        html: <% task().result %>
```
///

### Bonus: Extend Your Solution (Optional)

Make your solution **robust and scalable**.

#### Add Workflow Input

Let users filter by NE-ID

/// details | Hint
Add a workflow input attribute `neId` and adjust the resource URL being queried accordingly. Consider auto-generating an input-form, to simplify the node selection by the user. As long you use the attribute name *neId*, the auto-generator will provide you with a pre-defined device picker component.

Input section may look like this:
```yaml
  input:
    - neId
```

URL to become:
```yaml
  url: https://restconf-gateway/restconf/data/nsp-equipment:network/network-element=<% $.neId %>/hardware-component/port/transceiver-details
```

You may consider keeping the `neId` input attribute optional. If not provided, the workflow would still return all transceivers of the entire network.
///

#### Add Scheduling

Run the report every hour/day

#### Export

Allow saving as CSV / JSON / Markdown

/// details | Hint
Workflows can write data onto the [NSP file-server](https://network.developer.nokia.com/learn/25_4/nsp-administration/nsp-file-server). Check for API operation `uploadTextToFile` in the corresponding Postman collection (Developer Portal).
///

#### Scalability Note

/// admonition | Do you see any issues with the current workflow if run at scale?
    type: question
/// details | Answer
    type: success
The current implementation retrieves all data at once.

On large networks this could:
- Slow down execution
- Hit RESTCONF API size limits
- Overload WebUI render Consider pagination or filtering per NE.

If network size grows (1000s of ports), consider pagination or limiting results.
Use `nsp-inventory:find` with filtering to build a more scalable and performant solution.
///
///


## Summary

 Congratulations! You have completed this activity. Take this opportunity to look back on some of the things you have achieved:

- Explored NSP RESTCONF API
- Created a working workflow to collect SFP data
- Formatted output as an HTML report
- Learned YAQL and workflow design concepts

---

## Next Steps

Here are some suggestions on how to continue:

* Let the user provide the `ne-name` to make the solution more operator-friendly
* Update the workflow to accept a list of nodes as input, rather a single device only
* Use Jinja2 (or Python) instead of JS to render the HTML output
* Explore action `nsp.generatePDF` for generating PDF reports
* Creating similar workflows for **cards** and **ports** reporting
