# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

# to remove the default playground fabric and associated resources

kubectl delete toponodes -n eda --all

kubectl delete interfaces -n eda --all

kubectl delete topolink -n eda --all