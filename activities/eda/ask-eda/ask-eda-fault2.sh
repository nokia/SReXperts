#!/usr/bin/env bash
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

if eval "$(echo 'ZG9ja2VyIGV4ZWMgY2xhYi1zcmV4cGVydHMtY2xpZW50MTIgc2ggLWMgJ3N1ZG8gaXAgbGluayBzZXQgYm9uZDAgZG93biAmJiBzdWRvIGlwIGxpbmsgc2V0IGV0aDEgZG93biAmJiBzdWRvIGlwIGxpbmsgc2V0IGV0aDIgZG93biAmJiBzdWRvIGlwIGxpbmsgc2V0IGV0aDMgZG93bicK' | base64 -d)" &>/dev/null; then
  echo "Introducing fault into the data center fabric..."
  echo ""
  echo "Done!"
  echo "Head over to the EDA UI and use Ask EDA to troubleshoot it."
  echo ""
  echo "When you are done troubleshooting, run the following to restore the network:"
  echo "bash ~/activities/eda/ask-eda/ask-eda-restore.sh"
else
  echo "Something went wrong, please check with an instructor..."
fi