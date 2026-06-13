# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""Generate a network-services inventory CSV from EDA JSON dumps.

The script reads five JSON list dumps from a data directory (``--data-dir``,
default: ``<current working directory>/data``). Each file is a single object
with an ``items`` array (``kubectl get … -o json`` style):

    interfaces.json   - physical Interface resources (used for label matching
                        and for LAG / Loopback type description)
    vlans.json        - VLAN objects that bind a Bridge Domain to interfaces
                        through label selectors
    irbs.json         - IRB objects that bridge a Bridge Domain to a Router
    bis.json          - BridgeInterface objects (direct BD <-> interface)
    ris.json          - RoutedInterface objects (direct Router <-> interface)

Run it with ``--data-dir`` pointing at a directory populated by the playbook
for a single EDA deployment; it writes ``network_services_inventory.csv`` in
that same directory.

Attachments come from four sources, which are walked independently:

1. VLAN -> bridgeDomain + interfaceSelectors (label match against Interfaces)
2. BridgeInterface -> bridgeDomain + interface (direct attachment)
3. RoutedInterface -> router + interface (direct attachment, includes loopbacks)
4. IRB -> links a Bridge Domain and a Router on every node where the IRB is deployed.
"""

from __future__ import annotations

import argparse
import csv
import json
from operator import attrgetter
from pathlib import Path
from typing import Any, Iterator, Literal, NamedTuple

# JSON object shapes from the EDA API / playbook dumps (nested dicts and lists).
JsonObject = dict[str, Any]
ServiceKind = Literal["MAC-VRF", "IP-VRF"]


class InventoryRow(NamedTuple):
    """One CSV row: service, type, interface, iface type, VLAN, node."""

    service_name: str
    service_type: str
    interface_name: str
    interface_type: str
    vlan_id: str
    node_name: str


def load(filename: str | Path) -> list[JsonObject]:
    """Read a JSON list dump and return the top-level ``items`` array."""
    path = Path(filename)
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return []
    try:
        data: Any = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{path}: invalid JSON ({exc})") from exc
    if not isinstance(data, dict):
        return []
    items = data.get("items")
    return items if isinstance(items, list) else []


def load_inventory_sources(
    data_dir: Path,
) -> tuple[
    list[JsonObject],
    list[JsonObject],
    list[JsonObject],
    list[JsonObject],
    list[JsonObject],
]:
    """Load the five resource JSON files used to build the inventory."""
    files = ("interfaces", "vlans", "irbs", "bis", "ris")
    return tuple(load(data_dir / f"{f}.json") for f in files)


def matches(selectors: list[Any], labels: dict[str, Any]) -> bool:
    """Return True when every ``key=value`` selector is satisfied by the labels."""
    for s in selectors:
        if not isinstance(s, str):
            return False
        key, sep, value = s.partition("=")
        if not sep:
            return False
        if labels.get(key) != value:
            return False
    return True


def describe(iface: JsonObject | None, member: JsonObject) -> str:
    """Build the 'Interface Type' string from an Interface resource and member."""
    spec = (iface or {}).get("spec") or {}
    t = spec.get("type")
    if t == "Loopback":
        return "loopback"
    if t != "LAG":
        return "interface"
    members = spec.get("members") or []
    peers = [m for m in members if m != member]
    return "lag interface with " + ", ".join(
        f'"{p.get("interface", "")}" on device "{p.get("node", "")}"' for p in peers
    )


def clean_vlan_id(value: Any) -> str:
    """Normalize the API's vlanID into something printable.

    BridgeInterface and RoutedInterface objects sometimes carry the literal
    string ``"null"`` to mean 'no VLAN tagging on this attachment'. Render
    those as an empty cell so they align with how IRBs are displayed.
    """
    if value in (None, "", "null"):
        return ""
    return str(value)


def _str_cell(value: Any) -> str:
    """Coerce a JSON/API value to a CSV cell string."""
    return "" if value is None else str(value)


def attach_via_resource(
    rows: set[InventoryRow],
    iface_by_name: dict[str, JsonObject],
    item: JsonObject,
    service_kind: ServiceKind,
) -> None:
    """Common logic for BridgeInterface and RoutedInterface.

    Both objects share the same shape: ``spec.{bridgeDomain|router}`` names the
    parent service, ``spec.interface`` references an Interface resource, and
    ``status.subinterfaces`` lists every realized {node, interface} pair.
    """
    spec = item.get("spec", {})
    parent = (
        spec.get("bridgeDomain") if service_kind == "MAC-VRF" else spec.get("router")
    )
    iface_name = spec.get("interface")
    if not parent or not iface_name:
        return
    vlan_id = clean_vlan_id(spec.get("vlanID"))
    parent_iface = iface_by_name.get(str(iface_name))

    p_spec = (parent_iface.get("spec") or {}) if parent_iface else {}
    member_list = p_spec.get("members") or []

    for sub in item.get("status", {}).get("subinterfaces", []):
        node, port = sub.get("node"), sub.get("interface")
        if not node or not port:
            continue
        # Find the Interface member that backs this realization so describe()
        # can return the right LAG / loopback / interface label.
        member: JsonObject = {"node": node, "interface": port}
        if parent_iface:
            member = next(
                (
                    m
                    for m in member_list
                    if m.get("node") == node and m.get("interface") == port
                ),
                member,
            )
        rows.add(
            InventoryRow(
                service_name=_str_cell(parent),
                service_type=service_kind,
                interface_name=_str_cell(port),
                interface_type=describe(parent_iface, member),
                vlan_id=vlan_id,
                node_name=_str_cell(node),
            )
        )


def irb_owning_nodes(irb: JsonObject) -> Iterator[str]:
    """Yield each node where the IRB has a L3 endpoint.

    An IRB's ``status.interfaces`` lists every node that participates in the
    service, but only entries whose ``ipv4Addresses`` or ``ipv6Addresses``
    is non-empty are interesting, as both distinguishes one-IRB-per-node deployments
    and anycast/distributed gateways.
    """
    for sub in irb.get("status", {}).get("interfaces", []):
        if sub.get("ipv4Addresses") or sub.get("ipv6Addresses"):
            node = sub.get("node")
            if node:
                yield str(node)


def iface_index_by_name(interfaces: list[JsonObject]) -> dict[str, JsonObject]:
    """Map Interface resource name -> resource; skip entries without a name."""
    out: dict[str, JsonObject] = {}
    for i in interfaces:
        md = i.get("metadata")
        if not isinstance(md, dict):
            continue
        name = md.get("name")
        if isinstance(name, str) and name:
            out[name] = i
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build network_services_inventory.csv from EDA JSON dumps.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path.cwd() / "data",
        metavar="DIR",
        help=(
            "Directory containing interfaces.json, vlans.json, irbs.json, bis.json, "
            "and ris.json (default: <current working directory>/data)"
        ),
    )
    args = parser.parse_args()
    data_dir: Path = args.data_dir.expanduser().resolve()
    if not data_dir.is_dir():
        parser.error(f"data directory does not exist or is not a directory: {data_dir}")

    interfaces, vlans, irbs, bis, ris = load_inventory_sources(data_dir)

    rows: set[InventoryRow] = set()
    iface_by_name = iface_index_by_name(interfaces)

    # Pathway 1: VLAN with label selectors -> matching Interface members
    for vlan in vlans:
        spec = vlan.get("spec", {})
        bd, selectors_raw = spec.get("bridgeDomain"), spec.get("interfaceSelectors")
        selectors = selectors_raw if isinstance(selectors_raw, list) else []
        if not bd or not selectors:
            continue
        vlan_id = clean_vlan_id(spec.get("vlanID"))
        for iface in interfaces:
            md = iface.get("metadata")
            labels = md.get("labels", {}) if isinstance(md, dict) else {}
            if not isinstance(labels, dict):
                labels = {}
            if not matches(selectors, labels):
                continue
            iface_spec = iface.get("spec") or {}
            if not isinstance(iface_spec, dict):
                continue
            for member in iface_spec.get("members") or []:
                if not isinstance(member, dict):
                    continue
                node, port = member.get("node"), member.get("interface")
                if not node or not port:
                    continue
                rows.add(
                    InventoryRow(
                        service_name=_str_cell(bd),
                        service_type="MAC-VRF",
                        interface_name=_str_cell(port),
                        interface_type=describe(iface, member),
                        vlan_id=vlan_id,
                        node_name=_str_cell(node),
                    )
                )

    # Pathway 2: BridgeInterface -> direct attachment to a Bridge Domain
    for bi in bis:
        attach_via_resource(rows, iface_by_name, bi, "MAC-VRF")

    # Pathway 3: RoutedInterface -> direct attachment to a Router
    for ri in ris:
        attach_via_resource(rows, iface_by_name, ri, "IP-VRF")

    # Pathway 4: IRB links a Bridge Domain and a Router
    # on every node where the IRB is deployed.
    for irb in irbs:
        md = irb.get("metadata")
        if not isinstance(md, dict):
            continue
        irb_name = md.get("name")
        if not isinstance(irb_name, str) or not irb_name:
            continue
        irb_spec = irb.get("spec") or {}
        if not isinstance(irb_spec, dict):
            continue
        bd = irb_spec.get("bridgeDomain")
        router = irb_spec.get("router")
        for node in irb_owning_nodes(irb):
            if bd:
                rows.add(
                    InventoryRow(
                        service_name=_str_cell(bd),
                        service_type="MAC-VRF",
                        interface_name=irb_name,
                        interface_type="irb",
                        vlan_id="",
                        node_name=node,
                    )
                )
            if router:
                rows.add(
                    InventoryRow(
                        service_name=_str_cell(router),
                        service_type="IP-VRF",
                        interface_name=irb_name,
                        interface_type="irb",
                        vlan_id="",
                        node_name=node,
                    )
                )

    headers = [
        "Service Name",
        "Service Type",
        "Interface Name",
        "Interface Type",
        "VLAN ID",
        "Node Name",
    ]
    sorted_rows = sorted(
        rows,
        key=attrgetter("service_name", "node_name", "interface_name"),
    )

    out_csv: Path = data_dir / "network_services_inventory.csv"
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="|", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        writer.writerows(sorted_rows)


if __name__ == "__main__":
    main()
