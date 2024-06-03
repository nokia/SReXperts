# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from srlinux.constants import OS_NAME
from srlinux.data import TagValueFormatter, Border, Data, ColumnFormatter, Formatter
from srlinux.location import build_path
from srlinux.mgmt.cli import CliPlugin
from srlinux.mgmt.server.server_error import ServerError
from srlinux.schema import FixedSchemaRoot
from srlinux.syntax import Syntax
from datetime import datetime


class Plugin(CliPlugin):

    '''
      Adds 'show version' command.

      Example output:

      Hostname          : DUT4
      Chassis Type      : 7250 IXR-10
      Part Number       : Sim Part No.
      Serial Number     : Sim Serial No.
      System MAC Address: 00:01:04:FF:00:00
      Software Version  : v0.0.0-12388-g1815c7e
      Architecture      : x86_64
      Last Booted       : 2019-09-12T17:34:42.865Z
      Total Memory      : 49292336 kB
      Free Memory       : 8780776 kB
    '''

    def load(self, cli, **_kwargs):
        cli.show_mode.add_command(
            Syntax('my_version', help='Show my custom basic information of the system'), update_location=False, callback=self._print,
            schema=self._get_schema())

    def _print(self, state, output, arguments, **_kwargs):
        self._fetch_state(state)
        result = self._populate_data(state, arguments)
        self._set_formatters(result)
        output.print_data(result)

    def _get_schema(self):
        root = FixedSchemaRoot()
        root.add_child(
            'basic system info',
            fields=[
                'Current time',
                'Hostname',
                'Chassis Type',
                'Part Number',
                'Serial Number',
                'System HW MAC Address',
                'OS',
                'Software Version',
                'Build Number',
                'Architecture',
                'Last Booted',
                'Total Memory',
                'Free Memory']
        )
        return root

    def _fetch_state(self, state):
        hostname_path = build_path('/system/name/host-name:')
        chassis_path = build_path('/platform/chassis')
        software_version_path = build_path('/system/app-management/application[name="idb_server"]')
        control_path = build_path('/platform/control[slot="*"]')

        try:
            self._hostname_data = state.server_data_store.get_data(hostname_path, recursive=True)
        except ServerError:
            self._hostname_data = None

        try:
            self._chassis_data = state.server_data_store.get_data(chassis_path, recursive=True)
        except ServerError:
            self._chassis_data = None

        try:
            self._software_version = state.server_data_store.get_data(software_version_path, recursive=True)
        except ServerError:
            self._software_version = None

        try:
            self._control_data = state.server_data_store.get_data(control_path, recursive=True)
        except ServerError:
            self._control_data = None

    def _populate_data(self, state, arguments):
        result = Data(arguments.schema)
        data = result.basic_system_info.create()
        data.current_time = str(datetime.now())

        data.hostname = '<Unknown>'
        if self._hostname_data:
            data.hostname = self._hostname_data.system.get().name.get().host_name or data.hostname

        data.chassis_type = '<Unknown>'
        data.part_number = '<Unknown>'
        data.serial_number = '<Unknown>'
        data.system_hw_mac_address = '<Unknown>'
        data.last_booted = '<Unknown>'
        if self._chassis_data:
            data.chassis_type = self._chassis_data.platform.get().chassis.get().type or data.chassis_type
            data.part_number = self._chassis_data.platform.get().chassis.get().part_number or data.part_number
            data.serial_number = self._chassis_data.platform.get().chassis.get().serial_number or data.serial_number
            data.system_hw_mac_address = self._chassis_data.platform.get().chassis.get().hw_mac_address \
                or data.system_hw_mac_address
            data.last_booted = self._chassis_data.platform.get().chassis.get().last_booted or data.last_booted

        data.os = OS_NAME
        data.software_version = '<Unknown>'
        data.build_number = '<Unknown>'
        if self._software_version:
            if self._software_version.system.get().app_management.get().application.exists('idb_server'):
                sw_version = self._software_version.system.get().app_management.get().application.get('idb_server').version
                if len(sw_version.strip()):
                    sw_version_strings = sw_version.split('-')
                    data.software_version = sw_version_strings[0]
                    if len(sw_version_strings) > 1:
                        data.build_number = '-'.join(sw_version_strings[1:])

        data.architecture = '<Unknown>'
        data.total_memory = '<Unknown>'
        data.free_memory = '<Unknown>'
        if self._control_data:
            for control_slot in ['A', 'B']:
                if self._control_data.platform.get().control.exists(control_slot):
                    ctrl_data = self._control_data.platform.get().control.get(control_slot)
                    if state.system_features.chassis and not ctrl_data.role == 'active':
                        continue
                    if 'cpu' in ctrl_data.child_names:
                        if ctrl_data.cpu.exists('all'):
                            data.architecture = ctrl_data.cpu.get('all').architecture
                    if 'memory' in ctrl_data.child_names:
                        total_mem_value = ctrl_data.memory.get().physical
                        free_mem_value = ctrl_data.memory.get().free
                        if total_mem_value:
                            data.total_memory = (str(total_mem_value // 1024)) + ' kB'
                        if free_mem_value:
                            data.free_memory = (str(free_mem_value // 1024)) + ' kB'
        return result

    def _set_formatters(self, data):
        data.set_formatter('/basic system info', Border(MyFormatter(), Border.Above | Border.Below))


class MyFormatter(Formatter):

    banner_list = [
"|\t ____  ____     __  __                _                  |",
"|\t/ ___||  _ \ ___\ \/ /_ __   ___ _ __| |_ ___            |",
"|\t\___ \| |_) / _ \\\  /| '_ \ / _ \ '__| __/ __|           |",
"|\t ___) |  _ <  __//  \| |_) |  __/ |  | |_\__ \           |",
"|\t|____/|_| \_\___/_/\_\ .__/ \___|_|   \__|___/           |",
"|\t ____   ___ ____  _  |_|  \033[5;92m ____       _                 \033[00m |",
"|\t|___ \ / _ \___ \| || |   \033[5;92m|  _ \ __ _| |_ __ ___   __ _ \033[00m |",
"|\t  __) | | | |__) | || |_  \033[5;92m| |_) / _` | | '_ ` _ \ / _` |\033[00m |",
"|\t / __/| |_| / __/|__   _| \033[5;92m|  __/ (_| | | | | | | | (_| |\033[00m |",
"|\t|_____|\___/_____|  |_|   \033[5;92m|_|   \__,_|_|_| |_| |_|\__,_|\033[00m |",
"|\t                                                         |"]


    def __init__(self):
        self.banner = [list(line.strip()) for line in self.banner_list]

    def iter_format(self, entry, max_width):

        data = [f"\tOS              : {entry.os}",
                f"\tChassis type    : {entry.chassis_type}",
                f"\tSoftware version: {entry.software_version}",
                f"\tSoftware build  : {entry.build_number}",
                f"\tArchitecture    : {entry.architecture}"]

        position = [3,4,5,6,7]

        for i, row in enumerate(self.banner):
            if i in position:
                line = "".join(row) + data[position.index(i)]
            else:
                line = "".join(row)
            yield line

