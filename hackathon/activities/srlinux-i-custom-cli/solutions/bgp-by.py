# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from srlinux import strings
from srlinux.data import Border, ColumnFormatter, TagValueFormatter, Borders, Data, Indent
from srlinux.location import build_path
from srlinux.mgmt.cli import CliPlugin, KeyCompleter
from srlinux.schema import FixedSchemaRoot
from srlinux.syntax import Syntax


class Plugin(CliPlugin):
    
    def load(self, cli, **_kwargs):
        syntax = Syntax('bgp-by', help="Displays brief but useful data related to BGP peers. \
                                        \n\nThe output can be filtered by selecting options at the command line.")
        syntax.add_named_argument(
            'network-instance',
            default='default',
            suggestions=KeyCompleter(path='/network-instance[name=*]'),
            help='network instance name')
        syntax.add_named_argument(
            'peer-as',
            default='*',
            value_checker=CheckASN(),
            help='peer as number')
        syntax.add_named_argument(
            'peer-address',
            default='*',
            suggestions=KeyCompleter(path='/network-instance[name=*]/protocols/bgp/neighbor[peer-address=*]'),
            help='ip address of peer')
        syntax.add_named_argument(
            'bgp-group',
            default='*',
            suggestions=KeyCompleter(path='/network-instance[name=*]/protocols/bgp/group[group-name=*]'),
            help='bgp group name')
       
        cli.show_mode.add_command(
            syntax,
            update_location=False,
            callback = self._print,
            schema = self._my_schema()
        ) 

    def _my_schema(self):
        root = FixedSchemaRoot()
        netinst = root.add_child(
            'network-instance',
            key = 'name',
            fields = [ 'name', 'local-as' ]
            )
        neigh = netinst.add_child(
            'neighbor',
            key = 'peer-address',
            fields = [ 'peer-type', 'peer-as', 'peer-group', 'interface' ]
        )

        return root

    def _fetch_state(self, state, arguments):
        local_as_path = build_path('/network-instance[name={name}]/protocols/bgp/autonomous-system', name=arguments.get('network-instance'))
        peer_path = build_path('/network-instance[name={name}]/protocols/bgp/neighbor[peer-address={peer_address}]', name=arguments.get('network-instance'), peer_address=arguments.get('peer-address'))
        nh_path = build_path('/network-instance[name={name}]/route-table/next-hop[index=*]', name=arguments.get('network-instance'))

        try:
            self._local_as_path_data = state.server_data_store.get_data(local_as_path, recursive=False)
        except ServerError:
            self._local_as_path_data = None

        try: 
            self._peer_path_data = state.server_data_store.get_data(peer_path, recursive=True)
        except ServerError:
            self._peer_path_data = None

        try:
            self._nh_path_data = state.server_data_store.get_data(nh_path, recursive=True)
        except ServerError:
            self._nh_path_data = None
   
    def _populate_schema(self, arguments):
        schema = Data(arguments.schema)
        peers = []
        for netinst in self._local_as_path_data.network_instance.items():
            netinst_node = schema.network_instance.create(netinst.name)
            netinst_node.local_as = netinst.protocols.get().bgp.get().autonomous_system
            if '*' != arguments.get('peer-as'):
                for peeraddr in self._peer_path_data.network_instance.get(netinst.name).protocols.get().bgp.get().neighbor.items(): 
                    if int(peeraddr.peer_as) == int(arguments.get('peer-as')):
                        peer_node = netinst_node.neighbor.create(peeraddr.peer_address)
                        peer_node.peer_type = peeraddr.peer_type
                        peer_node.peer_as = peeraddr.peer_as
                        peer_node.peer_group = peeraddr.peer_group
                        peers.append(peeraddr.peer_address) 
            elif '*' != arguments.get('peer-address'):
                for peeraddr in self._peer_path_data.network_instance.get(netinst.name).protocols.get().bgp.get().neighbor.items(): 
                    if peeraddr.peer_address == arguments.get('peer-address'):
                        peer_node = netinst_node.neighbor.create(peeraddr.peer_address)
                        peer_node.peer_type = peeraddr.peer_type
                        peer_node.peer_as = peeraddr.peer_as
                        peer_node.peer_group = peeraddr.peer_group
                        peers.append(peeraddr.peer_address) 
            elif '*' != arguments.get('bgp-group'):
                for peeraddr in self._peer_path_data.network_instance.get(netinst.name).protocols.get().bgp.get().neighbor.items(): 
                    if peeraddr.peer_group == arguments.get('bgp-group'):
                        peer_node = netinst_node.neighbor.create(peeraddr.peer_address)
                        peer_node.peer_type = peeraddr.peer_type
                        peer_node.peer_as = peeraddr.peer_as
                        peer_node.peer_group = peeraddr.peer_group
                        peers.append(peeraddr.peer_address) 
            else:
                for peeraddr in self._peer_path_data.network_instance.get(netinst.name).protocols.get().bgp.get().neighbor.items(): 
                    peer_node = netinst_node.neighbor.create(peeraddr.peer_address)
                    peer_node.peer_type = peeraddr.peer_type
                    peer_node.peer_as = peeraddr.peer_as
                    peer_node.peer_group = peeraddr.peer_group
                    peers.append(peeraddr.peer_address) 
            for nh_index in self._nh_path_data.network_instance.get(netinst.name).route_table.get().next_hop.items():
                if nh_index.ip_address in peers:
                    netinst_node.neighbor.get(nh_index.ip_address).interface = nh_index.subinterface
                    peers.remove(nh_index.ip_address)

        return schema 
    
    def _set_formatters(self, schema):
        schema.set_formatter('/network-instance', TagValueFormatter())
        schema.set_formatter('/network-instance/neighbor', Indent(ColumnFormatter(ancestor_keys=False), indentation=2))
    
    def _print(self, state, arguments, output, **_kwargs):
        self._fetch_state(state, arguments)
        schema = self._populate_schema(arguments)
        self._set_formatters(schema)
        output.print_data(schema)

class CheckASN(object):
    def __call__(self, value) -> bool:
        try:
            if (1 <= int(value) <= 65536):
                pass
            elif (131072 <= int(value) <= 4294967294):
                pass
            else:
                raise ValueError()
        except ValueError:
            raise ValueError(f"\nThis is not a valid 16-bit or 32-bit ASN: '{value}'")
        return True

