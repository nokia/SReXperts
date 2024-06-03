# Copyright 2024 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

from srlinux.mgmt.cli import CliPlugin, KeyCompleter
from srlinux.syntax import Syntax
from srlinux.schema import FixedSchemaRoot
from srlinux.location import build_path
from srlinux import strings
from srlinux.data import Border, ColumnFormatter, TagValueFormatter, Borders, Data, Indent
from srlinux.syntax.value_checkers import IntegerValueInRangeChecker
import json


class Plugin(CliPlugin):
    
    '''
        Load() method: load new CLI command at CLI startup
        Input: cli, the root node of the CLI command hierarchy
    '''
    def load(self, cli, **_kwargs):
        print("\n##########\n\n---> DEBUG: LOADING BGP-BY CLI PLUGIN\n\n##########\n")
       
    '''
        _my_schema() method: construct the schema for this cli command
        Return: schema object 
    '''    
    def _my_schema(self):
        root = FixedSchemaRoot()
        ## add your code here
        return root
   
    '''
        _fetch_state() method: extract relevant data from the state datastore
        Input: state, reference to the datastores
        Input: arguments, the CLI command's context
        Return: copy of a section of the state datastore 
    ''' 
    def _fetch_state(self, state, arguments):
        pass ## replace with your code
   
    '''
        _populate_schema() method: fill in schema from state datastore
        Input: arguments, the CLI command's context
        Return: filled in schema 
    ''' 
    def _populate_schema(self, arguments):
        pass ## replace with your code
   
    '''
        _set_formatters() method: 
        Input: schema, schema to augment with formatters 
    ''' 
    def _set_formatters(self, schema):
        pass ## repace with your code
   
    '''
        _print() method: the callback function
        Input: state, reference to the datastores
        Input: arguments, the CLI command's context
        Input: output, the CLI output object 
    '''
    def _print(self, state, arguments, output, **_kwargs):
        #self._fetch_state(state, arguments)
        #schema = self._populate_schema(state_datastore, arguments)
        #self._set_formatters(schema)
        #output.print_data(schema)
        pass ## remove pass once the methods above are implemented