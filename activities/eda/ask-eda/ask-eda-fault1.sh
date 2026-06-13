#!/usr/bin/env bash
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

if eval "$(echo 'Z25taWMgLWEgY2xhYi1zcmV4cGVydHMtbGVhZjExOjU3NDEwIC11IGFkbWluIC1wICRFVkVOVF9QQVNTV09SRCAtLXNraXAtdmVyaWZ5IHNldCAtLXVwZGF0ZS1wYXRoIC9pbnRlcmZhY2VbbmFtZT1ldGhlcm5ldC0xLzMxXS9hZG1pbi1zdGF0ZSAtLXVwZGF0ZS12YWx1ZSBkaXNhYmxlCg==' | base64 -d)" &>/dev/null; then
  echo "Introducing fault into the data center fabric..."
  echo ""
  echo "Done!"
  echo "Head over to the EDA UI and use Ask EDA to troubleshoot it."
else
  echo "Something went wrong, please check with an instructor..."
fi