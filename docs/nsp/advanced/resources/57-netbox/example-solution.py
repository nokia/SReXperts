# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import sys, json
from ipaddress import ip_address

import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings()


class ScriptStub(object):
    """Stub class to be used during interactive script execution.
    
    This class provides basic logging functionality when running the script outside
    the Netbox environment. It mimics the logging interface of the Netbox Script class.
    """
    def log(self, message="", obj=None):
        """Log a message and optionally an object.
        
        Args:
            message (str, optional): Message to log. Defaults to "".
            obj (any, optional): Object to log. Defaults to None.
        """
        if message:
            print(message)

        if obj:
            print(obj)

    def log_error(self, message="", obj=None):
        """Log an error message and optionally an object.
        
        Args:
            message (str, optional): Error message to log. Defaults to "".
            obj (any, optional): Object to log. Defaults to None.
        """
        self.log(message=message, obj=obj)

    def log_info(self, message="", obj=None):
        """Log an info message and optionally an object.
        
        Args:
            message (str, optional): Info message to log. Defaults to "".
            obj (any, optional): Object to log. Defaults to None.
        """
        self.log(message=message, obj=obj)


# Swap the classes if we're not inside the Netbox Script environment.
try:
    # We're inside the Netbox Environment
    from extras.scripts import Script as NetboxScriptCls
    from ipam.models import IPAddress
    from dcim.models import Interface

    ScriptCls = NetboxScriptCls
except ImportError:
    ScriptCls = ScriptStub


class NetboxNSPICM(ScriptCls):
    """Netbox script to sync interface configuration with NSP ICM Intents.
    
    This script handles the synchronization of Netbox interface configurations with
    Nokia Network Services Platform (NSP) Intent Configuration Management (ICM).
    It manages port connector and ethernet intents based on Netbox interface changes.
    """

    class Meta:
        """Metadata for the Netbox script.
        
        This class defines the script's name and description as it appears in the Netbox UI.
        """
        name = "Netbox NSP ICM"
        description = "Script to sync Netbox interface configuration with NSP ICM Intents"

    def get_device_system_ip(self, device_name):
        """Get the system IP address for a device.
        
        Args:
            device_name (str): Name of the device to get system IP for.
            
        Returns:
            str: The system IP address (ipv6) without subnet mask.
        """
        i = [i for i in list(IPAddress.objects.filter(interface__device__name=device_name, interface__name="system")) if '.' not in str(i.address)]

        return str(i[0]).split("/")[0] #only return IP, not mask.


    def execute_port_deployment(self, data, token, op_name, template_name, **kwargs):
        """Execute a port deployment operation in NSP ICM.
        
        This method handles creating, updating, or deleting port deployments in NSP ICM.
        The payload format varies based on the operation type.
        
        Args:
            data (dict): Configuration data containing NSP host and credentials.
            token (str): Authentication token for NSP API.
            op_name (str): Operation name ('create-deployment', 'update-deployment', or 'delete-deployment').
            template_name (str): Name of the template to use for deployment.
            **kwargs: Additional arguments:
                - target_data (str): JSON string containing deployment data (for create/update).
                - target (dict): Target configuration containing 'target' and 'target-identifier-value' (for create/update).
                - target_path (str): Path to the deployment to delete (for delete).
                
        Returns:
            dict: Response from NSP API if successful, None if failed.
        """
        payload = {"input": {"deployments": [{}]}}
        if op_name == "create-deployments" or op_name == "update-deployments":
            payload['input']['deployments'][0]['deployment-action'] = "deploy"
            payload['input']['deployments'][0]['template-name'] = template_name
            payload['input']['deployments'][0]['target-data'] = kwargs.get("target_data")
            payload['input']['deployments'][0]['targets'] = [kwargs.get("target")]

        if op_name == "delete-deployments":
            # NOOP because there's an issue in deleting intents
            return
            # payload['input']['delete-option'] = 'network-and-nsp'
            # payload['input']['deployments'][0] = {
            #     "deployment": f"/nsp-icm:icm/deployments/deployment[template-name='{template_name}'][target='{kwargs.get('target_path')}'][target-identifier-value='{kwargs.get('target_data')}']"
            # }

        response = requests.post(
            f"https://{data.get('nsp_host')}/restconf/operations/nsp-icm:{op_name}",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            verify=False
        )

        if response.status_code > 200:
            self.log_error(message=f"Error executing deployment [{op_name}][{template_name}] deployment: {response.json()}")
            return None
        else:
            self.log_info(message=f"Success executing deployment [{op_name}][{template_name}]")
            return response.json()


    def get_port_inventory(self, host, token, ne_id, port):
        """Get port inventory information from NSP.
        
        Args:
            host (str): NSP host address.
            token (str): Authentication token for NSP API.
            port (str): Port name to get inventory for.
            
        Returns:
            list: List of deployment data for the port, empty list if not found or error.
        """
        find_query = {
            "input": {
                "xpath-filter": f"/nsp-equipment:network/network-element[ne-id='{ne_id}']/hardware-component/port/equipment-extension-port:extension/deployment[target-identifier-value='{port}']"
            }
        }

        find_r = requests.post(f"https://{host}/restconf/operations/nsp-inventory:find",
                               headers={"Authorization": f"Bearer {token}"},
                               json=find_query,
                               verify=False
                               )
        if find_r.status_code > 200:
            return []

        if find_r.json()["nsp-inventory:output"]["total-count"] == 0:
            return []

        return find_r.json()["nsp-inventory:output"]["data"]

    def get_ip_interface_inventory(self, host, token, ne_id, id):
        """Get IP interface inventory information from NSP.
        
        Args:
            host (str): NSP host address.
            token (str): Authentication token for NSP API.
            ne_id (str): Network element ID.
            id (str): Interface id.
        """
        # the format we'll use for the interface name is `port126` ~ `port<netbox_id_number>`
        find_query = {
            "input": {
                "xpath-filter": f"/nsp-equipment:network/network-element[ne-id='{ne_id}']/equipment-extension-ne:extension/deployment[target-identifier-value='port{id}']"
            }
        }

        find_r = requests.post(f"https://{host}/restconf/operations/nsp-inventory:find",
                               headers={"Authorization": f"Bearer {token}"},
                               json=find_query,
                               verify=False
                               )
        if find_r.status_code > 200:
            return []

        if find_r.json()["nsp-inventory:output"]["total-count"] == 0:
            return []

        return find_r.json()["nsp-inventory:output"]["data"]

    def determine_intent_action(self, nb_interface_exists, intent_exists):
        """Determine the action to take based on Netbox interface and intent existence.
        
        Args:
            nb_interface_exists (bool): Whether the interface exists in Netbox.
            intent_exists (bool): Whether the intent exists in NSP.
            
        Returns:
            str: One of 'create-deployments', 'update-deployments', or 'delete-deployments'.
                 Returns None for unexpected states.
        """
        if not intent_exists and nb_interface_exists:
            return "create-deployments"
        elif intent_exists and nb_interface_exists:
            return "update-deployments"
        elif intent_exists and not nb_interface_exists:
            return "delete-deployments"
        else:
            # This case shouldn't happen in normal operation
            self.log_error(message="No action required - no intent and no netbox interface exists.")
            return "none" # shouldn't trigger a deployment change

    def run(self, data, commit=True):
        """Main execution method for the script.
        
        This method handles the synchronization of Netbox interface configurations with NSP ICM.
        It manages port connector, ethernet, and network interface intents based on the state of the Netbox interface.
        
        Args:
            data (dict): Configuration data containing interface details and NSP credentials.
            commit (bool, optional): Whether to commit changes. Defaults to True.
            
        Returns:
            None
        """
        r = requests.post(f"https://{data.get('nsp_host')}/rest-gateway/rest/api/v1/auth/token",
                          data={"grant_type": "client_credentials"},
                          auth=HTTPBasicAuth(data.get("nsp_username"), data.get("nsp_password")),
                          verify=False
                          )

        if r.status_code > 200:
            self.log_error(message=f"Unable to authenticate with error: {r.json}")

        token = r.json()["access_token"]
        
        self.log_info(message=f"Authenticated with NSP! Status Code:{r.status_code}")

        # Get device system ipv6 which is the NE-ID.
        device_system_ip = self.get_device_system_ip(data.get('device').get('name'))

        # assume we're only dealing with 1 port connector per port
        port_name_ether = data.get("name")  # e.g 1/1/c1/1
        port_name_connector = "/".join(port_name_ether.split("/")[:3])  # e.g. 1/1/c1
        port_id = data.get('id')

        # Check existence in both systems
        self.log_info(message="[NSP] Getting connector inventory")
        connector_inventory = self.get_port_inventory(data.get('nsp_host'), token, device_system_ip, port_name_connector)
        self.log_info(message=f"[NSP] Found {len(connector_inventory)} Ports matching target.")

        self.log_info(message="[NSP] Getting ethernet inventory")
        ethernet_inventory = self.get_port_inventory(data.get('nsp_host'), token, device_system_ip, port_name_ether)
        self.log_info(message=f"[NSP] Found {len(ethernet_inventory)} Ethernet interfaces matching target.")

        self.log_info(message="[NSP] Getting network interface inventory")
        network_inventory = self.get_ip_interface_inventory(data.get('nsp_host'), token, device_system_ip, port_id)
        self.log_info(message=f"[NSP] Found {len(network_inventory)} IP Interfaces matching target.")

        # List with the interface in question
        # e.g. nb_interface_exists = [<Interface:id=89>]
        nb_interface_exists = list(Interface.objects.filter(id=data.get('id')))

        # Get IP addresses from Netbox
        # e.g. ip_addresses = ["192.0.11.2/31", "2001:db8:11::2/127"]
        ip_addresses = None
        if nb_interface_exists:
            ip_addresses = list(IPAddress.objects.filter(interface__id=data.get('id')))
            ip_addresses = [str(ip.address) for ip in ip_addresses]

        # Determine actions for each intent
        connector_action = self.determine_intent_action(bool(nb_interface_exists), bool(connector_inventory))
        ethernet_action = self.determine_intent_action(bool(nb_interface_exists), bool(ethernet_inventory))
        network_action = self.determine_intent_action(bool(nb_interface_exists), bool(network_inventory))

        # deployment data
        port_mode = "network"  # TODO: if len(connected_endpoints) > 0, network, else access
        port_state = "enable" if data.get("enabled") else "disable"
        port_mtu = data.get("mtu")

        # Handle connector intent
        if connector_action:
            if connector_action == "delete-deployments":
                result_connector = self.execute_port_deployment(
                    data, token, connector_action, "NSP-Activity-57-Port-Connector",
                    target_path=connector_inventory[0].get("target"),
                    target_data=port_name_connector
                )
                self.log_info(message=f"[NSP] Connector Deployment Delete: {result_connector}")
            else:
                result_connector = self.execute_port_deployment(
                    data, token, connector_action, "NSP-Activity-57-Port-Connector",
                    target_data=f"{{\"port\":{{\"admin-state\":\"{port_state}\",\"connector\":{{\"breakout\":\"c1-100g\"}}}}}}",
                    target={
                        "target": f"/nsp-equipment:network/network-element[ne-id='{device_system_ip}']/hardware-component/port[component-id='shelf=1/cardSlot=1/card=1/mdaSlot=1/mda=1/port={port_name_connector}']",
                        "target-identifier-value": port_name_connector
                    }
                )
                self.log_info(message=f"[NSP] Connector Deployment: {result_connector}")

        # Handle ethernet intent
        if ethernet_action:
            if ethernet_action == "delete-deployments":
                result_eth = self.execute_port_deployment(
                    data, token, ethernet_action, "NSP-Activity-57-Port-Ethernet",
                    target_path=ethernet_inventory[0].get("target"),
                    target_data=port_name_ether
                )
                self.log_info(message=f"[NSP] Eth Deployment Delete: {result_eth}")
            else:
                result_eth = self.execute_port_deployment(
                    data, token, ethernet_action, "NSP-Activity-57-Port-Ethernet",
                    target_data=f"{{\"port\":{{\"admin-state\":\"{port_state}\",\"ethernet\":{{\"mode\":\"{port_mode}\",\"mtu\":\"{port_mtu}\",\"encap-type\":\"null\"}}}}}}",
                    target={
                        'target': f"/nsp-equipment:network/network-element[ne-id='{device_system_ip}']/hardware-component/port[component-id='shelf=1/cardSlot=1/card=1/mdaSlot=1/mda=1/port={port_name_connector}/breakout-port={port_name_ether}']",
                        "target-identifier-value": port_name_ether
                    }
                )
                self.log_info(message=f"[NSP] Ethernet Deployment: {result_eth}")

        # Handle network interface intent
        if network_action:
            if network_action == "delete-deployments":
                result_network = self.execute_port_deployment(
                    data, token, network_action, "NSP-Activity-57-Network-Interface",
                    target_path=network_inventory[0].get("target"),
                    target_data=f"port{port_id}"
                )
                self.log_info(message=f"[NSP] Interface Deployment Delete: {result_network}")
            else:
                # Only create/update network interface if we have IP addresses
                if ip_addresses:
                    ipv4 = [i for i in ip_addresses if "." in i][0].split("/") # split mask and IP
                    ipv6 = [i for i in ip_addresses if ":" in i][0].split("/")
                    result_network = self.execute_port_deployment(
                        data, token, network_action, "NSP-Activity-57-Network-Interface",
                        target_data=f"{{\"interface\":{{\"admin-state\":\"{port_state}\",\"port-binding\":\"port\",\"port\":\"{port_name_ether}\",\"ipv4\":{{\"primary\":{{\"address\":\"{ipv4[0]}\",\"prefix-length\":{ipv4[1]}}}}},\"ipv6\":{{\"address\":[{{\"ipv6-address\":\"{ipv6[0]}\",\"prefix-length\":{ipv6[1]}}}]}}}}}}",
                        target={
                            'target': f"/nsp-equipment:network/network-element[ne-id='{device_system_ip}']",
                            "target-identifier-value": f"port{port_id}"
                        }
                    )
                    self.log_info(message=f"[NSP] Interface Deployment: {result_network}")

        return None


if __name__ == '__main__':
    # run the script interactively.
    if len(sys.argv) < 2:
        exit('Not enough arguments for interactive call - please pass in JSON data')

    script = NetboxNSPICM()
    p_data = json.load(open(sys.argv[1]))
    try:
        script.run(p_data)
    except NameError as e:
        if "IPAddress" in str(e) or "Interface" in str(e) or "Device" in str(e):
            print("### Note ### Netbox ORM calls such as Interface.objects.filter() can't be run interactively, stub them for "
                  "testing instead.")
            raise(e)
