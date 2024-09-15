# Catching and solving resource shortages for BNG subscribers

| Item | Details |
| --- | --- |
| Short Description | Focus on identifying and troubleshooting issues with TPSDA resources |
| Skill Level | Intermediate |
| Tools Used | SR OS as a BNG, Python (with the `alc` library) |

In addition to the `alc` module classically known for BNG usecases with SR OS, pySROS can be used to interact with subscribers as well. It can't modify DHCP or RADIUS packets in-flight like `alc` can, however it can be used to enrich CLI outputs (that will then also work remotely), extend syslog functionality and add some automation to the system. The latter will be explored in this usecase.

## Objective

In this exercise, the problem to address is subscribers hitting the limit of the amount of NAT sessions they are allowed to open. This limit is set very conservatively in our BNG and it should be increased dynamically up to an acceptable value for the average subscriber. We'll use the BNG node `pe4`, some web servers in the topology and two IPoE subscribers simulated by Alpine Linux containers. The BNG is configured to do NAT (Network Address Translation) on the subscribers IP addresses, allowing the subscribers access to the network and to reach webservers hosted at `web1.srexperts.topology`, `web2.srexperts.topology` and `web3.srexperts.topology` in the containerlab topology.

## Accessing the lab

In this lab you will work with subscribers on the BNG node `clab-srexperts-pe4`. You can log in by using the DNS name of the container and the credentials provided to you.

```
ssh admin@clab-srexperts-pe4
```

The (IPoE) subscribers are emulated using Linux containers. For this usecase, at least one of the BNG subscribers will need to be logged in to. They can be accessed using the provided credentials as follows:

```
ssh user@clab-srexperts-sub1
ssh user@clab-srexperts-sub2
```

The third subscriber does not work by default, this is part of another usecase and will not be relevant here.

## Verify the subscribers exist in the system

Use `show service active-subscribers` to verify subscribers are working. Two subscribers should exist in the system. The subscribers are assigned a generic subscriber identifier by the system. This identifier is formed by combining the device MAC and the SAP identifier the subscriber arrived on, separated by a pipe symbol (`|`).

For this usecase, the example outputs given in this document should match what you see in your system. If you notice differences in output or behavior, please let us know!

Subscribers `00:d0:f6:01:01:01|1/1/c3/1:100` and `00:d0:f6:02:02:02|1/1/c3/1:100` will exist in the system. Your output should look similar to:

```
[/]
A:admin@pe4# show service active-subscribers

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

## Task 1: Exploring NAT

Log in to either of the subscribers and execute the command `ping web1.srexperts.topology`.

Does it work? Can you identify which NAT binding was generated?

Try executing `wget web1.srexperts.topology` now. Did that work? Is the NAT binding different this time? Can you identify the relevant routing-instances in the BNG node `pe4` that are playing a part in this functionality?

Commands that could come in handy are
- `tools dump nat sessions`
- `/show service active-subscribers detail`
- `/admin show configuration full-context | match nat`

Your output should be similar to:

```
[/]
A:admin@pe4# tools dump nat sessions

===============================================================================
Matched 1 session on Slot #2 MDA #1
===============================================================================
Owner               : L2-aware Subscr 00:d0:f6:01:01:01|1/1/c3/1:100
Policy              : NAT_POL1
FlowType            : ICMP              Timeout (sec)       : 59
Inside IP Addr      : 10.24.1.112
Inside Identifier   : 44
Outside IP Addr     : 10.67.200.1
Outside Identifier  : 1042
Foreign IP Addr     : 10.64.21.11
Nat Group           : 1
Nat Group Member    : 1
-------------------------------------------------------------------------------
===============================================================================
```

Useful information in this output includes; the outside and inside IP addresses for the subscriber as well as the foreign IP it is interacting with. You can tell based on this output which subscriber is creating the binding and which protocols are being used.

## Task 2: Exhausting NAT

Try both `ping web2.srexperts.topology` and `wget web2.srexperts.topology`.

Does the behavior differ compared to task 1? If it does, can you determine why, using what you saw in the previous task?

If the behavior hasn't changed, try `ping web3.srexperts.topology` and `wget web3.srexperts.topology`. Is the behavior still the same?

If you wish to verify or test any assumptions, you can reset the state of NAT bindings on the BNG using either:

```
# Renew the IPoE lease via
## On pe4
clear service id 401 ipoe session all
## On the subscriber host you are using
sudo ifdown eth1.100; sudo ifup eth1.100
```

Or, on `pe4`, execute:

```
/clear nat l2-aware-sub *
```

The expected outcome in this task is that the `ping` and `wget` commands start failing. The output for failing requests is similar to the following:

```
sub1:~$ ping web3.srexperts.topology
PING web3.srexperts.topology (10.64.23.11) 56(84) bytes of data.
From 10.24.1.5 (10.24.1.5) icmp_seq=1 Packet filtered

sub1:~$ wget web1.srexperts.topology
--2024-05-28 14:20:32--  http://web1.srexperts.topology/
Resolving web1.srexperts.topology (web1.srexperts.topology)... 10.64.21.11
Connecting to web1.srexperts.topology (web1.srexperts.topology)|10.64.21.11|:80... failed: Host is unreachable.
```

With the number of connections being created ever increasing, the number of ports required by the subscribers' devices is growing. For the next task, we'll explore a way to dynamically increase these NAT limits taking into account what the average subscriber is using.

## Task 3: Extending NAT

What (should have) happened during task 2 is that the maximum amount of sessions to be NATted for a single subscriber session was fully consumed. As you might have noticed, this limit is set low, limiting subscribers to 3 sessions. NAT bindings are created for ICMP interactions and TCP sessions, though as you might have noticed the ICMP bindings persist for longer while the TCP NAT bindings are destroyed when the TCP session is. An alternative to `wget` that allows inspection of the TCP NAT bindings is to `telnet` from a user to the servers' port 80.

As with most operational activities, we would like to catch such situations (running out of resources) before they become critical and end-users experience any impact of the limits being imposed upon them. In this scenario, we would like to implement a solution based around averaging the number of NAT bindings observed versus the number of hosts actively using NAT bindings on the system.

As an example, if there is 1 user in the system and 3 NAT bindings are in use, that means we are at the limit and we should raise the limit to avoid complaints (scale limits permitting). Similarly, with 2 users and 3 NAT bindings, we would be (on average) on 1.5 NAT bindings. After rounding up to 2, this is still below the configured limit.

Using CRON and pySROS on the SR OS device, implement a solution that increases the configuration under `/configure service nat nat-policy "NAT_POL1" session-limits max` to a value that enables this average value.

Feel free to refer to [nat.py](./examples/nat.py) in the [examples](./examples/) folder for inspiration or ask for assistance. In general, these steps are required:

1. Find the information that lets you determine the average amount of consumed NAT bindings per host in `/state` using either the [YANG-model](https://github.com/nokia/7x50_YangModels/blob/master/latest_sros_24.7/nokia-submodule/nokia-state-svc-nat.yang#L45) or the MD-CLI. The information to look for is in a `sessions` context.

2. Create a Python script that finds this information, determines if the maximum number of NAT bindings is acceptable and changes the value if not. Create your file in `/home/nokia/clab-srexperts/pe4/tftpboot/` on your Hackathon instance. This file will automatically become available to `pe4` at `tftp://172.31.255.29/`. Use a name for the script that makes sense for you. In the remaining subtasks, we will use `nat.py` as the filename.

Your script would collect data from

```
/nokia-state:state/service/nat/nat-policy[name="NAT_POL1"]
/nokia-conf:configure/service/nat/nat-policy[name="NAT_POL1"]/session-limits/max
```

and update the configuration of the latter. Examples of how to go about this are available [here](https://documentation.nokia.com/sr/24-7/pysros/examples.html#examples). The example script outputs look like

```
[/]
A:admin@pe4# pyexec "tftp://172.31.255.29/nat.py"
At time 2024/05/16 13:42:51: Found 2 hosts using 6 bindings, returning average 3
At time 2024/05/16 13:42:51: Getting dangerously close to session-limit 3, as we are over 66% of this value already at 3
At time 2024/05/16 13:42:51: Increasing session-limits from 3 to 6

[/]
A:admin@pe4# pyexec "tftp://172.31.255.29/nat.py"
At time 2024/05/16 14:05:21: Found 2 hosts using 6 bindings, returning average 3
At time 2024/05/16 14:05:21: Not increasing session-limits, 6 is ok.
```

3. Configure the Python script as a CRON task.

Since we would like to control this resource (and, in particular, avoid hitting the limit on it) while not actively looking at the CLI, CRON is an ideal tool for this.

CRON is a job-scheduler utility for UNIX-like operating systems and has been adopted in SR OS. CRON functionality in SR OS includes the ability to specify scripts that need to be run on a given schedule including; one-time only functionality (one-shot), interval and calendar functions. Scheduled reboots, peer turn-ups, service assurance agent tests and more can all be scheduled with CRON, as well as OAM events, such as connectivity checks, or troubleshooting runs. In this case, we will use the CRON functionality to schedule periodic script executions. To accomplish this, the following steps are necessary:

3.1. Create a Python script object under `/configure python python-script`. Ideally, use `tftp://172.31.255.29/nat.py` or similar as the location, as it allows for easier debugging / troubleshooting in general. Any changes made to the script file can be loaded into the SR OS object using `/perform python python-script reload script <python-script name>`. Make sure your script can be executed and works with `pyexec` before proceeding.

3.2. Create a script-policy under `/configure system script-control`, remember the `name` and `owner` the policy is created with. Assign the python-script object to the script-policy. Create a results directory for your script-policy, e.g. `cf3:/results_cron_nat/`. Make sure that directory exists.

3.3. Create a CRON schedule under `/configure system cron`, set it to run every 30 seconds.

3.4. Check and make sure your script is running at the configured intervals and is performing as expected.

Tip: Make sure all configuration you add has its `admin-state` set to `enable`!

The target configuration to add in this section is the following:

```
configure {
    python {
        python-script "cron-nat" {
            admin-state enable
            urls ["tftp://172.31.255.29/nat.py"]
            version python3
        }
    }
    system {
        cron {
            schedule "cron-nat" owner "TiMOS CLI" {
                admin-state enable
                interval 30
                type periodic
                script-policy {
                    name "cron-nat"
                    owner "admin"
                }
            }
        }
        script-control {
            script-policy "cron-nat" owner "admin" {
                admin-state enable
                results "cf3:/results_cron_nat/"
                python-script {
                    name "cron-nat"
                }
            }
        }
    }
}
```

You can use the `file list` and `file show` commands to show files being generated in `cf3:/results_cron_nat/`.

4. Repeat task 2 and hit the limit once again. If the value is set to `6` either lower it back down to `3` or use an alternative method of generating long(er) lasting NAT bindings. Confirm you have hit the limit and let the CRON task triggering your Python script change the configured limit. Confirm the limit was raised either via the script's output, the router configuration or from the subscribers by triggering additional NAT bindings that would go over the previously configured limit.
