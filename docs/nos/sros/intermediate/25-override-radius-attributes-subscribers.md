---
tags:
  - SROS
  - RADIUS
  - Python-script
  - Python-policy
  - BNG
  - PPPoE
  - DHCP
---

# Block IPv6 for selected BNG subscribers

|     |     |
| --- | --- |
| **Activity name** | Block IPv6 for selected BNG subscribers |
| **Short Description** | Block IPv6 connectivity for subscribers that match a specific criteria |
| **Difficulty** | Intermediate |
| **Tools used** | [MicroPython](https://docs.micropython.org/en/latest/library/index.html#), [Python policy](https://documentation.nokia.com/sr/26-3/7750-sr/books/tpsda/python-script-support-esm.html#ai9jxkma6b) |
| **Topology Nodes** | :material-router: PE4 (BNG) |
| **References** | [MD-CLI User Guide](https://documentation.nokia.com/sr/26-3/7750-sr/titles/md-cli-user.html#undefined)<br/>[TPSDA Guide](https://documentation.nokia.com/sr/26-3/7750-sr/titles/tpsda.html#undefined)<br/>[RADIUS Attributes Reference Guide](https://documentation.nokia.com/sr/26-3/7750-sr/titles/radius.html)<br/>[Python policy overview](https://documentation.nokia.com/sr/26-3/7750-sr/books/tpsda/python-script-support-esm.html#ai9jxkma6b)<br/>[SR BNG TPSDA Python 3 API](https://documentation.nokia.com/sr/26-3/tpsda-python-3-api/index.html)<br/>[BNG Blaster](https://rtbrick.github.io/bngblaster/) |

## Objective

You are a network administrator for an Internet Service Provider. A recent change in company policy requires IPv6 connectivity to be disabled for a specific category of subscribers, in line with business and service requirements.

A subscriber falls into this category if both of the following conditions are met:

- The IPv4 address is assigned by RADIUS (via the `Framed-IP-Address` attribute)
- The assigned IPv4 address falls within the range 10.24.1.10–10.24.1.19

Assuming that the RADIUS server does not support the granularity required to enforce this requirement selectively, your goal is to implement this control on the 7750 SR BNG by leveraging the `python-policy` feature to inspect and modify RADIUS `Access-Accept` messages.

## Technology explanation

### Subscribers, sessions and hosts
In Nokia SROS subscriber management terminology, subscriber, subscriber-sessions and subscriber-hosts are related but distinct concepts:

- **Subscriber**: Represents a residential or small business user, uniquely identified by a `subscriber-id` (a string of characters). A subscriber is composed by one or more sessions/hosts.
- **Subscriber-Host**: Represents a single IP stack on an end-device (e.g. a PC, CPE or set-top box) requesting a service. It is identified by a unique combination that may include SAP ID, IP address, MAC address or PPPoE Session ID. 
- **Subscriber-Session**: A grouping of one or more subscriber-hosts that represent the different IP stacks of the same end-device. An IPoE dual-stack client (having 1x IPv4 and 1x IPv6 address assigned by DHCP) is an example scenario of a subscriber session grouping 2 hosts.

-{{ diagram(path='./../../../../../images/25-override-radius-attributes-subscribers/25-tech-explain.drawio', title='Fig. 1 - Simplified overview of a subscriber-management setup with two active subscribers', page=0, zoom=1.5) }}-

### Subscriber authentication via RADIUS
RADIUS is common method used by ISPs to authenticate subscribers. The typical flow for an IPoE DHCP subscriber is:

1. Subscriber host attempts to get an IP address (sends a DHCP Discover).
2. BNG captures this request and, in the background, sends an Access-Request message to the RADIUS server for authentication. 
3. If authentication is successful, RADIUS replies with Access-Accept message to the BNG. This message may include attributes that BNG will then use to instantiate the subscriber host with the desired configuration.
4. BNG (RADIUS client) reads the Access-Accept message and process the attributes inside.
5. DHCP process continues (Offer, Request, Ack), and if there are no errors, the subscriber host is instantiated in the system.

-{{ diagram(path='./../../../../../images/25-override-radius-attributes-subscribers/25-tech-explain.drawio', title='Fig. 2 - Authentication process for an IPoE DHCPv4 subscriber-host', page=1, zoom=1.5) }}-

### Python policy
User-defined python scripts can be used to intercept and modify RADIUS messages between the BNG RADIUS client and the RADIUS server. This is done via the SR OS python policy framework using the following base building blocks:

 - **python-script**: Implements the logic to inspect the contents of RADIUS message and take actions.
 - **python-policy**: Enables python-script evaluation for desired combination of RADIUS message types and direction (inbound or outbound).

-{{ diagram(path='./../../../../../images/25-override-radius-attributes-subscribers/25-tech-explain.drawio', title='Fig. 3 - Illustration of RADIUS messages conditional interception using python-policy', page=2, zoom=1.5) }}-

## Tasks
**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them. 

### Analyze the current situation
Login to :material-router: PE4, explore the subscribers and identify at least one that matches the target category.
!!! info "Connect to :material-router:PE4 from your group's hackathon instance"
    ```
    ssh admin@clab-srexperts-pe4 
    ```
/// note

All subscriber-hosts are instantiated in the vprn service id 401 ("bng-vprn").
///

/// admonition
    type: tip
List of commands that may help you explore:
```bash
show service subscriber-using # list all subscribers
show service active-subscribers hierarchy # Display all subscribers, sessions and hosts in a hierarchical view
show service active-subscribers subscriber <id> # inspect hosts owned by a specific subscriber
show service active-subscribers subscriber <id> detail # inspect details about a specific subscriber
show service id "401" subscriber-hosts # list all subscriber hosts in the service
show service id "401" subscriber-hosts ip <ip_address> detail # list details about a particular host identified by the IP address.
show service id 401 dhcp[6] lease-state #list all dhcpv4 or dhcpv6 leases
show service id 401 dhcp[6] lease-state ip[v6]-address detail # display details about a particular host DHCPv4 or DHCPv6 lease
show service id "401" pppoe session [detail] # list pppoe hosts (optionally use detail to display more info)
show service id "401" ipoe session [detail] # list ipoe hosts (optionally use detail to display more info)
```
///

To know if a particular subscriber IPv4 address was explicitly assigned by RADIUS (via `Framed-IP-Address` attribute), look for fields such as `Address Origin` or `IP Origin` in the detailed outputs.  
Following are 3 examples:
/// tab | subscriber-host detail

```bash hl_lines="26"
A:admin@g1-pe4# show service id "401" subscriber-hosts ip x.x.x.x detail 

===============================================================================
Subscriber Host table
===============================================================================
Sap                                                             
  IP Address                                                    
    MAC Address                PPPoE-SID       Origin          Fwding State
      Subscriber                                               
-------------------------------------------------------------------------------
[x/x/x/x:x]
  x.x.x.x
    xx:xx:xx:xx:xx:xx          N/A             DHCP            Fwding
      xxxxxxxxx
-------------------------------------------------------------------------------
Subscriber-interface  : xxxx
Group-interface       : xxxx
Sub Profile           : xxxx
SLA Profile           : xxxx
App Profile           : N/A
Egress Q-Group        : N/A
Egress Vport          : N/A

Acct-Session-Id       : xxxxxx
Acct-Q-Inst-Session-Id: xxxxxx
Address Origin        : AAA 
OT HTTP Rdr IP-FltrId : N/A
OT HTTP Rdr Status    : N/A
OT HTTP Rdr Fltr Src  : N/A
HTTP Rdr URL Override : N/A
GTP local break-out   : No
DIAMETER session ID Gx: N/A
-------------------------------------------------------------------------------
Number of subscriber hosts : 1
===============================================================================
```
///
/// tab | ipoe session detail

```bash hl_lines="37"
A:admin@g1-pe4# show service id "401" ipoe session ip-address x.x.x.x detail 

===============================================================================
IPoE sessions for service 401
===============================================================================

SAP                     : [x/x/x/x:x]
Mac Address             : xx:xx:xx:xx:xx:xx
Circuit-Id              : xxxxxxx
Remote-Id               : xxxxxxx
Session Key             : sap-mac

MC-Standby              : No

Subscriber-interface    : xxxxxx
Group-interface         : xxxxxx

Termination Type        : local
Up Time                 : 0d 04:04:32
Session Time Left       : N/A
Last Auth Time          : 03/17/2026 17:25:16
Min Auth Intvl (left)   : 0d 00:05:00 (0d 00:00:29)

Persistence Key         : N/A
Subscriber              : "xxxxx"
Sub-Profile-String      : "xxxxxx"
SLA-Profile-String      : "xxxxx"
SPI group ID            : (Not Specified)
ANCP-String             : "xx:xx:xx:xx:xx:xx"
Int-Dest-Id             : ""
App-Profile-String      : ""
Category-Map-Name       : ""
Acct-Session-Id         : "xxxxxxxxxxxx"
Sap-Session-Index       : x

IP Address              : x.x.x.x
IP Origin               : Radius
Address-Pool            : N/A
(...)
```
///
/// tab | pppoe session detail

```bash hl_lines="25"
A:admin@g1-pe4# show service id 401 pppoe session ip-address x.x.x.x detail 

===============================================================================
PPPoE sessions for svc-id 401
===============================================================================
Sap Id              Mac Address       Sid    Up Time         Type
    IP/L2TP-Id/Interface-Id                                      MC-Stdby
-------------------------------------------------------------------------------
[x/x/x/x:x]      xx:xx:xx:xx:xx:xx x      0d 04:34:03     local
    x.x.x.x                                                          
    xx:xx:xx:xx:xx:xx:xx:xx                                              


LCP State            : Opened
IPCP State           : Opened
IPv6CP State         : Opened
PPP MTU              : 1492
PPP Auth-Protocol    : CHAP
PPP User-Name        : xxxxxxx

Subscriber-interface : xxxxx
Group-interface      : xxxxx


IP Origin            : radius
DNS Origin           : none
NBNS Origin          : none
(...)
```
///

/// tip
To get a list of all subscriber-hosts IP addresses you can use `show service id "401" subscriber-hosts` or `show service active-subscribers hierarchy`. And then explore a few by using one of the above commands.
/// 
### Analyze RADIUS Access-Accept messages
Inspect the contents of the `Access-Accept` messages for one of the relevant subscriber sessions.  

Configure a new log (with a new `log-id`) to monitor the debug stream.  Then enable RADIUS debugging and monitor the output.
/// details | If you need assistance

/// tab | radius debug

```bash
A:admin@g1-pe4# debug private 

[pr:/debug]
A:admin@g1-pe4# info
    router "Base" {
        radius {
            servers {
                packet-types {
                    authentication true
                    accounting false
                    coa false
                }
            }
        }
    }

[pr:/debug]
A:admin@g1-pe4# commit
```

///
/// tab | log-id config 
/// note
This should be already pre-configured in PE4. 
///
```bash 
[gl:/configure log log-id "21"]
A:admin@g1-pe4# info
    admin-state enable
    description "debug log"
    source {
        debug true
    }
    destination {
        cli {
        }
    }
```
The log-id in this example is configured with destination CLI, which means it can be subscribed per terminal session to display the messages in real-time on the CLI.  
To subscribe/unsubscribe that log-id on your current terminal session, use the following commands respectively:
```
/tools perform log subscribe-to log-id "21" 
/tools perform log unsubscribe-from log-id "21" 
```
///
///

/// tip

To restart the subscriber session associated with a particular MAC-address, use the following command in your hackathon instance:
```bash
docker exec -it clab-srexperts-bngblaster bngblaster-cli /ctrl.sock session-restart session-id X
```
The session-id `X` (decimal) maps to the host MAC address least significant bits. For example `session-id 4` corresponds to the host with MAC-address `02:00:00:00:00:04`. The `session-id` can also be consulted in the `remote-id` identifier, which is displayed in the `show service id 401 ipoe session detail`  or  `show service id 401 ppp session detail` output.  
```bash hl_lines="8 10"
A:admin@g3-pe4#  show service id 401 ipoe session mac 02:00:00:00:00:04 detail 

===============================================================================
IPoE sessions for service 401
===============================================================================

SAP                     : [1/1/c5/1:100]
Mac Address             : 02:00:00:00:00:04
Circuit-Id              : agg1-e1/1:100
Remote-Id               : session4
Session Key             : sap-mac
(...)
```

Alternatively, you can force-clear a particular session on the BNG. When using this method, PPP clients will quickly attempt reestablishment, but IPoE (DHCP) clients will only do it after the DHCP lease-time expires:
```bash
clear service id 401 ipoe session ...
clear service id 401 ppp session ...
```

On session reconnect, some RADIUS debug messages are expected and session `Up Time` should reset:
/// tab | sample radius debug log
```bash 
51 2026/04/06 16:40:12.524 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Transmit
  Access-Request(1) 10.64.13.0:1812 id 189 len 139 vrid 1 pol RadPolicy1
    USER NAME [1] 17 02:00:00:00:00:04
    PASSWORD [2] 16 yAAo.bVJ7OmQSy3s6aleQ.
    NAS IP ADDRESS [4] 4 10.46.3.24
    VSA [26] 25 DSL(3561)
      AGENT CIRCUIT ID [1] 13 agg1-e1/1:100
      AGENT REMOTE ID [2] 8 session4
    NAS PORT TYPE [61] 4 Ethernet(15)
    NAS PORT ID [87] 12 1/1/c5/1:100
    VSA [26] 19 Nokia(6527)
      CHADDR [27] 17 02:00:00:00:00:04
```
///
/// tab | uptime change
```bash hl_lines="14"
A:admin@g3-pe4# show service id 401 ipoe session 

===============================================================================
IPoE sessions for svc-id 401
===============================================================================
Sap Id                           Mac Address         Up Time         MC-Stdby
    Subscriber-Id                                                    
        [CircuitID] | [RemoteID]                                     
-------------------------------------------------------------------------------
[1/1/c5/1:10]                    02:00:00:00:00:01   0d 00:33:15     
    cafe
[1/1/c5/1:12]                    02:00:00:00:00:03   4d 07:49:27     
    babe
[1/1/c5/1:100]                   02:00:00:00:00:04   0d 00:00:07     
    1/1/c5/1:100
[1/1/c5/1:101]                   02:00:00:00:00:06   4d 07:49:26     
    1/1/c5/1:101
-------------------------------------------------------------------------------
CID | RID displayed when included in session-key
Number of sessions : 4
===============================================================================
```
///
///

/// admonition | Examine the Access-Accept message
    type: question

> Write down your answer to the following questions, you may need them later:

- Which attribute needs to be inspected by python script to evaluate if the subscriber matches the target category?
- Which attributes are relevant for the subscriber address assignment? How those interact with the current BNG configuration?

///

### Apply a python-policy for RADIUS Access-Accept messages.
By now you should have a mental plan on how to accomplish the goal. It's time to start implementation.  

Configure a `python-policy`/`python-script` so that inbound `Access-Accept` RADIUS messages are intercepted and passed transparently without modification (you will change the script behavior in later tasks).

 1. Create a python script file inside `cf3:/` that contains at least one line of code.
 2. Define a `python-script` under `/configure python python-script`.
 3. Define a `python-policy` under `/configure python python-policy`.
 4. Apply the `python-policy` under the relevant `/configure aaa radius server-policy` that is being used to authenticate the subscribers.

/// tip

Enable debug for your python-script execution. Note this debug has not yet migrated to MD-CLI, so it needs to be enabled from Classic CLI context. You can quickly switch between those modes using `//`
```bash
[/]
A:admin@g1-pe4# //
INFO: CLI #2051: Switching to the classic CLI engine
INFO: CLI #2050: Classic CLI modification of the configuration is not allowed - 'model-driven' management interface configuration mode active
*A:g1-pe4# debug python python-script xxxxx script-all-info 
```
To disable debug in the Classic CLI, enter `no debug`

Don't forget to use `//` to switch back to the model-driven CLI.


///

Test the `python-script` execution by forcing a single subscriber to re-authenticate.  
/// details | How to force re-authentication?
    type: tip

One way to do it is to restart the subscriber session on the end-device
```title="example: restarting subscriber session 4 (mac-address 02:00:00:00:00:04)"
docker exec -it clab-srexperts-bngblaster bngblaster-cli /ctrl.sock session-restart session-id 4
```
///

If all goes well, a sequence of 3 debug messages should be logged, indicating that `python-script` intercepted the `Access-Accept` message successfully:
``` title="debug logs: python-script + radius"
192 2026/04/06 17:37:04.752 UTC minor: DEBUG #2001 Base Python Output
Python Output: xxxxx                    
193 2026/04/06 17:37:04.752 UTC minor: DEBUG #2001 Base Python Result
Python Result: xxxxx                    
194 2026/04/06 17:37:04.752 UTC minor: DEBUG #2001 Base RADIUS
RADIUS: Script                              
  Access-Accept(2) id 252 len 338 from 10.64.13.0:1812 policy xxxxx status success
```  
/// note
Python-script file modifications do not take effect automatically. To apply your updates, reload the script using:
    ```
    /perform python python-script reload script "xxxxx"
    ```
To verify `python-script` in-service status and last-update time, use: 
```
show python python-script "xxxxx"
```
///
/// details | Help
    type: tip
 - Inspect the vprn configuration and find the first reference point to the radius authentication policy
 - In MD-CLI configuration context, you can use `info flat | match radius` to search for configured lines that include the keyword `radius`.
 - You can create/edit :material-router: PE4 `cf3:/` files using the CLI built-in `file edit` tool, directly from the hackathon instance by accessing `/home/nokia/SReXperts/clab/clab-srexperts/pe4/A/config/cf3`, or by uploading them to the node using SFTP
 
/// details | configuration

```
/configure python python-script "my_script" admin-state enable
/configure python python-script "my_script" action-on-fail passthrough
/configure python python-script "my_script" urls ["cf3:/radius.py"]
/configure python python-script "my_script" version python3
/configure python python-policy "rpol" radius access-accept direction ingress script "my_script"
/configure aaa radius server-policy "RadPolicy1" python-policy "rpol"
```
///

/// details | python script
 
 ```py title="cf3:/radius.py"

 #The pass statement can be used as a placeholder when code is to be included in the future. 
 pass
 ```
 This script example is not performing any action. The result is that RADIUS `Access-Accept` messages are passed through unaltered to the BNG RADIUS client application. On the next tasks you will develop this script in order to inspect and conditionally modify the contents of RADIUS messages.
///
///

### Develop the python-script logic to identify the target subscribers
/// note

For this and next tasks, refer to [RADIUS SR BNG TPSDA Python 3 API](https://documentation.nokia.com/sr/26-3/tpsda-python-3-api/alc-radius.html#) for how to inspect or modify attributes in a RADIUS message. 
///
Modify the python-script to evaluate if a given subscriber matches the target category. 
/// tip

Have the script print a message if the condition matches, so you can visualize in debug log that evaluation is successful for the intended subscriber only.
///
/// details | Hint
    type: tip

Make use of python3 standard lib module [ipaddress](https://docs.python.org/3/library/ipaddress.html) to simplify operations over IP addresses.
///

### Finalize the changes to achieve the objective
Modify the python-script (and BNG configuration, if you think it is needed) to make sure that IPv6 hosts are not created for the subscribers that match the target category.

### Test functionality
Restart all subscriber sessions and verify that IPv6 hosts are blocked ONLY for the target category of subscribers.
/// tab | reset subscribers
```
docker exec -it clab-srexperts-bngblaster bngblaster-cli /ctrl.sock session-restart
```
///
/// tab | expected subscribers state
```bash hl_lines="54-72"
A:admin@g1-pe4# show service active-subscribers hierarchy  

===============================================================================
Active Subscribers Hierarchy
===============================================================================
-- 1/1/c5/1:100
   (SUB_PROF1)
   |
   +-- sap:[1/1/c5/1:100] - sla:SLA_PROF1
       |
       +-- IPOE-session - mac:02:00:00:00:00:04 - svc:401
           |
           |-- 10.24.1.129 - DHCP
           |
           |-- 2010:4:a:c::1/128 - DHCP6
           |
           +-- 2010:4:d:2c::/64 - DHCP6-PD

-- 1/1/c5/1:101
   (SUB_PROF1)
   |
   +-- sap:[1/1/c5/1:101] - sla:SLA_PROF1

       |
       |-- PPP-session - mac:02:00:00:00:00:05 - sid:1 - svc:401
       |   |   circuit-id:agg1-e1/2:101
       |   |   remote-id:session5
       |   |
       |   |-- 10.24.1.127 - IPCP
       |   |
       |   +-- 2010:4:d:2a::/64 - DHCP6-PD
       |
       +-- IPOE-session - mac:02:00:00:00:00:06 - svc:401
           |
           |-- 10.24.1.130 - DHCP
           |
           |-- 2010:4:a:d::1/128 - DHCP6
           |
           +-- 2010:4:d:2d::/64 - DHCP6-PD

-- 1/1/c5/1:102
   (SUB_PROF1)
   |
   +-- sap:[1/1/c5/1:102] - sla:SLA_PROF1
       |
       +-- PPP-session - mac:02:00:00:00:00:07 - sid:1 - svc:401
           |   circuit-id:agg1-e1/2:102
           |   remote-id:session7
           |
           |-- 10.24.1.128 - IPCP
           |
           +-- 2010:4:d:2b::/64 - DHCP6-PD

-- babe
   (SUB_PROF1)
   |
   +-- sap:[1/1/c5/1:12] - sla:SLA_PROF1
       |
       +-- IPOE-session - mac:02:00:00:00:00:03 - svc:401
           |
           +-- 10.24.1.14 - DHCP

-- beef
   (SUB_PROF1)
   |
   +-- sap:[1/1/c5/1:11] - sla:SLA_PROF1
       |
       +-- PPP-session - mac:02:00:00:00:00:02 - sid:1 - svc:401
           |   circuit-id:agg1-e1/2:11
           |   remote-id:session2
           |
           +-- 10.24.1.13 - IPCP

-- cafe
   (SUB_PROF1)
   |
   +-- sap:[1/1/c5/1:10] - sla:SLA_PROF1
       |
       +-- IPOE-session - mac:02:00:00:00:00:01 - svc:401
           |
           |-- 10.24.1.20 - DHCP
           |
           |-- 2010:4:a:cafe::/128 - DHCP6
           |
           +-- 2010:4:d:cafe::/64 - DHCP6-PD

-------------------------------------------------------------------------------
Number of active subscribers : 6
Flags: (N) = the host or the managed route is in non-forwarding state
===============================================================================
```
///

/// details | Solution
    type: success

/// tab | configuration
````
python {
        python-script "my_script" {
            admin-state enable
            action-on-fail passthrough
            urls ["cf3:/radius.py"]
            version python3
        }
        python-policy "rpol" {
            radius access-accept direction ingress {
                script "my_script"
            }
        }
    }

/configure aaa radius server-policy "RadPolicy1" python-policy "rpol"
````
///
/// tab | script
````py title="cf3:/radius.py"
from alc import radius
import ipaddress
start_address = ipaddress.IPv4Address('10.24.1.10')
end_address = ipaddress.IPv4Address('10.24.1.19')
framedip_bytes = radius.attributes.get((8,))
if framedip_bytes:
    framedip = ipaddress.IPv4Address(framedip_bytes)
    if framedip >= start_address and framedip <= end_address:
        radius.attributes.clear((100,)) #clear Framed-IPv6-Pool VSA
        radius.attributes.clear((26,6527,131)) #clear Alc-Delegated-IPv6-Pool VSA
        radius.attributes.clear((123,)) # clear Delegated-IPv6-Prefix VSA
        radius.attributes.clear((97,)) # clear Framed-IPv6-Prefix VSA
````
///
/// admonition | Did you arrive to similar solution?
    type: question
 There is (at least) one alternative way to solve it.
///
///

## Summary

Congratulations!  If you have got this far you have tackled the complex task of integrating Python code into the RADIUS authentication data-path to modify RADIUS messages on the fly, adjusting their attributes and solving the objective of restricting IPv6 for specific user groups.

In this exercise you have:

- Used the `python-policy` feature to inspect RADIUS messages
- Written code in Python
- Worked with debug and other troubleshooting tools
- Manipulated RADIUS attributes
- Used customization with code to troubleshoot and provide workaround to limitations of RADIUS servers

<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>
