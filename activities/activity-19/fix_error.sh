# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

gnmic -a clab-srexperts-pe2 -u admin -p $EVENT_PASSWORD --insecure set \
    --update-path '/configure/macsec/connectivity-association[ca-name=CA_A]/static-cak/pre-shared-key[psk-id=1]/cak' \
    --update-value 'AA0123456789ABCDEF0123456789ABCD' &> /dev/null