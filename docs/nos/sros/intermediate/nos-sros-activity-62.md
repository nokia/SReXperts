---
tags:
  - SR OS
  - pySROS
  - Python
  - MD-CLI
  - alias
---

# Script (policy) results browsing made easy


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Script (policy) results browsing made easy                                                                                                                                                                                                                                                                                                                                                                                                                        |
| **Activity ID**             | 62                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Short Description**       | Create a command that allows you to easily view the latest script results file without needing to manually browse through the file system                                                                                                                                                                                                                                                                                                                                                |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/)<br/>[Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/MD-CLI_User_Guide_25.3.R1.pdf)<br/>[pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)<br/>[Python programming language](https://www.python.org)                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Topology Nodes**          | :material-router: PE1                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/MD-CLI_User_Guide_25.3.R1.pdf)<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/System_Management_Guide_25.3.R1.pdf)<br/>[pySROS user documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)<br/>[pySROS GitHub](https://github.com/nokia/pysros)<br/>[MD-CLI and YANG path finder](https://yang.labctl.net/yang/SROS/) |

If you have ever tried to create a script that is called from an SR OS `script-policy` in one of the many applications in which that feature can be used the following may seem familiar to you. Any time you test the policy it will run and create a file in the configured `results` directory. Trying to look at that latest log file then requires several steps...

- Find the script you are interested in and find out where it puts its script results.
- Look in that location and find the latest filename
- Issue a 'file show' command that specifies the location and the name of that file.

In this activity we will create an alias that makes it easier to view the latest script log files.

## Objective

Create a new `show` command using an alias and pySROS for model-driven SR OS that gives an operator the ability to use a one-liner to bring up a given script policy's most recent output. Consider allowing the operator to provide an argument to the script so if they know the name of the script-policy already they can get straight to the results file they need. 

/// details | Example command

/// tab | Example using menu selection

```
[/]
A:admin@g15-pe1# show script-policy-results
=======================================================================================
Available script policies
=======================================================================================
ID                        Policy Name
---------------------------------------------------------------------------------------
0                         EHS-TEST1
1                         EHS-TEST2
---------------------------------------------------------------------------------------
No. of defined script policies: 2
=======================================================================================
Select the ID of the script to show its latest result: 1
>>> Showing output for script policy EHS-TEST2 from cf3:\ehs_logs\/_20250506-103033-UTC.395397.out

You have successfully run script 2


[/]
A:admin@g15-pe1#

```
///

/// tab | Example using script name argument

```
[/]
A:admin@g15-pe1# show script-policy-results EHS-TEST1
>>> Showing output for script policy EHS-TEST1 from cf3:\script_results\/_20250506-103013-UTC.103873.out

You have successfully run script 1


[/]
A:admin@g15-pe1#

```
///

/// tab | Example using script ID argument

```
[/]
A:admin@g15-pe1# show script-policy-results 1
>>> Showing output for script policy EHS-TEST2 from cf3:\ehs_logs\/_20250506-103033-UTC.395397.out

You have successfully run script 2


[/]

```
///
///

## Technology explanation

This activity primarily involves Python 3.4 coding because this is the version that MicroPython is largely based on. This, in turn, is the version of Python that is available within model-driven SR OS devices. Within this environment, several libraries have been made available to operators as we will see in the next sections.

### Python3

The Python version running on the nodes is 3.4 whereas your own machine may be using a different version. Consider this when writing your code that you specifically want to run on SR OS. For example, if you are used to using [f-strings](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals) in your work you will find that they work on your machine but when you transfer your script to the node they will fail.  

Documentation for the Python 3.4 language can be found [here](https://docs.python.org/3.4/).  

This example structures the Python code in a modular manner. Snippets of data are collected and processed within their own functions. Those functions are all then called in the `main()` function and the tables are printed after the session has been disconnected.

/// details | Interested to learn more about Python code structure?

```py
# This is an example code layout

# Import the required modules
import sys
import uos
from pysros.management import connect
from pysros.pprint import Table

# Create functions to collect the data you are interest in
def data1(c)
    # Collect and process your first data

def data2(c)
    # Collect and process your second data

# ...etc

def main():
    # Start the session
    c = connect()

    # Call your functions here and organize the flow of the script
    data1(c)
    data2(c)

    # Disconnect the session
    c.disconnect()

# Call the main function
if __name__ == '__main__':
    main()

```
///

### Establishing a pySROS connection
When developing a Python script using pySROS, a connection must always be established to the SR OS device.
This is done using the [`connect` function](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.connect),
which can be used both locally, when executing the script on SR OS, or from a remote environment.

When connecting remotely, the pySROS connection is established through NETCONF, using SSH as transport. You have to provide, at least, the hostname and username to establish the connection. In such situations the SSH key located at `~/.ssh/id_rsa` would be used to log in and the default NETCONF port 830 would be used.

/// admonition | Host key verification
    type: warning
When running remotely and because we use the SSH protocol for transport, host key verification is a topic to keep track of. Host key verification is a security feature in SSH that ensures the server you are connecting to is the same server as the one you connected to previously. When connecting to an SSH server for the first time a client has the opportunity to save that server's public key. This public key can be verified upon later connection attempts to make sure the server still presents the same public key. This feature prevents man-in-the-middle attacks.

This functionality should be enabled in production environments. For ephemeral lab networks like the one we are using today it is less crucial, and requires some additional attention to set up properly as we would need to get and store each node's public key individually. This is why you will see that the `hostkey_verify` parameter to the remote `connect` calls has been set to `False`.
///

When running locally on model-driven SR OS, all parameters passed to `connect` are ignored, and the connection is established to the local node.

/// details | Example Python code to establish a remote pySROS connection

```python
from pysros.management import connect

c = connect(host = "clab-srexperts-pe1", username = "admin", hostkey_verify = False)
```
///

/// details | Example Python code to establish a local only pySROS connection

```python
from pysros.management import connect

c = connect()
```
///


### Finding configuration info with pySROS
To find the data you are looking for, open a CLI session on your node using SSH and enter the configuration tree by typing `configure private` at the CLI. Use the `tree` command or question mark to navigate through the tree. Type `info` to see the configuration in that path. Note that you can use modifiers like `json` to make the output easy to reuse. Once you have reached the data you are interested in issue the command `pwc json-instance-path` whilst in that context to get a path you can use in your Python code.

You can also use the [MD-CLI and YANG path finder](https://yang.labctl.net/yang/SROS/) to find the information you are interested in.

/// details | Example code that collects configuration data

/// tab | Python code
In the Python example below we collect the `script-policy` objects while filtering on the results attribute so we end up with the name of the script and the directory that the results files are stored in. The end result is a dictionary object.

```python
from pysros.management import connect
from pysros.pprint import printTree # Useful for pretty printing containers

c = connect()

cfg_path = '/nokia-conf:configure/system/script-control/script-policy'

script_results = c.running.get(cfg_path, filter={"results": {}})

printTree(script_results)
```
///
/// tab | Output
```
+-- ('EHS-TEST1', 'TiMOS CLI'):
|   `-- results: cf3:\script_results\
`-- ('EHS-TEST2', 'TiMOS CLI'):
    `-- results: cf3:\ehs_logs\
```
///
///

### pySROS table output
pySROS contains a module that can help you print tables that are in the style of a standard SR OS show command.<br/>Please familiarize yourself with the [pysros.pprint.Table Documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.pprint.Table).

/// details | Example of how this module is being used in this activity

/// tab | pprint.Table example

``` py
from pysros.management import connect
from pysros.pprint import Table

def summary_table(scripts):
    """Print a table that shows the options in case no choice was found."""
    rows = sorted(scripts.values(), key=lambda item: item[0])
    cols = [(25, "ID"), (62, "Policy Name")]
    width = sum((col[0] for col in cols))
    table = Table(
        "Available script policies",
        columns=cols,
        showCount="defined script policies",
        width=width,
    )
    return table, rows

c = connect()

scripts = {'0': (0, 'EHS-TEST1', 'cf3:\\script_results\\/'),
           '1': (1, 'EHS-TEST2', 'cf3:\\ehs_logs\\/')
           }

table, rows = summary_table(scripts)
table.print(rows)

c.disconnect()

```

///
/// tab | Output

```
[/]
A:admin@g15-pe1# pyexec table_test.py
=======================================================================================
Available script policies
=======================================================================================
ID                        Policy Name
---------------------------------------------------------------------------------------
0                         EHS-TEST1
1                         EHS-TEST2
---------------------------------------------------------------------------------------
No. of defined script policies: 2
=======================================================================================


```
///
///

### UOS and UIO module
This script makes use of the [UOS module](https://network.developer.nokia.com/static/sr/learn/pysros/latest/uos.html) that allows you to remove files or list, create and remove directories on the filesystem. The [UIO module](https://network.developer.nokia.com/static/sr/learn/pysros/latest/uio.html) on the other hand provides functionality that allows interacting with operators as well as reading and writing files using the well known `open` function in Python. These modules are MicroPython's equivalents of the corresponding Python libraries, `os` and `io`, and are only available to the on-box interpreter.

/// details | `uos` example code that gets a list of all files in a particular directory

/// tab | `uos` example
```python
import uos
from pysros.management import connect

c = connect()

directory = 'cf3:\\ehs_logs\\/'

files = uos.listdir(directory)

print(files)
```
///
/// tab | Output
```
[/]
A:admin@g15-pe1# pyexec UOS_test.py
['_20250506-094738-UTC.936418.out', '_20250506-094740-UTC.606973.out', '_20250506-094947-UTC.307113.out', '_20250506-095234-UTC.948102.out', '_20250506-095234-UTC.953706.out', '_20250506-095240-UTC.047791.out', '_20250506-095240-UTC.056271.out', '_20250506-102111-UTC.671274.out', '_20250506-102121-UTC.721798.out', '_20250506-103033-UTC.395397.out']

```
///
///

For the first file in this list, the code below uses `uio` to print the first line to the terminal and subsequently empty the contents of the file.
/// details | `uio` example to print the first line of a file

/// tab | `uio` example
Note that `uio` does not need explicit importing and is included by default.
```python
import uos
from pysros.management import connect

c = connect()

directory = 'cf3:\\ehs_logs\\/'

files = uos.listdir(directory)

with open(directory + files[0], "a+") as open_file:
    print(open_file.readline())
    open_file.seek(0)
    open_file.truncate()
```
///
/// tab | Output
```
[/]
A:admin@g15-pe1# pyexec UIO_test.py
You have successfully run script 2
```
///
///


### Script policies and testing
When its time to test your code you may have already created several scripts on your devices that have result files from previous activities.  

If you haven't then you will need to create some working script-policies to test your code. Create more than one script-policy and challenge your code by having them store results files in different locations.

/// details | If you need some help please read through this example

/// details | STEP 1 - Create two rudimentary python scripts 
    type: success

Save these files either on the filesystem of your SR OS node (TFTP it on or `file edit`) or you can run it from a remote location with pyexec
/// tab | test1.py
``` py
print("You have successfully run script 1")
```
///
/// tab | test2.py
``` py
print("You have successfully run script 2")
```
///
///

/// details | STEP 2 - Create two new directories to store result files in
    type: success
```
A:admin@g15-pe1# file make-directory cf3:\ehs_logs
A:admin@g15-pe1# file make-directory cf3:\script_results
```
///

/// details | STEP 3 - Configure two python-scripts
    type: success

This needs to reference the url of the files you created in step 1  
After you have committed this configuration you can test it runs using `pyexec`

/// tab | MD-CLI configuration
```
/configure python python-script "TEST1" admin-state enable
/configure python python-script "TEST1" urls ["cf3:\test1.py"]
/configure python python-script "TEST1" version python3

/configure python python-script "TEST2" admin-state enable
/configure python python-script "TEST2" urls ["cf3:\test2.py"]
/configure python python-script "TEST2" version python3

```
///
/// tab | MD-CLI output
```
(gl)[/]
A:admin@g15-pe1# pyexec "TEST1"
You have successfully run script 1

(gl)[/]
A:admin@g15-pe1# pyexec "TEST2"
You have successfully run script 2

```
///
///

/// details | STEP 4 - Configure a script-policy
    type: success

This needs to reference the directories you created in step 2 and the python-script you created in step 3 

```
/configure system script-control script-policy "EHS-TEST1" owner "TiMOS CLI" admin-state enable
/configure system script-control script-policy "EHS-TEST1" owner "TiMOS CLI" results "cf3:\script_results\"
/configure system script-control script-policy "EHS-TEST1" owner "TiMOS CLI" python-script name "TEST1"

/configure system script-control script-policy "EHS-TEST2" owner "TiMOS CLI" admin-state enable
/configure system script-control script-policy "EHS-TEST2" owner "TiMOS CLI" results "cf3:\ehs_logs\"
/configure system script-control script-policy "EHS-TEST2" owner "TiMOS CLI" python-script name "TEST2"
```
///

/// details | STEP 5 - Configure an EHS action
    type: success

The intricacies of EHS configuration are outside the remit of this activity but if you wish to read about the EHS feature then please do so in the [System Management Guide](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/event-account-logs.html#ai9exj5x1x)  

`line 3` and `line 17` need to reference the script-policy name configured in step 4  
`line 12` and `line 26` says what text in the message of the test event we want to use to trigger this EHS

``` {linenums="1" hl_lines="3,12,17,26"}
/configure log event-handling handler "EHS-HANDLER-TEST1" admin-state enable
/configure log event-handling handler "EHS-HANDLER-TEST1" entry 1 admin-state enable
/configure log event-handling handler "EHS-HANDLER-TEST1" entry 1 script-policy name "EHS-TEST1"

/configure log event-trigger logger event tmnxTestEvent admin-state enable
/configure log event-trigger logger event tmnxTestEvent entry 10 filter "1101"
/configure log event-trigger logger event tmnxTestEvent entry 10 handler "EHS-HANDLER-TEST1"

/configure log filter "1101" named-entry "1" action forward
/configure log filter "1101" named-entry "1" match application eq logger
/configure log filter "1101" named-entry "1" match event eq 2011
/configure log filter "1101" named-entry "1" match message eq "TEST1"
/configure log filter "1101" default-action drop

/configure log event-handling handler "EHS-HANDLER-TEST2" admin-state enable
/configure log event-handling handler "EHS-HANDLER-TEST2" entry 1 admin-state enable
/configure log event-handling handler "EHS-HANDLER-TEST2" entry 1 script-policy name "EHS-TEST2"

/configure log event-trigger logger event tmnxTestEvent admin-state enable
/configure log event-trigger logger event tmnxTestEvent entry 20 filter "1102"
/configure log event-trigger logger event tmnxTestEvent entry 20 handler "EHS-HANDLER-TEST2"

/configure log filter "1102" named-entry "1" action forward
/configure log filter "1102" named-entry "1" match application eq logger
/configure log filter "1102" named-entry "1" match event eq 2011
/configure log filter "1102" named-entry "1" match message eq "TEST2"
/configure log filter "1102" default-action drop

```
///

/// details | STEP 6 - Trigger both EHS
    type: success

/// tab | Trigger both EHS with the test event
```
[/]
A:admin@g15-pe1# tools perform log test-event custom-text TEST1

[/]
A:admin@g15-pe1# tools perform log test-event custom-text TEST2

```
///
/// tab | Logs 99 should show EHS has run
```
(gl)[/]
A:admin@g15-pe1# show log log-id 99 ascending

33723 2025/05/14 08:58:48.949 UTC INDETERMINATE: LOGGER #2011 Base Event Test
"TEST1"

33724 2025/05/14 08:58:48.950 UTC MINOR: SYSTEM #2069 Base EHS script
"Ehs handler :"EHS-HANDLER-TEST1" with the description : "" was invoked by the cli-user account "not-specified"."

33725 2025/05/14 08:58:58.667 UTC INDETERMINATE: LOGGER #2011 Base Event Test
"TEST2"

33726 2025/05/14 08:58:58.667 UTC MINOR: SYSTEM #2069 Base EHS script
"Ehs handler :"EHS-HANDLER-TEST2" with the description : "" was invoked by the cli-user account "not-specified"."
```
///
/// tab | You should now have result files in your directories
```
(gl)[/]
A:admin@g15-pe1# file list script_results/

Volume in drive cf3 on slot A is SROS VM.

Volume in drive cf3 on slot A is formatted as FAT32

Directory of cf3:\script_results\

05/14/2025  12:07a      <DIR>          ./
05/14/2025  12:07a      <DIR>          ../
05/14/2025  08:58a                  35 _20250514-085848-UTC.952125.out
               1 File(s)                     35 bytes.
               2 Dir(s)               753885184 bytes free.

```
///

///

///




### MD-CLI alias command
After you have created your python script you can execute it directly with the `pyexec` command. That is fine for you as you are the one that has created the script and knows the name of it and where you stored it!

For the benefit of operators it would make sense to wrap your python file into a MD-CLI alias so that operators can use a simple command to execute it without having to know what the file is called and where it is.

/// admonition
    type: tip
When you first create your MD-CLI alias you must logout and log back in before you can see it working
///

/// admonition
    type: tip
If you have created your alias, but then you change the contents of your python file afterwards you must use the command `perform python python-script reload script "self_test"` to get the python script to read the new python file. You can use the command `show python python-script self_test source-in-use` to see the contents of the python file the python script has currently loaded.
///

/// details | Example before and after outputs

/// tab | MD-CLI before
``` {hl_lines="2"}
(gl)[/]
A:admin@g15-pe1# pyexec "cf3:\nos-sros-activity-62.py"
=======================================================================================
Available script policies
=======================================================================================
ID                        Policy Name
---------------------------------------------------------------------------------------
0                         EHS-TEST1
1                         EHS-TEST2
---------------------------------------------------------------------------------------
No. of defined script policies: 2
=======================================================================================
Select the ID of the script to show its latest result:
```
///
/// tab | MD-CLI after
``` {hl_lines="2"}
(gl)[/]
A:admin@g15-pe1# show script-policy-results
=======================================================================================
Available script policies
=======================================================================================
ID                        Policy Name
---------------------------------------------------------------------------------------
0                         EHS-TEST1
1                         EHS-TEST2
---------------------------------------------------------------------------------------
No. of defined script policies: 2
=======================================================================================
Select the ID of the script to show its latest result:
```
///
///

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Setup your environment and the start of your script
The first step in this activity is setting up the environment to develop your script.
This can either be done with a remote pySROS connection, through the interactive Python interpreter,
or by editing the script and executing it locally in model-driven SR OS using `pyexec`.

/// tip | Script location
You can develop the script under your VM Instance folder `~/clab-srexperts/pe1/tftpboot/`. This folder's contents are accessible from PE1 via `tftp://172.31.255.29/`.

For example, if you create a script in `~/clab-srexperts/pe1/tftpboot/script.py`, you can run it on PE1 using `pyexec tftp://172.31.255.29/script.py`.
///

To begin, create some code that imports the required modules and has the table function discussed in section [pySROS table output](#pysros-table-output)

/// note
- All of the code provided below are examples. Feel free to code your own way in your own style to achieve a similar outcome.
- Before looking straight at the code provided, try to think how you would do it.
- Feel free to test as you go along and use tools like a Python interpreter to check everything is working before moving on.
- Be conscious that the full script might fail until all modules and logic control are in place.
///

/// details | Example start code
    type: success

```py
"""
This module contains code designed to run in the on-board interpreter of a
model-driven SR OS node to quickly display text file contents related to
the latest execution of a script policy.

This iteration has some features built in to improve user friendliness.
"""
import sys
import uos
from pysros.management import connect
from pysros.pprint import Table


def summary_table(scripts):
    """Print a table that shows the options in case no choice was found."""
    rows = sorted(scripts.values(), key=lambda item: item[0])
    cols = [(25, "ID"), (62, "Policy Name")]
    width = sum((col[0] for col in cols))
    table = Table(
        "Available script policies",
        columns=cols,
        showCount="defined script policies",
        width=width,
    )
    return table, rows
```
///


### Create a function for script config collection

Create a function that takes a connection object and returns a dictionary containing the name of the script file and the directory it uses to store its result files. Add an index number to each script-policy and use those as keys. It may be convenient later on when building the table output to include those index numbers in the tuples that represent the dictionary values

/// details | Example function for getting the script results location
    type: success
/// tab | Function code
```py
def get_script_results_location(c):
    """Get the existing script-policies and corresponding results location
    with a selection node filter."""
    cfg_path = "/nokia-conf:configure/system/script-control/script-policy"
    ehs_results = c.running.get(cfg_path, filter={"results": {}})
    result = {}
    index = 0
    for k, v in ehs_results.items():
        if str(v["results"]) == "/null":
            continue
        path = str(v["results"]).rsplit("/", 1)[0] + "/"
        result[str(index)] = (index, k[0], path)
        index += 1
    return result
```
///
/// tab | Example return value
```
{'0': (0, 'EHS-TEST1', 'cf3:\\script_results\\/'), '1': (1, 'EHS-TEST2', 'cf3:\\ehs_logs\\/')}
```
///
///

### Create the `main()` function and start the flow process


Create the `main()` function that starts with collecting any arguments the user has passed to the script. After that, run the function created in the previous section to collect details on the scripts configured on this device. If the user hasn't provided any arguments then print the table and prompt the user to select an ID of the script policy they would like to see.

/// admonition | Stop and take time to think here
    type: question
- What arguments would you find useful to pass to the script to get straight to the script-policy you are interested in?
- Would the script-policy name be a candidate?
- What could be a quicker argument if you needed to view results over and over again?
///

/// details | Example start of the `main()` function the deals with any script arguments
    type: success

```py
def main():
    """Main function, controlling flow of this script."""
    c = connect()

    input_id = -1
    input_name = None
    try:
        input_id = str(int(sys.argv[1]))
    except IndexError as _:
        # no input specified, no problem.
        pass
    except ValueError as _:
        # might be a script policy name
        input_name = sys.argv[1]

    found_scripts = get_script_results_location(c)

    if input_id == -1 and input_name is None:
        table, rows = summary_table(found_scripts)
        table.print(rows)
        input_id = input("Select the ID of the script to show its latest result: ")
```
///

### Create logic for handling a script name argument

We want to allow the user to pass the script name directly as an argument if they already know the name of the script they are interested in. This then skips the need for a menu and immediately prints the latest result file. Create some code in `main()` that allows for this and make sure you catch whether the user has provided the correct name of a script and deal with it accordingly if they haven't.

/// details | Example argument logic of `main()` function
    type: success

```py
    if input_id == -1:
        entry_found_by_name = [
            entry[0] for entry in found_scripts.values() if entry[1] == input_name
        ]
        if entry_found_by_name:
            input_id = str(entry_found_by_name[0])
        else:
            input_id = input_name

    while not input_id in found_scripts:
        table, rows = summary_table(found_scripts)
        table.print(rows)
        input_id = input(
            "The chosen ID '%s' was not found, please input an ID from the table above or 'quit': "
            % input_id
        )
        if input_id == "quit":
            return
```
///

### Find the results file and print it

We should now be at the stage where we know the ID of the script the user is interested in. We need to create some code in `main()` that looks in that directory, finds the latest file and prints it.

Use the [uos module](#uos-and-uio-module) to list the files.

/// details | Example code for in `main()` for printing the file
    type: success

```py
    results_file_location = found_scripts[input_id][2]
    files = [""]
    try:
        files = uos.listdir(results_file_location)
        if not files:
            print("Directory %s contains no files." % results_file_location)
            return
        with open(results_file_location + files[-1], "r+") as f:
            print(
                ">>> Showing output for script policy %s from %s\n"
                % (found_scripts[input_id][1], results_file_location + files[-1])
            )
            print(f.read())
    except ValueError as _:
        print("Couldn't find the file at %s" % (results_file_location + files[-1]))
```
///

### Call the main() function and test

Finally call the `main()` function:

/// details | In our example code we just finally need to call `main()`
    type: success

```py
if __name__ == "__main__":
    main()
```
///

The final script is included in its entirety below.


/// details | Final example script
    type: success

```py
"""
This module contains code designed to run in the on-board interpreter of a
model-driven SR OS node to quickly display text file contents related to
the latest execution of a script policy.

This iteration has some features built in to improve user friendliness.
"""
import sys
import uos
from pysros.management import connect
from pysros.pprint import Table


def summary_table(scripts):
    """Print a table that shows the options in case no choice was found."""
    rows = sorted(scripts.values(), key=lambda item: item[0])
    cols = [(25, "ID"), (62, "Policy Name")]
    width = sum((col[0] for col in cols))
    table = Table(
        "Available script policies",
        columns=cols,
        showCount="defined script policies",
        width=width,
    )
    return table, rows


def get_script_results_location(c):
    """Get the existing script-policies and corresponding results location
    with a selection node filter."""
    cfg_path = "/nokia-conf:configure/system/script-control/script-policy"
    ehs_results = c.running.get(cfg_path, filter={"results": {}})
    result = {}
    index = 0
    for k, v in ehs_results.items():
        if str(v["results"]) == "/null":
            continue
        path = str(v["results"]).rsplit("/", 1)[0] + "/"
        result[str(index)] = (index, k[0], path)
        index += 1
    return result


def main():
    """Main function, controlling flow of this script."""
    c = connect()

    input_id = -1
    input_name = None
    try:
        input_id = str(int(sys.argv[1]))
    except IndexError as _:
        # no input specified, no problem.
        pass
    except ValueError as _:
        # might be a script policy name
        input_name = sys.argv[1]

    found_scripts = get_script_results_location(c)

    if input_id == -1 and input_name is None:
        table, rows = summary_table(found_scripts)
        table.print(rows)
        input_id = input("Select the ID of the script to show its latest result: ")

    if input_id == -1:
        entry_found_by_name = [
            entry[0] for entry in found_scripts.values() if entry[1] == input_name
        ]
        if entry_found_by_name:
            input_id = str(entry_found_by_name[0])
        else:
            input_id = input_name

    while not input_id in found_scripts:
        table, rows = summary_table(found_scripts)
        table.print(rows)
        input_id = input(
            "The chosen ID '%s' was not found, please input an ID from the table above or 'quit': "
            % input_id
        )
        if input_id == "quit":
            return

    results_file_location = found_scripts[input_id][2]
    files = [""]
    try:
        files = uos.listdir(results_file_location)
        if not files:
            print("Directory %s contains no files." % results_file_location)
            return
        with open(results_file_location + files[-1], "r+") as f:
            print(
                ">>> Showing output for script policy %s from %s\n"
                % (found_scripts[input_id][1], results_file_location + files[-1])
            )
            print(f.read())
    except ValueError as _:
        print("Couldn't find the file at %s" % (results_file_location + files[-1]))


if __name__ == "__main__":
    main()

```
///

If you already have some scripts with results files you can start testing straight away. Or you can use the EHS example code in [Script policies and testing](#script-policies-and-testing) to create some example scripts and files.

If all has gone well this activity is complete and you now have an easy way of viewing the latest results file for a script policy. Some details you may want to check:

- The script needs to handle script policies that store their results files in different locations.
- The script needs to handle if there are no results files in the directory.
- The script needs to handle if the user has made a mistake in the argument they have passed to the script.
- The script needs to always choose the last results file that is available.

### Create a MD-CLI alias

Refer to section [MD-CLI alias command](#md-cli-alias-command) as a reference

/// details | Example MD-CLI alias configuration
    type: success
/// admonition
    type: note
Alter the url of the script below to reflect the location and name of the script you have made
///
/// tab | MD-CLI alias configuration
```
/configure python python-script "script-policy-results" admin-state enable
/configure python python-script "script-policy-results" urls ["cf3:\nos-sros-activity-62.py"]
/configure python python-script "script-policy-results" version python3
/configure system management-interface cli md-cli environment command-alias alias "script-policy-results" admin-state enable
/configure system management-interface cli md-cli environment command-alias alias "script-policy-results" description "show script-policy-results"
/configure system management-interface cli md-cli environment command-alias alias "script-policy-results" python-script "script-policy-results"
/configure { system management-interface cli md-cli environment command-alias alias "script-policy-results" mount-point "/show" }
```
///
/// tab | MD-CLI output
``` {hl_lines="2"}
(gl)[/]
A:admin@g15-pe1# show script-policy-results
=======================================================================================
Available script policies
=======================================================================================
ID                        Policy Name
---------------------------------------------------------------------------------------
0                         EHS-TEST1
1                         EHS-TEST2
---------------------------------------------------------------------------------------
No. of defined script policies: 2
=======================================================================================
Select the ID of the script to show its latest result:
```
///
///

## Summary and review

Congratulations!  If you have got this far you have completed this activity and achieved the following:

- You have used a pySROS either remotely or via the on-board interpreter to connect with model-driven SR OS
- You have learned about MicroPython and some of its differences compared to regular Python
- You have written or modified one or more applications using the Python 3 programming language
- You have used the model-driven CLI for changing configuration in SR OS
- You have created an alias that makes life simpler for anyone looking through `script-policy` outputs

This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity. Several activities refer back to this one as they use script policies. You may be interested in trying those while using your own version instead of the provided one.
