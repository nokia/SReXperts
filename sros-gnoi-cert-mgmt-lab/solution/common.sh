#!/bin/bash
# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


get_target_IP () {
  target=$1
  #  echo $target
  echo $(docker inspect -f '{{ .NetworkSettings.Networks.clab.IPAddress }}' $target))
}