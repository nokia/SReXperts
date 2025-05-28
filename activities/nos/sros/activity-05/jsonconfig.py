#!/usr/bin/env python
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


import json
import sys

from pysros.exceptions import ModelProcessingError
from pysros.management import connect, sros


def get_connection(host="clab-srexperts-pe1", user="admin", password=None):
    """Obtain a connection to the router.  This wrapper function to the pySROS connect
    method provides some defaults for the parameters and some error (Exception) handling.
    You will need to supply details when calling this function if you are executing this
    application remotely.

    Args:
        host (str, optional): Router to be configured (IP address or hostname). Defaults to "clab-srexperts-pe1".
        user (str, optional): Username. Defaults to "admin".
        password (_type_, optional): Password. Defaults to None.

    Raises:
        SystemExit: Failed to creation Connection object
        SystemExit: Failed to create mode-driven schema
        SystemExit: Failed to connect

    Returns:
        pysros.management.Connection: Connection object
    """
    try:
        connection_object = connect(
            host=host,
            username=user,
            password=password,
            hostkey_verify=False,
        )
        return connection_object
    except RuntimeError as error1:
        print(
            "Failed to connect during the creation of the Connection object. Error:",
            error1,
        )
        raise SystemExit()
    except ModelProcessingError as error2:
        print("Failed to create model-driven schema.  Error:", error2)
        raise SystemExit()
    except Exception as error3:
        print("Failed to connect.  Error:", error3)
        raise SystemExit()


def read_file(filename, format="json"):
    """Read in a file in various formats.

    Args:
        filename (str): Filename
        format (str, optional): Format of the data in the file. Defaults to "json".

    Raises:
        NotImplemented: Alternative formats are not implemented

    Returns:
        str: Contents of the file
    """
    if format == "json":
        try:
            with open(filename, "r") as input_file:
                data = json.load(input_file)
                return json.dumps(data)
        except ValueError as error:
            print("Failed to read file. Error:", error)
            raise SystemExit()
    else:
        raise NotImplemented


def convert_data(
    connection_object,
    data,
    source_format="json",
    destination_format="pysros",
):
    """Convert between structure data formats of encoded YANG according to a specific
    devices Connection object.  This function provides a wrapper around the pySROS
    convert method for use in this activity.

    Args:
        connection_object (pysros.management.Connection): Connection object
        data (str): Data payload to be converted
        source_format (str, optional): Encoding of source data. Defaults to "json".
        destination_format (str, optional): Encoding of resulting data. Defaults to "pysros".

    Raises:
        SystemExit: Failed to convert the data

    Returns:
        str or dict: Converted data.  A string when encoded as JSON IETF or XML, a dictionary
        when encoded as pySROS.
    """
    try:
        return connection_object.convert(
            "/",
            data,
            source_format=source_format,
            destination_format=destination_format,
        )
    except Exception as error:
        print("Failed to convert configuration.  Error:", error)
        raise SystemExit()


def read_input():
    """Obtain input from stdin.  Terminate the input with <ctrl>-d on a new line.

    Returns:
        str: Obtained input data
    """
    data = []
    print(
        "Enter your JSON IETF encoded configuration.  Press <ctrl>-d on a new line to finish."
    )
    while True:
        try:
            line = input()
        except EOFError:
            break
        data.append(line)
    return "\n".join(data)


def arguments():
    """Obtain command line arguments.  Test for the right number of arguments
    and the specific input options provided.

    Returns:
        str: "file" or "stdin"
    """

    def print_help_and_exit():
        print("Requires the string file or stdin as an input parameter")
        raise SystemExit()

    if not len(sys.argv) == 2:
        print_help_and_exit()
    if not any(item in sys.argv for item in ["file", "stdin"]):
        print_help_and_exit()
    return sys.argv[1]


def main():
    """The initial function definition."""
    args = arguments()
    connection_object = get_connection()
    if args == "file":
        if sros():
            file = "cf3:/green.json"
        else:
            file = "green.json"
        data = read_file(file)
    elif args == "stdin":
        data = read_input()
    else:
        raise NotImplemented
    pysros_config = convert_data(connection_object, data)
    try:
        connection_object.candidate.set(
            "/configure", pysros_config.pop(next(iter(pysros_config)))
        )
    except Exception as error:
        print("Failed to configure the device. Error:", error)
        raise SystemExit()
    connection_object.disconnect()


if __name__ == "__main__":
    main()
