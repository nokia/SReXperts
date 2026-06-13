# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

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


def main():
    """Main execution point of the pre-commit script."""
    # Your implementation starts here!
    pass


if __name__ == "__main__":
    main()
