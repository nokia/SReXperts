# Network Programming via NSP APIs

| Item | Details |
| --- | --- |
| Short Description | Practical use of NSP REST/RESTCONF APIs |
| Skill Level | Advanced |
| Tools Used | NSP, POSTMAN, Jupyter/Python |

## Summary

This activity focuses on demonstrating the practical use of NSP APIs for network programming tasks. Initially, participants will explore these APIs using a Postman collection to execute predefined tasks. Subsequently, they will learn how to replicate these functionalities using Python scripts and workflows within NSP.

The primary objective is to enable participants to collect statistics on specific NSP objects, such as port utilization and CPU/memory usage, leveraging inventory information available in NSP.

## Goals to achieve

### Basic NSP API functionalities:
* Gain familiarity with NSP APIs by utilizing them through a Postman collection.
* Learn to execute network-wide assurance capabilities via APIs, enabling comprehensive monitoring and management across the entire network infrastructure.
* Understand the capabilities of NSP's Workflow Manager by executing tasks using the provided workflow.
* Learn how to use Python to access NSP APIs efficiently.

### Extend functionality by customizing Python scripts and workflows:
* Enable customization of statistics collection parameters within Python scripts and workflow environments.
* Enhance existing capabilities to obtain network conditions, such as CPU/memory usage, through API interactions.

Participants will receive detailed explanations of the provided resources, enabling them to modify Python scripts and workflows for prototyping purposes.

## Extra information

For additional assistance and documentation, please refer to the developer portal or reach out to Nokia support if access is required:
* [NSP Developer Portal](https://network.developer.nokia.com/)
* [NSP API Documentation](https://network.developer.nokia.com/api-documentation/)
* [NSP Telemetry API Documentation 24.8](https://network.developer.nokia.com/learn/24_8/network-functions/data-collection-and-analysis/telemetry/mdm-telemetry-use/)
* [Workflow Manager Guide](https://network.developer.nokia.com/learn/24_4/network-programmability-automation-frameworks/workflow-manager-framework/wfm-workflow-development/)

## Postman Collection API interaction - Steps

#### To download and import the Postman collection:
1. Download the provided Postman collection from the repository.
2. Import the collection into Postman.
3. Review the collection to understand the available endpoints and functionalities.

#### To execute tasks using the Postman collection:
1. Open Postman and select the imported collection.
2. Enter on environment variables to confirm the NSP instance. Moreover, each participant will have a different target NeId, configure it accordingly.
3. Execute the desired requests to perform statistics collection on NSP objects.

### Prerequisites:
- Ensure you have Postman installed on your machine. If not, download and install it from [https://www.postman.com/downloads/](https://www.postman.com/downloads/).
- Import the collection JSON file provided into Postman (`Network Programming via NSP APIs - SReXpert APAC 2024.postman_collection.json`).
- Import the environment file provided (`Hackhathon SReXperts APAC 2024.postman_environment.json`) into Postman.

### Steps:

0. Discovery of the lab

If this is your first NSP activity for this hackathon, ensure to first execute the activity called `nsp-b-lab-discovery`. It should not take long!

1. **Initial Authentication - Get Token**
   - Open Postman.
   - Ensure that the environment variables `server`, `user`, and `password` are imported from the environment file and correctly set. Note: replace the user with your user id.
   - Run the "Initial Authentication - Get Token" request.
   - Verify that the request executes successfully and retrieves the access token. The token will be automatically stored as a global variable for subsequent requests.

2. **Get Ports from Specific neId**
   - Ensure the access token obtained in step 1 is available as a global variable.
   - Set the environment variable `neId` with the specific Network Element ID.
   - Run the "Get ports from specific neId" request.
   - Check the response to verify that it retrieves the ports associated with the specified Network Element ID. The ports with the format "1/1/cX/Y" will be counted and printed.

3. **Create Subscription Ports in neId**
   - Ensure the access token obtained in step 1 is available as a global variable.
   - Set the environment variable `neId` with the specific Network Element ID.
   - Run the "Create subscription ports in neId" request. [NSP Telemetry API Documentation 24.8 - Restconf Subscription](https://network.developer.nokia.com/learn/24_8/network-functions/data-collection-and-analysis/telemetry/mdm-telemetry-use/#Use_Case_1%C2%A0RESTCONF_Subscription_Management%C2%A0) explains the meaning of variables and how they can be used. For the current subscription main parameters are:

	- **name**:
        - The "name" of a subscription must be unique and cannot be modified during the lifetime of the subscription. It typically describes the purpose or function of the subscription.
        - Example: `"Port-Utilization-{{neId}}"`

    - **type**:
        - The value for "type" must be defined as the "classId" in the MDM Telemetry Device Mapping files. It specifies the type of telemetry data being collected.
        - Example: `"telemetry:/base/interfaces/utilization"`

    - **notification**:
        - The "notification" parameter must be set to "enabled" for the Kafka notification service. It enables the notification mechanism for the subscription.
        - Example: `"enabled"`

    - **db**:
        - Use the "db" parameter to enable DB persistence for data collection. It is required for Use Case 5: Historical and Real-time Data Subscription, Streaming, and Plotting when historical data subscription is desired.
        - Example: `"enabled"`

    - **sync-time**:
        - The "sync-time" parameter specifies the collection interval anchor. It controls when a subscription is started and is used to stagger multiple subscriptions for improved performance.
        - Example: `"00:00"`

    - **filter**:
    	- The "filter" parameter enhances filtering functionality using xpath expressions to identify objects. They can be obtained from the inventory model.
    	- Example: `"/nsp-equipment:network/network-element[ne-id='{{neId}}']/hardware-component/port"`

4. **Delete RESTCONF Subscriptions**
   - Ensure the access token obtained in step 1 is available as a global variable.
   - Run the "Delete RESTCONF subscriptions" request.
   - Confirm that the request successfully deletes the specified RESTCONF subscription via NSP UI.

**Note:** Ensure that the environment file (`Hackhathon SReXperts APAC 2024.postman_environment.json`) is imported and correctly configured with the required variables (`server`, `user`, `password`, `neId`) before executing each request.

## Python script API interaction - Steps

### Prerequisites:
- Ensure you have Jupyter Notebook installed on your machine. You can to set up Jupyter in VSCode following these steps:
1. Ensure you have Python installed on your system. If not, download and install Python from [python.org](https://www.python.org/downloads/).
2. Install Visual Studio Code from [code.visualstudio.com](https://code.visualstudio.com/).
3. Open VSCode and install the "Python" extension from the Extensions marketplace.
4. Install the "Jupyter" extension from the Extensions marketplace.
5. Open a new terminal in VSCode and install Jupyter by running the command: `pip install jupyter`.
6. Create a new Jupyter notebook in VSCode by opening the Command Palette (Ctrl+Shift+P), typing "Jupyter: Create New Blank Notebook", and selecting it.
- Make sure you have the necessary Python libraries installed: requests, json, base64, re, urllib.
- Open Jupyter Notebook and the file (`Network Programming via NSP APIs - SReXpert APAC 2024.ipynb`).
- Copy the provided script into a new cell in your Jupyter Notebook.



### Steps:

1. **Set up NSP Information:**
   - Modify the `username`, `password`, and `NSP_server_IP` variables with your NSP server credentials and IP address. Note: replace the user with your user id.

2. **Specify Use Case Target Information:**
   - Set the `NeId` variable to the specific Network Element ID.

3. **Authenticate:**
   - Run the cell to authenticate with the NSP server and obtain an access token.

4. **Retrieve Network Inventory from the Device:**
   - Execute the cell to fetch network inventory data from the specified Network Element.

5. **Create Telemetry Subscription:**
   - The script will automatically filter the ports based on the specified pattern and create telemetry subscriptions for each port.
   - Execute the cell to create telemetry subscriptions for the filtered ports.

6. **Check the Notifications in the System:**
   - Run the cell to retrieve and print the subscriptions currently active in the system.

7. **Clean up the Subscriptions:**
   - Execute the cell to delete the created subscriptions.

**Note:** Ensure that the Python environment where Jupyter Notebook is running has access to the NSP server and can communicate over HTTPS. Adjust any firewall or network settings as needed.

Feel free to run each cell in sequence by clicking on it and pressing Shift + Enter or by using the "Run" button in the Jupyter Notebook interface. Ensure that you follow the order specified above to execute the script successfully.

## Workflow execution interactions - Steps

### Prerequisites:

- Ensure you have access to the lab NSP provided for the hackathon.
- Basic knowledge on NSP Workflow Manager.
- Have this repo cloned.

### Steps:

1. **Log in to NSP and navigate to Workflow Manager:**
   - Provide the correct credentials. When the user has accessed NSP, click on the "hamburguer" menu (top left corner) and select "Workflows".
2. **Import workflows and actions into NSP:**
   - In the dropdown menu, select "All workflows" and click on the "Import" button on the top right.
   - Select the workflows included in this repo (_.yaml_ files) and import them in the system.
   - In the dropdown menu, select "actions" and click on the "Import" button on the top right.
   - Select the action provided in this repo (_.action_).
3. **Execute this workflow:**
   - In the all workflows view, select the workflow just uploaded (_inventory2telemetry_) by double-clicking and execute. You will have to enter a valid NE ID.
   - The workflow should display, asking for user input, all ethernet ports to create the subscription.
   - Select few (as desired) and proceed.
   - The workflow should terminate successfully and the subscriptions should appear in the _Data Collection and Analysis --> Management_ view.

The user can optionally execute the _deleteSubscriptionByKeyword_ to remove the created subscriptions from the system.

## Expanding use case to support system information

### Introduction

System information like CPU and memory utilization can be monitored in NSP. [NSP Telemetry API Documentation 24.8](https://network.developer.nokia.com/learn/24_8/network-functions/data-collection-and-analysis/telemetry/mdm-telemetry-use/)

### Customizing Postman Collection

To customize the Postman collection and extend functionality to support CPU and memory utilization, follow these steps:

1. **Update Subscription Configuration**:

   In the provided subscription JSON, modify the parameters to monitor CPU and memory utilization.

   ```json
   {
       "subscription": [
           {
               "name": "systemInfo",
               "description": "systemInfo for Hackathon",
               "period": 60,
               "sync-time": "00:00",
               "state": "enabled",
               "type": "telemetry:/base/system-info/system",
               "notification": "enabled",
               "db": "enabled"
           }
       ]
   }
   ```

   Ensure that the following parameters are appropriately configured:

   - **name**: A unique name for the subscription.
   - **description**: Description of the subscription.
   - **period**: Interval (in seconds) at which data is collected.
   - **sync-time**: Time anchor for data collection synchronization.
   - **state**: State of the subscription (enabled or disabled).
   - **type**: Type of telemetry data to be collected (e.g., CPU and memory utilization).
   - **notification**: Enable or disable notification for the subscription.
   - **db**: Enable or disable database persistence for data collection.

2. **Import Updated Collection to Postman**:

   Once you've updated the subscription configuration, import the updated collection to Postman.

3. **Set Environment Variables**:

   Set the necessary environment variables such as server IP, username, password, and any other variables required for authentication and endpoint configuration.

4. **Run Subscription Request**:

   Run the "systemInfo" subscription request to start monitoring system information including CPU and memory utilization.

5. **Verify Results**:

   After running the subscription request, verify that the system information, including CPU and memory utilization, is being collected successfully.

By following these steps, you can expand the functionality of the Postman collection to support monitoring of CPU and memory utilization in NSP.

## Customizing Jupyter Notebook

### Introduction

Following are the steps to customize the provided Python Jupyter Notebook to perform a systeminfo subscription in NSP. As stated, before the systeminfo subscription allows you to monitor system information such as CPU and memory utilization.

### Steps to Customize Notebook

1. **Open the Jupyter Notebook**:
   - Open the Jupyter Notebook file in your preferred Python environment.
   - Copy the file (Network Programming via NSP APIs - SReXpert APAC 2024.ipynb) as Custom - Network Programming via NSP APIs - SReXpert APAC 2024.ipynb.

2. **Check NSP Setup Information**:
   - Check the `username`, `password`, and `NSP_server_IP` variables with the appropriate values for your NSP environment. Note: replace the user with your user id.

3. **Update Use Case Target Information**:
   - If necessary, update the `NeId` variable with the specific Network Element ID.

4. **Authenticate**:
   - Ensure that the authentication process is successful by running the authentication code block.

5. **Network Inventory from the Device**:
   - Run the code block to retrieve network inventory information from the specified device.

6. **Parse Component ID and Name**:
   - If necessary, modify the code to parse the component ID and name based on the system information you want to monitor (e.g., CPU and memory utilization).

7. **Create Telemetry Subscription**:
   - Update the `url` variable with the appropriate endpoint for creating subscriptions.
   - Modify the payload JSON to create a subscription for system information (previous section explains the format).
   - Execute the code block to create the telemetry subscription.

8. **Check Notifications in the System**:
   - Run the code block to check the notifications in the system and verify that the subscription was successfully created.

9. **Clean Up Subscriptions** (Optional):
   - If necessary, modify or run the code block to delete any existing subscriptions related to system information.

10. **Run the Modified Notebook**:
    - Save the changes and execute the modified Jupyter Notebook to perform the systeminfo subscription.

11. **Verify Results**:
    - After running the notebook, verify that the system information subscription is active and collecting data as expected.

12. **Additional Customizations**:
    - Depending on your specific requirements, you may need to further customize the notebook code to handle additional functionalities or data processing related to system information monitoring.

By following these steps, you can customize the Python Jupyter Notebook to perform a systeminfo subscription and monitor CPU and memory utilization in your NSP environment.

## Customizing Workflows in NSP

#### To customize workflows and extend functionality:
1. Access Workflow Manager within NSP.
2. Import the workflow definitions (All Workflows --> Import) and adHoc actions (Actions --> Import) to see the provided examples.
3. Locate the relevant workflow and edit it according to your requirements. This may include: a) updating the inventory calls to fetch different elements b) customize the filtering and YAQL processing and c) add new actions or modify existing ones to address the required functionality.
4. Utilize the provided IDE plugin for Workflow Manager for a more efficient development experience.

Useful information:
- [YAQL library](https://yaql.readthedocs.io/en/latest/standard_library.html)
- [Mistral DSL v2](https://docs.openstack.org/mistral/latest/user/wf_lang_v2.html)
