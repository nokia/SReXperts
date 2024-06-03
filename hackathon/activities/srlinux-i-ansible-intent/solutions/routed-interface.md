# Solution: Routed Interface

This definition creates a routed interface on a device. The interface is configured with an IPv4 address and is associated with a network instance. Copy it to the `intent` folder of the `intent-based-ansible-lab` repository in home directory and run the playbook. Make sure the filename starts with `host_infra_` and has extension `.yml` or `.yaml`.

```yaml
# host_infra_leaf1.yml
clab-4l2s-l1:
  interfaces:
    ethernet-1/22:
      admin_state: enable
  subinterface:
    ethernet-1/22.0:
      ipv4_address: 10.5.0.0/31
  network_instance:
    ipvrf-1:
      interfaces:
        - ethernet-1/22.0
```
