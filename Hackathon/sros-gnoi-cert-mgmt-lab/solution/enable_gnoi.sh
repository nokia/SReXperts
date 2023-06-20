#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


targets="$(docker ps -f label=containerlab=certs --format {{.Names}} | paste -s -d, -)"

echo "enabling gNOI cert Mgmt"

gnmic -a $targets \
        -u admin -p admin --insecure set \
        --update-path /configure/system/grpc/gnoi/cert-mgmt/admin-state --update-value enable


echo "authorizing gNOI cert-mgmt RPCs"

gnmic -a $targets -u admin -p admin --insecure set \
        --prefix /configure/system/security/aaa/local-profiles/profile[user-profile-name="administrative"]/grpc/rpc-authorization \
        --update-path gnoi-cert-mgmt-cangenerate --update-value permit \
        --update-path gnoi-cert-mgmt-getcert --update-value permit \
        --update-path gnoi-cert-mgmt-install --update-value permit \
        --update-path gnoi-cert-mgmt-revoke --update-value permit \
        --update-path gnoi-cert-mgmt-rotate --update-value permit
