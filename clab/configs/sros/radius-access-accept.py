# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from alc import radius
from alc import cache
import binascii

ALU = 6527

def radius_accept():
  # get the MAC
  mac_hex = radius.attributes.getVSA(ALU,16)
  mac_hex = mac_hex.replace(b':', b'')
  ue_mac = binascii.unhexlify(mac_hex)
  with cache as cache_object:
    cache_info = cache_object.get(ue_mac)

    dhcp_info_len = int(cache_info[0])
    dhcp_client_info = cache_info[1:1+dhcp_info_len]
    class_len = len(radius.attributes.get(25))
    class_info = radius.attributes.get(25)

    cache_object.set(ue_mac, cache_info[0:1+dhcp_info_len] + bytes(chr(class_len), 'utf-8') + class_info)

if __name__ == "__main__":
  radius_accept()
