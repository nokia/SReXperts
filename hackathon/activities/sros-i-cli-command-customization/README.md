# Using Python to customize commands in SR OS

| Item | Details |
| --- | --- |
| Short Description | Ever wanted SR OS to have your own CLI commands?  Let's build them |
| Skill Level | Intermediate |
| Tools Used | SR OS, MD-CLI, Python (with the `pysros` library) |

In this lab, we demonstrate interactions with SR OS devices through pySROS. The pySROS libraries provide a model-driven management interface for Python developers to integrate with Nokia routers running compatible versions of SR OS in model-driven mode. pySROS programs can be executed on the router itself using a local Python interpreter, as well as remotely using NETCONF. In both cases the programs produce the same results.

## Objective
In this exercise you will build on these capabilities to extend and overwrite the model-driven CLI interface. We highlight the value of your own commands written in Python when run remotely.


## Accessing the lab
In this lab you will interact with model-driven SR OS, so any model-driven SR OS router in the topology would work. For this text we will assume the `p1` node is used.
```
ssh admin@clab-srexperts-p1
```

## Task 1: Coloring the CLI

In this first task, we will start from the existing command `show router interface`. Depending on your terminal client of choice and its settings, the output of this command is shown in various colors with possible highlights. With pySROS, we can override the existing CLI command to introduce coloring to the default show commands such that the CLI itself has the appropriate highlighting regardless of the client used (if the client supports colored output). Starting from the output of the aforementioned command:

```
[/]
A:admin@p1# show router interface

===============================================================================
Interface Table (Router: Base)
===============================================================================
Interface-Name                   Adm       Opr(v4/v6)  Mode    Port/SapId
   IP-Address                                                  PfxState
-------------------------------------------------------------------------------
InterfaceDown                    Up        Down/Down   Network n/a
   -                                                           -
p2_1                             Up        Up/Up       Network 1/1/c11/1
   10.64.11.22/31                                              n/a
   fd00:fde8:0:1:1:11:12:0/127                                 PREFERRED
   fe80::e00:aff:fe91:3e0b/64                                  PREFERRED
<... truncated>
```

In this task, we will introduce highlighting for operational states, IPv4 and IPv6 addresses, interface names and port identifiers. This task consists of three subtasks. First, we'll need some pySROS code that will give us our desired output. Then, this will have to be set up as a command alias. Finally, the script's remote output and functioning will be verified. We'll start with the Python code that produces our desired output and make it available for the router.

1. Start from the file [colored_interface.py](./examples/colored_interface.py) in the [examples](./examples/) folder and prepare it for on-box execution of the file by copying it to `/home/nokia/clab-srexperts/p1/tftpboot/`. This folder on your Hackathon instance is mounted inside the SR OS container by containerlab and reachable from SR OS via `tftp`. At that point, you will be able to execute and test the script through the on-board interpreter:
```
[/]
A:admin@p1# pyexec tftp://172.31.255.29/colored_interface.py
===============================================================================
Interface Table (Router: Base)
===============================================================================
Interface-Name                   Adm       Opr(v4/v6)  Mode    Port/SapId
   IP-Address                                                  PfxState
-------------------------------------------------------------------------------
p2_2                             Up        Up/Up       Network 1/1/c12/1
   10.64.12.23/31                                              n/a
<... truncated>
```

A `color` function has been provided, as well as several variables. Complete the code such that the script output is highlighted.
```
RED =  ""
MAGENTA = ""
YELLOW = ""
WHITE = ""
GREEN = ""
RESET_COLOR = ""


def color(color, text):
    return text
```
An article with information on the topic of changing colors is available [here](https://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html). Adding and removing colors may cause the columns to shift in the output of the provided script, feel free to investigate!

<details>
<summary>Example completed variables and `color` function</summary>

```
RED = "\u001b[31;1m"
MAGENTA = "\u001b[35;1m"
YELLOW = "\u001b[33;1m"
WHITE = "\u001b[37;1m"
GREEN = "\u001b[32;1m"
RESET_COLOR = "\u001b[0m"


def color(color, text):
    return color + text + RESET_COLOR
```

</details>

2. Configure the script as a command alias of your choosing.
    1. As a first step, we have to create the Python script object that will be called by the alias. To do that, add the following configuration:
    ```
    configure {
        python {
            python-script "colored_interface" {
                admin-state enable
                urls ["tftp://172.31.255.29/colored_interface.py"]
                version python3
            }
        }
    }
    ```
    2. Then, create the command alias itself:
    ```
    configure {
        system {
            management-interface {
                cli {
                    md-cli {
                        environment {
                            command-alias {
                                alias "colored-interface" {
                                    admin-state enable
                                    description "Display IP interface information in a custom color-coded way."
                                    python-script "colored_interface"
                                    mount-point "/show router" { }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    ```
    3. Now, commit these changes. Does your command-alias appear? Try logging out and in again. Command-aliases are loaded with the environment and won't appear for sessions using the unmodified environment. The command alias should now appear under the mount point.

3. Use your custom command with `show router colored-interface`

Try looking for your command under `/show router` in the context-sensitive help menu displayed via `?`. The description of the alias is shown there. This way you can include some information about your command in the CLI, in addition to the command itself.

Does your command work? If not, make sure the latest version of your script is being used by the configured alias and issue `/perform python python-script reload script "colored_interface"` to load any additional changes made to the script file into the version of the script that is stored in the router's memory.

Would this have worked if we used `interface` instead of `colored_interface` as the name for the alias?

4. When run remotely, the call to `pysros.management.connect` requires additional information. Update the code and replace the call to connect by changing
```
conn = connect()
```
to
```
conn = connect(host='clab-srexperts-p1', username='<provided>', password='<provided>',hostkey_verify=False)
```
Optionally, use input parameters for the hostname, username and password variables.
Does the command behave the same way remotely as it does on the device? What does the `hostkey_verify` parameter in the call above do? Would that be acceptable under all circumstances? Does the same script work when you run it against `clab-srexperts-p2`?

There are options along the lines of ordering the interfaces in the output, adding interfaces from other VRFs, ... . These topics are more advanced and no longer in the scope of this task, though feel free to explore them!

## Task 2: Solving truncated outputs

The second task is to solve a notorious challenge where the column width of an SR OS show command output is too small, resulting in a truncated output. One command where this truncation might happen is the SR OS show command that displays the LLDP neighbor list.

Consider the following SR OS show command for LLDP neighbors:

```
[/]
A:admin@p1# /show system lldp neighbor
Link Layer Discovery Protocol (LLDP) System Information

===============================================================================
NB = nearest-bridge   NTPMR = nearest-non-tpmr   NC = nearest-customer
===============================================================================
Lcl Port      Scope Remote Chassis ID  Index  Remote Port     Remote Sys Name
-------------------------------------------------------------------------------
1/1/c11/1     NB    0C:00:2B:0F:FB:00  1      1/1/c11/1, 100* p2
1/1/c12/1     NB    0C:00:2B:0F:FB:00  2      1/1/c12/1, 100* p2
===============================================================================
* indicates that the corresponding row element may have been truncated.
Number of neighbors : 2
```

In the above example, the `Remote Port` column values are truncated. In this task the goal is to make a Python script that we can call where the column widths are dynamically set based on data found in the router's state information.

An example [lldp_neighbor.py](./examples/lldp_neighbor.py) script is found in the [examples](./examples/) folder. It produces the following output:

```
[/]
A:admin@p1# pyexec tftp://172.31.255.29/lldp_neighbor.py
=============================================================================================================
NB = nearest-bridge   NTPMR = nearest-non-tpmr   NC = nearest-customer  EMOJIs : 😀 💩 🤠
=============================================================================================================
Lcl Port       Scope Remote Chassis ID  Index  Remote Port                                   Remote Sys Name
1/1/c11/1      NB    0C:00:2B:0F:FB:00  1      1/1/c11/1, 100-Gig Ethernet, "link #1 to P1"  p2
1/1/c12/1      NB    0C:00:2B:0F:FB:00  2      1/1/c12/1, 100-Gig Ethernet, "link #2 to P1"  p2
=============================================================================================================
Number of neighbors : 2
```

Clearly, the output is similar and solves our truncation issue. Thanks to the unicode support, some extra's can be added as unicode includes emoji's as well. This script, as before, works remotely in the same way it does on the device.
1. Build your own version of `lldp_neighbor.py`, optionally taking inspiration from the provided version and make sure the target LLDP information output shown above is achieved. Place your file at `/home/nokia/clab-srexperts/p1/tftpboot/lldp_neighbor.py` on your provided Hackathon instance to make it available for the SR OS node at `tftp://172.31.255.29/lldp_neighbor.py`.
2. Override the system's native `show system lldp neighbor` with the appropriate command-alias pointing to your Python version.

For this task, and in general, once you have created a `python-script` object that points to your Python file, the version that is in memory will remain there even when you are updating the file. You can dynamically reload the file using `/perform python python-script reload script <script name>`.


<details>
<summary>Example configuration to add for the lldp neighbor command-alias</summary>

```
    configure {
        python {
            python-script "lldp_neighbor" {
                admin-state enable
                urls ["tftp://172.31.255.29/lldp_neighbor.py"]
                version python3
            }
        }
    }
    configure {
        system {
            management-interface {
                cli {
                    md-cli {
                        environment {
                            command-alias {
                                alias "neighbor" {
                                    admin-state enable
                                    description "Display LLDP neighbor information without truncated text in columns."
                                    python-script "lldp_neighbor"
                                    mount-point "/show system lldp" { }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
```

</details>


## Task 3: Telemetry subscriptions at a glance
Another opportunity is encountered when trying to glean which gRPC subscription contains the path you're currently trying to use or troubleshoot, depending on the situation. In the SR OS model-driven CLI, we can display this information using show commands of the form `/show system telemetry grpc subscription # paths`. This works, however in most cases requires trial and error to find the correct identifier matching the subscription you're interested in. The desired path is never in the first subscription you try.

In this task, using pySROS and command-aliases, we'll create a new command that summarizes the paths and subscription IDs to quickly provide the wanted information.
1. Identify the relevant parts of the state tree using either the CLI or the [YANG model](https://github.com/nokia/7x50_YangModels) to find the desired information.
2. Starting from the skeleton shown below, build a file `telemetry_path_summary.py` and ensure it is reachable by the router via TFTP (or load it onto cf3). Note that `hostkey_verify` is being set to `False`, this is not recommended for a live environment.
```
from pysros.management import connect
from pysros.pprint import Table

def get_connection(host,username,password):
    try:
        c = connect(
            host=host,
            username=username,
            password=password,
            hostkey_verify=False,
        )
    except Exception as e:
        print("Failed to connect:", e)
        sys.exit(-1)
    return c


# Fuction definition to output a SR OS style table to the screen
def print_grpc_subs_table(rows):

    # Define the columns that will be used in the table.  Each list item
    # is a tuple of (column width, heading).
    cols = [
        (11, "Sub. Id", '^'),
        (68, "Path"),
    ]

    # Initalize the Table object with the heading and columns.
    table = Table("Overview of gRPC subscriptions and their associated paths", cols, showCount='Subscriptions')

    # Print the output passing the data for the rows as an argument to the function.
    table.print(rows)


def get_grpc_subscription_paths(conn):
    grpc_subs = . . .
    return result


def main():
    """The main procedure.  The execution starts here."""
    node_handle = get_connection()
    information = get_grpc_subscription_paths(node_handle)
    print_grpc_subs_table([ (sub_id,path) for sub_id,paths in information.items() for path in paths ])


if __name__ == "__main__":
    main()

```

A completed version of [telemetry_path_summary.py](./examples/telemetry_path_summary.py) is included in the [examples](./examples/) folder and can be used for inspiration.
The expected output is

```
[/]
A:admin@p1# pyexec "tftp://172.31.255.29/telemetry_path_summary.py"
===============================================================================
Overview of gRPC subscriptions and their associated paths
===============================================================================
 Sub. Id   Path
-------------------------------------------------------------------------------
    1      /state/port/oper-state
    1      /state/port/statistics
    1      /state/port/ethernet/statistics
    2      /state/router/bgp/neighbor/statistics
< ... truncated >
```
3. Create a command alias `/show system telemetry grpc paths` and confirm it shows all the subscribed paths and their associated gRPC subscription identifier on the router.
```
[/]
A:admin@p1# /show system telemetry grpc paths
===============================================================================
Overview of gRPC subscriptions and their associated paths
===============================================================================
  Sub. Id   Path
-------------------------------------------------------------------------------
     1      /state/port/oper-state
     1      /state/port/statistics
     1      /state/port/ethernet/statistics
    2      /state/router/bgp/neighbor/statistics
< ... truncated >
```
4. Can you make your script work remotely?

## Further reading
Some of the elements touched on in this lab are documented in more detail [here](https://network.developer.nokia.com/sr/learn/sr-os-python/sr-os-and-pysros-101/) as well as some extra material, including an implementation for the Linux `watch` command.
