# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import sys
from pysros.management import connect

def main():
    instance_id = sys.argv[1]
    with open("cf3:/bof-dns.cfg", "w+") as file_object:
        file_object.write("########################################\n")
        file_object.write("# Configure DNS\n")
        file_object.write("# https://containerlab.dev/manual/kinds/vr-sros/#boot-options-file\n")
        file_object.write("########################################\n")
        file_object.write("/bof private\n")
        file_object.write("dns primary-server 10.128.%s.15\n" % instance_id)
        file_object.write("commit\n")
        file_object.write("exit all\n")

if __name__ == "__main__":
    main()
