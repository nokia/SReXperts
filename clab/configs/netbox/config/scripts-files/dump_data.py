# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from extras.scripts import Script

class DumpData(Script):
    class Meta():
        name = "Dump Data"
        description = "Dump data structure passed to this script"

    def run(self, data, commit=True):
        return data
