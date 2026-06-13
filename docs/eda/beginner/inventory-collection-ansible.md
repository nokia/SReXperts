# Inventory Collection with Ansible

| <nbsp> {: .hide-th } |                                                                                                                                                                                                                        |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Inventory collection with Ansible |
| **Short Description**       | Retrieve service information using Ansible |
| **Difficulty**              | Beginner |
| **Tools used**              | [Ansible](https://docs.ansible.com/) , [Python](https://www.python.org) |
| **Topology Nodes**          | `leaf11`, `leaf12` and `leaf13` |
| **References**              | [Nokia EDA Ansible Collections][ansible-eda-doc] |

[ansible-eda-doc]: https://ansible.eda.dev/

Nokia EDA employs the "API first" approach, where every action performed in the platform is backed by an API call. By following this design paradigm, EDA offers its users a complete and open interface to write automation and integration tools leveraging these APIs.

In this exercise, you will use the official [EDA's Ansible collections][ansible-eda-doc] that are powered by the very same EDA REST API to extract operational data from the platform and build a readable CSV report.

## Prerequisites

Apart from having some familiarity with EDA, you should have some experience with the following tools, languages and technologies to successfully complete this activity:

* YAML Syntax
* Ansible Basics
* Python coding

## Objective

You have been tasked with creating an Excel-compatible report for another team that should include information about the network services deployed in a fabric along with the interfaces, VLANs and nodes participating in these services. Since Nokia EDA manages the data center network and the services running on top of it, you can get all of the required information easily by interfacing with EDA API and not talking to the nodes directly.

This task offers you the opportunity to leverage EDA's Ansible collections to get the necessary service information in a reusable, low-code approach, rather than having to write complex scripts to get the data from the nodes directly.

To map the services to their respective nodes and interfaces, and create a human-readable report in the form of a CSV file (which can be easily opened as an Excel table) you will need to create a lightweight Python script that acts on the data collected with Ansible.

## Technology explanation

Ansible is a powerful, open-source IT automation engine designed to simplify complex orchestration, configuration management and application deployment tasks. At its core, Ansible provides a human-readable, declarative language (YAML) to define automation jobs, allowing you to describe your desired target infrastructure state rather than writing complex scripts to get them there. It is agent-less and it securely connects to systems over standard protocols or directly to APIs to execute tasks efficiently, consistently, and reliably.

### EDA Ansible Collections on Ansible Galaxy

To interact with various systems, Ansible uses modules packaged into "Collections" hosted on Ansible Galaxy. Nokia EDA provides [Ansible collections](https://docs.ansible.com/projects/ansible/latest/collections_guide/index.html) published on [Ansible Galaxy](https://galaxy.ansible.com/ui/namespaces/nokia/) that allow you to manage and query resources declaratively. To keep the automation modules organized logically, the EDA Ansible integration is divided into two main categories:

1. **Core Collections:** These collections interface with the foundational EDA platform elements. You can use these modules to interact with base system APIs, handle system settings, alarms and manage EDA transactions.
2. **Application Collections:** These collections interact with the applications installed on top of EDA, which can be developed by anyone and/or be installed/removed anytime. [EDA Applications](https://docs.eda.dev/26.4/apps/) deliver additional functionality on top of the core EDA platform, for example:

    * Services app enables users to declaratively manage virtual network services.
    * Protocols app adds support for managing routing protocols
    * Interfaces app provides support for managing physical interfaces

### Collections versioning and APIs

As an Ansible user interacting with EDA, you have to use not one, but several collections. This is because EDA's API is pluggable and extensible. The applications may be installed and removed anytime, therefore the collections need to be standalone and versioned independently.

Read more about the mapping between EDA APIs and Ansible collections in the [Nokia EDA Ansible Collections documentation](https://ansible.eda.dev/#eda-apis-and-collections).

## Tasks

At a high level, the tasks ahead of you can be divided into three high-level blocks:

1. **Environment setup and inventory creation**: Define the target environment, credentials, and API endpoints using Ansible variables.
2. **Data collection with Ansible**: Create a sequence of tasks to authenticate against the EDA API, securely fetch an access token and individually retrieve configurations from EDA.
3. **Report creation with Python**: Create a Python script that parses the extracted JSON responses, correlates the information and formats the final output as a clean, Excel-compatible comma-separated values (`.csv`) file.

### Environment Setup

It is important to understand the required Python dependencies and Ansible Collections that are needed to run this activity. To ensure a fast and reproducible Python environment, this activity uses **[`uv`](https://docs.astral.sh/uv/)**.

/// note | **What is `uv`?**

`uv` is an extremely fast Python package and project manager written in Rust. It serves as a modern, high-performance drop-in replacement for tools like `pip` and `virtualenv`. It ensures dependencies are resolved and installed quickly within an isolated virtual environment.

///

Since EDA REST API endpoint is available on port 443 by default, you can choose where you want to develop and run your Ansible playbook:

* on your local machine
* on the hackathon server using the Code Server
* on the hackathon server using the CLI

> Regardless of the location you choose, the steps to follow are almost identical.

The [Quick Start][ansible-eda-doc] procedure in the Nokia EDA Ansible Collections documentation describes the steps to be followed to initialize your environment using `uv`:

1. Create a directory where you will initialize your project environment:

    ```bash
    mkdir eda-ansible
    cd eda-ansible
    ```

2. Create a project's `pyproject.toml` file which contains the core dependencies required for Nokia EDA Ansible Collections:

    ```toml
    cat << EOF > pyproject.toml
    [project]
    name = "eda-ansible"
    version = "0.1.0"
    description = "Nokia EDA Ansible collections dependencies"
    readme = "README.md"
    requires-python = "~=3.12.0"
    dependencies = [
        "ansible-core >= 2.15",
        "deepdiff >= 8.5.0",
        "pydantic >= 2.11.7",
        "python-dateutil >= 2.9.0.post0",
        "typing-extensions >= 4.7.1",
        "urllib3 >= 2.1.0",
    ]
    EOF
    ```

3. Run the `uv sync` command to seed your local virtual environment with the defined dependencies:

    ```bash
    uv sync
    ```

4. Now you need to install the set of EDA Ansible collections that you will leverage to achieve the task at hand.  
    You typically always need the core and utils collections, as they assist with EDA authentication and interactions with EDA's Core API. These collections are namely `nokia.eda_core_v1` and `nokia.eda_utils_v1`.

    Besides that, you need to install the collections that deal with EDA services and interfaces, these are two different applications, and, therefore, two different collections - `nokia.eda_services_v2` and `nokia.eda_interfaces_v1`.

    You can install them into your `uv`-managed environment using the following command:

    ```bash
    uv run ansible-galaxy collection install \
    nokia.eda_utils_v1 nokia.eda_core_v1 \
    nokia.eda_services_v2 \
    nokia.eda_interfaces_v1
    ```

Now your environment is ready to use the EDA Ansible collections.

### Configure the Ansible Inventory

In a typical box-by-box automation scenario the Ansible inventory file would contain a list of nodes in your network and the connection details to each of them. However, when working with an automation platform that manages the entire network, your Ansible inventory file would just contain the details of the automation platform itself, since Ansible will connect to the platform to execute the tasks.

Create a new file called `inventory.yaml` to define the connection details to your EDA instance following the example available at [Nokia EDA Ansible Configuration](https://ansible.eda.dev/#configuration).

> Since we are using `uv` to manage the Python environment, you will need to add a variable in your inventory file to ensure that the Python interpreter used by Ansible is the same as the one used by the playbook run with `uv`.  
> `ansible_python_interpreter: "{{ ansible_playbook_python }}"`

/// details | Solution

```yaml
all:
  vars:
    eda_api_url: https://<Your EDA instance URL>
    tls_skip_verify: false
    eda_username: admin
    eda_password: <Event Password>
    ansible_python_interpreter: "{{ ansible_playbook_python }}" #(1)!
  hosts:
    localhost:
      ansible_connection: local
```

1. This variable is required to ensure that the Python interpreter used by Ansible is the same as the one used by the playbook run with `uv`.

///

### Playbook structure

Now it is time to start authoring the playbook that will gather the data you need.  
Create a new playbook file called `playbook.yaml` to define the tasks that will be executed and since you are talking to an automation platform you can disable fact-gathering as we are not interested in the facts of the local machine.

```yaml
- name: Inventory collection playbook
  hosts: all
  gather_facts: false
  tasks:
    - name: some task
      ...
    - name: another task
```

### Authentication handling

The playbook structure we outlined above should start with the authentication tasks as our Ansible client will need to authenticate against EDA API before it can run any other modules from EDA Ansible collections.

EDA API authentication is covered in detail in the [Authentication section](https://ansible.eda.dev/#authentication) of the Nokia EDA Ansible Collections documentation. Skim through it and create the tasks to authenticate against EDA API by fetching the client secret and access token values.

You will need to use the following modules:

* [`nokia.eda_utils_v1.get_client_secret`](https://ansible.eda.dev/nokia.eda_utils_v1/module/get_client_secret) to fetch the client secret
* [`nokia.eda_utils_v1.get_token`](https://ansible.eda.dev/nokia.eda_utils_v1/module/get_token) to fetch the access token

/// details | Solution

```yaml
tasks:
  - name: Get client secret
    nokia.eda_utils_v1.get_client_secret:
      baseUrl: "{{ eda_api_url }}"
      keycloakAdminUsername: "{{ eda_username }}"
      keycloakAdminPassword: "{{ eda_password }}"
      tlsSkipVerify: "{{ tls_skip_verify }}"
    register: client_secret

  - name: Fetch EDA access token
    nokia.eda_utils_v1.get_token:
      baseUrl: "{{ eda_api_url }}"
      clientSecret: "{{ client_secret.result[0].secret }}"
      username: "{{ eda_username }}"
      password: "{{ eda_password }}"
      tlsSkipVerify: "{{ tls_skip_verify }}"
    register: access_token

  - name: Print access token
    ansible.builtin.debug:
      msg: "Access token: {{ access_token.result.access_token }}"
```

///

To verify that you have dialed in the authentication tasks correctly, you can add the `ansible.builtin.debug` task to print the access token value and run the playbook to see if you get the expected output:

```bash
uv run ansible-playbook -i inventory.yaml playbook.yaml
```

You should see the access token value printed in the output.

### Data collection

With authentication bits in place, you can start collecting the data you need for the report. The network you have at hand is a Layer 3 fabric with an EVPN-VXLAN overlay on top of it and in EDA you deal with abstracted network resources, rather than with CLI configuration snippets.

For example, Bridge Domains - to represent Layer 2 VRFs; Routers - to represent Layer 3 VRFs; Interfaces - to represent physical interfaces; VLANs - to represent attachments between the overlay services and the physical interfaces; IRBs - to represent Integrated Routing and Bridging interfaces; etc.

These abstracted resources are naturally exposed as Ansible modules and contained in several collections. For example, the [`nokia.eda_services_v2`](https://ansible.eda.dev/nokia.eda_services_v2/module/) collection contains the modules to interact with the Bridge Domains, Routers, VLANs, IRBs and Bridge Interfaces.

Let's work together through an example of how to collect the Bridge Domains[^1] data. The Bridge Domains are the Layer 2 VRFs in EDA and represent the broadcast domains created in the overlay network on top of the IP fabric.

You'll find the [`nokia.eda_services_v2.bridgedomain_list`](https://ansible.eda.dev/nokia.eda_services_v2/module/bridgedomain_list) module in the `nokia.eda_services_v2` collection that lists all instances of Bridge Domains configured in a particular EDA instance.

Here is how the task to fetch the Bridge Domains data looks like:

```yaml
- name: Get list of Bridge Domains
  nokia.eda_services_v2.bridgedomain_list:
    baseUrl: "{{ eda_api_url }}"
    authToken: "Bearer {{ access_token.result.access_token }}"
    tlsSkipVerify: "{{ tls_skip_verify }}"
    namespace: eda
  register: bds

- name: Print Bridge Domains data
  ansible.builtin.debug:
    var: bds.result
```

Note, how the `baseUrl` module argument is set to the value of the `eda_api_url` variable from the inventory file.

The `authToken` module argument is constructed by concatenating the `Bearer` prefix with the value of the `access_token.result.access_token` variable we fetched and registered in the previous task in the playbook.

The `tlsSkipVerify` module argument is set to the value of the `tls_skip_verify` variable from the inventory file. In your setup we have configured the TLS certificates to be verified, but in your lab you might want to flip it to `false` if needed.

The `namespace` module argument is set to `eda` as all the services are deployed in the `eda` namespace.

> Add the `ansible.builtin.debug` task to print the Bridge Domains data to verify that you see the data for the Bridge Domains configured in your EDA instance.

Also register the fetched output to a variable called `bds` as we would need to massage the returned data later to generate the CSV file for reporting.

The data recorded in the `bds` variable contains the list of dictionaries, each representing a Bridge Domain under the `results.items` key. Each dictionary contains the following keys pertaining to the requested resource:

* `apiVersion`
* `kind`
* `metadata`
* `spec`
* `status`

/// details | Example output of the `bds` variable

```yaml
{
    "changed": false,
    "failed": false,
    "result": {
        "apiVersion": "services.eda.nokia.com/v2",
        "items": [
            {
                "apiVersion": "services.eda.nokia.com/v2",
                "kind": "BridgeDomain",
                "metadata": {
                # ...
                    "name": "macvrf11",
                    "namespace": "eda"
                },
                "spec": {
                    # ...
                },
                "status": {
                    # ...
                }
            },
            {
                "apiVersion": "services.eda.nokia.com/v2",
                "kind": "BridgeDomain",
                "metadata": {
                    # ...
                    "name": "macvrf1101",
                    "namespace": "eda"
                },
                "spec": {
                    # ...
                },
                "status": {
                    # ...
                }
            }
        ],
        "kind": "BridgeDomainList"
    },
    "status": 200
}
```

///

Now that you know how to fetch the Bridge Domains data, you can start fetching the rest of the abstracted resources related to the overlay network, namely you will need:

* Routers
* VLANs
* Bridge Interfaces
* Router Interfaces
* IRBs

Find the respective modules in the [`nokia.eda_services_v2`](https://ansible.eda.dev/nokia.eda_services_v2/module/) collection and create the tasks to fetch the data for each of the resources while saving the output to variables.

/// details | Solution

```yaml
- name: Get list of Bridge Domains
  nokia.eda_services_v2.bridgedomain_list:
    baseUrl: "{{ eda_api_url }}"
    authToken: "Bearer {{ access_token.result.access_token }}"
    tlsSkipVerify: "{{ tls_skip_verify }}"
    namespace: eda
  register: bds

- name: Get list of Routers
  nokia.eda_services_v2.router_list:
    baseUrl: "{{ eda_api_url }}"
    authToken: "Bearer {{ access_token.result.access_token }}"
    tlsSkipVerify: "{{ tls_skip_verify }}"
    namespace: eda
  register: routers

- name: Get list of VLANs
  nokia.eda_services_v2.vlan_list:
    baseUrl: "{{ eda_api_url }}"
    authToken: "Bearer {{ access_token.result.access_token }}"
    tlsSkipVerify: "{{ tls_skip_verify }}"
    namespace: eda
  register: vlans

- name: Get list of Bridge Interfaces
  nokia.eda_services_v2.bridgeinterface_list:
    baseUrl: "{{ eda_api_url }}"
    authToken: "Bearer {{ access_token.result.access_token }}"
    tlsSkipVerify: "{{ tls_skip_verify }}"
    namespace: eda
  register: bis

- name: Get list of Routed Interfaces
  nokia.eda_services_v2.routedinterface_list:
    baseUrl: "{{ eda_api_url }}"
    authToken: "Bearer {{ access_token.result.access_token }}"
    tlsSkipVerify: "{{ tls_skip_verify }}"
    namespace: eda
  register: ris

- name: Get list of IRBs
  nokia.eda_services_v2.irbinterface_list:
    baseUrl: "{{ eda_api_url }}"
    authToken: "Bearer {{ access_token.result.access_token }}"
    tlsSkipVerify: "{{ tls_skip_verify }}"
    namespace: eda
  register: irbs
```

///

And you will also need to fetch the physical interfaces to map them to the overlay services for you report. The physical interfaces are part of the Interfaces application and, as you now know, each application has its own collection of modules - [`nokia.eda_interfaces_v1`](https://ansible.eda.dev/nokia.eda_interfaces_v1/) collection contains the modules to interact with the physical interfaces.

Find the [`nokia.eda_interfaces_v1.interface_list`](https://ansible.eda.dev/nokia.eda_interfaces_v1/module/interface_list) module in the `nokia.eda_interfaces_v1` collection that lists all instances of physical interfaces configured in a particular EDA instance.

/// details | Solution

```yaml
- name: Get list of Interfaces
  nokia.eda_interfaces_v1.interface_list:
    baseUrl: "{{ eda_api_url }}"
    authToken: "Bearer {{ access_token.result.access_token }}"
    tlsSkipVerify: "{{ tls_skip_verify }}"
    namespace: eda
  register: interfaces
```

///

### Saving the data for post processing

Now that you have collected the data, you are keeping it in the Ansible registered variables, or in other words, in the memory of the Ansible client. However, since we want to massage the fetched data into a CSV file to visualize it in Excel, we better save it to a file so that we can later process it with a Python script.

To save the data to a file you can use the native Ansible module [`ansible.builtin.copy`](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/copy_module.html) and export the variables to JSON files. Feel free to think on how to do this yourself and then check the solution below.

/// details | Solution

```yaml
    - name: Create data directory for output json files
      ansible.builtin.file:
        path: data
        state: directory

    - name: Save JSON outputs for Python processing
      ansible.builtin.copy:
        content: "{{ item.data | to_nice_json }}"
        dest: "{{ item.file }}"
      loop:
        - { data: "{{ bds.result }}", file: 'data/bds.json' }
        - { data: "{{ routers.result }}", file: 'data/routers.json' }
        - { data: "{{ vlans.result }}", file: 'data/vlans.json' }
        - { data: "{{ bis.result }}", file: 'data/bis.json' }
        - { data: "{{ ris.result }}", file: 'data/ris.json' }
        - { data: "{{ irbs.result }}", file: 'data/irbs.json' }
        - { data: "{{ interfaces.result }}", file: 'data/interfaces.json' }
```

///

With the solution like presented above, you get each of the registered variables saved to a separate JSON file in the `data` directory. Feel free to inspect the files to see the patterns in the data structure each abstracted resource has.

### Transforming the data for CSV generation

At this point you have a set of JSON files with the data you need to generate the CSV file. You can now develop a program in whatever language you prefer to parse the JSON files and generate the CSV file in the structure that makes sense for you.

For example, our CSV will have the following headers: `Service Name`, `Service Type`, `Interface Name`, `Interface Type`, `VLAN ID`, `Node Name`, where columns are delimited by a pipe (`|`) character.

/// tab | Service Name
Name of the L2/L3 service (network-instance) configured in EDA.
///

/// tab | Service Type
If the service is a Bridge Domain (L2 service), display `MAC-VRF`. If the service is a Router (L3 service), display `IP-VRF`.
///

/// tab | Interface Name
Name of the physical port which is attached to the service.
///

/// tab | Interface Type
It can be a regular bridged/routed interface, a LAG interface or an IRB interface. If it is a LAG interface, display the names of the other members of the LAG.
///

/// tab | VLAN ID
VLAN ID when dot1q encapsulation is used. This field does not apply to IRB interfaces.
///

/// tab | Node Name
Target node whose interface(s) are linked to the specific service.
///

This activity is not a lesson on how to parse JSON and/or generate a CSV file, therefore we will present one of the ways to do this in Python and you are free to use whatever language you prefer and develop your own solution.

/// details | Solution

You can execute a script with `uv`, like this:

```bash
uv run <path to the script>
```

```python
--8<-- "docs/eda/beginner/assets/generate_csv.py"
```

///

An example of what the proposed CSV could look like when rendered as a table is shown below:

| Service Name | Service Type | Interface Name | Interface Type | VLAN ID | Node Name |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ipvrf1201 | IP-VRF | irb0 | irb | | gXX-leaf11 |
| macvrf11 | MAC-VRF | ethernet-1-1 | interface | 1 | gXX-leaf11 |
| macvrf11 | MAC-VRF | ethernet-1-2 | lag interface with "ethernet-1-2" on device "gXX-leaf12", "ethernet-1-2" on device "gXX-leaf13" | 1 | gXX-leaf11 |
| macvrf1101 | MAC-VRF | ethernet-1-1 | interface | 1101 | gXX-leaf11 |
| macvrf1101 | MAC-VRF | ethernet-1-2 | lag interface with "ethernet-1-2" on device "gXX-leaf12", "ethernet-1-2" on device "gXX-leaf13" | 1101 | gXX-leaf11 |
| macvrf1101 | MAC-VRF | irb0 | irb | | gXX-leaf11 |
| ipvrf1201 | IP-VRF | irb0 | irb | | gXX-leaf12 |
| macvrf11 | MAC-VRF | ethernet-1-2 | lag interface with "ethernet-1-2" on device "gXX-leaf11", "ethernet-1-2" on device "gXX-leaf13" | 1 | gXX-leaf12 |
| macvrf1101 | MAC-VRF | ethernet-1-2 | lag interface with "ethernet-1-2" on device "gXX-leaf11", "ethernet-1-2" on device "gXX-leaf13" | 1101 | gXX-leaf12 |
| macvrf1101 | MAC-VRF | irb0 | irb | | gXX-leaf12 |
| ipvrf1201 | IP-VRF | irb0 | irb | | gXX-leaf13 |
| macvrf11 | MAC-VRF | ethernet-1-2 | lag interface with "ethernet-1-2" on device "gXX-leaf11", "ethernet-1-2" on device "gXX-leaf12" | 1 | gXX-leaf13 |
| macvrf11 | MAC-VRF | ethernet-1-3 | interface | 1 | gXX-leaf13 |
| macvrf1101 | MAC-VRF | ethernet-1-2 | lag interface with "ethernet-1-2" on device "gXX-leaf11", "ethernet-1-2" on device "gXX-leaf12" | 1101 | gXX-leaf13 |
| macvrf1101 | MAC-VRF | ethernet-1-3 | interface | 1101 | gXX-leaf13 |
| macvrf1101 | MAC-VRF | irb0 | irb | | gXX-leaf13 |

## Summary

Congratulations on completing the activity! By working through these tasks, you have successfully created an automated inventory report using Ansible and Nokia EDA. Here is a breakdown of what you have learned:

* You learned how to configure an Ansible inventory with specific variables to target the Nokia EDA API.
* You learned how to use the Nokia EDA Ansible Collection to generate a temporary access token and how to query specific network services and interfaces independently using EDA modules, gathering raw JSON data representing the fabric's state.
* You learned how to take complex, disconnected JSON responses and parse them into a flat, correlated format.

We hope you found this information useful and learned how to use Ansible Collections provided by Nokia EDA.

Well done!

[^1]: Want to learn more about Bridge Domains? Check out the [Bridge Domains](../beginner/bridge-domains.md) activity we prepared for you in this series.
