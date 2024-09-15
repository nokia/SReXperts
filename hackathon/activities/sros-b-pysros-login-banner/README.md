# SR OS Enhanced Login Banner with pySROS

| Item              | Details                                   |
| ----------------- | ----------------------------------------  |
| Short Description | Manage loggin banner with pySROS          |
| Skill Level       | Beginner                                  |
| Tools Used        | SR OS, Python (with the pysros library)   |

By tackling this particular scenario, you'll gain the ability to customize your SR OS system, so it consistently offers the information you need whenever you interface with the device through MD-CLI.

## High level tasks to complete this project

1. Use the MD-CLI `pwc` and `info` commands to navigate around the YANG-modelled data to find the CPU usage. 
2. Write a Python application using the pySROS libraries that extracts the CPU Usage and prints it out.
3. Create a login-script that calls your Python application on login to display the chosen data.

## Reference documentation

- [pySROS API documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest)
- [SR OS documentation](https://documentation.nokia.com/sr/)

## Accessing the lab
In this lab you will interact with the model-driven SR OS router PE3. To access it, use
```
ssh admin@clab-srexperts-pe3
```


## Task 1: Identify current CPU usage that should be displayed on login to SR OS using the MD-CLI pwc and info commands to navigate around the YANG-modelled data

Here is an example of how aquire the path and use it to obtain state data:
```
A:admin@pe3# /state system cpu 1 summary usage

[/state system cpu 1 summary usage]
A:admin@pe4# pwc json-instance-path
Present Working Context:
/nokia-state:state/system/cpu[sample-period="1"]/summary/usage
```
The resulting _Present Working Context_ can be used as the path for the pySROS `get()` function:

```
data = connection_object.running.get(
    '/nokia-state:state/system/cpu[sample-period="1"]/summary/usage'
)

print(data)

{'cpu-time': Leaf(399329), 'time-used': Leaf(399329), 'cpu-usage': Leaf('19.95')}

print(">>>Current cpu-usage = ", data["cpu-usage"], "%")

>>>Current cpu-usage =  19.95 %
```

Enhancement: If you wish to go a step further, explore the MD-CLI using the `info` and `pwc` commands for both configuration and state data to choose a selection of data points that you will find beneficial to see at login.

## Task 2: Write a Python application using the pySROS libraries that extracts the CPU usage and prints it out

Create a simple Python script in `/home/nokia/clab-srexperts/pe3/tftpboot/bannercpu.py` that will run locally on the router, using the pySROS libraries to obtain the identified data and print it to the screen.

An example pySROS application is shown [here](./example_solution/bannercpu.py) to get you started.

To test your code remotely ensure your Connection object has all the required parameters and just run it. Communication with the node will be handled by pySROS. See the documentation on [connection and data handling](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.management):


```
    connection_object = connect(
            host="clab-srexperts-pe3",
            username="username",
            password="password",
            hostkey_verify=False,
            )
```

*Note: You will need to enter the correct username and password*   

## Task 3: Create a login-script that calls your Python script on login to display the chosen data

* Create a login script file called `login.scr` in `/home/nokia/clab-srexperts/pe3/tftpboot/login.scr` that runs `pyexec tftp://172.31.255.29/bannercpu.py`
* Enable login-banner and point the login-scripts to the login.scr:
 ```
    configure {
        system {
            login-control {
                login-scripts {
                    global-script "tftp://172.31.255.29/login.scr"
                }
            }
        }
    }
 ```

Finally, try to login to the node and assess if you see the obtained data in the login banner.

