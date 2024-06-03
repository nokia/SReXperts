# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from alc import dhcpv4
def task_2():
  print("== Task 2 ==")

  # get & print the DHCP option 61 (client ID) for this packet
  client_id = dhcpv4.get(61)[0]
  print("Client ID: '" + str(client_id) + "'")

  # copy the client_id to DHCP option 82 (circuit ID)
  relayagent = [{1:[client_id]},]
  dhcpv4.set_relayagent(relayagent)

  # (optional) verify that the DCHP option 82 (circuit ID) of this packet contains the client ID
  # ...

if __name__ == "__main__":
  task_2()
