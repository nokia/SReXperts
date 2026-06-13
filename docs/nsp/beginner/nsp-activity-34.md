# Multiple Service Profiles

|     |     |
| --- | --- |
| **Activity name** | Multiple Service Profiles |
| **Activity ID** | 34 |
| **Short Description** | Create distinct prepopulated service configurations by choosing a service profile |
| **Difficulty** | Beginner |
| **Topology Nodes** | any SR OS nodes |
| **References** | [Intent Type ViewConfig Form](https://network.developer.nokia.com/learn/25_11/artifact-development/programming/network-automation/viewconfig-forms/) |

## Objectives

Creating a service often means entering many attributes by hand. That is slow and makes inconsistent or incorrect values more likely, even when operators only need a few standard "shapes" of service.

This activity introduces **Service Profiles** (for example **Gold**, **Silver**, or **Bronze**): the operator picks a tier and the form prepopulates attributes from that profile’s predefined service criteria, for faster provisioning with fewer manual errors.

## Technology Explanation

### Intent Manager

Intent Manager provides intent-based networking in NSP. It turns high-level objectives into automated actions so operators state **what** they want instead of **how** to configure it. Intent types are implemented in JavaScript using YANG-based models.

Declarative intent configuration (with validation) is kept separate from lifecycle operations (CRUD, audits, and synchronization): sync deploys changes and reconciles misaligned state, and audits detect drift. 

## Intent Type View

A view in Intent Manager lets you save a specific layout and filter criteria so you can quickly access subsets of your network configuration without rebuilding the interface manually. In this activity, we focus on managing the **epipe-site-sr** intent type.

## Tasks

/// warning
Remember that you are using a shared NSP system. Include your group number in every activity you perform.
///

**You should read these tasks from top to bottom before beginning the activity.**

It is tempting to skip ahead, but tasks may require you to have completed previous tasks before tackling them.

### Quick start on NSP Web UI

|     |     |
| --- | --- |
| **NE Session** | `☰` → `Network Search and Inventory` → find your group’s PE node (for example `g7-pe1`) → open the row context menu `⋮` → `Open in NE Session`. |
| **NSP Help** | `?` icon at the top right for context-aware quick help and to open the Help Center. On some pages, `?` also links directly to related Help Center articles. |
| **Intent Manager** | `☰` → `Network Intents` |
| **Service Management** | `☰` → `Service Management` |


### Creating a new intent type version

Before configuring the view, each user must create a unique version of the intent type based on their group number.

1. In the **Intent Manager**, locate the **epipe-site-sr** intent type and select **Export**.
2. To **Modify Metadata**, unzip the exported folder locally. Open the `meta-info.json` file and change the version number (on line 3) to match your assigned group number.
3. Now **Repackage** or compress the contents of the folder into zip format.
4. Return to the **Intent Manager** and from the **Import** option at the top right, import the newly zipped folder to create your group-specific version.

/// details | Are you repackaging to zip on a Mac?
    type: question

Compressing to create an `Archive.zip` adds a `__MACOSX` folder and sometimes a `.DS_Store` file. These system files interupts the import into the workflow system. So to remove it, run the following command in the terminal:
```
zip -d Archive.zip  __MACOSX/\*
zip -d Archive.zip '*.DS_Store'
```

///

### Create a new view

1. Navigate to **Intent Manager** and ensure you are in the **Intent Types** dropdown. Double-click the group-specific intent type version you created in the previous task.
2. Click the **Manage Views** button on the top-right corner of the workspace.
3. In the Manage Views interface, click the **+** icon to create a view and provide a name that includes the **Service Profile**, the **Group Name**, and a reference to the **epipe-site-sr** intent type.
    * *Format:* `g[GroupID]_[ServiceProfile]_epipe-site-sr`
    * *Example:* `g3_Gold_epipe-site-sr` or `g3_Silver_epipe-site-sr`.
4. To establish a functional baseline, copy the entire content of an existing **default.viewConfig** into the newly created view and click **Save selected file**.
5. Now it is your turn to literally "play" with building this new config form. Start by clicking the three dots on the viewConfig you just created, then choose **Build Viewconfig**. 

/// details | ViewConfig Forms
    type: info
    open: true

On the left-hand side you will find all of the attributes in this schemaForm, along with their current state. By clicking on the 3 dots on the right side of each attribute, you can choose to delete or hide these attributes. 

You can also choose **Adjust Attribute**, where you have finer control over an attribute (for example, default value, title, description, display mode, and more).

You can find more details about viewconfig forms in our [Dev Portal](https://network.developer.nokia.com/learn/25_11/artifact-development/programming/network-automation/viewconfig-forms/).

///

Once all changes in the `viewConfig` are correctly formatted, click the **Save ViewConfig** button to commit your changes.

To verify the configuration, navigate to the corresponding **schemaForm** file in the same section. This file displays the generated UI based on your configuration. Verify that the fields and layout appear as intended.

After confirming in the "Views" tab that the schemaForm is behaving the way it should, save the intent type and navigate to **Service Management**.

### Create a new service site template

/// note
In **Intent Manager**, make sure the underlying **Intent Type** is set to **Active** state.
///

Navigate to **Service Management** and select **Service Site Templates** from the dropdown. Fill in the details based on the intent type version and view you created. Repeat the process to create multiple **Service Site Templates** one for each view you had created with a meaningful name that reflects the service profile and your group name.

### Create a new service template

In this task, you create a new service template using the schemaForm from the previous task.

/// note
In **Intent Manager**, make sure the underlying **Intent Type** is set to **Active** state.
///

1. Navigate to **Service Management** and select **Service Templates** from the dropdown.
2. Click the **+ CREATE** button in the top right corner.
3. In the **General** section, fill in the following:
    * **Name:** Use a name that reflects the type of service (epipe) as well as your group name
    * **Description:** Define the service level or specific customer use case.
    * **Service Intent Type:** Select the specific model that governs this service (e.g., `epipe`).
    * **Intent Version:** Select the version compatible with your current network software. 
    * **Template State:** Set to **Draft** for initial testing.
    * Set to **Released** to make it available for production service creation.
    * **Config Form:** Select the "Default" config form.
4. Review all entered data for accuracy and click the **CREATE** button at the bottom of the page to create the template.

### Deploy to Network (optional)

With all templates in place, let’s test your work. Choose the service template and create a new service on any of the devices assigned to your group. You can use any of the service profiles you defined to test the deployment.

## Summary

Congratulations! You have completed this activity. Take a moment to review what you achieved:

* Gained hands-on experience in the Intent Manager backend by manually exporting, editing JSON metadata for version control, and re-importing custom intent types.
* Demonstrated the ability to transform a standard data model into a tailored user experience by utilizing the "Build ViewConfig" tool to hide, show, and rename attributes.
* Learned how to reduce operational risk by abstracting complex network parameters into simple "Gold, Silver, and Bronze" service tiers.
* Created a service in the network using your own intent type.
