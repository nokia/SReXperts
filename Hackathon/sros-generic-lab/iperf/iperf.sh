#!/usr/bin/env bash

# Copyright 2020 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# Start iperf3 server in the background
# with 8 parallel tcp streams,
# using ipv4 interfaces

iperf3 -c $1 -t 10000 -i 1 -p 5201 -P 8 -b 10M -M 1460 &
