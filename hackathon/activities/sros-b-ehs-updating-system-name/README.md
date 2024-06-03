# Use EHS to display a message when someone logs in

**Grading: Beginner**

**Elements: SR OS, pySROS**

The Event Handling System (EHS) is a framework that allows operator-defined behavior to be configured on the router. 

EHS adds user-controlled programmatic exception handling by allowing the execution of either a CLI script or a Python application when a log event (the "trigger") is detected.

Python applications are fully supported and use the SR OS model-driven interfaces and the pySROS libraries to obtain and manipulate state and configuration data, as well as pySROS API calls to execute YANG-modeled operations (and as a last resort, unstructured MD-CLI commands).

When developing an EHS Python application, the event attributes are passed to the application using the `get_event` function in the **pysros.ehs** module.

* **Note:** 
        The event handling system (EHS) and its functionality are available when executing on SR OS only and not on a remote machine.

## High level tasks to complete this project

1. **Specify the event-id of the ssh_user_login/logout event**

2. **Monitor user sessions by using the MD-CLI `pwc` and `info` commands to obtain user information**

3. **Create a pySROS script using `pysros.ehs` module to change system name when someone logs in/out**


## Reference Documentation

* [Functions for the event handling system (EHS)](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.ehs)
* [Model-driven SR OS interface](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html?highlight=ehs#module-pysros)
* [SR OS documentation](https://documentation.nokia.com/sr/)


## Accessing the lab

In this lab you will interact with the model-driven SR OS router `pe4`. To access it, use:

```
ssh -l admin clab-srexperts-pe4
```

## Event Handling Basic Configuration

Already Configured on `pe4` router, below you can find the essential sample steps needed to enable the EHS using pySROS script.
Follow each step and make sure the configuration is in place on the device.

### Step 1:

Configure the location of `ehs.py` pySROS script that is going to be triggered from EHS; this location can be either on `cf3:\` or any location accessible for the router like `/home/nokia/clab-srexperts/pe4/tftpboot/ehs.py`.

```
configure {
    python {
        python-script "ehs" {
            admin-state enable
            urls ["tftp://172.31.255.29/ehs.py"]
            version python3
        }
```

### Step 2:

Make the directory in `cf3:` to store the results of the EHS execution:

```
/file make-directory cf3:/ehs/
```

Finding the filenames and accessing the output of the EHS scripts can be time consuming. To address this, a Python script has been provided [here](./example_solution/latest-ehs-output.py). You need to copy it into `/home/nokia/clab-srexperts/pe4/tftpboot/latest-ehs-output.py`. Issue `tools perform python-script reload latest-ehs-output` command to make the script operational.

To simplify the process, an alias is added to MD-CLI environment. You can use `show latest-ehs-output ehs` to get the script's results.
    
### Step 3:

A `script-policy` needs to be created. A script policy can be configured to allow an EHS script to override datastore locks from any model-driven interface:

```
configure {
    system {
        script-control {
            script-policy "ehs" owner "admin" {
                admin-state enable
                results "cf3:/ehs/"
                python-script {
                    name ## after creating the python script in Task 3, add the pySROS file name here
                }
            }
        }
```

### Step 4:

Configure `log filter` to forward all logs:

```
configure {
    log {
        filter "user_login" {
            default-action forward
            named-entry "user-login" {
                action forward
            }
        }
```

### Step 5:

To connect the `script-policy` to an event that can be triggered through logs the `event-handling handler` need to be configured:

```
configure {
    log {
        event-handling {
            handler "ehs" {
                admin-state enable
                entry 10 {
                    admin-state enable
                    script-policy {
                        name "ehs"
                        owner "admin"
                    }
                }
            }
        }
```

### Step 6:

Finaly Configure the `log event-trigger` that connects the filtered logs to the event handler:

```
configure {
    log {
        event-trigger {
            security event ssh_user_login {
                admin-state enable
                entry 10 {
                    filter "user_login"
                    handler "ehs"
                }
            }
```

The infrastructure of the EHS is ready now to be used for triggering a Python application.

Make sure that the directory to store the results of the EHS executions:  `ehs` exist in `cf3:` use `/file list` or make it by: `/file make-directory cf3:/ehs/`. 

## Task 1: Specify the event-id of the ssh_user_login/logout event  

By means of `show log event-control "security"` command you can find the event id of **ssh_user_login/logout** to be used in the pySROS application as an input for the Function call **event.eventid**.

```
 A:admin@pe4# /state log log-events security event ssh_user_login event-id
        event-id 2009

 [/]
 A:admin@pe4# /state log log-events security event ssh_user_logout event-id
        event-id 2010
 ```

Extension: different events can be used as the trigger for EHS.


## Task 2: Monitor user sessions

Use `/show users` and `info / state users` commands to check the available information of users connected to the SR OS. 

```
A:admin@pe4# info /state users
    session 771 {
        user "admin"
        router-instance "management"
        connection-ip "172.31.255.29"
        connection-type sshv2
        login-time 2024-05-17T15:00:29.0+00:00
        idle-time 0
        current-active-session true
        connection-id 772
        session-create-time 2024-05-17T15:00:29.0+00:00
    }
```

Obtain the number of users currently logged in to the router using pySROS `get()` function with the help of filtering on a specific match, for example filter on sessions that their connection-type is SSHv2. [Example using filters](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros-management-datastore-get-example-content-node-filters).


<details>
<summary>Solution</summary>

```
from pysros.management import connect

def main():

    connection = connect(
        host="local connection only - unused",
        username="local connection only - unused",
    )

    data = connection.running.get(
        "/nokia-state:state/users/session",
        filter={
            "user": {},
            "connection-type": "sshv2",
            "connection-ip": {},
        },
    )

    print(data, "\n")
    number_of_sessions = len(list(data.keys()))
    print("Number of active sessions:", number_of_sessions)

if __name__ == "__main__":
    main()
```

</details>

<details>
<summary>Output</summary>


```
A:admin@pe4# pyexec tftp://172.31.255.29/test.py
{816: Container({'connection-type': Leaf('sshv2'), 'connection-ip': Leaf('172.31.255.29'), 'user': Leaf('admin')}), 807: Container({'connection-type': Leaf('sshv2'), 'connection-ip': Leaf('172.31.255.29'), 'user': Leaf('admin')})}

Number of active sessions: 2

```
</details>

## Task 3: Create a pySROS script using pysros.ehs module to change system name when someone logs in/out
1. Create `ehs.py` pySROS script in `/home/nokia/clab-srexperts/pe4/tftpboot/ehs.py` and configure the `python-script name` as below.

```
 /configure system script-control script-policy "ehs" owner "admin" python-script name ehs
```

        
After any change to the code, issue `tools perform python-script reload ehs` command.

2. To import pysros.ehs module, the Python application developer must add the following statement to the application:

```
from pysros.ehs import get_event
```
3. Use the **_event ID obtained in task 1_** to trigger a `set()` function for changing the system name of the node to a value containing **_the number of active sessions received in task 2_**.

   Here is an example showing the use of function call **_event.eventid_** and how a simple **_Set_** a pySROS data structure to the supplied path works [set(path, value)](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.set).

```
    name_path = "/nokia-conf:configure/system"
    name_value = {"name": new_system_name}

    trigger_event = get_event()
    if trigger_event.eventid in [2009, 2010]:

        connection.candidate.set(name_path, name_value)
```
   An example pySROS application for getting the number of connected sessions through SSH can be found in [ehs.py](./example_solution/ehs.py).


4. Finally open new terminals and login/logout to the node trhough ssh  : `ssh clab-srexperts-pe4`.
This security ssh_user_login/logout event will trigger the Python application from EHS and any user with active session open on pe4 will see the name of the node changes with change in the number of logged users.
