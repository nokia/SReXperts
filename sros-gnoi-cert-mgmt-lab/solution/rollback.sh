#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


certname='cert1'
cert_profile_name="grpc-tls-certs"
server_cipher_list="grpc-cipher-list"
server_tls_profile_name="grpc-tls-profile"

targets="$(docker ps -f label=containerlab=certs --format {{.Names}} | paste -s -d, -)"

# change the gRPC server back to unsecure
gnmic -a $targets -u admin -p admin --skip-verify set \
        --encoding json --print-request \
        --update-path /configure/system/grpc --update-value '{"allow-unsecure-connection":[null]}'

# delete tls profile
# delete ciphers
# delete certificate profile
gnmic -a $targets -u admin -p admin --insecure set \
        --delete /configure/system/security/tls/server-tls-profile[server-profile-name=${server_tls_profile_name}] \
        --delete /configure/system/security/tls/server-cipher-list[server-cipher-list-name=${server_cipher_list}] \
        --delete /configure/system/security/tls/cert-profile[cert-profile-name=${cert_profile_name}]

# delete certificates
gnoic -a $targets \
        --insecure -u admin -p admin \
        cert revoke \
        --id $certname

gnoic -a $targets \
        --insecure -u admin -p admin \
        cert get \
        --id $certname

# disable gNOI
echo "disabling gNOI cert Mgmt"
gnmic -a $targets \
        -u admin -p admin --insecure set \
        --update-path /configure/system/grpc/gnoi/cert-mgmt/admin-state --update-value disable

echo "denying gNOI cert-mgmt RPCs"
gnmic -a $targets -u admin -p admin --insecure set \
        --prefix /configure/system/security/aaa/local-profiles/profile[user-profile-name="administrative"]/grpc/rpc-authorization \
        --update-path gnoi-cert-mgmt-cangenerate --update-value deny \
        --update-path gnoi-cert-mgmt-getcert --update-value deny \
        --update-path gnoi-cert-mgmt-install --update-value deny \
        --update-path gnoi-cert-mgmt-revoke --update-value deny \
        --update-path gnoi-cert-mgmt-rotate --update-value deny 