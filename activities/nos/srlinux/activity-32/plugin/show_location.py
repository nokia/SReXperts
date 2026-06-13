# Copyright 2026 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import argparse
import logging
from datetime import datetime, timezone
from typing import cast

from srlinux.data import Border, Data, TagValueFormatter
from srlinux.data.data import DataChildrenOfType
from srlinux.location import build_path
from srlinux.mgmt.cli import CliPlugin, CommandNodeWithArguments
from srlinux.mgmt.cli.cli_loader import CliLoader
from srlinux.mgmt.cli.cli_output import CliOutput
from srlinux.mgmt.cli.cli_state import CliState
from srlinux.mgmt.server.server_error import ServerError
from srlinux.schema import FixedSchemaRoot, SchemaNode
from srlinux.schema.fixed_schema import FixedSchemaNode
from srlinux.syntax import Syntax

logger = logging.getLogger(__name__)
logger.level = logging.INFO


class Plugin(CliPlugin):
    """
    Adds `show location` command.

    Example output:

    --{ running }--[  ]--
    A:sw-coffee# show location
    Location: Next to the coffee machine in Room 0451.
    """

    def load(self, cli: CliLoader, arguments: argparse.Namespace) -> None:
        cli.show_mode.add_command(
            syntax=self._syntax(),
            schema=self._schema(),
            callback=self._print,
        )

    def _syntax(self) -> Syntax:
        return Syntax(
            name="location",
            short_help="📍 Show inventory location of system",
            help="📍 Show inventory location of system in a granular manner.",
        )

    def _schema(self) -> FixedSchemaNode:
        root = FixedSchemaRoot()
        root.add_child(
            "inventory",
            fields=[
                "Location",
            ],
        )
        return root

    def _print(
        self,
        state: CliState,
        output: CliOutput,
        arguments: CommandNodeWithArguments,
        **kwargs,
    ) -> None:
        self._fetch_state(state)
        data = self._populate_data(arguments)
        self._set_formatters(data)
        output.print_data(data)

    def _fetch_state(self, state: CliState):
        inventory_path = build_path("/inventory")

        try:
            self._inventory_data = state.server_data_store.get_data(
                inventory_path, recursive=False
            )
        except ServerError:
            self._inventory_data = None

    def _populate_data(self, arguments: CommandNodeWithArguments):
        data = Data(schema=cast(SchemaNode, arguments.schema))
        if not isinstance(data.inventory, DataChildrenOfType):
            raise ValueError("Inventory is not a container")

        inventory_container = data.inventory.create()

        if not self._inventory_data:
            raise ValueError("Inventory data not available")

        if not isinstance(self._inventory_data.inventory, DataChildrenOfType):
            raise ValueError("Inventory is not a container")

        inventory = self._inventory_data.inventory.get()

        if not isinstance(inventory.location, str):
            raise ValueError("Location is not a string type leaf")

        inventory_container.location = inventory.location

        return data

    def _set_formatters(self, data: Data):
        data.set_formatter(
            schema="/inventory",
            formatter=Border(TagValueFormatter(), Border.Above | Border.Below),
        )