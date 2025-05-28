#!/bin/bash
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


edactl="kubectl -n eda-system exec \$(kubectl -n eda-system get pods -l eda.nokia.com/app=eda-toolbox -o jsonpath='{.items[0].metadata.name}') -- edactl"

# latest transaction ID
TX_ID=$(eval $edactl transaction | tail -1 | awk '{print $1}')
TX_HASH=$(eval $edactl transaction ${TX_ID} | grep commit-hash | awk '{print $2}')

echo "$TX_ID $TX_HASH" > /opt/srexperts/eda-init-tx
