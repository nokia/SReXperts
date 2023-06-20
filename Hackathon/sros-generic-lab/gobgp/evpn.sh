#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


# Assuming a peer is already set up with ASN 65000
RD_BASE="65000"
ETAG=100
LABEL=100

for ((i=1; i<=10; i++))
do
  # Generate unique MAC address for each route
  MAC=$(printf '00:11:22:%02x:%02x:%02x' $((i>>16)) $((i>>8&255)) $((i&255)))

  # Generate unique IP address for each route
  IP="192.0.2.$((i%254+1))"

  # Generate unique Route Distinguisher for each route
  RD="${RD_BASE}:$i"

  # Announce the EVPN route
  gobgp global rib add -a evpn "route distinguisher $RD macadv $MAC $IP rd $RD etag $ETAG label $LABEL"
done
