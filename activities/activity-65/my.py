#!/usr/bin/env python3
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""
Capture-size monitor for a Nokia SR-OS pcap session.
Stops the capture, rolls over file, and restarts when the file
exceeds a configurable size threshold.
"""

import sys
import time
from pysros.management import connect # pyexec provides this module

#-------------------------------------------------------------------
#Configuration (adjust as needed)
#-------------------------------------------------------------------
SERVICE_NAME = "test-pcap"
SESSION_NAME = "test"
SIZE_THRESHOLD = 30000 # bytes
SLEEP_AFTER_STOP = 2 # seconds
SLEEP_AFTER_MOVE = 2 # seconds

#-------------------------------------------------------------------
def get_state_and_size(conn):
    #Retrieve session state and file size in a single RPC.
    
    path = "/nokia-state:state/mirror/mirror-dest[service-name='{}']".format(SERVICE_NAME) + "/pcap[session-name='{}']".format(SESSION_NAME)
    
    data = conn.running.get(path)
    state = data.get("session-state")
    # Convert the size leaf to an integer for comparison
    size = data.get("file-size")
    return state, size
#-------------------------------------------------------------------
def main():
    # ------------------------------------------------------------------
    # Connect to the local router (pyexec runs on the router itself)
    # ------------------------------------------------------------------
    try:
        conn = connect()
    except Exception as exc:
        print("Failed to connect to the router: {0}".format(exc))
        sys.exit(1)

    # ------------------------------------------------------------------
    # Get current session state and file size
    # ------------------------------------------------------------------
    state, size = get_state_and_size(conn)

    if str(state) != "in-progress":
        print("Session is not in-progress – nothing to do.")
        sys.exit(0)

    if size <= SIZE_THRESHOLD:
        print('Session "{0}" size {1} bytes – below threshold.'.format(
            SESSION_NAME, size))
        sys.exit(0)

    print('Session "{0}" size {1} bytes – above threshold.'.format(
        SESSION_NAME, size))

    # ------------------------------------------------------------------
    # Stop the capture
    # ------------------------------------------------------------------
    try:
        conn.cli('perform pcap "{0}" capture stop'.format(SESSION_NAME))
    except Exception as exc:
        print("Failed to stop capture: {0}".format(exc))
        sys.exit(1)

    print('Capture stopped for session "{0}"'.format(SESSION_NAME))
    time.sleep(SLEEP_AFTER_STOP)

    # ------------------------------------------------------------------
    # Rollover the pcap file
    # ------------------------------------------------------------------
    print("Pcap file rollover...")
    try:
        conn.cli('file move "{0}.pcap" "{0}.pcap.1" force'.format(SESSION_NAME))
    except Exception as exc:
        print("File move failed: {0}".format(exc))
        sys.exit(1)

    time.sleep(SLEEP_AFTER_MOVE)

    # ------------------------------------------------------------------
    # Restart the capture
    # ------------------------------------------------------------------
    try:
        conn.cli('perform pcap "{0}" capture start'.format(SESSION_NAME))
    except Exception as exc:
        print("Failed to restart capture: {0}".format(exc))
        sys.exit(1)

    print('Capture restarted for session "{0}"'.format(SESSION_NAME))
#---------------------------------------------------------------------
if __name__ == "__main__":
    main()
