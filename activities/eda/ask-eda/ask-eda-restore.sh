#!/usr/bin/env bash
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

if eval "$(echo 'ZG9ja2VyIGV4ZWMgY2xhYi1zcmV4cGVydHMtY2xpZW50MTIgc2ggLWMgJ3N1ZG8gaXAgbGluayBzZXQgZXRoMSB1cCAmJiBzdWRvIGlwIGxpbmsgc2V0IGV0aDIgdXAgJiYgc3VkbyBpcCBsaW5rIHNldCBldGgzIHVwICYmIHN1ZG8gaXAgbGluayBzZXQgYm9uZDAgZG93biAmJiBzdWRvIGlwIGxpbmsgc2V0IGJvbmQwIHVwJwo=' | base64 -d)" &>/dev/null; then
  echo "Fixing the state of the data center fabric..."
  echo ""
  echo "Done!"
else
  echo "Something went wrong, please check with an instructor..."
fi