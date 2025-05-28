---
tags:
  - SR OS
  - pySROS
  - Python
  - MD-CLI
  - alias
  - pyexec
  - JSON
  - JSON IETF
  - configuration
---

# Flexible encoding for configuration input on SR OS


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Flexible encoding for configuration input on SR OS                                                                                                                                                                                                                                                                                                                                                                                                                          |
| **Activity ID**           | 05                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Short Description**       | Customers often use automation tools to store and configure their network devices.  Often these tools store configurations in alternative formats from the MD-CLI format (that is used in the MD-CLI and in the model-driven save file).</p>This activity focuses on providing the ability to configure an SR OS node (from the MD-CLI or remotely) using an alternative model-driven encoding format (JSON IETF) without the need to convert into MD-CLI formatted configuration.                                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              | Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/), [Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/MD-CLI_User_Guide_25.3.R1.pdf), [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html), [Python programming language](https://www.python.org)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          | :material-router: PE1, :material-router: PE2                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **References**              | [MD-CLI user guide](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/MD-CLI_User_Guide_25.3.R1.pdf)<br/>[SR OS System management guide](https://documentation.nokia.com/sr/25-3/7750-sr/pdf/System_Management_Guide_25.3.R1.pdf)<br/>[pySROS user documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html)<br/>[pySROS GitHub](https://github.com/nokia/pysros) (check the examples directory) |


Customers often use automation tools to store and configure their network devices.  Often these tools store configurations in alternative formats from the MD-CLI format (that is used in the MD-CLI and in the model-driven save file).</p>This activity focuses on providing the ability to configure an SR OS node (from the MD-CLI or remotely) using an alternative model-driven encoding format (JSON IETF) without the need to convert into MD-CLI formatted configuration.</p>This activity has multiple high-level objectives that increase in complexity as you progress.

## Objective

1. Provide layer-3 VPRN connectivity between :material-router: PE1 and :material-router: PE2 for the `GREEN` VPRN by providing an MD-CLI command that reads from a file containing JSON IETF encoded configuration and applies it to the node
2. Provide layer-3 VPRN connectivity between :material-router: PE1 and :material-router: PE2 for the `RED` VPRN by providing an MD-CLI command that interactively reads in configuration in JSON IETF encoded format and applies it once all configuration has been applied

Only :material-router: PE1 will be configured in this activity (:material-router: PE2 will have configuration already applied)

## Technology explanation

To tackle this activity you will need to use the Python programming language pre-installed on all SR OS routers, installed locally on your workstation or installed on your groups Linux server instance.

A basic level of Python proficiency is assumed for this activity.

The key technologies this activity might utilize, include:

### pySROS file handling

pySROS provides the ability to manipulate files for input and output, both when executing on an SR OS device or on a remote server/workstation.  The following libraries included with pySROS might provide specific assistance in this area: [`uio`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/uio.html), [`uos`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/uos.html), [`uos.path`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/uos.path.html).

Libraries prefixed with a `u` are MicroPython libraries.  These may not be available remotely (depending on which Python interpreter you choose to run: Python3 or MicroPython).  Generally, pySROS allows you to import libraries without the associated `u` so that the same application code may be used on the SR OS device and remotely without alteration.

### pySROS input/output handling

pySROS provides the ability to read and write to various input locations, including STDIN.  This functionality may be useful when tackling **Objective 2**.  The following library included with pySROS might provide specific assistance in this area: [uio](https://network.developer.nokia.com/static/sr/learn/pysros/latest/uio.html).

### pySROS data conversion functions

At the heart of the pySROS library is it's complete understanding of the YANG modeled environment it is being used in.  This enables pySROS to convert between model-driven formats such as XML and JSON IETF with ease.  The [pySROS convert method](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Connection.convert) may prove valuable for this activity.

### MD-CLI pyexec command

The SR OS MD-CLI `pyexec` command allows operators to run a Python 3 application on the SR OS node by providing a filename as input or the name of a python-script configured in the MD-CLI.

Example uses: ```pyexec cf3:/myscript.py``` or ```pyexec my-script-name```

The [SR OS system management guide](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exgst4k) provides more information on it's use.


### MD-CLI alias command

SR OS MD-CLI command aliases provide a way for an operator to customize the user-experience of an SR OS node by renaming commands, creating shortcut aliases to existing commands or integrating custom developed commands directly into the MD-CLI with context sensitive help, auto-completion and the other user interface features operators love about SR OS.  

The [MD-CLI command reference guide](https://documentation.nokia.com/sr/25-3/7750-sr/books/md-cli-command-reference/environment_0.html#d67300) and the [SR OS system management guide](https://documentation.nokia.com/sr/25-3/7x50-shared/system-management/python.html#ai9exj5x8z) provide more information.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

All supporting files can be found in the `activities/nos/sros/activity-05` directory of the repository.

### Create a Python virtual environment

It is good practice when programming in Python to work in a virtual environment.  A virtual environment can be created in a number of ways, provided are two options (pick one).

*If you are developing on the SR OS devices directly you can skip this task.*

/// details | Create a virtual environment using uv

If you have the `uv` Python package and project manager installed then follow these instructions.  If you do not have the `uv` Python package and project manager installed then please try to create a virtual environment using `venv`.

Create the virtual environment using the `uv` command.

/// tab | cmd
``` bash
uv venv
``` 

///
/// tab | expected output
``` bash
Using CPython 3.11.11
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
```
///

It is important to make sure that you are using this newly created virtual environment.  To do this use the Linux `source` command.

``` bash
source .venv/bin/activate
```

You can now install pySROS.

///

/// details | Create a virtual environment using venv

A virtual environment can be created using the builtin `venv` Python module.  Create the virtual environment using the following command.

/// tab | cmd
``` bash
python -m venv .venv
``` 
///

It is important to make sure that you are using this newly created virtual environment.  To do this use the Linux `source` command.

``` bash
source .venv/bin/activate
```

You can now install pySROS.

///

### Install pySROS

When developing using pySROS you can develop on your personal device, on your groups Linux server or directly on the node.  The choice is yours.

*If you are developing on your groups Linux server or on the SR OS devices directly, pySROS is already pre-installed so you can skip this task.*

If you are developing locally, pySROS should be installed/upgraded if it is not already present on your device.  There are three methods that I will describe here: using the `uv` Python package and project manager, using the `pip` Python package manager and installing from the source code.

/// details | Installing pySROS using uv

If you have the `uv` Python package and project manager installed then follow these instructions.  If you do not have the `uv` Python package and project manager installed then please try to install using pip (it is more commonly used).

Ensure you are working in your virtual environment (created with `uv venv`) by using the `source` Linux command.

``` bash
source .venv/bin/activate
```

Next install the pySROS package from PyPI into your virtual environment.

/// tab | cmd
``` bash
uv pip install --upgrade pysros
``` 

///
/// tab | expected output
``` bash
Resolved 9 packages in 793ms
      Built ncclient==0.6.19
Prepared 9 packages in 2.96s
Installed 9 packages in 17ms
 + bcrypt==4.3.0
 + cffi==1.17.1
 + cryptography==44.0.2
 + lxml==5.3.1
 + ncclient==0.6.19
 + paramiko==3.5.1
 + pycparser==2.22
 + pynacl==1.5.0
 + pysros==25.3.1
```
///


pySROS is now installed inside your virtuall environment.

///

/// details | Installing pySROS using pip

Ensure you are working in your virtual environment by using the `source` Linux command.

``` bash
source .venv/bin/activate
```

Now ensure that you have the `pip` package manager installed by running the command.

/// tab | cmd
``` bash
python -m ensurepip
``` 
///
/// tab | possible outcome on Debian/Ubuntu
``` bash
ensurepip is disabled in Debian/Ubuntu for the system python.

Python modules for the system python are usually handled by dpkg and apt-get.

    apt-get install python-<module name>

Install the python-pip package to use pip itself.  Using pip together
with the system python might have unexpected results for any system installed
module, so use it on your own risk, or make sure to only use it in virtual
environments.
```
///

If you receive the message shown in the "possible outcome on Debian/Ubuntu" tab then run the following command to install `pip`.

``` bash
sudo apt-get install -y python-pip
```

Next install the pySROS package from PyPI into your virtual environment.

/// tab | cmd
``` bash
pip install --upgrade pysros
``` 
///
/// tab | expected output
``` bash
Collecting pysros
  Using cached pysros-25.3.1-py3-none-any.whl (85 kB)
Collecting ncclient~=0.6.12
  Using cached ncclient-0.6.19.tar.gz (112 kB)
  Preparing metadata (setup.py) ... done
Collecting lxml~=5.3.0
  Using cached lxml-5.3.2-cp311-cp311-manylinux_2_28_x86_64.whl (5.0 MB)
Collecting paramiko>=1.15.0
  Using cached paramiko-3.5.1-py3-none-any.whl (227 kB)
Collecting bcrypt>=3.2
  Using cached bcrypt-4.3.0-cp39-abi3-manylinux_2_34_x86_64.whl (284 kB)
Collecting cryptography>=3.3
  Using cached cryptography-44.0.2-cp39-abi3-manylinux_2_34_x86_64.whl (4.2 MB)
Collecting pynacl>=1.5
  Using cached PyNaCl-1.5.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl (856 kB)
Collecting cffi>=1.12
  Using cached cffi-1.17.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (467 kB)
Collecting pycparser
  Using cached pycparser-2.22-py3-none-any.whl (117 kB)
Installing collected packages: pycparser, lxml, bcrypt, cffi, pynacl, cryptography, paramiko, ncclient, pysros
  DEPRECATION: ncclient is being installed using the legacy 'setup.py install' method, because it does not have a 'pyproject.toml' and the 'wheel' package is not installed. pip 23.1 will enforce this behavior change. A possible replacement is to enable the '--use-pep517' option. Discussion can be found at https://github.com/pypa/pip/issues/8559
  Running setup.py install for ncclient ... done
Successfully installed bcrypt-4.3.0 cffi-1.17.1 cryptography-44.0.2 lxml-5.3.2 ncclient-0.6.19 paramiko-3.5.1 pycparser-2.22 pynacl-1.5.0 pysros-25.3.1
```
///

///

/// details | Installing pySROS from the source code

These instructions assume you have the `git` source code management tool installed.

Use `git` to clone the source code repository from GitHub (where the pySROS source code is published).

/// tab | cmd
``` bash
git clone https://github.com/nokia/pysros
``` 
///
/// tab | expected output
``` bash
Cloning into 'pysros'...
remote: Enumerating objects: 1000, done.
remote: Counting objects: 100% (121/121), done.
remote: Compressing objects: 100% (83/83), done.
remote: Total 1000 (delta 62), reused 76 (delta 36), pack-reused 879 (from 1)
Receiving objects: 100% (1000/1000), 1.04 MiB | 5.75 MiB/s, done.
Resolving deltas: 100% (729/729), done.
```
///

Now ensure that you have the `pip` package manager installed by running the command.

/// tab | cmd
``` bash
python -m ensurepip
``` 
///
/// tab | possible outcome on Debian/Ubuntu
``` bash
ensurepip is disabled in Debian/Ubuntu for the system python.

Python modules for the system python are usually handled by dpkg and apt-get.

    apt-get install python-<module name>

Install the python-pip package to use pip itself.  Using pip together
with the system python might have unexpected results for any system installed
module, so use it on your own risk, or make sure to only use it in virtual
environments.
```
///

If you receive the message shown in the "possible outcome on Debian/Ubuntu" tab then run the following command to install `pip`.

``` bash
sudo apt-get install -y python-pip
```

Next install the pySROS package from the source code you downloaded.

/// tab | cmd
``` bash
cd pysros
pip install .
``` 
///
/// tab | expected output
``` bash
Processing /home/nokia/jgctest/pysros
Collecting ncclient~=0.6.12
  Using cached ncclient-0.6.19.tar.gz (112 kB)
Collecting lxml~=5.3.0
  Downloading lxml-5.3.1-cp310-cp310-manylinux_2_28_x86_64.whl (5.2 MB)
     |████████████████████████████████| 5.2 MB 19.2 MB/s 
Collecting paramiko>=1.15.0
  Downloading paramiko-3.5.1-py3-none-any.whl (227 kB)
     |████████████████████████████████| 227 kB 89.9 MB/s 
Collecting pynacl>=1.5
  Using cached PyNaCl-1.5.0-cp36-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.manylinux_2_24_x86_64.whl (856 kB)
Collecting cryptography>=3.3
  Downloading cryptography-44.0.2-cp39-abi3-manylinux_2_28_x86_64.whl (4.2 MB)
     |████████████████████████████████| 4.2 MB 60.4 MB/s 
Collecting bcrypt>=3.2
  Downloading bcrypt-4.3.0-cp39-abi3-manylinux_2_28_x86_64.whl (284 kB)
     |████████████████████████████████| 284 kB 61.7 MB/s 
Collecting cffi>=1.12
  Downloading cffi-1.17.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (446 kB)
     |████████████████████████████████| 446 kB 86.2 MB/s 
Collecting pycparser
  Using cached pycparser-2.22-py3-none-any.whl (117 kB)
Using legacy 'setup.py install' for pysros, since package 'wheel' is not installed.
Using legacy 'setup.py install' for ncclient, since package 'wheel' is not installed.
Installing collected packages: pycparser, cffi, pynacl, cryptography, bcrypt, paramiko, lxml, ncclient, pysros
    Running setup.py install for ncclient ... done
    Running setup.py install for pysros ... done
Successfully installed bcrypt-4.3.0 cffi-1.17.1 cryptography-44.0.2 lxml-5.3.1 ncclient-0.6.19 paramiko-3.5.1 pycparser-2.22 pynacl-1.5.0 pysros-25.3.1
```
///

///


### Test end-to-end VPRN connectivity

To ensure the remote end of the VPRNs are ready for you to test with once you create your solution, they have been configured for you on :material-router: PE2.

Run the following command to verify the end-to-end traffic integrity of the `RED` and `GREEN` VPRNs.

*This command may take a few seconds (or minutes if it's the first time you've run pySROS against the specific node) to complete.*

/// tab | cmd
``` bash
python verify.py
``` 
///
/// tab | expected output
``` bash
Enter router password:
=====================================================================================
Verification table
=====================================================================================
Host                      GREEN config    RED config      GREEN traffic   RED traffic    
-------------------------------------------------------------------------------------
clab-srexperts-pe1        False           False           False           False          
clab-srexperts-pe2        True            True            False           False          
=====================================================================================
```
///

You can see from the expected output that :material-router: PE2 is configured but :material-router: PE1 is not and therefore, there is no connectivity between the sites (in either of the `GREEN` or `RED` VPRNs).  This is the correct state at this stage of the activity.

### Create an application that configures :material-router: PE1 from a JSON IETF file

This is the first major task of this activity.  The following are the headline steps this specific task requires:

#### Read in file

Create a Python application called `jsonconfig.py` that reads from a hard-coded filename (or optionally a filename you provide on the command line) that contains the configuration for the `GREEN` VPRN in JSON IETF encoding.

A file named -{{ github_link('activities/nos/sros/activity-05/green.json') }}- is available with the correctly encoded JSON IETF configuration for you to use.

You may choose to execute this application from the MD-CLI prompt on :material-router: PE1, or remotely from your machine or the server instance you have been provided.

#### Convert the obtained JSON IETF configuration into pySROS format

Having read in the JSON IETF data from the file, use the pySROS library to convert it into pySROS format.

#### Configure the node from your application using the converted data

Having obtained a pySROS formatted data structure containing the configuration, configure :material-router: PE1 with it.

/// details | Hint
    type: tip

pySROS utilizes NETCONF as the underlying protocol. 

NETCONF requires the operator to supply a top level path and (currently) pySROS requires the same. 
 
You have been provided with the full JSON IETF formatted configuration back to the YANG modeled root.  This includes the top level path, therefore, you will need to strip this off and supply it as the `path` parameter of the pySROS `set` method.
///

### Re-test end-to-end VPRN connectivity

Run the following command to verify the end-to-end traffic integrity of the `RED` and `GREEN` VPRNs.

*This command may take a few seconds to complete.*

/// tab | cmd
``` bash
python verify.py
``` 
///
/// tab | expected output
``` bash
Enter router password:
=====================================================================================
Verification table
=====================================================================================
Host                      GREEN config    RED config      GREEN traffic   RED traffic    
-------------------------------------------------------------------------------------
clab-srexperts-pe1        True            False           True            False           
clab-srexperts-pe2        True            True            True            False           
=====================================================================================
```
///

If your application works correctly, you will have been able to configure :material-router: PE1 on the command line, using your program, and the configuration for the `GREEN` VPRN should be shown present on :material-router: PE1.  

Both :material-router: PE1 and :material-router: PE2 should be able to ping each other over the `GREEN` VPRN showing that traffic is flowing correctly.

### Write a new program, or extend your current one, to configure :material-router: PE1 interactively in JSON IETF

Having successfully created a Python application to run on the :material-router: PE1 SR OS router, it's time to flex your Python and pySROS knowledge.

Either extend your original application, or write a new one, that allows you to cut and paste the JSON IETF configuration interactively into the SR OS MD-CLI and apply it to the router only when you are happy with it.

This new (or extended) application should not use any input files, but instead, you should cut-and-paste the following configuration for the `RED` VPRN.

For this task you should execute your created application *on the SR OS device* using the MD-CLI.


/// details | red.json
``` json
{
    "nokia-conf:configure": {
        "service": {
            "vprn": [
                {
                    "service-name": "activity-05-red",
                    "admin-state": "enable",
                    "service-id": 502,
                    "customer": "1",
                    "bgp-evpn": {
                        "mpls": [
                            {
                                "bgp-instance": 1,
                                "admin-state": "enable",
                                "route-distinguisher": "10.46.15.21:502",
                                "vrf-target": {
                                    "community": "target:65000:502"
                                },
                                "auto-bind-tunnel": {
                                    "resolution": "filter",
                                    "resolution-filter": {
                                        "sr-isis": true
                                    }
                                }
                            }
                        ]
                    },
                    "interface": [
                        {
                            "interface-name": "vprn-pe-ce",
                            "admin-state": "enable",
                            "loopback": true,
                            "ipv4": {
                                "primary": {
                                    "address": "10.0.0.21",
                                    "prefix-length": 32
                                }
                            }
                        }
                    ],
                    "static-routes": {
                        "route": [
                            {
                                "ip-prefix": "172.16.21.0\/24",
                                "route-type": "unicast",
                                "blackhole": {
                                    "admin-state": "enable",
                                    "generate-icmp": true
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
}
```

///

This JSON IETF configuration is also available in the -{{ github_link('activities/nos/sros/activity-05/red.json') }}- file within the repository if that is easier to cut and paste from.

/// details | Hint
    type: tip

You may wish to consider the `input()` Python method to solve this part of the activity.  You should also consider handling the `EOFError` Exception.

///

### Configure SR OS to reference your application

Configure this Python application info the SR OS configuration using the `/configure python python-script`.  Make sure you identify it as a `python3` script.

### Create a SR OS command-alias pointing to your configured Python application

Create a command alias called `load-json` that calls your interactive Python application (configured as a `python-script`) and has it's own customized question-mark (`?`) help text.

### If you get stuck

/// details | Hint
    type: tip

If you get stuck and need to return the lab to it's original starting position, run the following commands:

/// tab | cmd
``` bash
python setup-activity.py teardown --configure-all
python setup-activity.py setup
``` 
///
/// tab | expected output 1
``` bash
Enter router password:
Getting connection to clab-srexperts-pe1
Connecting to clab-srexperts-pe1.
This may take some time if this is the first time you have connected to clab-srexperts-pe1.
Connected to clab-srexperts-pe1.
YANG schema obtained and compiled.
Deleting service configuration from clab-srexperts-pe1.
Deleted service configuration from clab-srexperts-pe1.
Getting connection to clab-srexperts-pe2
Connecting to clab-srexperts-pe2.
This may take some time if this is the first time you have connected to clab-srexperts-pe2.
Connected to clab-srexperts-pe2.
YANG schema obtained and compiled.
Deleting service configuration from clab-srexperts-pe2.
Deleted service configuration from clab-srexperts-pe2.
```
///
/// tab | expected output 2
``` bash
Enter router password:
Getting connection to clab-srexperts-pe2
Connecting to clab-srexperts-pe2.
This may take some time if this is the first time you have connected to clab-srexperts-pe2.
Connected to clab-srexperts-pe2.
YANG schema obtained and compiled.
Configuring clab-srexperts-pe2.
Configuration of clab-srexperts-pe2 complete.
```
///


///



## Summary and review

Congratulations!  If you have got this far you have completed this activity and achieved the following:

- You have learnt how to install pySROS and Python virtual environments
- You have written one or more applications using the Python 3 programming language
- You have an understanding of model-driven management
- You have worked with YANG modeled data
- You have worked with multiple standardized encodings such as JSON IETF (defined in [RFC 7951](https://datatracker.ietf.org/doc/html/rfc7951))
- You have worked with file handling and interactive I/O operations in Python
- You have executed Python applications on the SR OS model-driven CLI (MD-CLI)
- You have created aliases on the SR OS model-driven CLI (MD-CLI) in order to integrate your own commands into the fabric of SR OS

This is a pretty extensive list of achievements! Well done!

If you're hungry for more have a go at another activity, or try the same activity using XML encoding (you can use the `info full-context xml` command on the SR OS MD-CLI to get your configuration in XML format).

/// details | Possible solution Python code (only look here as a last resort!)
    type: success

This is one possible solution, there are multiple ways to solve the tasks and there isn't a 'right' way.  If your code
works then your solution is great!

/// tab | code for example solution
``` python3
#!/usr/bin/env python

import json
import sys

from pysros.exceptions import ModelProcessingError
from pysros.management import connect, sros


def get_connection(host="clab-srexperts-pe1", user="admin", password=None):
    """Obtain a connection to the router.  This wrapper function to the pySROS connect
    method provides some defaults for the parameters and some error (Exception) handling.
    You will need to supply details when calling this function if you are executing this
    application remotely.

    Args:
        host (str, optional): Router to be configured (IP address or hostname). Defaults to "clab-srexperts-pe1".
        user (str, optional): Username. Defaults to "admin".
        password (_type_, optional): Password. Defaults to None.

    Raises:
        SystemExit: Failed to creation Connection object
        SystemExit: Failed to create mode-driven schema
        SystemExit: Failed to connect

    Returns:
        pysros.management.Connection: Connection object
    """
    try:
        connection_object = connect(
            host=host,
            username=user,
            password=password,
            hostkey_verify=False,
        )
        return connection_object
    except RuntimeError as error1:
        print(
            "Failed to connect during the creation of the Connection object. Error:",
            error1,
        )
        raise SystemExit()
    except ModelProcessingError as error2:
        print("Failed to create model-driven schema.  Error:", error2)
        raise SystemExit()
    except Exception as error3:
        print("Failed to connect.  Error:", error3)
        raise SystemExit()


def read_file(filename, format="json"):
    """Read in a file in various formats.

    Args:
        filename (str): Filename
        format (str, optional): Format of the data in the file. Defaults to "json".

    Raises:
        NotImplemented: Alternative formats are not implemented

    Returns:
        str: Contents of the file
    """
    if format == "json":
        try:
            with open(filename, "r") as input_file:
                data = json.load(input_file)
                return json.dumps(data)
        except ValueError as error:
            print("Failed to read file. Error:", error)
            raise SystemExit()
    else:
        raise NotImplemented


def convert_data(
    connection_object,
    data,
    source_format="json",
    destination_format="pysros",
):
    """Convert between structure data formats of encoded YANG according to a specific
    devices Connection object.  This function provides a wrapper around the pySROS
    convert method for use in this activity.

    Args:
        connection_object (pysros.management.Connection): Connection object
        data (str): Data payload to be converted
        source_format (str, optional): Encoding of source data. Defaults to "json".
        destination_format (str, optional): Encoding of resulting data. Defaults to "pysros".

    Raises:
        SystemExit: Failed to convert the data

    Returns:
        str or dict: Converted data.  A string when encoded as JSON IETF or XML, a dictionary
        when encoded as pySROS.
    """
    try:
        return connection_object.convert(
            "/",
            data,
            source_format=source_format,
            destination_format=destination_format,
        )
    except Exception as error:
        print("Failed to convert configuration.  Error:", error)
        raise SystemExit()


def read_input():
    """Obtain input from stdin.  Terminate the input with <ctrl>-d on a new line.

    Returns:
        str: Obtained input data
    """
    data = []
    print(
        "Enter your JSON IETF encoded configuration.  Press <ctrl>-d on a new line to finish."
    )
    while True:
        try:
            line = input()
        except EOFError:
            break
        data.append(line)
    return "\n".join(data)


def arguments():
    """Obtain command line arguments.  Test for the right number of arguments
    and the specific input options provided.

    Returns:
        str: "file" or "stdin"
    """

    def print_help_and_exit():
        print("Requires the string file or stdin as an input parameter")
        raise SystemExit()

    if not len(sys.argv) == 2:
        print_help_and_exit()
    if not any(item in sys.argv for item in ["file", "stdin"]):
        print_help_and_exit()
    return sys.argv[1]


def main():
    """The initial function definition."""
    args = arguments()
    connection_object = get_connection()
    if args == "file":
        if sros():
            file = "cf3:/green.json"
        else:
            file = "green.json"
        data = read_file(file)
    elif args == "stdin":
        data = read_input()
    else:
        raise NotImplemented
    pysros_config = convert_data(connection_object, data)
    try:
        connection_object.candidate.set(
            "/configure", pysros_config.pop(next(iter(pysros_config)))
        )
    except Exception as error:
        print("Failed to configure the device. Error:", error)
        raise SystemExit()
    connection_object.disconnect()


if __name__ == "__main__":
    main()
```
///

/// tab | file containing example solution
An example Python file named -{{ github_link('activities/nos/sros/activity-05/jsonconfig.py') }}- is provided as an example solution.

///

///


/// details | Possible solution MD-CLI alias configuration (only look here as a last resort!)
    type: success
/// tab | MD-CLI configuration
```
/configure python python-script "jsonconfig" admin-state enable
/configure python python-script "jsonconfig" urls ["cf3:/jsonconfig.py"]
/configure python python-script "jsonconfig" version python3
/configure system management-interface cli md-cli environment command-alias alias "load-json" admin-state enable
/configure system management-interface cli md-cli environment command-alias alias "load-json" description "Load the configuration using a JSON file or JSON via interactive input"
/configure system management-interface cli md-cli environment command-alias alias "load-json" python-script "jsonconfig"
/configure system management-interface cli md-cli environment command-alias alias "load-json" mount-point global
```

///
/// tab | Context sensitive help example
```

[/]
A:admin@g15-pe1# load-json?

 load-json

 Load the configuration using a JSON file or JSON via interactive input
```
///
///


