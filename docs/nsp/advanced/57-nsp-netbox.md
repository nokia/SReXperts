---
tags:
  - NSP
  - NetBox
  - Python
---

# Integrating NSP w/ NetBox

|     |     |
| --- | --- |
| **Activity name** | Integrating NSP w/ NetBox |
| **Activity ID** | 57 |
| **Short Description** | Use NetBox for infrastructure management on top of NSP to create/update infrastructure intents. |
| **Difficulty** | Advanced |
| **Tools used** | [Postman](https://www.postman.com/downloads/), [Postman (portable)](https://portapps.io/app/postman-portable/) |
| **Topology Nodes** | :material-router: PE1, :material-router: PE2, :material-router: PE3, :material-router: PE4, :material-router: P1, :material-router: P2 |
| **References** | [Nokia  Developer Portal](https://network.developer.nokia.com) (Sign up for a free account)<br/>[NSP Postman collections](https://network.developer.nokia.com/static/private/downloads/postmanCollections/24_11_NSP_Postman_Collections.zip)<br/>[NetBox Shell Documentation](https://netboxlabs.com/docs/netbox/en/stable/administration/netbox-shell/) |

## Objective

Keeping your network inventory and your operational systems in sync is a recurring challenge. You may already maintain device and service records in a central source-of-truth such as NetBox, while your devices are managed and configured through NSP. Without integration, you risk having two versions of the truth: one in your inventory database and another in the live network.

In this activity, you'll create a custom NetBox script that translates NetBox's version of the network state into NSP intents and pushes them into the live network. This ensures that updates made in your inventory system directly drive configuration changes on the devices.

This approach helps you:

* Reduce manual re-entry of configuration data across systems
* Ensure that the inventory view always corresponds to actual device state
* Move toward event-driven operations, where network inventory changes automatically trigger configuration updates

This is the rough flow chart of the solution we're going to construct, the NetBox custom script is where most of the effort will be focused.

``` mermaid
flowchart LR
    nb(NetBox) --> |Event-Rule| sc(NetBox <br> Custom Script)
    sc -->|RESTCONF API| nsp(NSP)
    nsp --> |gNMI/NETCONF| net(Network)
    style sc fill:red
```

## Technology Explanation

### NSP Intents
Nokia Network Services Platform (NSP) is a comprehensive network management and automation platform that uses intent-based networking principles to simplify operations. Rather than requiring operators to specify low-level device configurations, NSP allows them to declare high-level business intents that describe desired network behaviors, automatically translating these intents into device configurations and policies while continuously monitoring compliance.

### NetBox DCIM
NetBox is a Source of Truth platform (SoT) for managing network infrastructure state. Its DCIM module documents network devices, racks, cables and interfaces. The platform models physical hardware through devices and network connectivity through `Interfaces`, tracking both physical connections and configurations enabling automation use-cases.

### NetBox IPAM
The IP Address Management (IPAM) module in NetBox provides tools for managing IP addresses, prefixes, VLANs, and VRFs. A key feature is the `IPAddress` model which represents individual IP addresses and their assignments. IPAddress objects can be directly associated with Interface objects from the DCIM module, creating a clear link between physical ports and their IP addressing. The IPAM module supports both IPv4 and IPv6 addressing, CIDR notation, and can enforce rules around address assignment and utilization. 


## Tasks

**You should read these tasks from top-to-bottom before beginning the activity.**

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Accessing NetBox
!!! note
    Login to the NetBox UI via the web interface:<br>

    **URL**: http://**GROUP_NUMBER**.srexperts.net:8000 <br>
    **Username**: admin <br>
    **Password**: same password as the instance SSH or SR OS and SR Linux nodes <br>

### Explore NetBox
We've already done some work to load the Hackathon topology into NetBox - this includes specifying `Manufacturers` and `Device Types`, creating `Racks`, installing `Devices` into racks, creating `Interfaces` and connecting devices to one another. 

#### Explore Core NetBox Components
   * Browse the **Devices** section to see all network equipment
   * Examine the **Racks** view to understand physical infrastructure layout, use the **Elevations** menu option to view a visual representation of the rack front/rear.
   * Click into individual devices to view their basic information, browse the **Interfaces** tab to list interfaces and inspect their basic parameters.

#### Run the IP Allocation Custom Script
You may notice that devices don't have IPs assigned to interfaces within NetBox. Because each Hackathon instance VM has unique IP space, we must dynamically add IP addresses to each NetBox instance. The next instructions will show you an example of how a custom script is run interactively and what they can do.

???+ note "Run NetBox IP Assignment Script"
    * Navigate to `Customization > Scripts > Create IP interfaces on core nodes`
    * In the `Instance id` field, put in your group number such as `10`. Be sure this is correct, your NSP intents won't work unless this is correct.
    * Click the `Run Script` button.
    * This should result in successful results:
    ![IP Assignment Script Results](./images/57-netbox/nb-ip-script-results.png)

### Explore the NSPs APIs 
- [Install Postman](https://www.postman.com/downloads/)
- Download the [NSP Postman collections](https://network.developer.nokia.com/api-documentation/) and import to Postman - we'll specifically need the `Network Functions` and `ICM` Collections.

#### Setup Postman Authentication
- Create an Environment
- Populate the variables using the NSP credentials provided to you, **don't** just copy what's here:
    ![Postman Envvars](./images/57-netbox/postman-envvars.png)
- Update the **Initial Authentication** POST call with the following contents added to the **Script** tab:
    ```javascript
    var jsonBody = JSON.parse(responseBody);
    pm.environment.set("token", jsonBody.access_token);
    ```
- Run the **Initial Authentication** call and ensure a token is returned.

When the Initial Authentication call is made, the token should get updated in the environment variable.
Once authenticated, the generated bearer-token will be used for follow-up API calls to authenticate.
Be aware, that the token is only valid for a certain period of time.
Either one must refresh it once in a while, or reauthenticate when the token has expired.

If you use an older version of Postman, you will find the script in a tab called **Tests**.

/// note
The Postman collection hosted on the developer portal made available by the NSP product-team stores the auth-token under `Globals`.
The script used in this activity stores the token in the environment instead, which allows toggling between different environments without the need to reconnect.
///

#### List all network ports
List all network ports using RESTCONF, browse to the following Postman endpoint:

- `24.11 Network Functions` 
    - `Network Infrastructure Management` 
        - `Network Inventory`
            - `Get vs Find Restconf API samples` 
                - `GET getAllPorts`

![GetAllPorts Restconf API call](./images/57-netbox/postman-getAllPortsCall.png)

#### Search NSP Inventory 
Execute the `Filter ethernet ports` Postman example found in:

- `24.11 Network Functions`
    - `Network Infrastructure Management`
        - `Network Inventory`
            - `Get vs Find Restconf API samples`
                - `POST Filter ethernet ports`. 

Because this is using the `nsp-inventory:find` RPC using RESTCONF `POST`, we can pass JSON in the **Body** tab to filter for specific ports. Inspect the **Body** tab and adjust the xpath filter.

```
{
    "input" : {
        "xpath-filter": "/nsp-equipment:network/network-element[ne-name='g2-pe1']/hardware-component/port[contains('name', '1/1/c10')]",
        "include-meta": false
    }
}
```

/// note
To keep things easy, we are filtering by `ne-name` and not by `ne-id`.
In the example above the filter matches for port `1/1/c10` on `PE1` for Group 2.
Adjust the `ne-name` to match your group.
///

Inspect the results - note the `equipment-extension-port:extension` stanza in the results body **doesn't**  have a `deployments` key.
We'll come back to this later.

### Create NSP ICM Templates
We'll now set up some configuration templates we'll later reference in our NetBox script.
Head over to the NSP UI and browse to `Device Management > Configuration Intent Types`.

#### Check ICM Intent Types
Ensure our required intent-types have been imported into `Device Management`, the three types listed below should be in the table with a `Success` status.

* `port-connector_gsros_<version>` - For basic configuration on the physical port (Admin state etc.)
* `icm-equipment-port-ethernet` - For Ethernet configuration on the physical port (MTU, LLDP etc.)
* `icm-router-network-interface` - For IP Interfaces added to the SR OS `Base` router (IPv4, IPv6 addresses etc.)

![NSP Intent Types](./images/57-netbox/nsp-intent-types.png)

#### Create ICM Templates
We'll now create ICM Templates, these are the blueprints we'll use to create Intent deployments in our NetBox script. 

* Using the drop-down next to `Device Management` browse to `Configuration Templates`.
* Create a template called `Group <GROUP_NUMBER> - NSP Activity 57 - Port Connector` using intent-type `port-connector_gsros_<version>`, substitute in your group number. Click Release.
* Repeat for the other two intent-types: `icm-equipment-port-ethernet` and `icm-router-network-interface` using similar names and substituting "Port Connector" for "Port Ethernet" or "Network Interface". This is a name to identify the template which we'll use later when we create intent instances.

![NSP Intent Template](./images/57-netbox/nsp-intent-template.png)

#### Create ICM Configuration Deployments

Create 3 ICM Configuration Deployments using your templates.
Choose an unused port and do some basic port configuration, unused ports can be determined from the topology diagram provided in the hackathon briefing.

| Template | Target | Config |
| --- | --- | --- |
| Connector Port | NE: `PE1`<br/>Port: `1/1/c10` | Breakout: `c1-100g` |
| Ethernet Port | NE: `PE1`<br/>Port: `1/1/c10/1` | *keep defaults* |
| Network Interface | Interface Name: `port_1/1/c10/1` | Port Binding: `port`<br/>Port `1/1/c10/1`<br/>IPv4 Primary Address: `10.6.20.25`<br/>IPv4 Primary Prefix Length: `31` |

/// note
We'll use this naming scheme in the deployment script. This is the basic process we'll use via the API for the NetBox script.
///

![NSP ICM Deployments](./images/57-netbox/nsp-icm-deployments.png)

* Re-execute the `Filter Ethernet ports` Postman call from the previous step - can you see the `deployments` key? See the details of the deployment listed. This is how you should detect if an existing ICM Deployment already exists for a port. 

### Create NetBox Event Rule
NetBox event rules allow for a script to be run when a NetBox object changes, such as being created, updated or deleted. The script receives the object details as an argument.

#### View the Dump Data Script
Back in the NetBox UI, browse to `Customization > Scripts` and click on the `Dump Data` script. At the top there are tabs to show the script source and to show the `Jobs` - these are the instances of the script being executed. You can click the ID number of each job execution to view the script output.

![NSP Dump Script](./images/57-netbox/nb-dump-script.png)

#### Create Dump Data Event Rule
NetBox can create a rule that responds to changes for particular objects and trigger web hooks or script executions. We're going to create a testing rule that runs an existing script called **DumpData** - all this script does is print out the `data` parameter that's passed to the `run()` method of the script when the Event Rule is triggered.

* Create an Event Rule under `Operations > Event Rules` with **Action Type** of `Script` set to the existing **DumpData** script. 
* Note the `Action data` field where you can provide arbitrary JSON that gets included with the `data` parameter, we'll use this later. 
* You can test this rule by making a change to a device's interface and inspecting the job log: `Operations > Jobs > <id>`. This output is a useful reference when creating your custom script.

![NetBox Event Rule](./images/57-netbox/nb-event-rule.png)


### Write NetBox Script
Our goal is to have a python script that gets uploaded to NetBox and run whenever an interface object in NetBox is created or changed. Your challenge is to flesh out the skeleton script with all the required functionality to query NSP inventory, determine what action is needed and make calls to the NSP API to create ICM Deployments. You'll want to use Postman as your API reference to find the endpoints you need and what needs to be passed in them.

NetBox scripts should be written in your own development environment or IDE - VSCode is a great starting point.

#### NetBox Script Skeleton
We've provided this skeleton script as a starting point - it provides the basic structure and allows you to run the script interactively (on the terminal) or after being uploaded to NetBox. 

For running on the terminal, please ensure you've installed the `requests` pip package.
```
pip install requests
```

!!! tip
    This skeleton script has some custom magic that means it can (mostly) be run outside the NetBox execution environment. This means participants can run the script on their local machine or on the jump host to test the NSP calls. Any calls that use the NetBox models will fail, comment those out and set static values during testing.

??? note "skeleton.py"
    ```python 
    --8<-- "./docs/nsp/advanced/resources/57-netbox/skeleton.py"
    ```

??? note "sample_data.json"
    ```json
    --8<-- "./docs/nsp/advanced/resources/57-netbox/sample_data.json"
    ```


* Copy the above `sample_data.json` and `skeleton.py` contents into their own files in your development environment. Edit the `sample_data.json` file and update the `nsp_host`, `nsp_user` and `nsp_password` keys to match your lab access details.
* Run the skeleton script, passing in the sample_data.json file. You should get a message indicating successful authentication. If not, diagnose why.

```bash
> python3 ./skeleton.py sample_data.json
> Authenticated with NSP! Status Code:200
```

#### Your Turn
There are some hints below about how you could structure your script, try your best without referring to this if you can.

#### Script format
* The netbox `data` parameter doesn't indicate the action type (create, update, delete) so some logic is required to determine the required action.
* Write a method that can interface with the NSP Inventory API (`Filter ethernet ports`) explored earlier and search for Port/Ethernet/Interface deployments.
* Write a method that can create/update/delete an NSP ICM Deployment given service data parameters and the ICM template name. You'll need to explore the NSP ICM Postman collection to find the best API call to make.
* You'll need to create separate Port, Ethernet and Interface Deployments when the script runs.
* Assemble the final logic in the run() method, pulling the required information from NetBox object queries (interface details like state, MTU, IP address etc.) and pass it to the ICM deployment `target_data` param.

You can test your script by running it interactively and pass in the `sample_data.json` file. As mentioned above, netbox object queries won't work - you'll need to stub those out for static values during testing. Example output from a script execution is shown below:
```bash
> python3 ./skeleton.py sample_data.json
> Authenticated with NSP! Status Code:200
> Querying NSP for Port Deployments...
> 1 Port deployment found
> NetBox interface exists, we need to update the NSP ICM Deployment
> Updating NSP ICM Deployment...
> SUCCESS:204 - updated NSP ICM Deployment for Port 1/1/c10.
```

#### Useful NetBox script snippets
The [NetBox Shell Documentation](https://netboxlabs.com/docs/netbox/en/stable/administration/netbox-shell/) is a good reference for how to query and filter models in Custom scripts. You can also access the API docs directly in NetBox (a good way to see keys on each model) at `http://GROUP_NUMBER.srexperts.net:8000/api/`.

* Lookup a device's `system` address using the NetBox API. 
```python title="Get System Address"
i = [i for i in 
        list(IPAddress.objects.filter(
            interface__device__name="pe1", interface__name="system")) 
        if ':' not in str(i.address) # only ipv4 address
    ][0]
```

* Retrieve a NetBox interface from the id parameter in the `data` param:
```python title="Get Interface by ID"
nb_interface = list(Interface.objects.filter(id=data.get('id')))
```

* Get the IP addresses (IPv4 and IPv6) for a given Interface:
```python title="Get IP addresses for an interface by Interface ID"
ip_addresses = list(IPAddress.objects.filter(interface_id=data.get('id')))
```

### Deploy to NetBox
Once you have a basic script that can create/update/delete NSP ICM intent deployments based on the sample data, we can setup the Event Rule in NetBox.

#### Upload Script
First, we need to upload your script to NetBox:

* Browse to `Customization > Scripts > Add` and upload your script source. 
* Associate the script to an `Event Rule`. You can either reuse the Event Rule we created earlier or create a second one which might be better for debugging.
* When an interface is changed, a NetBox `Job` will be created with script execution output, as executed by the Event Rule.

#### Create Event Rule
* Browse to `Operations > Event Rules` in NetBox
* Create an event rule that will trigger your script. 
* Note the `Action data` section - provide the following JSON snippet customized with your NSP's login details and host IP.

```json
{"nsp_host":"nsp.srexperts.net","nsp_password":"<NSP_PASSWORD>","nsp_username":"<NSP_USERNAME>"}
```

![Final Event Rule](./images/57-netbox/nb-event-rule-final.png)

#### Test
Now you can test! Choose a device interface, make a change and test your script. 

/// note
To browse and edit device interfaces in NetBox, navigate to `Devices > Device Components > Interfaces`.
///

Some example changes:

* Change the NetBox interface state to "disabled" to ensure a Port Connector ICM deployment disables the interface.
* Change the MTU of a NetBox interface to ensure the Ethernet ICM deployment changes the ethernet MTU.
* Add an IP address to an existing interface and ensure a Network Interface ICM deployment is created.
* Delete an interface that already has ICM deployments, ensure that all three deployments are removed from NSP.


### Solution
Here is an example solution that can create and update NSP ICM Intents:

??? note "Example Solution"
    ```python 
    --8<-- "./docs/nsp/advanced/resources/57-netbox/example-solution.py"
    ```

/// hint
If you’d like to try out the example solution, note that the Python script references the ICM templates. Each template appears twice in the script. Simply search for `NSP-Activity-57` (6 occurrences) and replace it with the template names you created in [Create ICM Templates](#create-icm-templates).
///

### Summary
If you've made it this far and have even a basic solution, congratulations! 

* You have learnt the basics of the NSP ICM RESTCONF API
* You understand how to create NetBox Event Rules to automate configuration changes
* You can integrate NetBox with NSP ICM to automatically deploy network changes

We have illustrated the power of integrating network management systems to create automated actions that can speed up network operations, avoiding manual work. There is lots of potential with Nokia NSP to extend these ideas into a limitless number of potential use-cases.