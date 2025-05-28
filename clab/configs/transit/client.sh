#!/bin/bash
# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

ifup -a

mkdir -p /home/user/.ssh
touch /home/user/.ssh/authorized_keys
chmod 600 /home/user/.ssh/authorized_keys
cat /tmp/authorized_keys > /home/user/.ssh/authorized_keys
chown -R user:user /home/user/.ssh

echo "user ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
echo "user:$USER_PASSWORD" | chpasswd

# Download RIS data
curl -fsSL https://data.ris.ripe.net/rrc00/latest-bview.gz -o /tmp/latest-bview.gz
gunzip /tmp/latest-bview.gz

# start gobgpd daemon
gobgpd -t yaml -f /gobgp/gobgp.yml --disable-stdlog &

sleep 5

# Inject IPv4/IPv6 routes
gobgp mrt inject global --no-ipv6 /tmp/latest-bview 100
gobgp mrt inject global --no-ipv4 /tmp/latest-bview 100
gobgp global rib add -a ipv6 2406:c800::/32 aspath "38016"
gobgp global rib add -a ipv6 2406:c800:a1ca::/48 aspath "38016"
gobgp global rib add -a ipv6 2406:c800:e000::/48 aspath "38016"