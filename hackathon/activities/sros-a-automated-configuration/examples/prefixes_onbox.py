# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""Example implementation for the first leg of the automated-configuration
usecase for the Hackathon in SReXperts Americas 2024.

Consumes a list of prefixes stored in `prefixes.txt` and converts it into a
prefix-list configuration on the router. This version of the file runs locally
and requires a secondary component that regularly updates the `prefixes.txt`
file.

Tested on: SR OS 24.7.R1
"""

import json

from pysros.management import Empty, connect
from pysros.wrappers import Container, Leaf

# CRON configuration required:
"""
    configure {
        python {
            python-script "prefixes_onbox" {
                admin-state enable
                urls ["tftp://172.31.255.29/prefixes_onbox.py"]
                version python3
            }
        }
        system {
            cron {
                schedule "prefixes_onbox" owner "admin" {
                    admin-state enable
                    interval 60
                    type periodic
                    script-policy {
                        name "prefixes_onbox"
                        owner "admin"
                    }
                }
            }
            script-control {
                script-policy "prefixes_onbox" owner "admin" {
                    admin-state enable
                    results "/null"
                    python-script {
                        name "prefixes_onbox"
                    }
                }
            }
        }
    }
"""


def readPrefixes(filename):
    """Corresponding to the writeFile method in the prefixes_uploadonly script,
    this function takes as input a filename and converts the contents into a
    readymade list of IP prefixes to be used by the rest of the program.
    """
    with open(filename, "r+") as prefixes_file:
        prefixes = json.loads(prefixes_file.read())
    return prefixes


def data_to_matchlist_config(csv_data, match_list_name, connection_object):
    """Function that takes as input a comma-separated list of IP prefixes, a
    target name for an ip-prefix-list and a connection object.

    The connection object represents an MD SR OS router. The prefixes in the CSV
    data are used to populate an ip-prefix-list on the router using the specified
    name.

    There is no output for this function.
    """
    cfg_path = (
        '/nokia-conf:configure/filter/match-list/ip-prefix-list[prefix-list-name="%s"]'
        % match_list_name
    )
    cfg_payload = {"prefix-list-name": Leaf(match_list_name), "prefix": {}}
    for item in csv_data:
        cfg_payload["prefix"][item] = Container({"ip-prefix": Leaf(item)})
    connection_object.candidate.set(cfg_path, cfg_payload, method="replace")


def create_acl(acl_name, acl_id, entries, connection_object):
    """Function that takes a name and identifier as inputs, as well as a list
    of tuples that represent ACL entries and a connection object that
    represents an MD SR OS router.

    Through the connection object, an ACL is created on the router with the
    specified ACL name, identifier and the listed entries.

    There is no output for this function.
    """
    cfg_path = (
        '/nokia-conf:configure/filter/ip-filter[filter-name="%s"]' % acl_name
    )
    cfg_payload = {
        "filter-name": Leaf(acl_name),
        "filter-id": Leaf(acl_id),
        "entry": {},
    }
    for entry_id, entry_match_list, entry_action in entries:
        cfg_payload["entry"][entry_id] = Container(
            {
                "entry-id": entry_id,
                "match": Container(
                    {
                        "ip": Container(
                            {"ip-prefix-list": Leaf(entry_match_list)}
                        )
                    }
                ),
                "action": Container({entry_action: Leaf(Empty)}),
            }
        )
    connection_object.candidate.set(cfg_path, cfg_payload, method="replace")


def create_matchlist_and_acl(config_prefix, prefixes, connection_object):
    """Rather than the listed `create_acl` and `data_to_matchlist_config`
    functions, this function wraps both in one call to the MD SR OS router
    represented by the input connection_object.

    The function includes a view of what the configured result would be on the
    router for verification.

    Other than the configuration set on the router, there is no output.
    """
    # intended result
    """
    {
    'match-list': {
            'ip-prefix-list': {
                'maxmind_matchlist': {
                    'prefix-list-name': 'maxmind_matchlist',
                    'prefix': {
                        '2.125.160.216/29': {
                            'ip-prefix': '2.125.160.216/29'
                        },
                        '81.2.69.142/31': {
                            'ip-prefix': '81.2.69.142/31'
                        },
                        '81.2.69.144/28': {
                            'ip-prefix': '81.2.69.144/28'
                        },
                        '81.2.69.160/27': {
                            'ip-prefix': '81.2.69.160/27'
                        },
                        '81.2.69.192/28': {
                            'ip-prefix': '81.2.69.192/28'
                        },
                        '149.101.100.0/28': {
                            'ip-prefix': '149.101.100.0/28'
                        },
                        '216.160.83.56/29': {
                            'ip-prefix': '216.160.83.56/29'
                        }
                    }
                }
            }
        },
        'ip-filter': {
            'maxmind_acl': {
                'filter-name': 'maxmind_acl',
                'filter-id': 100),
                'entry': {
                    10: {
                        'entry-id': 10,
                        'match': {
                            'ip': {
                                'ip-prefix-list': 'maxmind_matchlist'
                            }
                        },
                        'action': {
                            'drop': Leaf(Empty)
                        }
                    }
                }
            }
        }
    }
    """
    cfg_path = "/nokia-conf:configure/filter"
    cfg_payload = {
        "match-list": {
            "ip-prefix-list": {},
        },
        "ip-filter": {},
    }
    cfg_payload["match-list"]["ip-prefix-list"][
        config_prefix + "matchlist"
    ] = {"prefix-list-name": config_prefix + "matchlist", "prefix": {}}
    for prefix in prefixes:
        cfg_payload["match-list"]["ip-prefix-list"][
            config_prefix + "matchlist"
        ]["prefix"][prefix] = {"ip-prefix": prefix}

    cfg_payload["ip-filter"][config_prefix + "acl"] = {
        "filter-name": config_prefix + "acl",
        "filter-id": 100,
        "entry": {
            10: {
                "entry-id": 10,
                "match": {
                    "ip": {"ip-prefix-list": config_prefix + "matchlist"}
                },
                "action": {"drop": Leaf(Empty)},
            }
        },
    }

    connection_object.candidate.set(cfg_path, cfg_payload, method="replace")


def main():
    """The main procedure. The execution starts here."""
    prefixes = readPrefixes("cf3:/prefixes.txt")
    conn = connect()
    data_to_matchlist_config(prefixes, "maxmind_matchlist", conn)
    create_acl("maxmind_acl", 100, ((10, "maxmind_matchlist", "drop"),), conn)
    # OR / AND
    # create_matchlist_and_acl("maxmind_", prefixes, conn)


if __name__ == "__main__":
    main()
