#!/usr/bin/env python3
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

#
# Example implementation of an event handler script to set interface descriptions according to information learnt over LLDP.
#
# Paths:
#   system lldp interface neighbor system-name - e.g. system lldp interface * neighbor * system-name
#   system lldp interface neighbor port-id - e.g. system lldp interface * neighbor * port-id
# Options:
#   interfaces: <array> - list of interfaces to enable auto-configuration of descriptions, e.g. [ ethernet-1/{10,11}, ethernet-2/5 ]
#   debug: <value>[default false] - optional debug prints - will be visible in 'last-stdout-stderr' leaf
#
# Example config:
#   system {
#        event-handler {
#            instance lldp {
#                admin-state enable
#                upython-script set-lldp-descriptions.py
#                paths [
#                    "system lldp interface * neighbor * port-id"
#                    "system lldp interface * neighbor * system-name"
#                ]
#                options {
#                    object interfaces {
#                        values [
#                            ethernet-1/12
#                            ethernet-1/{2..10}
#                            ethernet-1/{21..24}
#                            ethernet-1/{25,27..30}
#                        ]
#                    }
#                }
#            }
#        }
#    }

import sys
import json

_MAX_PATH_RANGE_EXPANSION = 4096

class PathRangeExpansionError(Exception):
    pass

def _expand_ranges(path):
    result = {}
    start = path.find('{') + 1
    end = path.find('}')
    if start < 1 or end < 0 or start == end:
        result[path] = None
        return result

    range_block = path[start:end]
    numbers = set()
    splits = range_block.split(',')
    # For each range
    for split in splits:
        pos = split.find('..')
        try:
            if pos >= 0:
                low = int(split[:pos])
                high = int(split[pos+2:])
                if high - low + 1 > _MAX_PATH_RANGE_EXPANSION:
                    raise PathRangeExpansionError(
                        f'Cannot expand path to more than {_MAX_PATH_RANGE_EXPANSION} paths')

                for i in range(low, high+1):
                    numbers.add(i)
            else:
                numbers.add(int(split))
        except (TypeError, ValueError) as e:
            raise PathRangeExpansionError(f"Invalid range expansion in '{path}': {type(e)}: {e}")

    if len(result) + len(numbers) > _MAX_PATH_RANGE_EXPANSION:
        raise PathRangeExpansionError(f'Cannot expand path to more than {_MAX_PATH_RANGE_EXPANSION} paths')

    sorted_list = sorted(numbers)
    if not sorted_list:
        raise PathRangeExpansionError(
            f"Invalid range expansion in '{path}': Must expand to at least one number")
    if sorted_list[0] < 0:
        raise PathRangeExpansionError(
            f"Invalid range expansion in '{path}': Negative numbers are not supported")

    for number in sorted_list:
        new_value = path[:start-1] + str(number) + path[end+1:]
        result[new_value] = None

    # found and expanded range
    return result

def process_options(options):
    parsed_interfaces = {}
    for interface_range in enabled_interfaces(options):
        interface_list = _expand_ranges(interface_range)
        parsed_interfaces.update(interface_list)
    return parsed_interfaces

def create_actions(parsed_interfaces, interfaces):
    actions = {'actions': []}
    for interface, lldp_info in interfaces.items():
        if interface in parsed_interfaces:
            if lldp_info.get('broadcast', False):
                description = 'to-broadcast-domain'
            else:
                description = f'to-{lldp_info.get("system-name", "unknown")}-{lldp_info.get("port-id","unknown")}'
            actions['actions'].append({
                'set-cfg-path':{'path':f'interface {interface} description',
                'value':description,
                'always-execute':True}
            })
    return actions

def enabled_interfaces(options):
    return options.get('interfaces', [])

def process_paths(paths):
    interfaces = {}
    for update in paths:
        path = update.get('path','')
        value = update.get('value','')
        if path.startswith('interface'):
            interface_name = path.split(' ')[1]
        else:
            interface_name = path.split(' ')[3]
        if interface_name not in interfaces:
            interfaces[interface_name] = {}
        if path.endswith('system-name'):
            if 'system-name' in interfaces.get(interface_name, {}):
                interfaces[interface_name]['broadcast'] = True
            else:
                interfaces[interface_name]['system-name'] = value
        elif path.endswith('port-id'):
            if 'port-id' in interfaces.get(interface_name, {}):
                interfaces[interface_name]['broadcast'] = True
            else:
                interfaces[interface_name]['port-id'] = value
    return interfaces

def event_handler_main(in_json_str):
    in_json = json.loads(in_json_str)
    paths = in_json['paths']
    options = in_json['options']
    parsed_interfaces = process_options(options)
    lldp_interfaces = process_paths(paths)
    if options.get('debug', '') == 'true':
        print(
            f'enabled interfaces = {enabled_interfaces(options)}\n\
parsed interfaces = {parsed_interfaces}\n'
        )
    actions = create_actions(parsed_interfaces, lldp_interfaces)

    response = actions
    json_response = json.dumps(response)
    return json_response

#
# This code is only if you want to test it from bash - this isn't used when invoked from SRL
#
def main():
    example_in_json_str = """
{
    "paths": [
        {
            "path":"system lldp interface ethernet-1/2 neighbor test-1/2 system-name",
            "value":"testdut1/2"
        },
        {
            "path":"system lldp interface ethernet-1/2 neighbor test-1/2 port-id",
            "value":"testport1/2"
        },
        {
            "path":"system lldp interface ethernet-1/3 neighbor test-1/3 system-name",
            "value":"testdut1/3"
        },
        {
            "path":"system lldp interface ethernet-1/3 neighbor test-1/3 port-id",
            "value":"testport3"
        },
        {
            "path":"system lldp interface ethernet-1/2 neighbor broadcast1/2 system-name",
            "value":"broadcastdut1/2"
        },
        {
            "path":"system lldp interface ethernet-1/2 neighbor broadcast1/2 port-id",
            "value":"broadcasttestport1/2"
        }
    ],
    "options": {"interfaces":["ethernet-1/2", "ethernet-1/{10,11,14..20}"],"debug":"true"}
}
"""
    json_response = event_handler_main(example_in_json_str)
    print(json_response)

if __name__ == "__main__":
    sys.exit(main())
