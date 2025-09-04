#!/bin/bash

# for containers with names clab-srexperts-leaf11 clab-srexperts-leaf12 clab-srexperts-leaf13 clab-srexperts-spine11 clab-srexperts-spine12
# For containers with names clab-srexperts-leaf11, clab-srexperts-leaf12, clab-srexperts-leaf13, clab-srexperts-spine11, and clab-srexperts-spine12, execute the revert command that removes the EDA configuration and restores the initial state of the DC1 nodes.
REVERT_CMD="sr_cli tools system configuration checkpoint clab-initial revert"
NODES=("leaf11" "leaf12" "leaf13" "spine11" "spine12")

for node in "${NODES[@]}"; do
  docker exec -it clab-srexperts-$node ${REVERT_CMD}
done