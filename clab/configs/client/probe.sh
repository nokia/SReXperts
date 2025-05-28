#!/bin/bash
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

#usage: ./probe.sh <target-ip> [interval in seconds]

# Activity #20 SR Linux basic agent - Probe client

TARGET="$1"
PORT="9999"
INTERVAL="${2:-0.5}"  # Default interval between probes (in seconds)
TIMEOUT=1
echo "Probing $TARGET:$PORT using TCP..."

while true; do
    RESPONSE=$(echo "ping" | socat -T "$TIMEOUT" - TCP:"$TARGET":$PORT,connect-timeout="$TIMEOUT")

    if [ -n "$RESPONSE" ]; then
        echo "$(date) - Response from $RESPONSE"
        sleep "$INTERVAL"
    else
        echo "$(date) - No response or refused connection"
        sleep $INTERVAL
    fi
    
done