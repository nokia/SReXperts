# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from alc import dhcpv4
from alc import cache

def task_3_dhcp4_discover():
  client_id = dhcpv4.get(61)[0]
  ue_mac = dhcpv4.chaddr[:6]
  with cache as cache_object:
    if cache_object.get(ue_mac):
        pass
    else:
        cache_object.set(ue_mac, (bytes(chr(len(client_id)), 'utf-8') + client_id))
        # <task 4>
        # if (client_fqdn := dhcpv4.get(81)[0][2:]):
        #   cache_object.set(ue_mac + b'\x81', client_fqdn)
        # </task 4>
  with cache as cache_object:
    relayagent = [{1:[cache_object.get(ue_mac)]},]
  dhcpv4.set_relayagent(relayagent)


def task_3_dhcp4_request():
  ue_mac = dhcpv4.chaddr[:6]
  with cache as cache_object:
    cache_info = cache_object.get(ue_mac)

    dhcp_info_len = int(cache_info[0])
    dhcp_client_info = cache_info[1:1+dhcp_info_len]

    if (len(cache_info) > dhcp_info_len+1):
      class_len = int(cache_info[1+dhcp_info_len])
      class_info = cache_info[1+dhcp_info_len+1:1+dhcp_info_len+1+class_len]
    else:
      class_info = ""

    relayagent = [{1:[dhcp_client_info + "\x00" + class_info]},]
  dhcpv4.set_relayagent(relayagent)

if __name__ == "__main__":
  if ord(dhcpv4.get(53)[0]) == 1:
    # DISCOVER is attr 53 value 1
    task_3_dhcp4_discover()
  elif ord(dhcpv4.get(53)[0]) == 3:
    # REQUEST is attr 53 value 1
    task_3_dhcp4_request()