# Configure and test end-to-end EVPN

| Item | Details |
| --- | --- |
| Short Description | EVPN configuration can be complicated, but it's much easier if you automate it |
| Skill Level | Intermediate |
| Tools Used | SR OS, EVPN, Python (with the `pysros` library) |

## Objective

In this lab, you will configure an EVPN service and confirm it functions correctly from the router's perspective. You will also access the simulated clients being provided with the service to confirm they can interact with each other.

The EVPN will be configured between `pe1` and `pe3` and tests will be included that confirm connectivity.

Optionally, you can try to add `pe2` and `pe4` as extra sites to the service to assess the portability of your code. The EVPN will provide connectivity between `client01` and `client03` (and optionally `client02` and `client04`), so the result should be that a ping or any kind of traffic between the clients' eth1 interfaces on VLAN 500 works.


## Accessing the lab
In this lab you will interact with the model-driven SR OS PE's and optionally several client nodes. Commands to access them are
```
ssh -l admin clab-srexperts-pe1
ssh -l admin clab-srexperts-pe2
ssh -l admin clab-srexperts-pe3
ssh -l admin clab-srexperts-pe4
#
ssh -l user clab-srexperts-client01
ssh -l user clab-srexperts-client02
ssh -l user clab-srexperts-client03
ssh -l user clab-srexperts-client04
```

## Task 1: Configuring a single EVPN-site

Create a pySROS script `create-evpn.py` in `/home/nokia/clab-srexperts/pe1/tftpboot/` that will run locally on the router. Your script should implement the following functions:
1. `get_connection()` should return a connection to the SR OS system
2. `create_vpls(connection_object, service_name, service_id)`  takes the `Connection` object and an ID and name for your EVPN-VPLS as inputs and uses those to create a VPLS in the candidate datastore. This function should **not** yet trigger a commit.
3. `create_vprn(connection_object, service_name, service_id)` takes the `Connection` object and an ID and name for your EVPN-VPRN as inputs and uses those to create a VPRN in the candidate datastore. This function should trigger a commit.
4. `main()` calls the above functions listed above in an order that makes sense.
5. Once implemented, execute your script as `pyexec tftp://172.31.255.29/create-evpn.py` and verify that the configuration appears in `pe1`'s running datastore.

For inspiration, you can look to the [examples](./examples) folder as it contains a version of [examples/create-evpn.py](./examples/create-evpn.py).

Some inputs for the service to be deployed:
- Route-distinguishers for the VPLS will be of the form `65021:500`, for the VPRN they will be `65020:501`.
- Similarly, route-targets are `target:65021:500` and `target:65020:501` for the VPLS import and export targets and VPRN vrf-target, respectively.
- On each PE, the port connected to the client device is `1/1/c6/1`.
- The subnet to use in the service is `10.70.10.0/24`.
- Use VLAN ID `500` for the client VLAN and VPLS Service ID, the next ID available should be the VPRN Service ID.
The target configuration for our EVPN, is the following:

```
configure {
    service {
        vpls "evpn-vpls-500" {
            admin-state enable
            service-id 500
            customer "1"
            routed-vpls {
            }
            bgp 1 {
                route-distinguisher "65020:500"
                route-target {
                    export "target:65020:500"
                    import "target:65020:500"
                }
            }
            bgp-evpn {
                mpls 1 {
                    admin-state enable
                    auto-bind-tunnel {
                        resolution filter
                        resolution-filter {
                            sr-isis true
                        }
                    }
                }
            }
            sap 1/1/c6/1:500 {
            }
        }
        vprn "evpn-vprn-501" {
            admin-state enable
            service-id 501
            customer "1"
            bgp-ipvpn {
                mpls {
                    admin-state enable
                    route-distinguisher "65021:501"
                    vrf-target {
                        community "target:65021:501"
                    }
                }
            }
            interface "evpn-vpls" {
                ipv4 {
                    primary {
                        address 10.70.10.101
                        prefix-length 24
                    }
                }
                vpls "evpn-vpls-500" {
                }
            }
        }
    }
}
```

Example script execution:

```
(gl)[/configure]
A:admin@pe1# pyexec tftp://172.31.255.29/create-evpn.py
```

## Task 2: Verifying service behavior

Create a pySROS script `/home/nokia/clab-srexperts/pe1/tftpboot/verify-evpn.py` that will run locally on the router to perform sanity checks on the service created in the previous step. Creating the script in the `tftpboot` folder lets the script run from the router CLI called as `tftp://172.31.255.29:/verify-evpn.py`. This allows you to more easily work on the file remotely, and still have it readily available when looking on the router.

- Ensure the VPLS and VPRN services are operationally up
- Check the BGP routes received that correspond to this service and see if the sites respond to ping
- Confirm the local site has advertised the necessary routes
- Check if any of the four clients are reachable
- Format the output in a table

Try to reuse as much as possible from the previous task, [examples/verify-evpn.py](./examples/verify-evpn.py) can serve as inspiration. To use the example script as-is, first fill in your instance ID in the route reflector IP address to replace the value currently marked as "X".

Example output:

```
(gl)[/configure]
A:admin@pe1# pyexec tftp://172.31.255.29/verify-evpn.py
===============================================================================
Verification for service evpn-{vpls,vprn}-500
===============================================================================
                 Parameter tested                  Result
-------------------------------------------------------------------------------
                 VPLS Oper. State                  up
                 VPRN Oper. State                  up
                   BGP RR State                    Established
               EVPN Session Active                 True
              # EVPN Routes Received               115
               # EVPN Routes Active                22
                # EVPN Routes Sent                 15
                  PE2 reachable                    Yes
                  PE3 reachable                    Yes
                  PE4 reachable                    Yes
                client01 reachable                 Yes
                client02 reachable                 Yes
                client03 reachable                 No
                client04 reachable                 No
-------------------------------------------------------------------------------
No. of Tests run: 14
===============================================================================
```

## Task 3: Generalizing your scripts

Configuring a service and testing it in this manner doesn't generalize well, as copying the scripts and running them individually is not very convenient.  You'll quickly end up having to copy and maintain many separate copies of the same code in most real-world situations and this is to be avoided. Use your script from task 1 as a building block and modify it such that when executed from your instance CLI, a dynamic number of routers is configured to be part of the service.

The generalized script takes as input a list of tuples of a service ID, a host to configure the service on and the IP address the host should use in that service as well as credentials to use for the router(s). Subnets per service/VLAN are as follows:

- 500: 10.70.10.0/24
- 600: 10.70.11.0/24
- 600: 10.70.12.0/24

where the PE# is assigned the 10# address, and client0# is assigned address #.

Execute your updated script from the hypervisor to configure service `500`/`501` on `pe3`. `pe2` and `pe4` can optionally be included.

Now that your script is generalized, configure EVPN `600` on at least two PEs.

Finally, generalize the verification script in the same way and use it confirm the services you have configured are behaving as expected.

Example executions for creating and verifying multiple services via the generalized script:

```
# python general-create-evpn.py  -p < password > -u admin -s 500/clab-srexperts-pe1/10.70.10.101,600/clab-srexperts-pe1/10.70.11.101,700/clab-srexperts-pe2/10.70.12.102,500/clab-srexperts-pe3/10.70.10.103,600/clab-srexperts-pe3/10.70.11.103,700/clab-srexperts-pe4/10.70.12.104
# python general-verify-evpn.py -p < password > -u admin -s 500/clab-srexperts-pe1/10.70.10.101,600/clab-srexperts-pe1/10.70.11.101,700/clab-srexperts-pe2/10.70.12.102,500/clab-srexperts-pe3/10.70.10.103,600/clab-srexperts-pe3/10.70.11.103,700/clab-srexperts-pe4/10.70.12.104
===============================================================================
Verification for service evpn-{vpls,vprn}-{500,501} on PE1
===============================================================================
                 Parameter tested                  Result
-------------------------------------------------------------------------------
  . . .
-------------------------------------------------------------------------------
No. of Tests run: 14
===============================================================================
===============================================================================
Verification for service evpn-{vpls,vprn}-{600,601} on PE1
===============================================================================
                 Parameter tested                  Result
-------------------------------------------------------------------------------
  . . .
===============================================================================
Verification for service evpn-{vpls,vprn}-{700,701} on PE4
  . . .
===============================================================================
```

Try to reuse as much as possible from the previous tasks. In the [examples](./examples/) you'll find some generalized versions of the previous scripts. As before, to use the [general-verify-evpn.py](./examples/general-verify-evpn.py) script as-is, first fill in your instance ID in the route reflector IP address to replace the value currently marked as "X".

## Optional: error handling, logging and more

Not covered so far are these two topics:

- What happens to your service if you try to use a SAP that is already in use?
- What if some other user has an exclusive lock on the datastore and your script is unable to configure anything?

Does it still work as expected in these situations?

Similarly, you could look into adding logging to your script so that there is accountability for services configured in the network.

Lastly, what is missing so far (at least in the example solution, this may not be the case for you!) is configuration validation. Clearly, the state information is being verified and connectivity is being checked but there is no check to see if the configuration is still in line with the input template. This can help to avoid rogue configuration and might be interesting to explore.

