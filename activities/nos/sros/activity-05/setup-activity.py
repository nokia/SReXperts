#!/usr/bin/env python
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


import argparse
from getpass import getpass

from pysros.management import connect
from pysros.wrappers import Container, Leaf


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["setup", "teardown"])
    parser.add_argument(
        "--configure-all", action="store_true", help=argparse.SUPPRESS
    )
    args = parser.parse_args()
    return args


def get_connection(host, passwd):
    print(f"Getting connection to {host}")
    try:
        print(
            f"Connecting to {host}.\nThis may take some time if this is the first time you have connected to {host}."
        )
        c = connect(
            host=host,
            username="admin",
            password=passwd,
            hostkey_verify=False,
        )
        print(f"Connected to {host}.\nYANG schema obtained and compiled.")
        return c
    except Exception as issue:
        raise SystemExit(
            f"Failed to get connectio to {host}: {issue}"
        ) from issue


def unconfigure(host, passwd):
    c = get_connection(host=host, passwd=passwd)
    try:
        print(f"Deleting service configuration from {host}.")
        c.candidate.delete(
            '/nokia-conf:configure/service/vprn[service-name="activity-05-green"]'
        )
        c.candidate.delete(
            '/nokia-conf:configure/service/vprn[service-name="activity-05-red"]'
        )
        print(f"Deleted service configuration from {host}.")
        c.disconnect()
    except Exception as issue:
        print(
            f"Failed to delete service configuration from {host}: {issue}"
        )
        pass


def configure(host, config, passwd):
    c = get_connection(host=host, passwd=passwd)
    try:
        print(f"Configuring {host}.")
        c.candidate.set("/configure", config)
        print(f"Configuration of {host} complete.")
        c.disconnect()
    except Exception as issue:
        raise SystemExit(f"Failed to configure {host}: {issue}") from issue


def main():
    args = get_args()
    passwd = getpass("Enter router password:")
    pe1_config = {
        "service": Container(
            {
                "vprn": {
                    "activity-05-green": Container(
                        {
                            "service-id": Leaf(501),
                            "bgp-evpn": Container(
                                {
                                    "mpls": {
                                        1: Container(
                                            {
                                                "vrf-target": Container(
                                                    {
                                                        "community": Leaf(
                                                            "target:65000:501"
                                                        )
                                                    }
                                                ),
                                                "admin-state": Leaf(
                                                    "enable"
                                                ),
                                                "auto-bind-tunnel": Container(
                                                    {
                                                        "resolution-filter": Container(
                                                            {
                                                                "sr-isis": Leaf(
                                                                    True
                                                                )
                                                            }
                                                        ),
                                                        "resolution": Leaf(
                                                            "filter"
                                                        ),
                                                    }
                                                ),
                                                "route-distinguisher": Leaf(
                                                    "10.46.15.21:501"
                                                ),
                                                "bgp-instance": Leaf(1),
                                            }
                                        )
                                    }
                                }
                            ),
                            "interface": {
                                "vprn-pe-ce": Container(
                                    {
                                        "interface-name": Leaf(
                                            "vprn-pe-ce"
                                        ),
                                        "admin-state": Leaf("enable"),
                                        "loopback": Leaf(True),
                                        "ipv4": Container(
                                            {
                                                "primary": Container(
                                                    {
                                                        "prefix-length": Leaf(
                                                            32
                                                        ),
                                                        "address": Leaf(
                                                            "10.0.0.21"
                                                        ),
                                                    }
                                                )
                                            }
                                        ),
                                    }
                                )
                            },
                            "admin-state": Leaf("enable"),
                            "static-routes": Container(
                                {
                                    "route": {
                                        (
                                            "172.16.21.0/24",
                                            "unicast",
                                        ): Container(
                                            {
                                                "route-type": Leaf(
                                                    "unicast"
                                                ),
                                                "blackhole": Container(
                                                    {
                                                        "admin-state": Leaf(
                                                            "enable"
                                                        ),
                                                        "generate-icmp": Leaf(
                                                            True
                                                        ),
                                                    }
                                                ),
                                                "ip-prefix": Leaf(
                                                    "172.16.21.0/24"
                                                ),
                                            }
                                        )
                                    }
                                }
                            ),
                            "customer": Leaf("1"),
                            "service-name": Leaf("activity-05-green"),
                        }
                    ),
                    "activity-05-red": Container(
                        {
                            "service-id": Leaf(502),
                            "bgp-evpn": Container(
                                {
                                    "mpls": {
                                        1: Container(
                                            {
                                                "vrf-target": Container(
                                                    {
                                                        "community": Leaf(
                                                            "target:65000:502"
                                                        )
                                                    }
                                                ),
                                                "admin-state": Leaf(
                                                    "enable"
                                                ),
                                                "auto-bind-tunnel": Container(
                                                    {
                                                        "resolution-filter": Container(
                                                            {
                                                                "sr-isis": Leaf(
                                                                    True
                                                                )
                                                            }
                                                        ),
                                                        "resolution": Leaf(
                                                            "filter"
                                                        ),
                                                    }
                                                ),
                                                "route-distinguisher": Leaf(
                                                    "10.46.15.21:502"
                                                ),
                                                "bgp-instance": Leaf(1),
                                            }
                                        )
                                    }
                                }
                            ),
                            "interface": {
                                "vprn-pe-ce": Container(
                                    {
                                        "interface-name": Leaf(
                                            "vprn-pe-ce"
                                        ),
                                        "admin-state": Leaf("enable"),
                                        "loopback": Leaf(True),
                                        "ipv4": Container(
                                            {
                                                "primary": Container(
                                                    {
                                                        "prefix-length": Leaf(
                                                            32
                                                        ),
                                                        "address": Leaf(
                                                            "10.0.0.21"
                                                        ),
                                                    }
                                                )
                                            }
                                        ),
                                    }
                                )
                            },
                            "admin-state": Leaf("enable"),
                            "static-routes": Container(
                                {
                                    "route": {
                                        (
                                            "172.16.21.0/24",
                                            "unicast",
                                        ): Container(
                                            {
                                                "route-type": Leaf(
                                                    "unicast"
                                                ),
                                                "blackhole": Container(
                                                    {
                                                        "admin-state": Leaf(
                                                            "enable"
                                                        ),
                                                        "generate-icmp": Leaf(
                                                            True
                                                        ),
                                                    }
                                                ),
                                                "ip-prefix": Leaf(
                                                    "172.16.21.0/24"
                                                ),
                                            }
                                        )
                                    }
                                }
                            ),
                            "customer": Leaf("1"),
                            "service-name": Leaf("activity-05-red"),
                        }
                    ),
                }
            }
        )
    }
    pe2_config = {
        "service": Container(
            {
                "vprn": {
                    "activity-05-green": Container(
                        {
                            "service-id": Leaf(501),
                            "bgp-evpn": Container(
                                {
                                    "mpls": {
                                        1: Container(
                                            {
                                                "vrf-target": Container(
                                                    {
                                                        "community": Leaf(
                                                            "target:65000:501"
                                                        )
                                                    }
                                                ),
                                                "admin-state": Leaf(
                                                    "enable"
                                                ),
                                                "auto-bind-tunnel": Container(
                                                    {
                                                        "resolution-filter": Container(
                                                            {
                                                                "sr-isis": Leaf(
                                                                    True
                                                                )
                                                            }
                                                        ),
                                                        "resolution": Leaf(
                                                            "filter"
                                                        ),
                                                    }
                                                ),
                                                "route-distinguisher": Leaf(
                                                    "10.46.15.22:501"
                                                ),
                                                "bgp-instance": Leaf(1),
                                            }
                                        )
                                    }
                                }
                            ),
                            "interface": {
                                "vprn-pe-ce": Container(
                                    {
                                        "interface-name": Leaf(
                                            "vprn-pe-ce"
                                        ),
                                        "admin-state": Leaf("enable"),
                                        "loopback": Leaf(True),
                                        "ipv4": Container(
                                            {
                                                "primary": Container(
                                                    {
                                                        "prefix-length": Leaf(
                                                            32
                                                        ),
                                                        "address": Leaf(
                                                            "10.0.0.22"
                                                        ),
                                                    }
                                                )
                                            }
                                        ),
                                    }
                                )
                            },
                            "admin-state": Leaf("enable"),
                            "static-routes": Container(
                                {
                                    "route": {
                                        (
                                            "172.16.22.0/24",
                                            "unicast",
                                        ): Container(
                                            {
                                                "route-type": Leaf(
                                                    "unicast"
                                                ),
                                                "blackhole": Container(
                                                    {
                                                        "admin-state": Leaf(
                                                            "enable"
                                                        ),
                                                        "generate-icmp": Leaf(
                                                            True
                                                        ),
                                                    }
                                                ),
                                                "ip-prefix": Leaf(
                                                    "172.16.22.0/24"
                                                ),
                                            }
                                        )
                                    }
                                }
                            ),
                            "customer": Leaf("1"),
                            "service-name": Leaf("activity-05-green"),
                        }
                    ),
                    "activity-05-red": Container(
                        {
                            "service-id": Leaf(502),
                            "bgp-evpn": Container(
                                {
                                    "mpls": {
                                        1: Container(
                                            {
                                                "vrf-target": Container(
                                                    {
                                                        "community": Leaf(
                                                            "target:65000:502"
                                                        )
                                                    }
                                                ),
                                                "admin-state": Leaf(
                                                    "enable"
                                                ),
                                                "auto-bind-tunnel": Container(
                                                    {
                                                        "resolution-filter": Container(
                                                            {
                                                                "sr-isis": Leaf(
                                                                    True
                                                                )
                                                            }
                                                        ),
                                                        "resolution": Leaf(
                                                            "filter"
                                                        ),
                                                    }
                                                ),
                                                "route-distinguisher": Leaf(
                                                    "10.46.15.22:502"
                                                ),
                                                "bgp-instance": Leaf(1),
                                            }
                                        )
                                    }
                                }
                            ),
                            "interface": {
                                "vprn-pe-ce": Container(
                                    {
                                        "interface-name": Leaf(
                                            "vprn-pe-ce"
                                        ),
                                        "admin-state": Leaf("enable"),
                                        "loopback": Leaf(True),
                                        "ipv4": Container(
                                            {
                                                "primary": Container(
                                                    {
                                                        "prefix-length": Leaf(
                                                            32
                                                        ),
                                                        "address": Leaf(
                                                            "10.0.0.22"
                                                        ),
                                                    }
                                                )
                                            }
                                        ),
                                    }
                                )
                            },
                            "admin-state": Leaf("enable"),
                            "static-routes": Container(
                                {
                                    "route": {
                                        (
                                            "172.16.22.0/24",
                                            "unicast",
                                        ): Container(
                                            {
                                                "route-type": Leaf(
                                                    "unicast"
                                                ),
                                                "blackhole": Container(
                                                    {
                                                        "admin-state": Leaf(
                                                            "enable"
                                                        ),
                                                        "generate-icmp": Leaf(
                                                            True
                                                        ),
                                                    }
                                                ),
                                                "ip-prefix": Leaf(
                                                    "172.16.22.0/24"
                                                ),
                                            }
                                        )
                                    }
                                }
                            ),
                            "customer": Leaf("1"),
                            "service-name": Leaf("activity-05-red"),
                        }
                    ),
                }
            }
        )
    }

    if args.configure_all:
        host = [
            ("clab-srexperts-pe1", pe1_config),
            ("clab-srexperts-pe2", pe2_config),
        ]
    else:
        host = [("clab-srexperts-pe2", pe2_config)]

    if args.operation == "setup":
        for h in host:
            configure(host=h[0], config=h[1], passwd=passwd)

    if args.operation == "teardown":
        for h in host:
            unconfigure(host=h[0], passwd=passwd)


if __name__ == "__main__":
    main()
