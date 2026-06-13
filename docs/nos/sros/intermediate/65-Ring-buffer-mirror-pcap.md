---
tags:
  - Service Mirror
  - PCAP
  - pySROS
  - SR OS
  - MD-CLI
  - RMON
  - gNMIc
  - EHS

---

# Ring Buffer Mirror PCAP


|                             |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Activity name**           | Ring buffer mirror pcap to local router filesystem                                                                                                                                                                                                                                                                                                                                                                                                                         |
| **Activity ID**           | 65                                                                                                                                                                                                                                                                                                                                                                   |
| **Short Description**       | Implement a pySROS script to monitor and automatically rotate pcap files saved at local filesystem                                                                                                                                                                                                                                                                                                                                                      |
| **Difficulty**              |   Intermediate                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **Tools used**              | [SR OS](https://www.nokia.com/ip-networks/service-router-operating-system-nos/)<br/>[Model-Driven CLI (MD-CLI)](https://documentation.nokia.com/sr/26-3/7750-sr/titles/md-cli-user.html)<br/>[pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/introduction.html)<br/>[Python programming language](https://www.python.org/)                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| **Topology Nodes**          | :material-router: P2                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **References**              | [pySROS](https://network.developer.nokia.com/static/sr/learn/pysros/latest/introduction.html)<br/>[Nokia YANG browser](https://yangbrowser.nokia.com/sros/26.3.R1?from=0)<br/>[Mirror Services](https://documentation.nokia.com/sr/26-3/7750-sr/books/oam-diagnostics/mirror-services.html)<br/>[SR OS Event handling system (EHS)](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/event-account-logs.html#ai9exj5x1x)</br> [SR OS RMON](https://documentation.nokia.com/sr/26-3/7x50-shared/basic-system-configuration/system-management.html#ai9entl9f3)</br>[SR OS gNMI](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/grpc.html)<br/>[gNMIc](https://gnmic.openconfig.net)


As a Network Operator, you may deal with unexpected spikes in the ingress or egress QoS queues used by network interfaces or service SAPs on a router. One effective troubleshooting method is to use the SR OS  mirror feature to capture traffic to a pcap file in order to identify the source and type of the unexpected traffic.

If external FTP or SFTP servers are unavailable, the captures can be stored locally on a Compact Flash (CF) card (other than CF3 that is reserved for system files). However, this approach introduces the risk of exhausting the card’s disk space before the offending traffic is captured.

With pySROS, you can automate the monitoring and management of the pcap files stored on the CF card.

## Objective

You are a network engineer investigating the origin of network-control traffic that occasionally spikes (for about 100 milliseconds) at high-rate on network interface which causes service impact across your network. You would like to perform a packet-capture to inspect a sample of the offending traffic. Because it is logistically hard to install a dedicated sniffer device, and remote-mirroring is not a possibility due to bandwidth constraints, you have decided to mirror the traffic to a pcap onto the local router CF.  

You already have identified a P router where this traffic is seen spiking, configured a mirror-pcap to continuously save the traffic on the local router filesystem and an EHS script that stops the capture once a spike is detected. However, because the spike is rare and random, the mirror-pcap quickly fills the entire filesystem space and the pcap-mirror stops before the issue is seen. 

Your goal is to configure an automated way to limit the max filesystem-usage by the mirror-pcap, while keeping the most recent captured traffic.  

## Technology explanation

### Packet capture (PCAP)

Packet capture is a troubleshooting technique that combines traffic mirroring and analysis.  
In SR OS, traffic mirroring to a PCAP file allows ingress or egress packets to be captured and stored in PCAP format for detailed inspection.  
Using pySROS, it is possible to automate and monitor PCAP file sizes, helping to prevent local disk space exhaustion when continuous packet capture is required.  

### Service Mirroring
Mirroring in SR OS is a monitoring feature that copies packets from a SAP, port, filter or subscriber, and sends them to a destination for troubleshooting, lawful intercept, or traffic analysis.

### Event Handling System (EHS)
The Event Handling System (EHS) is a framework that allows user-defined behavior to be configured on the router.  
EHS adds user-controlled programmatic exception handling by allowing the execution of either a CLI script or a Python 3 application when a log event (the ‟trigger”) is detected.  
Various fields in the log event provide regexp style expression matching, which allows flexibility for the trigger definition.  
Here the EHS will trigger the stop condition for the PCAP based on the customized RMON event.  

### Remote Network Monitoring (RMON)
Remote Network Monitoring (RMON) on Nokia SR OS provides a framework for configuring generic alarms and events based on SNMP MIB object thresholds.  
The customized event for this task will count `port network egress octets` and trigger an event log based on defined thresholds.  

For more details about SNMP consult the [SR OS System Management Guide](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/snmp.html#ariaid-title1). 

### CRON
CRON is a feature in SR OS that supports periodic and date/time-based scheduling. It can be used to automate a wide range of tasks, including:   

  - Scheduling Service Assurance Agent (SAA) functions
  - Scheduled reboots
  - Peer turn-ups
  - OAM events (connectivity checks, troubleshooting runs)
  - Exporting statistics or accounting data to external servers
  - Execute pySROS script

#### Schedule Types   

The schedule element supports three types of runs:      

  | Type     | Description |
  |:--------:|:------------|
  | One-shot | Runs only once |
  | Periodic | Runs at a defined interval (in seconds) |
  | Calendar | Runs based on month, day of month, weekday, hour, and minute |  

If both end-time and interval are configured, whichever condition is reached first applies. Consult the [SR OS System Management Guide](https://documentation.nokia.com/sr/26-3/7x50-shared/basic-system-configuration/system-management.html#ariaid-title40) for more details.

### Python
[MicroPython](https://docs.micropython.org/en/v1.10/library/index.html) is the interpreter that SR OS runs locally. This interpreter implements Python 3.4 (with some extensions from Python 3.5 and 3.6) and is designed to operate using a small memory footprint.  

Consider this when writing your code that you specifically want to run on SR OS. For example, if you are used to using f-strings in your work you will find that they work on your machine but when you transfer your script to the node they will fail.

Documentation for the Python 3.4 language can be found [here](https://docs.python.org/3.4/).


### pySROS
The pySROS libraries provide a model-driven management interface for Python developers to integrate with any router (from any vendor) that supports NETCONF and YANG-library according to the IETF standards.  Nokia routers including those running the Service Router Operating System (SR OS) and SR Linux are supported.

The libraries provide an Application Programming Interface (API) for developers to create applications that can interact with network devices.  In addition, Nokia SR OS devices allow operators to run Python applications directly on the router.

When a developer uses only libraries and constructs supported on SR OS, a single application may be executed from a development machine or ported directly to an SR OS node where the application is executed without modification.


#### Establishing a pySROS connection
When developing a Python script using pySROS, a connection must always be established to the SR OS device. This is done using the [connect](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.connect) function, which can be used both locally, when executing the script on SR OS, or from a remote environment.
For this activity, Python script will be used locally on SR OS.


/// details | Establishing a pySROS connection
    type: tip

``` python
from pysros.management import connect

c = connect()

```
///

#### Finding state info with pySROS
To find the data you are looking for, login to your node and enter the state tree by typing `state` at the CLI. Use the `tree` command or question mark to navigate your way around. Type `info` to see the data in that path. Once you have found the final path of data you are interested in issue the command `pwc json-instance-path` whilst in that context to get a path string you can use in your Python code.


/// Details | Example

//// Tab| Configure
``` hl_lines="2 4"
[ex:/configure log log-id "50"]
A:admin@g3-p2# pwc json-instance-path 
Present Working Context:
/nokia-conf:configure/log/log-id[name="50"]
```
////
///// Tab| State
``` hl_lines="2 4"
[/state system alarms]
A:admin@g3-p2# pwc json-instance-path 
Present Working Context:
/nokia-state:state/system/alarms
```
/////
///

You can also use the [MD-CLI](https://documentation.nokia.com/sr/26-3/7750-sr/titles/md-cli-user.html) and [Nokia YANG browser](https://yangbrowser.nokia.com/sros/26.3.R1?from=0) to find the path information you are interested in.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  


/// warning

In SR OS devices the local CF3 is reserved for system files and it is operational best practice not to use it for any other files.  

Storing non-system files (for example, large log and accounting files) on CF3 can consume space required for critical system files such as the configuration file (`config.cfg`), boot images (`*.tim`), and debug files (`debug.cfg`). Consequently, CF3 is not recommended for storing large files like pcap captures.  

This activity runs in a simulated environment and you will use local CF3 to store the Mirror pcap files.  
In real deployments, depending on the SR OS router model, you can use CF1, CF2, or a USB device to safely store pcap files, logs, or debug data.
For pcap captures, it is strongly recommended to use an external SFTP server, which provides far greater storage capacity than local CF cards.  
///


### Startup configuration
Before you start, you need to run a script from your hackathon instance to apply the configurations at :material-router: P2 required for this task.  

The config will mirror :material-router: P2 network port `1/1/c3/1` towards :material-router: PE3 to a PCAP file named `test.pcap` saved locally at CPM CF3.  

Use the command below to create the config for EHS and RMON.  

/// details | Startup configuration location
    type: success
    open: true

From the home directory run the startup config setup file at `~/SReXperts/activities/activity-65/startup-65.sh`.  

```bash 
bash ~/SReXperts/activities/activity-65/startup-65.sh
```
///   

#### Connect to the CLI on :material-router: P2

Use the MD-CLI commands to inspect the mirror config/status.   

/// tab| Connect to :material-router: P2 
```
ssh admin@clab-srexperts-p2
```
///

/// tab| Configuration validation
```
show mirror mirror-dest "test-pcap"
```
```
show mirror mirror-source "test-pcap"
```
```
show pcap "test" detail
```
///

For more details about mirror usage and configuration consult the user guide [Mirror Service](https://documentation.nokia.com/sr/26-3/7750-sr/books/oam-diagnostics/mirror-services.html) section.

/// details| Sample output.
    type: tip

/// tab| show mirror mirror-dest   

```bash
===============================================================================
Mirror Service
===============================================================================
Service Id       : 500                  Type          : ETH
Service Name     : test-pcap
Description      : (Not Specified)
Admin State      : Up                   Oper State    : Up
Forwarding Class : be                   Remote Sources: No
Slice            : 256                  
Sampling Rate    : None                 
Pcap Sess Name   : test                 
Use Global Sampl*: No                   
Per-Flow Hashing : No                   
-------------------------------------------------------------------------------
Legend: ETH = Ether, IPO = Iponly, UNK = Unknown

===============================================================================
Mirror Services SDP
===============================================================================
SdpId IP Addr         CfgEgrLbl  OprEgrLbl  Signal RemSrc CfgIngLbl  OprIngLbl
-------------------------------------------------------------------------------
No Matching Entries
===============================================================================
 
-------------------------------------------------------------------------------
Local Sources
-------------------------------------------------------------------------------
Admin State      : Up                   
Source Origin    : config               
Total Sources    : 1                    
 
-Port                                      1/1/c3/1                         Ing
===============================================================================
* indicates that the corresponding row element may have been truncated.
```
///   
    
/// tab| show mirror-source   

```bash
===============================================================================
Mirror Service
===============================================================================
Service Id       : 500                  Type          : ETH
Service Name     : test-pcap
Description      : (Not Specified)
Admin State      : Up                   Oper State    : Up
Forwarding Class : be                   Remote Sources: No
Slice            : 256                  
Sampling Rate    : None                 
Pcap Sess Name   : test                 
Use Global Sampl*: No                   
Per-Flow Hashing : No                   
-------------------------------------------------------------------------------
Legend: ETH = Ether, IPO = Iponly, UNK = Unknown

===============================================================================
Mirror Services SDP
===============================================================================
SdpId IP Addr         CfgEgrLbl  OprEgrLbl  Signal RemSrc CfgIngLbl  OprIngLbl
-------------------------------------------------------------------------------
No Matching Entries
===============================================================================
 
-------------------------------------------------------------------------------
Local Sources
-------------------------------------------------------------------------------
Admin State      : Up                   
Source Origin    : config               
Total Sources    : 1                    
 
-Port                                      1/1/c3/1                         Ing
===============================================================================
* indicates that the corresponding row element may have been truncated.
```
///    
 
/// tab| show pcap detail   

```bash
===============================================================================
Pcap Session "test" Information
===============================================================================
Application Type   : mirror-dest        Session State   : ready
Capture            : stop               Last Changed    : 04/21/2026 10:03:54
Capture File Url   : ftp://*:*@10.128.3.12/cf3:/test.pcap
                                                                               
Router Instance    : management
                                                                               
Buffer Size        : 0 Bytes            File Size       : 0 Bytes
Write Failures     : 0                  Read Failures   : 0
Proc Time Bailouts : 0                  Last File Write : 05/11/2026 13:17:47
Dropped Packets    : 0 Packets          Captured Packets: 0 Packets
===============================================================================
```
///

///   

Use the MD-CLI commands to inspect the RMON config/status.    
```
show system thresholds type alarm   
```

For more details about RMON usage and configuration consult the [RMON](https://documentation.nokia.com/sr/26-3/7x50-shared/basic-system-configuration/system-management.html#ai9entl9f3) guide.

/// details| Sample output.
    type: tip

/// tab| show system thresholds type alarms 

```bash
=================================================================
Threshold Alarms
=================================================================
Variable: tmnxPortNetEgressFwdInProfOcts.1.1647313089.8   <---- SNMP MIB object - port network egreess qos queue 8 (nc)
Alarm Id         : 1000     Last Value : 2593
Rising Event Id  : 1000     Threshold  : 10000
Falling Event Id : 200      Threshold  : 5000
Sample Interval  : 30       SampleType : delta
Startup Alarm    : either   Owner      : TiMOS CLI
 
=================================================================
```
///
///

Use the MD-CLI command to inspect EHS configs/status

```
show system script-control script "stop-pcap"
```
```
show system script-control script-policy "spolicy-stop-pcap"
```
```
show log filter-id 200
```
```
show log event-handling handler "handler-stop-pcap"
```

For more details about EHS usage and configuration consult the [EHS](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/event-account-logs.html#ai9exj5x1x) guide.  

/// details | Sample output
    type: tip  

/// tab | show system script-control script   

```bash
===============================================================================
Script Information
===============================================================================
Script                       : stop-pcap
Owner name                   : TiMOS CLI
Description                  : none
Administrative status        : enabled
Operational status           : enabled
Script source location       : cf3:/stop-pcap.txt
Last script error            : none
Last change                  : 2026/05/11 10:51:52  UTC
 
===============================================================================
```
///   

/// tab | show system script-control script-policy    

```bash
===============================================================================
Script-policy Information
===============================================================================
Script-policy                : spolicy-stop-pcap
Script-policy Owner          : TiMOS CLI
Administrative status        : enabled
Operational status           : enabled
Script                       : stop-pcap
Script owner                 : TiMOS CLI
Python script                : N/A
Source location              : cf3:/stop-pcap.txt
Results location             : cf3:/results
Max running allowed          : 1
Max completed run histories  : 10
Max lifetime allowed         : 0d 01:00:00 (3600 seconds)
Completed run histories      : 0
Executing run histories      : 0
Initializing run histories   : 0
Max time run history saved   : 0d 01:00:00 (3600 seconds)
Script start error           : N/A
Python script start error    : N/A
Last change                  : 2026/05/11 10:51:52  UTC
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

/// tab| show log filter-id   

```bash
===========================================================================
Log Filter
===========================================================================
Filter-id     : 200      Applied       : no       Default Action: drop
Filter-name   : 200
Description   : (Not Specified)
 
-------------------------------------------------------------------------------
Log Filter Match Criteria
-------------------------------------------------------------------------------
Entry-name    : nc-spike
Entry-id      : 1                       Action        : forward
Application   :                         Operator      : off
Event Number  : 0                       Operator      : off
Severity      : none                    Operator      : off
Subject       :                         Operator      : off
Match Type    : exact string                          : 
Message       : tmnxPortNetEgressFwdInProfOcts
Match Type    : regular expression      Operator      : equal
Router        :                         Operator      : off
Match Type    : exact string            Operator      : off
Description   : (Not Specified)
-------------------------------------------------------------------------------
===========================================================================
```
///  

/// tab| show log event-handling handler   

```bash
===============================================================================
Event Handling System - Handlers
===============================================================================
 
===============================================================================
Handler          : handler-stop-pcap
===============================================================================
Description      : (Not Specified)
Admin State      : up                                Oper State : up
 
-------------------------------------------------------------------------------
Handler Execution Statistics
  Success        : 3                                 
  Err No Entry   : 0                                 
  Err Adm Status : 0                                 
Total            : 3                                 
 
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
Handler Action-List Entry
-------------------------------------------------------------------------------
Entry-id         : 10                                
Description      : (Not Specified)
Admin State      : up                                Oper State : up
Script
  Policy Name    : spolicy-stop-pcap                 
  Policy Owner   : TiMOS CLI                         
Min Delay        : 0                                 
Last Exec        : 05/11/26 19:31:31 UTC             
-------------------------------------------------------------------------------
Handler Action-List Entry Execution Statistics
  Success        : 3                                 
  Err Min Delay  : 0                                 
  Err Launch     : 0                                 
  Err Adm Status : 0                                 
Total            : 3                                 
===============================================================================
```
///
///

### Start the pcap mirror   

Run the following command from :material-router: P2 MD-CLI to start the mirror pcap. 

```
perform pcap "test" capture start
```
If the MD-CLI command is applied without any error, then the show pcap state is `in-progress`.

/// details| Expected output.
    type: tip

```bash
A:admin@g3-p2# perform pcap "test" capture start

A:admin@g3-p2# show pcap detail                  

===============================================================================
Pcap Session "test" Information
===============================================================================
Application Type   : mirror-dest        Session State   : in-progress
Capture            : start              Last Changed    : 04/21/2026 10:03:54
Capture File Url   : ftp://*:*@10.128.2.12/cf3:/test.pcap
                                                                               
Router Instance    : management
                                                                               
Buffer Size        : 180 Bytes          File Size       : 131 Bytes
Write Failures     : 0                  Read Failures   : 0
Proc Time Bailouts : 0                  Last File Write : 05/11/2026 13:21:04
Dropped Packets    : 0 Packets          Captured Packets: 1 Packets
===============================================================================
```
///

### Prepare a pySROS script to monitor the mirror pcap state and file size

Now that a mirror pcap is running let's think about the pySROS script requirements and preparation.

Consider including in your script:

 - Monitor pcap state
 - Monitor pcap file size (30KB)
 - If pcap size limit is reached then stop pcap and perform pcap file rollover to pcap.1
 - Restart pcap (with original file name)


/// details | Script location
    type: tip

You can develop the script under your hackathon instance folder `~/SReXperts/clab/clab-srexperts/p2/A/config/cf3`. This folder contents are accessible from :material-router: P2 node via `cf3:/`.  
For instance, if you create a script in `~/SReXperts/clab/clab-srexperts/p2/A/config/cf3/my.py`, you can run it on :material-router:P2 using `pyexec cf3:/my.py`.

///


/// details| Stop and take time to think here
    type: question
    
Think here how would you implement this pySROS script?

 - You need to know how to obtain the state of mirror pcap and the pcap file size. Can you login to MD-CLI and go into the state tree and find a good state leaf that provides this information?  
 - You will need to stop and restart the mirror pcap consult [pySROS documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Connection.cli) `connection.cli()` details how to execute cli commands with python scripts.  


///
#### pySROS connect

Consult the [documentation](https://network.developer.nokia.com/static/sr/learn/pysros/26.3.1/index.html) for details on how to establish a pySROS connection.  

See the example below for how to use `connect()` and `get` system name.

/// details| Sample pySROS `connect` and `get` system name 
    type: success

```python
from pysros.management import connect
connection_object = connect()
pysros_ds = connection_object.running.get("/nokia-conf:configure/system/name")
print(pysros_ds)
```
///

### pySROS `connect()` `get` mirror state and mirror size

Start developing your pySROS script by fetching the mirror pcap state and the file-size.  
  
You can run from :material-router: P2 in the MD-CLI with `pyexec` to run/test your script.
```bash
pyexec cf3:/my.py
```

You will need to find the correct path for the mirror pcap to fetch the correct data. 

Consult the [finding state info with pySROS](http://localhost:8001/nos/sros/intermediate/65-Ring-buffer-mirror-pcap/#finding-state-info-with-pysros) section above for instructions.

When you are done run/test the script you created with `pyexec`.  

/// details | Solution (read only if you need assistance)
    type: success

```python
from pysros.management import connect
connection_object = connect()
state=connection_object.running.get("/nokia-state:state/mirror/mirror-dest[service-name='test-pcap']/pcap[session-name='test']/session-state")
size=connection_object.running.get("/nokia-state:state/mirror/mirror-dest[service-name='test-pcap']/pcap[session-name='test']/file-size")
print("Session state: {0}, size: {1} bytes".format(state, size))
```
///

### pySROS stop and start pcap

Add to your script the pcap file start and stop actions.

You will need pySROS module [`connection.cli()`](https://network.developer.nokia.com/static/sr/learn/pysros/latest/pysros.html#pysros.management.Connection.cli) to run MD-CLI commands trough python script.


Use the following CLI command to stop pcap:

```
perform pcap "test" capture stop   
```

Use the following CLI command to start pcap:

```
perform pcap "test" capture start   
```

When you are done run/test the script with the additions with `pyexec`.

To proceed to the next task, the mirror pcap last state should be `in-progress`.

Monitor the mirror pcap state with your script and show the result with the following CLI show command:

```
show pcap "test"
```

/// details | Solution (read only if you need assistance)
    type: success

```python
from pysros.management import connect
import time
connection_object = connect()
state=connection_object.running.get("/nokia-state:state/mirror/mirror-dest[service-name='test-pcap']/pcap[session-name='test']/session-state")
size=connection_object.running.get("/nokia-state:state/mirror/mirror-dest[service-name='test-pcap']/pcap[session-name='test']/file-size")
print("Session state: {0}, size: {1} bytes".format(state, size))
connection_object.cli("perform pcap \"test\" capture stop")
print("Capture stopped for session \"test\"")
time.sleep(3)
connection_object.cli("perform pcap \"test\" capture start")
print("Capture restarted for session \"test\"")
```
///

### Final pySROS script

You already know how to get the state, the get file size, the stop and start pcap.
Let's include the logical sequence to your script.   

  - Check if pcap not "in-progress" stop here no action
  - Check if pcap "in-progress" and file size is 30KB stop pcap 
  - Move `test.pcap` to `test.pcap.1`. To manipulate files in the SR OS consult the [file commands documentation](https://documentation.nokia.com/sr/26-3/7750-sr/books/md-cli-command-reference/oper-file_0.html).
  - Restart pcap keeping original name `test.pcap`

When you are done run/test your final script with `pyexec` 

/// details | Solution (read only if you need assistance)
    type: success

```python
#!/usr/bin/env python3
"""
Capture-size monitor for a Nokia SR-OS pcap session.
Stops the capture, rolls over file, and restarts when the file
exceeds a configurable size threshold.
"""

import sys
import time
from pysros.management import connect # connect SR OS

#-------------------------------------------------------------------
#Configuration (adjust as needed)
#-------------------------------------------------------------------
SERVICE_NAME = "test-pcap"
SESSION_NAME = "test"
SIZE_THRESHOLD = 30000 # bytes
SLEEP_AFTER_STOP = 2 # seconds
SLEEP_AFTER_MOVE = 2 # seconds

#-------------------------------------------------------------------
def get_state_and_size(conn):
    #Retrieve session state and file size in a single RPC.
    
    path = "/nokia-state:state/mirror/mirror-dest[service-name='{}']".format(SERVICE_NAME) + "/pcap[session-name='{}']".format(SESSION_NAME)
    
    data = conn.running.get(path)
    state = data.get("session-state")
    # Convert the size leaf to an integer for comparison
    size = data.get("file-size")
    return state, size
#-------------------------------------------------------------------
def main():
    # ------------------------------------------------------------------
    # Connect to the local router (pyexec runs on the router itself)
    # ------------------------------------------------------------------
    try:
        conn = connect()
    except Exception as exc:
        print("Failed to connect to the router: {0}".format(exc))
        sys.exit(1)

    # ------------------------------------------------------------------
    # Get current session state and file size
    # ------------------------------------------------------------------
    state, size = get_state_and_size(conn)

    if str(state) != "in-progress":
        print("Session is not in-progress – nothing to do.")
        sys.exit(0)

    if size <= SIZE_THRESHOLD:
        print('Session "{0}" size {1} bytes – below threshold.'.format(
            SESSION_NAME, size))
        sys.exit(0)

    print('Session "{0}" size {1} bytes – above threshold.'.format(
        SESSION_NAME, size))

    # ------------------------------------------------------------------
    # Stop the capture
    # ------------------------------------------------------------------
    try:
        conn.cli('perform pcap "{0}" capture stop'.format(SESSION_NAME))
    except Exception as exc:
        print("Failed to stop capture: {0}".format(exc))
        sys.exit(1)

    print('Capture stopped for session "{0}"'.format(SESSION_NAME))
    time.sleep(SLEEP_AFTER_STOP)

    # ------------------------------------------------------------------
    # Rollover the pcap file
    # ------------------------------------------------------------------
    print("Pcap file rollover...")
    try:
        conn.cli('file move "{0}.pcap" "{0}.pcap.1" force'.format(SESSION_NAME))
    except Exception as exc:
        print("File move failed: {0}".format(exc))
        sys.exit(1)

    time.sleep(SLEEP_AFTER_MOVE)

    # ------------------------------------------------------------------
    # Restart the capture
    # ------------------------------------------------------------------
    try:
        conn.cli('perform pcap "{0}" capture start'.format(SESSION_NAME))
    except Exception as exc:
        print("Failed to restart capture: {0}".format(exc))
        sys.exit(1)

    print('Capture restarted for session "{0}"'.format(SESSION_NAME))
#---------------------------------------------------------------------
if __name__ == "__main__":
    main()

```
///

### Use CRON make your pySROS script run on a schedule

Now automate your final working pySROS script with CRON.   

Steps to configure CRON to execute the python script.

1. Define a `python-script` under:
```
/configure python python-script
```  

2. Define a `script-policy` under:
```
/configure system script-control script-policy
```

3. Define a `schedule` under:
```
/configure system cron schedule
```  

The scheduler CRON will run the `cf3:my.py` script periodically every 60s

/// details | Config
    type: tip

/// tab | python-script  
```
/configure python python-script "mon_pcap" urls cf3:/my.py  
/configure python python-script "mon_pcap" version python3  
/configure python python-script "mon_pcap" admin-state enable  
```
/// 
/// tab | script-policy  
```
/configure system script-control script-policy "smon_pcap" max-completed 10   
/configure system script-control script-policy "smon_pcap" results "cf3:/mon_pcap-results"   
/configure system script-control script-policy "smon_pcap" python-script name "mon_pcap"   
/configure system script-control script-policy "smon_pcap" admin-state enable
```
/// 
/// tab | scheduler cron   
```
/configure system cron schedule "cmon_pcap" interval 60  
/configure system cron schedule "cmon_pcap" type periodic  
/configure system cron schedule "cmon_pcap" script-policy name "smon_pcap"  
/configure system cron schedule "cmon_pcap" admin-state enable  
```
///
///

Inspect CRON scheduler active with the following CLI command:
```
show system cron schedule "cmon_pcap"
```

/// details | Output: cron schedule
    type: info
```
===============================================================================
CRON Schedule Information
===============================================================================
Schedule                     : cmon_pcap
Schedule owner               : TiMOS CLI
Description                  : none
Administrative status        : enabled
Operational status           : enabled
Script Policy                : smon_pcap
Script Policy Owner          : TiMOS CLI
Script                       : N/A
Script owner                 : N/A
Python-script                : mon_pcap
Source location              : cf3:/my.py
Results location             : cf3:/mon_pcap-results
Schedule type                : periodic
Interval                     : 0d 00:01:00 (60 seconds)
Repeat count                 : infinite
Next scheduled run           : 0d 00:00:51
End time                     : none
Weekday                      : none
Month                        : none
Day of month                 : none
Hour                         : none
Minute                       : none
Number of schedule runs      : 2
Last schedule run            : 2026/05/15 16:22:20  UTC
Number of schedule failures  : 0
Last schedule failure        : no error
Last failure time            : never
 
===============================================================================

```
///

### Simulate the network-control traffic spike

Now that you have tackled the main objective of automatically rotating PCAP files, let's finish the activity by simulating a spike event that will trigger the final stop condition for the packet-capture and CRON scheduler. It's expected that after this, your python-script won't rotate any more files, preserving the latest data captured.
Start a rapid `ping` to :material-router: PE3 direct connected interface.

/// note 

From the :material-router: P2 CLI start the ping.
```bash
ping 10.64.12.5 fc nc size 1500 interval 0.01 count 1000 output-format summary
```
///

Wait for the `ping` process to finish and then check in the `show log log-id 99` that: 

  - RMON detected the traffic spike 
  - EHS was invoked
  - The script to stop the pcap ran

/// details | Output: `show log log-id 99`
    type: tip

```bash
574 2026/05/14 11:40:57.611 UTC MAJOR: SYSTEM #2053 Base CLI 'exec'
"The CLI user initiated 'exec' operation to process the commands in the SROS CLI file cf3:/stop-pcap.txt has completed with the result of success"

7573 2026/05/14 11:40:57.611 UTC WARNING: SYSTEM #2121 Base Commit
"Commit to configure by  (Cron/EHS) from Cron/EHS succeeded."

7572 2026/05/14 11:40:57.606 UTC MAJOR: SYSTEM #2052 Base CLI 'exec'
"A CLI user has initiated an 'exec' operation to process the commands in the SROS CLI file cf3:/stop-pcap.txt"

7571 2026/05/14 11:40:57.605 UTC MINOR: SYSTEM #2069 Base EHS script
"Ehs handler :"handler-stop-pcap" with the description : "" was invoked by the cli-user account "not-specified"."

7570 2026/05/14 11:40:57.604 UTC MAJOR: SNMP #2101 Base RMON delta alarm
"RMON alarm: Rising : value=433268, >=400000 : alarm-index 1000, event-index 1000 alarm-variable OID tmnxPortNetEgressFwdInProfOcts.1.1647313089.8"
```
///

Use the show commands you learned so far and try to respond the next questions.

1. What is the actual status of the mirror service, is it disabled?   
2. Has the python script scheduled execution stopped?
3. Are the latest `test.pcap` and `test.pcap.1` files are present at `cf3:`?


/// details | TIP: CLI shows
    type: tip
```
show mirror mirror-dest
```
```    
show system cron schedule
```
```
file list
```
///

/// details | Solution
    type: success

/// tab | 1 - Mirror service status

YES, it is expected that the mirror service pcap status is disabled, admin-down or oper-down.
```    
A:admin@g3-p2# show mirror mirror-dest 

===============================================================================
Mirror Services
===============================================================================
Id          Type   Adm    Opr    Destination                   SDP Lbl/   Slice
    Name                                                       SAP QoS    
-------------------------------------------------------------------------------
500         ETH    Down   Down   None                          n/a        256
    test-pcap
-------------------------------------------------------------------------------
Legend: ETH = Ether, IPO = Iponly, UNK = Unknown
===============================================================================

```
///

/// tab | 2- Python script status

YES, it is expected that the python script execution stopped: admin-down and oper-down.
```
A:admin@g3-p2# show system cron schedule 

===============================================================================
CRON Schedule Information
===============================================================================
Schedule                     : mon_pcap
Schedule owner               : TiMOS CLI
Description                  : none
Administrative status        : disabled
Operational status           : disabled
Script Policy                : mon_pcap
Script Policy Owner          : TiMOS CLI
Script                       : N/A
Script owner                 : N/A
Python-script                : mon_pcap
Source location              : cf3:my.py
Results location             : cf3:/mon_pcap-results
Schedule type                : periodic
Interval                     : 0d 00:01:00 (60 seconds)
Repeat count                 : infinite
Next scheduled run           : 0d 00:00:00
End time                     : none


Weekday                      : none
Month                        : none
Day of month                 : none
Hour                         : none
Minute                       : none
Number of schedule runs      : 2
Last schedule run            : 2026/05/15 18:59:52  UTC
Number of schedule failures  : 0
Last schedule failure        : no error
Last failure time            : never
 
===============================================================================

```
///

/// tab | 3 - Pcap files list
YES, the files are present on `cf3:` for future inspection.
```
A:admin@g3-p2# file list test*      

Volume in drive cf3 on slot A has no label.

Directory of cf3:

05/15/2026  07:00p              165781 test.pcap
05/14/2026  06:16p               64016 test.pcap.1
               2 File(s)                 229797 bytes.
               0 Dir(s)            146790617088 bytes free.

```
///
///

You can also check on your hackathon instance in the folder `~/SReXperts/activities/activity-65/` with all configuration files used to deploy this activity.

## Summary and review

Congratulations! If you have got this far you have completed this activity and achieved the following:   
  
  -  You have learnt how to handle the mirror service PCAP to avoid CF card exhaustion
  -  You have learnt the behavior of SR OS show commands
  -  You have written one or more applications using the Python programming language using the MicroPython interpreter pre-installed on SR OS
  -  You have worked with YANG modeled data
  -  You have executed Python applications on the SR OS Model-Driven CLI (MD-CLI)
  -  You learnt about SR OS built-in automation features with RMON, EHS and CRON.

Using pySROS together with EHS, RMON, and CRON offers a reliable, automated solution for managing local PCAP storage on Nokia SR OS routers.
The approach prevents disk-space exhaustion while preserving the latest capture data.

If you're hungry for more, try another activity.  


You can see how SR OS provides many automation alternatives, including built‑in features used in this task such as RMON, CRON, and EHS. Today, with pySROS you have greater flexibility for automation. Consider that this activity could be rewritten using only pySROS—challenge yourself to learn more about it [pySROS Documentation](https://network.developer.nokia.com/static/sr/learn/pysros/latest/introduction.html).
