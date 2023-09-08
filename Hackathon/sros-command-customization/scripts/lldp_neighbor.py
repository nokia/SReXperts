#!/usr/bin/env python3

# ## lldp_neighbor.py
#   Copyright 2022 Nokia
# ##

# pylint: disable=consider-using-f-string

"""Re-implementation of "show system lldp neighbor" intended to improve
    upon existing SR OS command and remove some of the known limitations
Tested on: SR OS 22.5.R2
"""


import sys
from pysros.management import connect
from pysros.exceptions import ModelProcessingError


translate_lldp_type = {
    "nearest-bridge": "NB",
}


def get_connection():
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
            host="clab-srx-sros1",
            username="admin",
            password="admin",
            hostkey_verify=False
        )
    except RuntimeError as error1:
        print("Failed to connect.  Error:", error1)
        sys.exit(-1)
    except ModelProcessingError as error2:
        print("Failed to create model-driven schema.  Error:", error2)
        sys.exit(-2)
    return connection_object


def print_table(rows, col_min_widths):
    """Function definition to print a table in the form of a list
    of rows with information regarding minimal column width to
    the text console of an SR OS device or a remote operator's
    terminal.
    :parameter rows: the data formatted as rows
    :type rows: list
    :paramater col_min_widths:  a list containing integer data
                                corresponding to a minimum width
                                for each column.
    :type col_min_widths: list
    """

    red = "\u001b[31;1m"
    green = "\u001b[32;1m"
    yellow = "\u001b[33;1m"
    brown = "\u001b[34;1m"
    cyan = "\u001b[35;1m"
    reset_color = "\u001b[0m"
    extra_text = (
        green + "EMOJIs : " + reset_color +
        yellow + "\U0001f600" + reset_color + " " +
        brown + "\U0001f4a9" + reset_color + " " +
        red + "\U0001F920" + reset_color
    )

    cols = [
        (6 + max(col_min_widths[0], len("Lcl Port")), "Lcl Port"),
        (1 + max(col_min_widths[1], len("Scope")), "Scope"),
        (2 + max ( col_min_widths[2], len("Remote Chassis ID")), "Remote Chassis ID"),
        (2 + max ( col_min_widths[3], len("Index")), "Index"),
        (2 + max ( col_min_widths[4], len("Remote Port")), "Remote Port"),
        (1 + max ( col_min_widths[5], len("Remote Sys Name")), "Remote Sys Name"),
    ]

    # Initalize the Table object with the heading and columns.
    # table = Table("Interfaces modified by script (up -> down) ", cols)
    print(sum((x[0] for x in cols)) * "=")
    print(
        "NB = nearest-bridge   NTPMR = nearest-non-tpmr   "
        "NC = nearest-customer  " + extra_text
    )
    print(sum((x[0] for x in cols)) * "=")
    print(
        "%-*s%-*s%-*s%-*s%-*s%-*s"
        % (
            cols[0][0],
            "Lcl Port",
            cols[1][0],
            "Scope",
            cols[2][0],
            "Remote Chassis ID",
            cols[3][0],
            "Index",
            cols[4][0],
            "Remote Port",
            cols[5][0],
            "Remote Sys Name",
        )
    )
    for row in rows:
        print(
            "%-*s%-*s%-*s%-*s%-*s%-*s"
            % (
                cols[0][0],
                row[0],
                cols[1][0],
                row[1],
                cols[2][0],
                row[2],
                cols[3][0],
                row[3],
                cols[4][0],
                row[4],
                cols[5][0],
                cyan + row[5] + reset_color,
            )
        )
    print(sum((x[0] for x in cols)) * "=")
    print("Number of neighbors : %s" % len(rows))


def find_lldp_ports(conn):
    """Function that collects information about ports that are
    or are not configured with LLDP and, if they are, which types.

    These ports are returned along with the configured LLDP types found.

    :parameter conn: connection to an SR OS device
    :type conn: .Connection
    :returns: Dictionary mapping port to configured LLDP types
    :rtype: :py:class:`dict`
    """
    configured_ports = conn.running.get(
        "/nokia-conf:configure/port", defaults=True
    )
    lldp_config_types_per_port = {}
    for port_key, config in configured_ports.items():
        card, mda, port_id = port_key.split("/", 2)
        if "c" not in port_id or "/" in port_id:
            if "ethernet" not in config or "lldp" not in config["ethernet"]:
                # means it's all defaults
                # or there is no LLDP set on the port
                continue
            lldp_config_types_per_port[
                card + "/" + mda + "/" + port_id
            ] = config["ethernet"]["lldp"]["dest-mac"].keys()
        else:
            # host port case
            pass
    return lldp_config_types_per_port


def check_lldp(connection):
    """Function uses find_lldp_ports to see which parts of the state model
    should be consulted for the necessary information to re-build the table
    created by the native "show system lldp neighbor" command.

    This information is returned as the first element of the tuple,
    the second element is a list containing minimal widths to be used
    to be able to show all the values properly, based on the values
    intended to be within those cells.

    :parameter connection: connection to an SR OS device
    :type connection: .Connection
    :returns: tuple of result and min_len
    :rtype: :py:class:`tuple`
    """
    # ordered list of tuples?
    result = []
    min_len = [0] * 6

    for port, lldp_types in find_lldp_ports(connection).items():
        for lldp_type in lldp_types:
            lldp_state_info = connection.running.get(
                '/nokia-state:state/port[port-id="%s"]/ethernet/lldp/dest-mac[mac-type="%s"]'
                % (port, lldp_type)
            )
            if "remote-system" not in lldp_state_info:
                continue
            remote_systems = lldp_state_info["remote-system"]
            for index, remote_system in remote_systems.items():
                new_tuple = (
                    port,
                    translate_lldp_type[lldp_type],
                    remote_system["chassis-id"].data,
                    str(index[1]),
                    remote_system["port-description"].data,
                    remote_system["system-name"].data,
                )
                result.append(new_tuple)
                for i in enumerate(new_tuple):
                    if len(i[1]) > min_len[i[0]]:
                        min_len[i[0]] = len(i[1])
    return result, min_len


if __name__ == "__main__":
    sr = get_connection()
    results, col_widths = check_lldp(sr)
    print_table(results, col_widths)
