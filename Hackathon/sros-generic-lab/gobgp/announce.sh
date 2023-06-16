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

# Populate prefixes
gobgp global rib add 192.168.109.200/32 $attr_v4
gobgp global rib add 192.168.109.201/32 $attr_v4
gobgp global rib add 192.168.109.202/32 $attr_v4