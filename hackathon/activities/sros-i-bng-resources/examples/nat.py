# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.management import connect
from utime import localtime, strftime


def print_log(message):
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

    print(format_str)


def ceil(input_number):
    return int(input_number+1) if input_number-0.5 < int(input_number) and input_number != int(input_number) else round(input_number)


def get_nat_binding_avg(connection_object):
    num_hosts = connection_object.running.get('/nokia-state:state/service/nat/nat-policy[name="NAT_POL1"]/statistics/mda[mda-id="2/1"]/hosts/active')
    num_bindings = { }
    for protocol in ['tcp', 'udp', 'icmp-query', 'gre-query']:
        num_bindings[protocol] = connection_object.running.get('/nokia-state:state/service/nat/nat-policy[name="NAT_POL1"]/statistics/mda[mda-id="2/1"]/sessions/%s/created' % protocol) - connection_object.running.get('/nokia-state:state/service/nat/nat-policy[name="NAT_POL1"]/statistics/mda[mda-id="2/1"]/sessions/%s/destroyed' % protocol)
    num_bindings = sum(num_bindings.values())
    print_log("Found %s hosts using %s bindings, returning average %s" % (str(num_hosts), str(num_bindings), str(ceil(num_bindings/num_hosts))))
    return ceil(num_bindings/num_hosts)


def check_nat_bindings(connection_object, target_num_bindings):
    path = '/nokia-conf:configure/service/nat/nat-policy[name="NAT_POL1"]/session-limits/max'
    curr_num_bindings = connection_object.running.get(path)
    orig_curr_num_bindings = curr_num_bindings
    while 0.66 * curr_num_bindings < target_num_bindings:
        print_log("Getting dangerously close to session-limit %s, as we are over 66%% of this value already at %s" % (curr_num_bindings, target_num_bindings))
        curr_num_bindings = curr_num_bindings + 3
    if (curr_num_bindings == orig_curr_num_bindings):
        print_log("Not increasing session-limits, %s is ok." % (curr_num_bindings))
    else:
        print_log("Increasing session-limits from %s to %s" % (orig_curr_num_bindings, curr_num_bindings))
        connection_object.candidate.set(path, curr_num_bindings)


def main():
    connection_object = connect()
    avg_bindings = get_nat_binding_avg(connection_object)
    check_nat_bindings(connection_object, avg_bindings)



if __name__ == "__main__":
    main()