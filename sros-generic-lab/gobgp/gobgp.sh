#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# configure IP address
bash /gobgp/ipaddr.sh
# start gobgpd daemon
sleep 180
gobgpd -t yaml -f /gobgp/gobgp.yml &
sleep 5

# make ipv4 BGP announcement
bash /gobgp/ipv4.sh
