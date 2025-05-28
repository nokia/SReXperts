#!/usr/bin/env python3
# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause


import os
import sys

# Get the directory where the script is located
CUR_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the YAML file (in the same directory as the script)
FILE = os.path.join(CUR_DIR, "srx.clab.yml")

# Nodes to modify
nodes_to_modify = ["spine11", "spine12", "leaf11", "leaf12", "leaf13"]

try:
    # Read the file content
    with open(FILE, 'r') as f:
        lines = f.readlines()
    
    # Process the file line by line
    current_node = None
    modified_lines = []
    
    for line in lines:
        # Check if this is a node definition line
        for node in nodes_to_modify:
            if f"{node}:" in line and not line.strip().startswith('#'):
                current_node = node
                break
        
        # If we're in one of the target nodes and this is a startup-config line, comment it out
        if current_node and "startup-config:" in line and not line.strip().startswith('#'):
            # Add a # before startup-config if it doesn't already have one
            indent = line[:line.index("startup-config:")]
            modified_line = f"{indent}# startup-config:{line.split('startup-config:', 1)[1]}"
            modified_lines.append(modified_line)
            # Reset current_node if we've altered the startup-config, we'll move on to a new node in the nodes_to_modify list.
            current_node = None
        elif current_node and "startup-config:" in line and line.strip().startswith('#'):
            # if the line is already commented out, just append the line.
            modified_lines.append(line)
            current_node = None
        else:
            modified_lines.append(line)

    # Write the modified content back to the file
    with open(FILE, 'w') as f:
        f.writelines(modified_lines)
    
    print("Successfully commented out startup-config fields for spine11, spine12, leaf11, leaf12, and leaf13 nodes.")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
