# Service Troubleshooting

|     |     |
| --- | --- |
| **Activity name** | Service Troubleshooting |
| **Activity ID** | 36 |
| **Short Description** | Troubleshoot point-to-point EVPN ELINE (Epipe) services |
| **Difficulty** | Beginner |
| **Topology Nodes** | :material-router: PE1, :material-router: PE2, :material-router: client1, :material-router: client2 |
| **References** | [NSP Documentation](https://documentation.nokia.com/nsp/25-11/libfiles/landing.html) <br/> [NSP Service Management Guide](https://documentation.nokia.com/nsp/25-11/NSP_Service_Management_Guide/iptitle.html) <br/> [SR OS EVPN-based epipe Documentation](https://documentation.nokia.com/sr/25-10/7x50-shared/layer-2-services-evpn/ethernet-virtual-private-networks.html#unique_1626067102) |


## Objective

When a customer-impacting alarm lands in the NOC, you still have to establish which service is failing, which endpoint or construct is unhealthy, and whether the live network matches what Service Management expects. Piecing that together across inventory, notes, and scattered logins is slow and easy to get wrong.

This activity mirrors that unhealthy situation with an EVPN ELINE (EPIPE) service and the focus is to stay within **NSP** space to identify the affected service object, narrow down the scope of cause, and plan remediation so the **intent** stays authoritative. Accessing the router CLI is only an optional confirmation once you have a hypothesis figured out. 

## Technology explanation

### Service Management

Service Management is where EVPN ELINE services live in inventory and lifecycle. Operators create and change them through a single UI, and the platform keeps the intended service model so you can correct it and redeploy without losing the authoritative definition.

### Fault Management and Object Troubleshooting

Fault Management, together with Object Troubleshooting, gives a consolidated health picture on the **Troubleshooting Summary Board**, shows which part of the service is unhealthy before you open a router session, and lets you cross-launch troubleshooting workflows from the affected service object itself.

### Workflow Manager (WFM)

WFM runs workflows on OpenStack Mistral (DSL v2) and integrates with NSP and other systems. This lab uses two workflows: one that creates the EVPN ELINE service and the other to run troubleshooting. As part of the troubleshooting, the flow runs the same `show` sequence an operator would otherwise type by hand.

## Tasks

/// warning
Remember that you are using a shared NSP system. Include your group number in every workflow input that asks for **Group**.
///

**You should read these tasks from top to bottom before beginning the activity.**

It is tempting to skip ahead, but tasks may require you to have completed previous tasks before tackling them.

### Quick start on NSP Web UI

|     |     |
| --- | --- |
| **NE Session** | `☰` → `Network Search and Inventory` → find your group’s PE node (for example `g7-pe1`) → open the row context menu `⋮` → `Open in NE Session`. |
| **NSP Help** | `?` icon at the top right for context-aware quick help and to open the Help Center. On some pages, `?` also links directly to related Help Center articles. |
| **Service Management** | `☰` → `Service Management` |
| **Workflow Manager** | `☰` → `Workflows` |
| **Object Troubleshooting** | `☰` → `Object Troubleshooting` → set Target Type to `Service` |

/// details | How to check workflow execution status?
    type: question

To check the execution status of any workflow, navigate to **Workflow Manager**, select **Workflow Executions** from the dropdown. Locate your execution. If you see more than one execution (since it is a shared NSP system), double-click one of the entries. From the dropdown, select **Input/Output** to cross-check your execution. To drill deeper into the flow, select **Flow** view from the dropdown.

///

Before you go further, remember you are **not** meant to fix the issue directly on the routers. Analyze the situation in NSP, then make the change in Service Management so the intended model stays aligned.

/// details | Score Yourself
    type: tip

As you work through the tasks, give yourself:

- `3 points` if you identify the unhealthy site without opening router CLI first
- `3 points` if you use the cross-launched troubleshooting workflow to prove the root cause
- `2 points` if you restore the service from Service Management only
- `2 points` if you can clearly explain the operational advantage of the NSP-driven method over a manual device-by-device troubleshooting approach

Maximum score: `10/10`
///

### Prerequisites

Let’s assume the following conditions are already true:

- an EVPN ELINE service has already been created in Service Management using the `srexperts-evpn-epipe-creation` workflow
- the service is present in NSP but is not healthy
- the affected service uses two PE endpoints, `PE1` and `PE2`, with attachment circuits toward `client1` and `client2`
- you have access to NSP Service Management and Object Troubleshooting views

### Identify the Problem from NSP First

Open the pre-created EVPN ELINE service in **Object Troubleshooting**. In this network, names follow `epipe-<NE Service ID>` (for example `epipe-1711` when the service ID is `1711`). On the **Troubleshooting Summary Board**, review EVPN ELINE health and determine which site is unhealthy before you collect any CLI output.

The **operational advantage** here is that NSP shrinks the problem space right away and keeps the investigation anchored on the service object instead of scattered router sessions. However, the **limitation** is that the board only reflects what NSP knows about the service and related objects. It shows **where** things are wrong but not the full remediation path.

/// details | Solution (use only if you get stuck)
    type: success
    -{{video(url="https://gitlab.com/-/project/69754954//uploads/969fdd14b7c5edf984d41ca699d81bdb/Identify_the_Problem_from_NSP_First.mp4")}}-
///

### Run Service Troubleshooting Workflow

From the service object, launch the context-aware `srexperts-tshoot-evpn-epipe` workflow from the top-right play button. It runs the diagnostics you would otherwise type by hand: `show service id "<service>" base`, `show service id "<service>" bgp-evpn`, and `show router bgp routes evpn auto-disc next-hop <peer-ip>`.

NSP does not replace the underlying analysis model. It **automates** the familiar CLI sequence, uses service context so the right routers and commands are chosen for you, and returns one **HTML** report that is faster to produce and easier to read than scattered paste-ins. You should reach the same root cause you would reach with manual, router-by-router CLI checks.

/// details | Solution (use only if you get stuck)
    type: success
    -{{video(url="https://gitlab.com/-/project/69754954//uploads/1c3e88269e35ba26539144ac4c90f208/Run_Service_Troubleshooting_Workflow.mp4")}}-
///

### Remediate the Service

After you accept the root cause, restore the **admin-state** of the unhealthy site (matching what the workflow showed) in the service intent in Service Management. After you change and redeploy, confirm the EVPN ELINE shows as **healthy** again in NSP.

/// details | Solution (use only if you get stuck)
    type: success
    -{{video(url="https://gitlab.com/-/project/69754954//uploads/d48a2be1469f1278cb8e7a7bf835f83b/Remediate_the_Service_in_Service_Management.mp4")}}-
///

/// details | Why NSP improves Service Troubleshooting?
    type: question

You create an EVPN ELINE in Service Management, see that it is unhealthy, use the **Troubleshooting Summary Board** and object workflows to compress discovery and prove cause, then correct intent in Service Management and redeploy until the service is healthy again.

That is not an argument against device `show` commands rather it is an argument for running the **same** checks in a service-anchored, repeatable way: less guessing which PE matters, fewer hand-copied command strings, one consolidated report, and fixes that stay tied to the model instead of one-off box edits. For operations teams, that means less manual correlation, steadier triage, and less configuration drift.

///

/// note
The troubleshooting workflow is **not** a generic out-of-the-box catalog entry. It was rather built for this activity purely to show how teams can capture local practice as object-launchable automation.
///

## Summary

Congratulations! In this activity you have:

- Used **Object Troubleshooting** to identify the unhealthy site before relying on router CLI.
- Cross-launched a workflow from the service object to run the device diagnostics in one pass.
- Remediated through Service Management by restoring site config and redeploying.

## Next steps

Given what you had gained through this activity, you could do a lot more as next steps:

- Extend the troubleshooting workflow to highlight disabled `admin-state` in the HTML report
- Add SAP state, EVPN/MPLS context, or other checks so the first-pass report carries more signal.
- Introduce another fault (wrong port, missing EVPN reachability, and so on) to compare how outputs differ.
- Add a remediation workflow that suggests the fix after analysis while still committing changes through Service Management.
- Reuse the same pattern on another service type such as an EVPN ELAN.
