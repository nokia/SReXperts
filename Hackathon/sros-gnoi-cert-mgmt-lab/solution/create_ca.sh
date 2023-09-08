#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

mkdir -p certs

gnoic cert create-ca --cert-out certs/cert.pem --key-out certs/key.pem
ls -la certs/
openssl x509 -noout -text -in certs/cert.pem
openssl rsa -in certs/key.pem -check
