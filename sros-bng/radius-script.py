# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from alc import radius
from alc import cache

# this script is executed when a radius access-request or authentication-request is sent to the Radius server and should contain a solution to exercise 2
# while a basic program structure and comments were provided for your benefit, you are by no means required to follow them!

if __name__ == "__main__":
  print("=== Radius script ===")
  
  # print all available radius attributes
  #...

  # find a way to retrieve the client FQDN that you received as option 81 in the dhcp-script.py
  # if it was found, retrieve it. If it was not found, you should not proceed with the execution of this script
  #client_fqdn = ...
  #print("Client FQDN found: '" + client_fqdn + "'")

  # set the Radius option User-Name (ID 1) to client_fqdn, instead of a MAC address
  #...
