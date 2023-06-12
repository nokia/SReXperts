# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from alc import dhcpv4
from alc import cache

# This script is executed when a DHCP discover packet is received, and should contain the solution to exercises 1 & 2
# while a basic program structure and comments were provided for your benefit, you are by no means required to follow them!

def exercise_1():
  print("== Exercise 1==")
  
  # get & print the DHCP option 61 (client ID) for this packet
  #client_id = ...
  #print("Client ID: '" + client_id + "'")

  # copy the client_id to DHCP option 82 (circuit ID)
  #...

  # (optional) verify that the DCHP option 82 (circuit ID) of this packet contains the client ID
  #...

def exercise_2():
  print("== Exercise 2==")

  # get & print the DHCP option 81 (client FQDN) of this packet
  #client_fqdn = ...
  #print("Client FQDN: '" + client_fqdn + "'")

  # find a way to store the client FQDN so that it may be used when the radius-script.py is executed
  # important: this is only required for client 3: clients 1 & 2 do not require customization towards the Radius server

if __name__ == "__main__":
  print("=== DHCP script ===") 

  # == Exercise 1 ==
  exercise_1()

  # == Exercise 2 ==
  exercise_2()
