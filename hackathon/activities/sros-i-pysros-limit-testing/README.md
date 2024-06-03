# pySROS best practices and limits

| Item | Details |
| --- | --- |
| Short Description | pySROS provides unrivaled flexibility for SR OS but in this activity we'll explore some of the best practices for local and remote Python applications |
| Skill Level | Intermediate |
| Tools Used | SR OS, Python (with the `pysros` library) |

## Objective
In this lab, the best practices for pySROS are tested. We'll play around with the robustness of the framework and look for the limits of the on-board interpreter. For this, as a first task, we'll gauge how fast and efficient operations against the configuration are when running on-box compared to off-box executions. Following that, for on-box executions, we'll look at memory consumption and runtime limits. This is key, as it ensures custom pySROS commands and scripts can't affect other key processes in the router. The third task is optional and is somewhat of a mini competition: we welcome you to discover breaking issues in pySROS on the router.

## Accessing the lab
In this lab you will interact with model-driven SR OS, so any model-driven SR OS router in the topology would work. For this text we will assume the `p2` node is used.

```
ssh admin@clab-srexperts-p2
```

## Task 1: Comparing speed of pySROS on-box and off-box

Logic dictates that when executed through the on-box interpreter, pySROS is able to quickly collect small amounts of data. It doesn't have to pass through the network after all. This implies off-box execution of pySROS scripts prefers queries that fetch large amounts of data as it has less overhead. In this task, we will put that to the test.

1. Create a pySROS script for on-box execution that prints the `in-octets` counter for port `1/1/c1/1` as the CLI output. The path for this counter is `/state/port[port-id="1/1/c1/1"]/statistics/in-octets`. Either put this script on the tftp location accessible from SR OS (`/home/nokia/clab-srexperts/p2/tftpboot/task1.py` as seen from outside the router equals `tftp://172.31.255.29/` as seen from inside the router) or put the file on the router CF3. We assume the former, as that is easier for development. The expected output is similar to the following:

```
[/]
A:admin@p2# pyexec tftp://172.31.255.29/task1.py
4079633
```

No frills or fancy business, just being able to output the data is enough.

2. Try your script both from the cloud instance hosting your lab topology and from your laptop (if possible!). Update the credentials and hostname when running remotely. Disable `hostkey_verify`, this is acceptable for this lab environment and lets us skip the step of explicitly trusting the router's SSH server host key. Make sure to test the remote execution options twice. Why does the first remote execution take longer than the second?

3. Instead of outputting the data, we'll now measure how long retrieving the `state` data takes. What do you expect the result will be? How big do you expect the difference to be? Use the time library and optionally add some extra iterations to determine an average time required for the `get` operation for the `ìn-octets` counter.

Does retrieving the entire `state` tree change the results any?

Why would few queries returning large result sets be preferable to many queries returning small result sets?

In the [examples](./examples) folder some inspiration is provided in the file [task1.py](./examples/task1.py).

4. With pySROS, filters can be added to `get` operations. Modify your call from the previous subtask, add a filter that retrieves only the `in-octets` counter from subtask 2. What do you observe in the results? What does that imply about where the filtering is being implemented?

## Task 2: Explore pySROS' limits for on-box executions

As SR OS routers are generally deployed in critical parts of the network where robustness and guarantees are key, pySROS is all well and good as long as it can't cause any unintended side-effects on the routers. To verify this, we find that the SR OS documentation states:

```
When a Python 3 application is spawned, SR OS confirms that the minimum percentage of sufficient free system memory is available. The percentage value for minimum available system memory is configurable within the MD-CLI environment settings.
```

This means the Python processes will never be able to starve the system of memory.

1. In this first subtask, can you verify the memory limit for a single pySROS execution executed on-box? You may find this information either in the documentation, via `/state` or by simply trying to consume all the memory you can in a script.

2. The second subtask consists of the exact same question, applied not to memory consumption but to time consumption. An execution lifetime limit should exist for the interpreter to ensure processes can't run indefinitely. Does such a limit exist? Does it matter whether we use a `command-alias` or a script executed via `pyexec`?

In case you're looking for some hints or ideas, feel free to refer to the [examples/task2.py](./examples/task2.py) file. This file is written to be executed from the router's flash card `cf3` only.

## Task 3: Getting creative...

Continuing the spirit of the second task, this task is an open invitation for you to find issues or problems in the pySROS framework. Anything you can think of, feel free to unleash it on the systems made available to you and let us know if you find something that isn't in line with your expectation or appears to be misbehaving. Any behavior caused by pySROS that inadvertently impacts the system's forwarding capacity or causes unexpected reboots shouldn't be possible. Even if things do behave the way you expected, let us know what you're trying. We're excited to hear what you're coming up with!
