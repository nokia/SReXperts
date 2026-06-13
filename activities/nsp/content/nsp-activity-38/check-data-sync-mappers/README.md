# Check Data Sync Mappers

**check-data-sync-mappers** checks whether NSP data sync mappers (resync classes) are available by calling the **get-full-resync-classes** RPC. Use it before running **trigger-service-resync** or brownfield discovery to confirm the environment is set up and to see which resync classes are returned for your group's `pe1` and `pe2` nodes.

## What it does

1. **GET** network elements from NSP (`/restconf/data/nsp-equipment:network/network-element`).
2. Resolve the expected workgroup nodes automatically by **ne-name**: `g<N>-pe1` and `g<N>-pe2` (for example, group 1 -> `g1-pe1`, `g1-pe2`).
3. Build one RPC input body per target node: `nsp-admin-resync:input` with **plugin-id** `mdm` and that node's **ne-id**.
4. **POST** to `https://<nsp>/restconf/operations/nsp-admin-resync:get-full-resync-classes` for each resolved node.
5. If the RPC **succeeds**: the report lists the returned non-OpenConfig resync classes for each node and labels them with the node **ne-name** and **ne-id**. If it **fails** or a node is missing from inventory: the report shows that per node.

## Files

- **check-data-sync-mappers.yaml** - workflow definition
- **check-data-sync-mappers.json** - input form schema (group only; no manual NE picker)
- **check-data-sync-mappers-report.jinja** - HTML report template
- **get-network-elements.action** - legacy suggest action from the earlier manual-NE version; the current workflow no longer depends on it

If you are using the current group-based workflow, you do not need the old NE picker action.

## Input

| Input | Required | Description |
|-------|----------|-------------|
| `group` | Yes | Required workgroup number. The workflow automatically looks for `g<N>-pe1` and `g<N>-pe2` in NSP inventory and runs the RPC against each matching node. |

## Output

- **result** - HTML report only (overall status and a per-node table of resync classes, missing-node notices, or RPC errors). No other output variables.
- The report always includes a **Node** column showing the node **ne-name** and **ne-id**, so it is clear which classes apply to which node.
- The report filters out any classes whose identifier contains `openconfig`.

## Usage

1. Import the workflow into NSP (**Workflows** in the WebUI or the VS Code extension).
2. Run it and enter your workgroup number in **group**. The workflow fetches network elements and automatically checks your group's `g<N>-pe1` and `g<N>-pe2` nodes.
3. Read the report: green/success with per-node class rows means data sync mappers are available on those nodes; orange rows indicate a missing node or an RPC failure for that node.

## Notes

- The RPC and body follow the **nsp-admin-resync:get-full-resync-classes** (or **nsp-resync-config:get-full-resync-classes**) schema: input has `plugin-id` and optional `ne-id`; output contains **sbi-classes** (resync classes).
- Data sync mappers are installed via CAM/Artifact Manager; this workflow checks that the get-full-resync-classes RPC is present and returns the list of available classes.
