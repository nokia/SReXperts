#!/usr/bin/env python3

### Author: Mohammad Zaman- mohammad.zaman@nokia.com
#   Copyright 2023 Nokia
###



# Import sys for returning specific exit codes
from lib2to3.pytree import Base
from pathlib import Path
import sys
from pysros.pprint import Table

# Import the connect method from the management pySROS sub-module
from pysros.management import connect, Datastore

# Import the exceptions that are referenced so they can be caught on error.
from pysros.exceptions import ModelProcessingError


def get_connection(host=None, credentials=None):
    """Function definition to obtain a Connection object to a specific SR OS device
    and access the model-driven information."""

    # The try statement coupled with the except statements allow an operation(s) to be
    # attempted and specific error conditions handled gracefully
    try:
        connection_object = connect(
            host=host,
            username=credentials["username"],
            password=credentials["password"],
        )

        # Confirm to the user that the connection establishment completed successfully
        print("Connection established successfully")

        # Return the Connection object that we created
        return connection_object

    # This first exception is described in the pysros.management.connect method
    # and references errors that occur during the creation of the Connection object.
    # If the provided exception is raised during the execution of the connect method
    # the information provided in that exception is loaded into the e1 variable for use
    except RuntimeError as error1:
        print(
            "Failed to connect during the creation of the Connection object.  Error:",
            error1,
        )
        sys.exit(101)

    # This second exception is described in the pysros.management.connect method
    # and references errors that occur whilst compiling the YANG modules that have been
    # obtained into a model-driven schema.
    # If the provided exception is raised during the execution of the connect method the
    # information provided in that exception is loaded into the e2 variable for use.
    except ModelProcessingError as error2:
        print("Failed to create model-driven schema.  Error:", error2)
        sys.exit(102)

    # This last exception is a general exception provided in Python
    # If any other unhandled specific exception is thrown the information provided in
    # that exception is loaded into the e3 variable for use
    except Exception as error3:  # pylint: disable=broad-except
        print("Failed to connect.  Error:", error3)
        sys.exit(103)


def get_list_keys(connection_object, target, path):
    datastore = Datastore(connection_object, target)
    return datastore.get_list_keys(path)



# Fuction definition to output a SR OS style table to the screen
def print_table(port_info):
    """Setup and print the SR OS style table"""

    # Define the columns that will be used in the table.  Each list item
    # is a tuple of (column width, heading).
    cols = [
        (10, "Port"),
        (15, "In-Octets"),
        (15, "Out-Octets"),
        (15, "Difference"),
        (15, "Ingress BW")
    ]

    # Initalize the Table object with the heading and columns.
    table = Table("Ports with Details", cols, showCount="PORTS")

    # Print the output passing the data for the rows as an argument to the function.
    table.print(port_info)



def main():
    """Example general/main function"""

    # Define some user credentials to pass to the get_connect function
    credentials = {"username": "admin", "password": "admin"}

    # Call the get_connection function providing a hostname/IP and the credentials
    # Returns a Connection object for use in obtaining data from the SR OS device
    # or configuring that device
    connection_object = get_connection(  # pylint: disable=unused-variable
        host="clab-srx-wan1", credentials=credentials
    )
    assert connection_object

    port_info = []
    port_path = connection_object.running.get("/nokia-state:state/port")
    for i in port_path:
        if "port-id" in port_path[i].keys():
            port_id = port_path[i]['port-id'].data  
            in_oct = port_path[i]['statistics']['in-octets'].data
            out_oct = port_path[i]['statistics']['out-octets'].data
            abs_diff_oct = abs(out_oct - in_oct)
            bw = str((in_oct*8)/1000000)+'Mb'
            port_info.append([port_id,in_oct, out_oct, abs_diff_oct, bw])
    print_table(port_info)
    connection_object.disconnect()

if __name__ == "__main__":
    main()

