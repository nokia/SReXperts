# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from pysros.management import connect
from pysros.ehs import get_event
from utime import localtime, strftime

SCRIPT_ACL_NAMES = {
    "bgp": "ehs_controlled_bgp_peers",
    "ntp": "ehs_controlled_ntp_peers"
}

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

def find_vprns(connection):
    """
    Function that returns the list of router instances configured on the system
    """
    vprns = ["router[router-name=\"Base\"]/bgp/neighbor"]
    vprn_filter = {
        "service-name": {},
    }
    vprn_name_list = connection.running.get(
        '/nokia-conf:configure/service/vprn',
        filter=vprn_filter,
    )
    for vprn in vprn_name_list:
        vprns.append("service/vprn[service-name=\"%s\"]/bgp/neighbor" % vprn)
    return vprns

def find_bgp_peers(connection):
    """
    Function to find configured BGP peers and return them as a dictionary
    with each key being a VPRN name and each value being a list of configured
    BGP neighbor IP addresses.
    """
    results_miskeyed = {key: [] for key in find_vprns(connection)}
    bgp_filter = {
        "ip-address" : {},
    }
    for context, bgp_peers in results_miskeyed.items():
        bgp_peers.extend(connection.running.get_list_keys(
            '/nokia-conf:configure/' + context
        ) )
    results = {}
    for key,value in results_miskeyed.items():
        vrf = key.split('=')[1].split('"')[1]
        results[vrf] = value
    return results 

def find_ntp_peers(connection):
    """
    Function to find configured NTP servers and return them as a dictionary
    with each key being a VPRN name and each value being a list of configured
    NTP server addresses.
    """
    results = {}
    for server, vrf in connection.running.get_list_keys('/nokia-conf:configure/system/time/ntp/server'):
        if vrf in results.keys():
            results[vrf].append(server)
        else:
            results[vrf] = [server]
    return results 


def update_prefix_lists(connection, peer_list, protocol, vrf_name = ""):
    if vrf_name:
        pfx_list_name = (SCRIPT_ACL_NAMES[protocol] + vrf_name)[:32]
    else:
        pfx_list_name = (SCRIPT_ACL_NAMES[protocol])[:32]
    path = '/nokia-conf:configure/filter/match-list/ip-prefix-list[prefix-list-name="%s"]/prefix' % pfx_list_name
    payload = {}
    for peer in peer_list:
        payload[peer+"/32"] = {"ip-prefix": peer + "/32"}
    
    print("Updating prefix list %s with prefixes %s"% (pfx_list_name, ",".join(payload.keys())))

    if payload:
        connection.candidate.set(path, payload, commit=False)
        return True
    return False


def main():
    """The main procedure.  The execution starts here."""
    connection = connect(
        host="local connection only - unused",
        username="local connection only - unused",
    )
 
    trigger_event = get_event()
    if (trigger_event.appid == "SYSTEM" and trigger_event.eventid in [2006,2007,2008]):
        print_log("Configuration was changed. Re-exploring configured NTP and BGP peers for prefix list update.")
        vrf_bgp_peers = find_bgp_peers(connection)
        vrf_ntp_peers = find_ntp_peers(connection)

        for protocol, set_of_peers in [("bgp", vrf_bgp_peers), ("ntp", vrf_ntp_peers)]:
            for vrf, peers in set_of_peers.items():
                changes_per_vrf = update_prefix_lists(connection, peers, protocol, vrf)
            changes_global = update_prefix_lists(connection, [peer_ip for peer_ip_list in set_of_peers.values() for peer_ip in peer_ip_list], protocol)
            if changes_per_vrf or changes_global:
                connection.candidate.commit()




    connection.disconnect()
    return


if __name__ == "__main__":
    main()
