# Lab discovery

| Item | Details |
| --- | --- |
| Short Description | initial use-case for NSP activities to get devices discovered |
| Skill Level | Beginner |
| Tools Used | NSP |

## Prerequisites
Basic knowledge the NSP UI

## Objectives

This activity is about getting your nodes discovered in NSP.<br>
Note: NSP is shared for all groups, while dedicated network devices are provided.

## Access to the Lab

Access details to NSP will be provided in the hackathon.<br>
There is no requirement to access the NEs directly.

## Steps

1. Open NSP WebUI in your browser (open: https://nsp.srexperts.net)
2. Provide username and password for your group.
3. Open `Device Discovery` from hamburger menu.
4. Update `Admin State` for discovery rules `SROS-rule-x` and `SRL-rule-x` (x represents your group-id) to value `Up`. The `Edit` action is found when clicking the 3dots icon.
5. Manual trigger both(!) discovery rules. Once again, the `Discover` action is found when clicking the 3dots icon.
6. Validate if devices have been discovered! Use the `View discovered IP addresses` action and the Error tab on the side panel. You should see 7 SR nodes (pe1, pe2, pe3, pe4, p1, p2, vRR) and 9 SRL nodes (agg1, ixp1, leaf11, leaf12, leaf13, leaf21, peering2, spine11, spine12). All devices should be shown as `Reachable` and `Resync Status` as `done`.
7. Back in `Network Inventory View` you should just see the 16 nodes that belong to your group, because access control is automatically applied based on the user/group you are logged in as.
8. Validate device connectivity using `Model Driven Configurator` (MDC) by connecting to one SRL node (e.g. leaf11) and list all interfaces under `Srl_nokia-interfaces:/interface`. Then connect to one SROS node (e.g. p1) and list all interfaces (physical ports) by clicking on `Nokia-conf:/configure` and then `Port List`.

Now you are ready to execute the NSP-related activity of your choice!
