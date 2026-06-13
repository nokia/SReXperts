#!/bin/bash
# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

/bin/sed -i "s/lab use only/lab use only\n        file.write(f'primary-dns      10.128.${INSTANCE_ID}.15\\\\n')\n/g" /opt/nokia/entrypoint
/bin/tini -s /opt/nokia/entrypoint --
