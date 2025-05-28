#!/bin/bash
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


edactl() {
    kubectl -n eda-system exec -it $(kubectl -n eda-system get pods -l eda.nokia.com/app=eda-toolbox -o jsonpath={.items[0].metadata.name}) -- edactl "$@"
}

TX_HASH=$(cat /opt/srexperts/eda-init-tx | cut -d ' ' -f 2)
edactl git restore $TX_HASH
