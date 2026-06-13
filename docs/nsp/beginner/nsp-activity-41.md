# Resource Pool Monitoring and Alerting

|     |     |
| --- | --- |
| **Activity name** | Resource Pool Monitoring and Alerting |
| **Activity ID** | 41 |
| **Short Description** | Event-driven automation when a resource pool threshold is crossed |
| **Difficulty** | Beginner |
| **Topology Nodes** | any :material-router: PE nodes |
| **References** | [Resource Management](https://network.developer.nokia.com/learn/25_11/artifact-development/programming/network-automation/resource-manager/) <br> [Workflow Kafka Trigger](https://network.developer.nokia.com/learn/25_11/artifact-development/programming/workflows/wfm-workflow-development/wfm-Advanced-Concepts/#Kafka_trigger) <br>  [Kafka Event Execution](https://network.developer.nokia.com/learn/25_11/artifact-development/programming/workflows/workflow-manager-apis/#Kafka_event_execution) |

## Objective

Pool utilization often rises quietly until fulfillments begin to fail. By then there is little time to react. The gap this activity targets is **early signal** when a pool crosses **its** warning or critical bands, plus a practical path from that signal to **automated follow-up** instead of relying on manual checks alone.

Using resource pool threshold policies and Workflow Kafka triggers, you will understand how event-driven automation comes full circle. 

## Technology explanation

### Fault Management (FM)

Fault Management (FM) monitors the network for anomalies and generates alarms (or alerts, in this activity) when predefined conditions are met. In the context of Resource Management, FM alarms are crucial for notifying operators when resource pools approach or exceed their capacity thresholds.

### Workflow Kafka rules

The Kafka trigger in WFM provides a powerful mechanism within NSP to subscribe to specific events (such as FM alarms) and trigger actions—for example, starting a workflow. By integrating Kafka rules with FM alarms, NSP can achieve closed-loop automation, where network events automatically trigger predefined operational procedures.

## Tasks

/// warning
Remember that you are using a shared NSP system. Ensure your group number is included in the intent-type artifacts you create (filename and any group-scoped names).
///

**You should read these tasks from top to bottom before beginning the activity.**

It is tempting to skip ahead, but tasks may require you to have completed previous tasks before tackling them.

### Quick start on NSP Web UI

|     |     |
| --- | --- |
| **NE Session** | `☰` → `Network Search and Inventory` → find your group’s PE node (for example `g7-pe1`) → open the row context menu `⋮` → `Open in NE Session`. |
| **NSP Help** | `?` icon at the top right for context-aware quick help and to open the Help Center. On some pages, the `?` icon also links directly to related Help Center articles. |
| **Resource Management** | `☰` → `Network Intents` → top right `⋮` → `Open Resource Management` |
| **Intent-Based Service Fulfillment (IBSF)** | `☰` → `Service Management` |
| **Workflow Manager** | `☰` → `Workflows` |

/// note
Treat each block below as a **challenge**, not a script. Use NSP and what you learned in [Service Provisioning with Resource Pools](nsp-activity-67.md) to decide *where* to click and *what* to run. Open a **Hint** only when you are stuck, want to validate your plan, or need exact names and menu paths.
///

### Prerequisite

Complete [Service Provisioning with Resource Pools](nsp-activity-67.md) first so you already have a numeric pool, a threshold policy, and services tied to that pool.

### Trust your policy

Convince yourself that the pool you will stress is governed by the threshold policy you expect before any new alarms or Kafka activity appear.

- What would you inspect to prove warning / minor / major percentages match what you intended?
- How would you prove the **same** pool is actually bound to that policy (not only that a policy exists)?

/// details | Where to look
    type: hint
From **Resource Management**, use the menus to open **Threshold policies** and review the policy attached to your pool. Cross-check from **Numeric pools** that the pool references that policy.
///

/// details | What if the policy or link is missing?
    type: question

Re-run the `create-numeric-pool-with-threshold-policy` workflow from [Service Provisioning with Resource Pools](nsp-activity-67.md), then repeat the checks above.
///

### Make utilization cross the line

Drive pool utilization through **warning** and/or **critical** in a controlled way, without stepping on other groups’ reservations.

- Pick a stress pattern (workflows, services, or both) that increases utilization monotonically until thresholds should fire.
- Decide when you will stop (for example pool full, or fulfillments failing as expected) and what evidence you will record at each stage.

/// details | One reliable stress pattern
    type: hint
Run the `create-evpn-epipe-service-with-resource-pool` workflow repeatedly with **unique** service names until utilization crosses your thresholds. Stop when the pool is full or runs fail as expected.
///

/// details | What if you never see an alarm in FM?
    type: question
Threshold-crossing alarms for pools are often **system** alarms and may be **administrator-visible** only. That limitation is intentional for the next challenge: prove the signal through automation instead of only the FM UI.
///

### Prove automation saw the signal

Show that something **downstream of FM** received a usable signal when thresholds were crossed, even if your account cannot see the underlying system alarm in the FM UI.

/// details | Kafka triggers
    type: hint

In **Workflow Manager**, open **Kafka Triggers**. Some rules are pre-provisioned for this lab. After a threshold is crossed, expect a **Times Matched** counter to increase on the relevant rule.

///

Now how would you inspect payload handed to a workflow without trusting the FM screen alone?

/// details | Workflow execution and I/O
    type: hint

In **Workflow Manager** → **Workflow Executions**, locate a run whose name matches `srx-alarm-kafka-payload`. On a shared system there may be several runs. So pick one tied to your test window. Use **Input/Output** to confirm how alarm fields appear for downstream logic.
///

## Summary

Congratulations! In this activity you have learnt:

* How utilization becomes an operator signal on the pool
* How captured fault or alert payload drives workflow input
* How to tune rules against real fault events.
