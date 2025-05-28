---
tags:
  - NSP
  - Workflow Manager
---

# Inventory Report using Workflow Manager

|     |     |
| --- | --- |
| **Activity name** | Inventory Report using Workflow |
| **Activity ID** | 70 |
| **Short Description** | Collect detailed information about transceivers (SFPs, ...) installed |
| **Difficulty** | Beginner |
| **Tools used** |  |
| **Topology Nodes** | all SR OS and SRLinux nodes |
| **References** |  |

## Objective

Retrieve detailed transceiver attributes (like vendor, type, wavelength) for all installed pluggable optics (like SFPs) in
the network using a workflow and visualize the data as an HTML report.

This workflow demonstrates integration of:

* RESTCONF API to query NE hardware
* Data filtering and extraction using Jinja-style selectors
* Result rendering as an HTML table

## Technology Explanation

Nokia NSP supports collecting detailed hardware inventory using RESTCONF.
The `transceiver-details` subtree under each port in the hardware-component model exposes the SFP-specific information.

/// tab |  RESTCONF resource for transceiver information
```
/network/network-element[ne-id=*]/hardware-component/port[component-id=*]/transceiver-details
```
///
/// tab |  YANG Path Reference

From the transceiver-details subtree, the following fields are retrieved:

- `connector-code` *(string)*
- `vendor-o-u-i` *(string)*
- `laser-wave-length` *(decimal64)*
- `optical-compliance` *(string)*
- `specific-type` *(string)*
- `number-of-lanes` *(int64)*
- `connector-type` *(string)*
- `link-length-support` *(string)*
///

## Tasks

/// warning
Remind, that you are using a single NSP system (shared), that is used for all groups. Therefore, ensure
your group-number is part of the workflow name you are creating to ensure uniqueness.
///

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Explore NSP Physical Inventory

Nokia NSP supports collecting detailed hardware inventory via its RESTCONF gateway.
The `transceiver-details` subtree under each port in the hardware-component model exposes the SFP-specific information.

A good resource to get started is the API/model documentation available on Developer Portal.
Check information resources available about physical inventory.
Query NSP using curl, POSTMAN or WFM WebUI to explore inventory data available.

/// note | Resource URI to query transceiver details
```
/network/network-element[ne-id=*]/hardware-component/port[component-id=*]/transceiver-details
```
///

To query the inventory use the resource URI provided above. You can either run a simple `GET` or using
the more advaced `nsp-inventory:find`. Either way, the response will contain the list of optical modules
including key parameters such as:

- Connector code and type
- Laser wavelength and tunability
- Optical compliance
- Vendor OUI
- Position in the chassis

Once received, the data can be reformatted into a table (using markdown or html). This transformation
could be done using java-script, python or jinja2. To extract the data, YAQL expressions need to be
used.
 
### Create a basic workflow to retrieve transceiver data

Implementation is rather straight forward. Using `nsp.https` you don't need to provide any access credentials.
Please ensure to use an unique workflow name to avoid conflicts with other hackathon participants.

/// details | Solution (if getting stuck)
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

Execute your workflow and check execution results. Instead of using RESTCONF GET, you could also use `nsp-inventory:find`.

### Extend you workflow to produce a dynamic HTML table

Again, there are multiple ways to get here. You may decide to use JavaScript, Python or Jinja2.
There is no wrong or right, while it all may depend on your own preferences.

/// details | Solution (if getting stuck)
```yaml
version: '2.0'

NspSfpInventoryGroupXX:
  type: direct

  output:
    result: <% $.html %>

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
      on-complete:
        - renderTable

    renderTable:
      action: std.js
      input:
        context: <% $.testdata %>
        script: |
          var row = $[4];
          var header = $;
          var report = "<!DOCTYPE html><html><style>table {font-family: NokiaPure, sans-serif;border-collapse: collapse;} th, td {border: 1px solid #dddddd;text-align: left;padding: 8px;} </style><body>";

          report += "<table><tr><th>" + header[0] + "</th></tr>";
          report += "<tr><td>" + header[1] + "</td></tr>";
          report += "<tr><td>" + header[2] + "</td></tr>";
          report += "<tr><td>" + header[3] + "</td></tr></table><p>";
          
          report=report+"<table><tr><th><b>Connector</b><th><b>O-U-I</b><th><b>Wavelength</b><th><b>Compliance</b><th><b>Type</b><th><b>Lanes</b><th><b>Connector Type</b><th><b>Link Length Support</b><th><b>SFP Position</b></th></tr>" 

          for (var i = 0; i < row.length; i++) {
            if (row[i][0] != null) {
              report += "<tr><td>" + row[i][0] + "<td>" + row[i][1] + "<td>" + row[i][2] + "<td>" + row[i][3];
              report += "<td>" + row[i][4] + "<td>" + row[i][5] + "<td>" + row[i][6] + "<td>" + row[i][7];
              let text = row[i][8]["nsp-model:identifier"];
              let pattern = /\[(.*?)\]/g;
              let result = text.match(pattern);
              report += "<td>" + result + "</td></tr>";
            }
          }

          report += "</table></body></html>";
          return report;
      publish:
        html: <% task().result %>
```
///

**Sample Output:**

| Connector | O-U-I   | Wavelength | Compliance | Type   | Lanes | Connector Type | Link Length Support | SFP Position |
|-------|---------|------------|------------|--------|-------|-----------------|--------|-----------------------------|
| LC    | 00:25:90| 1310 nm    | LR4        | QSFP28 | 4     | Duplex          | 10 km  | [ne-id=SR01][port=1/1/1]    |


### Now it's your turn

Since we've provided a complete solution for the initial workflows, now we want to test your understanding.
There is also an opportunity here to make some reasonable changes...

**Q: What are the caveats of the solution workflow provided?**

/// details | Solution
    type: success

The initial task `getInfo` publishes a complex data structure. This could be simplified.
Using JavaScript to render HTML output is not straightforward and difficult to test.
Using Jinja2 (or python) makes things easier.
Instead of rendering HTML, Markdown could be considered.

What happens, if the network has millions of physical ports?
Would the solution still work? Could we use pagination to make it scale? How?
///
  
**Possible modifications:**

* Add error handling and timeout logic
* Refactor the workflow to simplify YAQL and use Jinja2 instead of JavaScript
* Filter results by NE-ID provided by operator (w/ schema-form input)
* Export output to CSV, JSON  or PDF
* Store files (CSV, JSON, PDF, MD, or PDF) on file-service