#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


self=10.55.13.1

# Define BGP attributes
attr_v4="
  -a ipv4 \
  origin egp \
  nexthop $self \
  med 100 \
"

# Starting IP block, modify to suit your needs
IP_BASE_1="192.10.10"
IP_BASE_2="193.20.10"
IP_BASE_3="193.30.10"
IP_BASE_4="193.40.10"

START=0
END=250

for ((i=START; i<=END; i++))
do
  # Generate unique /32 subnet for each prefix
  PREFIX_1="${IP_BASE_1}.$i/32"
  PREFIX_2="${IP_BASE_2}.$i/32"
  PREFIX_3="${IP_BASE_3}.$i/32"
  PREFIX_4="${IP_BASE_4}.$i/32"

  # Announce the routes
  gobgp global rib add $PREFIX_1 $attr_v4
  gobgp global rib add $PREFIX_2 $attr_v4
  gobgp global rib add $PREFIX_3 $attr_v4
  gobgp global rib add $PREFIX_4 $attr_v4
done
