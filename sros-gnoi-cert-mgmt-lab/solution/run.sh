#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


./deploy_lab.sh

./enable_gnoi.sh

./install_certs.sh

echo "waiting 60s before rotating the certificate(s)"
sleep 60

./rotate_certs.sh
