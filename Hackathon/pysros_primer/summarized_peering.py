#!/usr/bin/env python3
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.pprint import Table
from pysros.management import connect, sros


def get_connection():
    if sros():
        try:
            connection_object = connect()
            return connection_object
        except Exception as error:
            raise SystemExit(error) from error
    else:
        raise SystemExit("Only for use locally on the SR OS MD-CLI")


def obtain_bgp_data(connection_object):
    try:
        bgp_config_data = connection_object.running.get(
            '/nokia-conf:configure/router[router-name="Base"]/bgp/neighbor'
        )
        bgp_state_data = connection_object.running.get(
            '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
        )
        return bgp_config_data, bgp_state_data
    except LookupError as lookup_error:
        raise SystemExit(lookup_error)


def build_table(bgp_config_data, bgp_state_data):
    summary = "SReXperts 2023"
    columns = [
        (30, "Peer"),
        (20, "Group"),
        (20, "State"),
        (30, "Negotiated capabilities"),
    ]
    rows = []
    for neighbor in bgp_config_data:
        group = bgp_config_data[neighbor]["group"].data
        session_state = bgp_state_data[neighbor]["statistics"][
            "session-state"
        ].data
        try:
            negotiated_capability = bgp_state_data[neighbor]["statistics"][
                "negotiated-family"
            ].data
        except KeyError:
            negotiated_capability = None
        rows.append([neighbor, group, session_state, negotiated_capability])
    width = sum([col[0] for col in columns])
    table = Table(
        "Summarized peerings",
        columns=columns,
        showCount="Number of peers",
        summary=summary,
        width=width,
    )
    return table, rows


def main():
    connection_object = get_connection()
    bgp_config_data, bgp_state_data = obtain_bgp_data(connection_object)
    table, rows = build_table(bgp_config_data, bgp_state_data)
    table.print(rows)


if __name__ == "__main__":
    main()
