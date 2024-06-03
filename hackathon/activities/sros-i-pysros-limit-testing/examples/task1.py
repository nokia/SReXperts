# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.management import connect,sros
from pysros.pprint import Table
import time


def table_builder(rows, title):
    cols = [(60, "Test"), (15, "Result", '>'), (4, "")]
    table = Table(title, columns=cols,
                  showCount="Number of tests")
    table.print(rows)


def main():
    conn = connect(username="<username>", password="<password>", host='clab-srexperts-p2', hostkey_verify=False)

    print(
        "Number of in-octets on port 1/1/c1/1 is %s" %
        conn.running.get('/state/port[port-id="1/1/c1/1"]/statistics/in-octets')
    )

    table_title = "SR OS limit testing (off-box)"
    running_avg = 0
    num_iter = 10

    result = []

    # The first for-loop encountered here loops over a list of tuples, where each tuple identifies a task.
    # In the tuples, each one has three values:
    #    a name for the test, a path to retrieve from the router and a filter value
    # This follows along with the lab activity and
    #
    # The first tuple is getting a specific port counter, a small amount of data
    #
    # The second test collects a far larger payload and should behave differently
    #
    # The third test uses the same path filtered to see if that helps, or if the client
    # still has to pull in all the data before being able to apply a filter to it
    #
    # The second for loop repeats each test a number of times to get to an acceptable
    # average value. Feel free to lower or increase it.
    #
    for info,path,filter_value in [
        ("Retrieving a single value", '/state/port[port-id="1/1/c1/1"]/statistics/in-octets', None),
        ("Retrieving the entire state",'/state', None),
        ("Retrieving the entire state but filtered", '/state', {
                "port": {
                    "port-id": "1/1/c1/1",
                    "statistics": {
                    }
                }
            }
        )
    ]:
        for i in range(1,num_iter+1):
            # if the program runs on SR OS this path is used
            if sros():
                table_title = "SR OS limit testing (on-box)"
                time1 = time.ticks_us()
                checked_value = conn.running.get(path, filter=filter_value)
                time2 = time.ticks_us()
                measurement = time.ticks_diff(time2, time1)
            else:
                time1 = time.perf_counter()
                checked_value = conn.running.get(path, filter=filter_value)
                time2 = time.perf_counter()
                measurement = (time2 - time1) * 1000000
            running_avg = running_avg + (measurement - running_avg) / i

        result.append((info, "%.2f us"%running_avg))

    table_builder(result, table_title)


if __name__ == '__main__':
    main()
