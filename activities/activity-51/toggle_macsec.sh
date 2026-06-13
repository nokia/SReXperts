# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

### SReXperts 2026
### Activity 51 MACsec toogle script
### cat ~/SReXperts/activities/activity-51/toggle_macsec.sh 

### Print the status before
echo "status before"
gnmic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure get \
--path '/configure/port[port-id=1/1/c1/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' | grep -e enable -e disable
gnmic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure get \
--path '/configure/port[port-id=1/1/c2/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' | grep -e enable -e disable
gnmic -a clab-srexperts-p1 -u admin -p $EVENT_PASSWORD --insecure get \
--path '/configure/port[port-id=1/1/c1/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' | grep -e enable -e disable
gnmic -a clab-srexperts-p2 -u admin -p $EVENT_PASSWORD --insecure get \
--path '/configure/port[port-id=1/1/c1/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' | grep -e enable -e disable

### Toggle macsec for both links
echo "Toggle macsec for both links"
###  PE1 to  P1 link
echo "Toggle PE1 to  P1 link"
gnmic -a clab-srexperts-pe1 -a clab-srexperts-p1 -u admin -p $EVENT_PASSWORD --insecure getset \
    --get '/configure/port[port-id=1/1/c1/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' \
    --condition 'true' \
    --update '.[0].updates[0].Path' \
    --value '.[0].updates[0].values["configure/port/ethernet/dot1x/macsec/sub-port/admin-state"] | if contains("disable") then "enable" else "disable" end'

### PE1 to  P2 link
echo "PE1 to P2 link"
gnmic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure getset \
    --get '/configure/port[port-id=1/1/c2/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' \
    --condition 'true' \
    --update '.[0].updates[0].Path' \
    --value '.[0].updates[0].values["configure/port/ethernet/dot1x/macsec/sub-port/admin-state"] | if contains("disable") then "enable" else "disable" end'

gnmic -a clab-srexperts-p2 -u admin -p $EVENT_PASSWORD --insecure getset \
    --get '/configure/port[port-id=1/1/c1/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' \
    --condition 'true' \
    --update '.[0].updates[0].Path' \
    --value '.[0].updates[0].values["configure/port/ethernet/dot1x/macsec/sub-port/admin-state"] | if contains("disable") then "enable" else "disable" end'

### Print the status after
echo "status after"
gnmic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure get \
--path '/configure/port[port-id=1/1/c1/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' | grep -e enable -e disable
gnmic -a clab-srexperts-pe1 -u admin -p $EVENT_PASSWORD --insecure get \
--path '/configure/port[port-id=1/1/c2/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' | grep -e enable -e disable
gnmic -a clab-srexperts-p1 -u admin -p $EVENT_PASSWORD --insecure get \
--path '/configure/port[port-id=1/1/c1/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' | grep -e enable -e disable
gnmic -a clab-srexperts-p2 -u admin -p $EVENT_PASSWORD --insecure get \
--path '/configure/port[port-id=1/1/c1/1]/ethernet/dot1x/macsec/sub-port[sub-port-id=1]/admin-state' | grep -e enable -e disable
