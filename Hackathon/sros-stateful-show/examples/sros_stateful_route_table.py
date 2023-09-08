# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from uio import open
from uos import listdir,remove
from utime import localtime, strftime
import sys
from time import time
from pysros.management import connect
from pysros.pprint import Table


def router_timestamp_to_epoch_time(router_timestamp_string, mktime_function, struct_time_class):
    day,time,timezone = router_timestamp_string.split('_')[1].split('-')
    year,month,day = day[:4], day [4:6], day[6:]
    hour,minute,second = [time[i:i+2] for i in range(0, len(time), 2)]
    # could do something with TZ and DST here
    # ignore week-day and year-day
    # datetime!
    return mktime_function(struct_time_class((int(year),int(month),int(day),int(hour),int(minute),int(second),0,0,0)))


def create_log(message):
    """
    Helper function to display log messages with a timestamp
    """
    curr_time = localtime()
    time_str = "%g/%g/%g %g:%g:%g %s" % (
        curr_time.tm_year,
        curr_time.tm_mon,
        curr_time.tm_mday,
        curr_time.tm_hour,
        curr_time.tm_min,
        curr_time.tm_sec,
        "CEST",
    )
    time_str = strftime("%Y/%m/%d %H:%M:%S", curr_time)
    format_str = "At time %s: %s" % (time_str, message)

    return(format_str)


def print_table(rows, run_number):
    """Setup and print the SR OS style table"""
    cols = [
        (24, "Prefix"),
        (13, "Protocol"),
        (24, "Next Hop"),
    ]
    table = Table("Routing table snapshot", cols, showCount="Routes")
    print(create_log("Run number %s, result:\n" % run_number))
    table.print(rows)

def output(routes, run_number):
    rows = []
    message = create_log("Run number %s, result:\n" % run_number)

    for prefix,value in sorted(routes.items()):
        next_hop_ip = ""
        if value['protocol'].data != "local":
            next_hop_ip = value['nexthop'][0]['nexthop-ip']
        rows.append((prefix, value['protocol'].upper(), next_hop_ip))
        message += "\tPrefix %+18s is learned through protocol  %+8s"\
            %(prefix, value['protocol'].upper())
        if value['protocol'].data != "local":
            message += " via %s\n" % next_hop_ip
        else:
            message += "\n"

    print_table(rows, run_number)
    return message

def file_write(message):
    with open("cf3:/sros_stateful/current", mode="w") as file_object:
        file_object.write(message)


def get_route_table_information(connection):
    rt_filter = {
        "protocol": {},
        "nexthop": {
            "nexthop-ip": {}
        }
    }
    rt_state = connection.running.get(
        '/nokia-state:state/router[router-name="Base"]/route-table/unicast/ipv4/route',
        filter=rt_filter,
    )
    return rt_state

def get_script_results_location(connection):
    result = set()
    cfg_path = '/nokia-conf:configure/system/script-control'
    all_cron_cfg = connection.running.get(cfg_path)['script-policy']
    for policy_name, policy in all_cron_cfg.items():
        result.add(policy["results"].data)
    return result


def is_file_older_than_hour(date, current_time):
    return current_time > date+3600

def get_newest_run_number(connection):
    paths_to_results = get_script_results_location(connection)
    curr_time = time()
    found_stored_runs = [-1]

    for path in paths_to_results:
        cron_result_files = listdir(path)
        for i in cron_result_files:
            with open(path+i, "r") as older_file:
                line = older_file.readline()
                # At time 2023/06/10 14:11:26: run number 0 was executed, result:
                try:
                    found_stored_runs.append(int(line.split(' ')[6][:-1]))
                except IndexError as e:
                    # disregarding shenanigans, running script instance file already exists here
                    # so skip that one
                    pass
    return max(found_stored_runs)+1


def control_cron_output(connection):
    from utime import time,struct_time,mktime         # type: ignore
    paths_to_results = get_script_results_location(connection)
    curr_time = time()
    for path in paths_to_results:
        cron_result_files = listdir(path)
        for individual_file in cron_result_files:
            if individual_file == "current":
                continue
            file_creation_date = router_timestamp_to_epoch_time(individual_file, mktime, struct_time)
            if curr_time - file_creation_date > 120:
                #print("Deleting file %s:\n/file remove %s" %(path+individual_file, path + individual_file))
                remove(path + individual_file)


def main():
    """The main procedure.  The execution starts here."""
    connection = connect(
        host="local connection only - unused",
        username="local connection only - unused",
    )
    run_nr = get_newest_run_number(connection)

    if len(sys.argv) == 0:
        # CRON
        control_cron_output(connection)
        routes = get_route_table_information(connection)
        output(routes, run_nr)
    else:
        # PYEXEC
        control_cron_output(connection)
        routes = get_route_table_information(connection)
        text_output = output(routes, run_nr)
        file_write(text_output)

    connection.disconnect()


if __name__ == "__main__":
    main()
