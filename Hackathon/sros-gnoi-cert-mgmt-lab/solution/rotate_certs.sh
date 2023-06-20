#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


certname='cert1'

targets="$(docker ps -f label=containerlab=certs --format {{.Names}} | paste -s -d, -)"

echo "rotating $certname in all targets"

gnoic -a $targets \
        -u admin -p admin \
        --tls-ca certs/cert.pem \
        cert rotate \
        --gen-csr \
        --print-csr \
        --validity 300s \
        --ca-key certs/key.pem \
        --ca-cert certs/cert.pem \
        --id $certname -d

echo "check $certname in all targets"

gnoic -a $targets \
        -u admin -p admin \
        --tls-ca certs/cert.pem \
        cert get \
        --id $certname
