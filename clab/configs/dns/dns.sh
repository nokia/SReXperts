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

dnsmasq

