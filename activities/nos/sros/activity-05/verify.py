#!/usr/bin/env python
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


import argparse
from getpass import getpass

from pysros.management import connect
from pysros.pprint import Padding, Table
from pysros.wrappers import Container, Leaf


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        required=False,
        help="Run with verbose logging",
    )
    args = parser.parse_args()
    return args


def get_connection(host, passwd, verbose=False):
    if verbose:
        print(f"Getting connection to {host}")
    try:
        if verbose:
            print(
                f"Connecting to {host}.\nThis may take some time if this is the first time you have connected to {host}."
            )
        c = connect(
            host=host,
            username="admin",
            password=passwd,
            hostkey_verify=False,
        )
        setattr(c, "name", host)
        if verbose:
            print(
                f"Connected to {host}.  YANG schema obtained and compiled."
            )
        return c
    except Exception as issue:
        raise SystemExit(
            f"Failed to get connectio to {host}: {issue}"
        ) from issue


def disconnect_session(host_connection, verbose=False):
    if verbose:
        print(f"Disconnecting {host_connection.name}.")
    host_connection.disconnect()
    if verbose:
        print(f"Disconnected {host_connection.name}.")


def test_config_exists(host_connection, service_name=None, verbose=False):
    if verbose:
        print(
            f"Testing that the {service_name} configuration exists on {host_connection.name}"
        )
    status = host_connection.running.exists(
        f'/nokia-conf:configure/service/vprn[service-name="{service_name}"]'
    )
    if status:
        if verbose:
            print(
                f"Configuration for {service_name} exists on {host_connection.name}"
            )
        return True
    else:
        if verbose:
            print(
                f"Configuration for {service_name} does not exist on {host_connection.name}"
            )
        return False


def test_ping_remote_end(
    host_connection, router_instance=False, verbose=False
):
    if host_connection.name == "clab-srexperts-pe1":
        dest_ip = "10.0.0.22"
    elif host_connection.name == "clab-srexperts-pe2":
        dest_ip = "10.0.0.21"
    else:
        raise SystemError("Cannot determine remote end")
    input_options = {
        "destination": dest_ip,
        "output-format": "summary",
        "router-instance": router_instance,
    }
    if verbose:
        print(
            f"Running ping from {host_connection.name} to remote IP {dest_ip}"
        )
    output = host_connection.action(
        "/nokia-oper-global:global-operations/ping", input_options
    )
    if str(output["status"]) == "completed":
        if int(
            output["results"]["summary"]["statistics"]["packets"]["sent"]
        ) == int(
            output["results"]["summary"]["statistics"]["packets"][
                "received"
            ]
        ):
            if verbose:
                print(
                    f"Ping completed successfully from {host_connection.name} to {dest_ip}"
                )
            return True
        else:
            if verbose:
                print(
                    f"Ping failed from {host_connection.name} to {dest_ip}"
                )
            return False
    else:
        if verbose:
            print(f"Ping failed from {host_connection.name} to {dest_ip}")
        return False


def main():
    args = get_args()
    hosts = ["clab-srexperts-pe1", "clab-srexperts-pe2"]
    host_connections = []
    passwd = getpass("Enter router password:")
    for host in hosts:
        host_connections.append(
            get_connection(host, passwd, verbose=args.verbose)
        )

    rows = []
    for host_connection in host_connections:
        rows_host = [host_connection.name]
        rows_host.append(
            test_config_exists(
                host_connection,
                service_name="activity-05-green",
                verbose=args.verbose,
            )
        )
        rows_host.append(
            test_config_exists(
                host_connection,
                service_name="activity-05-red",
                verbose=args.verbose,
            )
        )
        rows_host.append(
            test_ping_remote_end(
                host_connection,
                router_instance="activity-05-green",
                verbose=args.verbose,
            )
        )
        rows_host.append(
            test_ping_remote_end(
                host_connection,
                router_instance="activity-05-red",
                verbose=args.verbose,
            )
        )
        rows.append(tuple(rows_host))
    cols = [
        (25, "Host"),
        (15, "GREEN config"),
        (15, "RED config"),
        (15, "GREEN traffic"),
        (15, "RED traffic"),
    ]
    width = sum([col[0] for col in cols])
    table = Table("Verification table", columns=cols, width=width)
    table.print(rows)

    for host_connection in host_connections:
        disconnect_session(host_connection, verbose=args.verbose)


if __name__ == "__main__":
    main()
