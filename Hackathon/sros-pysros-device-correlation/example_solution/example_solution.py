#!/usr/bin/env python3
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


import json
from operator import itemgetter
from pysros.management import connect
from pysros.exceptions import ModelProcessingError
from pysros.pprint import Table

class Node:
    def __init__(self, node_name, lab_name) -> None:
        self.node_name = node_name
        self.connection = self._get_connection(lab_name)

    def _get_connection(self, lab_name):
        try:
            return connect(
                host=f"clab-{lab_name}-{self.node_name}",
                username="admin",
                password="admin",
                hostkey_verify=False,
            )
        except ModelProcessingError as model_processing_error:
            raise SystemExit(model_processing_error) from model_processing_error
        except Exception as error:
            raise SystemExit(error) from error


def read_clab_topology(lab_directory):
    with open("./" + lab_directory + "/topology-data.json", "r") as input_file:
        json_file_contents = json.load(input_file)
    return json_file_contents


def identify_sros_nodes(clab_topo):
    sros_nodes = []
    for item in clab_topo["nodes"]:
        if clab_topo["nodes"][item]["kind"] == "vr-nokia_sros":
            sros_nodes.append(item)
    return list(set(sros_nodes))


def _bgp_enabled_devices(node_connections):
    nodes = []
    for node in node_connections:
        try:
            data_output = node.connection.running.get(
                '/nokia-state:state/router[router-name="Base"]/bgp/statistics/operational-state'
            )
            if data_output.data == "Up":
                nodes.append(node.node_name)
        except LookupError:
            pass
    return sorted(nodes)


def _isis_enabled_devices(node_connections):
    nodes = []
    for node in node_connections:
        try:
            data_output = node.connection.running.get(
                '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]/oper-state'
            )
            if data_output.data == "up":
                nodes.append(node.node_name)
        except LookupError:
            pass
    return sorted(nodes)


def _ipv4_routes_in_rib(node_connections):
    nodes_ipv4 = []
    for node in node_connections:
        try:
            nodes_ipv4.append(
                (
                    node.node_name,
                    len(
                        node.connection.running.get_list_keys(
                            '/nokia-state:state/router[router-name="Base"]/route-table/unicast/ipv4/route'
                        )
                    ),
                )
            )
        except LookupError:
            pass
    return list(reversed(sorted(nodes_ipv4, key=itemgetter(1))))


def _cpu_util_rankings(node_connections):
    tmp = {}
    for node in node_connections:
        try:
            cpu = node.connection.running.get(
                '/nokia-state:state/system/cpu[sample-period="60"]/summary/usage/cpu-usage'
            ).data
            tmp[node.node_name] = float(cpu)
        except LookupError:
            pass
    sorted_cpu_nodes_high_low = list(
        reversed(sorted(tmp.items(), key=lambda x: x[1]))
    )
    return sorted_cpu_nodes_high_low


def collate_data(node_connections):
    data = {}
    data["bgp_enabled_devices"] = _bgp_enabled_devices(node_connections)
    data["isis_enabled_devices"] = _isis_enabled_devices(node_connections)
    data["hot_cpus_high_low"] = _cpu_util_rankings(node_connections)
    data["ipv4_routes_in_rib"] = _ipv4_routes_in_rib(node_connections)
    return data


def print_table(data):
    key_values = []
    for key, value in data.items():
        key_values.append([key, value])
    summary = """SReXperts 2023"""
    rows = key_values
    cols = [(20, "Item"), (70, "Value")]
    width = sum([col[0] for col in cols])
    table = Table(
        "Collated network information",
        columns=cols,
        showCount="Number of metrics",
        summary=summary,
        width=width,
    )
    table.print(rows)


def main():
    lab_name = "sros-pysros-device-correlation"
    clab_topo = read_clab_topology("clab-" + lab_name)
    sros_nodes = identify_sros_nodes(clab_topo)
    node_connections = []
    for node in sros_nodes:
        node_connections.append(Node(node, lab_name))
    data = collate_data(node_connections)
    print_table(data)


if __name__ == "__main__":
    main()
