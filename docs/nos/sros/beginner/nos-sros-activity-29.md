---
tags:
  - MD-CLI
  - SR OS
  - Introduction
  - YANG-CLI
  - CLI
---

# Introduction to the SR OS Model-Driven CLI


|                             |          |
| --------------------------- | ----------------------------------------- |
| **Activity name**           | Introduction to the SR OS Model-Driven CLI   |
| **Activity ID**             | 29    |
| **Short Description**       | Learn to efficiently navigate and operate the Nokia SR OS Model-Driven CLI (MD-CLI) by understanding its prompt and modes, exploring configuration and state hierarchies, managing changes with commit/rollback workflows, using output modifiers, creating aliases, and leveraging command history.  |
| **Difficulty**              | Beginner   |
| **Tools used**              | SR OS CLI   |
| **Topology Nodes**          | :material-router: PE1, :material-router: PE2, :material-router: P1, :material-router: P3    |
| **References**              | [MD-CLI User Guide](https://documentation.nokia.com/sr/26-3/7750-sr/titles/md-cli-user.html)<br/>[MD-CLI Explorer](https://documentation.nokia.com/sr/26-3/mdcli-explorer/index.html)<br/>[SR OS YANG Browser](https://yangbrowser.nokia.com/sros/26.3.R3) |

*This activity is designed as a starter guide for those operators who have never used SR OS Model-Driven CLI before.  If you are familiar with SR OS MD-CLI we suggest you tackle one of the other activities at the level you feel is appropriate.*

The Nokia SR OS supports two classes of management interfaces: classic management interfaces (the classic CLI and SNMP) and model-driven management interfaces (the MD-CLI, NETCONF, and gRPC). [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/model-driven-management-interfaces.html#ai9exgstzy)

## Objective

By completing this hackathon activity, you will gain practical, hands-on experience with the Nokia SR OS Model-Driven CLI (MD-CLI), a modern, YANG-based management interface that provides a consistent and structured approach to router configuration, state and operations. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/get-started-md-cli-user.html#ai89jylu4b).

You will learn how to [navigate](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/navigate.html#ai89jylu4e) the MD-CLI hierarchy, [apply and commit configurations](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/edit-configuration.html#ai89jylu0o) using the transactional candidate datastore model, customize their working environment through [command aliases](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/navigate.html#concept_hkg_hb3_bqb), and safeguard network changes using the [rollback option](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/edit-configuration.html#unique_1649078562), building the foundational skills needed to confidently manage Nokia SR OS nodes using the CLI in a model-driven operational environment.


## Technology Explanation

The MD-CLI (Model-Driven Command Line Interface) represents a modern approach to router management. It is built on a common infrastructure that uses YANG models as the core definition for configuration, state, and operational actions, ensuring consistency across the MD-CLI, NETCONF, and gRPC interfaces.

### Key benefits of the MD-CLI include:

- **Transactional configuration**: Changes are made in a private or shared candidate configuration datastore and only become active in the running configuration datastore after a `commit` command is issued. This eliminates strict configuration ordering requirements that exist in the classic CLI. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/edit-configuration.html#ai89jylu0r).

- **Multi-user configuration modes**: Private, exclusive, global, and read-only modes control how simultaneous configuration sessions interact with each other.

- **Structured data output**: Configuration and state can be displayed in JSON or XML formats, making it easy to integrate with automation tools and applications such as pySROS, NETCONF and gRPC clients. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/display-information.html#ai89jylu4a).

- **Configuration groups and aliases**: Flexible templates and custom command shortcuts simplify and accelerate the configuration process. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/navigate.html#unique_324622772).

- **Automation-ready**: The MD-CLI shares the same YANG models used by the external API interfaces such as NETCONF and gRPC, enabling seamless integration with model-driven automation workflows. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/get-started-md-cli-user.html#unique_1083917134).

In model-driven configuration mode, the MD-CLI is the preferred CLI engine, and features such as commit history, configuration annotations, rollback, configuration groups, and MD-CLI command aliases are fully available. All nodes in this hackathon are operating in this mode by default. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/model-driven-management-interfaces.html#ai9exj5x4z).

In this hackathon, you will explore the MD-CLI hands-on across six progressive tasks:

- Navigating the interface
- Applying configurations
- Inspecting operational state
- Customizing your environment with aliases
- Managing configuration safety through checkpoints and rollback
- Managing configuration concurrently in a multi-session environment

By the end, you will have a solid foundation for operating Nokia SR OS routers using the model-driven approach.

## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.

### Navigating the MD-CLI

#### Key Concepts

##### The Two-Line Prompt
By default, the SR OS MD-CLI features a two-line prompt:

- Line 1: Shows baseline status indicator (`!`), uncommitted changes indicator (`*`), configuration mode (`ex`, `gl`, `pr`, `ro`), and current context in `[]`.
- Line 2: Shows the active CPM, your username, and the system name (e.g., `A:admin@g4-pe2#`).

More information about MD-CLI prompt can be found [here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/navigate.html#unique_591069178).
``` markdown title="Example prompt"
(pr)[/configure router "Base" bgp]
A:admin@g4-pe2#
```
/// details | Description
    type: tip

- **Baseline Status**: Absence of the baseline status indicator (`!`) signifies that the current candidate configuration baseline is synchronized with the running configuration.
- **Uncommitted Changes**: Absence of the uncommitted changes indicator (`*`) indicates no pending changes in the current candidate configuration.
- **Configuration Mode**: The user is currently navigating in (`pr`) (private) configuration mode.
- **Current context is**: `/configure router "Base" bgp`
- **Active CPM**: `A`
- **Username**: `admin`
- **System name**: `g4-pe2`
///

##### Configuration Modes

| Mode      | Reference                       |
| ----------- | ------------------------------------ |
|Exclusive (`ex`)	| Only one user can make changes|
|Global (`gl`)	| Shared candidate configuration datastore|
|Private (`pr`)  | Per-user private candidate configuration datastore|
|Read-only (`ro`)	|	View only|

1. Login to :material-router:PE2 MD-CLI and observe the prompt. Identify the CPM, username, and system name.

    !!! info "Connect to :material-router:PE2 from your group's hackathon instance"
        ```
        ssh admin@clab-srexperts-pe2
        ```

    ??? example "Observe the prompt"
        ``` bash
        [/]
        A:admin@g4-pe2#
        ```

2. Enter configuration mode: `edit-config private`

    ??? example "Configuration mode"
        ``` bash
        [/]
        A:admin@g4-pe2# edit-config private
        INFO: CLI #2070: Entering private configuration mode
        INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

        (pr)[/]
        A:admin@g4-pe2#
        ```

    ??? info "configuration regions"
        SR OS model-driven design features 4 different configuration regions (each one with its own dedicated datastores).

        | Region      | Description                       |
        | ----------- | ------------------------------------ |
        |configure | The main configuration |
        |bof	| boot options file|
        |debug	| debugging configuration|
        |li | lawful intercept |

        The main **configure** region is the one targeted by default when using `edit-config`. To enter a different configuration region, you have to specifiy it explicitly in the command:
        ``` title="entering bof region using private mode"
        A:admin@g4-pe2# edit-config bof private
        INFO: CLI #2070: Entering private configuration mode
        INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

        (pr:bof)[/]
        ```

        [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/system-management/model-driven-management-interfaces.html#ai9exj5x5a)


3. Navigate to the BGP context: `configure router bgp`

    ??? example "configure router bgp"
        ``` bash
        (pr)[/]
        A:admin@g4-pe2# configure router bgp

        (pr)[/configure router "Base" bgp]
        ```

4. Use the `tree` command to explore the command tree under the current context. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/navigate.html#ariaid-title33).
5. Use `back`, `top`, and `exit` commands to navigate between levels.
6. Use the `pwc` command to display the present working context. You can pick the desired output format (`model-path`, `gnmi-path`, `cli-path`, `json-instance-path`).

    ??? example "model-driven `pwc` options"
        Navigate to some configuration context first:
        ```
        (pr)[/]
        A:admin@g4-pe2# /configure router bgp group "iBGP-DC"

        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        ```
        Explore the `pwc` options:
        ``` bash hl_lines="2 7 12 17"
        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# pwc model-path
        Present Working Context:
        /nokia-conf:configure/router=Base/bgp/group=iBGP-DC

        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# pwc gnmi-path
        Present Working Context:
        /configure/router[router-name=Base]/bgp/group[group-name=iBGP-DC]

        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# pwc cli-path
        Present Working Context:
        /configure router "Base" bgp group "iBGP-DC"

        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# pwc json-instance-path
        Present Working Context:
        /nokia-conf:configure/router[router-name="Base"]/bgp/group[group-name="iBGP-DC"]
        ```
    ??? note "why is this useful?"
        While developing your application or scripts to interact with SR OS, you can easily discover the appropriate path syntax by using CLI `pwc` command.

        | option      | description                       |
        | ----------- | ------------------------------------ |
        |`model-path` | YANG-modeled format for RESTCONF|
        |`gnmi-path` |gNMI format for streaming telemetry|
        |`cli-path`	|MD-CLI format on a single line for copying and pasting|
        |`json-instance-path` |YANG-modeled format for pySROS|

7. Exit `/configure` context, and then quit configuration mode using `quit-config` command.

    ??? example "quitting from configuration mode"
        ```
        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# exit all

        (pr)[/]
        A:admin@g4-pe2# quit-config
        INFO: CLI #2074: Exiting private configuration mode

        [/]
        A:admin@g4-pe2#
        ```
#### Key Navigation Commands

| Action      | SR OS MD-CLI                       |
| ----------- | ------------------------------------ |
|Move back one level	| `back [number]`|
|Return to operational root	|`exit [all]`|
|Move to top level	|`top`|
|Show command tree |		`tree [flat] [detail]`|
|Switch CLI engines	|	`//`|
|Run a command in the other CLI engine	|   `//command`|
|Exit the CLI session |  `logout` |

A quick reference to these navigational commands can also be found in the [MD-CLI Quick Reference Guide](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-quick-reference/navigational-operational-commands.html#ariaid-title1).

#### Falling-back to Classic CLI engine
You can use `//`, `/!classic-cli`, and `/!md-cli` to toggle between model-driven and classic CLI engines.

A small subset of operational command functions is not yet available on model-driven. In order to run those, it's useful to briefly switch back to classic CLI engine (without making any intrusive configuration change). An example of such a command is the classic command `oam sdp-ping`.

:material-router: PE2 should have SDP `1111` configured. Run `oam sdp-ping 1111 count 1` from the classic CLI engine to test reachability of this SDP.

??? example "Toggling between CLI engines"
    ```
    [/]
    A:admin@g4-pe2# //
    INFO: CLI #2051: Switching to the classic CLI engine
    INFO: CLI #2050: Classic CLI modification of the configuration is not allowed - 'model-driven' management interface configuration mode active
    A:g4-pe2#
    ```

??? example "Explicilty toggling to `classic-cli` engine"
    ```
    [/]
    A:admin@g4-pe2# /!classic-cli
    INFO: CLI #2051: Switching to the classic CLI engine
    INFO: CLI #2050: Classic CLI modification of the configuration is not allowed - 'model-driven' management interface configuration mode active
    A:g4-pe2#
    ```

??? example "Toggle engine, run command, and switch back to original engine in one-shot"
    ```
    [/]
    A:admin@g4-pe2# //oam sdp-ping 1111 count 1
    INFO: CLI #2051: Switching to the classic CLI engine
    INFO: CLI #2050: Classic CLI modification of the configuration is not allowed - 'model-driven' management interface configuration mode active
    A:g3-pe2# /oam sdp-ping 1111 count 1

    --------------------------------------------------------------------
    Actual IP Address - Local  : 10.46.3.22
    Expected Peer IP  - Remote : 10.46.3.22
    Actual IP Address - Remote : 10.46.3.21
    Expected Peer IP  - Local  : 10.46.3.21
    IP Address Mismatch        : No
    --------------------------------------------------------------------
    Err SDP-ID Info             Local           Remote
    --------------------------------------------------
        SDP-ID:                 1111            N/A
        Administrative State:   Up              N/A
        Operative State:        Up              N/A
        Path MTU:               8910            N/A
        Response SDP Used:                      No
        IP Interface State:     Up
        Forwarding Class        be              be
        Profile                 Out             Out

    Request Result: Sent - Reply Received
    RTT: 24.2(ms)

    INFO: CLI #2052: Switching to the MD-CLI engine

    [/]
    A:admin@g4-pe2#
    ```

More information about switching between the classic CLI and the MD-CLI engines can be found [here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/switch-between-classic-cli-md-cli-engines.html#ai89jylu31).

??? note "Notes about using `//`"
    - `//` toggles between engines, it does not explicitly target a specific engine. If the file is executed from an unexpected starting engine, `//` will switch to the wrong engine.
    - The recommended alternatives are `/!classic-cli` and `/!md-cli`, which explicitly switch to the intended engine regardless of which engine the file execution started in.
    - Additionally, command completion and `?` help are not supported for commands following `//`, making it harder to validate commands.

#### SR OS MD-CLI and YANG Browsers

The following sites can be handy to discover or find MD-CLI commands and YANG paths. Displayed results can be filtered by combining different criteria:

| Site      |                      |
| ----------- | ------------------------------------ |
|[MD-CLI Explorer](https://documentation.nokia.com/sr/26-3/mdcli-explorer/index.html) | List and describe all MD-CLI configuration contexts and operational commands |
|[SR OS YANG Browser](https://yangbrowser.nokia.com/sros/26.3.R3) | List and describe all SR OS YANG paths  |

### Basic Configuration: Exploring & modifying an existing BGP setup

In this task, BGP is already configured and running on all SR OS nodes. Your goal is to inspect the existing configuration, understand its structure in the MD-CLI, make targeted modifications, and safely commit those changes using the transactional candidate datastore model.

The MD-CLI uses a **candidate configuration datastore** model. Changes are staged in the candidate configuration and only become active after a `commit` command is issued. This means you can safely explore and modify the candidate without impacting the running network until you are ready.

1. **Enter configuration mode and inspect the existing BGP configuration**

    Enter private configuration mode and navigate to the BGP context.


    Use the `info` command to display the current candidate configuration from this context.
    You should see the existing BGP groups and neighbors already configured.

    ??? example "info bgp"
        ``` bash
        (pr)[/configure router "Base" bgp]
        A:admin@g4-pe2# info
            admin-state enable
            loop-detect discard-route
            min-route-advertisement 1
            path-mtu-discovery true
            router-id 10.46.4.22
            inter-as-vpn true
            ibgp-multipath true
            advertise-inactive true
            rapid-withdrawal true
            peer-ip-tracking true
            rapid-update {
                vpn-ipv4 true
                vpn-ipv6 true
                evpn true
            }
            add-paths {
                ipv4 {
                    send 8
                    receive true
                }
                ipv6 {
                    send 8
                    receive true
                }
                evpn {
                    send 8
                    receive true
                }
            }
            extended-nh-encoding {
                vpn-ipv4 true
                label-ipv4 true
                ipv4 true
            }
            next-hop-resolution {
                shortcut-tunnel {
                    family ipv4 {
                        resolution filter
                        resolution-filter {
                            sr-isis true
                        }
                    }
                    family ipv6 {
                        resolution filter
                        resolution-filter {
                            sr-isis true
                        }
                    }
                }
                labeled-routes {
                    transport-tunnel {
                        family vpn {
                            resolution filter
                            resolution-filter {
                                sr-isis true
                            }
                        }
                    }
                }
            }
            multipath {
                max-paths 64
                ebgp 64
                ibgp 64
                family ipv4 {
                }
                family ipv6 {
                }
            }
            group "dc1" {
                admin-state enable
                peer-as 4200001000
                family {
                    ipv4 true
                    ipv6 true
                }
                send-default {
                    ipv4 true
                    ipv6 true
                }
                import {
                    policy ["eBGP-accept-dc"]
                }
                export {
                    policy ["eBGP-redist-dc"]
                }
                advertise-ipv6-next-hops {
                    ipv4 true
                }
                dynamic-neighbor {
                    interface "spine11" {
                        allowed-peer-as ["4200001000"]
                    }
                    interface "spine12" {
                        allowed-peer-as ["4200001000"]
                    }
                }
            }
            group "iBGP-CORE" {
                admin-state enable
                connect-retry 1
                peer-as 65000
                family {
                    ipv4 true
                    vpn-ipv4 true
                    ipv6 true
                    vpn-ipv6 true
                    evpn true
                }
                export {
                    policy ["iBGP-redist"]
                }
                advertise-ipv6-next-hops {
                    vpn-ipv6 true
                    label-ipv6 true
                    evpn true
                    vpn-ipv4 true
                    label-ipv4 true
                    ipv4 true
                }
            }
            group "iBGP-DC" {
                admin-state enable
                connect-retry 1
                peer-as 65000
                family {
                    evpn true
                }
                advertise-ipv6-next-hops {
                    evpn true
                }
            }
            neighbor "fd00:fde8::4:11" {
                admin-state enable
                group "iBGP-CORE"
            }
            neighbor "fd00:fde8::4:12" {
                admin-state enable
                group "iBGP-CORE"
            }
            neighbor "fd00:fde8::4:13" {
                admin-state enable
                group "iBGP-DC"
            }
        ```


    Use the `info detail` command to also see default values that are not explicitly configured.


2. **Inspect the running configuration and compare**

    Use `info from running` command to see what is currently active on the router, then use the `compare` command to confirm there are no pending changes before you start.

    ??? example "compare"
        ``` bash
        (pr)[/configure router "Base"]
        A:admin@g4-pe2# compare
        ```
    No output from `compare` means the candidate and running configurations are identical which means a clean starting point.

3. **Modify an existing BGP neighbor**

    Make a targeted change to an existing configured neighbor, for example, change keepalive and hold-time value to one of the neighbors.
    /// tip

    From the `[/configure router "Base" bgp]` context, you can use `info neighbor *` to list all configured neighbors along with their respective configurations.
    ///

    ??? example "modifying configuration"
        ``` bash
        (pr)[/configure router "Base" bgp]
        A:admin@g4-pe2# neighbor "xxxx:xxxx::x:xx" keepalive 10

        *[pr:/configure router "Base" bgp]
        A:admin@g4-pe2# neighbor "xxxx:xxxx::x:xx" hold-time seconds 30
        ```

    Optionally you can use the `annotate` feature to leave a comment embedded in the configuration. Create a comment associated to the neighbor you are modifying.
    ??? example "embedding comments using `annotate`"
        ``` bash
        *(pr)[:/configure router "Base" bgp]
        A:admin@g4-pe2# annotate "this neighbor is being used to perform tests" neighbor "xxxx:xxxx::x:xx"
        ```

    Use the `compare` command to review your staged changes before committing.


    ??? example "reviewing pending changes with `compare`"
        ``` bash
        *(pr)[/configure router "Base" bgp]
        A:admin@g4-pe2# compare
        +   # comment: this neighbor is being used to perform tests
            neighbor "xxxx:xxxx::x:xx" {
        +       keepalive 10
        +       hold-time {
        +           seconds 30
        +       }
            }
        ```
    The `*` in the prompt indicates there are uncommitted changes in the candidate configuration.

4. **Validate and commit**

    Before committing, validate the candidate configuration using the `validate` command to catch any errors.

    ??? example "validate"
        ```
        *(pr)[/configure router "Base" bgp]
        A:admin@g4-pe2# top

        *(pr)[/configure]
        A:admin@g4-pe2# validate
        ```

    If validation passes, commit with a descriptive comment.

    ??? example "commit"
        ```
        *(pr)[/configure]
        A:admin@g4-pe2# commit comment "Modified BGP neighbor keepalive and hold-time"
        ```


    You will notice that an optional `comment` parameter has been added to `commit` which allows you to provide some meaningful description of what you did for subsequent troubleshooting and audit purposes.  This is optional, but recommended.

    After a successful commit, the `*` disappears from the prompt, confirming the running configuration now matches the candidate.

    You can also run the `compare` command to validate that there are no outstanding changes/differences between the running and candidate configuration datastores.  The output should be empty now.

5. **Discard unwanted changes**

    If you want to undo a specific change without discarding everything, use the `discard` command with a path. For example, to discard only the BGP changes.


    ??? example "discard a specific change"
        ``` bash
        *(pr)[/configure system]
        A:admin@g4-pe2# discard /configure router bgp
        ```

    Or, from within the BGP context, issue `discard` command without a path to discard all changes from the current context downward.

    ??? example "discard within the path"
        ``` bash
        *(pr)[/configure router "Base" bgp]
        A:admin@g4-pe2# discard

        ```

    More information about discarding changes can be found [here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/edit-configuration.html#ai89jylu19).

6. **Quit configuration mode**, back to the operational mode

    ??? example "quit configuration mode"
        ``` bash
        exit all
        quit-config
        ```

#### Inspect operational state

MD-CLI allows you to navigate through the whole YANG modeled `/state` tree and display operational information using the `info` command at the different contexts (in similar fashion to configuration mode).
MD-CLI exposes state in the `/state` path.

1. Type `state` to enter the `/state` context.

    ??? example "entering state"
        ```
        [/]
        A:admin@g4-pe2# state

        [/state]
        ```

2. Navigate into the bgp neighbor context (same neighbor used in last task)

    ??? example "navigating into the bgp neighbor state context"
        ```
        [/state]
        A:admin@g4-pe2# router bgp neighbor "xxxx:xxxx::x:xx"

        [/state router "Base" bgp neighbor "xxxx:xxxx::x:xx"]
        A:admin@g4-pe2#
        ```

3. Use `info` to display the context state information.

    ??? example "bgp neighbor state"
        ``` hl_lines="6 9 15 17 19"
        [/state router "Base" bgp neighbor "xxxx:xxxx::x:11"]
        A:admin@g4-pe2# info
            statistics {
                peer-port 179
                local-port 61289
                session-state "Established"
                last-state "Active"
                last-event "recvOpen"
                last-error "Cease (Other Configuration Change)"
                negotiated-family ["EVPN" "IPv4" "IPv6" "VPN-IPv4" "VPN-IPv6"]
                operational-local-address "xxxx:xxxx::x:22"
                operational-remote-address "xxxx:xxxx::x:11"
                peer-identifier "XX.XX.XX.11"
                established-transitions 5
                last-established-time XXXX-XX-XXTXX:XX:XX.X+00:00
                in-update-elapsed-time 455
                hold-time-interval 30
                remaining-idle-hold-time 0
                keep-alive-interval 10
                (...)
            (...)
        ```
        If the `hold-time` and `keepalive` were modified as suggested in previous task, you shall see the new operational timers and that a session re-establishment occured (which would be expected due to `hold-time` renegotiation).


### CLI aliasing & environment settings

The MD-CLI supports two levels of environment configuration:

- Global environment (`configure system management-interface cli md-cli environment`): persistent, applies to new sessions only.
- Per-session environment (`environment` context): not persistent, applies only to the current session.

More information about environment commands can be found [here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/navigate.html#unique_324622772).

#### What are aliases?

Aliases allow operators to define custom command names that execute MD-CLI commands or Python applications. They are displayed in command completion and `?` help.

In Nokia SR OS MD-CLI, the `mount-point` parameter within a command alias definition specifies the CLI context(s) from which the alias is accessible and executable. An alias can be mounted **globally** using `mount-point global`, making it available from any MD-CLI context, or it can be mounted at one or more **specific paths** (e.g., `mount-point "/show"` or `mount-point "/tools perform"`), which restricts the alias to only those contexts, attempting to invoke it from an unmounted context results in an `Unknown element` error. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/navigate.html#concept_tz4_jd3_bqb).

!!! note
    Alias names must not conflict with MD-CLI root elements (e.g., `admin`) or global commands (e.g., `insert`).

1. **Create a navigation shortcut alias**

    Create a navigation shortcut alias named `go-to-alias` that automatically navigates the user directly to the `configure system management-interface cli md-cli environment command-alias` context, which is the location where command aliases are managed to be executed from any MD-CLI context (`mount-point global`).


    ??? example "configure alias"
        ``` bash
        /configure system management-interface cli md-cli environment command-alias alias "go-to-alias"
        admin-state enable
        cli-command "configure system management-interface cli md-cli environment command-alias"
        mount-point global { }
        ```
    Then use it:

    !!! note

        Changes made to the global environment configuration apply only to new sessions and do not affect current sessions.

        You will need to start a new session (or log out and log in again) for the configured alias in the global configuration context to take effect.


    ??? example "use alias"
        ``` bash
        (pr)[/configure router "Base" bgp]
        A:admin@g4-pe2# go-to-alias

        (pr)[/configure system management-interface cli md-cli environment command-alias]
        A:admin@g4-pe2#
        ```

2. **Create an alias with a dynamic key parameter**


    ??? example "configure alias with parameter"
        ``` bash
        (pr)[/configure system management-interface cli md-cli environment command-alias]
        A:admin@g4-pe2#
            alias "vprn-state" {
                admin-state enable
                cli-command "info candidate /state service vprn"
                mount-point "/show" { }
            }
        ```

    Usage:

    ??? example "use alias"
        ``` bash
        A:admin@g4-pe2# show vprn-state 200
        ```

3. **Create an alias with output modifiers**


    ??? example "configure alias with an output modifier"
        ``` bash
        (pr)[/configure system management-interface cli md-cli environment command-alias]
        A:admin@g4-pe2#
            alias "bgp-top-line" {
                admin-state enable
                cli-command "show router bgp summary | match \"AS:\""
                mount-point global { }
            }
        ```

    ??? example "use alias"
        ``` bash
        A:admin@g4-pe2# bgp-top-line
        BGP Router ID:10.46.4.22       AS:65000       Local AS:65000

        ```

Now that you are familiar with alias definition in the SR OS model-driven CLI, try to configure following aliases:

- `show sap` :material-arrow-right: `show service sap-using`

- `show services` :material-arrow-right: `show service services-using`

- `show logs` :material-arrow-right: `show log log-id 99`


### Rollback in MD-CLI

In the MD-CLI, the `rollback` command loads a previously saved configuration file into the **candidate configuration**. It does not automatically commit, you can review the candidate before committing. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/edit-configuration.html#unique_1649078562).

#### How it works

The rollback command is equivalent to a `load full-replace` with a saved configuration file. It can be specified by:

- A saved configuration number (e.g., `rollback 1`, `rollback 3`, `rollback <number>`).

- A commit history identifier (e.g., `rollback commit-id 3`, `rollback commit-id <number>`).

- The `rollback 0`,  loads the last saved `config.cfg`.


!!! note "`load full-replace`"
    The `load full-replace` command is used in the MD-CLI to replace the entire candidate configuration with the contents of a specified file.
    `load full-replace` discards the current candidate configuration entirely and replaces it with the contents of the specified file.

More information about load and replace configuration can be found [here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-quick-reference/configuration-workflow-commands.html#ai89d5m910).

#### Commit confirmed: a safety net for rollback

The MD-CLI also offers `commit confirmed`, which activates changes **for a defined period of time**; changes take operational effect immediately in the running configuration. An automatic rollback occurs after a default timeout of **10 minutes** unless the operator explicitly confirms with `commit confirmed accept`. To cancel immediately and roll back, use commit confirmed cancel. [More information can be found here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/edit-configuration.html#d2e10113)

On rollback (timer expiry, `commit confirmed cancel`, session exit, or disconnect): The running configuration is reverted to its state before the commit was issued, and the changes are returned to the candidate configuration datastore.

In the following tasks, you will add a BGP route policy that will cause route withdrawals in the routing table. By the help of the `commit confirmed` and `rollback` options you will avoid the wrong configuration to impact the network more than **a defined period of time**.

Before applying any change to the BGP route policy, check the route table.

??? "checks before change"

    /// tab | "route table"
    ``` bash hl_lines="9"
    A:admin@g4-pe2# show router route-table summary
    ===============================================================================
    Route Table Summary (Router: Base)
    ===============================================================================
                                Active                   Available
    -------------------------------------------------------------------------------
    Aggregate                     2                        2
    ARP-ND                        0                        0
    BGP                           23                       23
    BGP (Backup)                  0                        0
    BGP_LABEL                     0                        0
    DHCP-CLNT                     0                        0
    Direct                        7                        7
    ESMBCAST                      0                        0
    Host                          0                        6
    ISIS                          25                       25
    ISIS (LFA)                    11                       11
    LDP                           0                        0
    Managed                       0                        0
    NAT                           0                        0
    OSPF                          0                        0
    OSPF (LFA)                    0                        0
    OSPFv3                        0                        0
    OSPFv3 (LFA)                  0                        0
    Periodic                      0                        0
    RIB-API                       0                        0
    RIP                           0                        0
    Static                        0                        0
    Sub Mgmt                      0                        0
    Video                         0                        0
    VPN Leak                      0                        0
    -------------------------------------------------------------------------------
    Total                         57                       63
    ===============================================================================
    NOTE: ISIS/OSPF LFA routes and BGP/BGP-VPN Backup routes are not counted
        towards the total.
    ===============================================================================
    ```
    ///
    /// tab | "bgp summary"
    ``` bash hl_lines="13 14 19 20"

    A:admin@g4-pe2# show router bgp summary all
    ===============================================================================
    BGP Summary
    ===============================================================================
    Legend : D - Dynamic Neighbor
    ===============================================================================
    Neighbor
    Description
    ServiceId          AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                        PktSent OutQ
    -------------------------------------------------------------------------------
    fd00:fde8::4:11
    Def. Inst       65000   13912    0 04d18h56m 47/22/2 (IPv4)
                            13820    0           49/17/2 (IPv6)
                                                16/11/6 (VpnIPv4)
                                                8/7/2 (VpnIPv6)
                                                16/2/8 (Evpn)
    fd00:fde8::4:12
    Def. Inst       65000   13910    0 04d18h56m 47/1/2 (IPv4)
                            13817    0           49/0/2 (IPv6)
                                                18/0/6 (VpnIPv4)
                                                10/0/2 (VpnIPv6)
                                                28/0/8 (Evpn)
    fd00:fde8::4:13
    Def. Inst       65000   23107    0 04d18h56m 89/0/8 (Evpn)
                            13803    0
    ```
    ///


1. **Make a change and commit:** Configure a policy with `default-action { action-type reject }` and apply it to the BGP group `"iBGP-CORE"` as an import policy. Use commented commits to facilitate identification when performing a rollback.

    ??? example "policy configuration"
        ``` bash
        /configure policy-options policy-statement "test-rollback" default-action action-type reject
        commit comment policy-test-configured
        ```

    Apply the configured `policy-statement` as an import policy to the existing bgp group "iBGP-CORE" and commit.

    ??? example "apply import policy to bgp group"
        ``` bash
        /configure router bgp group "iBGP-CORE" import policy "test-rollback"
        commit comment policy-test-applied
        ```


2. **Identify the issue:** Check the route table and compare with the results recorded before the change. It is obvious that routes rejected by the import policy are not installed in the route table, causing route withdrawals and traffic loss.


    ??? "checks after change"

        /// tab | "route table"
        ``` bash hl_lines="10"
        A:admin@g4-pe2# show router route-table summary

        ===============================================================================
        Route Table Summary (Router: Base)
        ===============================================================================
                                    Active                   Available
        -------------------------------------------------------------------------------
        Aggregate                     2                        2
        ARP-ND                        0                        0
        BGP                           0                        0
        BGP (Backup)                  0                        0
        BGP_LABEL                     0                        0
        DHCP-CLNT                     0                        0
        Direct                        7                        7
        ESMBCAST                      0                        0
        Host                          0                        6
        ISIS                          25                       25
        ISIS (LFA)                    11                       11
        LDP                           0                        0
        Managed                       0                        0
        NAT                           0                        0
        OSPF                          0                        0
        OSPF (LFA)                    0                        0
        OSPFv3                        0                        0
        OSPFv3 (LFA)                  0                        0
        Periodic                      0                        0
        RIB-API                       0                        0
        RIP                           0                        0
        Static                        0                        0
        Sub Mgmt                      0                        0
        Video                         0                        0
        VPN Leak                      0                        0
        -------------------------------------------------------------------------------
        Total                         34                       40
        ===============================================================================
        NOTE: ISIS/OSPF LFA routes and BGP/BGP-VPN Backup routes are not counted
            towards the total.
        ===============================================================================
        ```
        ///
        /// tab | "bgp summary"
        ``` bash hl_lines="14 15 20 21"
        A:admin@g4-pe2# show router bgp summary all

        ===============================================================================
        BGP Summary
        ===============================================================================
        Legend : D - Dynamic Neighbor
        ===============================================================================
        Neighbor
        Description
        ServiceId          AS PktRcvd InQ  Up/Down   State|Rcv/Act/Sent (Addr Family)
                            PktSent OutQ
        -------------------------------------------------------------------------------
        fd00:fde8::4:11
        Def. Inst       65000   14004    0 04d19h41m 47/0/2 (IPv4)
                                13912    0           49/0/2 (IPv6)
                                                    16/11/6 (VpnIPv4)
                                                    8/7/2 (VpnIPv6)
                                                    16/2/8 (Evpn)
        fd00:fde8::4:12
        Def. Inst       65000   14002    0 04d19h41m 47/0/2 (IPv4)
                                13909    0           49/0/2 (IPv6)
                                                    18/0/6 (VpnIPv4)
                                                    10/0/2 (VpnIPv6)
                                                    28/0/8 (Evpn)
        fd00:fde8::4:13
        Def. Inst       65000   23251    0 04d19h41m 89/0/8 (Evpn)
                                13893    0
        ```
        ///


3. **Check commit history:**
    Use Tab completion on `rollback commit-id` or on `rollback` to find the last known-good commit.

    !!! note
        The `rollback` command is only available in model-driven management interface configuration mode and must be executed from the root of the configuration branch (`/configure`)

    ??? example "decide on the good `commit-id`/`rollback-id` to rollback to"
        /// tab | commit-id
        ```bash hl_lines="4 10"
        (pr)[/configure]
        A:admin@g4-pe2# rollback commit-id <Tab>

        <commit-id>
        16
        Committed 2026-05-04T13:47:14.9+00:00 by admin (MD-CLI) from 10.128.4.1
        Comment   "policy-test-applied"
        Location  "cf3:\config.cfg"
        15
        Committed 2026-05-04T13:30:58.4+00:00 by admin (MD-CLI) from 10.128.4.1
        Comment   "policy-test-configured"
        Location  "cf3:\config.cfg.1"
        14
        Committed 2026-05-04T13:30:12.8+00:00 by admin (MD-CLI) from 10.128.4.1
        Location  "cf3:\config.cfg.2"
        . . .
        ```
        ///
        /// tab | rollback-id
        ```bash hl_lines="4 11"
        (pr)[/configure]
        A:admin@g4-pe2# rollback <Tab>

        <rollback-id>
        startup - The configuration that will be loaded by the system when it boots
        0
        Committed 2026-05-04T13:47:14.9+00:00 by admin (MD-CLI) from 10.128.4.1
        Comment   "policy-test-applied"
        Location  "cf3:\config.cfg"
        1
        Committed 2026-05-04T13:30:58.4+00:00 by admin (MD-CLI) from 10.128.4.1
        Comment   "policy-test-configured"
        Location  "cf3:\config.cfg.1"
        2
        Committed 2026-05-04T13:30:12.8+00:00 by admin (MD-CLI) from 10.128.4.1
        Location  "cf3:\config.cfg.2"
        . . .
        ```
        ///
The system displays commit IDs with timestamps, users, and comments.

4. **Load the previous configuration** into the candidate:

    ??? example "perform rollback"
        ```
        (pr)[/configure]
        A:admin@g4-pe2# rollback commit-id 15
        Loaded 1,620 lines in 0.2 seconds from file "cf3:\config.cfg.1"

        ```

5. **Inspect the candidate** before committing:


    ??? example "compare"
        ```bash
        *(pr)[/configure]
        A:admin@g4-pe2# compare
            router "Base" {
                bgp {
                    group "iBGP-CORE" {
        -               import {
        -                   policy ["test-rollback"]
        -               }
                    }
                }
            }

        ```


6. **Commit with confirmation** to safely test the rollback:

    ??? example "commit confirmed"
        ```
        *(pr)[/configure]
        A:admin@g4-pe2# commit confirmed

        INFO: CLI #2090: Commit confirmed - automatic rollback in 9 minutes 59 seconds

        ```

    If traffic recovers (bgp routes back to the routing table), confirm permanently:

    ??? example "accept confirm"
        ```
        (pr)[/configure]
        A:admin@g4-pe2# commit confirmed accept
        INFO: CLI #2092: Commit confirmed - accepted - automatic rollback canceled

        ```

    There is also the option `commit confirmed cancel` in case a `commit confirmed` does not lead to expected outcome that is not the case in our example.
    Below you can find a sample showcase.

    ??? example "cancel confirm"
        ```
        (pr)[/configure]
        A:admin@g4-pe2# commit confirmed cancel
        INFO: CLI #2096: Commit confirmed - canceled - automatic rollback of changes

        ```

This workflow provides a safe, non-disruptive recovery path, changes in unaffected areas of the configuration are not impacted, and the operator retains full control before making changes permanent.

### Concurrent configuration access

What happens when multiple users attempt to access or edit the configuration at the same time? In this exercise, you'll explore how the different configuration modes interact in a multi-session environment.

[Find detailed information about this topic here](https://documentation.nokia.com/sr/26-3/7x50-shared/md-cli-user/edit-configuration.html#ai89jylu01)

Open two parallel CLI sessions to :material-router:PE2. We will refer to them as session-1 and session-2 in the following tasks.
```
ssh admin@clab-srexperts-pe2
```

#### The shared candidate

Exclusive(`ex`), global(`gl`) and read-only(`ro`) configuration modes share the same candidate configuration instance at all times. `ro` mode has read-only access, while both `ex` and `gl` have read-write access.

1. Enter global(`gl`) configuration mode on both session-1 and session-2.

    ??? example "entering global configuration mode"
        ```
        [/]
        A:admin@g4-pe2# edit-config global
        INFO: CLI #2054: Entering global configuration mode

        (gl)[/]
        A:admin@g4-pe2#
        ```

2. On session-1, navigate to `/configure router "Base" bgp group "iBGP-DC"` and make a configuration change (don't commit yet). Then, run `compare` on session-2. Do you see the same pending changes?

    ??? example "session-1: making a change in the shared candidate"
        ``` title="session-1"
            (gl)[/configure router "Base" bgp group "iBGP-DC"]
            A:admin@g4-pe2# description session1
        ```
        ``` title="session-2"
            (gl)[/]
            A:admin@g4-pe2# compare
                configure {
                    router "Base" {
                        bgp {
                            group "iBGP-DC" {
            +                   description "session1"
                            }
                        }
                    }
                }
        ```
        Because global configuration mode uses the shared candidate instance, the same changes are immediatly visible in both sessions.

3. On session-2, exit the configuration mode using `quit-config` and attempt to enter exclusive(`ex`) candidate configuration mode. Does the system allow it?

    ??? example "session-2: attempt to enter exclusive configuration mode"
        ```
        (gl)[/]
        A:admin@g4-pe2# quit-config
        INFO: CLI #2056: Exiting global configuration mode

        [/]
        A:admin@g4-pe2# edit-config exclusive
        MINOR: MGMT_CORE #2052: Exclusive datastore access unavailable - model-driven interface editing global candidate
        ```
        The exclusive(`ex`) configuration mode can have exclusive write-access to both the running configuration datastore and the shared candidate configuration datastore. As session-1 is still in global(`gl`) configuration mode, exclusive write-access cannot be obtained at this time.


4. On session-1, either discard or commit the pending changes on session-1 and then `quit-config`. Try entering exclusive configuration mode on session-2 again.

    ??? example "session-2: entering exclusive configuration mode"
        ``` title="session-1"
        *(gl)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# commit

        (gl)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# exit

        (gl)[/]
        A:admin@g4-pe2# quit-config
        INFO: CLI #2056: Exiting global configuration mode
        ```
        ``` title="session-2"
        [/]
        A:admin@g4-pe2# edit-config exclusive
        INFO: CLI #2060: Entering exclusive configuration mode
        INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

        (ex)[/]
        A:admin@g4-pe2#

        ```

5. Make a configuration change from session-2 while in exclusive configuration mode (without committing). Can you figure out a way to see those pending changes from session-1?

    ??? example "session-1: monitoring shared candidate pending changes"
        ``` title="session-1"
        [/]
        A:admin@g4-pe2# edit-config global
        MINOR: MGMT_CORE #2051: Global datastore access unavailable - the MD-CLI has exclusive lock on configuration

        [/]
        A:admin@g4-pe2#

        [/]
        A:admin@g4-pe2# edit-config read-only
        INFO: CLI #2066: Entering read-only configuration mode

        (ro)[/]
        A:admin@g4-pe2#
        ```
        ``` title="session-2"
        (ex)[/]
        A:admin@g4-pe2# configure router bgp group "iBGP-DC"

        (ex)[/configure router "Base" bgp group "iBGP-DC"]

        (ex)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# delete description

        *(ex)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# connect-retry 2

        *(ex)[/configure router "Base" bgp group "iBGP-DC"]
        ```
        ``` title="session-1"
        (ro)[/]
        A:admin@g4-pe2# compare
            configure {
                router "Base" {
                    bgp {
                        group "iBGP-DC" {
        -                   description "session1"
        -                   connect-retry 1
        +                   connect-retry 2
                        }
                    }
                }
            }

        ```

        Attempts to enter global(`gl`) fail because session-2 has an exclusive write-access lock for the shared candidate configuration. Since the read-only(`ro`) configuration mode shares the same candidate configuration instance and can't make changes it can be combined with an existing exclusive configuration mode session.


#### The private candidates

Each private(`pr`) mode session uses it's own private candidate configuration datastore, isolated from all other candidates in the system. This lets multiple users work on different parts of configuration at same time.

!!! note
    When entering private(`pr`) candidate configuration mode, the current `running` configuration is copied to the respective private candidate baseline. This baseline is not automatically updated if there are changes to the `running` configuration caused by a different session. The user is signaled that the baseline is outdated by the presence of a baseline status indicator (`!`) in the prompt.

1. Enter private(`pr`) configuration mode on both session-1 and session-2.

    ??? example "entering private configuration mode"
        ```
        [/]
        A:admin@g4-pe2# edit-config private
        INFO: CLI #2070: Entering private configuration mode
        INFO: CLI #2061: Uncommitted changes are discarded on configuration mode exit

        (pr)[/]
        ```

2. On session-1, configure a custom `keepalive` and `hold-time` on the bgp group `iBGP-DC` (but don't commit yet). Can you see those changes from session-2?

    ??? example "session-1: changing private candidate configuration"
        ``` title="session-1"
        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# hold-time seconds 30

        *(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# keepalive 10

        *(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# compare
        +   keepalive 10
        +   hold-time {
        +       seconds 30
        +   }
        ```
        ``` title="session-2"
        (pr)[/]
        A:admin@g4-pe2# compare

        (pr)[/]
        ```
        No changes appear on session-2 because the private candidates are isolated.

3. Commit the changes on session-1. Do you observe any change on session-2?

    ??? example "session-2 state after commit on session-1"
        ``` title="session-1"
        *(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# commit

        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2#
        ```
        ``` title="session-2"
        (pr)[/]
        A:admin@g4-pe2#

        !(pr)[/]
        A:admin@g4-pe2# info configure router bgp group "iBGP-DC"
            admin-state enable
            connect-retry 1
            peer-as 65000
            family {
                evpn true
            }
            advertise-ipv6-next-hops {
                evpn true
            }

        ```
        Despite the system `running` configuration being updated, note that those changes are not immediately seen in session-2's private candidate. This is because the candidate baseline does not sync automatically with the `running` configuration. Instead, the user is informed via the `!` indicator that the baseline is outdated.

4. On session-2, use `update` to sync the private candidate baseline with the current `running` configuration. Are the changes committed in session-1 visible now?

    ??? example "session-2: updating baseline"
        ``` title="session-2"
        !(pr)[/]
        A:admin@g4-pe2# update

        (pr)[/]
        A:admin@g4-pe2# info configure router bgp group "iBGP-DC"
            admin-state enable
            connect-retry 1
            keepalive 10
            peer-as 65000
            hold-time {
                seconds 30
            }
            family {
                evpn true
            }
            advertise-ipv6-next-hops {
                evpn true
            }

        ```
        After synchronizing the baseline configuration in session-2's private candidate configuration session to the `running` configuration with `update`, your changes become visible from session-2.

5. What happens if both session-1 and session-2 make conflicting changes? How can the the conflict be resolved?

    Try the following:

     - On session-1, change bgp group "iBGP-DC" `keepalive` to 15, and commit.
     - On session-2, change bgp group "iBGP-DC" `keepalive` to 20, and commit.

    ??? example "observing configuration change conflict"
        ``` title="session-1"
        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# keepalive 15

        *(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# compare
        -   keepalive 10
        +   keepalive 15

        *(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# commit
        ```
        ``` title="session-2"
        !(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# keepalive 20

        !*(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# compare
        -   keepalive 10
        +   keepalive 20

        !*(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# commit
        MINOR: MGMT_CORE #2703: Commit canceled - conflicts detected - use update
        ```
        The system detects that you are attempting to change a configuration section for which the current baseline is not synchronized with the `running` configuration. The change is detected as a conflict and the commit is rejected.

6. Resolve the conflict using `update`.

    ??? example "resolving conflict"
        ``` title="session-2"
        !*(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# update /configure
        ~   /configure router "Base" bgp group "iBGP-DC" keepalive 20
        ##  keepalive - exists with different value: keepalive 15 - change updated: replace existing value

        *(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# compare
        -   keepalive 15
        +   keepalive 20

        *(pr)[/configure router "Base" bgp group "iBGP-DC"]
        A:admin@g4-pe2# commit

        (pr)[/configure router "Base" bgp group "iBGP-DC"]
        ```
        After synchronizing the baseline configuration in session-2's private candidate configuration session to the `running` configuration with `update` once again, the conflict is resolved and your commit can proceed.

## Summary
Congratulations!  You have completed the activity.

If you have completed all the tasks above, you have gone through a progressive learning path: from orientation and navigation, through configuration and operational state inspection, to productivity features (aliases) and operational resilience (rollback and managing concurrent configuration access). Each task builds on the previous, giving a comprehensive introduction to the Nokia SR OS MD-CLI.

Here is a short summary table of some topics you have covered:

| Concept      | MD-CLI Approach                         |
| ----------- | ------------------------------------ |
|Configuration mode	| `private`, `global`, `exclusive` or `read-only` (transactional, candidate-based)|
|Apply changes	|`commit`|
|Undo uncommitted changes|	`discard`|
|Inspect changes	|`compare`|
|Inspect operational state |`info /state` |
|CLI shortcuts|	`environment command-alias`|
|Rollback|	`rollback` |

