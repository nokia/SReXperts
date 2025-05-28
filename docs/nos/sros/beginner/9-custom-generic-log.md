---
tags:
  - event_handling
  - ehs
  - custom_log
  - pySROS
  - SR OS
---

# Generating customized log events with EHS


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Generating customized log events with EHS                                                                                                                                                                                                                                                                                |
| **Activity ID**           | 09        |
| **Short Description**       | Custom Events can be generated in pySROS script for use case specific conditions and as a trigger for Event Handling System                                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              | Beginner                                                                                                                                                                                                                                                                                                                                                                                                                   |
| **Tools used**              | [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/index.html), [EHS Module](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.ehs), [SR OS YANG Models](https://github.com/nokia/7x50_YangModels/tree/master/latest_sros_25.3), [SR OS YANG path finder](https://yang.labctl.net/yang/SROS/)                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| **Topology Nodes**          |  :material-router: PE2                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [Functions for the event handling system (EHS)](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.ehs)<br/>[Model-driven SR OS interface](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html?highlight=ehs#module-pysros)<br/> [SR OS Documentation](https://documentation.nokia.com/sr/25-3/index.html)|



The ability to raise a custom event via the `perform log custom-event` command is available in model-driven interfaces. Log events generated in this way pass through the regular event processing pipeline and are visible via all usual mechanisms, including show commands and configured log destinations.

There are 6 distinct events that exist within model-driven SR OS that can be used to send a `custom-event` out into the world. Each event corresponds to a severity level, ranging from `indeterminate` for `tmnxCustomEvent6` to `critical` for `tmnxCustomEvent1`. The other intermediate levels are `major` for `tmnxCustomEvent2`, `minor` for `tmnxCustomEvent3`, `warning` for `tmnxCustomEvent4` and `cleared` for `tmnxCustomEvent5`.
```
A:admin@g15-pe2# show log event-control "logger"
=======================================================================
Log Events
=======================================================================
Application
 ID#    Event Name                       P   g/s     Logged     Dropped
-----------------------------------------------------------------------
  ...
   2020 tmnxCustomEvent1                 CR  thr          0           0
   2021 tmnxCustomEvent2                 MA  thr          2           0
   2022 tmnxCustomEvent3                 MI  thr          0           0
   2023 tmnxCustomEvent4                 WA  thr          3           0
   2024 tmnxCustomEvent5                 CL  thr          0           0
   2025 tmnxCustomEvent6                 IN  thr          0           0
```
Custom events can be used as triggers for event handlers, with all parameters passed into the associated EHS scripts. The customizable log events will be output to any configured log destinations (for example, syslog or SNMP traps).

## Objective

Imagine you’re operating a customer-facing service that suddenly experiences an outage. Your network monitoring system (NMS) detects the issue and triggers an alert.

In this activity, we simulate that **automated monitoring system trigger**, by using the `perform log custom-event` command. This command manually raises a custom event,
complete with parameters that would typically be provided by the monitoring system (e.g., service ID, interface name, customer subnet). The custom event is taken by the Event Handling System (EHS) and used to call a Python application. In the scenario pictured above, this Python application may instead be called by the NMS or by an operator. We aim to show that as long as the events are available in the system, SR OS can use (custom) events as triggers for pre-programmed responses with the on-box interpreter.

For the activity, once the custom event is triggered, EHS catches it and executes a `python-script` to automatically instantiate debugging configuration.

This not only mirrors how service providers can automate failure recovery or root cause analysis, but it also shows how the EHS can be leveraged to support intelligent, responsive network behavior through programmable interfaces.

Through the tasks we will see how to pass essential parameters for creating a VPRN service to the EHS by raising a Custom Log Event, and how to use those parameters to configure the service.

``` mermaid
classDiagram
  direction LR
  class Custom-Event {
    - Subject
    - MessageString
    - Parameter1()
    - Parameter2()
    - ...Parameter8()

  }
  class EHS-pySROS-script {
    - trigger_event.eventid
    - configure-vprn(Parameters)
    - successful(raise custom-event)
    - failed(raise custom-event)
  }

Custom-Event --> EHS-pySROS-script : triggers
Custom-Event --> EHS-pySROS-script : pass parameters
EHS-pySROS-script --> Custom-Event : can trigger

```

## Event Handling Script Functionality
The Event Handling System (EHS) is a framework that enables operators to configure custom behavior on the router.

The EHS introduces user-defined, programmatic exception handling by executing either a CLI script or a Python application in response to a detected log event, referred to as the "trigger".

Python applications are fully supported and leverage the model-driven interfaces available in SR OS along with the pySROS libraries to access and modify both state and configuration data. These applications can also invoke YANG-modeled operations via pySROS API calls, and, if necessary, execute unstructured MD-CLI commands as a fallback.

During the development of an EHS Python application, event attributes are made available through the `get_event` function in the `pysros.ehs` module.

!!! note "[pysros.ehs - Functions for the event handling system (EHS)](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.ehs)"
    The `pysros.ehs` module is available when executing on SR OS only. On a remote machine, the event handling system (EHS) and its functionality are not supported.



## Tasks
**You should read these tasks from top-to-bottom before beginning the activity.**</p>
It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.


In the upcoming tasks, you will set up logic that will react to an event and drive an automated response. You will then raise a `custom event log` containing specific parameters, simulating a monitoring system's function in generating a tailored alert except now there is no need for any additional elements to call your Python application. The raised event itself will act as the trigger for your Python application, which will use the supplied parameters to configure a VPRN service for debugging purposes.

### EHS Configuration

In this task we will ensure the event handling system is ready to respond to an event. The infrastructure of the EHS is already configured on :material-router: PE2 so that we can focus on the main goal of this activity; in the upcoming tasks you can develop your pySROS code on your group's hackathon VM, under the location</p> `/home/nokia/SReXperts/activities/nos/sros/activity-09/ehs_basic.py`

This same `ehs_basic.py` file has been made available within :material-router:PE2 via container binds.

??? note
    In the Hackathon environment the `/home/nokia/clab-srexperts/pe2/tftpboot/` directory on your groups Hackathon VM is made available using TFTP to the node `PE2`.  Any file you put in that folder will be accessible from within SR OS using TFTP. This could be used as an alternative to `scp` or manually copying over file contents for containerlab environnments.


Any modifications you make to that file in your group's hackathon VM will be visible to the router, this is the preferred method of development as it allows you to modify the file under the Linux filesystem while being able to test on the containerlab node.


!!! info "Connect to :material-router:PE2 from your group's hackathon VM"
    ssh admin@clab-srexperts-pe2

In the box below you see that the full configuration for setting up the EHS on the node has already been prepared for you. However, the second step (creating a directory to store the `python-script` execution results) must be performed manually by you before continuing with the tasks.

??? note "EHS Configuration"
    1- python-script location
    ```
    configure {
        python {
            python-script "ehs_basic" {
                admin-state enable
                urls ["tftp://172.31.255.29/ehs_basic.py"]
                version python3
            }
        }
    ```
    2-make-directory for ehs execution results
    ```
    /file make-directory cf3:/results_ehs_basic/
    ```
    3-script-policy for enabling system to use pySROS script for event handling
    ```
    configure {
        system {
            script-control {
                script-policy "ehs_basic" owner "TiMOS CLI" {
                    admin-state enable
                    results "cf3:/results_ehs_basic/"
                    python-script {
                        name "ehs_basic"
                    }
                }
            }
        }
    ```
    4-filter logs intended to trigger the event handler
    ```hl_lines="9"
    configure {
        log {
            filter "custom-event-4" {
                default-action drop
                named-entry "custom-event-4" {
                    action forward
                    match {
                        event {
                            eq 2023
                        }
                    }
                }
            }
        }

    ```
    5-event-handler links the script-policy to the ehs that can be triggered by logs
    ```
    configure {
        log {
            event-handling {
                handler "ehs_basic" {
                    admin-state enable
                    entry 10 {
                        script-policy {
                            name "ehs_basic"
                            owner "admin"
                        }
                    }
                }
            }
        }

    ```
    6-event-trigger links the filtered logs to the event-handler
    ```
    configure {
        log {
            event-trigger {
                logger event tmnxCustomEvent4 {
                    admin-state enable
                    entry 10 {
                        admin-state enable
                        filter "custom-event-4"
                        handler "ehs_basic"
                    }
                }
            }
        }

    ```
Before proceeding, execute the command to create a results directory on :material-router: PE2 before you continue:

 ```bash
 /file make-directory cf3:/results_ehs_basic/
 ```

In the EHS configuration on :material-router: PE2, the `event-id = 2023` is equivalent to `tmnxCustomEvent4` with `Warning` severity.  This is used to trigger the EHS to perform an action as shown in the configuration above.

The pre-configured EHS configuration can be verified and inspected using following commands. Ensure your environment matches the example outputs.

!!! success "EHS Configuration Verification"
    /// tab | python-script

    ``` bash hl_lines="8"
    A:admin@g15-pe2# show python python-script "ehs_basic"

    ===============================================================================
    Python script "ehs_basic"
    ===============================================================================
    Description   : (Not Specified)
    Admin state   : inService
    Oper state    : inService
    Oper state
    (distributed) : inService
    Version       : python3
    Action on fail: drop
    Protection    : none
    Primary URL   : tftp://172.31.255.29/ehs_basic.py
    Secondary URL : (Not Specified)
    Tertiary URL  : (Not Specified)
    Active URL    : primary
    Run as user   : (Not Specified)
    Code size     : 47
    Last changed  : 04/14/2025 15:30:59
    ===============================================================================

    ```
    ///
    /// tab |  script-policy

    ``` bash hl_lines="9"
    A:admin@g15-pe2# show system script-control script-policy "ehs_basic"

    ===============================================================================
    Script-policy Information
    ===============================================================================
    Script-policy                : ehs_basic
    Script-policy Owner          : TiMOS CLI
    Administrative status        : enabled
    Operational status           : enabled
    Script                       : N/A
    Script owner                 : N/A
    Python script                : ehs_basic
    Source location              : tftp://172.31.255.29/ehs_basic.py
    Results location             : cf3:/results_ehs_basic/
    Max running allowed          : 1
    Max completed run histories  : 1
    Max lifetime allowed         : 0d 01:00:00 (3600 seconds)
    Completed run histories      : 0
    Executing run histories      : 0
    Initializing run histories   : 0
    Max time run history saved   : 0d 01:00:00 (3600 seconds)
    Script start error           : N/A
    Python script start error    : N/A
    Last change                  : 2025/04/14 15:46:41  UTC
    Max row expire time          : never
    Last application             : N/A
    Last auth. user account      : not-specified

    ===============================================================================
    Script Run History Status Information
    -------------------------------------------------------------------------------
    No script run history entries
    ===============================================================================
    ```
    ///
    /// tab |  log filter

    ``` bash hl_lines="16"
    A:admin@g15-pe2# show log filter-id "custom-event-4"

    ===========================================================================
    Log Filter
    ===========================================================================
    Filter-id     : 1        Applied       : no       Default Action: drop
    Filter-name   : custom-event-4
    Description   : (Not Specified)

    -------------------------------------------------------------------------------
    Log Filter Match Criteria
    -------------------------------------------------------------------------------
    Entry-name    : custom-event-4
    Entry-id      : 1                       Action        : forward
    Application   :                         Operator      : off
    Event Number  : 2023                    Operator      : equal
    Severity      : none                    Operator      : off
    Subject       :                         Operator      : off
    Match Type    : exact string                          :
    Message       :
    Match Type    : sub string              Operator      : off
    Router        :                         Operator      : off
    Match Type    : exact string            Operator      : off
    Description   : (Not Specified)
    -------------------------------------------------------------------------------
    ===========================================================================
    ```
    ///
    /// tab |  handler

    ``` bash hl_lines="11 26"
    A:admin@g15-pe2# show log event-handling handler "ehs_basic"

    ===============================================================================
    Event Handling System - Handlers
    ===============================================================================

    ===============================================================================
    Handler          : ehs_basic
    ===============================================================================
    Description      : (Not Specified)
    Admin State      : up                                Oper State : up

    -------------------------------------------------------------------------------
    Handler Execution Statistics
    Success        : 0
    Err No Entry   : 0
    Err Adm Status : 0
    Total            : 0

    -------------------------------------------------------------------------------
    -------------------------------------------------------------------------------
    Handler Action-List Entry
    -------------------------------------------------------------------------------
    Entry-id         : 10
    Description      : (Not Specified)
    Admin State      : up                                Oper State : up
    Script
    Policy Name    : ehs_basic
    Policy Owner   : TiMOS CLI
    Min Delay        : 0
    Last Exec        : never
    -------------------------------------------------------------------------------
    Handler Action-List Entry Execution Statistics
    Success        : 0
    Err Min Delay  : 0
    Err Launch     : 0
    Err Adm Status : 0
    Total            : 0
    ===============================================================================
    ```
    ///

### EHS Output

You may find that it is time-consuming looking through the directories linked to each `script-policy` for any available files that may contain the output of the script-policy you're interested in. Since any script executions triggered by EHS invoke a script-policy, that would be a hurdle to get over any time the policy is executed.

For troubleshooting that is an issue so we are using a Python script that has been prepared as an alias in the :material-router: PE2 node. You can call the command using `/show script-policy-results`. The script itself is available in the Hackathon repo and ready for you to use on :material-router: PE2.

Try the alias with `/show script-policy-results`

??? note "script-policy-results alias"
    ```
    [/]
    A:admin@g15-pe2# /show script-policy-results
    =======================================================================================
    Available script policies
    =======================================================================================
    ID                        Policy Name
    ---------------------------------------------------------------------------------------
    0                         ehs_basic
    ---------------------------------------------------------------------------------------
    No. of defined script policies: 1
    =======================================================================================
    Select the ID of the script to show its latest result: 0
    Directory cf3:/results_ehs_basic/ contains no files.
    ```

Before proceeding with the tasks, take a moment to familiarize yourself with how the command for sending custom events works, including its mandatory and optional parameters.

??? success "perform log custom-event"
    /// tab | event-number

    ``` bash hl_lines="8"
    A:admin@g15-pe2# /perform log custom-event ?

    custom-event

    [event-number] <number>
    <number> - <1..6>

    'event-number' is: mandatory

        Custom event to send

    [event-number]        ^ Custom event to send
    ```
    ///
    /// tab | message-string & subject

    ``` bash hl_lines="5 6"
    A:admin@g15-pe2# /perform log custom-event 6 ?

    custom-event

    message-string        ^ Message for the log event
    subject               ^ Subject of the log event

    ```
    ///
    /// tab | custom parameters

    ``` bash
    A:admin@g15-pe2# /perform log custom-event 6 message-string test-msg-strng subject test-sbjct ?

    custom-event

    parameter1            - Custom text of the parameter
    parameter2            - Custom text of the parameter
    parameter3            - Custom text of the parameter
    parameter4            - Custom text of the parameter
    parameter5            - Custom text of the parameter
    parameter6            - Custom text of the parameter
    parameter7            - Custom text of the parameter
    parameter8            - Custom text of the parameter
    ```
    ///
    /// tab | expected output

    ``` bash hl_lines="1 9 10"
    A:admin@g15-pe2# show log log-id 99

    ===============================================================================
    Event Log 99 log-name 99
    ===============================================================================
    Description : Default System Log
    Memory Log contents  [size=500   next event=3  (not wrapped)]

    2 2025/05/07 08:00:21.540 UTC INDETERMINATE: LOGGER #2025 Base test-sbjct
    "test-msg-strng"

    1 2025/05/07 08:00:15.185 UTC INDETERMINATE: LOGGER #2010 Base Clear LOGGER
    "Clear function clearLogId has been run with parameters: log-id="99" context="".  The completion result is: success.  Additional error text, if any, is: "

    ```
    ///

In the event handling system configuration described in the "Event Handling Script Functionality" section above, we used the event with application-id `{ eq 2023 }`. According to the table at the beginning of the activity, this corresponds to the event named `tmnxCustomEvent4`. Therefore, any occurrence of `CustomEvent4` will trigger the Event Handling System (EHS).

### Custom event log parameters
The first task is to develop a pySROS script in `/home/nokia/SReXperts/activities/nos/sros/activity-09/ehs_basic.py` that prints the parameters passed to the event log. This will help you understand how the input parameters in the command `perform log custom-event` work. In the example solution parameters are given values that would be needed for configuring a VPRN service.

```py title="event-id 2023 : tmnxCustomEvent4" hl_lines="4-11"
Event Specific Parameters
        logCustomEventSubject        --->   log subject
        logCustomEventMessageString  --->   log message
        logCustomEventParameter1     --->   service_name
        logCustomEventParameter2     --->   service_id
        logCustomEventParameter3     --->   interface_name
        logCustomEventParameter4     --->   ipv4_address
        logCustomEventParameter5     --->   ipv4_pfxlen
        logCustomEventParameter6     --->   sap_id
        logCustomEventParameter7     --->   not used
        logCustomEventParameter8     --->   not used

```

??? tip "Sample PySROS script to print the parameters"
    ```py
    from pysros.ehs import get_event
    from pysros.management import connect


    def main():
        connection = connect(
            host="local connection only - unused",
            username="local connection only - unused",
        )

        trigger_event = get_event()
        if not trigger_event:
            return

        if trigger_event.appid == "LOGGER" and trigger_event.eventid == 2023:

            for i in trigger_event.eventparameters:
                print(i)

    if __name__ == "__main__":
        main()
    ```




1. Be sure to reload your source code into the `python-script` object in the memory of the router before you test your changes. The version in memory isn't updated automatically. Use the following command:

    !!! note "reload python-script"
        ```py
        /perform python python-script reload script "ehs_basic"
        ```
   To view the script version currently loaded in memory you can use the following show command:

    !!! note "show python-script in-use"
        ```py
        /show python python-script "ehs_basic" source-in-use
        ```

2. Run the `perform log custom-event` command with the mandatory fields for `event-number` `4`, `subject` and `message-string` and add 6 additional parameters as below:

    - `parameter1` -> Service name
    - `parameter2` -> Service ID
    - `parameter3` -> Interface name
    - `parameter4` -> Interface IP address
    - `parameter5` -> Interface IP prefix length
    - `parameter6` -> Interface SAP

    !!! note "Send a custom log event with service information on :material-router:PE2"
        ``` bash
        /perform log custom-event 4 subject "NEW VPRN CREATION" message-string "CREATE VPRN WITH NEW PARAMETERS" parameter1 new-vprn-name parameter2 400 parameter3 new-int-name parameter4 192.168.6.50 parameter5 24 parameter6 1/1/c6/1:400

        ```

3. If you look at the logs, you will find an event with `application-id` **LOGGER** and `event-id` **2023** with the provided `subject` and  `message-string`.

    /// tab | show log

    ``` bash
    A:admin@g15-pe2# show log log-id 99 | match LOGGER post-lines 1
    67 2025/04/01 12:33:54.843 UTC WARNING: LOGGER #2023 Base NEW VPRN CREATION
    "CREATE VPRN WITH NEW PARAMETERS"

    ```
    ///

4. You can use the EHS output alias command described in the "EHS Output" section above to look at the result of the script executed by the EHS.

    /// tab | show script-policy-results

    ``` bash hl_lines="1 11"
    A:admin@g15-pe2# show script-policy-results
    =======================================================================================
    Available script policies
    =======================================================================================
    ID                        Policy Name
    ---------------------------------------------------------------------------------------
    0                         ehs_basic
    ---------------------------------------------------------------------------------------
    No. of defined script policies: 1
    =======================================================================================
    Select the ID of the script to show its latest result: 0
    >>> Showing output for script policy ehs_basic from cf3:/results_ehs_basic/_20250507-081059-UTC.076278.out

    ('logCustomEventSubject', 'NEW VPRN CREATION')
    ('logCustomEventMessageString', 'CREATE VPRN WITH NEW PARAMETERS')
    ('logCustomEventParameter1', 'new-vprn-name')
    ('logCustomEventParameter2', '400')
    ('logCustomEventParameter3', 'new-int-name')
    ('logCustomEventParameter4', '192.168.6.50')
    ('logCustomEventParameter5', '24')
    ('logCustomEventParameter6', '1/1/c6/1:400')
    ('logCustomEventParameter7', '')
    ('logCustomEventParameter8', '')

    ```
    ///


### Use the Parameters of a Custom Event Log for Configuration
Now that you've learned how the parameters of a custom generic event log work, it's time to apply that knowledge in your second task: configuring a new VPRN service using those parameters. </p> Develop a pySROS script to pass the parameters from the "Custom event log parameters" task above to a pySROS [`.set()`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Datastore.set) method to configure a VPRN service.</p> When finished with your code, don't forget to reload the script as mentioned earlier.

**Optional** : As an additional challenge, consider using the pySROS [exceptions](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#module-pysros.exceptions) module to raise a custom event based on the success or failure of the configuration.</p>
For example, a failure may happen if you use a duplicate service-id.

??? tip "Sample PySROS script to configure with EHS"
    ```py
    from pysros.ehs import get_event
    from pysros.exceptions import SrosMgmtError
    from pysros.management import connect


    def raise_custom_event(connection, event_num, event_sub, event_msg):
        #Function to raise custom event log

        path = "/nokia-oper-perform:perform/log/custom-event"
        payload = {
            "event-number": event_num,
            "subject": event_sub,
            "message-string": event_msg,
        }
        connection.action(path, payload)


    def main():
        #The main procedure. The execution starts here.
        connection = connect(
            host="local connection only - unused",
            username="local connection only - unused",
        )

        trigger_event = get_event()
        if not trigger_event:
            return

        if trigger_event.appid == "LOGGER" and trigger_event.eventid == 2023:
            #eventid 2023 triggers the ehs

            for i in trigger_event.eventparameters:
                #print the parameters passed through the custom event log
                print(i)

            service_name = trigger_event.eventparameters["logCustomEventParameter1"]
            service_id = trigger_event.eventparameters["logCustomEventParameter2"]
            interface_name = trigger_event.eventparameters["logCustomEventParameter3"]
            ipv4_address = trigger_event.eventparameters["logCustomEventParameter4"]
            ipv4_pfxlen = trigger_event.eventparameters["logCustomEventParameter5"]
            sap_id = trigger_event.eventparameters["logCustomEventParameter6"]

            path = "/nokia-conf:configure/service"
            #use the parameters as payload for VPRN configuration
            payload = {
                "vprn": {
                    "service-name": "%s" % service_name,
                    "admin-state": "enable",
                    "service-id": int(service_id),
                    "customer": "1",
                    "interface": {
                        "interface-name": "%s" % interface_name,
                        "admin-state": "enable",
                        "ipv4": {
                            "primary": {
                                "address": "%s" % ipv4_address,
                                "prefix-length": int(ipv4_pfxlen),
                            }
                        },
                        "sap": {"sap-id": "%s" % sap_id},
                    },
                }
            }

            connection.candidate.set(path, payload, commit=False)

            print(
                "Comparison output:\n%s"
                % connection.candidate.compare(output_format="md-cli")
            )

            try:
                connection.candidate.set(path, payload, commit=True)
                event_msg = (
                    "VPRN service with service-id ["
                    + service_id
                    + "] is created successfully"
                )
                #raise custom event log if succeeded
                raise_custom_event(
                    connection, 2, "EHS Script Successful", event_msg
                )

            except SrosMgmtError as e:
                event_msg = str(e)
                #raise custom event log if failed
                raise_custom_event(connection, 2, "EHS Script Failed", event_msg)

            print(event_msg)


    if __name__ == "__main__":
        main()

    ```
!!! example "Example with successful service creation"
    /// tab | perform log with new parameters
    ``` bash
    perform log custom-event 4 subject "NEW VPRN CREATION" message-string "CREATE VPRN WITH NEW PARAMETERS" parameter1 new-vprn-name parameter2 400 parameter3 new-int-name parameter4 192.168.6.50 parameter5 24 parameter6 1/1/c6/1:400
    ```
    ///
    /// tab | show log

    ``` bash hl_lines="9 10 27 28"
    A:admin@g15-pe2# show log log-id 99

    ===============================================================================
    Event Log 99 log-name 99
    ===============================================================================
    Description : Default System Log
    Memory Log contents  [size=500   next event=9  (not wrapped)]

    8 2025/04/01 12:47:58.072 UTC MAJOR: LOGGER #2021 Base EHS Script Successful
    "VPRN service with service-id [400] is created successfully"

    7 2025/04/01 12:47:58.070 UTC WARNING: SYSTEM #2121 Base Commit
    "Commit to configure by  (Cron/EHS) from Cron/EHS succeeded."

    6 2025/04/01 12:47:58.067 UTC WARNING: SNMP #2005 vprn400 new-int-name
    "Interface new-int-name is operational"

    5 2025/04/01 12:47:58.067 UTC MINOR: SVCMGR #2108 vprn400
    "Status of interface new-int-name in service 400 (customer 1) changed to admin=up oper=up"

    4 2025/04/01 12:47:58.057 UTC MINOR: SVCMGR #2103 vprn400
    "Status of service 400 (customer 1) changed to administrative state: up, operational state: up"

    3 2025/04/01 12:47:58.009 UTC MINOR: SYSTEM #2069 Base EHS script
    "Ehs handler :"ehs_basic" with the description : "" was invoked by the cli-user account "not-specified"."

    2 2025/04/01 12:47:58.009 UTC WARNING: LOGGER #2023 Base NEW VPRN CREATION
    "CREATE VPRN WITH NEW PARAMETERS"

    ```
    ///
    /// tab | show script-policy-results

    ``` bash
    A:admin@g15-pe2# show script-policy-results
    =======================================================================================
    Available script policies
    =======================================================================================
    ID                        Policy Name
    ---------------------------------------------------------------------------------------
    0                         ehs_basic
    ---------------------------------------------------------------------------------------
    No. of defined script policies: 1
    =======================================================================================
    Select the ID of the script to show its latest result: 0
    >>> Showing output for script policy ehs_basic from cf3:/results_ehs_basic/_20250507-081856-UTC.882935.out

    ('logCustomEventSubject', 'NEW VPRN CREATION')
    ('logCustomEventMessageString', 'CREATE VPRN WITH NEW PARAMETERS')
    ('logCustomEventParameter1', 'new-vprn-name')
    ('logCustomEventParameter2', '400')
    ('logCustomEventParameter3', 'new-int-name')
    ('logCustomEventParameter4', '192.168.6.50')
    ('logCustomEventParameter5', '24')
    ('logCustomEventParameter6', '1/1/c6/1:400')
    ('logCustomEventParameter7', '')
    ('logCustomEventParameter8', '')
    Comparison output:
    configure {
            service {
    +           vprn "new-vprn-name" {
    +               admin-state enable
    +               service-id 400
    +               customer "1"
    +               interface "new-int-name" {
    +                   admin-state enable
    +                   ipv4 {
    +                       primary {
    +                           address 192.168.6.50
    +                           prefix-length 24
    +                       }
    +                   }
    +                   sap 1/1/c6/1:400 {
    +                   }
    +               }
    +           }
            }
        }
    VPRN service with service-id [400] is created successfully

    ```
///

!!! example "Example with failed service creation"
    /// tab | perform log with duplicate service-id

    ``` bash
     perform log custom-event 4 subject "NEW VPRN CREATION" message-string "CREATE VPRN WITH DUPLICATE SERVICE-ID" parameter1 new-vprn-name-2 parameter2 400 parameter3 new-int-name-2 parameter4 192.168.7.50 parameter5 24 parameter6 1/1/c6/1:402

    ```

    ///
    /// tab | show log

    ``` bash hl_lines="9 10 15 16"
    A:admin@g15-pe2# show log log-id 99

    ===============================================================================
    Event Log 99 log-name 99
    ===============================================================================
    Description : Default System Log
    Memory Log contents  [size=500   next event=12  (not wrapped)]

    11 2025/05/07 08:20:34.551 UTC MAJOR: LOGGER #2021 Base EHS Script Failed
    "MINOR: MGMT_CORE #5001: configure service vprn "new-vprn-name-2" - vprn service new-vprn-name also has id 400 - configure service vprn "new-vprn-name""

    10 2025/05/07 08:20:34.528 UTC MINOR: SYSTEM #2069 Base EHS script
    "Ehs handler :"ehs_basic" with the description : "" was invoked by the cli-user account "not-specified"."

    9 2025/05/07 08:20:34.528 UTC WARNING: LOGGER #2023 Base NEW VPRN CREATION
    "CREATE VPRN WITH DUPLICATE SERVICE-ID"

    ```
    ///
    /// tab | show script-policy-results

    ``` bash
    A:admin@g15-pe2# show script-policy-results                                                                                                                                                                             =======================================================================================
    Available script policies
    =======================================================================================
    ID                        Policy Name
    ---------------------------------------------------------------------------------------
    0                         ehs_basic
    ---------------------------------------------------------------------------------------
    No. of defined script policies: 1
    =======================================================================================
    Select the ID of the script to show its latest result: 0
    >>> Showing output for script policy ehs_basic from cf3:/results_ehs_basic/_20250507-082034-UTC.528552.out

    ('logCustomEventSubject', 'NEW VPRN CREATION')
    ('logCustomEventMessageString', 'CREATE VPRN WITH DUPLICATE SERVICE-ID')
    ('logCustomEventParameter1', 'new-vprn-name-2')
    ('logCustomEventParameter2', '400')
    ('logCustomEventParameter3', 'new-int-name-2')
    ('logCustomEventParameter4', '192.168.7.50')
    ('logCustomEventParameter5', '24')
    ('logCustomEventParameter6', '1/1/c6/1:402')
    ('logCustomEventParameter7', '')
    ('logCustomEventParameter8', '')
    Comparison output:
    configure {
            service {
    +           vprn "new-vprn-name-2" {
    +               admin-state enable
    +               service-id 400
    +               customer "1"
    +               interface "new-int-name-2" {
    +                   admin-state enable
    +                   ipv4 {
    +                       primary {
    +                           address 192.168.7.50
    +                           prefix-length 24
    +                       }
    +                   }
    +                   sap 1/1/c6/1:402 {
    +                   }
    +               }
    +           }
            }
        }
    MINOR: MGMT_CORE #5001: configure service vprn "new-vprn-name-2" - vprn service new-vprn-name also has id 400 - configure service vprn "new-vprn-name"

    ```
///


## Summary

Congratulations! If you've made it this far you have completed this activity and achieved the following:

- You have seen how EHS can be configured to handle events.
- You have used the MD-CLI to send custom events.
- You have executed Python applications on SR OS
- You have added your own parameters to custom events.
- You have made the system react to event via the EHS.
- You have observed EHS making configuration changes based on the event parameters.

This use-case illustrates a practical example of network self-healing, where an `event` triggers a pre-scripted, intelligent configuration workflow all without any outside intervention.

Do you want to extend your pySROS script? You could think about repurposing `tmnxCustomEvent4` for something else you have in mind or you could try to add a different action to be performed for a different event. An example could be to let the script configured for `tmnxCustomEvent4` send out a custom event `tmnxCustomEvent3` with parameters to add another interface, add route-target configuration or set up a PE-CE routing protocol in the VPRN.

Interested in the `script-policy-results` implementation? Check out usecase [Script (policy) results browsing made easy](../intermediate/nos-sros-activity-62.md) in the SR OS section.
