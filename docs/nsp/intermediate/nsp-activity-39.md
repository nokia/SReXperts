# Custom Service Splitting

| Field | Value |
| --- | --- |
| **Activity name** | Custom Service Splitting |
| **Activity ID** | 39 |
| **Short Description** | Execute a custom service splitting approach to regroup service sites together |
| **Difficulty** | Intermediate |
| **Topology Nodes** | :material-router: PE1, :material-router: PE2 |
| **References** | [NSP Developer Portal](https://network.developer.nokia.com) |

## Objective

Building on [Brownfield Service Discovery](../beginner/nsp-activity-38.md), production networks often keep brownfield inventory that matched an early design or first import—not how you later want services **grouped** or **stitched** for operations, assurance, or customer ownership. When that gap shows up, you need a controlled path to propose regroupings and apply them only after review.

In situations like these, this activity shows how NSP lets you split what brownfield discovery surfaced into separate services and regroup sites using custom algorithms (for example **customer ID**) so the outcome better fits the customer network.

## Tasks

**You should read these tasks from top to bottom before beginning the activity.**

It is tempting to skip ahead, but tasks may require you to have completed previous tasks before tackling them.

/// warning
Remember that you are using a shared NSP system. Include your group number in every workflow input that asks for **Group ID** (and in filters such as `g<N>-p1` where applicable).
///

### Quick start on NSP Web UI

|     |     |
| --- | --- |
| **NE Session** | `☰` → `Network Search and Inventory` → find your group's PE node (for example `g7-pe1`) → open the row context menu `⋮` → `Open in NE Session`. |
| **NSP Help** | `?` icon at the top right for context-aware quick help and to open the Help Center. On some pages, the `?` icon also links directly to related Help Center articles. |
| **Service Management** | `☰` → `Service Management` |
| **Workflow Manager** | `☰` → `Workflows` |

To keep the walkthrough in one place, this activity uses workflows to present the splitting algorithm in action.

/// details | How to check workflow execution status?
    type: question

To check the execution status of any workflow, navigate to **Workflow Manager**, select **Workflow Executions** from the dropdown. Locate your execution. If you see more than one execution (since it is a shared NSP system), double-click one of the entries. From the dropdown, select **Input/Output** to cross-check your execution. To drill deeper into the flow, select **Flow** view from the dropdown.

///

### Prerequisite

Complete [Brownfield Service Discovery](../beginner/nsp-activity-38.md) first so you already have a view of how services get stitched by default in NSP.

### Generate a Service Splitting Report

1. In Workflows, clone `custom-service-splitting`
2. Name it `custom-service-splitting-g<groupID>`, for example `custom-service-splitting-g3`

3. On the cloned workflow row, open the **⋮** (three-dots) menu on the right, choose **Modify status**, and set the status to **Published**.
4. From the same menu, choose **Execute**. Set the input parameters to
      - **Group ID:** your assigned group value, for example `group3`
      - **Splitting Algorithm:** split-by-customer-id
      - **Approve Changes:** false

5. When the workflow execution completes, open it and review the HTML report.
6. Confirm the recommendations are only for services in your group

??? question "Why set `Approve Changes` to false first?"
    Leaving **Approve Changes** false keeps this run in **recommendation-only** mode: you read the HTML report before **execute-approved-splits** runs. You can also see whether any multi-site brownfield services match your inputs and whether the algorithm returned split candidates—without applying moves or creating services yet.

### Add an Approval Gate

1. In Workflows, edit your **`custom-service-splitting-g<groupID>`** workflow
2. Locate the end of the workflow after the report-rendering step
3. Add a subworkflow task that calls the **execute-approved-splits** workflow
  /// details | Solution if you get stuck
    type: hint
  
  ```
    execute-approved-splits:
      workflow: execute-approved-splits
      input:
        list_for_report: <% $.list_for_report %>
      publish:
        result: <% task().result.result %>
  ```
  ///

4. Connect the report/review path to **execute-approved-splits** only when **Approve Changes** is checked
  /// details | Solution if you get stuck
    type: hint
  
  ```
      on-success:
        - execute-approved-splits: <% $.approved %>
  ```
  ///

5. Pass the report list output into the **execute-approved-splits** subworkflow
6. Save and publish the workflow

### Approve and Execute

1. Execute your updated workflow again with the same **Group ID** and selected algorithm
2. Check **Approve Changes** only after you have reviewed the recommendations
3. Confirm that the execution calls **execute-approved-splits**
4. In **Executions**, verify that the workflow results and final report show the site moves completed and that NSP created any new destination service IDs from the supplied target service names

## Summary

Congratulations. In this activity, with the help of the **custom-service-splitting** workflow:

- You have generated a splitting report
- You compared the built-in splitting algorithms
- You published the workflow before executing it
- You added an approval flow to gate the execution
- You executed only the approved suggestions

### Next Steps

You have already split using **customer ID**. Suppose you must group by **Service Site Name**. How would you do that? Try extending the workflow yourself: add a suitable field to **Workflow Inputs**, connect it in the workflow definition, and add the branch or condition so the recommender and HTML report follow the new choice. The underlying logic is already there. Your task is to find where to register the extra dropdown option and which condition should trigger it.
