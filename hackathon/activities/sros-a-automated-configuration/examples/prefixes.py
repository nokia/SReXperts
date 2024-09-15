# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""Example implementation for the first leg of the automated-configuration
usecase for the Hackathon in SReXperts Americas 2024.

Calls out to Maxmind API and configures prefix lists on MD SR OS using
pySROS. This version of the file runs remotely and is standalone.

Tested on: SR OS 24.7.R1
"""

import os
from base64 import b64encode
from io import BytesIO
from zipfile import ZipFile

import requests
from dotenv import find_dotenv, load_dotenv
from pysros.management import Empty, connect
from pysros.wrappers import Container, Leaf


def getBasicAuthentication(user, password):
    """Shorthand method for returning a usable basic authentication"""
    return b64encode(bytes(user + ":" + password, "utf-8")).decode("utf-8")


def getPrefixesFromMaxmind(country):
    """Function that takes a country as input, and queries the example
    database made available by Maxmind for related prefix data. As this
    example database is limited in size, the resulting list of prefixes is
    limited in size as well.

    Returns a list of IP Prefixes associated with the input country.
    """
    # account_id = "###"
    # license_key = "###"
    #
    # basicAuth = {
    #     "Content-Type": "application/json",
    #     "Authorization": f"Basic {getBasicAuthentication(account_id, license_key)}",
    # }
    # url = "https://download.maxmind.com/geoip/databases/GeoLite2-City/download?suffix=csv"
    # x = requests.get(url, headers = basicAuth, verify = False, proxies={})
    url = "https://dev.maxmind.com/static/GeoIP2-Country-CSV_Example.zip"
    resp = requests.get(url, verify=False, proxies={})

    # write to disk
    # url = "https://dev.maxmind.com/static/GeoIP2-City-CSV_Example.zip"
    # x = requests.get(url)
    # z = zipfile.ZipFile(io.BytesIO(x.content))
    # z.extractall("database/")
    # with open("database/GeoIP2-Country-Locations-en.csv", "rb+") as output:
    #     ...

    # in memory
    geoip_csv_zipped = ZipFile(BytesIO(resp.content))
    geo_id = 000
    resulting_prefixes = []
    for line in geoip_csv_zipped.open(
        "GeoIP2-Country-CSV_Example/GeoIP2-Country-Locations-en.csv"
    ).readlines():
        if country in line:
            geo_id = line.decode("utf-8").split(",", 1)[0]
    for line in geoip_csv_zipped.open(
        "GeoIP2-Country-CSV_Example/GeoIP2-Country-Blocks-IPv4.csv"
    ).readlines():
        prefix_line = line.decode("utf-8")
        if geo_id in prefix_line:
            resulting_prefixes.append(prefix_line.split(",", 1)[0])
    return resulting_prefixes


# def database_MaxMindPython():
#     #- https://github.com/maxmind/MaxMind-DB/blob/main/test-data/GeoIP2-Country-Test.mmdb
#     with geoip2.webservice.Client(###, '###', host="geolite.info") as client:
#         print(client.city('1.2.3.4'))
#         print(client.city('1.2.3.4').country)


def data_to_matchlist_config(csv_data, match_list_name, connection_object):
    """Function that takes as input a comma-separated list of IP prefixes, a
    target name for an ip-prefix-list and a connection object.

    The connection object represents an MD SR OS router. The prefixes in the CSV
    data are used to populate an ip-prefix-list on the router using the specified
    name.

    There is no output for this function.
    """
    cfg_path = f'/nokia-conf:configure/filter/match-list/ip-prefix-list[prefix-list-name="{match_list_name}"]'
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
        f'/nokia-conf:configure/filter/ip-filter[filter-name="{acl_name}"]'
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
    load_dotenv(find_dotenv())  # Load the .env file.

    # Fetch variables from the .env file.
    username_var = os.getenv("ACCOUNT_USERNAME")
    password_var = os.getenv("ACCOUNT_PASSWORD")

    prefixes = getPrefixesFromMaxmind(b"United Kingdom")
    # prefixes = getPrefixesFromMaxmind(b"Sweden")

    conn = connect(
        host="clab-srexperts-pe1",
        username=username_var,
        password=password_var,
        hostkey_verify=False,
    )
    # data_to_matchlist_config(prefixes, "maxmind_matchlist", conn)
    # create_acl("maxmind_acl",100,((10, "maxmind_matchlist", "drop"),),conn)
    # OR / AND
    create_matchlist_and_acl("maxmind_", prefixes, conn)


if __name__ == "__main__":
    main()
