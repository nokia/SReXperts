# Custom Service Splitting Resources

Use this file as a quick companion to the activity, not as a second lab guide.

## Quick Start

1. Clone **custom-service-splitting** and name it **`custom-service-splitting-g<groupID>`**, for example **`custom-service-splitting-g3`**
2. Publish your cloned workflow
3. Execute it with **Group ID**, **Splitting Algorithm**, and **Approve Changes** left unchecked
4. Review the HTML report
5. Add the approval-gated **execute-approved-splits** subworkflow call to your clone
6. Save and publish the updated workflow
7. Execute it again with **Approve Changes** checked only when the suggested moves and target service names look correct

## Workflow Inputs

- **Group ID**: your assigned group value, for example `group3`
- **Splitting Algorithm**: `split-by-customer-id` or `split-by-site-name`
- **Approve Changes**: leave unchecked for review executions and check it only when you are ready to execute approved changes

## Algorithm Options

- `split-by-customer-id`: groups recommendations by customer ID
- `split-by-site-name`: groups recommendations by site name

## Report Layout

- **Current Service Name** is grouped across rows for sites that came from the same discovered service
- **Service Type** is also grouped across those same rows
- **NE ID** and **NE Name** identify the moved site
- **Customer ID** appears immediately before **Target Service Name** for `split-by-customer-id`
- **Site Name** appears immediately before **Target Service Name** for `split-by-site-name`
- **Target Service Name** is the site name when the split creates a new service, or the existing service name when the target already exists

## Resource Roles

- **custom-service-splitting** is the starter workflow
- **custom-service-splitting-solution** shows the completed workflow with the approval-gated execution step added
- **execute-approved-splits** is the subworkflow you connect in the final task; it uses `target-service-name` for new services and `target-service-identifier` for existing services
- **service-splitting-report** is the HTML report template used during review and execution confirmation

## Common Mistakes

- Using a group value that does not match your brownfield services
- Forgetting to publish the cloned workflow before running it
- Forgetting to save and publish after adding **execute-approved-splits**
- Executing with **Approve Changes** selected before you are ready to move sites
- Choosing an algorithm that has no matching split candidates for your services
