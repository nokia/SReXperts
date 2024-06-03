# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""Example implementation for the second leg of the automated-configuration
usecase for the Hackathon in SReXperts EMEA 2024.

Tested on: SR OS 24.3.R2-1
"""

import argparse
import ipaddress
import json
import os
import subprocess
import sys

import requests
from dotenv import find_dotenv, load_dotenv
from pysros.management import connect


def get_connection(host=None, username=None, password=None, port=830):
    """Function definition to obtain a Connection object to a specific
    SR OS device and access the model-driven information.
    :parameter host: The hostname or IP address of the SR OS node.
    :type host: str
    :paramater credentials: The username and password to connect
                            to the SR OS node.
    :type credentials: dict
    :parameter port: The TCP port for the connection to the SR OS node.
    :type port: int
    :returns: Connection object for the SR OS node.
    :rtype: :py:class:`pysros.management.Connection`
    """
    try:
        connection_object = connect(
            host=host,
            username=username,
            password=password,
            port=port,
            hostkey_verify=False,
        )
    except RuntimeError as error1:
        print("Failed to connect.  Error:", error1)
        sys.exit(-1)
    return connection_object


def bgpq4(as_or_as_set):
    """Function wrapping either a subprocess call to the Linux `bgpq4` utility
    or a surrogate load of a provided file that contains example generated and
    packaged with this usecase for situations where the `bgpq4` utility may
    not be working.

    It takes as input an AS number or an as-set name and outputs a prefix list
    in a JSON format that corresponds to the that AS or that as-set.
    """
    bgpq4_result = ""
    with open("bgpq4_result.json", "r+") as bgpq4_resultfile:
        bgpq4_result = json.loads(bgpq4_resultfile.read())

    # as bgpq4 uses TCP 43 communication and that may be blocked on a firewall
    # level, a usable output is available in the `bgpq4_result.json` as a
    # workaround. You may uncomment the following line to retrieve live data.
    # bgpq4_result = subprocess.run(["bgpq4", "-j", as_or_as_set], capture_output=True).stdout

    bgpq4_result = json.loads(bgpq4_result)
    for pfx_list_name, prefixes in bgpq4_result.items():
        cfg_path = f'/nokia-conf:configure/filter/match-list/ip-prefix-list[prefix-list-name="{pfx_list_name}"]'
        cfg_payload = {"prefix-list-name": pfx_list_name, "prefix": {}}
        for prefix in prefixes:
            cfg_payload["prefix"][prefix["prefix"]] = {
                "ip-prefix": prefix["prefix"]
            }
    return cfg_path, cfg_payload


def whois(as_or_as_set):
    """Function wrapping either a subprocess call to the Linux `whois` utility
    or a surrogate load of a provided file that contains example data generated
    and packaged with this usecase for situations where the `whois` utility
    may not be working.

    It takes as input an AS number or an as-set name and outputs a prefix list
    in a JSON format that corresponds to the that AS or that as-set.
    """
    whois_result = ""
    with open("whois_result.txt", "r+") as whois_resultfile:
        whois_result = whois_resultfile.read()

    # as whois uses TCP 43 communication and that may be blocked on a firewall
    # level, a usable output is available in the `whois_result.txt` as a
    # workaround. You may uncomment the following lines to retrieve live data.
    # whois_result = subprocess.run(
    #    ["whois", "-h", "whois.radb.net", as_or_as_set],
    #    capture_output=True
    # ).stdout.decode("utf-8")

    whois_result = filter(None, whois_result.split("\n"))
    whois_result_dict = {}
    for key, value in [i.split(":", 1) for i in whois_result]:
        value = value.lstrip()
        if key not in whois_result_dict:
            whois_result_dict[key] = value
        elif isinstance(whois_result_dict[key], list):
            whois_result_dict[key].append(value)
        else:
            whois_result_dict[key] = [whois_result_dict[key]]
            whois_result_dict[key].append(value)
    return whois_result_dict


def create_routing_policy(conn, as_set, members):
    """Function that takes as input a pySROS connection object, a name of an
    as-set and the members that are part of this as-set.

    With this input, the function creates a community in the SR OS device
    represented by the conn object, and adds it to a routing policy statement.
    """
    path = "/nokia-conf:configure/policy-options"
    payload = {
        "community": {
            as_set: {
                "name": as_set,
                "member": {
                    member.replace("AS", ""): {
                        "member": member.replace("AS", "")
                    }
                    for member in members
                },
            }
        },
        "policy-statement": {
            f"BGP-{as_set}": {
                "name": f"BGP-{as_set}",
                "entry": {
                    10: {
                        "entry-id": 10,
                        "from": {"community": {"name": as_set}},
                        "action": {"action-type": "accept"},
                    }
                },
            }
        },
    }
    conn.candidate.set(path, payload)
    return f"BGP-{as_set}"


def setup_bgp_peering(conn, peer_address, peer_as, policy):
    """Function that takes as input a pySROS connection object, an IP address
    and AS number that are intended to be used as a configured BGP neighbor
    and a routing policy name.

    With this input, the function creates a BGP neighbor in the SR OS device
    represented by the conn object with the routing policy applied.
    """
    path = '/nokia-conf:configure/router[router-name="Base"]/bgp'
    payload = {
        "neighbor": {
            peer_address: {
                "ip-address": peer_address,
                "group": "AMS-IX",
                "peer-as": peer_as,
                "family": {"ipv6": True},
                "import": {"policy": [policy]},
                "origin-validation": {"ipv6": True},
            }
        },
        "group": {"AMS-IX": {"group-name": "AMS-IX"}},
    }
    conn.candidate.set(path, payload)


def get_as_ip_rpki_information(query_as):
    """Function that, using an AS number as input, queries the Hurricane
    Electric BGP Super Looking Glass to retrieve originated prefixes and
    verification as to whether or not those prefixes have rPKI information
    associated with them.

    The function returns a dictionary where the key is the input ASN and
    the value is a set of prefixes that have valid rPKI information available
    according to information available in the Looking Glass.
    """
    base_url = "https://bgp.he.net/super-lg/report/api/v1/"

    originated_prefixes_url = "prefixes/originated/"
    rpki_validation = "rpki/validate/"

    originated_prefixes = json.loads(
        requests.get(
            base_url + originated_prefixes_url + str(query_as)
        ).content
    )["prefixes"]
    payload = {"prefixes": []}
    for prefix in originated_prefixes:
        if ipaddress.ip_network(prefix["Prefix"]).version == 6:
            payload["prefixes"].append(prefix["Prefix"])

    validated_prefixes = json.loads(
        requests.post(
            base_url + rpki_validation + str(query_as), data=payload
        ).content
    )["response"]

    validated_prefix_set_for_as = set()
    for prefix in validated_prefixes:
        if prefix["Status"] == "valid":
            validated_prefix_set_for_as.add(prefix["Prefix"])
    return {query_as: frozenset(validated_prefix_set_for_as)}


def static_origin_validation(conn, as_ip_info):
    """Function that takes as input a pySROS connection object, and a
    dictionary that has as key an AS number and as value a set of ip
    prefixes including their subnet length.

    This is used to configure static origin-validation entries in the
    SR OS device that is attached to the other side of the connection object.
    """
    path = '/nokia-conf:configure/router[router-name="Base"]/origin-validation'
    payload = {"static-entry": {}}
    for key_as, value in as_ip_info.items():
        for ip_address in value:
            prefix, subnet_length = ip_address.split("/")
            payload["static-entry"][
                f"{prefix}/{subnet_length}", int(subnet_length), key_as
            ] = {
                "ip-prefix": f"{prefix}/{subnet_length}",
                "upto": int(subnet_length),
                "origin-as": key_as,
                "valid": True,
            }
    conn.candidate.set(path, payload)


def main():
    """The main procedure.  The execution starts here.

    This script is made up of two tasks, addressable using the `task` CLI
    flag. The first task creates a BGP peering while the second creates static
    rPKI entries.

    As further inputs, the script accepts an AS number and peering location,
    as well as a list of SR OS routes targeted for configuration modifications.
    """
    load_dotenv(find_dotenv())  # Load the .env file.

    # Fetch variables from the .env file.
    username_var = os.getenv("ACCOUNT_USERNAME")
    password_var = os.getenv("ACCOUNT_PASSWORD")

    parser = argparse.ArgumentParser(
        prog="peeringdb_rpki.py",
        description="Using input parameters, perform either "
        + "one of the tasks of the automated configuration "
        + "usecase in SReXperts EMEA 2024.\nSpecify a target"
        + " SR OS node, an AS number, an IXP location and a "
        + " task number to execute.",
    )
    parser.add_argument("-t", "--targets", required=True)
    parser.add_argument("-l", "--location", required=True)
    parser.add_argument("-as_number", "-as", required=True)
    parser.add_argument("-task", required=False, default=500)
    args = parser.parse_args()

    for target in args.targets.split(","):
        connection_object = get_connection(
            host=target, username=username_var, password=password_var
        )
        task = int(args.task)
        if task == 1:
            with open("asn_info_result.json", "r") as asn_info_resultfile:
                asn_info = json.loads(asn_info_resultfile.read())
            # Unauthenticated requests get throttled, above statement
            # is used in lieu of live data to avoid this and to not be
            # disruptive. You can uncomment the lines below to work with live
            # data instead
            # peeringdb_api = f"https://www.peeringdb.com/api/net?asn={args.as_number}"
            # asn_info = json.loads(requests.get(peeringdb_api).content)

            net_id = asn_info["data"][0]["id"]

            with open(f"net_id_{net_id}.json", "r") as net_info_backup:
                net_info = json.loads(net_info_backup.read())["data"][0]
            # Unauthenticated requests get throttled, above statement
            # is used in lieu of live data to avoid this and to not be
            # disruptive. You can uncomment the lines below to work with live
            # data instead
            # peeringdb_api = f"https://www.peeringdb.com/api/net/{net_id}"
            # net_info = json.loads(requests.get(peeringdb_api).content)["data"][0]
            peer_asn = net_info["asn"]
            peer_ip = "NONE_FOUND"
            for net_info_entry in net_info["netixlan_set"]:
                if net_info_entry["name"] == "AMS-IX":
                    peer_ip = net_info_entry["ipaddr6"]
                    break

            irr_as_set = asn_info["data"][0]["irr_as_set"]
            as_set_info = whois(irr_as_set)["members"]
            prefix_info_cfg_path, prefix_info_cfg_payload = bgpq4(irr_as_set)

            plcy = create_routing_policy(
                connection_object, irr_as_set, as_set_info
            )
            connection_object.candidate.set(
                prefix_info_cfg_path, prefix_info_cfg_payload
            )
            peer_ip = "fd00:fc00:0:51::3"
            peer_asn = "64599"
            setup_bgp_peering(connection_object, peer_ip, int(peer_asn), plcy)
        elif task == 2:
            origin_as_ips = get_as_ip_rpki_information(38016)
            static_origin_validation(connection_object, origin_as_ips)
        else:
            print("Nothing to do, neither task 1 nor task 2 were specified.")


if __name__ == "__main__":
    main()
