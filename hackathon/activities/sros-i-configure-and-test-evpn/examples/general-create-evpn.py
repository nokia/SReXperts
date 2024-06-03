# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import sys
import argparse
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
            hostkey_verify = False
        )
    except RuntimeError as error1:
        print("Failed to connect.  Error:", error1)
        sys.exit(-1)
    return connection_object


def create_vpls(connection, service_name, service_id):
    payload = {
        'bgp': {
            1: {
                'route-distinguisher': '65021:%s' % service_id,
                'route-target': {
                    'import': 'target:65021:%s' % service_id,
                    'export': 'target:65021:%s' % service_id
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
        'service-id': int(service_id),
        'sap': {
            '%s:%s' % (CLIENT_PORT, service_id): {
                'sap-id': '%s:%s' % (CLIENT_PORT, service_id)
            }
        },
        'customer': '1',
        'routed-vpls': {},
        'service-name': service_name,
        'admin-state': 'enable'
    }
    path = '/configure/service/vpls[service-name="evpn-vpls-%s"]' % service_id
    connection.candidate.set(path, payload, commit=False)


def create_vprn(connection, service_name, interface_name, service_id, ipaddress):
    payload = {
        'interface': {
            interface_name: {
                'vpls': {
                    interface_name: {
                        'vpls-name': interface_name
                    }
                },
                'interface-name': interface_name,
                'ipv4': {
                    'primary': {
                        'prefix-length': 24,
                        'address': ipaddress
                    }
                }
            }
        },
        'bgp-ipvpn': {
            'mpls': {
                'vrf-target': {
                    'community': 'target:65020:%s' % service_id,
                },
                'admin-state': 'enable',
                'route-distinguisher': '65020:%s' % service_id,
            }
        },
        'customer': '1',
        'admin-state': 'enable',
        'service-id': int(service_id),
        'service-name': service_name
    }
    path = '/configure/service/vprn[service-name="%s"]' % service_name
    connection.candidate.set(path, payload, commit=True)


def main():
    """The main procedure.  The execution starts here."""
    parser = argparse.ArgumentParser(
                    prog='SReXperts - EVPN Creator',
                    description='Accepts input parameters to generate templated EVPN configurations')
    parser.add_argument('-service_ids', '-s', help="A comma-separated list of a tuple representing a service. Tuples are service_id/pe/ipaddress")
    parser.add_argument('-username', '-u', help="Username to connect to hosts.")
    parser.add_argument('-password', '-p', help="Password to connect to hosts.")
    args = parser.parse_args()

    if not args.service_ids:
        print("No services specified, stop here.")
        sys.exit(0)
    else:
        for service_tuple in args.service_ids.split(','):
            svc_id, host, svc_ipaddress = service_tuple.split('/')

            vpls_svc_id = str(svc_id)
            vprn_svc_id = str(int(svc_id)+1)

            conn = get_connection(host = host, username = args.username, password = args.password)
            create_vpls(conn, "evpn-vpls-%s" % vpls_svc_id, vpls_svc_id)
            create_vprn(conn, "evpn-vprn-%s" % vprn_svc_id, "evpn-vpls-%s" % vpls_svc_id, vprn_svc_id, svc_ipaddress)

if __name__ == "__main__":
    main()
