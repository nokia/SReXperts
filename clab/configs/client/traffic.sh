#!/bin/sh
# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


set -eu

action=
dst=
validclients="all client01 client02 client03 client04 client11 client12 client13 client21"
validsuffix=".grt .vprn.dci"
hostname=$(/bin/hostname)

startTraffic() {
    log_file=/tmp/${prefix}.${suffix}.$(date +%FT%T).log
    pid_file=/tmp/traffic-${hostname}-${prefix}.${suffix}.pid
    if [ -f "$pid_file" ]; then
        pid=$(cat $pid_file)
        ps -p $pid > /dev/null 2>&1 && {
            echo "Already running for given host $prefix (pid $pid)" >&2 ;
            exit 1 ;
        } || {
            rm -f $pid_file || {
                echo Unable to remove orphan PID file $pid_file >&2 ;
                exit 1 ;
            }
        }
    fi
    echo "starting traffic to ${dst}, binding on ${hostname}.${suffix}, saving logs to ${log_file}"
    /usr/bin/iperf3 -6 -c ${prefix}.${suffix} -t 10000 -i 1 -p 5201 -B ${hostname}.${suffix} -P 8 -b 200K -M 1460 --logfile ${log_file} &
    echo $! > /tmp/traffic-$hostname-${prefix}.${suffix}.pid
}
stopTraffic() {
    pid_file=$(echo /tmp/traffic-$hostname-${prefix}.${suffix}.pid)
    if [ -f "$pid_file" ]; then
        echo "stopping traffic to ${dst}"
        pid=$(cat $pid_file)
        ps -p $pid > /dev/null 2>&1 && {
            sudo /bin/kill -9 $pid || {
                echo Unable to kill PID $pid >&2 ;
                exit 1 ;
            }
        } || {
            echo PID $pid not running >&2 ;
        }
        sudo rm -f $pid_file || {
            echo Unable to remove PID file $pid_file >&2 ;
            exit 1 ;
        }
    fi
}

usage() { echo "$0 [-a <start|stop>] [-d <dns hostname>]"; exit 0; }


while getopts ":ha:d:" arg; do
  case $arg in
    a) # Specify action, either start or stop.
      action=${OPTARG}
      [ "$action" = "start" -o "$action" = "stop" ] || usage
      ;;
    d) # Specify destination of traffic.
      dst=${OPTARG}
      prefix=$(echo $dst | cut -d. -f1)
      suffix=$(echo $dst | cut -d. -f2-) 
      # Test if a valid client has been defined
      echo $validclients | grep -q $prefix || (echo "$prefix is not a valid client, use one of: [ $validclients ]" && exit 1)
      # test for self
      echo ${hostname} | grep -q $prefix && (echo "cannot use self to send traffic towards." && exit 1)
      # If no tld has been specified, use .grt
      [ "$suffix" = "$dst" ] && suffix="grt"
      # test if only a dot has been specified.
      [ "$suffix" = "" ] && (echo "Error: invalid hostname, example: $prefix.grt or $prefix.vprn.dci" && exit 1)
      # test for valid dns suffixes
      echo $validsuffix | grep -q $suffix || (echo "$suffix is not a valid dns suffix, use one of: [ $validsuffix ]" && exit 1)
      ;;
    h | *) # Display help.
      usage
      exit 0
      ;;
  esac
done

if [ -z "$action" ]; then
    usage
fi
if [ -z "$dst" ]; then
    usage
fi

if [ $action = "start" ]; then
    if [ $prefix = "all" ]; then
        for client in $(echo ${validclients} | sed 's/all //g')
        do
            [ "$hostname" = "$client" ] && continue
            dst=$client.$suffix
            prefix=$client
            startTraffic
        done
    else
       startTraffic
    fi
fi
if [ $action = "stop" ]; then
    if [ $prefix = "all" ]; then
        for client in $(echo ${validclients} | sed 's/all //g')
        do
            [ "$hostname" = "$client" ] && continue
            dst=$client.$suffix
            prefix=$client
            stopTraffic
        done
    else
       stopTraffic
    fi
fi

#
