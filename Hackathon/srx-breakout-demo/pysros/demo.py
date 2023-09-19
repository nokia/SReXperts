#!/usr/bin/env python3

from pysros.management import connect
from pysros.pprint import printTree
import yaml, jinja2
from os import listdir
from os.path import isfile, join
import concurrent.futures
import glob
import json
import time
import re

class Node:
    def __init__(self, name, ip_address, port=830, username="admin", password="admin", index=None, group=None):
        self.name = name
        self.ip_address = ip_address
        self.port = port
        self.username = username
        self.password = password
        self.group = group
        self.node_id = index
        self.connection = self._get_connection(ip_address, port, username, password)
        self._configure_traffic_ports()
        self.ports = self._get_ports()
        self.traffic_ports = self._identify_traffic_capable_ports()
        
    def _get_ports(self):
        return self.connection.running.get_list_keys('/nokia-state:state/port')
        
    def _configure_traffic_ports(self):
        ports_filename = "/demo/configs/routers/ports.json.j2"
        if isfile(ports_filename):
            environment = jinja2.Environment(loader=jinja2.FileSystemLoader('/'))
            template = environment.get_template(ports_filename)
            rendered = template.render()
            config = self.connection.convert('/', rendered, source_format='json', destination_format='pysros')
            self.connection.candidate.set('/nokia-conf:configure', config['configure'])
        else:
            raise SystemExit(f"Cannot find {ports_filename}")
    
    def _identify_traffic_capable_ports(self):
        is_traffic_port = re.compile('\d/\d/c\d/1')
        traff_ports = []
        for port in self.ports:
            if is_traffic_port.match(port):
                traff_ports.append(port)
        return traff_ports 
        
    def _get_connection(self, ip_address, port, username, password):
        try:
            connection = connect(host=ip_address, port=port, username=username, password=password, hostkey_verify=False)
            return connection
        except RuntimeError as error:
            raise SystemExit(error)
    
    def __str__(self):
        return_string = f"name: {self.name}, node_id: {self.node_id}, group: {self.group}, ip_address: {self.ip_address}, port: {self.port}, username: {self.username}, password: {self.password}"
        return return_string

class LinkTable:
    def __init__(self, links, nodes, clab_topo):
        self.links = links
        self.node_links = {}
        for node in nodes:
            self.node_links[node.name] = {'ports': node.traffic_ports, 'node_id': node.node_id}
        self.nodes = nodes
        self.linktable = self._allocate_links(clab_topo)
        
    def _allocate_links(self, clab_topo):
        table = {}
        interface_number = re.compile(r'(\d+)$')
        for link in self.links:
            a_end_node = link['a']['node']
            z_end_node = link['z']['node']
            a_end_port_allocation = f"1/1/c{interface_number.findall(link['a']['interface'])[0]}/1"
            z_end_port_allocation = f"1/1/c{interface_number.findall(link['z']['interface'])[0]}/1"
            
            for end in ['a', 'z']:
                for node in self.nodes:
                    if not link[end]['node'] in node.name:
                        self.node_links[link[end]['node']] = {'node_id': clab_topo['nodes'][link[end]['node']]['index']}
                        
                # Specific static numbering for openbgpd
                if link[end]['node'] == "openbgpd":
                        self.node_links[link[end]['node']]['node_id'] = str(254)
                        if end == 'a':
                            self.node_links[link['z']['node']]['node_id'] = str(255)
                        elif end =='z':
                            self.node_links[link['a']['node']]['node_id'] = str(255)
                        
            if self.node_links[link['a']['node']]['node_id'] < self.node_links[link['z']['node']]['node_id']:
                is_a_end_lowest_rtr_id = True
                lowest_node_id = self.node_links[link['a']['node']]['node_id']
                highest_node_id = self.node_links[link['z']['node']]['node_id']
            else:
                is_a_end_lowest_rtr_id = False
                lowest_node_id = self.node_links[link['z']['node']]['node_id']
                highest_node_id = self.node_links[link['a']['node']]['node_id']
            ip_addr = f"192.{lowest_node_id}.{highest_node_id}.0"
            remote_ip_addr = f"192.{lowest_node_id}.{highest_node_id}.1"
            
            if a_end_node in table.keys():
                table[a_end_node].update({a_end_port_allocation: {'ip_addr': ip_addr, 'remote_node': z_end_node}})
            else:
                table[a_end_node] = {a_end_port_allocation: {'ip_addr': ip_addr, 'remote_node': z_end_node}}
            if z_end_node in table.keys():
                table[z_end_node].update({z_end_port_allocation: {'ip_addr': remote_ip_addr, 'remote_node': a_end_node}})
            else:
                table[z_end_node] = {z_end_port_allocation: {'ip_addr': remote_ip_addr, 'remote_node': a_end_node}}
        return table
       
def read_yaml_json_file(filename, format):
    if format == "json" or format == "yaml":
        with open(filename, 'r') as f:
            if format == "yaml":
                contents = yaml.safe_load(f)
            if format == "json":
                contents = json.load(f)
        return contents
    else:
        raise SystemExit("Incorrect file format requested") 
    
def get_sros_nodes_from_clab_topo(clab_topo):
    nodes = []
    for node in clab_topo['nodes'].keys():
        if clab_topo['nodes'][node]['kind'] == "vr-sros":
            if 'ansible-group' in clab_topo['nodes'][node]['labels']:
                nodes.append((node, clab_topo['nodes'][node]['mgmt-ipv4-address'], clab_topo['nodes'][node]['index'], clab_topo['nodes'][node]['labels']['ansible-group']))
            else:
                nodes.append((node, clab_topo['nodes'][node]['mgmt-ipv4-address'], clab_topo['nodes'][node]['index']))
    return set(nodes)
            
def _render_template(environment, file, node, vars):
    template = environment.get_template(file)
    if vars['link_table'] == {}:
        vars['link_table'][node.name] = {}
    rendered = template.render(isis_area=vars['isis_area'],
                               isis_password=vars['isis_password'],
                               rtr_number=node.node_id,
                               links=vars['link_table'][node.name],
                               node_name=node.name,
                               openbgpd_peer=vars['openbgpd_peer'],
                               bgp_rr=vars['bgp_rr'],
                               bgp_rr_ip = vars['bgp_rr_ip'],
                               telemetry_collector_ip = vars['telemetry_collector_ip'],
                               location = vars['location'])
    return rendered    

def _build_jinja_templates(node, vars):
    global_path = '/demo/configs/routers/'
    global_files = glob.glob(global_path+'*.j2', recursive=False)
    group_path = f'/demo/configs/routers/{node.group}/'
    group_files = glob.glob(group_path+'*.j2', recursive=False)
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader('/'))
    config = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for file in global_files:
            pool.submit(config.append(_render_template(environment, file, node, vars)))
        for file in group_files:
            pool.submit(config.append(_render_template(environment, file, node, vars)))
    return config

def configure_system(node, vars):
    config = _build_jinja_templates(node, vars)
    pysros_config = []
    for item in config:
        pysros_config.append(node.connection.convert('/', item, source_format='json', destination_format='pysros'))
    print('\n')
    print("=" * 80)
    print(f"Configuration changes requested for node {node.name}")
    print("=" * 80)
    for config_element in pysros_config:
        for top_level_element in config_element.keys():
            printTree(config_element)
            node.connection.candidate.set(f'/{top_level_element}', config_element[top_level_element], commit=False)
    diffs = node.connection.candidate.compare(output_format='md-cli')
    reset_color = "\u001b[0m"
    if diffs:
        bright_yellow = "\u001b[33;1m"
        print('\n')
        print("=" * 80)
        print(f"Changes actually made on node {node.name}")
        print("=" * 80)
        print(diffs)
        print(f"{bright_yellow}Node {node.name} configuration changed{reset_color}")
    else:
        bright_green = "\u001b[32;1m"
        print(f"{bright_green}Node {node.name} configuration changes not required{reset_color}")
    node.connection.candidate.commit()

def get_telemetry_node(clab_topo, vars):
    for node in clab_topo['nodes']:
        if node == vars['telemetry_collector']:
            vars['telemetry_collector_ip'] = clab_topo['nodes'][node]['mgmt-ipv4-address']
    
def main():
    clab_topo = read_yaml_json_file('/demo/clab-srx-demo/topology-data.json', 'json')
    vars = read_yaml_json_file('/demo/configs/routers/vars.yml', 'yaml')
    get_telemetry_node(clab_topo, vars)
    nodes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for router in get_sros_nodes_from_clab_topo(clab_topo):
            pool.submit(nodes.append(Node(name=router[0], ip_address=router[1], index=router[2], group=router[3])))
            if router[0] == vars['bgp_rr']:
                vars['bgp_rr_ip'] = f"10.10.10.{router[2]}"    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        vars['link_table'] = LinkTable(clab_topo['links'], nodes, clab_topo).linktable
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
        for node in nodes:
            pool.submit(configure_system(node, vars))

if __name__=="__main__":
    main()
