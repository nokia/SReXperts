#!/usr/bin/env python3

### pysros-configure-bgp.py
#   Copyright 2023 Nokia
###

"""Example to show how to configure BGP peering and policies based on PeeringDB and IRR queries """

# Import the required libraries
import sys
import os
import typing
import requests
import json
import logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

from pysros.management import connect

# Import the exceptions so they can be caught on error.
from pysros.exceptions import ModelProcessingError

# Global credentials dictionary for the purposes of this example.  Global variables
# discouraged in operational applications.
creds = {"username": "admin", "password": "admin"}


def query_peeringdb(
    asn: int, ix: str
) -> typing.Tuple[typing.Optional[str], typing.Optional[str], typing.Optional[str]]:
    """
    Lookup ASN in PeeringDB and return ipv4,ipv6 peering IPs at given IX
    """

    url = f"https://www.peeringdb.com/api/netixlan?asn={asn}&name__contains={ix.replace(' ','%20')}"
    logging.info(f"PeeringDB query: {url}")
    resp = requests.get(url=url)
    pdb_json = json.loads(resp.text)
    print(pdb_json)
    if "data" in pdb_json and pdb_json["data"]:
        site = pdb_json["data"][0]
        return (site["name"], site["ipaddr4"], site["ipaddr6"])
    return (None, None, None)


def get_prefixlist(asn: int):
    """
    Retrieve list of prefixes registered in IRR for the given AS
    """
    url = f"https://irrexplorer.nlnog.net/api/prefixes/asn/AS{asn}"
    logging.info(f"irrexplorer query: {url}")
    resp = requests.get(url=url)
    logging.info(f"irrexplorer reply: {resp.text}")
    pfl_json = json.loads(resp.text)
    # Could use bgpOrigins (AS list) too
    source = (
        pfl_json["directOrigin"]
        if "directOrigin" in pfl_json and pfl_json["directOrigin"]
        else pfl_json["overlaps"]
    )
    return [i["prefix"] for i in source if i["goodnessOverall"] >= 1]


def add_peers(*, connection, peers):
    """Generate the configuration for each BGP peer, configure it"""
    print("Adding BGP peers...")
    for peer in peers:
        try:
            for a in ("ip4", "ip6"):
                if peer[a]:
                    # Configure the full prefix list in 1 Netconf transaction, per address type
                    # Composite key ip-prefix + type
                    pfx_list = {
                        (p, "exact"): {}
                        for p in peer["prefixlist"]
                        if (a == "ip4" and "." in p) or (a == "ip6" and ":" in p)
                    }
                    connection.candidate.set(
                        f"/nokia-conf:configure/policy-options/prefix-list[name=rpki-pfx-{peer['as']}-{a}]",
                        {"prefix": pfx_list} if pfx_list else {},
                    )

                    # Create a corresponding import policy
                    policy_name = f"import-rpki-{peer['as']}-{a}"
                    policy = {
                        "nokia-conf:entry": {
                            10: {
                                "from": {"prefix-list": [f"rpki-pfx-{peer['as']}-{a}"]},
                                "action": {"action-type": "accept"},
                            }
                        },
                        "nokia-conf:default-action": {
                            "action-type": "reject"  # Or accept with lower preference, optionally adding a community
                        },
                    }
                    connection.candidate.set(
                        f"/nokia-conf:configure/policy-options/policy-statement[name={policy_name}]",
                        policy,
                    )

                    # Create neighbor
                    neighbor = {
                        "group": "ebgp",
                        "peer-as": peer["as"],
                        "description": f"Provisioned by pySROS - {peer['desc']}",
                        "import": {"policy": [policy_name]},
                    }
                    connection.candidate.set(
                        f"/nokia-conf:configure/router[router-name=Base]/bgp/neighbor[ip-address={peer[a]}]",
                        neighbor,
                    )
        except Exception as error:  # pylint: disable=broad-except
            print("Failed to create", peer, "Error:", error)
            continue


def get_connection(host=None, credentials=None):
    """Function definition to obtain a Connection object to a specific SR OS device
    and access the model-driven information."""

    # The try statement coupled with the except statements allow an operation(s) to be
    # attempted and specific error conditions handled gracefully
    try:
        connection_object = connect(
            host=host,
            username=credentials["username"],
            password=credentials["password"],
            hostkey_verify=False,
        )

        # Confirm to the user that the connection establishment completed successfully
        print("Connection established successfully")

        # Return the Connection object that we created
        return connection_object

    # This first exception is described in the pysros.management.connect method
    # and references errors that occur during the creation of the Connection object.
    # If the provided exception is raised during the execution of the connect method
    # the information provided in that exception is loaded into the e1 variable for use
    except RuntimeError as error1:
        print(
            "Failed to connect during the creation of the Connection object.  Error:",
            error1,
        )
        sys.exit(101)

    # This second exception is described in the pysros.management.connect method
    # and references errors that occur whilst compiling the YANG modules that have been
    # obtained into a model-driven schema.
    # If the provided exception is raised during the execution of the connect method the
    # information provided in that exception is loaded into the e2 variable for use.
    except ModelProcessingError as error2:
        print("Failed to create model-driven schema.  Error:", error2)
        sys.exit(102)

    # This last exception is a general exception provided in Python
    # If any other unhandled specific exception is thrown the information provided in
    # that exception is loaded into the e3 variable for use
    except Exception as error3:  # pylint: disable=broad-except
        print("Failed to connect.  Error:", error3)
        sys.exit(103)


def main():
    """Provide a list of hosts to add the users too and this main function connects
    to each device in turn and adds the user."""
    inventory_hosts = [
        "clab-IXP-Peering-sros"
    ]  # Hardcoded to SR OS host from 1st topology...
    peer_asns = [os.getenv("AS2") or 24875]
    for asn in peer_asns:
        (site, ip4, ip6) = query_peeringdb(asn=asn, ix=os.getenv("IXP") or "AMS-IX")
        prefixlist = get_prefixlist(asn=asn)
        for host in inventory_hosts:
            try:
                connection_object = get_connection(host, creds)
                add_peers(
                    connection=connection_object,
                    peers=[
                        {
                            "as": int(asn),
                            "ip4": ip4,
                            "ip6": ip6,
                            "desc": site,
                            "prefixlist": prefixlist,
                        }
                    ],
                )
            except Exception:  # pylint: disable=broad-except
                continue


if __name__ == "__main__":
    main()
