#!/bin/sh
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


# Before we deploy the fabric, we need to remove some default allocation pools to keep the UI clean and let attendees create pools as they need them.

kubectl get -n eda indexallocationpool -o name | \
  grep -v "srexperts-asnpool\|irb-subif-pool\|tunnel-index-pool\|vlan-pool\|lagid-pool" | \
  xargs kubectl delete -n eda

kubectl get -n eda ipallocationpool -o name | \
  grep -v "srexperts" | xargs kubectl delete -n eda

kubectl delete -n eda --all ipinsubnetallocationpool

kubectl delete -n eda --all subnetallocationpool
