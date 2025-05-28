# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import sys, json
import requests
from requests.auth import HTTPBasicAuth
import urllib3

urllib3.disable_warnings()

# Stub class to be used during interactive script execution
class ScriptStub(object):
    def log(self, message="", obj=None):
        if message:
            print(message)

        if obj:
            print(obj)

    def log_error(self, message="", obj=None):
        self.log(message=message, obj=obj)

    def log_info(self, message="", obj=None):
        self.log(message=message, obj=obj)

# Swap the classes
try:
    # We're inside the Netbox Environment
    from extras.scripts import Script as NetboxScriptCls
    from ipam.models import IPAddress
    from dcim.models import Interface

    ScriptCls = NetboxScriptCls
except ImportError:
    # We're not inside the Netbox Environment
    ScriptCls = ScriptStub

class NetboxNSPICM(ScriptCls):
    class Meta():
        name = "Netbox NSP ICM"
        description = "Script to sync Netbox interface configuration with NSP ICM Intents"

    def get_port_inventory(self, host, token, port):
        pass

    def run(self, data, commit=True):
        # I've done the authentication bit for you, it's boring anyway :)
        r = requests.post(f"https://{data.get('nsp_host')}/rest-gateway/rest/api/v1/auth/token",
                        data={"grant_type": "client_credentials"},
                        auth=HTTPBasicAuth(data.get("nsp_username"), data.get("nsp_password")),
                        verify=False
                        )

        if r.status_code > 200:
            self.log_error(message=f"Unable to authenticate with error: {r.json}")

        token = r.json()["access_token"]

        self.log_info(message=f"Authenticated with NSP! Status Code:{r.status_code}")

        # Hacker: you have the data, you have NSP, you have all you need.
        # - Find the interface in NSP inventory
        # - determine if there is an existing intent
        # - - if yes, update it and deploy
        # - - if not, create it and deploy
        
        pass

if __name__ == '__main__':
    # run the script interactively.
    if len(sys.argv) < 2:
        exit('Not enough arguments for interactive call - please pass in JSON data')

    script = NetboxNSPICM()
    p_data = json.load(open(sys.argv[1]))
    script.run(p_data)