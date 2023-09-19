#!/usr/bin/env bash

while true; do
    iperf3 -c 192.0.5.0 -tinf -u -b 100M
done
