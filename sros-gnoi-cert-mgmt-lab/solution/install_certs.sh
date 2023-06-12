#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


certname='cert1'
cert_profile_name="grpc-tls-certs"
server_cipher_list="grpc-cipher-list"
server_tls_profile_name="grpc-tls-profile"

targets="$(docker ps -f label=containerlab=certs --format {{.Names}} | paste -s -d, -)"

gnmi_base_insecure_cmd="gnmic -a $targets -u admin -p admin --insecure"
gnmi_base_no_verify_cmd="gnmic -a $targets -u admin -p admin --skip-verify"
gnmi_base_secure_cmd="gnmic -a $targets -u admin -p admin --tls-ca certs/cert.pem"

echo "create $certname in all targets"
gnoic -a $targets \
        --insecure -u admin -p admin \
        cert install \
        --gen-csr \
        --print-csr \
        --validity 300s \
        --ca-key certs/key.pem \
        --ca-cert certs/cert.pem \
        --id $certname

echo "check $certname in all targets"

gnoic -a $targets \
        --insecure -u admin -p admin \
        cert get \
        --id $certname

# create SROS server TLS profile
gnmic -a $targets -u admin -p admin --insecure set \
        --update-path /configure/system/security/tls/cert-profile[cert-profile-name=${cert_profile_name}]/entry[entry-id=1]/certificate-file --update-value $certname.crt \
        --update-path /configure/system/security/tls/cert-profile[cert-profile-name=${cert_profile_name}]/entry[entry-id=1]/key-file --update-value $certname.key \
        --update-path /configure/system/security/tls/cert-profile[cert-profile-name=${cert_profile_name}]/admin-state --update-value enable

# tls12 ciphers
gnmic -a $targets -u admin -p admin --insecure set \
        --update-path /configure/system/security/tls/server-cipher-list[server-cipher-list-name=${server_cipher_list}]/tls12-cipher[index=1]/name --update-value tls-rsa-with3des-ede-cbc-sha \
        --update-path /configure/system/security/tls/server-cipher-list[server-cipher-list-name=${server_cipher_list}]/tls12-cipher[index=2]/name --update-value tls-rsa-with-aes128-cbc-sha \
        --update-path /configure/system/security/tls/server-cipher-list[server-cipher-list-name=${server_cipher_list}]/tls12-cipher[index=3]/name --update-value tls-rsa-with-aes256-cbc-sha \
        --update-path /configure/system/security/tls/server-cipher-list[server-cipher-list-name=${server_cipher_list}]/tls12-cipher[index=4]/name --update-value tls-rsa-with-aes128-cbc-sha256 \
        --update-path /configure/system/security/tls/server-cipher-list[server-cipher-list-name=${server_cipher_list}]/tls12-cipher[index=5]/name --update-value tls-rsa-with-aes256-cbc-sha256 

# tls13 ciphers
gnmic -a $targets -u admin -p admin --insecure set \
        --update-path /configure/system/security/tls/server-cipher-list[server-cipher-list-name=${server_cipher_list}]/tls13-cipher[index=1]/name --update-value tls-aes256-gcm-sha384 \
        --update-path /configure/system/security/tls/server-cipher-list[server-cipher-list-name=${server_cipher_list}]/tls13-cipher[index=2]/name --update-value tls-aes128-gcm-sha256

# create server-tls-profile
gnmic -a $targets -u admin -p admin --insecure set \
        --update-path /configure/system/security/tls/server-tls-profile[server-profile-name=${server_tls_profile_name}]/cert-profile --update-value ${cert_profile_name} \
        --update-path /configure/system/security/tls/server-tls-profile[server-profile-name=${server_tls_profile_name}]/cipher-list --update-value ${server_cipher_list} \
        --update-path /configure/system/security/tls/server-tls-profile[server-profile-name=${server_tls_profile_name}]/admin-state --update-value enable 

# check tls-profile oper-state
# check server-tls-profile oper-state
gnmic -a $targets -u admin -p admin --insecure get \
        --path /state/system/security/tls/server-tls-profile/oper-state \
        --path /state/system/security/tls/cert-profile/oper-state

# change the gRPC server from unsecure to secure
gnmic -a $targets -u admin -p admin --insecure set \
        --update-path /configure/system/grpc/tls-server-profile --update-value ${server_tls_profile_name}

# --skip-verify
gnmic -a $targets -u admin -p admin --skip-verify get \
        --path /state/system/security/tls/server-tls-profile/oper-state \
        --path /state/system/security/tls/cert-profile/oper-state


# --tls-ca
gnmic -a $targets \
        -u admin -p admin \
        --tls-ca certs/cert.pem get \
        --path /state/system/security/tls/server-tls-profile/oper-state \
        --path /state/system/security/tls/cert-profile/oper-state


gnoic -a $targets \
        --tls-ca certs/cert.pem \
        -u admin -p admin \
        cert get \
        --id $certname