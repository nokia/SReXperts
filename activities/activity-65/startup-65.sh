# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

response=$(gnmic -a clab-srexperts-p2 -u "admin" -p $EVENT_PASSWORD --insecure get\
    --path /bof/router[router-name=*]/interface[interface-name=*]/cpm[cpm-type=*]/ipv4/ip-address)

ip=$(echo "$response" | jq -r '.[0].updates[0].values["bof/router/interface/cpm/ipv4/ip-address"]')

interface=$(gnmic -a clab-srexperts-p2 -u "admin" -p $EVENT_PASSWORD --insecure get\
    --path /state/port[port-id=1/1/c3/1]/if-index)

if_index=$(echo "$interface" | jq -r '.[0].updates[0].values["state/port/if-index"]')


gnmic -a clab-srexperts-p2 -u admin -p $EVENT_PASSWORD --insecure set \
    --update-path '/configure/mirror' \
    --update-file ~/SReXperts/activities/activity-65/mirror.json

gnmic -a clab-srexperts-p2 -u admin -p $EVENT_PASSWORD --insecure set \
    --update-path '/configure/system' \
    --update-file ~/SReXperts/activities/activity-65/script.json

gnmic -a clab-srexperts-p2 -u admin -p $EVENT_PASSWORD --insecure set \
    --update-path '/configure/log' \
    --update-file ~/SReXperts/activities/activity-65/ehs.json

gnmic -a clab-srexperts-p2 -u admin -p $EVENT_PASSWORD --insecure set \
    --update-path '/configure/system' \
    --update-file ~/SReXperts/activities/activity-65/rmon.json


gnmic -a clab-srexperts-p2 -u "admin" -p $EVENT_PASSWORD --insecure set\
    --update-path '/configure/mirror/mirror-dest[service-name=test-pcap]/pcap[session-name=test]/file-url'\
    --update-value 'ftp://admin:'$EVENT_PASSWORD'@'$ip'/cf3:/test.pcap'\
    --update-path '/configure/system/thresholds/rmon/alarm[rmon-alarm-id=1000]/variable-oid'\
    --update-value 'tmnxPortNetEgressFwdInProfOcts.1.'$if_index'.8'

gnmic -a clab-srexperts-p2 -u admin -p $EVENT_PASSWORD --insecure set \
    --update-path '/configure/system/security/ftp-server' \
    --update-value true    

sftp admin@clab-srexperts-p2 <<EOF
put ~/SReXperts/activities/activity-65/stop-pcap.txt
quit
EOF
echo "Startup script completed!"
