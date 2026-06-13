# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

### SreXperts 2026
### Activity 18 - Securing gRPC with mTLS 

import os
from pygnmi.client import gNMIclient
# avoid error messages in stdout as per https://github.com/akarneliuk/pygnmi/issues/120
import logging
from pygnmi.client import logger as gnmi_logger
gnmi_logger.setLevel(logging.CRITICAL + 1)
### SReXperts 2026
### Activity 18 - Securing gRPC with mTLS 
def main():
    """Main entrypoint function"""
    report = {}
    password=os.getenv("EVENT_PASSWORD")
    if password is None:
        raise ValueError("No Event password defined! Env variable not set.")

    for node in ["clab-srexperts-pe1", "clab-srexperts-ixp1"]: #optionally include additional nodes
        result = "no grpc"
        try:
            with gNMIclient(    target=(node,57400),
                                username="admin",
                                password=password,
                                insecure=True) as gc:
                _ = gc.capabilities()
                result = "unsecure"
        except Exception as e:
            pass
        if (result == "no grpc"):
            try:
                with gNMIclient(    target=(node,57400),
                                    username="admin",
                                    password=password,
                                    path_root="ca.pem") as gc:
                    _ = gc.capabilities()
                    result = "tls"
            except Exception as e:
                pass

        if (result == "no grpc"):
            try:
                with gNMIclient(    target=(node,57400),
                                    username="admin",
                                    password=password,
                                    path_root="ca.pem",
                                    path_cert="client.pem",
                                    path_key="client.key") as gc:
                    _ = gc.capabilities()
                    result = "mtls"
            except Exception as e:
                pass

        report[node] = result


    for node,result in report.items():
        print(f"{node:<20}: {result}")

if __name__ == "__main__":
    main()
