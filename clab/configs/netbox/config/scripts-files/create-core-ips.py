# Copyright 2025 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from extras.scripts import *
from ipam.models import IPAddress
from dcim.models import Device, Interface

class CreateCoreIPs(Script):
    class Meta():
        name = "Create IP interfaces on core nodes"
        description = "Script to Create IP interfaces on all P and PE nodes"

    instance_id = IntegerVar(
        description="Instance ID of your assigned Lab",
        required=True
    )

    node_data = {
        "p1": {
            "interfaces": {
                "system": {
                    "name": "system",
                    "ipv4": "10.46.INSTANCE_ID.11/32",
                    "ipv6": "fd00:fde8::INSTANCE_ID:11/128",
                },
                "1/1/c11/1": {
                    "name": "p2_1",
                    "ipv4": "10.64.11.22/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:12:0/127",
                },
                "1/1/c12/1": {
                    "name": "p2_2",
                    "ipv4": "10.64.12.23/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:11:1/127",
                },
                "1/1/c1/1": {
                    "name": "pe1",
                    "ipv4": "10.64.11.0/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:21:0/127",
                },
                "1/1/c2/1": {
                    "name": "pe2",
                    "ipv4": "10.64.11.2/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:22:0/127",
                },
                "1/1/c6/1": {
                    "name": "pe2_2",
                    "ipv4": "10.64.60.0/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:222:0/127",
                },
                "1/1/c3/1": {
                    "name": "pe3",
                    "ipv4": "10.64.11.4/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:23:0/127",
                },
                "1/1/c4/1": {
                    "name": "pe4",
                    "ipv4": "10.64.11.6/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:24:0/127",
                },
            }
        },
        "p2": {
            "interfaces": {
                "system": {
                    "name": "system",
                    "ipv4": "10.46.INSTANCE_ID.12/32",
                    "ipv6": "fd00:fde8::INSTANCE_ID:12/128",
                },
                "1/1/c11/1": {
                    "name": "p1_1",
                    "ipv4": "10.64.11.23/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:12:1/127",
                },
                "1/1/c12/1": {
                    "name": "p1_2",
                    "ipv4": "10.64.12.22/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:11:0/127",
                },
                "1/1/c1/1": {
                    "name": "pe1",
                    "ipv4": "10.64.12.0/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:21:0/127",
                },
                "1/1/c2/1": {
                    "name": "pe2",
                    "ipv4": "10.64.12.2/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:22:0/127",
                },
                "1/1/c3/1": {
                    "name": "pe3",
                    "ipv4": "10.64.12.4/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:23:0/127",
                },
                "1/1/c4/1": {
                    "name": "pe4",
                    "ipv4": "10.64.12.6/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:24:0/127",
                },
            }
        },
        "pe1": {
            "interfaces": {
                "system": {
                    "name": "system",
                    "ipv4": "10.46.INSTANCE_ID.21/32",
                    "ipv6": "fd00:fde8::INSTANCE_ID:21/128",
                },
                "1/1/c1/1": {
                    "name": "p1",
                    "ipv4": "10.64.11.1/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:21:1/127",
                },
                "1/1/c2/1": {
                    "name": "p2",
                    "ipv4": "10.64.12.1/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:21:1/127",
                }
            }
        },
        "pe2": {
            "interfaces": {
                "system": {
                    "name": "system",
                    "ipv4": "10.46.INSTANCE_ID.22/32",
                    "ipv6": "fd00:fde8::INSTANCE_ID:22/128",
                },
                "1/1/c1/1": {
                    "name": "p1",
                    "ipv4": "10.64.11.3/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:22:1/127",
                },
                "1/1/c2/1": {
                    "name": "p2",
                    "ipv4": "10.64.12.3/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:22:1/127",
                }
            }
        },
        "pe3": {
            "interfaces": {
                "system": {
                    "name": "system",
                    "ipv4": "10.46.INSTANCE_ID.23/32",
                    "ipv6": "fd00:fde8::INSTANCE_ID:23/128",
                },
                "1/1/c1/1": {
                    "name": "p1",
                    "ipv4": "10.64.11.5/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:23:1/127",
                },
                "1/1/c2/1": {
                    "name": "p2",
                    "ipv4": "10.64.12.5/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:23:1/127",
                }
            }
        },
        "pe4": {
            "interfaces": {
                "system": {
                    "name": "system",
                    "ipv4": "10.46.INSTANCE_ID.24/32",
                    "ipv6": "fd00:fde8::INSTANCE_ID:24/128",
                },
                "1/1/c1/1": {
                    "name": "p1",
                    "ipv4": "10.64.11.7/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:11:24:1/127",
                },
                "1/1/c2/1": {
                    "name": "p2",
                    "ipv4": "10.64.12.7/31",
                    "ipv6": "fd00:fde8:0:1:INSTANCE_ID:12:24:1/127",
                }
            }
        }
    }

    def run(self, data, commit):
        for device_name, device_data in self.node_data.items():
            interfaces = device_data["interfaces"]
            for int_name, int_data in interfaces.items():
                # get interface
                device = Device.objects.get(name=device_name)
                iface = Interface.objects.get(device=device, name=int_name)

                # create IPv4 address
                ipa4 = IPAddress(
                    address=int_data["ipv4"].replace("INSTANCE_ID", str(data["instance_id"])),
                )

                # assign to interface
                ipa4.assigned_object = iface
                if commit:
                    ipa4.save()

                self.log_success(f"Created {ipa4} on {device_name} interface {int_name}")

                # create IPv6 interface
                ipa6 = IPAddress(
                    address=int_data["ipv6"].replace("INSTANCE_ID", str(data["instance_id"])),
                )

                # assign to interface
                ipa6.assigned_object = iface
                if commit:
                    ipa6.save()

                iface.description = int_data["name"]
                if commit:
                    iface.save()

                self.log_success(f"Created {ipa6} on {device_name} interface {int_name}")

