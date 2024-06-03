# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import sys
from pysros.management import connect

CLIENT_PORT = '1/1/c6/1'

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
        )
    except RuntimeError as error1:
        print("Failed to connect.  Error:", error1)
        sys.exit(-1)
    return connection_object


def create_vpls(connection, service_name):
    payload = {
        'bgp': {
            1: {
                'route-distinguisher': '65021:500',
                'route-target': {
                    'import': 'target:65021:500',
                    'export': 'target:65021:500',
                },
                'bgp-instance': 1
            }
        },
        'bgp-evpn': {
            'mpls': {
                1: {
                    'auto-bind-tunnel': {
                        'resolution': 'filter',
                        'resolution-filter': {
                            'sr-isis': True
                        }
                    },
                    'bgp-instance': 1,
                    'admin-state': 'enable'
                }
            }
        },
        'service-id': 500,
        'sap': {
            '%s:500' % CLIENT_PORT: {
                'sap-id': '%s:500' % CLIENT_PORT
            }
        },
        'customer': '1',
        'routed-vpls': {},
        'service-name': service_name,
        'admin-state': 'enable'
    }
    path = '/configure/service/vpls[service-name="%s"]' % service_name
    connection.candidate.set(path, payload, commit=False)


def create_vprn(connection, service_name, vpls_name):
    payload = {
        'interface': {
            vpls_name: {
                'vpls': {
                    vpls_name: {
                        'vpls-name': vpls_name
                    }
                },
                'interface-name': vpls_name,
                'ipv4': {
                    'primary': {
                        'prefix-length': 24,
                        'address': '10.70.10.101'
                    }
                }
            }
        },
        'bgp-ipvpn': {
            'mpls': {
                'vrf-target': {
                    'community': 'target:65020:501'
                },
                'admin-state': 'enable',
                'route-distinguisher': '65020:501'
            }
        },
        'customer': '1',
        'admin-state': 'enable',
        'service-id': 501,
        'service-name': service_name
    }
    path = '/configure/service/vprn[service-name="%s"]' % service_name
    connection.candidate.set(path, payload, commit=True)


def main():
    """The main procedure.  The execution starts here."""
    conn = get_connection()
    create_vpls(conn, "evpn-vpls-500")
    create_vprn(conn, "evpn-vprn-501", "evpn-vpls-500")

if __name__ == "__main__":
    main()
