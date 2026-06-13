---
tags:
  - MD-CLI
  - YANG-CLI
  - CLI
  - Introduction
---


# Introduction to the SR Linux YANG CLI


|                             |          |
| --------------------------- | ----------------------------------------- |
| **Activity name**           | Introduction to the SR Linux YANG CLI   |
| **Activity ID**             | 28    |
| **Short Description**       | Learn to efficiently navigate and operate the Nokia SR Linux Model-Driven CLI (MD-CLI) by understanding its prompt and modes, exploring configuration and state hierarchies, managing changes with commit/rollback workflows, using output modifiers, creating aliases, and leveraging command history.  |
| **Difficulty**              | Beginner   |
| **Tools used**              | SR Linux CLI   |
| **Topology Nodes**          | :material-router: leaf21, :material-router: leaf22, :material-router: leaf23, :material-router: spine21, :material-router: spine22    |
| **References**              | [CLI User Guide](https://documentation.nokia.com/srlinux/26-3/books/config-basics/configuration-management.html)<br/>[Getting Started with SR Linux CLI](https://learn.srlinux.dev/get-started/cli/)<br/> |

Nokia SR Linux is a modern, fully model-driven Network Operating System (NOS). Unlike traditional NOS platforms, SR Linux is built from the ground up on a 100% YANG-modelled infrastructure, meaning that every configuration element, state value, and operational action is defined by a YANG model. This ensures consistency across the CLI, NETCONF, and gRPC management interfaces.

*This activity is designed as a starter guide for those operators who have never used SR Linux before.  If you are familiar with SR Linux we suggest you tackle one of the other activities at the level you feel is appropriate.*

In this activity, you will explore the SR Linux CLI over four progressive tasks, navigating the interface, applying real configurations, customizing your environment with aliases, and managing configuration safety through checkpoints and rollback. By the end, you will have a solid foundation for operating Nokia SR Linux nodes using the model-driven approach.

## Objective

By completing this hackathon activity, you will gain practical, hands-on experience with the Nokia SR Linux CLI, a modern, YANG-based management interface that provides a consistent and structured approach to router configuration and operations. You will learn how to navigate the CLI hierarchy, apply and commit configurations using the transactional candidate datastore model, use output modifiers and wildcards for efficient operations, and safeguard network changes using rollback. The activity equips you with the foundational skills needed to confidently manage Nokia SR Linux nodes using the CLI in a model-driven operational environment.

## Technology Explanation

### SR Linux Architecture

-{{ image(url='./../../../../../images/28-srl-architecture.png', title='SR Linux Architecture', padding=10, shadow=true) }}-

The SR Linux CLI is a modern, powerful, and highly customizable text-based interface. It was designed to evolve the CLI paradigm, bringing features common in modern shells (such as context-aware autocompletion, structured output, and inline suggestions) to network operations.

If you're already an experienced SR OS operator you will find SR Linux familiar and highly extensible.  If you're not an SR OS user, you will also find SR Linux very familiar as it shares many of the characteristics of Linux. 

**Key benefits of the SR Linux CLI include:**

- **Transactional configuration:** Changes are made in a candidate datastore and only become active after a `commit` command is issued. A `diff` command allows you to review staged changes before applying them. [More information can be found here](https://documentation.nokia.com/srlinux/26-3/books/config-basics/configuration-management.html#configuration-modes).

- **Multiple CLI modes:** `running`, `candidate`, `show` and `state` modes allow operators to view configuration, make changes, and inspect state information, including counters and derived values, from a single consistent interface.

- **Structured data output:** Configuration and state can be displayed in JSON or YAML formats using the `| as json` and `| as yaml` output modifiers, making it easy to integrate with automation tools. [More information can be found here](https://documentation.nokia.com/srlinux/26-3/books/system-mgmt/cli-interface.html#cli-output-formatt-filter).

- **Wildcards and ranges:** Operators can apply configuration or retrieve state across multiple list elements simultaneously using `*` wildcards and `{x..y}` range syntax, enabling bulk configuration changes with a single command. [More information can be found here](https://documentation.nokia.com/srlinux/26-3/books/system-mgmt/cli-interface.html#ranges-and-wildcards).

- **Automation-ready:** The SR Linux CLI shares the same YANG models used by the external API interfaces such as NETCONF, JSON-RPC and gRPC, enabling seamless integration with model-driven automation workflows.

The `running`, `candidate`, `show` and `state` modes are entered using the `enter` global command and provide a clean separation between viewing active configuration, staging changes, executing show commands to display information and inspecting operational state.


## Tasks

**You should read these tasks from top-to-bottom before beginning the activity**.  

It is tempting to skip ahead but tasks may require you to have completed previous tasks before tackling them.  

### Orientation, Navigating the SR Linux CLI

#### Key Concepts

##### The Two-Line Prompt

By default, the SR Linux CLI features a two-line prompt:

- Line 1: Shows the current CLI mode (`running`, `candidate`, `show`, `state`) and the current context in `[  ]`.
- Line 2: Shows the CPM you are connected to, the username and the hostname (e.g., `A:admin@g1-leaf21#`).

``` srl
--{ running }--[  ]--
A:admin@g1-leaf21#
```

``` srl
--{ * candidate shared default }--[ network-instance default protocols bgp ]--
A:admin@g1-leaf21#
```

The `*` prefix on the mode indicator means there are uncommitted changes in the candidate datastore.

**CLI Modes**

-{{ diagram(path='./../../../../../images/srl-cli-modes.drawio', title='CLI Modes in SR Linux', page=0, zoom=1.5) }}-


| Mode        | Description                                      |
| ----------- | ------------------------------------------------ |
| `running`   | View active configuration; execute operational commands; no config changes allowed |
| `candidate` | Stage configuration changes in the candidate datastore |
| `show` | Execute `show` CLI plugins to display information about configured features and operational states |
| `state`     | View configuration *and* state values (counters, oper-state, statistics, etc.) |

1. Log in and observe the prompt. Identify the CLI mode, current context, username, and hostname.

    ??? example "Observe the prompt"
        ```srl
        --{ + running }--[  ]--
        A:admin@g1-leaf21# show version
        -------------------------------------------------------------------------
        Hostname             : g1-leaf21
        Chassis Type         : 7220 IXR-D3L
        Part Number          : Sim Part No.
        Serial Number        : Sim Serial No.
        System HW MAC Address: 1A:0C:13:FF:00:00
        OS                   : SR Linux
        Software Version     : v26.3.1
        Build Number         : 410-g98ed16c774c
        Architecture         : x86_64
        Last Booted          : 2026-04-21T10:03:54.921Z
        Total Memory         : 65842952 kB
        Free Memory          : 8873776 kB
        -------------------------------------------------------------------------
        ```

2. Enter candidate configuration mode: `enter candidate`

    ??? example "Configuration mode"
        ``` srl
        --{ running }--[  ]--
        A:admin@g1-leaf21# enter candidate

        --{ candidate shared default }--[  ]--
        A:admin@g1-leaf21#
        ```

3. Navigate to the BGP context: `network-instance default protocols bgp`

    ??? example "YANG navigation"
        ``` srl
        --{ running }--[  ]--
        A:admin@g1-leaf21# network-instance default protocols bgp

        --{ candidate shared default }--[ network-instance default protocols bgp ]--
        A:admin@g1-leaf21#
        ```

4. Use the `tree` command to explore the command tree under the current context.

    /// admonition | Tool
        type: note
    To easily navigate the full YANG model, you can use the [SR Linux YANG browser](https://yangbrowser.nokia.com/srlinux/26.3.1)
    
    ///

5. Use `exit`, `exit all`, `exit to`, `back` and `/` to navigate between levels.

6. Use `pwc` to display the present working context.

7. Use the `info` command to inspect the datastore content.

    ??? example "Config inspection"
        ``` srl
        --{ running }--[  ]--
        A:admin@g1-leaf21# network-instance default protocols bgp


        --{ running }--[ network-instance default protocols bgp ]--
        A:admin@g1-leaf21# info autonomous-system
            autonomous-system 4200002001

        ```

8. Enter `state` mode to inspect operational state values alongside configuration.

    ??? example "Enter state mode"
        ``` srl
        --{ + running }--[  ]--
        A:admin@g1-leaf21# enter state


        --{ + state }--[  ]--
        A:admin@g1-leaf21# info interface ethernet-1/1 oper-state
            oper-state up
        ```

    /// admonition | Note
    Instead of entering a specific CLI mode, you can also pull information from a specific datastore using the `from` keyword:
    ```srl
    --{ + running }--[  ]--
    A:admin@g1-leaf21# info from state interface ethernet-1/1 oper-state
        oper-state up
    ```
    ///

#### Key Navigation Commands

| Action                          | SR Linux CLI                         |
| ------------------------------- | ------------------------------------ |
| Move back one level             | `exit`                               |
| Exit to a specific parent       | `exit to <context>`                  |
| Move to root context            | `/`                                  |
| Show command tree               | `tree`                               |
| Show present working context    | `pwc`                                |
| Enter candidate mode            | `enter candidate`                    |
| Enter show mode                 | `enter show`                    |
| Enter running mode              | `enter runnning`                    |
| Enter state mode                | `enter state`                        |
| List available commands         | `?` or `??` (global commands too)    |


### Basic Configuration, Exploring & Modifying an Existing BGP Setup

SR Linux uses a **candidate configuration datastore** model, changes are staged in the candidate configuration and only become active after a `commit` command is issued. This means you can safely explore and modify the candidate without impacting the running network until you are ready.

In this task, BGP is already configured and running on all SR Linux nodes. Your goal is to inspect the existing configuration, understand its structure in the SR Linux CLI, make targeted modifications, and safely commit those changes.

1. **Enter configuration mode and inspect the existing BGP configuration:**

    Enter candidate mode and navigate to the BGP context for the default network instance.

    ??? example "navigate to BGP context"
        === "Commands"
            ```
            enter candidate
            ```
            ```
            network-instance default protocols bgp
            ```
        === "Expected output"
            ``` srl
            --{ running }--[  ]--
            A:admin@g1-leaf21# enter candidate

            --{ candidate shared default }--[  ]--
            A:admin@g1-leaf21# network-instance default protocols bgp

            --{ candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21#
            ```

    Use `info` to display the current candidate configuration from this context.
    You should see the existing BGP groups and neighbors already configured.

    ??? example "info bgp"
        === "Commands"
            ```
            info
            ```
        === "Expected output"
            ``` srl
            --{ + candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21# info
                autonomous-system 4200002001
                router-id 10.46.1.43
                dynamic-neighbors {
                    interface ethernet-1/31.0 {
                        peer-group spine
                        allowed-peer-as [
                            4200002000
                        ]
                    }
                    interface ethernet-1/32.0 {
                        peer-group spine
                        allowed-peer-as [
                            4200002000
                        ]
                    }
                }
                ebgp-default-policy {
                    import-reject-all false
                    export-reject-all false
                }
                afi-safi evpn {
                    multipath {
                        allow-multiple-as true
                        ebgp {
                            maximum-paths 64
                        }
                        ibgp {
                            maximum-paths 64
                        }
                    }
                    evpn {
                        rapid-update true
                    }
                }
                afi-safi ipv4-unicast {
                    admin-state enable
                    multipath {
                        allow-multiple-as true
                        ebgp {
                            maximum-paths 32
                        }
                        ibgp {
                            maximum-paths 32
                        }
                    }
                    ipv4-unicast {
                        advertise-ipv6-next-hops true
                        receive-ipv6-next-hops true
                    }
                }
                afi-safi ipv6-unicast {
                    admin-state enable
                    multipath {
                        allow-multiple-as true
                        ebgp {
                            maximum-paths 32
                        }
                        ibgp {
                            maximum-paths 32
                        }
                    }
                }
                transport {
                    mtu-discovery true
                }
                group iBGP-DC {
                    next-hop-self true
                    peer-as 65000
                    afi-safi evpn {
                        admin-state enable
                    }
                    afi-safi ipv4-unicast {
                        admin-state disable
                    }
                    afi-safi ipv6-unicast {
                        admin-state disable
                    }
                    local-as {
                        as-number 65000
                        prepend-global-as false
                    }
                    timers {
                        connect-retry 1
                        minimum-advertisement-interval 1
                    }
                    transport {
                        local-address 10.46.1.43
                    }
                }
                group spine {
                    export-policy [
                        local
                    ]
                }
                neighbor fd00:fde8::1:13 {
                    peer-group iBGP-DC
                }
            ```

    Use `info detail` to also see default values that are not explicitly configured.

2. **Inspect the running configuration and compare:**

    Use `info from running` to see what is currently active on the router, then use `diff` to confirm there are no pending changes before you start.

    ??? example "diff"
        === "Commands"
            ```
            diff
            ```
        === "Expected output"
            ``` srl
            --{ candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21# diff
            ```
    No output from `diff` means the candidate and running configurations are identical, a clean starting point.

3. **Modify an existing BGP neighbor:**

    Make a targeted change to an existing neighbor, for example, add a description and a local-preference value to one of the neighbors.
    
    Use `diff` to review your staged changes before committing.

    ??? example "modify configuration"
        === "Commands"
            ```
            neighbor fd00:fde8::1:13 description "iBGP-DC overlay peer to vRR"
            ```
            ```
            neighbor fd00:fde8::1:13 local-preference 170
            ```
            ```
            diff
            ```
        === "Expected output"
            ``` srl
            --{ + candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21# neighbor fd00:fde8::1:13 description "iBGP-DC overlay peer to vRR"


            --{ +* candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21# neighbor fd00:fde8::1:13 local-preference 170


            --{ +* candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21# diff
                neighbor fd00:fde8::1:13 {
            +         description "iBGP-DC overlay peer to vRR"
            +         local-preference 170
                }

            ```

    The `*` in the prompt indicates there are uncommitted changes in the candidate configuration.

4. **Validate and commit:**

    Before committing, validate the candidate configuration using the `commit validate` command to catch any errors.

    ??? example "commit"
        === "Commands"
            ```
            commit validate
            ```
            ```
            commit now
            ```
        === "Expected output"
            ``` srl
            --{ +* candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21# commit validate
            All changes are valid.


            --{ +* candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21# commit now
            All changes have been committed. Leaving candidate mode.


            --{ + running }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21#
            ```

    After a successful commit, the `*` disappears from the prompt and the mode switches back to `running`, confirming the running configuration now matches the committed candidate.

    Alternatively, use `commit stay` to commit and stay in the candidate mode if you want to continue making config changes.

5. **Discard unwanted changes:**

    If you want to undo staged changes without committing them, use the `discard` command. For example, to discard all changes in the current candidate session:

    !!! example "discard all changes"
        ``` srl
        --{ * candidate shared default }--[  ]--
        A:admin@g1-leaf21# discard stay
        ```

    The `stay` keyword discards all changes but keeps you in candidate mode so you can continue editing. The `now` keyword discards changes and exits candidate mode.

    If you want to undo a specific change without discarding everyting, use the `discard` command with a specific YANG path.

    You can also use `load startup` to fully reset the candidate to the startup configuration:

    !!! example "load startup"
        ``` srl
        --{ * candidate shared default }--[  ]--
        A:admin@g1-leaf21# load startup
        ```


### Output Modifiers, Wildcards & CLI Aliasing

The SR Linux CLI supports environment customization at the session level, including command aliases, output modifiers, and powerful wildcard/range expressions.

1. **Use the `| as` output modifier to convert output to JSON, XML or YAML**

    The `| as json`, `| as xml` and `| as yaml` modifiers transform `info` output into structured formats, useful for scripting and automation.

    ??? example "info | as json"
        ``` srl
        --{ + running }--[ interface mgmt0 ]--
        A:admin@g1-leaf21# info | as json
        {
        "name": "mgmt0",
        "admin-state": "enable",
        "subinterface": [
            {
            "index": 0,
            "admin-state": "enable",
            "ipv4": {
                "admin-state": "enable",
                "dhcp-client": {
                }
            },
            "ipv6": {
                "admin-state": "enable",
                "dhcp-client": {
                }
            }
            }
        ]
        }
        ```

2. **Use wildcards and ranges for bulk configuration and queries**

    Wildcards (`*`) and ranges (`{x..y}`) allow you to target multiple YANG list elements in a single command, a powerful capability for bulk configuration and state inspection.

    ??? example "wildcard and range examples"
        ``` srl
        # View admin-state for interfaces 1 through 4
        info interface ethernet-1/{1..4} admin-state

        # View traffic rates for all interfaces in table format
        info from state interface * traffic-rate | filter fields in-bps out-bps | as table

        # Enable interfaces 5 through 10 in a single command
        interface ethernet-1/{5..10} admin-state enable

        # Set a description on a set of interfaces
        interface ethernet-1/{1,3..5,8} description "configured with range"
        ```

    ??? example "changing configuration using ranges"
        ``` srl
        --{ candidate shared default }--[  ]--
        A:admin@g1-leaf21# interface ethernet-1/{5..10} admin-state enable

        --{ * candidate shared default }--[  ]--
        A:admin@g1-leaf21# diff
        +     interface ethernet-1/5 {
        +         admin-state enable
        +     }
        +     interface ethernet-1/6 {
        +         admin-state enable
        +     }
        +     interface ethernet-1/7 {
        +         admin-state enable
        +     }
        +     interface ethernet-1/8 {
        +         admin-state enable
        +     }
        +     interface ethernet-1/9 {
        +         admin-state enable
        +     }
        +     interface ethernet-1/10 {
        +         admin-state enable
        +     }

        --{ * candidate shared default }--[  ]--
        A:admin@g1-leaf21# commit now
        ```

#### Output Modifiers Reference

| Modifier         | Description                                              |
| ---------------- | -------------------------------------------------------- |
| `| more`        | Paginate output                                          |
| `| as json`     | Transform output to JSON format                          |
| `| as yaml`     | Transform output to YAML format                          |
| `| as table`    | Transform output to table format                         |
| `| grep <str>`  | Filter output lines matching a string                    |
| `| head <n>`    | Show first N lines                                       |
| `| tail <n>`    | Show last N lines                                        |
| `| jq <expr>`   | Transform JSON output using jq                           |
| `| yq <expr>`   | Transform YAML output using yq                           |


#### What Are Aliases?

Aliases allow operators to define custom command names that map to longer SR Linux CLI commands.

3. **Create a navigation shortcut alias**

    !!! example "configure alias"
        === "Create alias"
            ``` srl
            environment alias "go-bgp" "/network-instance default protocols bgp"
            ```
        === "Use alias from any context"
            ``` srl
            --{ candidate shared default }--[  ]--
            A:admin@g1-leaf21# go-bgp

            --{ candidate shared default }--[ network-instance default protocols bgp ]--
            A:admin@g1-leaf21#
            ```

        !!! Warning
            The above way of defining an alias is session specific. Consider adding it to your configuration, to make the alias persistent across sessions.

            **Steps required:**
            ```title="enter candidate mode"
            enter candidate
            ```
            ```title="configure alias"
            /system cli environment alias go-bgp command "/network-instance default protocols bgp"
            ```
            ```title="commit changes"
            commit stay
            ```


4. **Create an alias with output modifiers**

    ??? example "configure alias with modifier"
        === "traffic-rate alias"
            ``` srl
            /system cli environment alias traffic-rate command "/info from state interface * traffic-rate | filter fields in-bps out-bps | as table"
            ```
        === "Expected output"
            ``` srl
            --{ + running }--[  ]--
            A:admin@g1-leaf21# traffic-rate
            +---------------------+----------------------+----------------------+
            |      Interface      |        In-bps        |       Out-bps        |
            +=====================+======================+======================+
            | ethernet-1/1        |                    0 |                  164 |
            | ethernet-1/2        |                  989 |                 1186 |
            | ethernet-1/3        |                      |                      |
            | ethernet-1/4        |                      |                      |
            | ethernet-1/5        |                      |                      |
            | ethernet-1/6        |                      |                      |
            | ethernet-1/7        |                      |                      |
            | ethernet-1/8        |                      |                      |
            | ethernet-1/9        |                      |                      |
            | ethernet-1/10       |                      |                      |
            | ethernet-1/11       |                      |                      |
            | ethernet-1/12       |                      |                      |
            | ethernet-1/13       |                      |                      |
            | ethernet-1/14       |                      |                      |
            | ethernet-1/15       |                      |                      |
            | ethernet-1/16       |                      |                      |
            | ethernet-1/17       |                      |                      |
            | ethernet-1/18       |                      |                      |
            | ethernet-1/19       |                      |                      |
            | ethernet-1/20       |                      |                      |
            | ethernet-1/21       |                      |                      |
            | ethernet-1/22       |                      |                      |
            | ethernet-1/23       |                      |                      |
            | ethernet-1/24       |                      |                      |
            | ethernet-1/25       |                      |                      |
            | ethernet-1/26       |                      |                      |
            | ethernet-1/27       |                      |                      |
            | ethernet-1/28       |                      |                      |
            | ethernet-1/29       |                      |                      |
            | ethernet-1/30       |                      |                      |
            | ethernet-1/31       |                  320 |                  323 |
            | ethernet-1/32       |                  457 |                  323 |
            | ethernet-1/33       |                      |                      |
            | ethernet-1/34       |                      |                      |
            | irb0                |                      |                      |
            | lag1                |                  989 |                 1186 |
            | mgmt0               |                12667 |               284334 |
            | system0             |                      |                      |
            +---------------------+----------------------+----------------------+
            ```

5. **Create an alias with an argument**

    ??? example "configure alias with an argument"
        === "bgp-neighbor alias"
            ``` srl
            /system cli environment alias "bgp-neighbor" command "/show network-instance default protocols bgp neighbor {}"
            ```
        === "Expected output"
            ``` srl
            --{ + running }--[  ]--
            A:admin@g1-leaf21# bgp-neighbor fd00:fde8::1:13
            ------------------------------------------------------------------------------------------------------------------------
            BGP neighbor summary for network-instance "default"
            Flags: S static, D dynamic, L discovered by LLDP, B BFD enabled, - disabled, * slow
            ------------------------------------------------------------------------------------------------------------------------
            ------------------------------------------------------------------------------------------------------------------------
            +------------+------------+------------+------------+------------+------------+------------+------------+------------+
            |  Net-Inst  |    Peer    |   Group    |   Flags    |  Peer-AS   |   State    |   Uptime   |  AFI/SAFI  | [Rx/Active |
            |            |            |            |            |            |            |            |            |    /Tx]    |
            +============+============+============+============+============+============+============+============+============+
            | default    | fd00:fde8: | iBGP-DC    | S          | 65000      | establishe | 4d:4h:58m: | evpn       | [58/58/23] |
            |            | :1:13      |            |            |            | d          | 13s        |            |            |
            +------------+------------+------------+------------+------------+------------+------------+------------+------------+
            ------------------------------------------------------------------------------------------------------------------------
            Summary:
            1 configured neighbors, 1 configured sessions are established, 0 disabled peers
            2 dynamic peers
            ```

Now that you are familiar with alias definition in SRL CLI, try to configure following aliases:

- `show system-logs` :material-arrow-right: `show system logging buffer system`
- `display up-int` :material-arrow-right: `display interfaces in the oper-state up`


### Checkpoint & Rollback

SR Linux supports configuration rollback via checkpoint files. This allows operators to revert to a previous known-good configuration with minimal service impact.

#### Key Behaviors

- Checkpoints are created explicitly by operators or automatically by the system (e.g., before a commit).
- The special `startup` checkpoint always reflects the startup configuration.
- Rolling back with `load checkpoint` stages the checkpoint as the new candidate, a subsequent `commit` is required to apply it.
- Checkpoints are stored in state under `/system/configuration/checkpoint[id=<name>]`.
- Each checkpoint is stored with an `id`, where `id = 0` represents the most recent checkpoint.
<!--  -->

1. **Save a named checkpoint before making changes**

    ??? example "save checkpoint"
        ``` srl
        --{ running }--[  ]--
        A:admin@g1-leaf21# tools system configuration generate-checkpoint name "before-bgp-changes"
        /system:
            Generated checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json' with name 'before-bgp-changes' and comment ''
        ```

2. **Make configuration changes, then revert**

    Make some configuration changes (e.g., modify a BGP neighbor). Then load the checkpoint to revert.

    ??? example "load checkpoint"
        ``` srl
        --{ + candidate shared default }--[  ]--
        A:admin@g1-leaf21# load checkpoint name before-bgp-changes
        /system/configuration/checkpoint[id=before-bgp-changes]:
            Loaded checkpoint '/etc/opt/srlinux/checkpoint/checkpoint-0.json'



        --{ +* candidate shared default }--[  ]--
        A:admin@g1-leaf21#
        ```

    Review the `diff` to confirm that the revert staged the expected changes, then `commit`.

    ??? example "commit after rollback"
        ``` srl
        --{ * candidate shared default }--[  ]--
        A:admin@g1-leaf21# diff
        # ... shows the reverted changes ...

        --{ * candidate shared default }--[  ]--
        A:admin@g1-leaf21# commit now
        ```

3. **Revert to the startup configuration**

    The special `startup` checkpoint always reflects the startup (boot) configuration and can be used to fully reset the node.

    ??? example "load startup checkpoint"
        ``` srl
        --{ + candidate shared default }--[  ]--
        A:admin@g1-leaf21# load startup auto-commit
        /system/configuration/checkpoint[id=__startup__]:
            Reverting to startup configuration

        /:
            Successfully reverted configuration

        ```

    !!! note
        `load startup auto-commit` both loads the startup checkpoint *and* commits it in a single step, bypassing the normal candidate review workflow. **Use with care**.

4. **List available checkpoints**

    ??? example "list checkpoints"
        ``` srl
        --{ running }--[  ]--
        A:admin@g1-leaf21# info from state / system configuration checkpoint * | as table | filter fields *
        ```

#### Operational Best Practices

| Scenario                             | Recommended Action                                        |
| ------------------------------------ | --------------------------------------------------------- |
| Before major service changes         | `tools system configuration generate-checkpoint`          |
| Before committing large changes      | Review with `diff` first                                  |
| Scheduled maintenance                | Generate a named checkpoint at the start of the window    |
| Enable auto-checkpoint               | Configuration checkpoint will be automatically created after every successful commit    |
| Revert to known-good state           | `load checkpoint <name>` then `commit now`                |
| Full reset to startup configuration  | `load startup auto-commit`                                |



## Summary

Congratulations!  You have completed the activity.

If you completed all the tasks above, you have gone through a progressive learning path; from orientation and navigation, through configuration, to productivity features (aliases, output modifiers, wildcards) and operational resilience (rollback).

Here is a short summary table of some topics you have covered:

| Concept                     | SR Linux CLI Approach                                      |
| --------------------------- | ---------------------------------------------------------- |
| Configuration mode          | `enter candidate` (transactional, candidate-based)         |
| Apply changes               | `commit` or `commit now`                                   |
| Undo uncommitted changes    | `discard` or `discard stay`                                |
| Inspect staged changes      | `diff`                                                     |
| View operational state      | `enter state`, then `info`                                 |
| Structured output formats   | `| as json`, `| as yaml`, `| as table`                  |
| CLI shortcuts               | `environment alias`                                        |
| Bulk config / queries       | Wildcards (`*`) and ranges (`{x..y}`)                     |
| Rollback                    | `load checkpoint <name>` then `commit now`                 |
| Reset to startup            | `load startup auto-commit`                                 |


<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js" async></script>
