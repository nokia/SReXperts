# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import yaml
from pysros.management import connect


def read_yaml_file(file_path):
    with open(file_path, "r") as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as error:
            raise SystemExit(error) from error
    return data


def main():

    connection_object = connect(
        host="clab-srexperts-pe4",
        username="",
        password="",
        hostkey_verify=False,
    )

    vprn_path = "/nokia-conf:configure/service"

    config = read_yaml_file("vprn.yaml")

    vprn_payload = {
        "vprn": {
            "service-name": config["service-name"],
            "admin-state": "enable",
            "service-id": config["service-id"],
            "customer": config["customer"],
            "interface": {
                "interface-name": config["interface-name"],
                "admin-state": "enable",
                "ipv4": {
                    "primary": {
                        "address": config["ipv4-address"],
                        "prefix-length": config["ipv4-prefix-length"],
                    }
                },
                "sap": {"sap-id": config["sap-id"]},
            },
        }
    }

    # print(vprn_payload)

    connection_object.candidate.set(vprn_path, vprn_payload)


if __name__ == "__main__":
    main()
