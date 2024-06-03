# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import sys
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
        )
    except RuntimeError as error1:
        print("Failed to connect.  Error:", error1)
        sys.exit(-1)
    return connection_object


def oper_states(conn, service_id):
    # - Ensure the VPLS and VPRN services are operationally up
    vpls_state = conn.running.get('/state/service/vpls[service-name="evpn-vpls-%s"]/oper-state' % service_id)
    vprn_state = conn.running.get('/state/service/vprn[service-name="evpn-vprn-%s"]/oper-state' % str(int(service_id) + 1))
    return [
        ("VPLS Oper. State", vpls_state),
        ("VPRN Oper. State", vprn_state),
    ]

def evpn_rr_healthy(conn, service_id):
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


def sites_reachable(conn, service_id):
    # - Check if remote sites interfaces respond to ping
    # We know that the other possible sites are PE2, PE3 and PE4
    return [
        ("PE2 reachable",ping_wrapper(conn, "10.70.10.102", 'evpn-vprn-501')),
        ("PE3 reachable",ping_wrapper(conn, "10.70.10.103", 'evpn-vprn-501')),
        ("PE4 reachable",ping_wrapper(conn, "10.70.10.104", 'evpn-vprn-501'))
    ]

def clients_reachable(conn, service_id):
    # - Check if any of the four clients are reachable
    # We know that the other client sites are client01, 02, 03 and 04
    return [
        ("client01 reachable",ping_wrapper(conn, "10.70.10.1", 'evpn-vprn-501')),
        ("client02 reachable",ping_wrapper(conn, "10.70.10.2", 'evpn-vprn-501')),
        ("client03 reachable",ping_wrapper(conn, "10.70.10.3", 'evpn-vprn-501')),
        ("client04 reachable",ping_wrapper(conn, "10.70.10.4", 'evpn-vprn-501'))
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


def main():
    """The main procedure.  The execution starts here."""
    conn = get_connection()

    investigate_services = ["500"]
    verified_services = {svc:[] for svc in investigate_services}
    for service in investigate_services:
        verified_services[service] += oper_states(conn, service)
        verified_services[service] += evpn_rr_healthy(conn, service)
        verified_services[service] += sites_reachable(conn, service)
        verified_services[service] += clients_reachable(conn, service)

    for service in investigate_services:
        print_verified_results(verified_services[service], "evpn-{vpls,vprn}-%s" % service)

if __name__ == "__main__":
    main()