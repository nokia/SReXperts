# Configure Brownfield Services NSP

**configure-brownfield-services** configures or removes **one VPRN and one VPLS** per workgroup on the selected PE(s) via NSP RESTCONF (device configuration). The same service names and service IDs are used on each targeted node unless **`mismatched_site_names`** is enabled.

## Files

- **configure-brownfield-services.yaml** – workflow definition
- **configure-brownfield-report.jinja** – Jinja template for the HTML report (same pattern as set-auto-stitch-rule)

## Inputs

| Input           | Values                    | Description |
|----------------|---------------------------|-------------|
| `operation`    | `configure` \| `remove`   | Configure or remove services. |
| `service_scope` | `all` \| `vprn_only` \| `vpls_only` | Apply both VPRN+VPLS, only VPRN, or only VPLS. |
| `node_scope`   | `all` \| `pe1` \| `pe2`    | Target both PEs, only PE1, or only PE2. Nodes must match **`g<N>-pe1` / `g<N>-pe2`** for your **group** (see **Target nodes** below). |
| `group`        | integer (default `1`)     | Workgroup number so each group gets unique service names and IDs (e.g. group 2 → `activity-38-g2-vprn`, `activity-38-g2-vpls`; VPRN service-id `601`, VPLS service-id `701`). |
| `plan`         | boolean (default `false`)| If `true`, no PATCH or DELETE is sent to nodes; the run only shows what would be deployed or removed (see **Plan mode** below). |
| `mismatched_customer_ids` | boolean (default `false`) | If `true`, PE1 uses customer `1` and PE2 uses customer `2` on each service. Independent of `mismatched_site_names`; both may be `true`. |
| `mismatched_site_names` | boolean (default `false`) | If `true`, VPRN/VPLS `service-name` values differ per site (`…-vprn-pe1` vs `…-vprn-pe2`, and likewise for VPLS). **Remove** must use the same flag so DELETE paths match configured names. |

## Plan mode

When **`plan: true`**, the run resolves target nodes and builds the same config/delete list as for a real run, but it **does not** call RESTCONF PATCH or DELETE. Instead it outputs:

- **message** – A short summary of what would happen (e.g. which nodes would be configured and which service names).
- **plan_detail** – Structured object with `operation`, `nodes`, and either `service_scope`/`group` (configure) or `deletes_per_node` (remove), plus `summary`.

Use plan mode to verify targets and service names before running with `plan: false`.

## Services (per group)

For a given **group** `N`:

- **Service names (default):** `activity-38-g{N}-vprn`, `activity-38-g{N}-vpls`.
- **With `mismatched_site_names: true`:** `activity-38-g{N}-vprn-pe1` / `…-vprn-pe2` and `activity-38-g{N}-vpls-pe1` / `…-vpls-pe2` on the respective PEs.
- **Service IDs:** `vprn_id = 501 + (N-1)×100`, `vpls_id = 601 + (N-1)×100` (e.g. group 1 → `501`, `601`; group 2 → `601`, `701`; group 3 → `701`, `801`).
- **VPRN:** BGP-EVPN, loopback, static routes (PE1 vs PE2 differ by RD and IPs where applicable).
- **VPLS:** BGP-VPLS on both PEs; VPLS-id and route-target use the same per-group values.

## Usage

1. Import into NSP (e.g. via Artifact Manager or NSP Workflow Manager).
2. Run with the desired inputs. Always set **group** to your workgroup number so services are unique:
   - Group 1, configure all on both PEs: `operation=configure`, `service_scope=all`, `node_scope=all`, `group=1`.
   - Group 2, configure only VPRN on PE1: `operation=configure`, `service_scope=vprn_only`, `node_scope=pe1`, `group=2`.
   - Remove only VPLS for group 3: `operation=remove`, `service_scope=vpls_only`, `node_scope=all`, `group=3`.

## Output

- **result** – HTML report only (same pattern as set-auto-stitch-rule). The NSP UI renders this as a formatted report with color-coded status: green (success/creation), blue (success/removal), orange (plan), red (errors), gray (no targets / no changes). No other output variables are returned so the UI can render the report properly.

## Notes

- **Target nodes** are resolved from NSP inventory: `network-element` entries whose **`ne-name`** starts with **`g<group>-`** (e.g. `g1-pe1`, `g1-pe2` for group 1) and whose name matches **node_scope** (`pe1` / `pe2` / both).
- Configure uses RESTCONF **PATCH** to merge the service subtree into `nokia-conf:configure`.
- Remove uses RESTCONF **DELETE** on each service path. Commit is not performed; ensure device/NSP commit behavior as needed.
