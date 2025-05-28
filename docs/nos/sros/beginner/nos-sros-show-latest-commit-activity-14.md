---
tags:
  - SR OS
  - pySROS
  - MD-CLI
  - Python
---

# Creating a custom command to show latest commits


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Create a custom `show` command that displays information about the system's commit history                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Short Description**       | Using Python with the pySROS library, you will create a custom `show` command that displays information about the latest commits. The output will be a table containing the ID, the time and date, the user who performed the commit and some information about the differences introduced in the commits.                                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [Python](https://docs.python.org/3.4/), [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html), [MD-CLI](https://yang.labctl.net/yang/SROS/25.3.R1/l)                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Topology Nodes**          | :material-router: PE1                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [Basic Python 3 tutorial](https://docs.python.org/3/tutorial/index.html)<br/>[SR OS YANG browser (Commit History)](https://yang.labctl.net/yang/SROS/25.3.R1/t/!b!nokia/!p!_all!/%2Fstate:state%2Fsystem%2Fmanagement-interface%2Fconfiguration-region[region-name=*]%2Fcommit-history%2Fcommit-id[id=*]%2Fid)<br/>[pySROS examples](https://network.developer.nokia.com/static/sr/learn/pysros/latest/examples.html)<br/>[SR OS commit history documentation](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/model-driven-management-interfaces.html#ai9exj5x5m) |

In this activity you will implement a custom `show` command to display information about the latest commits performed on a system. To do this, you will write a Python script that uses pySROS to retrieve information from the system. The output should include at least the commit ID, the date and time of the commit, the name of the user who performed the change and some information about the changes introduced with that commit.

## Objective

In this activity you will learn about navigating through the MD-CLI and updating configuration in model-driven SR OS. You will explore the YANG model that lives at the core of the system and use it to navigate through the datastores on the system to find information you need.

Using this information, you will use Python to develop your own MD-CLI command to use on the system and configure it as a permanent addition to your router's environment so that anyone can use it without having to understand the complexity that lies behind the command.

## Technology explanation

Since 2017, SR OS has provided the model-driven mode in addition to the original classic mode. In the next sections we will go over some of the changes and features coming with model-driven mode, as well as introduce the problem that we aim to solve in this activity.


### Model-driven SR OS, YANG models and datastores
As the term "model-driven" suggests, a model-driven Network Operating System (NOS) such as SR OS has one or more data models at its core.  These data models compile together to provide the schema for the system.  These data models are written using a language called YANG and the data models used in this activity are for SR OS and are available [online](https://github.com/nokia/7x50_YangModels).

These YANG models are used to provide consistency between the YANG modeled interfaces; the MD-CLI, NETCONF and gNMI. They describe the structure and data-types of everything in SR OS.

One of the advantages of model-driven SR OS is that the system becomes transactional in nature. Changes have to be explicitly applied from a `candidate` configuration datastore to the `running` configuration datastore via a `commit` action rather than being immediately applied. This reduces the chances for operational impact to occur as a result of partial configuration changes.  SR OS will atomically apply configuration changes to the system, this means that either all changes stored in the `candidate` configuration datastore will be successfully applied upon a `commit`, or none of them will be applied and your device will remain operationally intact.

Rather than having to store rollback points explicitly, model-driven SR OS can create them automatically on each successful `commit`. That introduces the need for visualizing the `commit` history in a clear format, as an operator may want to rollback to an earlier configuration and will need to find out which `commit` corresponded to the desired state.

The YANG model also shows us the datastores supported by the system. For the release of SR OS used in this activity, we have access to 5 different datastores though we will only use the `startup`, `running` and `candidate` datastores in this activity.

The role of the `startup` datastore is to store the configuration to be loaded at system startup. The `running` datastore contains the live configuration on the system and the `candidate` datastore acts as a staging area where any changes to the configuration can be made, validated and committed once ready.

Using the MD-CLI, you will navigate through the hierarchical structure of the datastores to help you build a new command as will be shown in the next section.

/// details | Side quest
Can you identify which other datastores are supported?
///

### MD-CLI
Based on the YANG model, the MD-CLI can be used to display configuration and state information in different paths. This information can be retrieved using the [`info` command](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/display-information.html#ai89jylu4e), which outputs the information in the same structure it is saved in the YANG datastore.

- The `pwc` command can be used to display the path associated with a given context (in various encodings).
- The `tree` command can be used to display the underlying YANG schema of the device.
- The `/state` branch stores read-only information about the current state of the system, while modifiable configurations are stored in the `/configure` branch.

In the MD-CLI, the session is either in operational or [configuration mode](https://documentation.nokia.com/sr/25-3/7x50-shared/md-cli-user/edit-configuration.html), which is indicated in the command prompt.

/// details | Command prompt in operational mode
```
[/]
A:admin@g15-pe1#
```
///
/// details | Command prompt in exclusive configuration mode
```
(ex)[/]
A:admin@g15-pe1#
```
///

The `/state` branch is accessible in either mode while the `/configure` branch can only be accessed in configuration mode.

In configuration mode, any changes are made to a candidate datastore, as opposed to the running datastore, which holds the running configuration of the system.
When entering configuration mode, the running datastore is copied into a separate baseline datastore.
Then, changes to the configuration are saved to a third candidate datastore.
This means that, upon entering configuration mode, all three datastores have the same content, and before any changes are made to the candidate datastore, it will match the baseline datastore.
The `commit` command is used to validate changes and merge the candidate configuration into the running datastore.

In addition, configuration mode is either global, private, exclusive or read-only.

- All users in global configuration mode share the same candidate datastore, so each user is able to see the each other's modifications.

- In private mode, the user works on their own private candidate datastore, and their uncommitted changes are not visible to others.

- In exclusive mode, only a single user is allowed to modify the global datastore. If another user is already editing the global datastore, either in global or exclusive mode, it is impossible to enter exclusive mode. If there is a user in private mode, it is possible to enter exclusive mode, but the other user will not be able to commit their changes.

- In read-only mode, the user can see changes made to the global candidate datastore, but cannot make any modifications.

As you are working on the candidate datastore, an asterisk on the prompt indicates there are changes that have not been committed. Note that is also possible for the baseline datastore to become out-of-date with the running datastore, which is indicated by an exclamation mark in the prompt. This might happen, for example, if a user is in global mode and another user already in private mode commits their changes, or if a user is in private mode and a user in global or private mode commits their changes. In this case, the baseline datastore needs to be updated with the `update` command before the candidate changes can be committed.

### Commit History
With `commit` taking on a prominent role in configuration management, being able to browse through the changes made with each commit and any information associated with them becomes key. A command to display this information exists:

- `show system management-interface commit-history`

This command displays a human-centric representation of the commit history information stored in the router. Using the MD-CLI you can look at what is stored in the router as well. The information displayed by the `show` command is available under the following path:

- `/state system management-interface configuration-region configure commit-history`


### Python on SR OS and pySROS
Modern releases of model-driven SR OS provide a [Python environment](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html) using the [MicroPython](https://docs.micropython.org/en/latest/index.html) interpreter, based on Python 3.4.

The [pySROS library](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html) provides a way to programmatically interface with SR OS from a Python script and allows a developer to query and modify the various datastores. This can be done from a script being executed directly within the SR OS node, or from a remote host in which case pySROS handles establishing a remote connection to the SR OS node.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Make a change to the configuration and check the YANG datastore

In this section you will become comfortable with the MD-CLI when looking for information and making changes.  In order to build your own show command, both of these will be relevant.

To begin, you will use the MD-CLI to make changes to the shared `candidate` configuration datastore and verify how this is reflected in the `running` datastore.
For this exercise, we will disable the port 1/1/c6/1, which is connected to node `client01`.

!!! warning

    Before you finish the activity, make sure to undo all the changes you've made to the configuration.


Start by checking that the port is up using the `show` command. Confirm that you see the same status in the `running` datastore using the `info` command on the `/state` YANG branch.

/// details | Check that the port is up with the `show` command
/// tab | Command
```
show port "1/1/c6/1"
```

///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# show port "1/1/c6/1"

===============================================================================
Ethernet Interface
===============================================================================
Description        : link to client01
Interface          : 1/1/c6/1                   Oper Speed       : 100 Gbps
FP Number          : 1                          MAC Chip Number  : 1
Link-level         : Ethernet                   Config Speed     : N/A
Admin State        : up                         Oper Duplex      : full
Oper State         : up
[...] (truncated)
```
///
///

/// details | Confirm the same status in the `running` datastore
/// tab | Commands
```
info /state port 1/1/c6/1 port-state
info /state port 1/1/c6/1 oper-state
```

///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# info state port 1/1/c6/1 port-state
    port-state up

[/]
A:admin@g15-pe1# info state port 1/1/c6/1 oper-state
    oper-state up
```
///

!!! tip

    The `oper-state` key shows the operational state of the port, whether it is administratively enabled or disabled.
    If the port is administratively enabled but it is operationally down, `oper-state` will be `down`.

///

Then, enter configuration mode and check the configuration of the port.

/// tab | Commands
```
edit-config exclusive
info /configure port 1/1/c6/1
```

///
/// tab | Expected output

```
[/]
A:admin@g15-pe1# edit-config exclusive
INFO: CLI #2060: Entering exclusive configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(ex)[/]
A:admin@g15-pe1# info configure port 1/1/c6/1
    admin-state enable
    description "link to client01"
    ethernet {
    mode access
        encap-type dot1q
        mtu 8704
    }
```
///

!!! warning

    If you are unable to enter the exclusive configuration mode, check if someone else is in configuration mode.
    You can use the command `show system management-interface configuration-sessions` to do this.


Note that the configuration of the port is `admin-state enable`, meaning it is administratively up.
Let's disable the port in the configuration and check that it actually goes down.

Change the configuration of the port to be administratively down but don't commit your changes. Confirm that this changes the candidate datastore and not the running configuration.

/// tab | Commands
```
/configure port 1/1/c6/1 admin-state disable
info /configure port 1/1/c6/1
info from running /configure port 1/1/c6/1
```

///
/// tab | Expected output

```
(ex)[/]
A:admin@g15-pe1# /configure port 1/1/c6/1 admin-state disable

*(ex)[/]
A:admin@g15-pe1# info /configure port 1/1/c6/1
    admin-state disable
    description "link to client01"
    ethernet {
        mode hybrid
    }

*(ex)[/]
A:admin@g15-pe1# info from running /configure port 1/1/c6/1
    admin-state enable
    description "link to client01"
    ethernet {
        mode hybrid
    }
```
///

!!! tip
    In configuration mode, you can use the `compare` command to see your uncommitted changes and `discard` to discard any changes you've made.

Commit your changes and check the running datastore again. It should now contain your modifications.

/// tab | Commands
```
commit comment "Disable port 1/1/c6/1 to client01"
info from running /configure port 1/1/c6/1
```

///
/// tab | Expected output

```
*(ex)[/]
A:admin@g15-pe1# commit comment "Disable port 1/1/c6/1 to client01"

(ex)[/]
A:admin@g15-pe1# info from running /configure port 1/1/c6/1
    admin-state disable
    description "link to client01"
    ethernet {
        mode hybrid
    }
```
///

As before, check the state of port `1/1/c6/1` and confirm that it actually went down.

/// details | Check the status of the port using the `show port` command
/// tab | Command
```
show port "1/1/c6/1"
```

///
/// tab | Expected output
```
(ex)[/]
A:admin@g15-pe1# show port "1/1/c6/1"

===============================================================================
Ethernet Interface
===============================================================================
Description        : link to client01
Interface          : 1/1/c6/1                   Oper Speed       : 100 Gbps
FP Number          : 1                          MAC Chip Number  : 1
Link-level         : Ethernet                   Config Speed     : N/A
Admin State        : down                       Oper Duplex      : full
Oper State         : down
[...] (truncated)
```
///
///

### Check the commit history and find your commit

In model-driven SR OS, a commit history is kept containing details about all the times the configuration has been modified.

Check the commit history for the changes you made to the configuration.

/// tab | Command
```
show system management-interface commit-history
```

///
/// tab | Expected output
```
(ex)[/]
A:admin@g15-pe1# show system management-interface commit-history

===============================================================================
Commit History
===============================================================================
Total Commits : 26

32
  Committed 2025-04-14T09:38:07.1+00:00 by admin (MD-CLI) from 172.31.255.29
  Comment   "Disable port 1/1/c6/1 to client01"
  Location  "tftp://172.31.255.29/config.txt"
[...]
```
///

!!! tip
    Each commit in the history has an unique ID. In the output above, the commit ID is 32.

!!! warning
    It is possible that the latest commit ID does not correspond to the number of total commits, such as in the example above.
    To get the latest commit you should always check for the commit with the highest ID, while the number of commits is the total number of entries in the commit history.

You should find the details for your latest commit, including a timestamp, your username and the comment you added in the `show` command output. Confirm that this information is saved in the `running` datastore as well.

/// tab | Command
```
info /state system management-interface configuration-region configure commit-history commit-id <id>
```

///
/// tab | Expected output
```
(ex)[/]
A:admin@g15-pe1# info /state system management-interface configuration-region configure commit-history commit-id 32
    timestamp 2025-04-14T09:38:07.1+00:00
    user "admin"
    type md-cli
    from 172.31.255.29
    location "tftp://172.31.255.29/config.txt"
    comment "Disable port 1/1/c6/1 to client01"
```
///



### Use pySROS to get information about the commit history
In this section, we'll use the Hackathon VM instance that comes with Python and pySROS preinstalled to query information about the commit history from the YANG datastore.

!!! warning

    The code written in this section should be compatible with the Python environment in model-driven SR OS, which is a limited version based on Python 3.4.
    Check [the official documentation](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html) for more details.

In your Hackathon VM instance, start an interactive Python interpreter using the `python` command.

```
❯ python
Python 3.11.2 (main, Nov 30 2024, 21:22:50) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

Inside the Python shell, use the `connect` function from pySROS to create a connection to the router. Examples for how to do this are available [here](https://network.developer.nokia.com/static/sr/learn/pysros/latest/examples.html#connecting-to-the-sr-os-model-driven-interface), while the complete documentation for the `connect` function is available [here](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.connect).

/// details | Import the pySROS function `connect` and create a connection to your node
```python
from pysros.management import connect
connection = connect(host = "clab-srexperts-pe1", username = "admin", hostkey_verify = False)
```

!!! note
    Executing `connect()` might take some time when it connects for the first time, as it needs to transfer information from the node to establish the connection.
    On posterior connections, this function will execute much faster, as the information will be kept cached.
    
!!! warning
    The option `hostkey_verify = False` disables verification of the host key when establishing the SSH connection. This option should be enabled if used in a production environment.
///

In the previous sections, we queried the commit history saved in the `running` datastore directly from the MD-CLI, using `info /state system management-interface configuration-region configure commit-history`.

All data in the datastore has a unique path that can be retrieved from the MD-CLI. Using a combination of navigating through the context hierarchy and the `pwc` command, find out under which path the commit-history is stored.

/// details | Uncover the path associated with commit-history
/// tab | Command
```
/state system management-interface configuration-region configure commit-history
pwc json-instance-path
```
///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# state system management-interface configuration-region configure commit-history

[/state system management-interface configuration-region configure commit-history]
A:admin@g15-pe1# pwc json-instance-path
Present Working Context:
/nokia-state:state/system/management-interface/configuration-region[region-name="configure"]/commit-history
```
///
///

The path can also be found [here](https://yang.labctl.net/yang/SROS/25.3.R1/l/!b!nokia/!p!_all!/%2Fstate:state%2Fsystem%2Fmanagement-interface%2Fconfiguration-region[region-name=*]%2Fcommit-history).

Using the interactive Python interpreter and the connection you created in the previous step, use the [`get()` method](https://network.developer.nokia.com/static/sr/learn/pysros/latest/introduction.html#obtaining-data) to query information stored in the `running` datastore from the commit history path.

/// details | Query YANG data with the `get()` method
```python
path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
connection.running.get(path)
```
///

Getting the commit history data will return a [Python dictionary](https://docs.python.org/3.4/tutorial/datastructures.html#dictionaries), in which the keys are the commit IDs. You can get a list of all commit IDs with the pySROS `get_list_keys()` method. The commit with the highest ID will be the most recent.

Once again use the interactive Python interpreter and use the `get_list_keys()` method instead of the `get()` method to retrieve only the commit IDs.

/// details | Get the highest commit ID with the `get_list_keys()` method
```python
connection.running.get_list_keys(path)
```
///

Use the previous call to find the commit-history entry that corresponds to the highest commit ID found.
/// details | Get the `commit-history` entry associated with the highest commit ID
```python
highest_commit_id = max(connection.running.get_list_keys(path))
path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id[id=%s]" % highest_commit_id
connection.running.get(path)
```
///

The information you get through pySROS should correspond to the information obtained through the MD-CLI, make sure this is the case and ask for assistance if it is not.

/// details | Iterate through and print the info about the latest commit
/// tab | Command
```python
latest_commit = connection.running.get(path)
for key,value in latest_commit.items():
    print(key, value)
```
///
/// tab | Expected output
```python
>>> for key,value in latest_commit.items():
...     print(key, value)
...
id 32
timestamp 2025-04-14T09:38:07.1Z
user admin
type md-cli
from 172.31.255.29
location tftp://172.31.255.29/config.txt
increment-location cf3:\.commit-history\config-2025-04-14T09:38:07.1Z-32.is
comment Disable port 1/1/c6/1 to client01
```
///
You should see the same data as what is returned by the command `info state system management-interface configuration-region configure commit-history commit-id <id>`, where <id> is the highest commit ID available, in the MD-CLI.
///

Having the commit history obtained using pySROS, it is also possible to display a SR OS style table with this information.
From pySROS, import `Table` and use the commit history details to [build the table](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros-pprint-table-example-usage).
Your table should include the commit ID, its time, the user name and source, and the comment (if it exists).


/// details | Build a table with the commit history information
/// tab | Command
```python
from pysros.pprint import Table

path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
data = connection.running.get(path)

columns = [(4, "ID"), (25, "Time"), (15, "User"), (15, "From"), (50, "Comment")]
table = Table("Commit History", columns, width = 120, showCount = "commits")
rows = []

for id in sorted(data.keys()):
    commit = data[id]
    row = []
    row.append(id)
    row.append(commit['timestamp'])
    row.append(commit['user'])
    row.append(commit['from'])
    if 'comment' in commit:
        row.append(commit['comment'])
    else:
        row.append("")
    rows.append(row)

table.print(rows)
```
///
/// tab | Expected output
```
>>> from pysros.pprint import Table
>>>
>>> path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
>>> data = connection.running.get(path)
>>>
>>> columns = [(4, "ID"), (25, "Time"), (15, "User"), (15, "From"), (50, "Comment")]
>>> table = Table("Commit History", columns, width = 120, showCount = "commits")
>>> rows = []
>>>
>>> for id in sorted(data.keys()):
...     commit = data[id]
...     row = []
...     row.append(id)
...     row.append(commit['timestamp'])
...     row.append(commit['user'])
...     row.append(commit['from'])
...     if 'comment' in commit:
...         row.append(commit['comment'])
...     else:
...         row.append("")
...     rows.append(row)
...
>>> table.print(rows)
========================================================================================================================
Commit History
========================================================================================================================
ID   Time                      User            From            Comment
------------------------------------------------------------------------------------------------------------------------
[...]
32   2025-04-14T09:38:07.1Z    admin           172.31.255.29   Disable port 1/1/c6/1 to client01
------------------------------------------------------------------------------------------------------------------------
No. of commits: 28
========================================================================================================================
```
///
In the example above, we create a `Table` object, which takes as arguments the title, the columns, the width, and an optional parameter to show as the total count.
The columns argument is a list of tuples, where each pair has an integer, which is the width of the column, and a string, which is its title.
///



### Compile your Python code into a script and create a custom MD-CLI command

Now that you have used pySROS to retrieve the commit history information and can print a SR OS style table with it, gather your code and put it into a single script. Test it in your remote environment and then transfer it to `PE1`.

/// details | Exception handling in a live environment

If there is an issue executing a statement or an expression in Python, an exception is raised.
If this occurs in the interactive interpreter, this will simply be printed to the terminal but if the script is running non-interactively (e.g. through `pyexec` on SROS), its execution
will be halted. As such, when writing code to use in a live environment it is important
to implement appropriate [exception handling](https://docs.python.org/3.4/tutorial/errors.html#handling-exceptions).

With the pySROS code we have used for this activity so far, the functions that might raise exceptions are [`connect()`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.connect)
and [`get()`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.get)
if there is an error in their execution, such as failing to connect or trying to get a non-existent path.
A simple exception handling implementation for these functions where we inform the user that an issue was encountered and exit gracefully might be as follows.

```python
import sys
from pysros.management import connect, InvalidPathError, ModelProcessingError, InternalError, SrosMgmtError

try:
    connection = connect(host = "clab-srexperts-pe1", username = "admsin", hostkey_verify = False)
except RuntimeError as runtime_error:
    print("Failed to connect.  Error:", runtime_error)
    sys.exit(1)
except ModelProcessingError as model_proc_error:
    print("Failed to create model-driven schema.  Error:", model_proc_error)
    sys.exit(1)

path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"

try:
    data = connection.running.get(path)
except RuntimeError as runtime_error:
    print("Runtime Error:", runtime_error)
    sys.exit(1)
except InvalidPathError as invalid_path_error:
    print("Invalid Path Error:", invalid_path_error)
    sys.exit(1)
except SrosMgmtError as sros_mgmt_error:
    print("SR OS Management Error:", sros_mgmt_error)
    sys.exit(1)
except TypeError as type_error:
    print("Type Error:", type_error)
    sys.exit(1)
except InternalError as internal_error:
    print("Internal Error:", internal_error)
    sys.exit(1)
```
///

/// details | Script to print a table with the commit history (`show-commits.py`)
```python
from pysros.management import connect
from pysros.pprint import Table

connection = connect(host = "clab-srexperts-pe1", username = "admin", hostkey_verify = False)

path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
data = connection.running.get(path)

columns = [(4, "ID"), (25, "Time"), (15, "User"), (15, "From"), (50, "Comment")]
table = Table("Commit History", columns, width = 120, showCount = "commits")
rows = []

for id in sorted(data.keys()):
    commit = data[id]
    row = []
    row.append(id)
    row.append(commit['timestamp'])
    row.append(commit['user'])
    row.append(commit['from'])
    if 'comment' in commit:
        row.append(commit['comment'])
    else:
        row.append("")
    rows.append(row)

table.print(rows)
```
///

Terminate your interactive Python interpreter using either `quit()` or `Ctrl+D`.
To test your script, you can either run it as a script by putting the code in a file
and passing it as an argument to your Python interpreter or you can paste it into the interactive interpreter.
In this example we use the former.

/// details | Execute the script from the shell
/// tab | Command
```
python show-commits.py
```
///
/// tab | Expected output
```
❯ python show-commits.py
========================================================================================================================
Commit History
========================================================================================================================
ID   Time                      User            From            Comment
------------------------------------------------------------------------------------------------------------------------
[...]
32   2025-04-14T09:38:07.1Z    admin           172.31.255.29   Disable port 1/1/c6/1 to client01
------------------------------------------------------------------------------------------------------------------------
No. of commits: 28
========================================================================================================================
```
///
///

After verifying the script is working as expected, copy it to your node and test it.

/// details | Copy the script to the node
/// tab | Command
```
scp show-commits.py admin@clab-srexperts-pe1:cf3:/
```
///
/// tab | Expected output
```
❯ scp show-commits.py admin@clab-srexperts-pe1:cf3:/
Warning: Permanently added 'clab-srexperts-pe1' (ECDSA) to the list of known hosts.

show-commits.py                                                                            100% 2411   784.5KB/s   00:00
```
///
///

After transferring the script, log into the node and execute the script with the SR OS integrated Python interpreter by calling it with `pyexec`.

/// details | Execute the script on your node
/// tab | Command
```
pyexec show-commits.py
```
///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# pyexec show-commits.py
========================================================================================================================
Commit History
========================================================================================================================
ID   Time                      User            From            Comment
------------------------------------------------------------------------------------------------------------------------
[...]
32   2025-04-14T09:38:07.1Z    admin           172.31.255.29   Disable port 1/1/c6/1 to client01
------------------------------------------------------------------------------------------------------------------------
No. of commits: 28
========================================================================================================================
```
///
///

After verifying the script executes successfully on your node, create a persistent alias to be able to call it with the command `/show commits`, making your command available to other operators as well. To achieve this, we will make the alias part of the configuration.

/// details | Create the alias `show commits`
```
configure exclusive
configure
    python {
        python-script "commits" {
            admin-state enable
            urls ["cf3:/show-commits.py"]
            version python3
        }
    }
    system {
        management-interface {
            cli {
                md-cli {
                    environment {
                        command-alias {
                            alias "commits" {
                                admin-state enable
                                python-script "commits"
                                mount-point "/show" { }
                            }
                        }
                    }
                }
            }
        }
    }
commit comment "Create a persistent alias for my custom command."
```
///

Now your command will be available under the chosen mount point `/show` for any new MD-CLI session created going forward. Log out and in again to confirm this.

/// details | Execute the alias on your node
/// tab | Command
```
show commits
```
///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# show commits
========================================================================================================================
Commit History
========================================================================================================================
ID   Time                      User            From            Comment
------------------------------------------------------------------------------------------------------------------------
[...]
32   2025-04-14T09:38:07.1Z    admin           172.31.255.29   Disable port 1/1/c6/1 to client01
33   2025-04-14T10:15:33.3Z    admin           172.31.255.29   Create a persistent alias for my custom command.
------------------------------------------------------------------------------------------------------------------------
No. of commits: 29
========================================================================================================================
```
///
///

You can do the same thing ephemerally using the `environment` command. This has the advantage of being immediately visible and may aid with debugging, however the change will disappear as soon as your session is terminated. Try creating an alias called `commits-e` mounted on the same point with the following command:

- `environment command-alias alias commits-e python-script "commits" admin-state enable mount-point "/show"`

Now confirm both aliases work and, after renewing your session once more, only the persistent configured version remains.

### Revert your changes to the configuration

After having completed all the sections above, revert the changes you have made to the system configuration by re-enabling port 1/1/c6/1.

/// details | Re-enable port 1/1/c6/1
/// tab | Command
```
edit-config exclusive
/configure port 1/1/c6/1 admin-state enable
commit comment "Re-enable port 1/1/c6/1"
info state port 1/1/c6/1 oper-state
```
///
/// tab | Expected Output
```
[/]
A:admin@g15-pe1# edit-config exclusive
INFO: CLI #2060: Entering exclusive configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(ex)[/]
A:admin@g15-pe1# /configure port 1/1/c6/1 admin-state enable

*(ex)[/]
A:admin@g15-pe1# commit comment "Re-enable port 1/1/c6/1"

(ex)[/]
A:admin@g15-pe1# info state port 1/1/c6/1 oper-state
    oper-state up
```
///
///

### (Optional) Extend your output with additional information

Well done! At this point, you should have been able to implement a basic but useful custom command to show the commit history.
If you are feeling adventurous, the tasks in this section will guide you in expanding the information included in your script, but they require more complex programming skills.
These are completely optional, so feel free to jump ahead to the conclusion, but don't be afraid to go for them if you feel up to the challenge!

#### Relative timestamps

With the absolute timestamp value of each commit, it is possible to calculate how long ago it was, which might be convenient to include in your output.
Since this adds some complexity to the activity, it is left as an optional exercise for those familiar enough with Python.
To do this, you can use Python's [`datetime` module](https://docs.python.org/3.4/library/datetime.html) to show how much time has passed since each commit was done.

!!! warning

    While SROS supports the `datetime` module, it doesn't implement the [`srtptime` function](https://docs.python.org/3.4/library/datetime.html#strftime-and-strptime-behavior),
    which would be used in most Python environments to parse the timestamp string into a `datetime` object.
    An alternative approach compatible with SROS is to use regular expressions with the [`re` module](https://docs.python.org/3.4/library/re.html#module-re).
    Note that the implementation of `re` is also limited on SROS. More details on differences in the implementation are available [here](https://docs.micropython.org/en/latest/library/re.html).

To start, calculate the time difference for the latest commit.

/// details | Calculate the time difference for the latest commit
/// tab | Command
```python
from pysros.management import connect
from datetime import datetime, timezone
import re

connection = connect(host = "clab-srexperts-pe1", username = "admin", hostkey_verify = False)

path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
highest_commit_id = max(connection.running.get_list_keys(path))

path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id[id=%s]" % highest_commit_id
commit = connection.running.get(path)

match = re.match("^(\\d+)-(\\d+)-(\\d+)T(\\d+):(\\d+):(\\d+)\.\\dZ$", str(commit['timestamp']))
commit_year = int(match.group(1))
commit_month = int(match.group(2))
commit_day = int(match.group(3))
commit_hour = int(match.group(4))
commit_minute = int(match.group(5))
commit_second = int(match.group(6))
commit_time = datetime(commit_year, commit_month, commit_day, commit_hour, commit_minute, commit_second, tzinfo = timezone.utc)
commit_time_delta = datetime.now(timezone.utc) - commit_time
commit_time_delta_days = commit_time_delta.days
commit_time_delta_hours = commit_time_delta.seconds // 3600
commit_time_delta_minutes = (commit_time_delta.seconds % 3600) // 60
commit_time_delta_seconds = (commit_time_delta.seconds % 3600) % 60
print("{}d {}h {}m {}s ago".format(commit_time_delta_days, commit_time_delta_hours, commit_time_delta_minutes, commit_time_delta_seconds))
```
///
/// tab | Expected output
```
>>> from pysros.management import connect
>>> from datetime import datetime, timezone
>>> import re
>>>
>>> connection = connect(host = "clab-srexperts-pe1", username = "admin", hostkey_verify = False)
>>>
>>> path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
>>> highest_commit_id = max(connection.running.get_list_keys(path))
>>>
>>> path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id[id=%s]" % highest_commit_id
>>> commit = connection.running.get(path)
>>>
>>> match = re.match("^(\\d+)-(\\d+)-(\\d+)T(\\d+):(\\d+):(\\d+)\.\\dZ$", str(commit['timestamp']))
>>> commit_year = int(match.group(1))
>>> commit_month = int(match.group(2))
>>> commit_day = int(match.group(3))
>>> commit_hour = int(match.group(4))
>>> commit_minute = int(match.group(5))
>>> commit_second = int(match.group(6))
>>> commit_time = datetime(commit_year, commit_month, commit_day, commit_hour, commit_minute, commit_second, tzinfo = timezone.utc)
>>> commit_time_delta = datetime.now(timezone.utc) - commit_time
>>> commit_time_delta_days = commit_time_delta.days
>>> commit_time_delta_hours = commit_time_delta.seconds // 3600
>>> commit_time_delta_minutes = (commit_time_delta.seconds % 3600) // 60
>>> commit_time_delta_seconds = (commit_time_delta.seconds % 3600) % 60
>>> print("{}d {}h {}m {}s ago".format(commit_time_delta_days, commit_time_delta_hours, commit_time_delta_minutes, commit_time_delta_seconds))
0d 0h 16m 32s ago
```
///
///

Having implemented the calculation of the relative timestamp, integrate it into your script to replace the absolute timestamp with the relative one.

/// details | Commit table script with relative timestamps
/// tab | Command
```python
from pysros.management import connect
from pysros.pprint import Table

from datetime import datetime, timezone
import re

connection = connect(host = "clab-srexperts-pe1", username = "admin", hostkey_verify = False)

path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
data = connection.running.get(path)

columns = [(4, "ID"), (25, "Time"), (15, "User"), (15, "From"), (50, "Comment")]
table = Table("Commit History", columns, width = 120, showCount = "commits")
rows = []

for id in sorted(data.keys()):
    commit = data[id]
    row = []
    row.append(id)
    match = re.match("^(\\d+)-(\\d+)-(\\d+)T(\\d+):(\\d+):(\\d+)\.\\dZ$", str(commit['timestamp']))
    commit_year = int(match.group(1))
    commit_month = int(match.group(2))
    commit_day = int(match.group(3))
    commit_hour = int(match.group(4))
    commit_minute = int(match.group(5))
    commit_second = int(match.group(6))
    commit_time = datetime(commit_year, commit_month, commit_day, commit_hour, commit_minute, commit_second, tzinfo = timezone.utc)
    commit_time_delta = datetime.now(timezone.utc) - commit_time
    commit_time_delta_days = commit_time_delta.days
    commit_time_delta_hours = commit_time_delta.seconds // 3600
    commit_time_delta_minutes = (commit_time_delta.seconds % 3600) // 60
    commit_time_delta_seconds = (commit_time_delta.seconds % 3600) % 60
    row.append("{}d {}h {}m {}s ago".format(commit_time_delta_days, commit_time_delta_hours, commit_time_delta_minutes, commit_time_delta_seconds))
    row.append(commit['user'])
    row.append(commit['from'])
    if 'comment' in commit:
        row.append(commit['comment'])
    else:
        row.append("")
    rows.append(row)

table.print(rows)
```
///
/// tab | Expected output
```
>>> from pysros.management import connect
>>> from pysros.pprint import Table
>>>
>>> from datetime import datetime, timezone
>>> import re
>>>
>>> connection = connect(host = "clab-srexperts-pe1", username = "admin", hostkey_verify = False)
>>>
>>> path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
>>> data = connection.running.get(path)
>>>
>>> columns = [(4, "ID"), (25, "Time"), (15, "User"), (15, "From"), (50, "Comment")]
>>> table = Table("Commit History", columns, width = 120, showCount = "commits")
>>> rows = []
>>>
>>> for id in sorted(data.keys()):
...     commit = data[id]
...     row = []
...     row.append(id)
...     match = re.match("^(\\d+)-(\\d+)-(\\d+)T(\\d+):(\\d+):(\\d+)\.\\dZ$", str(commit['timestamp']))
...     commit_year = int(match.group(1))
...     commit_month = int(match.group(2))
...     commit_day = int(match.group(3))
...     commit_hour = int(match.group(4))
...     commit_minute = int(match.group(5))
...     commit_second = int(match.group(6))
...     commit_time = datetime(commit_year, commit_month, commit_day, commit_hour, commit_minute, commit_second, tzinfo = timezone.utc)
...     commit_time_delta = datetime.now(timezone.utc) - commit_time
...     commit_time_delta_days = commit_time_delta.days
...     commit_time_delta_hours = commit_time_delta.seconds // 3600
...     commit_time_delta_minutes = (commit_time_delta.seconds % 3600) // 60
...     commit_time_delta_seconds = (commit_time_delta.seconds % 3600) % 60
...     row.append("{}d {}h {}m {}s ago".format(commit_time_delta_days, commit_time_delta_hours, commit_time_delta_minutes, commit_time_delta_seconds))
...     row.append(commit['user'])
...     row.append(commit['from'])
...     if 'comment' in commit:
...         row.append(commit['comment'])
...     else:
...         row.append("")
...     rows.append(row)
...
>>> table.print(rows)
========================================================================================================================
Commit History
========================================================================================================================
ID   Time                      User            From            Comment
------------------------------------------------------------------------------------------------------------------------
[...]
32   0d 22h 46m 3s ago         admin           172.31.255.29   Disable port 1/1/c6/1 to client01
33   0d 22h 8m 37s ago         admin           172.31.255.29   Create a persistent alias for my custom command.
34   0d 21h 55m 43s ago        admin           172.31.255.29   Re-enable port 1/1/c6/1
------------------------------------------------------------------------------------------------------------------------
No. of commits: 30
========================================================================================================================
```
///
///

After checking the script is working as expected, copy the new version to the router.
The version of the script stored in the router's memory isn't updated automatically, load your changes into the router with the `/perform python python-script reload script <name>` command.

/// details | Reload the script
/// tab | Command
```
/perform python python-script reload script "commits"
```
///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# /perform python python-script reload script "commits"

[/]
A:admin@g15-pe1#
```
///
///

Finally, execute the `show commits` alias and check that the command reflects the changes you made to the script.

/// details | Execute the alias on your node
/// tab | Command
```
show commits
```
///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# show commits
========================================================================================================================
Commit History
========================================================================================================================
ID   Time                      User            From            Comment
------------------------------------------------------------------------------------------------------------------------
[...]
32   0d 22h 46m 3s ago         admin           172.31.255.29   Disable port 1/1/c6/1 to client01
33   0d 22h 8m 37s ago         admin           172.31.255.29   Create a persistent alias for my custom command.
34   0d 21h 55m 43s ago        admin           172.31.255.29   Re-enable port 1/1/c6/1
------------------------------------------------------------------------------------------------------------------------
No. of commits: 30
========================================================================================================================
```
///
///

#### Incremental saves and counting changes

Model-driven SR OS supports [incrementally saved configuration](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/model-driven-management-interfaces.html#unique_1907621511),
which saves the changes made in each commit to an unique file and periodically merges these into the complete configuration file.

Enable incremental configuration and make another change to the configuration.

/// tab | Command
```
configure system management-interface cli md-cli auto-config-save true
configure system management-interface commit-history 50
configure system management-interface configuration-save configuration-backups 50
configure system management-interface configuration-save incremental-saves true
commit comment "Enable incremental config"
```

///
/// tab | Expected output
```
(ex)[/]
A:admin@g15-pe1# configure system management-interface cli md-cli auto-config-save true

*(ex)[/]
A:admin@g15-pe1# configure system management-interface commit-history 50

*(ex)[/]
A:admin@g15-pe1# configure system management-interface configuration-save configuration-backups 50

*(ex)[/]
A:admin@g15-pe1# configure system management-interface configuration-save incremental-saves true

*(ex)[/]
A:admin@g15-pe1# commit comment "Enable incremental config"

(ex)[/]
A:admin@g15-pe1#
```
///

Check the commit history for this latest entry. Try using your `show commits` command to do this.

/// tab | Commands
```
show commits
```

///
/// tab | Expected output
```
(ex)[/]
A:admin@g15-pe1# show commits
========================================================================================================================
Commit History
========================================================================================================================
ID   Time                      User            From            Comment
------------------------------------------------------------------------------------------------------------------------
[...]
43   0d 0h 1m 10s ago          admin           172.31.255.29   Enable incremental config
------------------------------------------------------------------------------------------------------------------------
No. of commits: 43
========================================================================================================================
```
///

Now check all the details of the commit entry from the state datastore.

/// tab | Commands
```
info state system management-interface configuration-region configure commit-history commit-id <id>
```

///
/// tab | Expected output
```
(gl)[/]
A:admin@g15-pe1# info state system management-interface configuration-region configure commit-history commit-id 43
    timestamp 2025-04-29T13:00:04.6+00:00
    user "admin"
    type md-cli
    from 172.31.255.29
    location "tftp://172.31.255.29/config.txt"
    increment-location "cf3:\.commit-history\config-2025-04-29T13-00-04.6Z-43.is"
    comment "Enable incremental config"

```
///

Notice the new `increment-location` entry saved to the commit history.
This points to the location of the file containing the incremental changes made in each commit.
Check the contents of this file to see they match the latest changes you made to the configuration.

!!! warning

    Don't make any changes to the files stored in the `.commit-history` directory.

/// tab | Command
```
file show cf3:\.commit-history\config-2025-04-29T13-00-04.6Z-43.is
```

///
/// tab | Expected output
```
(gl)[/]
A:admin@g15-pe1# file show cf3:\.commit-history\config-2025-04-29T13-00-04.6Z-43.is
File: config-2025-04-29T13-00-04.6Z-43.is
-------------------------------------------------------------------------------
# TiMOS-B-25.3.R1 both/x86_64 Nokia 7750 SR Copyright (c) 2000-2025 Nokia.
# All rights reserved. All use subject to applicable license agreements.
# Built on Wed Mar 12 21:50:19 UTC 2025 by builder in /builds/253B/R1/panos/main/sros
# Configuration format version 25.3 revision 0

# Generated 2025-04-29T13:00:04.7Z by admin from 172.31.255.29
# Commit ID 43
#   Committed 2025-04-29T13:00:04.6Z by admin (MD-CLI) from 172.31.255.29
#   Comment   "Enable incremental config"

    configure {
        system {
            management-interface {
+               commit-history 50
                cli {
                    md-cli {
+                       auto-config-save true
                    }
                }
                configuration-save {
-                   configuration-backups 5
+                   configuration-backups 50
-                   incremental-saves false
+                   incremental-saves true
                }
            }
        }
    }
[...]
```
///

It might be useful to include information in your custom command about the changes made in each commit,
like the number of lines changed.
Use the [`open()` function](https://network.developer.nokia.com/static/sr/learn/pysros/latest/uio.html#uio.open)
to count the number of insertions and removals in the commit, and include this information in your table.

Note that files stored in a SR node cannot be accessed remotely using the pySROS library, so this part of the script can only be used when
being executed directly in model-driven SR OS.
You can use the [`sros()` function](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.sros)
to only include this in your output if it being executed in SR OS.

!!! tip
    Note that the `increment-location` file is not guaranteed to always be present in the filesystem.
    Make sure to handle this gracefully, e.g. with exception handling.

/// details | Getting details on incremental changes
```python
from pysros.management import connect, sros
from pysros.pprint import Table

connection = connect(host = "clab-srexperts-pe1", username = "admin", hostkey_verify = False)

path = "/nokia-state:state/system/management-interface/configuration-region[region-name=\"configure\"]/commit-history/commit-id"
data = connection.running.get(path)

columns = [(4, "ID"), (25, "Time"), (15, "User"), (15, "From"), (30, "Changes"), (50, "Comment")]
table = Table("Commit History", columns, width = 150, showCount = "commits")
rows = []

for id in sorted(data.keys()):
    commit = data[id]
    row = []
    row.append(id)
    row.append(commit['timestamp'])
    row.append(commit['user'])
    row.append(commit['from'])
    if sros():
        if 'increment-location' in commit:
            try:
                with open(str(commit['increment-location'])) as f:
                    insertions = 0
                    removals = 0
                    for line in f:
                        if line[0] == "+":
                            insertions += 1
                        elif line[0] == "-":
                            removals += 1
                    row.append("{} insertion(s), {} removal(s)".format(insertions, removals))
            except OSError:
                row.append("N/A")
        else:
            row.append("N/A")
    else:
        row.append("N/A")
    if 'comment' in commit:
        row.append(commit['comment'])
    else:
        row.append("")
    rows.append(row)

table.print(rows)
```
///

Copy the script onto your node and reload the script.

/// details | Reload the script
/// tab | Command
```
/perform python python-script reload script "commits"
```
///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# /perform python python-script reload script "commits"

[/]
A:admin@g15-pe1#
```
///
///

Finally, execute the `show commits` command to get the output with the new information.

/// details | Commit history table with change details
/// tab | Command
```
show commits
```
///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# show commits
======================================================================================================================================================
Commit History
======================================================================================================================================================
ID   Time                      User            From            Changes                        Comment
------------------------------------------------------------------------------------------------------------------------------------------------------
[...]
43   2025-04-29T13:00:04.6Z    admin           172.31.255.29   4 insertion(s), 2 removal(s)   Enable incremental config
------------------------------------------------------------------------------------------------------------------------------------------------------
No. of commits: 43
======================================================================================================================================================
```
///
///

### Conclusion and review
Congratulations! By this point you should have successfully completed the activity and implemented the custom `show` command.
With the work you have put in, you should now have a basic understanding of the following topics:

- Navigating the MD-CLI and using it to retrieve state information and change the configuration on SR OS.

- Remotely retrieving information using pySROS and printing a SR OS-like table from the Python shell.

- Creating a Python script and setting it up as a custom `show` command in SR OS.

If you also ventured into the optional, more advanced tasks, you should also have become familiar with: 

- Using the data obtained through pySROS to extend your custom command with additional information.

- Making use of incremental saves to check the changes made in each commit and using this info in your script.

Good job in completing all the tasks in this activity! With this knowledge you should be well equipped to further expand your script or develop other custom commands you might find useful.
