# Trigger Service Resync

**trigger-service-resync** triggers brownfield discovery resync for the selected service types and devices via NSP RESTCONF. Service types are chosen with checkboxes (L3VPN, ELAN, E-Line, IES). Results are displayed per service and node (success or error) in a formatted report, similar to the set-auto-stitch-rule workflow.

## Files

- **trigger-service-resync.yaml** – workflow definition
- **trigger-service-resync-report.jinja** – Jinja template for the HTML result report
- **trigger-service-resync.json** – input form schema for NSP UI

## Inputs

| Input                  | Type    | Description |
|------------------------|---------|-------------|
| `service_type_l3vpn`   | boolean | Resync L3VPN (VPRN) services (default: true). |
| `service_type_elan`   | boolean | Resync ELAN (VPLS) services (default: true). |
| `service_type_eline`  | boolean | Resync E-Line (Epipe) services (default: false). |
| `service_type_ies`    | boolean | Resync IES services (default: false). |
| `node_scope`          | `all` \| `pe1` \| `pe2` | Target nodes: both PEs, PE1 only, or PE2 only (matched by `ne-name` containing pe1/pe2). |
| `group`               | integer (default `1`) | Workgroup number; nodes are filtered by name prefix `g<N>-` (e.g. g1-pe1, g1-pe2). |

If no service type checkbox is selected, all four types are resynced.

## Output

- **result** – Rendered HTML report only (table with Service Type, Node ID, Node Name, Status, Error), using the same visual style as set-auto-stitch-rule (headline, table, success/error styling). No other output variables are returned so the UI can render the report properly.

## Usage

1. Import the workflow (and form JSON) into NSP (e.g. via Artifact Manager or Workflow Manager).
2. Run with the desired inputs. Set **group** to your workgroup number so the correct PEs are selected. Check the service type checkboxes you want to resync (L3VPN, ELAN, E-Line, IES):
   - Resync L3VPN and ELAN on both PEs for group 1: check L3VPN and ELAN, `node_scope=all`, `group=1`.
   - Resync L3VPN only on PE1 for group 2: check only L3VPN, `node_scope=pe1`, `group=2`.

## Display

Results are displayed in the same style as **set-auto-stitch-rule**: an HTML report generated via **nsp.jinja_template** with the `trigger-service-resync-report` template. The table shows one row per node with success (green) or error (red) status and any error message.

## Notes

- The workflow calls the NSP RESTCONF operation for triggering resync (e.g. `nsp-admin-resync:trigger-resync`). The exact endpoint and request/response format may vary by NSP version; see the [NSP Developer Portal](https://network.developer.nokia.com) for the current API.
- Target nodes are resolved from NSP inventory by filtering `network-element` entries whose `ne-name` matches the group prefix and node_scope (pe1/pe2).
