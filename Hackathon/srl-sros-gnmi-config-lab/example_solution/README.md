### In this solutions document, we are configuring eBGP among all routers. Each router will have its own ASN based on the first two octets of its ipv4 system address as shown in the [topology file](../topology.png) for example, clab-config-sr1's system address is 3.1.1.1 and the ASN is 65031. Keep this in mind if you have taken a different approach.

> If there is a router that you need to configure quickly, click the link below for the solution

- [clab-config-sr1](#clab-config-sr1)
- [clab-config-sr2](#clab-config-sr2)
- [clab-config-spine1](#clab-config-spine1)
- [clab-config-spine2](#clab-config-spine2)
- [clab-config-leaf1](#clab-config-leaf1)
- [clab-config-leaf2](#clab-config-leaf2)


### There are different approaches that can be used to configure the devices using gNMIc - we will start with creating a single file to update just a single portion of the configuration.

## Configuring the "system" interface on clab-config-sr1

> getting the initial interface configuration hierarchy

```
gnmic -a clab-config-sr1 -u admin -p admin --insecure get \
          --path "/configure/router[router-name=Base]/interface"
```

> setting up the 'system' interface on clab-config-sr1

*Contents of sr1-system-interface.yaml*

```
admin-state: enable
ipv4:
    primary:
        address: 3.1.1.1
        prefix-length: 32
```

``` 
gnmic -a clab-config-sr1 -u admin -p admin --insecure set \
          --update-path "/configure/router[router-name=Base]/interface[interface-name=system]" \
          --update-file sr1-system-interface.yaml
```

It is easy to make simple mistakes that can lead to the command failing to execute.

For this reason, it is often helpful to use `--dry-run` option to see what is being sent to the device. 

Here is an example - in this first case, I have create the same `sr1-system-interface.yaml` file from above, but I did not indent properly:

```
admin-state: enable
ipv4:
primary:
    address: 3.1.1.1
    prefix-length: 32
```

Now, running the command fails:

```
gnmic -a clab-config-sr1 -u admin -p admin --insecure set \
          --update-path "/configure/router[router-name=Base]/interface[interface-name=system]" \
          --update-file sr1-system-interface.yaml
target "clab-config-sr1" set request failed: target "clab-config-sr1" SetRequest failed: rpc error: code = InvalidArgument desc = MINOR: MGMT_CORE #2201: /configure/router[router-name=Base]/interface[interface-name=system]/ipv4 - Unknown element - gRPC: update operation 1
Error: one or more requests failed
```

Let's see what we are sending - it doesn't like the way we have set `ipv4`

```
gnmic -a clab-config-sr1 -u admin -p admin --insecure set \
          --update-path "/configure/router[router-name=Base]/interface[interface-name=system]" \
          --update-file sr1-system-interface.yaml --dry-run
{
  "update": [
    {
      "path": "configure/router[router-name=Base]/interface[interface-name=system]",
      "val": "json_val:\"{\\\"admin-state\\\":\\\"enable\\\",\\\"ipv4\\\":null,\\\"primary\\\":{\\\"address\\\":\\\"1.1.1.1\\\",\\\"prefix-length\\\":32}}\""
    }
  ]
}
```

You can see that there is a `:null` value after `ipv4` instead of the `primary` dictionary. This is an easy way to determine that the yaml file was not correct.

After fixing the yaml file, the output from the `--dry-run` is accurate:

```
$ gnmic -a clab-config-sr1 -u admin -p admin --insecure set \
          --update-path "/configure/router[router-name=Base]/interface[interface-name=system]" \
          --update-file sr1-system-interface.yaml --dry-run
{
  "update": [
    {
      "path": "configure/router[router-name=Base]/interface[interface-name=system]",
      "val": "json_val:\"{\\\"admin-state\\\":\\\"enable\\\",\\\"ipv4\\\":{\\\"primary\\\":{\\\"address\\\":\\\"3.1.1.1\\\",\\\"prefix-length\\\":32}}}\""
    }
  ]
}
```









# SOLUTIONS PER ROUTER

### clab-config-sr1

```
gnmic -a clab-config-sr1 -u admin -p admin --insecure set \
         --update-path "/configure" --update-file sr1.yaml
```


### clab-config-sr2

```
gnmic -a clab-config-sr2 -u admin -p admin --insecure set \
         --update-path "/configure" --update-file sr2.yaml
```

### clab-config-spine1

```
gnmic -a clab-config-spine1 -u admin -p NokiaSrl1! --skip-verify --encoding json_ietf set \
         --update-path "/" --update-file spine1.yaml
```

### clab-config-spine2

```
gnmic -a clab-config-spine2 -u admin -p NokiaSrl1! --skip-verify --encoding json_ietf set \
         --update-path "/" --update-file spine2.yaml
```

### clab-config-leaf1

```
gnmic -a clab-config-leaf1 -u admin -p NokiaSrl1! --skip-verify --encoding json_ietf set \
         --update-path "/" --update-file leaf1.yaml
```

### clab-config-leaf2

```
gnmic -a clab-config-leaf2 -u admin -p NokiaSrl1! --skip-verify --encoding json_ietf set \
         --update-path "/" --update-file leaf2.yaml
```
