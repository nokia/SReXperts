#!/bin/bash
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# start the probe responder: setsid /probe-responder.sh

# Activity #20 SR Linux basic agent - Probe server

#redirect stderr and stdout to a log file
exec >/tmp/"$0".log 2>&1

PORT=9999
HOSTNAME=$(hostname)

echo "Responder listening on TCP port $PORT..."
socat TCP-LISTEN:$PORT,reuseaddr,fork SYSTEM:"echo $HOSTNAME"
