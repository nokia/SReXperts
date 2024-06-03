# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import sys
import argparse
from pysros.management import connect
from pysros.pprint import Table

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
            hostkey_verify=False
        )
    except RuntimeError as error1:
        print("Failed to connect.  Error:", error1)
        sys.exit(-1)
    return connection_object


def oper_states(conn, vpls_service_id, vprn_service_id):
    # - Ensure the VPLS and VPRN services are operationally up
    vpls_state = conn.running.get('/state/service/vpls[service-name="evpn-vpls-%s"]/oper-state' % vpls_service_id)
    vprn_state = conn.running.get('/state/service/vprn[service-name="evpn-vprn-%s"]/oper-state' % vprn_service_id)
    return [
        ("VPLS Oper. State", vpls_state),
        ("VPRN Oper. State", vprn_state),
    ]

def evpn_rr_healthy(conn):
    # - Ensure BGP-EVPN connection to RR is up, and routes are being exchanged
    bgp_rr_state = conn.running.get(
        '/state/router[router-name="Base"]/bgp/neighbor[ip-address="fd00:fde8::X:13"]/statistics', # fill in your instance ID for X
        filter = {
            "session-state": {},
            "remote-family": {},
            "family-prefix": {
                "evpn": {}
            }
        }
    )
    return [
        ("BGP RR State", bgp_rr_state['session-state']),
        ("EVPN Session Active", "EVPN" in bgp_rr_state["remote-family"]["family"]),
        ("# EVPN Routes Received", bgp_rr_state['family-prefix']["evpn"]["received"]),
        ("# EVPN Routes Active", bgp_rr_state['family-prefix']["evpn"]["active"]),
        ("# EVPN Routes Sent", bgp_rr_state['family-prefix']["evpn"]["sent"])
    ]


def ping_wrapper(conn, destination, service_name):
    path = '/nokia-oper-global:global-operations/ping'
    input_data = {
        'destination': destination,
        'router-instance': service_name,
        'count': 1,
        'timeout': 1
    }
    response = "No"
    if conn.action(path, input_data)["results"]["probe"][1]['status'].data == 'response-received':
        response = "Yes"
    return response


def sites_reachable(conn, src_pe, service_name, subnet):
    # - Check if remote sites interfaces respond to ping
    pe_sites = [1,2,3,4]
    pe_sites.remove(src_pe)
    result = []
    for pe in pe_sites:
        result.append(("PE%s reachable" % pe,ping_wrapper(conn, subnet + ".10" + str(pe), service_name)))
    return result

def clients_reachable(conn, service_name, subnet):
    # - Check if any of the four clients are reachable
    # We know that the other client sites are client01, 02, 03 and 04
    return [
        ("client01 reachable",ping_wrapper(conn, subnet + ".1", service_name)),
        ("client02 reachable",ping_wrapper(conn, subnet + ".2", service_name)),
        ("client03 reachable",ping_wrapper(conn, subnet + ".3", service_name)),
        ("client04 reachable",ping_wrapper(conn, subnet + ".4", service_name))
    ]


# Fuction definition to output a SR OS style table to the screen
def print_verified_results(rows, service_name):

    # Define the columns that will be used in the table.  Each list item
    # is a tuple of (column width, heading).
    cols = [
        (50, "Parameter tested", '^'),
        (29, "Result"),
    ]

    # Initalize the Table object with the heading and columns.
    table = Table("Verification for service %s" % service_name, cols, showCount='Tests run')

    # Print the output passing the data for the rows as an argument to the function.
    table.print(rows)


def get_pe_id(connection):
    name = connection.running.get('/configure/system/name')
    return int(name.split('pe')[1][0])

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

            pe_id = get_pe_id(conn)

            verified_service = []
            verified_service += oper_states(conn, vpls_svc_id, vprn_svc_id)
            verified_service += evpn_rr_healthy(conn)
            verified_service += sites_reachable(conn, pe_id, "evpn-vprn-" + str(vprn_svc_id), svc_ipaddress.rsplit('.',1)[0])
            verified_service += clients_reachable(conn, "evpn-vprn-" + str(vprn_svc_id), svc_ipaddress.rsplit('.',1)[0])
            print_verified_results(verified_service, "evpn-{vpls,vprn}-{%s,%s} on PE%d" % (vpls_svc_id, vprn_svc_id, pe_id))

if __name__ == "__main__":
    main()
