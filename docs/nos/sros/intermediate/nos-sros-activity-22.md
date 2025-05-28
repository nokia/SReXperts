---
tags:
  - SR OS
  - pySROS
  - Python
  - MD-CLI
  - alias
---

# Sanity check MD-CLI show command


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Sanity check MD-CLI show command                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Activity ID**             | 22                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Short Description**       | Create a single show command for operators to quickly see personalized health data for a node                                                                                                                                                                                                                                                                                                                                                 |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/)<br/>[Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/MD-CLI_User_Guide_25.3.R1.pdf)<br/>[pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)<br/>[Python programming language](https://www.python.org)                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| **Topology Nodes**          | :material-router: PE1 :material-router: PE2 :material-router: PE3 :material-router: PE4                                                                                                                                                                                                                                                                                                                                                                                                                    |
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/MD-CLI_User_Guide_25.3.R1.pdf)<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/System_Management_Guide_25.3.R1.pdf)<br/>[pySROS user documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)<br/>[pySROS GitHub](https://github.com/nokia/pysros)<br/>[MD-CLI and YANG path finder](https://yang.labctl.net/yang/SROS/) |


Engineers that work on network issues often need a quick way of viewing the health of a node. An engineer will have to remember and run multiple show commands to look at different health metrics and the company will be reliant on each engineer to know what to look for, how to look for it and how to interpret it.  

## Objective

Create a single show command that runs a sanity check so that engineers can use a single command to view all the health metrics that are important to this node. If any of the checks fail provide an output to show what fails. Be as creative as you like here and select outputs that you think are important. As a minimum have your show command check the status of:

- The Card status 
- The IS-IS adjacencies
- The BGP peerings
- The CPU utilization
- The Memory utilization

/// details | Example output with all tests passing

```
(gl)[/]
A:admin@g15-pe1# show self_test
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
ISIS STATUS                                                  PASS
BGP STATUS                                                   PASS
BUSIEST CPU CORE OVER 5MIN                                   4%
MEMORY UTILIZATION                                           53%
===============================================================================
```
///

/// details | Example output with a failed test

```
(gl)[/]
A:admin@g15-pe1# show self_test
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
ISIS STATUS                                                  PASS
BGP STATUS                                                   FAIL
BUSIEST CPU CORE OVER 5MIN                                   5%
MEMORY UTILIZATION                                           53%
===============================================================================


===============================================================================
Details Of Failed Tests
===============================================================================
Failures
-------------------------------------------------------------------------------
The BGP peer 10.64.51.2 is not Established
===============================================================================
```
///

Optionally also include the following:

- The MDA status
- The MPLS tunnel status
- The Service status
- Basic ping tests
- CF3 utilization
- Fan speed

/// details | Example output with all tests passing

```
(gl)[/]
A:admin@g15-pe1# show self_test
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
MDA STATUS                                                   PASS
ISIS STATUS                                                  PASS
MPLS STATUS                                                  PASS
BGP STATUS                                                   PASS
SERVICE STATUS                                               PASS
PING TESTS                                                   PASS
BUSIEST CPU CORE OVER 5MIN                                   5%
MEMORY UTILIZATION                                           53%
CF3 UTILIZATION                                              39%
FAN TRAY 1 SPEED                                             0%
FAN TRAY 2 SPEED                                             0%
FAN TRAY 3 SPEED                                             0%
FAN TRAY 4 SPEED                                             0%
===============================================================================

```
///

/// details | Example with a failed test

```
(gl)[/]
A:admin@g15-pe1# show self_test
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
MDA STATUS                                                   PASS
ISIS STATUS                                                  PASS
MPLS STATUS                                                  PASS
BGP STATUS                                                   FAIL
SERVICE STATUS                                               FAIL
PING TESTS                                                   PASS
BUSIEST CPU CORE OVER 5MIN                                   5%
MEMORY UTILIZATION                                           53%
CF3 UTILIZATION                                              39%
FAN TRAY 1 SPEED                                             0%
FAN TRAY 2 SPEED                                             0%
FAN TRAY 3 SPEED                                             0%
FAN TRAY 4 SPEED                                             0%
===============================================================================


===============================================================================
Details Of Failed Tests
===============================================================================
Failures
-------------------------------------------------------------------------------
The BGP peer 10.64.54.0 is not Established
The IES service client01 is not up
===============================================================================

```
///

As a stretch goal to take it to the next level consider:

- Having an output that shows non-zero network QoS drops
- Having an output that shows non-zero port errors
- Either (or both) of the above with an optional time interval that collects two iterations of data so you can provide a delta between them

/// details | Example output without setting an iteration interval

```
(gl)[/]
A:admin@g15-pe1# show self_test
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
MDA STATUS                                                   PASS
ISIS STATUS                                                  PASS
BGP STATUS                                                   PASS
MPLS STATUS                                                  PASS
SERVICE STATUS                                               PASS
PING TESTS                                                   FAIL
BUSIEST CPU CORE OVER 5MIN                                   6%
MEMORY UTILIZATION                                           53%
CF3 UTILIZATION                                              39%
FAN TRAY 1 SPEED                                             0%
FAN TRAY 2 SPEED                                             0%
FAN TRAY 3 SPEED                                             0%
FAN TRAY 4 SPEED                                             0%
===============================================================================


===============================================================================
Details Of Failed Tests
===============================================================================
Failures
-------------------------------------------------------------------------------
Ping to 10.46.15.22 saw packet loss
Ping to 10.46.15.23 saw packet loss
Ping to 10.46.15.24 saw packet loss
===============================================================================


===============================================================================
Any non-zero network QoS drops
===============================================================================
Port            Q          I/E        Profile    Drops
-------------------------------------------------------------------------------
1/1/c1/1        1          E          in         37
===============================================================================


===============================================================================
Any non-zero port errors
===============================================================================
Port            I/E        Drops
-------------------------------------------------------------------------------
===============================================================================
```
///

/// details | Example output with a 30s iteration interval

```
(gl)[/]
A:admin@g15-pe1# show self_test 30
Collecting second iteration in 30 seconds. Please wait
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
MDA STATUS                                                   PASS
ISIS STATUS                                                  FAIL
BGP STATUS                                                   PASS
MPLS STATUS                                                  FAIL
SERVICE STATUS                                               PASS
PING TESTS                                                   PASS
BUSIEST CPU CORE OVER 5MIN                                   6%
MEMORY UTILIZATION                                           53%
CF3 UTILIZATION                                              39%
FAN TRAY 1 SPEED                                             0%
FAN TRAY 2 SPEED                                             0%
FAN TRAY 3 SPEED                                             0%
FAN TRAY 4 SPEED                                             0%
===============================================================================


===============================================================================
Details Of Failed Tests
===============================================================================
Failures
-------------------------------------------------------------------------------
The ISIS adjacency on interface p1 is not up
The ISIS SR-LFA coverage is not 100%
===============================================================================


===============================================================================
Any incrementing network QoS drops over 30 seconds
===============================================================================
Port            Q          I/E        Profile    Drops
-------------------------------------------------------------------------------
1/1/c1/1        1          E          in         4
===============================================================================


===============================================================================
Any incrementing port errors over 30 seconds
===============================================================================
Port            I/E        Drops
-------------------------------------------------------------------------------
===============================================================================
```
///

## Technology explanation

This activity primarily involves Python 3.4 coding because this is the version that MicroPython is largely based on. This, in turn, is the version of Python that is available within model-driven SR OS devices. Within this environment, several libraries have been made available to operators as we will see in the next sections.

### Python3

The Python version running on the nodes is 3.4 whereas your own machine may be using a different version. Consider this when writing your code that you specifically want to run on SR OS. For example, if you are used to using [f-strings](https://docs.python.org/3/tutorial/inputoutput.html#formatted-string-literals) in your work you will find that they work on your machine but when you transfer your script to the node they will fail.  

Documentation for the Python 3.4 language can be found [here](https://docs.python.org/3.4/).  

This example structures the Python code in a modular manner. Snippets of data are collected and processed within their own functions. Those functions are all then called in the main() function and the tables are printed after the session has been disconnected.

/// details | Interested to learn more about Python code structure?
```py
# This is an example code layout

# Import the required modules
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

    # Call all your functions here and collate them into data for the tables
    data1(c)
    data2(c)

    # Disconnect the session
    c.disconnect()

    # Print the tables here with the data you have collected

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


### Finding state info with pySROS
To find the data you are looking for, login to your node and enter the state tree by typing `/state` at the CLI. Use the `tree` command or question mark to navigate your way around. Type `info` to see the data in that path. Once you have found the final path of data you are interested in issue the command `pwc json-instance-path` whilst in that context to get a path string you can use in your Python code.  
  
You can also use the [MD-CLI and YANG path finder](https://yang.labctl.net/yang/SROS/) to find the information you are interested in.

/// details | Example MD-CLI output
```
[/]
A:admin@g15-pe1# state router bgp neighbor "10.64.51.2" statistics

[/state router "Base" bgp neighbor "10.64.51.2" statistics]
A:admin@g15-pe1# pwc json-instance-path
Present Working Context:
/nokia-state:state/router[router-name="Base"]/bgp/neighbor[ip-address="10.64.51.2"]/statistics
```
///

/// admonition
    type: tip
When a path contains double quotes like this one, if you want to use it in your python code you will need to use single quotes to declare it as a variable

/// tab | json-instance-path

```
/nokia-state:state/router[router-name="Base"]/bgp/neighbor[ip-address="10.64.51.2"]/statistics
```

///
/// tab | The same json-instance-path as a python string variable

``` py
my_path = '/nokia-state:state/router[router-name="Base"]/bgp/neighbor[ip-address="10.64.51.2"]/statistics'
```

///
///

### pySROS get_list_keys
The [get_list_keys](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.get_list_keys) method added in pySROS version 22 will be used in these examples to get the lists of objects like interfaces, BGP peers and ports. This then allows you to collect a specific piece of information from each of these entities. Without using this method the alternative would be to collect all data from all the entities. As an example if you did this on ports, each port has thousands of data points associated with it, if your device has lots of ports you may find that your python script fails as it runs out of memory.

/// details | Example `get_list_keys` script
/// tab | get_list_keys example test.py

``` py
from pysros.management import connect

c = connect()

output = c.running.get_list_keys("/nokia-state:state/port")

c.disconnect()

print(output)
print("The data type of output is {}".format(type(output)))
```

///
/// tab | output

```
[/]
A:admin@g15-pe1# pyexec test.py
['1/1/c1', '1/1/c1/1', '1/1/c2', '1/1/c2/1', '1/1/c3', '1/1/c3/1', '1/1/c4', '1/1/c4/1', '1/1/c5', '1/1/c5/1', '1/1/c6', '1/1/c6/1', '1/1/c7', '1/1/c8', '1/1/c9', '1/1/c10', '1/1/c11', '1/1/c12', 'A/1', 'A/3', 'A/4']
The data type of output is <class 'list'>

```
///
///

### pySROS table output
pySROS contains a module that can help you print tables that are in the style of a standard SR OS show command. Please familiarize yourself with this module here [pysros.pprint.Table documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.pprint.Table).  


/// admonition
    type: tip
Make all your column widths add up to 79
///

/// details | Example `pprint.Table` script
/// tab | pprint.Table example table_test.py

``` py
from pysros.management import connect
from pysros.pprint import Table

def print_table(rows, cols, title):
    """
    This function uses the Table class from the pysros.pprint module to print a table
    in the style of the Nokia SROS CLI.
    It takes a list of lists as the rows.
    It takes a list of tuples which are the column names and their width.
    It takes a title string which is printed out at the top of the table.
    """
    # Initialize the Table object with the heading and columns.
    table = Table(title, cols)
    table.print(rows) # Print the table

c = connect()

# Just an example of how to collate the data, not real data.
list_of_lists = [
    ["port1", "UP"],
    ["port2", "UP"],
    ["port3", "UP"],
    ["port4", "DOWN"],
    ["port5", "UP"]
]

c.disconnect()

print_table(list_of_lists, [(50, "Ports"), (29, "Status")], "Port Status")
```

///
/// tab | output

```
[/]
A:admin@g15-pe1# pyexec table_test.py
===============================================================================
Port Status
===============================================================================
Ports                                              Status
-------------------------------------------------------------------------------
port1                                              UP
port2                                              UP
port3                                              UP
port4                                              DOWN
port5                                              UP
===============================================================================


```
///
///

### MD-CLI alias command
After you have created your python script you can execute it directly with the `pyexec` command. That is fine for you as you are the one that has created the script and knows the name of it and where you stored it!

For the benefit of operators it would make sense to wrap your python file into a MD-CLI alias so that operators can use a simple command to execute it without having to know what the file is called and where it is.

/// admonition
    type: tip
When you first create your MD-CLI alias you must logout and log back in before you can view it working
///

/// admonition
    type: tip
If you have created your alias, but then you change the contents of your python file afterwards you must use the command `perform python python-script reload script "self_test"` to get the python script to read the new python file. You can use the command `show python python-script self_test source-in-use` to see the contents of the python file the python script has currently loaded.
///

/// details | Example before and after outputs
    type: tip
/// tab | MD-CLI before
``` {hl_lines="2"}
(gl)[/]
A:admin@g15-pe1# pyexec "cf3:\nos-sros-activity-22.py"
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
ISIS STATUS                                                  PASS
BGP STATUS                                                   PASS
BUSIEST CPU CORE OVER 5MIN                                   4%
MEMORY UTILIZATION                                           53%
===============================================================================
```
///
/// tab | MD-CLI after
``` {hl_lines="2"}
(gl)[/]
A:admin@g15-pe1# show self_test
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
ISIS STATUS                                                  PASS
BGP STATUS                                                   PASS
BUSIEST CPU CORE OVER 5MIN                                   4%
MEMORY UTILIZATION                                           53%
===============================================================================
```
///
///

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Start your script file
The first step in this activity is setting up the environment to develop your script.
This can either be done with a remote pySROS connection, through the interactive Python interpreter,
or by editing the script and executing it locally in SROS using `pyexec`.

Refer to the [Establishing a PySROS connection](#establishing-a-pysros-connection) section for more help

/// tip | Script location
You can develop the script under your VM Instance folder `~/clab-srexperts/pe1/tftpboot/`.  This folder contents are accessible from PE1 node via `tftp://172.31.255.29/`.  
For instance, if you create a script in `~/clab-srexperts/pe1/tftpboot/hc.py`, you can run it on PE1 using `pyexec tftp://172.31.255.29/hc.py`.
///

In a file editor of your choice create a python script with the code layout discussed in the technology section with the print_table function.

/// details | Start code (read only if you get stuck)
    type: success
```py
#!/usr/bin/env python3

# Import the required modules
from pysros.management import connect
from pysros.pprint import Table   

# Our function from earlier that helps us print pretty show commands
def print_table(rows, cols, title):
    """
    This function uses the Table class from the pysros.pprint module to print a table
    in the style of the Nokia SROS CLI.
    It takes a list of lists as the rows.
    It takes a list of tuples which are the column names and their width.
    It takes a title string which is printed out at the top of the table.
    """
    # Initialize the Table object with the heading and columns.
    table = Table(title, cols)
    table.print(rows) # Print the table

# This is where we will place the functions we create to collect and process each set of data

def main():
    # Start the session
    c = connect()

    # Call all your functions here and collate them into data for the tables

    # Disconnect the session
    c.disconnect()

    # Print the tables here with the data you have collected

# Call the main function
if __name__ == '__main__':
    main()

```
///

### Get card status
/// admonition | Stop and take time to think here
    type: question
This first function you create will be similar to many of the others so it makes sense to take your time and think here how would you implement this function?

- You need a function that gathers the state of the card. Can you login to MD-CLI and go into the state tree and find a good state to gather information on?
- How will you implement a function that uses get_list_keys so we don't gather information we don't need?
- You want a function that will return a value that either passes all the tests or provides details of any failed tests. How will you do that?
///

Create a function that will check the operational state of all the provisioned cards in the chassis. Return a result that can signify whether all the cards are correctly operational. If a card isn't operational return a result that provides detail on what is wrong so it can be used in another table that highlights any failed tests.

/// details | Card status (read only if you get stuck)
    type: success
/// tab | New function
```py
def card(c):
    """
    This function first uses the get_list_keys method to get a list of all the cards in the system.
    It then iterates through the list of cards and checks the operational state of each card.
    If the operational state is not 'in-service', it adds a failure string message within a list
    to the result list. (list of lists). The function returns the result list, which will be empty
    if all provisioned cards are operationally in-service.
    """
    top_path  = "/nokia-state:state/card"
    cards = c.running.get_list_keys(top_path)
    specific_path = '/nokia-state:state/card[slot-number="{}"]/hardware-data'
    result = []
    for card in cards:
        # Check if the card is not operationally in-service
        if c.running.get(specific_path.format(card))['oper-state'].data not in ["in-service", "empty"]:
            # If it isn't then we add to the result list to signify a failure
            result.append(["Card {} is not operationally in-service".format(card)])
    return result
```
///

/// tab | Code added to `main()`
```py
def main():
    # Start the session
    c = connect()

    # Create two lists to hold the results table data and any failure table data
    result_table_data = []
    failure_table_data = []

    # Card data
    card_result = card(c)
    if card_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["CARD STATUS", "FAIL"])
        failure_table_data.extend(card_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["CARD STATUS", "PASS"])

    # Disconnect the session
    c.disconnect()

    # Print the results table
    print_table(result_table_data, [(60, "Test"), (19, "Result")], "Self Test Results")
    
    # Print the failure table only if there are any failures
    if failure_table_data:
        print("\n")
        print_table(failure_table_data, [(79, "Failures")], "Details Of Failed Tests")
```
///
///

You should be at the stage now where you have a working script (albeit with just one test at the moment).
Put your script on CF3 of the node you are working on and execute your script with pyexec. If successful you should see a CLI output showing that the card test passes.

/// details | Full script at this point (read only if you get stuck)
    type: success
/// tab | Full script at this point
```py
#!/usr/bin/env python3

# Import the required modules
from pysros.management import connect
from pysros.pprint import Table   

# Our function from earlier that helps us print pretty show commands
def print_table(rows, cols, title):
    """
    This function uses the Table class from the pysros.pprint module to print a table
    in the style of the Nokia SROS CLI.
    It takes a list of lists as the rows.
    It takes a list of tuples which are the column names and their width.
    It takes a title string which is printed out at the top of the table.
    """
    # Initialize the Table object with the heading and columns.
    table = Table(title, cols)
    table.print(rows) # Print the table

def card(c):
    """
    This function first uses the get_list_keys method to get a list of all the cards in the system.
    It then iterates through the list of cards and checks the operational state of each card.
    If the operational state is not 'in-service', it adds a failure string message within a list
    to the result list. (list of lists). The function returns the result list, which will be empty
    if all provisioned cards are operationally in-service.
    """
    top_path  = "/nokia-state:state/card"
    cards = c.running.get_list_keys(top_path)
    specific_path = '/nokia-state:state/card[slot-number="{}"]/hardware-data'
    result = []
    for card in cards:
        # Check if the card is not operationally in-service
        if c.running.get(specific_path.format(card))['oper-state'].data not in ["in-service", "empty"]:
            # If it isn't then we add to the result list to signify a failure
            result.append(["Card {} is not operationally in-service".format(card)])
    return result

def main():
    # Start the session
    c = connect()

    # Create two lists to hold the results table data and any failure table data
    result_table_data = []
    failure_table_data = []

    # Card data
    card_result = card(c)
    if card_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["CARD STATUS", "FAIL"])
        failure_table_data.extend(card_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["CARD STATUS", "PASS"])

    # Disconnect the session
    c.disconnect()

    # Print the results table
    print_table(result_table_data, [(60, "Test"), (19, "Result")], "Self Test Results")
    
    # Print the failure table only if there are any failures
    if failure_table_data:
        print("\n")
        print_table(failure_table_data, [(79, "Failures")], "Details Of Failed Tests")

# Call the main function
if __name__ == '__main__':
    main()
```
///
/// tab | Node output
```
[/]
A:admin@g15-pe1# pyexec test1.py
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
===============================================================================

```
///
///

You could even shutdown card 1 and check that the test fails and shows some failure detail.

/// details | Shutdown card 1
/// tab | Command
```
edit-config private
configure card 1 admin-state disable
commit
```
///
/// tab | Expected output
```
[/]
A:admin@g15-pe1# edit-config private
INFO: CLI #2070: Entering private configuration mode
INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

(pr)[/]
A:admin@g15-pe1# configure card 1 admin-state disable

*(pr)[/]
A:admin@g15-pe1# commit
```
///
///

/// details | Run your script and check the card is down
```
[/]
A:admin@g15-pe1# pyexec test1.py
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  FAIL
===============================================================================


===============================================================================
Details Of Failed Tests
===============================================================================
Failures
-------------------------------------------------------------------------------
Card 1 is not operationally in-service
===============================================================================
```
///

!!! warning
    Don't forget to re-enable the card you shutdown.

### Get IS-IS status
Now go through the same process with the other data. Devise and create a function to gather IS-IS adjacency data


/// details | IS-IS status (read only if you are stuck)
    type: success
/// tab | New function
```py
def isis(c):
    """
    This function first uses the get_list_keys method to get a list of all the ISIS interfaces.
    It then iterates through the list of interfaces and checks the operational state of each
    adjacency. If the operational state is not 'up', it adds a message to the result list.
    The function returns the result list, which will be empty if all adjacencies are
    operationally up.
    """
    top_path  = '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]/interface'
    interfaces = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]'
        '/interface[interface-name="{}"]/adjacency[adjacency-index="1"]'
    )
    result = []
    for interface in interfaces:
        if interface != "system": # Skip the system interface
            # There could be a LookupError if there is no adjacency index at all
            try:
                # Check if the adjacency is not operationally up
                if c.running.get(specific_path.format(interface))['oper-state'].data != "up":
                    # If it isn't then we add to the result list to signify a failure
                    result.append(["The ISIS adjacency on interface {} is not up".format(interface)])
            except LookupError:
                result.append(["The ISIS adjacency on interface {} is not up".format(interface)])
    return result
```
///

/// tab | Code added to `main()`

/// admonition
    type: note
As we have already created the lists to collect the data for the tables in `main()` and we have already called the print_table functions as well: That code is not repeated below. This is the only new code that needs to be added to `main()`
///

```py
    # ISIS data
    isis_result = isis(c)
    if isis_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["ISIS STATUS", "FAIL"])
        failure_table_data.extend(isis_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["ISIS STATUS", "PASS"])
```
///
///

### Get BGP status
Now go through the same process for the BGP test. Devise and create a function to gather BGP peering data. 

/// details | BGP status (read only if you are stuck)
    type: success
/// tab | New function
```py
def bgp(c):
    """
    This function first uses the get_list_keys method to get a list of all the BGP peers.
    It then iterates through the list of peers and checks the operational state of each peering.
    If the operational state is not 'Established', it adds a message to the result list.
    The function returns the result list, which will be empty if all BGP peerings are Established.
    """
    top_path  = '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
    peerings = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
        '[ip-address="{}"]/statistics'
    )
    result = []
    for peer in peerings:
        # Check if the peering is not Established
        if c.running.get(specific_path.format(peer))['session-state'].data != "Established":
            # If it isn't then we add to the result list to signify a failure
            result.append(["The BGP peer {} is not Established".format(peer)])
    return result
```
///

/// tab | Code added to `main()`

/// admonition
    type: note
As we have already created the lists to collect the data for the tables in `main()` and we have already called the print_table functions as well: That code is not repeated below. This is the only new code that needs to be added to `main()`
///
```py
    # BGP data
    bgp_result = bgp(c)
    if bgp_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["BGP STATUS", "FAIL"])
        failure_table_data.extend(bgp_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["BGP STATUS", "PASS"])
```
///
///


### Get CPU utilization
/// admonition | Stop and take time to think here
    type: question
This function is a little different to the others because instead of displaying a PASS/FAIL to the user it displays an absolute value. You could - if you wish - decide you want to stay with the PASS/FAIL theme and come up with some thresholds for these values that would signify a PASS/FAIL in your view.

- How would you implement this function?
- Would you want to know the CPU sample-period over 1, 60 or 300 seconds?
- Is it right to focus on the `cpu-usage` state or `capacity-usage` state? Why?
///

Now go through the same process for the CPU data. Devise and create a function to gather CPU stats.


/// details | CPU status (read only if you are stuck)
    type: success
/// tab | New function
```py
def cpu(c):
    """
    This function collects the cpu-usage of the businest CPU core over a 5 minute period.
    The collected data is a string, so it is converted to a float and then to an int to show a whole number
    """
    path  = '/nokia-state:state/system/cpu[sample-period="300"]/summary/busiest-core-utilization'
    result = c.running.get(path)['cpu-usage'].data
    return int(float(result))
```
///

/// tab | Code added to `main()`

/// admonition
    type: note
As we have already created the lists to collect the data for the tables in `main()` and we have already called the print_table functions as well: That code is not repeated below. This is the only new code that needs to be added to `main()`
///
```py
    # CPU data
    result_table_data.append(["BUSIEST CPU CORE OVER 5MIN", "{}%".format(cpu(c))])
```
///
///


### Get memory utilization
/// admonition | Stop and take time to think here
    type: question
If you look at the state tree in MD-CLI you can see we don't get a utilization figure for memory. We just get 'current-total-size', 'total-in-use' and 'available-memory'. How would you calculate a utilization percentage from this?
///

Now go through the same process for the Memory data. Devise and create a function to gather memory stats and calculate the utilization as a percentage. You might need to use some maths in Python to come up with a percentage value!

/// details | Function code (read only if you are stuck)
    type: success
/// tab | New function
```py
def memory(c):
    """
    This function collects the memory in use and available from the system
    From this it calculates the memory utilization and formats it the same way as the CPU utilization
    """
    path = "/nokia-state:state/system/memory-pools/summary"
    result = c.running.get(path)
    total_size = result['current-total-size'].data
    available = result['available-memory'].data
    total_mem = total_size + available
    utilization = (total_size / total_mem) * 100
    pretty_utilization = "{}%".format(int(utilization))
    return pretty_utilization
```
///

/// tab | Code added to `main()`

/// admonition
    type: note
As we have already created the lists to collect the data for the tables in `main()` and we have already called the print_table functions as well: That code is not repeated below. This is the only new code that needs to be added to `main()`
///
```py
    # Memory data
    result_table_data.append(["MEMORY UTILIZATION", memory(c)])
```
///
///


### Create a MD-CLI alias

Refer to section [MD-CLI alias command](#md-cli-alias-command) as a reference

/// details | MD-CLI alias configuration (read only if you are stuck)
    type: success

/// admonition
    type: note
Alter the url of the script below to reflect the location and name of the script you have made
///

/// tab | MD-CLI alias configuration
```
/configure python python-script "self_test" admin-state enable
/configure python python-script "self_test" urls ["cf3:\nos-sros-activity-22.py"]
/configure python python-script "self_test" version python3
/configure system management-interface cli md-cli environment command-alias alias "self_test" admin-state enable
/configure system management-interface cli md-cli environment command-alias alias "self_test" description "show self_test"
/configure system management-interface cli md-cli environment command-alias alias "self_test" python-script "self_test"
/configure system { management-interface cli md-cli environment command-alias alias "self_test" mount-point "/show" }
```
///
/// tab | MD-CLI output
``` {hl_lines="2"}
(gl)[/]
A:admin@g15-pe1# show self_test
===============================================================================
Self Test Results
===============================================================================
Test                                                         Result
-------------------------------------------------------------------------------
CARD STATUS                                                  PASS
ISIS STATUS                                                  PASS
BGP STATUS                                                   PASS
BUSIEST CPU CORE OVER 5MIN                                   4%
MEMORY UTILIZATION                                           53%
===============================================================================
```
///

///

### Initial set of tasks complete
Consider testing your script at this stage if you haven't been doing it as you go along. It should be working but may just show all pass results.
You could shutdown a BGP session or an IS-IS session and check your show command now recognizes the failure. Check the failure table appears to show what failed.
If you shutdown card 1 you should now see lots of failures and multiple rows appear in the failure table.

/// details | Full script at this stage
    type: success

```py
#!/usr/bin/env python3

from pysros.management import connect
from pysros.pprint import Table


def print_table(rows, cols, title):
    """
    This function uses the Table class from the pysros.pprint module to print a table
    in the style of the Nokia SROS CLI.
    It takes a list of lists as the rows.
    It takes a list of tuples which are the column names and their width.
    It takes a title string which is printed out at the top of the table.
    """
    # Initialize the Table object with the heading and columns.
    table = Table(title, cols)
    table.print(rows) # Print the table

def card(c):
    """
    This function first uses the get_list_keys method to get a list of all the cards in the system.
    It then iterates through the list of cards and checks the operational state of each card.
    If the operational state is not 'in-service', it adds a failure string message within a list
    to the result list. (list of lists). The function returns the result list, which will be empty
    if all provisioned cards are operationally in-service.
    """
    top_path  = "/nokia-state:state/card"
    cards = c.running.get_list_keys(top_path)
    specific_path = '/nokia-state:state/card[slot-number="{}"]/hardware-data'
    result = []
    for card in cards:
        # Check if the card is not operationally in-service
        if c.running.get(specific_path.format(card))['oper-state'].data not in ["in-service", "empty"]:
            # If it isn't then we add to the result list to signify a failure
            result.append(["Card {} is not operationally in-service".format(card)])
    return result

def isis(c):
    """
    This function first uses the get_list_keys method to get a list of all the ISIS interfaces.
    It then iterates through the list of interfaces and checks the operational state of each
    adjacency. If the operational state is not 'up', it adds a message to the result list.
    The function returns the result list, which will be empty if all adjacencies are
    operationally up.
    """
    top_path  = '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]/interface'
    interfaces = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]'
        '/interface[interface-name="{}"]/adjacency[adjacency-index="1"]'
    )
    result = []
    for interface in interfaces:
        if interface != "system": # Skip the system interface
            # There could be a LookupError if there is no adjacency index at all
            try:
                # Check if the adjacency is not operationally up
                if c.running.get(specific_path.format(interface))['oper-state'].data != "up":
                    # If it isn't then we add to the result list to signify a failure
                    result.append(["The ISIS adjacency on interface {} is not up".format(interface)])
            except LookupError:
                result.append(["The ISIS adjacency on interface {} is not up".format(interface)])
    return result

def bgp(c):
    """
    This function first uses the get_list_keys method to get a list of all the BGP peers.
    It then iterates through the list of peers and checks the operational state of each peering.
    If the operational state is not 'Established', it adds a message to the result list.
    The function returns the result list, which will be empty if all BGP peerings are Established.
    """
    top_path  = '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
    peerings = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
        '[ip-address="{}"]/statistics'
    )
    result = []
    for peer in peerings:
        # Check if the peering is not Established
        if c.running.get(specific_path.format(peer))['session-state'].data != "Established":
            # If it isn't then we add to the result list to signify a failure
            result.append(["The BGP peer {} is not Established".format(peer)])
    return result

def cpu(c):
    """
    This function collects the cpu-usage of the businest CPU core over a 5 minute period.
    The collected data is a string, so it is converted to a float and then to an int to show a whole number
    """
    path  = '/nokia-state:state/system/cpu[sample-period="300"]/summary/busiest-core-utilization'
    result = c.running.get(path)['cpu-usage'].data
    return int(float(result))

def memory(c):
    """
    This function collects the memory in use and available from the system
    From this it calculates the memory utilization and formats it the same way as the CPU utilization
    """
    path = "/nokia-state:state/system/memory-pools/summary"
    result = c.running.get(path)
    total_size = result['current-total-size'].data
    available = result['available-memory'].data
    total_mem = total_size + available
    utilization = (total_size / total_mem) * 100
    pretty_utilization = "{}%".format(int(utilization))
    return pretty_utilization

def main():
    # Start the session
    c = connect()

    # Create two lists to hold the results table data and any failure table data
    result_table_data = []
    failure_table_data = []
    
    # Card data
    card_result = card(c)
    if card_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["CARD STATUS", "FAIL"])
        failure_table_data.extend(card_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["CARD STATUS", "PASS"])
    
    # ISIS data
    isis_result = isis(c)
    if isis_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["ISIS STATUS", "FAIL"])
        failure_table_data.extend(isis_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["ISIS STATUS", "PASS"])
    
    # BGP data
    bgp_result = bgp(c)
    if bgp_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["BGP STATUS", "FAIL"])
        failure_table_data.extend(bgp_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["BGP STATUS", "PASS"])
    
    # CPU data
    result_table_data.append(["BUSIEST CPU CORE OVER 5MIN", "{}%".format(cpu(c))])

    # Memory data
    result_table_data.append(["MEMORY UTILIZATION", memory(c)])
    
    # Disconnect the session
    c.disconnect()

    # Print the results table
    print_table(result_table_data, [(60, "Test"), (19, "Result")], "Self Test Results")
    
    # Print the failure table only if there are any failures
    if failure_table_data:
        print("\n")
        print_table(failure_table_data, [(79, "Failures")], "Details Of Failed Tests")

# Call the main function
if __name__ == '__main__':
    main()
```
///


## Extension tasks

### Get MDA status
Create a function that reads the status of the MDAs and add it to your show command

/// details | Testing MDAs (read only if you are stuck)
    type: success

/// tab | New function
```py
def mda(c):
    """
    This function needs to be a bit different as we have to run get_list_keys twice, once
    to get a list of cards, and again against each card to get a list of MDAs in that card.
    MDAs are also different in that this state data also shows for MDAs that are not
    provisioned so we also filter off anything that has an oper-state of 'empty'
    """
    top_path  = "/nokia-state:state/card"
    cards = c.running.get_list_keys(top_path)
    mda_path = '/nokia-state:state/card[slot-number="{}"]/mda'
    specific_path = '/nokia-state:state/card[slot-number="{}"]/mda[mda-slot="{}"]/hardware-data'
    result = []
    
    for card in cards:
        mdas = c.running.get_list_keys(mda_path.format(card))
        # Check if the card is not operationally in-service
        for mda in mdas:
            if c.running.get(
                specific_path.format(card, mda)
            )['oper-state'].data not in ["in-service", "empty"]:
                # If it isn't then we add to the result list to signify a failure
                result.append(["MDA {}/{} is not operationally in-service".format(card, mda)])
    return result
```
///
/// tab | Code added to `main()`
```py
    # MDA data
    mda_result = mda(c)
    if mda_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["MDA STATUS", "FAIL"])
        failure_table_data.extend(mda_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["MDA STATUS", "PASS"])
```
///
///

### Get MPLS status
Create a function that checks the health of MPLS tunnels and add it to your show command.

/// admonition | Stop and take time to think here
    type: question
If our nodes were using LDP or RSVP-TE then this would be an easy task similar to the previous functions as the MPLS would be stateful. But our lab is using SR-ISIS. What would you pick up on to signify that SR-ISIS tunnels are healthy?
///

/// details | Testing MPLS (read only if you are stuck)
    type: success

/// tab | New function
```py
def mpls(c):
    """
    This function checks that the SR-LFA coverage is 100% for the node-sid topology.
    """
    path = (
        '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]'
        '/sr-lfa-coverage[level-number="2"][multi-topology-id="ipv4"]'
        '[sid-type="node-sid"][protocol-version="ipv4"]'
    )
    data = c.running.get(path)['lfa-covered-percent'].data
    result = []
    if data != 100:
        # If it isn't then we add to the result list to signify a failure
        result.append(["The ISIS SR-LFA coverage is not 100%"])
    return result
```
///
/// tab | Code added to `main()`
```py
    # MPLS data
    mpls_result = mpls(c)
    if mpls_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["MPLS STATUS", "FAIL"])
        failure_table_data.extend(mpls_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["MPLS STATUS", "PASS"])
```
///
///

### Get service status
Create a function that checks that services are up. Different service types are kept in different paths. How would you write your function to handle this?

/// details | Testing services (read only if you are stuck)
    type: success

/// tab | New function
```py
def svc(c):
    """
    Different service types are in different paths, so for this function we need to check both
    separately and then combine the results into one list. For this example we are just checking
    VPLS and IES services. We also need to check that the IES service is not the internal one
    which is used for the system
    """
    top_path  = "/nokia-state:state/service/{}"
    vpls_services = c.running.get_list_keys(top_path.format("vpls"))
    ies_services = c.running.get_list_keys(top_path.format("ies"))
    specific_path = '/nokia-state:state/service/{}[service-name="{}"]'
    result = []
    for vpls in vpls_services:
        # Check if the service is not up
        if c.running.get(specific_path.format('vpls', vpls))['oper-state'].data != "up":
            # If it isn't then we add to the result list to signify a failure
            result.append(["The VPLS service {} is not up".format(vpls)])
    for ies in ies_services:
        if ies != "_tmnx_InternalIesService": # Skip the internal IES service
            # Check if the service is not up
            if c.running.get(specific_path.format('ies', ies))['oper-state'].data != "up":
                # If it isn't then we add to the result list to signify a failure
                result.append(["The IES service {} is not up".format(ies)])
    return result
```
///
/// tab | Code added to `main()`
```py
    # svc data
    svc_result = svc(c)
    if svc_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["SERVICE STATUS", "FAIL"])
        failure_table_data.extend(svc_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["SERVICE STATUS", "PASS"])
```
///
///

### Create a ping test

Create a function that runs some ping tests to different destinations in the network that checks for any packet loss. What destinations would you choose? Ping isn't listed in the `state` tree so instead we need to use the [connection.action](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Connection.action) method.

/// details | Basic ping tests (read only if you are stuck)
    type: success

/// tab | New function
```py
def ping(c):
    """
    This function takes a connection object and pings destinations of your choice.
    It uses the c.action method to ping and we extract just the packet loss from the result.
    If any packet loss is seen then we flag a failure by populating the result list and return. 
    """

    ping_path = '/nokia-oper-global:global-operations/ping'
    ping_data = {'destination': '{}',
                    'output-format': 'summary',
                    'interval': "0.01",
                    'timeout': 1}

    ping_dest  = [
                     "10.46.15.22", # PE2
                     "10.46.15.23", # PE3
                     "10.46.15.24"  # PE4
                 ]
    
    result = []

    for dest in ping_dest:
        ping_data['destination'] = dest
        the_ping = c.action(ping_path, ping_data)
        pktloss = the_ping['results']['summary']['statistics']['packets']['loss'].data
        if pktloss != '0.0':
            # If packet loss isn't 0.0 then we add to the result list to signify a failure
            result.append(["Ping to {} saw packet loss".format(dest)])
    return result
```
///
/// tab | Code added to `main()`
```py
    # ping tests
    ping_result = ping(c)
    if ping_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["PING TESTS", "FAIL"])
        failure_table_data.extend(ping_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["PING TESTS", "PASS"])
```
///
///

### Check CF3 utilization

Create a function that checks the utilization of the CF3 card. What do we need to think about here?

/// details | Check CF3 utilization (read only if you are stuck)
    type: success

/// tab | New function
```py
def cf3(c):
    """
    This function collects the utilization of the CF3 flash device on the active CPM.
    You need to find out first which CPM is active in order to do this.
    """
    active_cpm = c.running.get("/nokia-state:state/system/active-cpm-slot").data
    flash_path  = '/nokia-state:state/cpm[cpm-slot="{}"]/flash[flash-id="3"]'.format(active_cpm)
    result = c.running.get(flash_path)['percent-used'].data
    return "{}%".format(result)
```
///
/// tab | Code added to `main()`
```py
    # CF3 flash data
    result_table_data.append(["CF3 UTILIZATION", cf3(c)])
```
///
///

### Get the fan tray speeds

Create a function that checks the fan speed of the fan trays in the system. How will you make your function find the number fan trays in this particular system and adjust the result output accordingly?

/// admonition
    type: note
Virtual machines may show a fan speed of 0% as there aren't any real fan trays
///

/// details | Check fan speed (read only if you are stuck)
    type: success

/// tab | New function
```py
def fan(c):
    """
    This function first uses the get_list_keys method to get a list of all the fan trays
    It then iterates through the list of trays and gets their speed
    For each tray, the speed is added to the result list
    """
    top_path  = '/nokia-state:state/chassis[chassis-class="router"][chassis-number="1"]/fan'
    fan_trays = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/chassis[chassis-class="router"][chassis-number="1"]/fan[fan-slot="{}"]'
    )
    result = []
    for tray in fan_trays:
        speed = c.running.get(specific_path.format(tray))['speed'].data
        result.append(["FAN TRAY {} SPEED".format(tray), "{}%".format(speed)])
    return result
```
///
/// tab | Code added to `main()`
```py
    # Fan data
    # We 'extend' the result table list this time because of multiple fan trays
    result_table_data.extend(fan(c))
```
///
///

### Extension tasks complete

Now you have completed all the optional tasks. Get your script and alias updated and test it.

/// details | Full script at this stage
    type: success

```py
#!/usr/bin/env python3

# Import the required modules
from pysros.management import connect
from pysros.pprint import Table   

# Our function from earlier that helps us print pretty show commands
def print_table(rows, cols, title):
    """
    This function uses the Table class from the pysros.pprint module to print a table
    in the style of the Nokia SROS CLI.
    It takes a list of lists as the rows.
    It takes a list of tuples which are the column names and their width.
    It takes a title string which is printed out at the top of the table.
    """
    # Initialize the Table object with the heading and columns.
    table = Table(title, cols)
    table.print(rows) # Print the table

def card(c):
    """
    This function first uses the get_list_keys method to get a list of all the cards in the system.
    It then iterates through the list of cards and checks the operational state of each card.
    If the operational state is not 'in-service', it adds a failure string message within a list
    to the result list. (list of lists). The function returns the result list, which will be empty
    if all provisioned cards are operationally in-service.
    """
    top_path  = "/nokia-state:state/card"
    cards = c.running.get_list_keys(top_path)
    specific_path = '/nokia-state:state/card[slot-number="{}"]/hardware-data'
    result = []
    for card in cards:
        # Check if the card is not operationally in-service
        if c.running.get(specific_path.format(card))['oper-state'].data not in ["in-service", "empty"]:
            # If it isn't then we add to the result list to signify a failure
            result.append(["Card {} is not operationally in-service".format(card)])
    return result

def mda(c):
    """
    This function needs to be a bit different as we have to run get_list_keys twice, once
    to get a list of cards, and again against each card to get a list of MDAs in that card.
    MDAs are also different in that this state data also shows for MDAs that are not
    provisioned so we also filter off anything that has an oper-state of 'empty'
    """
    top_path  = "/nokia-state:state/card"
    cards = c.running.get_list_keys(top_path)
    mda_path = '/nokia-state:state/card[slot-number="{}"]/mda'
    specific_path = '/nokia-state:state/card[slot-number="{}"]/mda[mda-slot="{}"]/hardware-data'
    result = []
    
    for card in cards:
        mdas = c.running.get_list_keys(mda_path.format(card))
        # Check if the card is not operationally in-service
        for mda in mdas:
            if c.running.get(
                specific_path.format(card, mda)
            )['oper-state'].data not in ["in-service", "empty"]:
                # If it isn't then we add to the result list to signify a failure
                result.append(["MDA {}/{} is not operationally in-service".format(card, mda)])
    return result

def isis(c):
    """
    This function first uses the get_list_keys method to get a list of all the ISIS interfaces.
    It then iterates through the list of interfaces and checks the operational state of each
    adjacency. If the operational state is not 'up', it adds a message to the result list.
    The function returns the result list, which will be empty if all adjacencies are
    operationally up.
    """
    top_path  = '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]/interface'
    interfaces = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]'
        '/interface[interface-name="{}"]/adjacency[adjacency-index="1"]'
    )
    result = []
    for interface in interfaces:
        if interface != "system": # Skip the system interface
            # There could be a LookupError if there is no adjacency index at all
            try:
                # Check if the adjacency is not operationally up
                if c.running.get(specific_path.format(interface))['oper-state'].data != "up":
                    # If it isn't then we add to the result list to signify a failure
                    result.append(["The ISIS adjacency on interface {} is not up".format(interface)])
            except LookupError:
                result.append(["The ISIS adjacency on interface {} is not up".format(interface)])
    return result

def mpls(c):
    """
    This function checks that the SR-LFA coverage is 100% for the node-sid topology.
    """
    path = (
        '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]'
        '/sr-lfa-coverage[level-number="2"][multi-topology-id="ipv4"]'
        '[sid-type="node-sid"][protocol-version="ipv4"]'
    )
    data = c.running.get(path)['lfa-covered-percent'].data
    result = []
    if data != 100:
        # If it isn't then we add to the result list to signify a failure
        result.append(["The ISIS SR-LFA coverage is not 100%"])
    return result

def bgp(c):
    """
    This function first uses the get_list_keys method to get a list of all the BGP peers.
    It then iterates through the list of peers and checks the operational state of each peering.
    If the operational state is not 'Established', it adds a message to the result list.
    The function returns the result list, which will be empty if all BGP peerings are Established.
    """
    top_path  = '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
    peerings = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
        '[ip-address="{}"]/statistics'
    )
    result = []
    for peer in peerings:
        # Check if the peering is not Established
        if c.running.get(specific_path.format(peer))['session-state'].data != "Established":
            # If it isn't then we add to the result list to signify a failure
            result.append(["The BGP peer {} is not Established".format(peer)])
    return result

def svc(c):
    """
    Different service types are in different paths, so for this function we need to check both
    separately and then combine the results into one list. For this example we are just checking
    VPLS and IES services. We also need to check that the IES service is not the internal one
    which is used for the system
    """
    top_path  = "/nokia-state:state/service/{}"
    vpls_services = c.running.get_list_keys(top_path.format("vpls"))
    ies_services = c.running.get_list_keys(top_path.format("ies"))
    specific_path = '/nokia-state:state/service/{}[service-name="{}"]'
    result = []
    for vpls in vpls_services:
        # Check if the service is not up
        if c.running.get(specific_path.format('vpls', vpls))['oper-state'].data != "up":
            # If it isn't then we add to the result list to signify a failure
            result.append(["The VPLS service {} is not up".format(vpls)])
    for ies in ies_services:
        if ies != "_tmnx_InternalIesService": # Skip the internal IES service
            # Check if the service is not up
            if c.running.get(specific_path.format('ies', ies))['oper-state'].data != "up":
                # If it isn't then we add to the result list to signify a failure
                result.append(["The IES service {} is not up".format(ies)])
    return result

def ping(c):
    """
    This function takes a connection object and pings destinations of your choice.
    It uses the c.action method to ping and we extract just the packet loss from the result.
    If any packet loss is seen then we flag a failure by populating the result list and return. 
    """

    ping_path = '/nokia-oper-global:global-operations/ping'
    ping_data = {'destination': '{}',
                    'output-format': 'summary',
                    'interval': "0.01",
                    'timeout': 1}

    ping_dest  = [
                     "10.46.15.22", # PE2
                     "10.46.15.23", # PE3
                     "10.46.15.24"  # PE4
                 ]
    
    result = []

    for dest in ping_dest:
        ping_data['destination'] = dest
        the_ping = c.action(ping_path, ping_data)
        pktloss = the_ping['results']['summary']['statistics']['packets']['loss'].data
        if pktloss != '0.0':
            # If packet loss isn't 0.0 then we add to the result list to signify a failure
            result.append(["Ping to {} saw packet loss".format(dest)])
    return result

def cpu(c):
    """
    This function collects the cpu-usage of the businest CPU core over a 5 minute period.
    The collected data is a string, so it is converted to a float and then to an int to show a whole number
    """
    path  = '/nokia-state:state/system/cpu[sample-period="300"]/summary/busiest-core-utilization'
    result = c.running.get(path)['cpu-usage'].data
    return int(float(result))

def memory(c):
    """
    This function collects the memory in use and available from the system
    From this it calculates the memory utilization and formats it the same way as the CPU utilization
    """
    path = "/nokia-state:state/system/memory-pools/summary"
    result = c.running.get(path)
    total_size = result['current-total-size'].data
    available = result['available-memory'].data
    total_mem = total_size + available
    utilization = (total_size / total_mem) * 100
    pretty_utilization = "{}%".format(int(utilization))
    return pretty_utilization

def cf3(c):
    """
    This function collects the utilization of the CF3 flash device on the active CPM.
    You need to find out first which CPM is active in order to do this.
    """
    active_cpm = c.running.get("/nokia-state:state/system/active-cpm-slot").data
    flash_path  = '/nokia-state:state/cpm[cpm-slot="{}"]/flash[flash-id="3"]'.format(active_cpm)
    result = c.running.get(flash_path)['percent-used'].data
    return "{}%".format(result)

def fan(c):
    """
    This function first uses the get_list_keys method to get a list of all the fan trays
    It then iterates through the list of trays and gets their speed
    For each tray, the speed is added to the result list
    """
    top_path  = '/nokia-state:state/chassis[chassis-class="router"][chassis-number="1"]/fan'
    fan_trays = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/chassis[chassis-class="router"][chassis-number="1"]/fan[fan-slot="{}"]'
    )
    result = []
    for tray in fan_trays:
        speed = c.running.get(specific_path.format(tray))['speed'].data
        result.append(["FAN TRAY {} SPEED".format(tray), "{}%".format(speed)])
    return result

def main():
    # Start the session
    c = connect()

    # Create two lists to hold the results table data and any failure table data
    result_table_data = []
    failure_table_data = []

    # Card data
    card_result = card(c)
    if card_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["CARD STATUS", "FAIL"])
        failure_table_data.extend(card_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["CARD STATUS", "PASS"])
    
    # MDA data
    mda_result = mda(c)
    if mda_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["MDA STATUS", "FAIL"])
        failure_table_data.extend(mda_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["MDA STATUS", "PASS"])

    # ISIS data
    isis_result = isis(c)
    if isis_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["ISIS STATUS", "FAIL"])
        failure_table_data.extend(isis_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["ISIS STATUS", "PASS"])

    # BGP data
    bgp_result = bgp(c)
    if bgp_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["BGP STATUS", "FAIL"])
        failure_table_data.extend(bgp_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["BGP STATUS", "PASS"])

    # MPLS data
    mpls_result = mpls(c)
    if mpls_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["MPLS STATUS", "FAIL"])
        failure_table_data.extend(mpls_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["MPLS STATUS", "PASS"])

    # svc data
    svc_result = svc(c)
    if svc_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["SERVICE STATUS", "FAIL"])
        failure_table_data.extend(svc_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["SERVICE STATUS", "PASS"])

    # ping tests
    ping_result = ping(c)
    if ping_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["PING TESTS", "FAIL"])
        failure_table_data.extend(ping_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["PING TESTS", "PASS"])

    # CPU data
    result_table_data.append(["BUSIEST CPU CORE OVER 5MIN", "{}%".format(cpu(c))])

    # Memory data
    result_table_data.append(["MEMORY UTILIZATION", memory(c)])

    # CF3 flash data
    result_table_data.append(["CF3 UTILIZATION", cf3(c)])

    # Fan data
    # We 'extend' the result table list this time because of multiple fan trays
    result_table_data.extend(fan(c))

    # Disconnect the session
    c.disconnect()

    # Print the results table
    print_table(result_table_data, [(60, "Test"), (19, "Result")], "Self Test Results")

    # Print the failure table only if there are any failures
    if failure_table_data:
        print("\n")
        print_table(failure_table_data, [(79, "Failures")], "Details Of Failed Tests")

# Call the main function
if __name__ == '__main__':
    main()
```
///

## Legendary stretch goal tasks

### Get non-zero network Q drops

Create some code that creates a new table with any non-zero network QoS drops.

/// admonition | Stop and take time to think here
    type: question
- Can you find some state information in MD-CLI that shows network queue drops?
- How will you differentiate between network ports and access/connector ports?
- How will you structure your new tables?
///

/// details | Network QoS drops (check only if you are stuck)
    type: success

/// tab | New function
```py
def collect_qos_drops(c):
    """
    This function takes a connection object then gets a list of all ports.
    It looks for ports that have network queues and finds any that are non-zero.
    If any are non-zero then it gathers the info in lists of lists for the table function.
    """

    # Get a list of the ports
    port_list = c.running.get_list_keys("/nokia-state:state/port")
    
    # A list to store the data in
    data = []

    for port in port_list:
        # Grab all the info on that port
        port_info = c.running.get('/nokia-state:state/port[port-id="{}"]'.format(port))

        if port_info['port-class'].data != 'connector':
            # If the port doesn't have network queues we ignore it
            try:
                port_info['network']['egress']['queue']
            except:
                pass
            else:
                # Collect the numbers of egress and ingress queues
                egress_queues = sorted(port_info['network']['egress']['queue'].keys())
                ingress_queues = sorted(port_info['network']['ingress']['queue'].keys())
                # Go through each egress queue looking for non-zero drops
                for q_e in egress_queues:
                    in_drops = (
                        port_info['network']['egress']['queue'][q_e]
                        ['statistics']['in-profile-dropped-packets'].data
                    )
                    out_drops = (
                        port_info['network']['egress']['queue'][q_e]
                        ['statistics']['out-profile-dropped-packets'].data
                    )
                    if in_drops != 0:
                        data.append([port, q_e, 'E', 'in', in_drops])
                    if out_drops != 0:
                        data.append([port, q_e, 'E', 'out', out_drops])
                # Go through each ingress queue looking for non-zero drops
                for q_i in ingress_queues:
                    in_drops = (
                        port_info['network']['ingress']['queue'][q_i]
                        ['statistics']['in-profile-dropped-packets'].data
                    )
                    out_drops = (
                        port_info['network']['ingress']['queue'][q_i]
                        ['statistics']['out-profile-dropped-packets'].data
                    )
                    if in_drops != 0:
                        data.append([port, q_i, 'I', 'in', in_drops])
                    if out_drops != 0:
                        data.append([port, q_i, 'I', 'out', out_drops])
    return data
```
///
/// tab | Code added to `main()`
```py
    # Collect data on QoS drops
    qos_table_title = "Any non-zero network QoS drops"
    qos_table = collect_qos_drops(c)

    c.disconnect() # Already in main()

    print("\n") # Add an extra space in between tables
    print_table(
        qos_table,
        [(15, "Port"), (10, "Q"), (10, "I/E"), (10, "Profile"), (34, "Drops")],
        qos_table_title
    )
```
///
///

/// admonition | Stop and take time to think here
    type: question
- How can you test this?
- How would you create some network qos drops on queues without pushing a load of traffic through?

/// details | Answer
    type: success

Setting the MBS to 0 on a queue makes a queue drop all traffic and will increment your QoS drop counter.

```
/configure port 1/1/c1/1 ethernet network egress queue-policy "test"
/configure qos network-queue "test" queue 1 mbs 0.0
```

Don't forget to remove the queue-policy from the port when finished so your network continues to work!

```
/configure port 1/1/c1/1 ethernet network egress delete queue-policy
```

///
///

### Get non-zero port errors

Create some code that creates a new table with any non-zero port errors.

/// admonition | Note
    type: note
It isn't an easy task to test this in a lab scenario. You could if you wish change to packet stats instead of errors just to see it all working.
///

/// details | Port errors (check only if you are stuck)
    type: success

/// tab | New function
```py
def collect_port_errors(c):
    """
    This function takes a connection object then gets a list of all ports.
    It looks for ports that have any non-zero Ethernet errors.
    If any are non-zero then it gathers the info in lists of lists for the table function.
    """

    # Get a list of the ports
    port_list = c.running.get_list_keys("/nokia-state:state/port")
    
    # A list to store the data in
    data = []

    for port in port_list:
        # Grab all the info on that port
        port_info = c.running.get('/nokia-state:state/port[port-id="{}"]'.format(port))

        if port_info['port-class'].data != 'connector':
            # If the port doesn't have Ethernet statistics we ignore it
            try:
                port_info['ethernet']['statistics']
            except:
                pass
            else:
                # Grab the in and out error data
                in_errors = port_info['ethernet']['statistics']['in-errors'].data
                out_errors = port_info['ethernet']['statistics']['out-errors'].data

                # If they are not zero we add the data to the list to be printed
                if in_errors != 0:
                    data.append([port, 'I', in_errors])
                if out_errors != 0:
                    data.append([port, 'E', out_errors])
    return data
```
///
/// tab | Code added to `main()`
```py
    # Collect data on port errors
    error_table_title = "Any non-zero port errors"
    error_table = collect_port_errors(c)

    c.disconnect() # Already in main()

    print("\n") # Add an extra space in between tables
    print_table(
        error_table,
        [(15, "Port"), (10, "I/E"), (54, "Drops")],
        error_table_title
    )
```
///
///

### Create logic to gain delta stats

Create some new code that collects the non-zero QoS drops and port errors over an interval and only print those tables if the QoS drops or port errors are incrementing over that period.

/// admonition | Stop and take time to think here
    type: question
- What do we need to add to allow a user to provide an argument to our script?
- What logic can we use to allow the script to be used with and without arguments?
- How can we ensure the user provides a valid argument?
- What logic will you use in a new function to compare the two iterations of data?
- How can we handle the situation where QoS drops or port errors start incrementing **between** iterations
///

/// details | Two iterations of data for delta stats (check only if you are stuck)
    type: success

/// tab | New libraries to import
At the very top of your code you will want to add in the time and sys libraries so that you can pause the script for the specified period and get an argument from the user
```py
#!/usr/bin/env python3

# Import the required modules
from pysros.management import connect # Already configured
from pysros.pprint import Table # Already configured
import time
import sys  
```
///
/// tab | New function to compare iterations of data
```py
def compare_lists(list1, list2, list_item_to_compare):
    """
    This function takes two lists of lists and compares a certain index in them.
    It matches items based on their unique identifiers (the rest of the content in the list).
    If items are in list2 but not in list1, then they must have started incrementing
    during the collection interval so we add them straight to the new list.
    """
    new_list = []

    # Create dictionaries to map unique identifiers to list items
    def create_dict(lst):
        return {
            tuple(
                item[:list_item_to_compare] + item[list_item_to_compare + 1:]
            ): item
            for item in lst
        }

    dict1 = create_dict(list1)
    dict2 = create_dict(list2)

    # Find new items in list2 that are not in list1
    for key in set(dict2.keys()) - set(dict1.keys()):
        new_list.append(dict2[key])

    # Compare items that exist in both lists
    for key in set(dict1.keys()) & set(dict2.keys()):
        diff = dict2[key][list_item_to_compare] - dict1[key][list_item_to_compare]
        if diff != 0:
            incrementing_list = dict1[key][:]
            incrementing_list[list_item_to_compare] = diff
            new_list.append(incrementing_list)
    
    return new_list
```
///
/// tab | New logic added to `main()`
Add this code to `main()` before the `c.disconnect()` line so the script can be used with and without an argument.

```py
    # Only run this if a user has supplied an argument with the script
    if len(sys.argv) != 1:
        # Grab the user supplied argument
        try: 
            interval = int(sys.argv[1])
        # If the user hasn't provided an integer let's complain
        except:
            print("Enter an integer argument for the number of seconds you want to collect for")
            sys.exit()
        else:
            print("Collecting second iteration in {} seconds. Please wait".format(interval))
            time.sleep(interval)
            # Collect another set of data after the interval has elapsed
            qos_table2 = collect_qos_drops(c)
            error_table2 = collect_port_errors(c)
            # Run the previous and new data against the compare_lists function
            new_qos_table = compare_lists(qos_table, qos_table2, 4)
            new_error_table = compare_lists(error_table, error_table2, 2)
            # Update the data we show in the table so delta values are now seen.
            qos_table = new_qos_table
            error_table = new_error_table
            # Update the title of the tables to show the delta values
            qos_table_title = "Any incrementing network QoS drops over {} seconds".format(interval)
            error_table_title = "Any incrementing port errors over {} seconds".format(interval)

    # Disconnect the session
    c.disconnect() # Already configured
```
///
///

## Summary and review

Congratulations for getting through all the tasks, extension tasks and legendary stretch goal tasks! Get your script and alias updated and test it. If you have got to this stage you have achieved the following:

- You have established a connection with pySROS either remotely or locally on a MD-CLI device.
- You have learnt how to navigate and find state data in MD-CLI.
- You have used the `get_list_keys` method to find out what entities a node has been configured with.
- You have learnt how to output a table that looks like a SR OS show command using the `pprint.Table` method.
- You have created an alias in model-driven SR OS that exposes your code as if it were a native command.
- You have written some complicated code that gets multiple iterations of data over a user defined period and calculates the difference.

This is a pretty extensive list of achievements! Well done!

If you're hungry for more then have a go at another activity, or try to expand upon this one if you have some more ideas. Why not try and add packets per second to the final delta stats?

/// details | Full legendary script (check only if you are stuck)
    type: success

```py
#!/usr/bin/env python3

# Import the required modules
from pysros.management import connect
from pysros.pprint import Table
import time
import sys   

# Our function from earlier that helps us print pretty show commands
def print_table(rows, cols, title):
    """
    This function uses the Table class from the pysros.pprint module to print a table
    in the style of the Nokia SROS CLI.
    It takes a list of lists as the rows.
    It takes a list of tuples which are the column names and their width.
    It takes a title string which is printed out at the top of the table.
    """
    # Initialize the Table object with the heading and columns.
    table = Table(title, cols)
    table.print(rows) # Print the table

def card(c):
    """
    This function first uses the get_list_keys method to get a list of all the cards in the system.
    It then iterates through the list of cards and checks the operational state of each card.
    If the operational state is not 'in-service', it adds a failure string message within a list
    to the result list. (list of lists). The function returns the result list, which will be empty
    if all provisioned cards are operationally in-service.
    """
    top_path  = "/nokia-state:state/card"
    cards = c.running.get_list_keys(top_path)
    specific_path = '/nokia-state:state/card[slot-number="{}"]/hardware-data'
    result = []
    for card in cards:
        # Check if the card is not operationally in-service
        if c.running.get(specific_path.format(card))['oper-state'].data not in ["in-service", "empty"]:
            # If it isn't then we add to the result list to signify a failure
            result.append(["Card {} is not operationally in-service".format(card)])
    return result

def mda(c):
    """
    This function needs to be a bit different as we have to run get_list_keys twice, once
    to get a list of cards, and again against each card to get a list of MDAs in that card.
    MDAs are also different in that this state data also shows for MDAs that are not
    provisioned so we also filter off anything that has an oper-state of 'empty'
    """
    top_path  = "/nokia-state:state/card"
    cards = c.running.get_list_keys(top_path)
    mda_path = '/nokia-state:state/card[slot-number="{}"]/mda'
    specific_path = '/nokia-state:state/card[slot-number="{}"]/mda[mda-slot="{}"]/hardware-data'
    result = []
    
    for card in cards:
        mdas = c.running.get_list_keys(mda_path.format(card))
        # Check if the card is not operationally in-service
        for mda in mdas:
            if c.running.get(
                specific_path.format(card, mda)
            )['oper-state'].data not in ["in-service", "empty"]:
                # If it isn't then we add to the result list to signify a failure
                result.append(["MDA {}/{} is not operationally in-service".format(card, mda)])
    return result

def isis(c):
    """
    This function first uses the get_list_keys method to get a list of all the ISIS interfaces.
    It then iterates through the list of interfaces and checks the operational state of each
    adjacency. If the operational state is not 'up', it adds a message to the result list.
    The function returns the result list, which will be empty if all adjacencies are
    operationally up.
    """
    top_path  = '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]/interface'
    interfaces = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]'
        '/interface[interface-name="{}"]/adjacency[adjacency-index="1"]'
    )
    result = []
    for interface in interfaces:
        if interface != "system": # Skip the system interface
            # There could be a LookupError if there is no adjacency index at all
            try:
                # Check if the adjacency is not operationally up
                if c.running.get(specific_path.format(interface))['oper-state'].data != "up":
                    # If it isn't then we add to the result list to signify a failure
                    result.append(["The ISIS adjacency on interface {} is not up".format(interface)])
            except LookupError:
                result.append(["The ISIS adjacency on interface {} is not up".format(interface)])
    return result

def mpls(c):
    """
    This function checks that the SR-LFA coverage is 100% for the node-sid topology.
    """
    path = (
        '/nokia-state:state/router[router-name="Base"]/isis[isis-instance="0"]'
        '/sr-lfa-coverage[level-number="2"][multi-topology-id="ipv4"]'
        '[sid-type="node-sid"][protocol-version="ipv4"]'
    )
    data = c.running.get(path)['lfa-covered-percent'].data
    result = []
    if data != 100:
        # If it isn't then we add to the result list to signify a failure
        result.append(["The ISIS SR-LFA coverage is not 100%"])
    return result

def bgp(c):
    """
    This function first uses the get_list_keys method to get a list of all the BGP peers.
    It then iterates through the list of peers and checks the operational state of each peering.
    If the operational state is not 'Established', it adds a message to the result list.
    The function returns the result list, which will be empty if all BGP peerings are Established.
    """
    top_path  = '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
    peerings = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/router[router-name="Base"]/bgp/neighbor'
        '[ip-address="{}"]/statistics'
    )
    result = []
    for peer in peerings:
        # Check if the peering is not Established
        if c.running.get(specific_path.format(peer))['session-state'].data != "Established":
            # If it isn't then we add to the result list to signify a failure
            result.append(["The BGP peer {} is not Established".format(peer)])
    return result

def svc(c):
    """
    Different service types are in different paths, so for this function we need to check both
    separately and then combine the results into one list. For this example we are just checking
    VPLS and IES services. We also need to check that the IES service is not the internal one
    which is used for the system
    """
    top_path  = "/nokia-state:state/service/{}"
    vpls_services = c.running.get_list_keys(top_path.format("vpls"))
    ies_services = c.running.get_list_keys(top_path.format("ies"))
    specific_path = '/nokia-state:state/service/{}[service-name="{}"]'
    result = []
    for vpls in vpls_services:
        # Check if the service is not up
        if c.running.get(specific_path.format('vpls', vpls))['oper-state'].data != "up":
            # If it isn't then we add to the result list to signify a failure
            result.append(["The VPLS service {} is not up".format(vpls)])
    for ies in ies_services:
        if ies != "_tmnx_InternalIesService": # Skip the internal IES service
            # Check if the service is not up
            if c.running.get(specific_path.format('ies', ies))['oper-state'].data != "up":
                # If it isn't then we add to the result list to signify a failure
                result.append(["The IES service {} is not up".format(ies)])
    return result

def ping(c):
    """
    This function takes a connection object and pings destinations of your choice.
    It uses the c.action method to ping and we extract just the packet loss from the result.
    If any packet loss is seen then we flag a failure by populating the result list and return. 
    """

    ping_path = '/nokia-oper-global:global-operations/ping'
    ping_data = {'destination': '{}',
                    'output-format': 'summary',
                    'interval': "0.01",
                    'timeout': 1}

    ping_dest  = [
                     "10.46.15.22", # PE2
                     "10.46.15.23", # PE3
                     "10.46.15.24"  # PE4
                 ]
    
    result = []

    for dest in ping_dest:
        ping_data['destination'] = dest
        the_ping = c.action(ping_path, ping_data)
        pktloss = the_ping['results']['summary']['statistics']['packets']['loss'].data
        if pktloss != '0.0':
            # If packet loss isn't 0.0 then we add to the result list to signify a failure
            result.append(["Ping to {} saw packet loss".format(dest)])
    return result

def cpu(c):
    """
    This function collects the cpu-usage of the businest CPU core over a 5 minute period.
    The collected data is a string, so it is converted to a float and then to an int to show a whole number
    """
    path  = '/nokia-state:state/system/cpu[sample-period="300"]/summary/busiest-core-utilization'
    result = c.running.get(path)['cpu-usage'].data
    return int(float(result))

def memory(c):
    """
    This function collects the memory in use and available from the system
    From this it calculates the memory utilization and formats it the same way as the CPU utilization
    """
    path = "/nokia-state:state/system/memory-pools/summary"
    result = c.running.get(path)
    total_size = result['current-total-size'].data
    available = result['available-memory'].data
    total_mem = total_size + available
    utilization = (total_size / total_mem) * 100
    pretty_utilization = "{}%".format(int(utilization))
    return pretty_utilization

def cf3(c):
    """
    This function collects the utilization of the CF3 flash device on the active CPM.
    You need to find out first which CPM is active in order to do this.
    """
    active_cpm = c.running.get("/nokia-state:state/system/active-cpm-slot").data
    flash_path  = '/nokia-state:state/cpm[cpm-slot="{}"]/flash[flash-id="3"]'.format(active_cpm)
    result = c.running.get(flash_path)['percent-used'].data
    return "{}%".format(result)

def fan(c):
    """
    This function first uses the get_list_keys method to get a list of all the fan trays
    It then iterates through the list of trays and gets their speed
    For each tray, the speed is added to the result list
    """
    top_path  = '/nokia-state:state/chassis[chassis-class="router"][chassis-number="1"]/fan'
    fan_trays = c.running.get_list_keys(top_path)
    specific_path = (
        '/nokia-state:state/chassis[chassis-class="router"][chassis-number="1"]/fan[fan-slot="{}"]'
    )
    result = []
    for tray in fan_trays:
        speed = c.running.get(specific_path.format(tray))['speed'].data
        result.append(["FAN TRAY {} SPEED".format(tray), "{}%".format(speed)])
    return result

def collect_qos_drops(c):
    """
    This function takes a connection object then gets a list of all ports.
    It looks for ports that have network queues and finds any that are non-zero.
    If any are non-zero then it gathers the info in lists of lists for the table function.
    """

    # Get a list of the ports
    port_list = c.running.get_list_keys("/nokia-state:state/port")
    
    # A list to store the data in
    data = []

    for port in port_list:
        # Grab all the info on that port
        port_info = c.running.get('/nokia-state:state/port[port-id="{}"]'.format(port))

        if port_info['port-class'].data != 'connector':
            # If the port doesn't have network queues we ignore it
            try:
                port_info['network']['egress']['queue']
            except:
                pass
            else:
                # Collect the numbers of egress and ingress queues
                egress_queues = sorted(port_info['network']['egress']['queue'].keys())
                ingress_queues = sorted(port_info['network']['ingress']['queue'].keys())
                # Go through each egress queue looking for non-zero drops
                for q_e in egress_queues:
                    in_drops = (
                        port_info['network']['egress']['queue'][q_e]
                        ['statistics']['in-profile-dropped-packets'].data
                    )
                    out_drops = (
                        port_info['network']['egress']['queue'][q_e]
                        ['statistics']['out-profile-dropped-packets'].data
                    )
                    if in_drops != 0:
                        data.append([port, q_e, 'E', 'in', in_drops])
                    if out_drops != 0:
                        data.append([port, q_e, 'E', 'out', out_drops])
                # Go through each ingress queue looking for non-zero drops
                for q_i in ingress_queues:
                    in_drops = (
                        port_info['network']['ingress']['queue'][q_i]
                        ['statistics']['in-profile-dropped-packets'].data
                    )
                    out_drops = (
                        port_info['network']['ingress']['queue'][q_i]
                        ['statistics']['out-profile-dropped-packets'].data
                    )
                    if in_drops != 0:
                        data.append([port, q_i, 'I', 'in', in_drops])
                    if out_drops != 0:
                        data.append([port, q_i, 'I', 'out', out_drops])
    return data

def collect_port_errors(c):
    """
    This function takes a connection object then gets a list of all ports.
    It looks for ports that have any non-zero Ethernet errors.
    If any are non-zero then it gathers the info in lists of lists for the table function.
    """

    # Get a list of the ports
    port_list = c.running.get_list_keys("/nokia-state:state/port")
    
    # A list to store the data in
    data = []

    for port in port_list:
        # Grab all the info on that port
        port_info = c.running.get('/nokia-state:state/port[port-id="{}"]'.format(port))

        if port_info['port-class'].data != 'connector':
            # If the port doesn't have Ethernet statistics we ignore it
            try:
                port_info['ethernet']['statistics']
            except:
                pass
            else:
                # Grab the in and out error data
                in_errors = port_info['ethernet']['statistics']['in-errors'].data
                out_errors = port_info['ethernet']['statistics']['out-errors'].data

                # If they are not zero we add the data to the list to be printed
                if in_errors != 0:
                    data.append([port, 'I', in_errors])
                if out_errors != 0:
                    data.append([port, 'E', out_errors])
    return data

def compare_lists(list1, list2, list_item_to_compare):
    """
    This function takes two lists of lists and compares a certain index in them.
    It matches items based on their unique identifiers (the rest of the content in the list).
    If items are in list2 but not in list1, then they must have started incrementing
    during the collection interval so we add them straight to the new list.
    """
    new_list = []

    # Create dictionaries to map unique identifiers to list items
    def create_dict(lst):
        return {
            tuple(
                item[:list_item_to_compare] + item[list_item_to_compare + 1:]
            ): item
            for item in lst
        }

    dict1 = create_dict(list1)
    dict2 = create_dict(list2)

    # Find new items in list2 that are not in list1
    for key in set(dict2.keys()) - set(dict1.keys()):
        new_list.append(dict2[key])

    # Compare items that exist in both lists
    for key in set(dict1.keys()) & set(dict2.keys()):
        diff = dict2[key][list_item_to_compare] - dict1[key][list_item_to_compare]
        if diff != 0:
            incrementing_list = dict1[key][:]
            incrementing_list[list_item_to_compare] = diff
            new_list.append(incrementing_list)
    
    return new_list

def main():
    # Start the session
    c = connect()

    # Create two lists to hold the results table data and any failure table data
    result_table_data = []
    failure_table_data = []

    # Card data
    card_result = card(c)
    if card_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["CARD STATUS", "FAIL"])
        failure_table_data.extend(card_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["CARD STATUS", "PASS"])
    
    # MDA data
    mda_result = mda(c)
    if mda_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["MDA STATUS", "FAIL"])
        failure_table_data.extend(mda_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["MDA STATUS", "PASS"])

    # ISIS data
    isis_result = isis(c)
    if isis_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["ISIS STATUS", "FAIL"])
        failure_table_data.extend(isis_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["ISIS STATUS", "PASS"])

    # BGP data
    bgp_result = bgp(c)
    if bgp_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["BGP STATUS", "FAIL"])
        failure_table_data.extend(bgp_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["BGP STATUS", "PASS"])

    # MPLS data
    mpls_result = mpls(c)
    if mpls_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["MPLS STATUS", "FAIL"])
        failure_table_data.extend(mpls_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["MPLS STATUS", "PASS"])

    # svc data
    svc_result = svc(c)
    if svc_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["SERVICE STATUS", "FAIL"])
        failure_table_data.extend(svc_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["SERVICE STATUS", "PASS"])

    # ping tests
    ping_result = ping(c)
    if ping_result: # If the returned list is not empty, it means there was a failure
        result_table_data.append(["PING TESTS", "FAIL"])
        failure_table_data.extend(ping_result)
    else: # If the returned list is empty, it means there was no failure
        result_table_data.append(["PING TESTS", "PASS"])

    # CPU data
    result_table_data.append(["BUSIEST CPU CORE OVER 5MIN", "{}%".format(cpu(c))])

    # Memory data
    result_table_data.append(["MEMORY UTILIZATION", memory(c)])

    # CF3 flash data
    result_table_data.append(["CF3 UTILIZATION", cf3(c)])

    # Fan data
    # We 'extend' the result table list this time because of multiple fan trays
    result_table_data.extend(fan(c))

    # Collect data on QoS drops
    qos_table_title = "Any non-zero network QoS drops"
    qos_table = collect_qos_drops(c)

    # Collect data on port errors
    error_table_title = "Any non-zero port errors"
    error_table = collect_port_errors(c)

    # Only run this if a user has supplied an argument with the script
    if len(sys.argv) != 1:
        # Grab the user supplied argument
        try: 
            interval = int(sys.argv[1])
        # If the user hasn't provided an integer let's complain
        except:
            print("Enter an integer argument for the number of seconds you want to collect for")
            sys.exit()
        else:
            print("Collecting second iteration in {} seconds. Please wait".format(interval))
            time.sleep(interval)
            # Collect another set of data after the interval has elapsed
            qos_table2 = collect_qos_drops(c)
            error_table2 = collect_port_errors(c)
            # Run the previous and new data against the compare_lists function
            new_qos_table = compare_lists(qos_table, qos_table2, 4)
            new_error_table = compare_lists(error_table, error_table2, 2)
            # Update the data we show in the table so delta values are now seen.
            qos_table = new_qos_table
            error_table = new_error_table
            # Update the title of the tables to show the delta values
            qos_table_title = "Any incrementing network QoS drops over {} seconds".format(interval)
            error_table_title = "Any incrementing port errors over {} seconds".format(interval)

    # Disconnect the session
    c.disconnect()

    # Print the results table
    print_table(result_table_data, [(60, "Test"), (19, "Result")], "Self Test Results")

    # Print the failure table only if there are any failures
    if failure_table_data:
        print("\n") # Add an extra space in between tables
        print_table(failure_table_data, [(79, "Failures")], "Details Of Failed Tests")

    print("\n") # Add an extra space in between tables
    print_table(
        qos_table,
        [(15, "Port"), (10, "Q"), (10, "I/E"), (10, "Profile"), (34, "Drops")],
        qos_table_title
    )

    print("\n") # Add an extra space in between tables
    print_table(
        error_table,
        [(15, "Port"), (10, "I/E"), (54, "Drops")],
        error_table_title
    )

# Call the main function
if __name__ == '__main__':
    main()
```
///