# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from alc import radius
from alc import cache
import binascii


def radius_request():
  # get the MAC
  mac_hex = radius.attributes.get(1)
  mac_hex = mac_hex.replace(b':', b'')
  ue_mac = binascii.unhexlify(mac_hex)

  with cache as cache_object:
    if (username_override := cache_object.get(ue_mac + b'\x81')):
      radius.attributes.set(1, username_override)


if __name__ == "__main__":
  radius_request()
