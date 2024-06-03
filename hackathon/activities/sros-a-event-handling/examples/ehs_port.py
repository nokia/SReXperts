# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.ehs import get_event
from pysros.management import connect

PORTS_TO_CONFIGS = {
    "1/1/c7/1": {
        "interface_name": "p1_2",
        "ipv4_address": ("10.64.60.1", 31),
        "ipv6_address": ("fd00:fde8:0:1:1:11:222:1", 127),
    }
}


def main():
    """The main procedure.  The execution starts here."""
    connection = connect(
        host="local connection only - unused",
        username="local connection only - unused",
    )

    trigger_event = get_event()
    if not trigger_event:
        return
    if trigger_event.appid == "SNMP" and trigger_event.eventid == 2005:
        # This event signifies a linkUp
        # This is likely triggered by the operator changing a port configuration.
        # Operator accounts have access only to the "/configure port" tree, L3 interface and protocols must still be added.

        # from the eventparameters object we can learn which port was brought up
        # print(trigger_event.eventparameters)
        # EventParams({'ifOperStatus': 'up', 'ifDescr': '1/1/c7, IP interface, "QSFP28 Connector"', 'ifIndex': '1/1/c7', 'ifAdminStatus': 'up'})

        if (
            trigger_event.eventparameters["ifIndex"]
            not in PORTS_TO_CONFIGS.keys()
        ):
            print(
                "%s not recognized. Exiting."
                % trigger_event.eventparameters["ifIndex"]
            )
            return

        new_interface = PORTS_TO_CONFIGS[
            trigger_event.eventparameters["ifIndex"]
        ]["interface_name"]
        ipv4_address, ipv4_pfxlen = PORTS_TO_CONFIGS[
            trigger_event.eventparameters["ifIndex"]
        ]["ipv4_address"]
        ipv6_address, ipv6_pfxlen = PORTS_TO_CONFIGS[
            trigger_event.eventparameters["ifIndex"]
        ]["ipv6_address"]

        # based on configured data in the script (PORTS_TO_CONFIGS), create a router interface
        path = (
            "/nokia-conf:configure/router[router-name='Base']/interface[interface-name='%s']"
            % new_interface
        )
        payload = {
            "interface-name": new_interface,
            "port": trigger_event.eventparameters["ifIndex"],
            "ipv4": {
                "primary": {
                    "prefix-length": ipv4_pfxlen,
                    "address": ipv4_address,
                }
            },
            "ipv6": {
                "forward-ipv4-packets": True,
                "address": {
                    "prefix-length": ipv6_pfxlen,
                    "ipv6-address": ipv6_address,
                },
            },
        }
        connection.candidate.set(path, payload, commit=False)
        print(
            "Created interface %s in candidate - waiting to commit."
            % new_interface
        )

        # having both the new_interface and new_ip_address found, we can configure the routing protocols
        # isis (and bgp but not for this demo) to make use of this newly configured interface
        path = (
            "/nokia-conf:configure/router[router-name='Base']/isis[isis-instance='0']/interface[interface-name='%s']"
            % new_interface
        )
        payload = {
            "interface-type": "point-to-point",
        }
        connection.candidate.set(path, payload, commit=False)
        print(
            "Added interface %s to ISIS 0 - waiting to commit." % new_interface
        )

        path = "/nokia-conf:configure/router[router-name='Base']/mpls"
        payload = {
            "interface": {new_interface: {"interface-name": new_interface}}
        }
        connection.candidate.set(path, payload, commit=False)
        path = "/nokia-conf:configure/router[router-name='Base']/rsvp"
        payload = {
            "interface": {new_interface: {"interface-name": new_interface}}
        }
        print(
            "Comparison output:\n%s"
            % connection.candidate.compare(output_format="md-cli")
        )
        connection.candidate.set(path, payload, commit=True)
        print("Added interface %s to MPLS - committing." % new_interface)


if __name__ == "__main__":
    main()
