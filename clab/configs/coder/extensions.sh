#!/bin/sh
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


for extension in $(find /opt/srexperts/vscode-extensions -type f);
do
    code-server --install-extension $extension
done

curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

# fix for clab extension
sudo ln -s /home/coder /home/nokia
