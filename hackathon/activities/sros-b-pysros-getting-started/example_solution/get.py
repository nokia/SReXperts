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

    data1 = connection_object.running.get(
        "/nokia-state:state/system/oper-name"
    )
    data2 = connection_object.running.get(
        "/nokia-conf:configure/service/vprn",
        filter={"service-name": "dci", "bgp-ipvpn": {}},
    )
    data3 = connection_object.running.get(
        "/nokia-conf:configure/service/vprn",
        filter={"service-name": "dci", "interface": {"interface-name": {}}},
    )
    data4 = connection_object.running.get(
        "/nokia-conf:configure/service/vprn",
        filter={
            "service-name": "dci",
            "interface": {"interface-name": "client04", "ipv4": {}},
        },
    )
    print(">>>You are connected to device:", data1)
    print("\n")
    print(">>>VPRN info bgp-ipvpn:", data2)
    print("\n")
    print(">>>VPRN info interface:", data3)
    print("\n")
    print(">>>VPRN info interface-ipv4:", data4)
    print("\n")


if __name__ == "__main__":
    main()
