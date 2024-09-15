# Customizing DHCP and RADIUS flows with "alc"

| Item | Details |
| --- | --- |
| Short Description | Manipulate DHCP and RADIUS messages in-flight  |
| Skill Level | Intermediate |
| Tools Used | SR OS as a BNG, Python (with the `alc` library) |

SR OS allows operators to modify certain types of packets that flow through the router using the `alc` module. The traffic types that can be affected are
- diameter
- dhcp
- dhcp6
- gtpv1-c
- gtpv2-c
- pfcp
- pppoe
- radius

This gives the operator the capability and flexibility to make their own adaptation layer between the various systems (both on the client and server side) that interacts with SR OS using any of the protocols listed above.

## Objective
In this exercise, you will explore a standard BNG usecase with three subscribers accessing the router through an aggregation VPLS. Each subscriber comes with a unique MAC address and has a DHCPv4 client running. An external RADIUS server is used for authentication of the subscribers. This exercise will take you through the API to modify DHCP traffic, capture attributes sent in RADIUS traffic and store these values in the Python cache. The first task explores the BNG configuration, the second uses Python on DHCP and the third continues by adding Python for RADIUS traffic with cache usage. The final exercise affirms your learnings by applying them in a slightly different manner.


## Accessing the lab
In this lab you will play with subscribers on the BNG node `clab-srexperts-pe4`. You can log in by using the DNS name of the container.
```
ssh admin@clab-srexperts-pe4
```
The (IPoE) subscribers are emulated using Linux containers. They can be accessed via
```
ssh user@clab-srexperts-sub1
ssh user@clab-srexperts-sub2
ssh user@clab-srexperts-sub3
```
for debugging purposes or to trigger DHCP transactions on-demand. Use `sudo ifdown eth1.100; sudo ifup eth1.100` to force a new DHCP transaction. For convenience, you may want to wrap this action in a loop. This could be done as follows:
```
while :; do sudo ifdown eth1.100; sudo ifup eth1.100; sleep 15; done
```
You could also start the `crond` process on the emulated subscribers using `sudo crond`. A cron job will then begin to run every 5 minutes to renew the lease on interface `eth1.100`. For debugging purposes on the subscriber side, when going this route, you may prefer to use `sudo crond -l 1 -L /var/log/crond.log`.

Finally, the RADIUS server is accessible via
```
ssh user@clab-srexperts-radius
```
RADIUS server logs can be accessed either by addressing the container using docker commands or by logging in to the container via SSH, looking for the `/var/log/radius/radius.log` file and using `tail` to follow the output. Either become root after logging in or use `sudo` to track the outputs of this file, as the provided user does not have the necessary permissions to view the file.

## Verify the subscribers exist in the system
Use `show service active-subscribers` to verify subscribers are online. Initially, two subscribers exist in the system. The subscribers are assigned a generic subscriber identifier by the system. This identifier is formed by combining the device MAC and the SAP identifier the subscriber arrived on, separated by a pipe symbol (|). Though uniquely identifying the user, this doesn't give much information that can be correlated to perks or permissions the subscriber may or may not have.

For this activity it is important that two subscribers, `00:d0:f6:01:01:01|1/1/c3/1:100` and `00:d0:f6:02:02:02|1/1/c3/1:100` exist in the system initially.

<details>
<summary>Expected initial situation</summary>

```
[/]
A:admin@pe4# /show service active-subscribers

===============================================================================
Active Subscribers
===============================================================================
-------------------------------------------------------------------------------
Subscriber 00:d0:f6:01:01:01|1/1/c3/1:100
            (SUB_PROF1)
-------------------------------------------------------------------------------
NAT Policy    : NAT_POL1
Outside IP    : 10.67.200.1
Ports         : 1024-1055

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
(1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
-------------------------------------------------------------------------------
IP Address
                MAC Address        Session            Origin       Svc        Fwd
-------------------------------------------------------------------------------
10.24.1.112
                00:d0:f6:01:01:01  IPoE               DHCP         401        Y
-------------------------------------------------------------------------------

-------------------------------------------------------------------------------
Subscriber 00:d0:f6:02:02:02|1/1/c3/1:100
            (SUB_PROF1)
-------------------------------------------------------------------------------
NAT Policy    : NAT_POL1
Outside IP    : 10.67.200.0
Ports         : 1024-1055

-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
(1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
-------------------------------------------------------------------------------
IP Address
                MAC Address        Session            Origin       Svc        Fwd
-------------------------------------------------------------------------------
10.24.1.113
                00:d0:f6:02:02:02  IPoE               DHCP         401        Y
-------------------------------------------------------------------------------

-------------------------------------------------------------------------------
Number of active subscribers : 2
===============================================================================
```

</details>

Please alert someone if this is not the case.

## Task 1: Modify the default subscriber ID
Fortunately, SR OS makes this configurable. Issue `edit-config global` to enter the `global` configuration mode and explore the configuration tree under `/configure subscriber-mgmt`. See if you can find a way to change the identifier assigned to the subscribers. The `tree flat detail` command paired with appropriate `match` statements can be of use here. Look for configuration under the `auto-sub-id` keyword. Use `commit` to apply any changes you have made in the candidate datastore to the running datastore.

To renew the Subscriber-IDs in use on the system, clear the sessions on the BNG using the command below and trigger a renewal from the subscribers using any of the methods outlined in [the intro section](#accessing-the-lab).
```
[/]
A:admin@pe4# /clear service id "bng-vprn" ipoe session all
```
Confirm your configuration change has an effect in changing the chosen subscriber ID using the command from before.

You may not see any subscribers in the system. This could be normal depending on your applied configuration change as some fields that can be used to identify subscribers aren't being received by the router. If you don't see any subscribers, verify that this is indeed the issue using `/show log log-id 99` or `/show subscriber-mgmt errors sap all`. Fortunately, we can fix this! Move on to the next section to learn how.

<details>
<summary>Expected configuration change</summary>

```
    configure {
        subscriber-mgmt {
            auto-sub-id {
                ipoe-key [circuit-id]
            }
        }
    }
```

</details>

<details>
<summary>Expected new subscriber IDs (after removing them from the router and clients renewing)</summary>

```
    (ro)[/]
    A:admin@pe4# show service active-subscribers

    ===============================================================================
    Active Subscribers
    ===============================================================================
    -------------------------------------------------------------------------------
    No active subscribers found
    ===============================================================================
```

</details>

## Task 2: Shaking things up with Python
Adapting the subscriber identifier to certain well-known values is nice, though it does not cover all cases. For now, the subscriber hosts are set up to provide a Client ID (option 61) in their DHCP requests. You may have encountered the `circuit-id` and `remote-id` configuration options in the previous step. These refer to Circuit ID (option 82, sub-option 1) and Remote ID (option 82, sub-option 2) respectively. In this task, using `alc` and Python, you will copy or move the values contained in the Client ID to either the Circuit ID or the Remote ID, such that the system can use it as a subscriber identifier. For the remainder of this lab, the `circuit-id` configuration is assumed.

1. Create a file `task2.py` in a location where the router can access it. `/home/nokia/clab-srexperts/pe4/tftpboot/` is recommended as it allows access from the router using TFTP. This file location on the Linux hypervisor provided to you is mounted inside the SR OS container as part of the containerlab deployment. Files placed in this location can be accessed from the BNG after replacing the directory path with `tftp://172.31.255.29/`, the IP address is internal to the SR OS container. Starting from this snippet, add the logic required to copy or move the value contained in the Client ID to the Circuit ID field.
```
from alc import dhcpv4
def task_2():
  print("== Task 2 ==")

  # get & print the DHCP option 61 (client ID) for this packet
  #client_id = ...
  #print("Client ID: '" + client_id + "'")

  # copy the client_id to DHCP option 82 (circuit ID)
  # ...

  # (optional) verify that the DCHP option 82 (circuit ID) of this packet contains the client ID
  # ...


if __name__ == "__main__":
  task_2()
```
2. Add the necessary configuration to SR OS to ensure this script is executed on the DHCP packets reaching the router from the client. Make sure you issue `commit` statements to load the candidate datastore into the running datastore for your changes to take effect.
    1. Create a Python-script element called `task2` using [the documentation](https://documentation.nokia.com/sr/23-10-1/tpsda-python-3-api/alc-dhcpv4.html) for some inspiration.
    ```
    configure {
        python {
            python-script "task2" {
                admin-state enable
                urls ["tftp://172.31.255.29/task2.py"]
                version python3
            }
        }
    }
    ```
    To develop the Python script, edit the file and when ready for testing, reload the script using
    ```
    [/]
    A:admin@pe4# /perform python python-script reload script task2
    ```
    Ensure the new script is active and working. This can be done using
    ```
    [/]
    A:admin@pe4# /show python python-script "task2"
    ```
    Log 21 has been prepared to view Python script information. Enabling debugging for your Python script is done with this debug statement
    ```
    [/]
    A:admin@pe4# //debug python python-script "task2" script-all-info
    ```
    and the log will be printed directly to the console by issuing
    ```
    [/]
    A:admin@pe4# /tools perform log subscribe-to log-id 21
    ```
    This can be undone using
    ```
    [/]
    A:admin@pe4# /tools perform log unsubscribe-from log-id 21
    ```
    In the debug outputs you'll see the outputs generated by your script as well as any resulting changes made to packets. Make sure the system has DHCP interactions ongoing so your script is being triggered.
    An alternative to subscribing to the log outputs is to use the show command for the log, `/show log log-id 21`.


    For faster testing, clear the IPoE sessions and / or trigger the DHCP renewals from the subscribers as [before](#accessing-the-lab).

    At the risk of overcrowding the debug logs, by entering `debug exclusive` and enabling
    ```
    router "Base" {
        radius {
            servers {
                server-address 10.64.13.0 { }
            }
        }
    }
    router "bng-vprn" {
        dhcp {
            all-packets {
            }
        }
    }
    ```
    the DHCP and RADIUS traffic can be displayed for troubleshooting purposes.

    2. Create a Python-policy `python-policy` that applies the Python-script to the DHCP packet-types received from the client.
    ```
    configure {
        python {
            python-policy "python-policy" {
                dhcp discover direction ingress {
                    script "task2"
                }
                dhcp request direction ingress {
                    script "task2"
                }
            }
        }
    }
    ```
    3. Apply the Python-policy to the capture SAP in VPLS `bng-vpls` and to the `group-interface` in `bng-vprn`.
    ```
    configure {
        service {
            vpls "bng-vpls" {
                capture-sap 1/1/c3/1:* {
                    dhcp {
                        python-policy "python-policy" # for DHCP Discover
                    }
                }
            }
            vprn "bng-vprn" {
                subscriber-interface "SubInt1" {
                    group-interface "GrpInt1" {
                        ipv4 {
                            dhcp {
                                python-policy "python-policy" # for DHCP Requests
                            }
                        }
                    }
                }
            }
        }
    }
    ```
3. Clear the IPoE sessions in the system and let the subscriber hosts renew their leases. Confirm the Client ID value sent by the subscribers is now used as the subscriber ID value in SR OS.

In [examples/task2.py](./examples/task2.py) a possible implementation of the file to be created in this task is provided. Feel free to refer to it for help or ideas.

<details>
<summary>Expected new subscriber IDs (after removing them from the router and clients renewing)</summary>

```
    [/]
    A:admin@pe4# /show service active-subscribers

    ===============================================================================
    Active Subscribers
    ===============================================================================
    -------------------------------------------------------------------------------
    Subscriber 0ff1ce01
               (SUB_PROF1)
    -------------------------------------------------------------------------------
    NAT Policy    : NAT_POL1
    Outside IP    : 10.67.200.2
    Ports         : 1024-1055

    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    (1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
    -------------------------------------------------------------------------------
    IP Address
                  MAC Address        Session            Origin       Svc        Fwd
    -------------------------------------------------------------------------------
    10.24.1.112
                  00:d0:f6:01:01:01  IPoE               DHCP         401        Y
    -------------------------------------------------------------------------------

    -------------------------------------------------------------------------------
    Subscriber 0ff1ce02
               (SUB_PROF1)
    -------------------------------------------------------------------------------
    NAT Policy    : NAT_POL1
    Outside IP    : 10.67.200.3
    Ports         : 1024-1055

    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    (1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
    -------------------------------------------------------------------------------
    IP Address
                  MAC Address        Session            Origin       Svc        Fwd
    -------------------------------------------------------------------------------
    10.24.1.113
                  00:d0:f6:02:02:02  IPoE               DHCP         401        Y
    -------------------------------------------------------------------------------

    -------------------------------------------------------------------------------
    Number of active subscribers : 2
    ===============================================================================
```

</details>

## Task 3: Adding more logic and caching information to re-use
We are now able to use information sent by the subscriber device when creating a subscriber ID. That's nice, can the same be achieved for information coming from the RADIUS server?

Of course!

In this scenario, the RADIUS server adds a Class attribute (RADIUS option 25) in the Access-Accept message returned to the BNG. The idea is to mirror that value in the subscriber identifier along with the Client ID, such that the subscriber identifier in the system contains bits of information provided by both the DHCP client and the RADIUS server.

As before, we'll be achieving this using a Python policy with a new Python script assigned in some strategic locations. An additional element for this task will be storing the information in the Python cache. Since we need to gather and merge information from both the DHCP and the RADIUS transaction, the standard `alc` behavior will not be enough: it only affects a single packet. Storing and retrieving information from the Python cache provides some options to extend the functionality.

For the duration of this task, make sure you have at least one of the `sub1` and `sub2` subscriber machines set up to do regular renewals of its DHCP lease using one of the methods shown [above](#accessing-the-lab).

Commands that may come in useful for this task:

```
# Remove all information from named python-policy's cache.
# Useful to test behavior with no remnants from previous iterations remaining.
/clear python python-policy "python-policy" cache all
#
# Remove all IPoE sessions from the BNG. This ensures that the next time
# the subscribers renew their DHCP lease, there will not be a pre-existing session.
/clear service id "bng-vprn" ipoe session all
#
# Trigger a refresh and reload from the specified url(s) of the python-script object,
# to ensure the object in memory is aligned with any changes made to the underlying file.
/perform python python-script reload script <script-name>
#
# For the named python-policy, show all entries present in the cache.
/tools dump python python-policy "python-policy" cache
#
# Enable debugging on a python-script by name, and subscribe your CLI session to
# the log created to receive debug logs, so you receive immediate information about
# your script's functioning
//debug python python-script <script-name> script-all-info
/tools perform log subscribe-to log-id 21
/tools perform log unsubscribe-from log-id 21
```

1. Create a file `task3_dhcp.py` in a location where the router can access it, `/home/nokia/clab-srexperts/pe4/tftpboot/` is recommended as it allows access from the router using TFTP.
    1. In this first step, we will populate a cache entry with a key of your choosing and a value equal to the DHCP client's Client ID value. Use what you learned in the previous task, the fields that must be retrieved and stored will remain the same. Documentation on the Python Cache bindings is available [here](https://documentation.nokia.com/html/3HE19212AAABTQZZA01/alc-cache.html). Starting from this snippet, build your file:
    ```
    from alc import dhcpv4
    from alc import cache


    def task_3_dhcp4_discover():
        client_id = dhcpv4.get(61)[0]
        . . .
        dhcpv4.set_relayagent(relayagent)


    if __name__ == "__main__":
        ...
    ```

    2. As before, modify the router configuration to apply `task3_dhcp.py` to DHCP Discover messages instead of the file created in the previous task. Ensure the new script is active and working.

    3. Enable the Python cache on the `python-policy` created previously. The cache is disabled by default. Feel free to explore the configuration parameters, we will use the default settings and so require only a modification of the admin-state.
    ```
    configure {
        python {
            python-policy "python-policy" {
                cache {
                    admin-state enable
                }
            }
        }
    }
    ```

    4. Verify the Python cache is being populated with the value found in the DHCP Discover messages. This can be done using a tools command:
    ```
    [/]
    A:admin@pe4# /tools dump python python-policy "python-policy" cache
    ```

    5. For DHCP Request packets, the Circuit ID value should be populated based on the corresponding subscriber's cache key entry. Can you do this in the same Python file? The snippet below can give you some ideas.
    ```
    from alc import dhcpv4
    from alc import cache


    def task_3_dhcp4_discover():
        client_id = dhcpv4.get(61)[0]
        . . .
        dhcpv4.set_relayagent(relayagent)


    def task_3_dhcp4_request():
        . . .
        dhcpv4.set_relayagent(relayagent)

    if __name__ == "__main__":
        if ord(dhcpv4.get(53)[0])
            ...
        elif ord(dhcpv4.get(53)[0])
            ...
    ```

2. Instead of copying the Client ID into the Circuit ID field, we are now copying the Client ID into a cache entry and then retrieving the cache entry's value to put into the Circuit ID. We have succeeded in adding an extra step for no reason. Let's add some extra functionality to make this extra step worth it.
    1. Create a script `task3_radius.py` in the same location as the previous scripts. This script will retrieve the Class (RADIUS option 25) from the Access-Accept message returned by the RADIUS server and append it to the cache entry created by `task3_dhcp.py`. This snippet can be used as a starting point.
    ```
    from alc import radius
    from alc import cache
    import binascii


    def task_3_radius_accept():
        . . .
        with cache as cache_object:
            . . .

    if __name__ == "__main__":
        task_3_radius_accept()
    ```
    2. Add the RADIUS script to the correct packet type and direction in the existing python-policy to make the desired behavior possible. Is it important that the same python-policy object is used here?

    3. Add the python-policy with the script assigned to the `server-policy` used for RADIUS authentication:
    ```
    configure {
        aaa {
            radius {
                server-policy "RadAuthPolicy1" {
                    python-policy "python-policy"
                }
            }
        }
    }
    ```

3. Observe that by copying the DHCP Client's and RADIUS Server's information into a cache entry, copying that cache entry into the DHCP Circuit ID field and using that field for subscriber identification makes the subscriber ID in the system completely customizable.

In [examples/task3_radius.py](./examples/task3_radius.py) and [examples/task3_dhcp.py](./examples/task3_dhcp.py) possible implementations of the files to be created in this task are provided. Feel free to refer to them for help or ideas.

<details>
<summary>Expected configuration changes</summary>

```
    configure {
        aaa {
            radius {
                server-policy "RadAuthPolicy1" {
                    python-policy "python-policy"
                }
            }
        }
        python {
            python-script "task3_dhcp" {
                admin-state enable
                urls ["tftp://172.31.255.29/task3_dhcp.py"]
                version python3
            }
            python-script "task3_radius" {
                admin-state enable
                urls ["tftp://172.31.255.29/task3_radius.py"]
                version python3
            }
            python-policy "python-policy" {
                dhcp discover direction ingress {
                    script "task3_dhcp"
                }
                dhcp request direction ingress {
                    script "task3_dhcp"
                }
                radius access-accept direction ingress {
                    script "task3_radius"
                }
            }
        }
    }
```
</details>

<details>
<summary>Expected new subscriber IDs (after removing them from the router and clients renewing)</summary>

```
    [/]
    A:admin@pe4# /show service active-subscribers

    ===============================================================================
    Active Subscribers
    ===============================================================================
    -------------------------------------------------------------------------------
    Subscriber 0ff1ce0100cafe
               (SUB_PROF1)
    -------------------------------------------------------------------------------
    NAT Policy    : NAT_POL1
    Outside IP    : 10.67.200.5
    Ports         : 1024-1055

    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    (1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
    -------------------------------------------------------------------------------
    IP Address
                  MAC Address        Session            Origin       Svc        Fwd
    -------------------------------------------------------------------------------
    10.24.1.112
                  00:d0:f6:01:01:01  IPoE               DHCP         401        Y
    -------------------------------------------------------------------------------

    -------------------------------------------------------------------------------
    Subscriber 0ff1ce0200beef
               (SUB_PROF1)
    -------------------------------------------------------------------------------
    NAT Policy    : NAT_POL1
    Outside IP    : 10.67.200.4
    Ports         : 1024-1055

    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    (1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
    -------------------------------------------------------------------------------
    IP Address
                  MAC Address        Session            Origin       Svc        Fwd
    -------------------------------------------------------------------------------
    10.24.1.113
                  00:d0:f6:02:02:02  IPoE               DHCP         401        Y
    -------------------------------------------------------------------------------

    -------------------------------------------------------------------------------
    Number of active subscribers : 2
    ===============================================================================
```

</details>


## Task 4: Two's company, three's a crowd
This whole time, two subscribers have existed in the system using all sorts of subscriber identifiers. As you may or may not have seen, the topology comes equipped with 3 subscribers. This means we are missing a subscriber. An oversight in the RADIUS server provisioning caused the third subscriber to be expected to authenticate not using its MAC address as the Username, but by its assigned hostname "server.office3".

The DHCP Client for that subscriber is already configured to send this hostname value as Client FQDN (DHCP option 81). To quickly get the third subscriber online and remove any reason for complaints, you have to find a way to copy that DHCP option's value into the Access Request Username (RADIUS option 1) field.

This task is meant as one to combine and use what you have learned in the previous tasks, the subtasks are now less detailed than before.

1. Create new files or modify the files interacting with DHCP Discover messages from previous tasks to pick up on the presence of DHCP Option 81, and to store it into the Python cache when needed. Use the domain name information only, ignore the `rcode1` and `rcode2` fields. The format of this option is defined [here](https://datatracker.ietf.org/doc/html/rfc4702#section-2) should you wish to refer to it. The client is configured to send `rcode1,rcode2,name` for the option's value.
2. Create a file `task4_radius.py` that copies the Option 81 value if present in the Python cache from the cache entry into the Username field.
3. Apply this new script to the correct combination of packet type and direction to ensure the RADIUS server receives the changed value.
4. Confirm there are now three subscribers in the system, ensure the other subscribers weren't impacted by your changes. It should still be possible for `sub1` and `sub2` to create new IPoE sessions.

In [examples/task4_radius.py](./examples/task4_radius.py) a possible implementation of the file to be created in this task is provided. Feel free to refer to it for help or ideas. Included in [examples/task3_dhcp.py](./examples/task3_dhcp.py) are a few commented lines that can be used to implement the changes required in the DHCP interactions for this task. When using the example solution, ensure the cache is empty before validating your work. This can be done using the `clear` command included above.


<details>
<summary>Expected configuration changes</summary>

```
    configure {
        python {
            python-script "task4_radius" {
                admin-state enable
                urls ["tftp://172.31.255.29/task4_radius.py"]
                version python3
            }
            python-policy "python-policy" {
                radius access-request direction egress {
                    script "task4_radius"
                }
            }
        }
    }
```
</details>
<details>
<summary>Expected new subscriber IDs (after removing them from the router and clients renewing)</summary>

```
    [/]
    A:admin@pe4# /show service active-subscribers

    ===============================================================================
    Active Subscribers
    ===============================================================================
    -------------------------------------------------------------------------------
    Subscriber 0ff1ce0100cafe
               (SUB_PROF1)
    -------------------------------------------------------------------------------
    NAT Policy    : NAT_POL1
    Outside IP    : 10.67.200.0
    Ports         : 1056-1087

    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    (1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
    -------------------------------------------------------------------------------
    IP Address
                  MAC Address        Session            Origin       Svc        Fwd
    -------------------------------------------------------------------------------
    10.24.1.112
                  00:d0:f6:01:01:01  IPoE               DHCP         401        Y
    -------------------------------------------------------------------------------

    -------------------------------------------------------------------------------
    Subscriber 0ff1ce0200beef
               (SUB_PROF1)
    -------------------------------------------------------------------------------
    NAT Policy    : NAT_POL1
    Outside IP    : 10.67.200.1
    Ports         : 1056-1087

    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    (1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
    -------------------------------------------------------------------------------
    IP Address
                  MAC Address        Session            Origin       Svc        Fwd
    -------------------------------------------------------------------------------
    10.24.1.113
                  00:d0:f6:02:02:02  IPoE               DHCP         401        Y
    -------------------------------------------------------------------------------

    -------------------------------------------------------------------------------
    Subscriber 0ff1ce0300babe
               (SUB_PROF1)
    -------------------------------------------------------------------------------
    NAT Policy    : NAT_POL1
    Outside IP    : 10.67.200.10
    Ports         : 1024-1055

    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    (1) SLA Profile Instance sap:[1/1/c3/1:100] - sla:SLA_PROF1
    -------------------------------------------------------------------------------
    IP Address
                  MAC Address        Session            Origin       Svc        Fwd
    -------------------------------------------------------------------------------
    10.24.1.114
                  00:d0:f6:03:03:03  IPoE               DHCP         401        Y
    -------------------------------------------------------------------------------

    -------------------------------------------------------------------------------
    Number of active subscribers : 3
    ===============================================================================
```
</details>

## Task 5 (optional): Some suggestions for additional work
1. In this lab, IP addresses are being assigned via RADIUS. Using what you've learned, can you take this power away from the RADIUS server?
2. Can these Python policies and caches be used to phase out subscriber policies or NAT profiles?
3. When something goes wrong in any of the Python scripts, can you do any kind of error reporting?
4. ... - your ideas are welcomed!
