# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.management import connect,sros
import time
import sys

def flip_mode(mode):
    filename = sys.argv[0]
    if sros() and filename[:5] != 'cf3:/':
        filename = "cf3:/" + filename
    mode_inverse = {
        "timeout": "memory",
        "memory": "timeout"
    }
    with open(filename, "r+") as task2_file:
        contents = task2_file.read()
        contents = contents.replace(
            'mode = "%s"\n' % mode,
            'mode = "%s"\n' % mode_inverse[mode]
        )
        task2_file.seek(0)
        task2_file.write(contents)
        task2_file.truncate()


def main():
    mode = "memory"
    flip_mode(mode)
    conn = connect()

    if mode == "timeout":
        # To force a timeout (interpreter limit is set to 30 sec on P2)
        time.sleep(60)
    elif mode == "memory":
        # To force a memory limit error
        a = []
        while sros():
            #print(len(a))
            a.append(bytearray(10**6))


if __name__ == '__main__':
    main()
