#!/bin/bash
# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

ifup -a

mkdir -p /home/admin/.ssh
touch /home/admin/.ssh/authorized_keys
chmod 600 /home/admin/.ssh/authorized_keys
cat /tmp/authorized_keys > /home/admin/.ssh/authorized_keys
chown -R admin:admin /home/admin/.ssh

echo "admin ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
echo "admin:$USER_PASSWORD" | chpasswd

/usr/sbin/radiusd -x
