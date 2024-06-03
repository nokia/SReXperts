# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.management import connect

def main():

    connection_object = connect(
        host="clab-srexperts-pe4",
        username="",
        password="",
        hostkey_verify=False,
    )

    vprn_path = "/nokia-conf:configure/service"
    vprn_payload = {
        "vprn": {
                "service-name": "SERVICE-NAME",
                "admin-state": "enable",
                "service-id": 1111,
                "customer": "1",
                "interface": {
                        "interface-name": "INTERFACE-NAME",
                        "admin-state": "enable",
                        "ipv4": {
                            "primary": {
                                "address": "192.168.6.50",
                                "prefix-length": 24,
                            }
                        },
                        "sap":  {"sap-id": "1/1/c6/1:1111"},
                },
        }
    }
    connection_object.candidate.set(vprn_path, vprn_payload)

if __name__ == "__main__":
    main()
