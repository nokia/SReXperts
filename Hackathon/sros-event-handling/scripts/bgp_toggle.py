#!/usr/bin/env python3

# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

 
import sys
import time
from pysros.management import connect
from pysros.exceptions import ModelProcessingError


def main():
    print("Connecting to helper, this can take several minutes the first time")
    connection_object = connect(
        host="clab-sros-eh-helper1",
        username="admin",
        password="admin",
        hostkey_verify=False
    )
    print("Connection successful")
    path = '/nokia-conf:configure/router[router-name="Base"]/interface'
    if len(sys.argv) >= 2 and sys.argv[1] == "up":
        new_state = "enable"
    else:
        new_state = "disable"
    print("Changing admin state on interfaces facing RR to %s" % new_state)
    for peer in ["1", "2", "3"]:
        payload = {
            "internet_rr"+peer: {
                "admin-state" : new_state,
            }
        }
        connection_object.candidate.set(path, payload, commit=True)
        time.sleep(1)

if __name__ == "__main__":
    main()
